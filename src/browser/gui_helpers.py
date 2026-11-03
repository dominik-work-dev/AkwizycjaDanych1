import os


def all_documents_as_rows(documents):
    """Zamienia dokumenty z bazy na wiersze (id, ścieżka, wynik) posortowane po id.

    Wynik to None, bo przy zwykłej liście dokumentów nie ma zapytania.
    """
    rows = []
    for doc_id, path, vector in documents:
        rows.append((doc_id, path, None))
    rows.sort()
    return rows


def format_header():
    """Nagłówek tabeli (te same szerokości kolumn co w format_row)."""
    return f"{'ID':<5}{'Nazwa':<30}{'Wynik':<9}Ścieżka"


def format_row(doc_id, path, score):
    """Tekst jednego wiersza: id, nazwa pliku, wynik i ścieżka."""
    name = os.path.basename(path)
    if len(name) > 28:
        name = name[:25] + "..."

    if score is None:
        score_text = "-"
    else:
        score_text = f"{score:.4f}"

    return f"{doc_id:<5}{name:<30}{score_text:<9}{path}"
