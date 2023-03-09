# take two wordlist files and generate a wordshift using shifterator

import argparse
from collections import Counter

import pandas as pd

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

args = parser.parse_args()

if args.baseline != 'average':
    args.baseline = float(args.baseline)

reference = pd.read_csv(args.reference)[args.column]
comparison = pd.read_csv(args.comparison)[args.column]

reference_bag = Counter(reference)
comparison_bag = Counter(comparison)

if args.column == "Token":
    # print("read happiness scores")
    # scores = pd.read_csv('Hedonometer.csv', usecols=['Word', 'Happiness Score'])
    # scores = scores.set_index('Word')
    # scores = scores.to_dict()['Happiness Score']
    scores = 'labMT_English'
else:
    scores = {t: 1 for t in reference_bag.keys() | comparison_bag.keys()}

shift = sh.shifterator.Shift(reference_bag, comparison_bag, type2score_1=scores, type2score_2=scores, stop_lens=[(3,7)], reference_value=args.baseline)

shift.get_shift_graph(system_names=[args.reference_name, args.comparison_name])
