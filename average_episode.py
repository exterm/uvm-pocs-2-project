# plot timeseries for all episodes into a single plot
# overlaid so that the mean timeseries is visible
# we need to scale each timeseries to be the same length
# and plot them transparently so that the mean is visible

import argparse

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tqdm import tqdm

from lib import happiness

def shift_timeseries(timeseries, shift):
    return [None] * shift + timeseries

parser = argparse.ArgumentParser(
    description='Plot a combination of timeseries for all episodes in a wordlist.'
)

parser.add_argument('wordlist', type=str, help='Input CSV file')

# add options to speciy exact window size and lens - incompatible with --lenses
parser.add_argument('window_size', type=int, help='Window size to use')
parser.add_argument('lens', type=float, help='Lens value to use')
parser.add_argument('--output', '-o', type=str, help='Output file name')

args = parser.parse_args()

print("read happiness scores")
happiness_scores = pd.read_csv('Hedonometer.csv', usecols=['Word', 'Happiness Score'])
happiness_scores = happiness_scores.set_index('Word')
happiness_scores = happiness_scores.to_dict()['Happiness Score']

print("read wordlist")
wordlist_full = pd.read_csv(args.wordlist)

episodes = wordlist_full['Episode'].to_list()
episodes = list(set(episodes))

print("calculate timeseries for each episode")
episode_timeseries = []
for episode in tqdm(episodes):
    episode_wordlist = wordlist_full[wordlist_full['Episode'] == episode]
    episode_wordlist = episode_wordlist['Token'].to_list()

    episode_timeseries.append(
        happiness.timeseries_fast(args.window_size, episode_wordlist, happiness_scores, args.lens, progress_bar=False)
    )

min_episode_length = min([len(timeseries) for timeseries in episode_timeseries])
print("min episode length:", min_episode_length, "words")

# # eliminate the three shortest episodes
# episode_timeseries = sorted(episode_timeseries, key=len, reverse=False)
# episode_timeseries = episode_timeseries[5:]

# min_episode_length = min([len(timeseries) for timeseries in episode_timeseries])
# print("min episode length after removing shortest ones:", min_episode_length, "words")

# scale each timeseries to the same length as the shortest episode
# by sampling the timeseries min_episode_length times at regular intervals
scaled_timeseries = []
for timeseries in episode_timeseries:
    scaled_timeseries.append(
        [timeseries[i] for i in np.linspace(0, len(timeseries) - 1, min_episode_length, dtype=int)]
    )

# shift each timeseries to the right by the half of the window size
# so that the timeseries is centered on the word
scaled_timeseries = [shift_timeseries(timeseries, args.window_size // 2) for timeseries in scaled_timeseries]

# plot all timeseries in a single plot with transparency
for timeseries in scaled_timeseries:
    plt.plot(timeseries, color='black', alpha=0.02)

# plot the mean and median timeseries - watch out for None values
mean_timeseries = []
for i in range(min_episode_length):
    values = [timeseries[i] for timeseries in scaled_timeseries if timeseries[i] is not None]
    mean_timeseries.append(np.mean(values))

plt.plot(mean_timeseries, color='red')

plt.xlabel("Word position")
plt.ylabel("Happiness score")

plt.ylim(3, 7)

plt.title(f"Averaged timeseries, window size {args.window_size}, lens {args.lens}")

if args.output:
    plt.savefig(args.output, dpi=300)
else:
    plt.show()
