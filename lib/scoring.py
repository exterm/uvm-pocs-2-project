from collections import Counter

from tqdm import tqdm

# the average score of a text is the sum of the score of each word times the relative frequency of that word
def score_text(words, scores, lens: float = 0):
    word_counts = Counter(words)

    # filter out words that are within [average - lens, average + lens] of the average
    average = 5
    filter = lambda x: None if x is not None and x >= average - lens and x <= average + lens else x
    scores = {k: v for k, v in scores.items() if filter(v) is not None}

    # compute the average score of the text
    scorable_types = [word for word in word_counts if word in scores]
    scorable_tokens = [word for word in words if word in scores]
    if len(scorable_tokens) == 0:
        return None
    return sum([scores[word] * (word_counts[word] / len(scorable_tokens)) for word in scorable_types])

def timeseries(window_size, words, scores):
    return [score_text(words[i:i + window_size], scores) for i in tqdm(range(len(words) - window_size + 1))]

def filter_kernel(word_scores, lens):
    # not_none = [x for x in word_scores if x is not None]
    # average = sum(not_none) / len(not_none)
    average = 5

    # replace all scores that are within [average - lens, average + lens] with None
    filter = lambda x: None if x is not None and x >= average - lens and x <= average + lens else x
    return list(map(filter, word_scores))

def timeseries_fast(window_size, words: list[str], scores: dict[str, float], lens: float = 0.0, progress_bar: bool = True):
    word_scores = [scores.get(word) for word in words]

    word_scores = filter_kernel(word_scores, lens)

    timeseries = []
    for i in conditional_tqdm(range(len(word_scores) - window_size + 1), progress_bar):
        window = [x for x in word_scores[i:i + window_size] if x is not None]
        if len(window) == 0:
            timeseries.append(None)
        else:
            timeseries.append(sum(window) / len(window))

    return timeseries

def conditional_tqdm(iterable, condition):
    if condition:
        return tqdm(iterable)
    else:
        return iterable
