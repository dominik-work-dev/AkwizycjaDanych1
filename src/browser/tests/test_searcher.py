import os
import tempfile
import unittest

from src.indexer.database import init_db, save_index
from src.browser.searcher import make_query_vector, search, search_in_database


def sample_documents():
    return [
        (1, "a.txt", {"kot": 1.0}),
        (2, "b.txt", {"pies": 1.0}),
        (3, "c.txt", {"kot": 1.0, "pies": 1.0}),
    ]

def sample_idf():
    return {"kot": 1.0, "pies": 1.0, "ryba": 1.0}


class TestMakeQueryVector(unittest.TestCase):
    def test_weights_are_tf_times_idf(self):
        vector = make_query_vector("kot kot pies", {"kot": 2.0, "pies": 1.0})
        self.assertAlmostEqual(vector["kot"], (2 / 3) * 2.0)
        self.assertAlmostEqual(vector["pies"], (1 / 3) * 1.0)

    def test_stop_words_skipped(self):
        vector = make_query_vector("kot i pies", sample_idf())
        self.assertEqual(sorted(vector.keys()), ["kot", "pies"])

    def test_unknown_words_skipped(self):
        vector = make_query_vector("kot smok", sample_idf())
        self.assertEqual(list(vector.keys()), ["kot"])

    def test_empty_query(self):
        self.assertEqual(make_query_vector("", sample_idf()), {})


class TestSearch(unittest.TestCase):
    def test_results_sorted_by_score(self):
        results = search("kot", sample_documents(), sample_idf())
        ids = [doc_id for doc_id, _, _ in results]
        # dokument 1 pasuje idealnie, dokument 3 częściowo, dokument 2 wcale
        self.assertEqual(ids, [1, 3])

    def test_results_contain_paths(self):
        results = search("pies", sample_documents(), sample_idf())
        self.assertEqual(results[0][:2], (2, "b.txt"))

    def test_stop_words_in_query_ignored(self):
        with_stop_word = search("kot i", sample_documents(), sample_idf())
        without = search("kot", sample_documents(), sample_idf())
        self.assertEqual(with_stop_word, without)

    def test_unknown_word_gives_no_results(self):
        self.assertEqual(search("smok", sample_documents(), sample_idf()), [])

    def test_only_stop_words_gives_no_results(self):
        self.assertEqual(search("i w na", sample_documents(), sample_idf()), [])

    def test_limit(self):
        results = search("kot pies", sample_documents(), sample_idf(), limit=1)
        self.assertEqual(len(results), 1)

    def test_equal_scores_sorted_by_id(self):
        documents = [(5, "e.txt", {"kot": 1.0}), (2, "b.txt", {"kot": 1.0})]
        results = search("kot", documents, sample_idf())
        self.assertEqual([r[0] for r in results], [2, 5])

    def test_similarity_function_can_be_replaced(self):
        def score_is_id(query_vector, doc_vector):
            return 1.0 if doc_vector == {"pies": 1.0} else 0.5

        results = search("kot", sample_documents(), sample_idf(), similarity=score_is_id)
        self.assertEqual([r[0] for r in results], [2, 1, 3])


class TestSearchInDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        init_db(self.db_path)
        idf_items = list(sample_idf().items())
        save_index(self.db_path, sample_documents(), idf_items)

    def test_search_reads_index_from_database(self):
        results = search_in_database("kot", self.db_path)
        self.assertEqual([r[0] for r in results], [1, 3])
        self.assertEqual(results[0][1], "a.txt")


if __name__ == "__main__":
    unittest.main()
