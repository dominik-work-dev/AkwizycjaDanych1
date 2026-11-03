import unittest

from src.browser.similarity import cosine_similarity


class TestCosineSimilarity(unittest.TestCase):
    def test_identical_vectors(self):
        vector = {"kot": 1.0, "pies": 2.0}
        self.assertAlmostEqual(cosine_similarity(vector, vector), 1.0)

    def test_no_common_tokens(self):
        self.assertEqual(cosine_similarity({"kot": 1.0}, {"pies": 1.0}), 0.0)

    def test_partial_overlap(self):
        # (1*1) / (sqrt(1) * sqrt(2)) = 0.7071
        result = cosine_similarity({"kot": 1.0}, {"kot": 1.0, "pies": 1.0})
        self.assertAlmostEqual(result, 0.7071, places=4)

    def test_scaling_does_not_change_result(self):
        small = cosine_similarity({"kot": 1.0}, {"kot": 1.0, "pies": 1.0})
        big = cosine_similarity({"kot": 10.0}, {"kot": 1.0, "pies": 1.0})
        self.assertAlmostEqual(small, big)

    def test_empty_vector(self):
        self.assertEqual(cosine_similarity({}, {"kot": 1.0}), 0.0)
        self.assertEqual(cosine_similarity({}, {}), 0.0)


if __name__ == "__main__":
    unittest.main()
