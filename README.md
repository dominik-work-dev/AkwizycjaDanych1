# Indekser i wyszukiwarka dokumentów (Apache Beam + SQLite)

Projekt składa się z dwóch programów:

1. Indekser (`indexer.py`, Apache Beam) - wczytuje pliki `.txt`, nadaje im unikatowe
   identyfikatory, liczy reprezentację tf-idf i zapisuje wszystko do bazy SQLite.
2. Wyszukiwarka (`searcher.py`) - przetwarza zapytanie na tokeny i zwraca posortowaną
   listę dokumentów z bazy (id + ścieżka).

## Wymagania

- Python 3.12
- Apache Beam

## Instalacja

```
pip install -r requirements.txt
```
