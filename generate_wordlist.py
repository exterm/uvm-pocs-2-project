# Take the output CSV of scrape.py and convert it to a list of tokens
# Where each row in the output CSV contains a single word or punctuation.

import csv

from nltk.tokenize import word_tokenize
from tqdm import tqdm
import pandas as pd

# read in the CSV
with open('st-ds9-transcripts.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    data = list(reader)

def write_wordlist(data, filename):
    # we want to tokenize the text and write it to a CSV file with one token per row
    # The columns should be Episode,Season,Title,Location,Speaker,Context,Token
    # The rows should be the tokens in the order they appear in the text
    wordlist = []

    # tokenize each line
    for line in tqdm(data):
        tokens = [t.lower() for t in word_tokenize(line['Text'])]
        for token in tokens:
            wordlist.append({
                'Episode': line['Episode'],
                'Season': line['Season'],
                'Title': line['Title'],
                'Location': line['Location'],
                'Speaker': line['Speaker'],
                'Context': line['Context'],
                'Token': token
            })

    wordlist = pd.DataFrame(wordlist)

    # write to CSV file
    wordlist.to_csv(filename, index=False)

write_wordlist(data, 'wordlist_full.csv')

# filter down to just the first episode
episode = [d for d in data if d['Episode'] == '401']

write_wordlist(episode, 'wordlist_episode_401.csv')
