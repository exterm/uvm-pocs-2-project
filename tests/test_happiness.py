from lib import happiness

def test_score_text():
    scores = {'happy':9, 'bad':0 }
    assert happiness.score_text(['happy', 'happy', 'bad', 'noscore'], scores) == 4.5

def test_timeseries():
    scores = {'happy':9, 'bad':0 }
    assert happiness.timeseries(2, ['happy', 'happy', 'bad', 'noscore'], scores) == [9, 4.5, 0]

def test_timeseries_fast():
    scores = {'happy':9, 'bad':0 }
    assert happiness.timeseries_fast(2, ['happy', 'happy', 'bad', 'noscore'], scores) == [9, 4.5, 0]
