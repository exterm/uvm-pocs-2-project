from lib import scoring

def test_score_text():
    scores = {'happy': 9.0, 'bad': 0.0 }
    assert scoring.score_text(['happy', 'bad', 'happy', 'noscore'], scores) == 6.0

def test_score_text_when_no_scorable_tokens():
    scores = {'happy': 9.0, 'bad': 0.0 }
    assert scoring.score_text(['noscore'], scores) == None

def test_timeseries():
    scores = {'happy': 9.0, 'bad': 0.0 }
    assert scoring.timeseries(2, ['happy', 'bad', 'happy', 'noscore'], scores) == [4.5, 4.5, 9.0]

def test_timeseries_fast():
    scores = {'happy': 9.0, 'bad': 0.0 }
    assert scoring.timeseries_fast(2, ['happy', 'bad', 'happy', 'noscore'], scores) == [4.5, 4.5, 9.0]

def test_filter_kernel():
    scores = [5, 5, None]
    assert scoring.filter_kernel(scores, 0.0) == [None, None, None]

    scores = [4, 5, 6]
    assert scoring.filter_kernel(scores, 0.0) == [4, None, 6]

    scores = [4, 5, 6]
    assert scoring.filter_kernel(scores, 1.0) == [None, None, None]
