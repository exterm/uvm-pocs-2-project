# timeseries of words spoken by each character per episode
# based on the full wordlist, segmented by speaker and episode
# render all speakers in one plot

import argparse

import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
    description='Generate a timeseries of words spoken by each character per episode.'
)

parser.add_argument('wordlist', type=str, help='Input CSV file')
parser.add_argument('--speaker-count', type=int, default=15, help='Number of speakers to keep')
parser.add_argument('--omit-others', action='store_true', help='Omit the "Other" group')
parser.add_argument('--only', type=str, help='Only render the specified speaker(s) (comma-separated)')

args = parser.parse_args()

wordlist = pd.read_csv(args.wordlist)

# rescale episode numbers to start at 1
wordlist['Episode'] = wordlist['Episode'] - wordlist['Episode'].min() + 1

# filter to only the specified speakers
if args.only is not None:
    speakers = args.only.split(',')
    wordlist = wordlist[wordlist['Speaker'].isin(speakers)]

# group all but the most prolific speakers into a single "Other" group
grouped = wordlist.groupby('Speaker')
grouped = sorted(grouped, key=lambda x: len(x[1]), reverse=True)
grouped = grouped[args.speaker_count:]
speakers = [name for name, group in grouped]
if not args.omit_others:
    # render "Other" as a separate group
    wordlist.loc[wordlist['Speaker'].isin(speakers), 'Speaker'] = '(Others)'
else:
    # don't render "Other" at all, just omit it from the plot
    wordlist = wordlist[~wordlist['Speaker'].isin(speakers)]

# group by speaker and episode
grouped = wordlist.groupby(['Speaker', 'Episode'])

# count the number of tokens per speaker per episode
counts = grouped['Token'].count()

# unstack the speaker index to get a dataframe with columns for each speaker
counts = counts.unstack(level=0)

# plot
plt.figure()
# loop over each speaker
for speaker in counts.columns:
    plt.scatter(counts.index, counts[speaker], label=speaker)
plt.legend()
plt.title('Words spoken by each character per episode')
plt.xlabel('Episode')
plt.ylabel('Words spoken')
plt.draw()

# add a new column, "Scene", which counts the number of scenes per episode
# a new scene is defined as a change in location
wordlist['Scene'] = wordlist['Location'].ne(wordlist['Location'].shift()).cumsum()

# plot a timeseries of scenes a speaker appears in per episode
# group by speaker and episode
grouped = wordlist.groupby(['Speaker', 'Episode'])

# count the number of scenes per speaker per episode
counts = grouped['Scene'].nunique()

# unstack the speaker index to get a dataframe with columns for each speaker
counts = counts.unstack(level=0)

# plot
plt.figure()
# loop over each speaker
for speaker in counts.columns:
    plt.scatter(counts.index, counts[speaker], label=speaker)
plt.legend()
plt.title('Scenes a speaker appears in per episode')
plt.xlabel('Episode')
plt.ylabel('Scenes')
plt.draw()

plt.show()
