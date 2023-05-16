# plot timeseries for all episodes into a single plot
# overlaid so that the mean timeseries is visible
# we need to scale each timeseries to be the same length
# and plot them transparently so that the mean is visible

import argparse

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tqdm import tqdm

from lib import scoring

def shift_timeseries(timeseries, shift):
    return [None] * shift + timeseries

parser = argparse.ArgumentParser(
    description='Plot a combination of timeseries for all episodes in a wordlist.'
)

parser.add_argument('wordlist', type=str, help='Input CSV file')
parser.add_argument('lens', type=float, help='Lens value to use')
parser.add_argument('num_buckets', type=int, help='Number of buckets to use')
parser.add_argument('--output', '-o', type=str, help='Output file name')
parser.add_argument('--score-type', type=str, default="Valence", help='Which score type to use')

args = parser.parse_args()

print("read scores dictionary, using", args.score_type, "scores")
scores = pd.read_csv('ousiometry-data/ousiometry_data_augmented.tsv', usecols=['Word', args.score_type], sep='\t')

scores = scores.set_index('Word')
scores = scores.to_dict()[args.score_type]

print("read wordlist")
wordlist_full = pd.read_csv(args.wordlist)

episodes = wordlist_full['Episode'].to_list()
episodes = list(set(episodes))

print("calculate timeseries for each episode")
all_episode_timeseries = []
for episode in tqdm(episodes):
    episode_wordlist = wordlist_full[wordlist_full['Episode'] == episode]
    episode_wordlist = episode_wordlist['Token'].to_list()

    # create args.num_buckets buckets of equal size and calculate the happiness score for each bucket
    # the happiness score is the average happiness score of all words in the bucket
    bucket_size = len(episode_wordlist) // args.num_buckets
    episode_timeseries = []
    for i in range(args.num_buckets):
        bucket = episode_wordlist[i * bucket_size:(i + 1) * bucket_size]
        score = scoring.score_text(bucket, scores, args.lens)
        if score is None or score == 0:
            print(f"episode {episode} bucket {i} is empty")
        episode_timeseries.append(score)

    all_episode_timeseries.append(episode_timeseries)

# plot all timeseries in a single plot with transparency
for timeseries in all_episode_timeseries:
    plt.plot(timeseries, color='black', alpha=0.03)

# plot the mean and median timeseries - watch out for None values
mean_timeseries = []
for i in range(args.num_buckets):
    values = [timeseries[i] for timeseries in all_episode_timeseries if timeseries[i] is not None]
    mean_timeseries.append(np.mean(values))

plt.plot(mean_timeseries, color='red')

plt.xlabel("Percentage of tokens elapsed")
plt.ylabel(args.score_type + " score")

plt.xticks(np.arange(0, args.num_buckets + .01, args.num_buckets / 5), np.arange(0, 101, 20))

plt.title(f"Averaged timeseries, lens {args.lens}, buckets: {args.num_buckets}")

if args.output:
    plt.savefig(args.output, dpi=300)
else:
    plt.show()
