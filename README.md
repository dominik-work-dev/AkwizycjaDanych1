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
## Uruchamianie

```
python run_indexer.py
python run_searcher.py "kot i pies" - uruchomienie wyszukiwarki w terminalu
python run_gui.py - uruchomienie aplikacji z gui 
```

## Testy:

```
python -m unittest discover -s src -t . -v
```

## Fix dla WARNING:root:apitools not found, and bigquery client libraries are not available despite the import not raising an ImportError.
```
Get-ChildItem .venv\Lib\site-packages\apache_beam -Recurse -Filter *.pyd | Rename-Item -NewName { $_.Name + ".bak" }
python run_indexer.py
```