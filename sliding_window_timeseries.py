# assignment 20

import argparse

import cProfile
import pstats
from pstats import SortKey

import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

from lib import scoring

def set_axes(axes, last):
    axes.yaxis.set_major_formatter('{x:.2f}')
    axes.set_ylabel("Avg. happiness")
    # only label the x-axis on the bottom plot
    if last:
        axes.set_xlabel("Time (in words elapsed)")

def mark_seasons(axes, season_indices, last):
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

def get_episode_indices(wordlist):
    # find the row index of the first row for each episode
    episodes: list[int] = wordlist['Episode'].to_list()

    episode_pairs = zip(episodes, episodes[1:])

    # find the row index of the first row for each episode
    return [i for i, (a, b) in enumerate(episode_pairs) if a != b]

def center_scored_timeseries(timeseries, window_size):
    shift = window_size // 2
    return [None] * shift + timeseries + [None] * shift

def timeseries_by_episode(window_size: int, wordlist: pd.DataFrame, happiness_scores, lens: float):
    # create a list of lists of tokens per episode
    episodes = wordlist.groupby('Episode')['Token'].apply(list).tolist()

    score_episode = \
        lambda episode: scoring.timeseries_fast(window_size, episode, happiness_scores, lens, progress_bar=False)
    # use scoring.timeseries_fast to generate a scored timeseries for each episode
    timeseries = [score_episode(episode) for episode in tqdm(episodes)]

    # add None values to the beginning and end of each timeseries to account for the window size
    timeseries = [center_scored_timeseries(timeseries, window_size) for timeseries in timeseries]

    # return concatenated timeseries
    return [item for sublist in timeseries for item in sublist]

parser = argparse.ArgumentParser(
    description='Generate a timeseries of happiness scores for a given wordlist.'
)

parser.add_argument('wordlist', type=str, help='Input CSV file')
parser.add_argument('--profile', action='store_true', help='Profile the script')

# optional argument: iterate over a range of lens values
parser.add_argument('--lenses', action='store_true', help='Iterate over a range of lens values')

# add options to speciy exact window size and lens - incompatible with --lenses
parser.add_argument('--window-size', type=int, default=None, help='Window size to use')
parser.add_argument('--lens', type=float, default=None, help='Lens value to use')

parser.add_argument('--smol', action='store_true', help='Truncate the wordlist for testing purposes')

args = parser.parse_args()

if args.lenses and (args.window_size is not None or args.lens is not None):
    print("Error: --lenses and --window-size or --lens are incompatible")
    exit(1)

WINDOW_EXPONENTS = [1, 1.5, 2, 2.5, 3, 3.5, 4]
LENSES = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
# LENSES = [0, 0.5]
PREFERRED_WINDOW_SIZE = 316
PREFERRED_LENS = 1.5

print("read happiness scores")
happiness_scores = pd.read_csv('Hedonometer.csv', usecols=['Word', 'Happiness'])
happiness_scores = happiness_scores.set_index('Word')
happiness_scores = happiness_scores.to_dict()['Happiness']

if args.window_size is not None:
    window_sizes = [args.window_size]
else:
    window_sizes = [round(10 ** z) for z in WINDOW_EXPONENTS]

print("read wordlist")
wordlist_full = pd.read_csv(args.wordlist)

# truncate wordlist to a reasonable size
if args.smol:
    episodes = 5
    print(f"truncating wordlist to {episodes} episodes")
    # note that the Episodes column values start at an arbitrary value and are not necessarily sequential
    episode_indices = get_episode_indices(wordlist_full)
    wordlist_full = wordlist_full.iloc[:episode_indices[episodes]]

# just the tokens
wordlist = wordlist_full['Token'].to_list()

# find the row index of the first row for each season
seasons = wordlist_full['Season'].to_list()

max_season = max(seasons)
season_indices = [seasons.index(season) for season in range(1, max_season + 1) if season in seasons]


if args.profile:
    cProfile.run('happiness.timeseries(window_size, wordlist, happiness_scores)', 'restats')
    p = pstats.Stats('restats')
    p.sort_stats(SortKey.CUMULATIVE).print_stats(10)
    exit(0)

num_plots = len(LENSES) if args.lenses else len(window_sizes)

# Make a single figure containing a stacked set of plots for each window size
fig, axes = plt.subplots(num_plots, 1, sharex=True, sharey=False)

# increase vertical spacing between plots
fig.subplots_adjust(hspace=0.5)

if args.lenses:
    for i, lens in enumerate(LENSES):
        print(f"lens: {lens}")

        timeseries = timeseries_by_episode(PREFERRED_WINDOW_SIZE, wordlist_full, happiness_scores, lens)

        axes[i].plot(timeseries)
        axes[i].set_title(f"lens: {lens}, window size: {PREFERRED_WINDOW_SIZE}")

        last_plot = i == len(LENSES) - 1
        set_axes(axes[i], last_plot)
        mark_seasons(axes[i], season_indices, last_plot)
else:
    lens = args.lens or PREFERRED_LENS
    for i, window_size in enumerate(window_sizes):
        ax = axes[i] if num_plots > 1 else axes
        print(f"window size: {window_size}")

        timeseries = timeseries_by_episode(window_size, wordlist_full, happiness_scores, lens)

        ax.plot(timeseries)
        ax.set_title(f"Window size: {window_size}, lens: {lens}")

        last_plot = i == len(window_sizes) - 1
        set_axes(ax, last_plot)
        mark_seasons(ax, season_indices, last_plot)

plt.show()
