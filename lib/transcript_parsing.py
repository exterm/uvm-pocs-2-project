import re
from bs4 import BeautifulSoup

def parse_speaker_line(line):
    speaker_line_regex = re.compile(r'(?P<speaker>[^\[:]+)( \[[^\]]+\])?: (?P<context>\(.*\) )?(?P<text>.*)')
    match = speaker_line_regex.match(line)

    if match:
        speaker = match.group('speaker').strip().title()
        context = match.group('context')
        if context:
            context = context[1:-2]
        text = match.group('text')

        return {
            'speaker': speaker,
            'context': context,
            'text': text
        }
    else:
        return None

def parse_body(contents):
    # remove all tags except <br/>, </p>, <i> and </i>
    contents = re.sub(r'<(?!br|p|i|/i).*?>', '', contents)

    stripped_lines = []
    # strip each line and combine into one string
    for line in contents.splitlines():
        line = line.strip()
        if line:
            stripped_lines.append(line)

    contents = ' '.join(stripped_lines)

    # insert actual line breaks
    contents = re.sub(r'<br/?>', '\n', contents)
    contents = re.sub(r'</?p>', '\n', contents)

    # replace <i> and </i> with parentheses
    contents = re.sub(r'<i>\s*', '(', contents)
    contents = re.sub(r'\s*</i>', ')', contents)

    lines = []
    for line in contents.splitlines():
        line = line.strip()
        if line:
            lines.append(line)

    return lines

def parse_episode(text):
    transcript = []

    soup = BeautifulSoup(text, 'html5lib').body

    if not soup:
        return None

    # Get the title of the episode
    title = soup.select('body font > b')[0].text
    title = re.sub(r'\s+', ' ', title).strip()

    transcript_body = soup.select('body > div')[0]

    contents = str(transcript_body.contents[1])
    lines = parse_body(contents)

    location = None

    # Loop through each line
    for line in lines:
        # skip empty lines
        if not line:
            continue

        # new scene?
        if line.startswith('['):
            location = line[1:-1].lower()
            continue

        # Parse pure context line
        # Example:
        #   (The gangly youth is fishing off a covered bridge)
        if line.startswith('('):
            context = line[1:-1]
            transcript.append({
                'title': title,
                'location': location,
                'speaker': None,
                'context': context,
                'text': None
            })
            continue

        # Parse speaker line
        parsed_line = parse_speaker_line(line)
        if parsed_line:
            transcript.append({
                'title': title,
                'location': location,
                'speaker': parsed_line['speaker'],
                'context': parsed_line['context'],
                'text': parsed_line['text']
            })
        else:
            # Narrator line
            transcript.append({
                'title': title,
                'location': location,
                'speaker': 'Narrator',
                'context': None,
                'text': line
            })

    return transcript
