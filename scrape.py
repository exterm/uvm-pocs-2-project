# Scrape the transcripts of all episodes of a series from chakoteya.net
# Source: http://chakoteya.net/{series}/{episode}.htm (starting at 401)
# Output in CSV format. Columns: Episode, Season, Title, Location, Speaker, Context, Text

# TODO: Parse the location of the speaker
#   Example: LOCUTUS [on viewscreen]: Resistance is futile.

import csv
import requests
import argparse

from tqdm import tqdm

from lib import transcript_parsing

SERIES = {
    'TNG': {
        'URL path': 'NextGen',
        'first episode': 101,
        'last episode': 277,
        'last episode per season': {
            1: 126,
            2: 148,
            3: 174,
            4: 200,
            5: 226,
            6: 252,
            7: 277
        }
    },
    'DS9': {
        'URL path': 'DS9',
        'first episode': 401,
        'last episode': 575,
        'last episode per season': {
            1: 420,
            2: 446,
            3: 472,
            4: 498,
            5: 524,
            6: 550,
            7: 575
        }
    },
    'TOS': {
        'URL path': 'StarTrek',
        'first episode': 1,
        'last episode': 79,
        'last episode per season': {
            1: 29,
            2: 55,
            3: 79
        }
    },
}

# parse command line arguments
parser = argparse.ArgumentParser(description='Scrape the transcripts of all episodes of certain series')

parser.add_argument('series', type=str, help=f'The series to scrape. Options: {", ".join(SERIES.keys())}')

args = parser.parse_args()

# make sure the series is valid
if args.series not in SERIES:
    print(f'Invalid series: {args.series}')
    exit()

config = SERIES[args.series]

with open(f'st-{args.series.lower()}-transcripts.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Episode', 'Season', 'Title', 'Location', 'Speaker', 'Context', 'Text'])

    for episode_number in tqdm(range(config['first episode'], config['last episode'] + 1)):
        url = 'http://chakoteya.net/{0}/{1}.htm'.format(config['URL path'], episode_number)

        r = requests.get(url)

        # if episode doesn't exist, skip it
        if r.status_code != 200:
            print('Episode {0} does not exist'.format(episode_number))
            continue

        # Get the season number
        for s in config['last episode per season']:
            if episode_number <= config['last episode per season'][s]:
                season = s
                break

        # add episode content to CSV
        episode_transcript = transcript_parsing.parse_episode(r.text)
        if episode_transcript is None:
            print('Episode {0} could not be parsed'.format(episode_number))
            continue
        for line in episode_transcript:
            writer.writerow([
                episode_number,
                season,
                line['title'],
                line['location'],
                line['speaker'],
                line['context'],
                line['text']
            ])
