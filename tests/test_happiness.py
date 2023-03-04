from lib import happiness

def test_score_text():
    scores = {'happy': 9.0, 'bad': 0.0 }
    assert happiness.score_text(['happy', 'bad', 'happy', 'noscore'], scores) == 6.0

def test_timeseries():
    scores = {'happy': 9.0, 'bad': 0.0 }
    assert happiness.timeseries(2, ['happy', 'bad', 'happy', 'noscore'], scores) == [4.5, 4.5, 9.0]

def test_timeseries_fast():
    scores = {'happy': 9.0, 'bad': 0.0 }
    assert happiness.timeseries_fast(2, ['happy', 'bad', 'happy', 'noscore'], scores) == [4.5, 4.5, 9.0]

def test_filter_kernel():
    scores = [5, 5, None]
    assert happiness.filter_kernel(scores, 0.0) == [None, None, None]

    scores = [4, 5, 6]
    assert happiness.filter_kernel(scores, 0.0) == [4, None, 6]

    scores = [4, 5, 6]
    assert happiness.filter_kernel(scores, 1.0) == [None, None, None]
