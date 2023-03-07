# read a wordlist file and compute average happiness score for each location, speaker, episode, etc.

import csv
import argparse

import pandas as pd
import matplotlib.pyplot as plt

from scipy.stats import rankdata

from lib import happiness

GROUP_COUNT = 50
LENS = 1

parser = argparse.ArgumentParser(
    description='Generate a ranking of a certain set by average happiness score.'
)

parser.add_argument('wordlist', type=str, help='Input CSV file')
parser.add_argument('column', type=str, help='Column to use for grouping')
parser.add_argument('--lens', type=float, default=LENS, help='Lens value to use for shifterator')
parser.add_argument('--group-count', type=int, default=GROUP_COUNT, help='Number of groups to keep')

args = parser.parse_args()

wordlist = pd.read_csv(args.wordlist)

happiness_scores = pd.read_csv('Hedonometer.csv', usecols=['Word', 'Happiness Score'])
happiness_scores = happiness_scores.set_index('Word')
happiness_scores = happiness_scores.to_dict()['Happiness Score']

# group by column
grouped = wordlist.groupby(args.column)

# keep only the largest groups
grouped = sorted(grouped, key=lambda x: len(x[1]), reverse=True)[:args.group_count]

print("Most tokens:")
for name, group in grouped[:10]:
    print(f"{name:20} {len(group):>7}")

# bar chart of group sizes
plt.figure()
plt.bar([name for name, group in grouped], [len(group) for name, group in grouped])
plt.xticks(rotation=90)
plt.title(f"Number of tokens per {args.column}")
plt.draw()

# compute average happiness score for each group
averages = {}
for name, group in grouped:
    averages[name] = happiness.score_text(list(group['Token']), happiness_scores, lens=args.lens)

# sort by average happiness score
averages = {k: v for k, v in sorted(averages.items(), key=lambda item: item[1])}

# filter out zero values
averages_without_zero = {k: v for k, v in averages.items() if v != 0}

print("\nHappiest:")
# sort by descending score, use two decimal places for the score
highest = list(averages_without_zero.items())[-10:]
highest.sort(reverse=True, key=lambda x: x[1])
for k, v in highest:
    print(f"{v:.2f}", k)

# plot: spekaer on the x axis, happiness score on the y axis
# sorted by happiness score
plt.figure()
plt.bar([k for k, v in averages.items()], [v for k, v in averages.items()])
plt.xticks(rotation=90)
plt.title(f"Happiness score per {args.column}")
plt.draw()


print("\nUnhappiest:")
for k, v in list(averages_without_zero.items())[:10]:
    print(f"{v:.2f}", k)
# # plot the distribution
# plt.hist(averages.values(), bins=100)
# plt.title(f"Happiness score distribution for {args.column}")

# plt.show()

# plot zipf's law, use rankdata
ranks = rankdata(list(averages.values()))
plt.figure()
plt.plot(ranks, list(averages.values()))
plt.title(f"Happiness score distribution for {args.column}")
plt.xlabel("Rank")
plt.ylabel("Happiness score")

plt.show()
