import os
import subprocess
import sys

import customtkinter as ctk

from src.browser.gui_helpers import all_documents_as_rows, format_header, format_row
from src.browser.searcher import search
from src.indexer.indexer import DEFAULT_DB_PATH, to_full_path
from src.indexer.database import load_documents, load_idf

FONT = ("Consolas", 13)
FONT_BOLD = ("Consolas", 13, "bold")


def open_file(path):
    full_path = to_full_path(path)
    if not os.path.exists(full_path):
        return False

    if sys.platform.startswith("win"):
        os.startfile(full_path)
    elif sys.platform == "darwin":
        subprocess.run(["open", full_path])
    else:
        subprocess.run(["xdg-open", full_path])
    return True


class SearchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Wyszukiwarka dokumentów")
        self.geometry("950x550")

        self.documents = []
        self.idf = {}

        # Pole z zapytaniem
        self.entry = ctk.CTkEntry(
            self, placeholder_text="Wpisz zapytanie", height=36
        )
        self.entry.pack(fill="x", padx=15, pady=(15, 5))
        self.entry.bind("<KeyRelease>", self.on_query_change)

        # Informacja pod polem (liczba wyników, błędy)
        self.status_label = ctk.CTkLabel(self, text="", anchor="w")
        self.status_label.pack(fill="x", padx=15)

        # Nagłówek tabeli
        self.header_label = ctk.CTkLabel(
            self, text=format_header(), anchor="w", font=FONT_BOLD
        )
        self.header_label.pack(fill="x", padx=20, pady=(5, 0))

        # Lista wierszy z przewijaniem
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.load_index()
        self.show_all_documents()

    def load_index(self):
        """Wczytuje indeks z bazy (raz, przy starcie programu)."""
        if not os.path.exists(DEFAULT_DB_PATH):
            self.status_label.configure(
                text="Nie znaleziono bazy. Najpierw uruchom indekser: python run_indexer.py"
            )
            return
        self.documents = load_documents(DEFAULT_DB_PATH)
        self.idf = load_idf(DEFAULT_DB_PATH)

    def show_all_documents(self):
        rows = all_documents_as_rows(self.documents)
        if len(self.documents) > 0:
            self.status_label.configure(
                text=f"Wszystkie dokumenty: {len(rows)}. Kliknij wiersz, żeby otworzyć plik."
            )
        self.show_rows(rows)

    def on_query_change(self, event=None):
        query = self.entry.get().strip()
        if event:
            print(
                "char =", repr(event.char),
                "keysym =", event.keysym,
                "keycode =", event.keycode
            )
        if event and event.keysym in ("Alt_R", "ISO_Level3_Shift", "Control_L", "Control_R", "Shift_L", "Shift_R"):
            return
        if query == "":
            self.show_all_documents()
            return
        results = search(query, self.documents, self.idf)
        if len(results) == 0:
            self.status_label.configure(text="Brak wyników.")
        else:
            self.status_label.configure(
                text=f"Wyniki: {len(results)}. Kliknij wiersz, żeby otworzyć plik."
            )
        self.show_rows(results)

    def show_rows(self, rows):
        """Usuwa stare wiersze i rysuje nowe (każdy wiersz to przycisk)."""
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for doc_id, path, score in rows:
            button = ctk.CTkButton(
                self.list_frame,
                text=format_row(doc_id, path, score),
                anchor="w",
                font=FONT,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray25"),
                # path=path zapamiętuje ścieżkę właśnie tego wiersza
                command=lambda path=path: self.open_document(path),
            )
            button.pack(fill="x", pady=1)

    def open_document(self, path):
        if not open_file(path):
            self.status_label.configure(text=f"Nie znaleziono pliku: {path}")


def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = SearchApp()
    app.mainloop()


if __name__ == "__main__":
    main()
