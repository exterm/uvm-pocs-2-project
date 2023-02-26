from lib import transcript_parsing

def test_parse_speaker_line():
    assert transcript_parsing.parse_speaker_line('O\'Brien 2 [OC]: (chuckles) I should have known.') == {
        'speaker': 'O\'Brien 2',
        'context': 'chuckles',
        'text': 'I should have known.'
    }

def test_parse_speaker_line_with_no_context():
    assert transcript_parsing.parse_speaker_line('ODO [OC]: I should have known.') == {
        'speaker': 'Odo',
        'context': None,
        'text': 'I should have known.'
    }

def test_parse_speaker_line_with_no_oc():
    assert transcript_parsing.parse_speaker_line('ODO: I should have known.') == {
        'speaker': 'Odo',
        'context': None,
        'text': 'I should have known.'
    }

def test_parse_body():
    html = '''
    <td width="85%" align="left"> <font size="2" face="Arial, Helvetica, sans-serif"> <i>
    On Stardate 43997, Captain Jean-Luc Picard of the Federation Starship
    Enterprise...</i>
    </font>
    <p><font size="2" face="Arial, Helvetica, sans-serif"><b>[Saratoga - Bridge]</b>
    </font></p>
    <p><font size="2" face="Arial, Helvetica, sans-serif">LOCUTUS [on viewscreen]: Resistance is futile. You
    will disarm your weapons and escort us to sector zero zero one. If you
    attempt to intervene, we will destroy you. <br>
    CAPTAIN: (a Vulcan) Red alert. Load all torpedo bays. Ready phasers.
    Move us to position alpha, Ensign. <br>
    (The space battle begins) <br>
    TACTICAL: Aye, sir. </font></p>
    <p><font size="2" face="Arial, Helvetica, sans-serif"><b>[Corridor]</b>
    </font></p>
    '''

    print(transcript_parsing.parse_body(html))

    assert transcript_parsing.parse_body(html)[0:4] == [
        '(On Stardate 43997, Captain Jean-Luc Picard of the Federation Starship Enterprise...)',
        '[Saratoga - Bridge]',
        'LOCUTUS [on viewscreen]: Resistance is futile. You will disarm your weapons and escort us to sector zero zero one. If you attempt to intervene, we will destroy you.',
        'CAPTAIN: (a Vulcan) Red alert. Load all torpedo bays. Ready phasers. Move us to position alpha, Ensign.'
    ]

def test_parse_episode():
    html = open('tests/fixtures/401.htm').read()

    assert transcript_parsing.parse_episode(html)[0:5] == [
        {
            'title': 'Emissary',
            'location': None,
            'speaker': None,
            'context': 'On Stardate 43997, Captain Jean-Luc Picard of the Federation '
                       'Starship Enterprise was kidnapped for six days by an invading '
                       'force known as the Borg. Surgically altered, he was forced to '
                       'lead an assault on Starfleet at Wolf 359.',
            'text': None
        },
        {
            'title': 'Emissary',
            'location': 'Saratoga - Bridge',
            'speaker': 'Locutus',
            'context': None,
            'text': 'Resistance is futile. You will disarm your weapons and escort us to sector zero zero one. If you attempt to intervene, we will destroy you.'
        },
        {
            'title': 'Emissary',
            'location': 'Saratoga - Bridge',
            'speaker': 'Captain',
            'context': 'a Vulcan',
            'text': 'Red alert. Load all torpedo bays. Ready phasers. Move us to position alpha, Ensign.'
        },
        {
            'title': 'Emissary',
            'location': 'Saratoga - Bridge',
            'speaker': None,
            'context': 'The space battle begins',
            'text': None
        },
        {
            'title': 'Emissary',
            'location': 'Saratoga - Bridge',
            'speaker': 'Ops Officer',
            'context': 'woman',
            'text': "They've locked on."
        }
    ]


