import unittest

from src.indexer.tfidf import assign_ids, compute_idf, compute_tf, compute_tfidf


class TestAssignIds(unittest.TestCase):
    def test_ids_are_unique(self):
        result = assign_ids(["b.txt", "a.txt", "c.txt"])
        ids = [doc_id for doc_id, _ in result]
        self.assertEqual(len(ids), len(set(ids)))

    def test_ids_follow_sorted_paths(self):
        result = assign_ids(["b.txt", "a.txt"])
        self.assertEqual(result, [(1, "a.txt"), (2, "b.txt")])

    def test_empty_list(self):
        self.assertEqual(assign_ids([]), [])


class TestComputeTf(unittest.TestCase):
    def test_counts_divided_by_length(self):
        tf = compute_tf(["kot", "kot", "pies", "ryba"])
        self.assertEqual(tf, {"kot": 0.5, "pies": 0.25, "ryba": 0.25})

    def test_empty_tokens(self):
        self.assertEqual(compute_tf([]), {})

    def test_values_sum_to_one(self):
        tf = compute_tf(["a", "b", "b", "c", "c", "c"])
        self.assertAlmostEqual(sum(tf.values()), 1.0)


class TestComputeIdf(unittest.TestCase):
    def test_rarer_token_has_higher_idf(self):
        self.assertGreater(compute_idf(1, 10), compute_idf(9, 10))

    def test_idf_is_positive_for_single_document(self):
        self.assertGreater(compute_idf(1, 1), 0)

    def test_token_in_all_documents(self):
        self.assertAlmostEqual(compute_idf(5, 5), 1.0)


class TestComputeTfidf(unittest.TestCase):
    def test_multiplies_tf_by_idf(self):
        vector = compute_tfidf({"kot": 0.5, "pies": 0.5}, {"kot": 2.0, "pies": 1.0})
        self.assertEqual(vector, {"kot": 1.0, "pies": 0.5})

    def test_empty_tf(self):
        self.assertEqual(compute_tfidf({}, {"kot": 1.0}), {})


if __name__ == "__main__":
    unittest.main()
