import math


def cosine_similarity(vector_a, vector_b):
    """Podobieństwo cosinusowe dwóch słowników {token: waga}. Wynik od 0 do 1."""
    dot_product = 0.0
    for token, value in vector_a.items():
        if token in vector_b:
            dot_product += value * vector_b[token]

    sum_a = 0.0
    for value in vector_a.values():
        sum_a += value * value

    sum_b = 0.0
    for value in vector_b.values():
        sum_b += value * value

    if sum_a == 0 or sum_b == 0:
        return 0.0
    return dot_product / (math.sqrt(sum_a) * math.sqrt(sum_b))


def dot_product_similarity(vector_a, vector_b):
    dot_product = 0.0
    for token, value in vector_a.items():
        if token in vector_b:
            dot_product += value * vector_b[token]
    return dot_product
