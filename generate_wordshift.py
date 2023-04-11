# take two wordlist files and generate a wordshift using shifterator

import argparse
from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt

import shifterator as sh

parser = argparse.ArgumentParser(
    description='Generate a wordshift for two wordlists.'
)

parser.add_argument('reference', type=str, help='Reference CSV file')
parser.add_argument('comparison', type=str, help='Comparison CSV file')

parser.add_argument('--column', type=str, default="Token", help='Which column to use')
parser.add_argument('--baseline', type=str, default='average', help='Which value to use as neutral; defaults to the average of the reference system.')

parser.add_argument('--reference-name', type=str, default="reference", help='Name to use for the reference system')
parser.add_argument('--comparison-name', type=str, default="comparison", help='Name to use for the comparison system')

parser.add_argument('--score-type', type=str, default="labMT", help='Which score type to use')

args = parser.parse_args()

if args.baseline != 'average':
    args.baseline = float(args.baseline)

reference = pd.read_csv(args.reference)[args.column]
comparison = pd.read_csv(args.comparison)[args.column]

reference_bag = Counter(reference)
comparison_bag = Counter(comparison)

stop_lens = None

if args.column == "Token":
    if args.score_type == 'labMT':
        scores = 'labMT_English'
        stop_lens = [(3,7)]
    else:
        print(f"read {args.score_type} scores")
        scores = pd.read_csv('ousiometry-data/ousiometry_data_augmented.tsv', usecols=['Word', args.score_type], sep='\t')
        scores = scores.set_index('Word')
        scores = scores.to_dict()[args.score_type]
else:
    scores = {t: 1 for t in reference_bag.keys() | comparison_bag.keys()}

shift = sh.shifterator.Shift(reference_bag, comparison_bag, type2score_1=scores, type2score_2=scores, stop_lens=stop_lens, reference_value=args.baseline)

ax = shift.get_shift_graph(system_names=[args.reference_name, args.comparison_name], show_plot=False)

# create more space for title of plot
plt.subplots_adjust(top=0.9)

plt.show()
