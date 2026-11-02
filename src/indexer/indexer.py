import argparse
import os

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

from src.indexer.database import init_db, save_index
from src.indexer.tfidf import assign_ids, compute_idf, compute_tf, compute_tfidf
from src.indexer.tokenizer import tokenize
from src.indexer.file_pathing import to_full_path, to_project_path, DEFAULT_DB_PATH, DEFAULT_DOCS_FOLDER


def read_document(item):
    """(id, ścieżka) -> (id, ścieżka, tekst)"""
    doc_id, path = item
    with open(to_full_path(path), encoding="utf-8") as f:
        text = f.read()
    return doc_id, path, text


def make_tf(doc):
    """(id, ścieżka, tekst) -> (id, ścieżka, {token: tf})"""
    doc_id, path, text = doc
    return doc_id, path, compute_tf(tokenize(text))


def tokens_of_document(doc):
    """(id, ścieżka, tf) -> [(token, 1), ...] - po jednej parze na każdy unikatowy token."""
    tf = doc[2]
    pairs = []
    for token in tf:
        pairs.append((token, 1))
    return pairs


def make_idf_item(pair, n_docs):
    """(token, liczba dokumentów z tokenem) -> (token, idf)"""
    token, doc_freq = pair
    return token, compute_idf(doc_freq, n_docs)


def make_vector(doc, idf):
    """(id, ścieżka, tf) -> (id, ścieżka, {token: tf-idf})"""
    doc_id, path, tf = doc
    return doc_id, path, compute_tfidf(tf, idf)


def save_all(documents, db_path, idf_items):
    """Zapisuje wszystko do bazy SQLite (jeden zapis, żeby uniknąć blokad pliku)."""
    save_index(db_path, documents, idf_items)


def build_index(paths, db_path):
    """Potok beam"""
    init_db(db_path)

    with beam.Pipeline(options=PipelineOptions([])) as pipeline:
        # 1. Id + wczytanie tekstu
        docs = (pipeline | "Lista dokumentow" >> beam.Create(assign_ids(paths)) | "Wczytaj pliki" >> beam.Map(read_document))

        # 2. tf dla każdego dokumentu
        tf_docs = docs | "Policz tf" >> beam.Map(make_tf)

        # 3. Liczba dokumentów (N)
        n_docs = tf_docs | "Policz dokumenty" >> beam.combiners.Count.Globally()

        # 4. idf: w ilu dokumentach występuje token
        idf = (tf_docs | "Tokeny dokumentu" >> beam.FlatMap(tokens_of_document) | "Policz df" >> beam.CombinePerKey(sum) | "Policz idf" >> beam.Map(make_idf_item, beam.pvalue.AsSingleton(n_docs)))

        # 5. tf-idf dla każdego dokumentu
        vectors = tf_docs | "Policz tf-idf" >> beam.Map(make_vector, beam.pvalue.AsDict(idf))

        # 6. Zapis do bazy
        (
            vectors | "Zbierz w liste" >> beam.combiners.ToList() | "Zapisz do bazy" >> beam.Map(save_all, db_path, beam.pvalue.AsList(idf))
        )


def find_files(folder: str):
    """Zwraca ścieżki wszystkich plików .txt w folderze (razem z podfolderami).

    Ścieżki leżące w projekcie są zapisywane względem głównego folderu projektu.
    """
    paths = []
    for root, _, files in os.walk(folder):
        for name in files:
            if name.endswith(".txt"):
                paths.append(to_project_path(os.path.join(root, name)))
    return paths


def main():
    parser = argparse.ArgumentParser(description="Indekser dokumentów")
    parser.add_argument("folder", nargs="?", default=DEFAULT_DOCS_FOLDER)
    parser.add_argument("--db", default=DEFAULT_DB_PATH)
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print("Nie ma takiego folderu:", args.folder)
        return

    paths = find_files(args.folder)
    if len(paths) == 0:
        print("Nie znaleziono plików .txt w folderze:", args.folder)
        return

    build_index(paths, args.db)
    print("Zaindeksowano dokumentów:", len(paths))
    print("Baza zapisana w:", os.path.abspath(args.db))


if __name__ == "__main__":
    main()
