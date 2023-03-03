import argparse

import cProfile
import pstats
from pstats import SortKey

import matplotlib.pyplot as plt
import pandas as pd

from lib import happiness

parser = argparse.ArgumentParser(
    description='Generate a timeseries of happiness scores for a given wordlist.'
)

parser.add_argument('wordlist', type=str, help='Input CSV file')

args = parser.parse_args()

WINDOW_EXPONENTS = [1, 1.5, 2, 2.5, 3, 3.5, 4]

print("read happiness scores")
happiness_scores = pd.read_csv('Hedonometer.csv', usecols=['Word', 'Happiness Score'])
happiness_scores = happiness_scores.set_index('Word')
happiness_scores = happiness_scores.to_dict()['Happiness Score']

window_sizes = [round(10 ** z) for z in WINDOW_EXPONENTS]

print("read wordlist")
wordlist = pd.read_csv(args.wordlist, header=None).squeeze("columns")

# truncate wordlist to a reasonable size
# wordlist = wordlist[:100000]

# Make a single figure containing a stacked set of plots for each window size
fig, axes = plt.subplots(len(window_sizes), 1, sharex=True, sharey=True)

for i, window_size in enumerate(window_sizes):
    print(f"window size: {window_size}")
    # cProfile.run('happiness.timeseries(window_size, wordlist, happiness_scores)', 'restats')

    timeseries = happiness.timeseries_fast(window_size, wordlist, happiness_scores)
    axes[i].plot(timeseries)
    axes[i].set_title(f"Window size: {window_size}")

plt.show()

# p = pstats.Stats('restats')
# p.sort_stats(SortKey.CUMULATIVE).print_stats(10)
