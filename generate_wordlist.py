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
    print(f"writing {filename}...")
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

def write_episode(episode_number):
    episode = [d for d in data if d['Episode'] == episode_number]
    write_wordlist(episode, f'wordlist_episode_{episode_number}.csv')

def write_speaker(speaker):
    speaker_data = [d for d in data if d['Speaker'] == speaker]
    write_wordlist(speaker_data, f'wordlist_{speaker}.csv')

write_wordlist(data, 'wordlist_full.csv')

write_episode(401)

write_speaker('Sisko')
write_speaker('Kira')
write_speaker('Odo')
write_speaker('Dax')
write_speaker('Bashir')
write_speaker('O\'Brien')
write_speaker('Quark')
write_speaker('Rom')
write_speaker('Nog')
write_speaker('Garak')
write_speaker('Worf')
write_speaker('Dukat')

first_five_seasons = [d for d in data if int(d['Season']) <= 5]
seasons_after_five = [d for d in data if int(d['Season']) > 5]

write_wordlist(first_five_seasons, 'wordlist_first_five_seasons.csv')
write_wordlist(seasons_after_five, 'wordlist_seasons_after_five.csv')

first_four_seasons = [d for d in data if int(d['Season']) <= 4]
seasons_after_four = [d for d in data if int(d['Season']) > 4]

write_wordlist(first_four_seasons, 'wordlist_first_four_seasons.csv')
write_wordlist(seasons_after_four, 'wordlist_seasons_after_four.csv')
