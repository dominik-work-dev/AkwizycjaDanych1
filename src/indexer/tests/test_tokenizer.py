import unittest

from src.indexer.tokenizer import tokenize


class TestTokenize(unittest.TestCase):
    def test_lowercase_and_punctuation(self):
        self.assertEqual(tokenize("Kot, PIES!"), ["kot", "pies"])

    def test_stop_words_removed(self):
        self.assertEqual(tokenize("kot i pies w domu"), ["kot", "pies", "domu"])

    def test_empty_text(self):
        self.assertEqual(tokenize(""), [])

    def test_only_stop_words(self):
        self.assertEqual(tokenize("i w na"), [])

    def test_polish_letters(self):
        self.assertEqual(tokenize("Zażółć gęślą jaźń"), ["zażółć", "gęślą", "jaźń"])

    def test_custom_stop_words(self):
        self.assertEqual(tokenize("kot pies", stop_words={"kot"}), ["pies"])


if __name__ == "__main__":
    unittest.main()
