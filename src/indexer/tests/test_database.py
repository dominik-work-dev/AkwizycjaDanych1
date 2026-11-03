import os
import tempfile
import unittest

from src.indexer.database import init_db, load_documents, load_idf, save_index


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Każdy test dostaje własny, pusty plik bazy w nowym folderze tymczasowym.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        init_db(self.db_path)

    def test_new_database_is_empty(self):
        self.assertEqual(load_documents(self.db_path), [])
        self.assertEqual(load_idf(self.db_path), {})

    def test_save_and_load_documents(self):
        documents = [(1, "a.txt", {"kot": 0.5}), (2, "b.txt", {"pies": 1.0})]
        save_index(self.db_path, documents, [])
        self.assertEqual(load_documents(self.db_path), documents)

    def test_save_and_load_idf(self):
        save_index(self.db_path, [], [("kot", 1.5), ("pies", 2.0)])
        self.assertEqual(load_idf(self.db_path), {"kot": 1.5, "pies": 2.0})

    def test_init_db_clears_old_data(self):
        save_index(self.db_path, [(1, "a.txt", {"kot": 1.0})], [("kot", 1.0)])
        init_db(self.db_path)
        self.assertEqual(load_documents(self.db_path), [])


if __name__ == "__main__":
    unittest.main()
