import argparse

import cProfile
import pstats
from pstats import SortKey

import matplotlib.pyplot as plt
import pandas as pd

from lib import happiness

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

def shift_timeseries(timeseries, shift):
    return [None] * shift + timeseries


parser = argparse.ArgumentParser(
    description='Generate a timeseries of happiness scores for a given wordlist.'
)

parser.add_argument('wordlist', type=str, help='Input CSV file')
parser.add_argument('--profile', action='store_true', help='Profile the script')

# optional argument: iterate over a range of lens values
parser.add_argument('--lenses', action='store_true', help='Iterate over a range of lens values')

args = parser.parse_args()

WINDOW_EXPONENTS = [1, 1.5, 2, 2.5, 3, 3.5, 4]
# WINDOW_EXPONENTS = [1, 1.5, 2]
LENSES = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
# LENSES = [0, 0.5]
PREFERRED_WINDOW_SIZE = 10000

print("read happiness scores")
happiness_scores = pd.read_csv('Hedonometer.csv', usecols=['Word', 'Happiness Score'])
happiness_scores = happiness_scores.set_index('Word')
happiness_scores = happiness_scores.to_dict()['Happiness Score']

window_sizes = [round(10 ** z) for z in WINDOW_EXPONENTS]

print("read wordlist")
wordlist_full = pd.read_csv(args.wordlist)

# truncate wordlist to a reasonable size
# wordlist_full = wordlist_full[:100000]

# just the tokens
wordlist = wordlist_full['Token'].to_list()

# find the row index of the first row for each season
seasons = wordlist_full['Season'].to_list()

max_season = max(seasons)
season_indices = [seasons.index(season) for season in range(1, max_season + 1)]

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

        timeseries = happiness.timeseries_fast(
            PREFERRED_WINDOW_SIZE,
            wordlist,
            happiness_scores,
            lens
        )

        timeseries = shift_timeseries(timeseries, PREFERRED_WINDOW_SIZE // 2)

        axes[i].plot(timeseries)
        axes[i].set_title(f"lens: {lens}, window size: {PREFERRED_WINDOW_SIZE}")

        last_plot = i == len(LENSES) - 1
        set_axes(axes[i], last_plot)
        mark_seasons(axes[i], season_indices, last_plot)
else:
    for i, window_size in enumerate(window_sizes):
        print(f"window size: {window_size}")

        timeseries = happiness.timeseries_fast(window_size, wordlist, happiness_scores)

        timeseries = shift_timeseries(timeseries, window_size // 2)

        axes[i].plot(timeseries)
        axes[i].set_title(f"Window size: {window_size}")

        last_plot = i == len(window_sizes) - 1
        set_axes(axes[i], last_plot)
        mark_seasons(axes[i], season_indices, last_plot)

plt.show()

