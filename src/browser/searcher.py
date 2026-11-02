import argparse
import os

from src.indexer.indexer import DEFAULT_DB_PATH
from src.browser.similarity import cosine_similarity
from src.indexer.database import load_documents, load_idf
from src.indexer.tfidf import compute_tf, compute_tfidf
from src.indexer.tokenizer import tokenize


def make_query_vector(query, idf):
    """Zamienia zapytanie na słownik {token: tf-idf}."""
    tokens = tokenize(query)
    known_tokens = []
    for token in tokens:
        if token in idf:
            known_tokens.append(token)
    tf = compute_tf(known_tokens)
    return compute_tfidf(tf, idf)


def sort_key(result):
    """Klucz sortowania: najpierw najwyższy wynik, przy remisie mniejsze id."""
    doc_id, path, score = result
    return -score, doc_id


def search(query, documents, idf, similarity=cosine_similarity, limit=None):
    """Zwraca listę (id, ścieżka, wynik) posortowaną od najlepiej pasującego dokumentu."""
    query_vector = make_query_vector(query, idf)

    results = []
    for doc_id, path, vector in documents:
        score = similarity(query_vector, vector)
        if score > 0:
            results.append((doc_id, path, score))

    results.sort(key=sort_key)
    if limit is not None:
        results = results[:limit]
    return results


def search_in_database(query, db_path, similarity=cosine_similarity, limit=None):
    """Wczytuje indeks z bazy SQLite i wykonuje wyszukiwanie."""
    documents = load_documents(db_path)
    idf = load_idf(db_path)
    return search(query, documents, idf, similarity, limit)


def main():
    parser = argparse.ArgumentParser(description="Wyszukiwarka dokumentów")
    parser.add_argument("query")
    parser.add_argument("--db", default=DEFAULT_DB_PATH)
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()

    if not os.path.exists(args.db):
        print("Nie znaleziono bazy:", args.db)
        print("Najpierw uruchom indekser:  python run_indexer.py")
        return

    results = search_in_database(args.query, args.db, limit=args.top)
    if len(results) == 0:
        print("Brak wyników.")
        return

    place = 1
    for doc_id, path, score in results:
        print(f"{place}. id={doc_id}  wynik={score:.4f}  {path}")
        place += 1


if __name__ == "__main__":
    main()
