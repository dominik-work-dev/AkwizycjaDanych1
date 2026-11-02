import json
import os
import sqlite3


def init_db(db_path):
    """Tworzy puste tabele."""
    folder = os.path.dirname(os.path.abspath(db_path))
    os.makedirs(folder, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DROP TABLE IF EXISTS documents")
        conn.execute("DROP TABLE IF EXISTS idf")
        conn.execute(
            "CREATE TABLE documents ("
            "id INTEGER PRIMARY KEY, path TEXT NOT NULL, vector TEXT NOT NULL)"
        )
        conn.execute("CREATE TABLE idf (token TEXT PRIMARY KEY, value REAL NOT NULL)")
        conn.commit()
    finally:
        conn.close()


def save_index(db_path, documents, idf_items):
    """Zapisuje dokumenty [(id, ścieżka, słownik)] oraz wartości idf [(token, idf)]."""
    conn = sqlite3.connect(db_path)
    try:
        for doc_id, path, vector in documents:
            conn.execute(
                "INSERT INTO documents (id, path, vector) VALUES (?, ?, ?)",
                (doc_id, path, json.dumps(vector)),
            )
        for token, value in idf_items:
            conn.execute("INSERT INTO idf (token, value) VALUES (?, ?)", (token, value))
        conn.commit()
    finally:
        conn.close()


def load_documents(db_path):
    """Zwraca listę (id, ścieżka, słownik tf-idf)."""
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT id, path, vector FROM documents ORDER BY id").fetchall()
    finally:
        conn.close()
    result = []
    for doc_id, path, vector_text in rows:
        result.append((doc_id, path, json.loads(vector_text)))
    return result


def load_idf(db_path):
    """Zwraca słownik {token: idf}."""
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT token, value FROM idf").fetchall()
    finally:
        conn.close()
    return dict(rows)
