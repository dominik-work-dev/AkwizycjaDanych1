import os
import tempfile
import unittest

from src.indexer.database import load_documents, load_idf
from src.indexer.indexer import build_index, find_files, make_idf_item, make_tf, make_vector, tokens_of_document


class TestTransformFunctions(unittest.TestCase):
    """Testy pojedynczych kroków potoku (bez uruchamiania Beam)."""

    def test_make_tf_skips_stop_words(self):
        doc_id, path, tf = make_tf((1, "a.txt", "kot i kot"))
        self.assertEqual((doc_id, path), (1, "a.txt"))
        self.assertEqual(tf, {"kot": 1.0})

    def test_tokens_of_document_gives_one_pair_per_token(self):
        pairs = tokens_of_document((1, "a.txt", {"kot": 0.5, "pies": 0.5}))
        self.assertEqual(sorted(pairs), [("kot", 1), ("pies", 1)])

    def test_make_idf_item(self):
        token, value = make_idf_item(("kot", 1), 1)
        self.assertEqual(token, "kot")
        self.assertGreater(value, 0)

    def test_make_vector(self):
        result = make_vector((1, "a.txt", {"kot": 0.5}), {"kot": 2.0})
        self.assertEqual(result, (1, "a.txt", {"kot": 1.0}))


class TestBuildIndex(unittest.TestCase):
    """Test całego potoku na małych plikach tymczasowych."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.db_path = os.path.join(self.temp_dir.name, "test.db")

    def make_file(self, name, text):
        path = os.path.join(self.temp_dir.name, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_find_files_only_txt(self):
        self.make_file("a.txt", "kot")
        self.make_file("b.md", "pies")
        found = find_files(self.temp_dir.name)
        self.assertEqual([os.path.basename(p) for p in found], ["a.txt"])

    def test_documents_saved_with_unique_ids_and_paths(self):
        a = self.make_file("a.txt", "kot pies")
        b = self.make_file("b.txt", "pies ryba")
        build_index([a, b], self.db_path)
        docs = load_documents(self.db_path)
        self.assertEqual(len(docs), 2)
        self.assertEqual([d[0] for d in docs], [1, 2])
        self.assertEqual([d[1] for d in docs], [a, b])

    def test_rare_word_weighs_more_than_common_word(self):
        a = self.make_file("a.txt", "kot pies")
        b = self.make_file("b.txt", "pies ryba")
        build_index([a, b], self.db_path)
        docs = load_documents(self.db_path)
        vector_a = docs[0][2]
        # "pies" jest w obu dokumentach, "kot" tylko w jednym
        self.assertGreater(vector_a["kot"], vector_a["pies"])

    def test_idf_saved(self):
        a = self.make_file("a.txt", "kot")
        build_index([a], self.db_path)
        self.assertIn("kot", load_idf(self.db_path))

    def test_stop_words_not_in_index(self):
        a = self.make_file("a.txt", "kot i pies")
        build_index([a], self.db_path)
        vector = load_documents(self.db_path)[0][2]
        self.assertNotIn("i", vector)


if __name__ == "__main__":
    unittest.main()
