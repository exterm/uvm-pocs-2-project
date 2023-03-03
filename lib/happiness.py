from collections import Counter

from tqdm import tqdm

# the average happiness of a text is the sum of the happiness of each word times the relative frequency of that word
def score_text(words, scores):
    word_counts = Counter(words)
    total_words = len(words)
    scorable_words = [word for word in word_counts if word in scores]
    return sum([scores[word] * (word_counts[word] / total_words) for word in scorable_words])

def timeseries(window_size, words, scores):
    return [score_text(words[i:i + window_size], scores) for i in tqdm(range(len(words) - window_size + 1))]

def timeseries_fast(window_size, words: list[str], scores: dict[str, float]):
    all_scores = [scores.get(word) for word in words]

    timeseries = []
    for i in tqdm(range(len(all_scores) - window_size + 1)):
        window = all_scores[i:i + window_size]
        timeseries.append(sum([x for x in window if x is not None]) / len(window))

    return timeseries
