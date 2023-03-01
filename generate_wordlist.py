# Take the output CSV of scrape.py and convert it to a list of tokens
# Where each row in the output CSV contains a single word or punctuation.

import csv

from nltk.tokenize import word_tokenize
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser(
    description='Convert a CSV of Star Trek: Deep Space Nine transcripts to a list of tokens.'
)

parser.add_argument('input', type=str, help='Input CSV file')

args = parser.parse_args()

# read in the CSV
with open(args.input, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    data = list(reader)

tokens = []

# tokenize each line
for line in tqdm(data):
    tokens += [t.lower() for t in word_tokenize(line['Text'])]

# write to CSV file
with open('wordlist.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for token in tokens:
        writer.writerow([token])
