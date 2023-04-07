# read a wordlist file and compute average score for each location, speaker, episode, etc.

import argparse

import pandas as pd
import matplotlib.pyplot as plt

from scipy.stats import rankdata

from lib import scoring

LENS = 0

parser = argparse.ArgumentParser(
    description='Generate a ranking of a certain set by average of some per-word score.'
)

# Metrics can be happiness from Hedonometer.csv or different metrics from the ousiometry data

parser.add_argument('wordlist', type=str, help='Input CSV file')
parser.add_argument('column', type=str, help='Column to use for grouping')
parser.add_argument('metric_file', type=str, help='File to read metric values from')
parser.add_argument('metric_column', type=str, help='Column to use for metric values')
parser.add_argument('--lens', type=float, default=LENS, help='Lens value to use for scoring')
parser.add_argument('--group-count', type=int, default=None, help='Number of groups to keep')
parser.add_argument('--output-prefix', '--op', type=str, help='Output file name prefix')
parser.add_argument('--no-show', action='store_true', help='Do not show the plots')

args = parser.parse_args()

wordlist = pd.read_csv(args.wordlist)

scores = pd.read_csv(args.metric_file, usecols=['Word', args.metric_column], sep=None)
scores = scores.set_index('Word')
scores = scores.to_dict()[args.metric_column]

grouped = wordlist.groupby(args.column)

# sort largest groups first
grouped = sorted(grouped, key=lambda x: len(x[1]), reverse=True)

# keep only the largest groups
if args.group_count is not None:
    grouped = grouped[:args.group_count]

print("Most tokens:")
for name, group in grouped[:10]:
    print(f"{name:20} {len(group):>7}")

# bar chart of group sizes
plt.figure()
plt.bar([name for name, group in grouped], [len(group) for name, group in grouped])
plt.xticks(rotation=90)
plt.title(f"Number of tokens per {args.column}")
plt.subplots_adjust(bottom=0.25)
plt.draw()

column_string = args.column.lower().replace(' ', '_')
metric_column_string = args.metric_column.lower().replace(' ', '_')

if args.output_prefix is not None:
    plt.savefig(f"output/{args.output_prefix}_{column_string}_tokens.pdf", dpi=300)

# compute average score for each group
averages = {}
for name, group in grouped:
    averages[name] = scoring.score_text(list(group['Token']), scores, lens=args.lens)

# sort by average score
averages = {k: v for k, v in sorted(averages.items(), key=lambda item: item[1], reverse=True)}

# filter out zero values
averages_without_zero = {k: v for k, v in averages.items() if v != 0}

print("\Lowest scores:")
# sort by descending score, use two decimal places for the score
lowest = list(averages_without_zero.items())[-10:]
lowest.sort(key=lambda x: x[1])
for k, v in lowest:
    print(f"{v:.2f}", k)

# plot: speaker on the x axis, score on the y axis
# sorted by score
plt.figure()
plt.bar([k for k, v in averages.items()], [v for k, v in averages.items()])
plt.xticks(rotation=90)
plt.title(f"{args.metric_column} score per {args.column}")
plt.subplots_adjust(bottom=0.25)
plt.draw()
if args.output_prefix is not None:
    plt.savefig(f"output/{args.output_prefix}_{column_string}_{metric_column_string}_scores.pdf", dpi=300)

print("\Highest scores:")
for k, v in list(averages_without_zero.items())[:10]:
    print(f"{v:.2f}", k)

print("\nAverages:")
print(f"Score: {sum(averages.values()) / len(averages):.2f}")
print(f"Tokens per {args.column}: {sum([len(group) for name, group in grouped]) / len(grouped):.2f}")

# plot zipf's law, use rankdata
ranks = rankdata(list(averages.values()))
plt.figure()
plt.plot(ranks, list(averages.values()))
plt.title(f"{args.metric_column} distribution for {args.column}")
plt.xlabel("Rank")
plt.ylabel(args.metric_column)

if (args.output_prefix is None) and (not args.no_show):
    plt.show()
