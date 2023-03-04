from collections import Counter

from tqdm import tqdm

# the average happiness of a text is the sum of the happiness of each word times the relative frequency of that word
def score_text(words, scores):
    word_counts = Counter(words)
    scorable_types = [word for word in word_counts if word in scores]
    scorable_tokens = [word for word in words if word in scores]
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

def timeseries_fast(window_size, words: list[str], scores: dict[str, float], lens: float = 0.0):
    word_scores = [scores.get(word) for word in words]

    word_scores = filter_kernel(word_scores, lens)

    timeseries = []
    for i in tqdm(range(len(word_scores) - window_size + 1)):
        window = [x for x in word_scores[i:i + window_size] if x is not None]
        if len(window) == 0:
            timeseries.append(None)
        else:
            timeseries.append(sum(window) / len(window))

    return timeseries
