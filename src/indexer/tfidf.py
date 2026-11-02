import math
from collections import Counter


def assign_ids(paths):
    """Nadaje każdej ścieżce unikatowy numer (1, 2, 3..) według kolejności alfabetycznej."""
    sorted_paths = sorted(paths)
    result=[]
    number=1
    for path in sorted_paths:
        result.append((number, path))
        number += 1
    return result


def compute_tf(tokens):
    """Częstość tokenu w dokumencie: liczba wystąpień / liczba wszystkich tokenów."""
    if len(tokens) == 0:
        return {}
    total=len(tokens)
    counts=Counter(tokens)
    tf={}
    for token, count in counts.items():
        tf[token] = count / total
    return tf


def compute_idf(df, n):
    """IDF: log((1 + N) / (1 + df)) + 1.
    Dodaje jeden, żeby nie było zerowe
    """
    return math.log((1 + n) / (1 + df)) + 1


def compute_tfidf(tf, idf):
    """Mnoży tf każdego tokenu przez jego idf. Wynik:{token: waga}."""
    vector={}
    for token, tf_value in tf.items():
        vector[token] = tf_value * idf[token]
    return vector
