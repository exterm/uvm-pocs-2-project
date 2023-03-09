# plot two timeseries: average happiness of each group and number of tokens per group
# in the same diagram.

import argparse

import matplotlib.pyplot as plt
import pandas as pd

from scipy.stats import rankdata

from lib import happiness

parser = argparse.ArgumentParser(
    description='Plot happiness vs. wordcount.'
)

parser.add_argument('wordlist', type=str, help='Input CSV file')
parser.add_argument('column', type=str, help='Column to use for grouping')

args = parser.parse_args()

wordlist = pd.read_csv(args.wordlist)

happiness_scores = pd.read_csv('Hedonometer.csv', usecols=['Word', 'Happiness Score'])
happiness_scores = happiness_scores.set_index('Word')
happiness_scores = happiness_scores.to_dict()['Happiness Score']

grouped = wordlist.groupby(args.column)

# sort largest groups first
grouped = sorted(grouped, key=lambda x: len(x[1]), reverse=True)

# compute average happiness score for each group
averages = {}
for name, group in grouped:
    averages[name] = happiness.score_text(list(group['Token']), happiness_scores)

# render timeseries
plt.figure()
plt.plot([len(group) for name, group in grouped], [v for k, v in averages.items()], 'o')
plt.title(f"Happiness vs. wordcount for {args.column}")
plt.xlabel("Wordcount")
plt.ylabel("Happiness")
plt.draw()

plt.show()
