# Take the output CSV of scrape.py and convert it to a list of tokens
# Where each row in the output CSV contains a single word or punctuation.

import csv

from nltk.tokenize import word_tokenize
from tqdm import tqdm

# read in the CSV
with open('st-ds9-transcripts.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    data = list(reader)

def write_wordlist(data, filename):
    tokens = []

    # tokenize each line
    for line in tqdm(data):
        tokens += [t.lower() for t in word_tokenize(line['Text'])]

    # write to CSV file
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for token in tokens:
            writer.writerow([token])

write_wordlist(data, 'wordlist_full.csv')

# filter down to just the first episode
episode = [d for d in data if d['Episode'] == '401']

write_wordlist(episode, 'wordlist_episode_401.csv')
