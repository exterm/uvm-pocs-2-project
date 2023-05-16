import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

from lib import scoring

def set_axes(axes,  y_name, last: bool = False) -> None:
    axes.yaxis.set_major_formatter('{x:.2f}')
    axes.set_ylabel("Avg. " + y_name)
    # only label the x-axis on the bottom plot
    if last:
        axes.set_xlabel("Time (in words elapsed)")

def mark_seasons(axes, season_indices, last: bool = False) -> None:
    for i, season_index in enumerate(season_indices):
        axes.axvline(season_index, color='red', linestyle='--')

    # add a caption to each season line in the last plot
    if last:
        for i, season_index in enumerate(season_indices):
            axes.text(
                season_index + 5000,
                axes.get_ylim()[0],
                f"Season {i + 1}",
                verticalalignment='bottom',
                horizontalalignment='left'
            )

def segmented_timeseries(segmentation: str, wordlist: pd.DataFrame, dictionary, lens: float) -> list[tuple[float | None, int]]:
    # create a list of lists of tokens per episode
    episodes = wordlist.groupby('Episode')

    if segmentation == 'episode':
        return [score_segment(episode['Token'].to_list(), dictionary, lens) for _, episode in episodes]

    elif segmentation == 'scene':
        print("splitting into scenes")
        episodes_scenes = []
        for episode, episode_df in tqdm(episodes):
            # a new scene begins every time the Location changes. Note that Locations are not unique within an episode
            # so we need to use changes in Location as an indicator of a new scene
            locations = episode_df['Location'].to_list()
            scene_indices = [0] + [i + 1 for i, (a, b) in enumerate(zip(locations, locations[1:])) if a != b]

            # split the episode into scenes
            scenes = []
            for i in range(len(scene_indices) - 1):
                scenes.append(episode_df.iloc[scene_indices[i]:scene_indices[i + 1]])

            episodes_scenes.append(scenes)

        print("scoring scenes")
        scored_episode_scenes = [[score_segment(scene['Token'], dictionary, lens) for scene in episode] for episode in tqdm(episodes_scenes)]

        scored_scenes = []
        for episode in scored_episode_scenes:
            scored_scenes += episode

        return scored_scenes

    else:
        raise ValueError(f"Invalid segmentation: {segmentation}")

def score_segment(segment: list[str], dictionary, lens: float) -> tuple[float | None, int]:
    score = scoring.score_text(segment, dictionary, lens)
    return score, len(segment)

def get_season_indices(wordlist):
    # find the row index of the first row for each season
    seasons = wordlist['Season'].to_list()

    max_season = max(seasons)
    return [seasons.index(season) for season in range(1, max_season + 1)]

def get_episode_indices(wordlist):
    # find the row index of the first row for each episode
    episodes: list[int] = wordlist['Episode'].to_list()

    episode_pairs = zip(episodes, episodes[1:])

    # find the row index of the first row for each episode
    return [i for i, (a, b) in enumerate(episode_pairs) if a != b]

def plot_timeseries(num_plots: int, lens: float, axes: np.ndarray, score_name: str, i: int = 0) -> None:
    timeseries = segmented_timeseries(args.segmentation, wordlist_full, scores, lens)

    cur_pos = 0
    for segment_score, segment_length in timeseries:
        if segment_score is not None:
            weight: float = segment_length / max([length for _, length in timeseries])
            axes[i].scatter(cur_pos + segment_length / 2, segment_score, s=1000*np.sqrt(1/len(timeseries)), c='black', alpha=weight)
        cur_pos += segment_length

    axes[i].set_title(f"lens: {lens}")
    axes[i].set_ylim([-0.4, 0.4])

    last_plot = i == num_plots - 1
    set_axes(axes[i], score_name.lower(), last_plot)
    mark_seasons(axes[i], get_season_indices(wordlist_full), last_plot)

    # print min and max segment scores
    segment_scores = [score for score, _ in timeseries if score is not None]
    print(f"min {score_name.lower()}: {min(segment_scores)}")
    print(f"max {score_name.lower()}: {max(segment_scores)}")

    if args.segmentation != 'episode':
        episode_indices = get_episode_indices(wordlist_full)

        for episode_index in episode_indices:
            axes[i].axvline(x=episode_index, color='black', linestyle='dashed', linewidth=0.2)

parser = argparse.ArgumentParser(
    description='Generate a timeseries of scores for a given wordlist.'
)
exclusive_lens_args = parser.add_mutually_exclusive_group()

parser.add_argument('wordlist', type=str, help='Input CSV file')

parser.add_argument('--score-type', type=str, default="Valence", help='Which score type to use')

exclusive_lens_args.add_argument('--lenses', action='store_true', help='Iterate over a range of lens values')
exclusive_lens_args.add_argument('--lens', type=float, default=None, help='Lens value to use')

parser.add_argument('--smol', action='store_true', help='Truncate the wordlist for testing purposes')

VALID_SEGMENTATIONS = ['episode', 'scene']
parser.add_argument('--segmentation', type=str, default=VALID_SEGMENTATIONS[0], choices=VALID_SEGMENTATIONS, help='Segmentation to use')

args = parser.parse_args()

LENSES = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
# LENSES = [0, 0.5]
PREFERRED_LENS = 1.5

print("read scores dictionary, using", args.score_type, "scores")
scores = pd.read_csv('ousiometry-data/ousiometry_data_augmented.tsv', usecols=['Word', args.score_type], sep='\t')

scores = scores.set_index('Word')
scores = scores.to_dict()[args.score_type]

print("read wordlist")
wordlist_full = pd.read_csv(args.wordlist)

if args.smol:
    episodes = 5
    print(f"truncating wordlist to {episodes} episodes")
    # note that the Episodes column values start at an arbitrary value and are not necessarily sequential
    episode_indices = get_episode_indices(wordlist_full)
    wordlist_full = wordlist_full.iloc[:episode_indices[episodes]]

num_plots = len(LENSES) if args.lenses else 1

# Make a single figure containing a stacked set of plots for each window size
axes: np.ndarray
fig, axes = plt.subplots(num_plots, 1, sharex=True, sharey=False)

if num_plots == 1:
    axes = np.array([axes])

# increase vertical spacing between plots
fig.subplots_adjust(hspace=0.5)

if args.lenses:
    for i, lens in enumerate(LENSES):
        print(f"lens: {lens}")

        plot_timeseries(num_plots, lens, axes, args.score_type, i)
else:
    lens = PREFERRED_LENS if args.lens is None else args.lens

    plot_timeseries(num_plots, lens, axes, args.score_type)

plt.show()

