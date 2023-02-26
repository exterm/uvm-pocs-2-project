# Scrape the transcripts of all episodes of Star Trek: Deep Space Nine
# Source: http://chakoteya.net/DS9/{episode}.htm (starting at 401)
# Output in CSV format. Columns: Episode, Season, Title, Location, Speaker, Context, Text

# TODO: Parse the location of the speaker
#   Example: LOCUTUS [on viewscreen]: Resistance is futile.

import csv
import requests

from tqdm import tqdm

from lib import transcript_parsing

FIRST_EPISODE = 401
LAST_EPISODE = 575
LAST_EPISODE_PER_SEASON = {
    1: 420,
    2: 446,
    3: 472,
    4: 498,
    5: 524,
    6: 550,
    7: 575
}

with open('ds9.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Episode', 'Season', 'Title', 'Location', 'Speaker', 'Context', 'Text'])

    for episode_number in tqdm(range(FIRST_EPISODE, LAST_EPISODE + 1)):
        url = 'http://chakoteya.net/DS9/{0}.htm'.format(episode_number)

        r = requests.get(url)

        # if episode doesn't exist, skip it
        if r.status_code != 200:
            print('Episode {0} does not exist'.format(episode_number))
            continue

        # Get the season number
        for s in LAST_EPISODE_PER_SEASON:
            if episode_number <= LAST_EPISODE_PER_SEASON[s]:
                season = s
                break

        # add episode content to CSV
        episode_transcript = transcript_parsing.parse_episode(r.text)
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
