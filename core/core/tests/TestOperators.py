import unittest

from core.queries.operators import compare


class TestOperators(unittest.TestCase):

    def test_equal(self):
        self.assertTrue(compare(10, "==", 10))

    def test_not_equal(self):
        self.assertTrue(compare(10, "!=", 20))

    def test_greater(self):
        self.assertTrue(compare(20, ">", 10))

    def test_greater_equal(self):
        self.assertTrue(compare(20, ">=", 20))

    def test_less(self):
        self.assertTrue(compare(10, "<", 20))

    def test_less_equal(self):
        self.assertTrue(compare(10, "<=", 10))

    def test_invalid_operator(self):
        with self.assertRaises(ValueError):
            compare(10, "=", 10)

    def test_incompatible_types(self):
        with self.assertRaises(ValueError):
            compare(10, ">", "twenty")


if __name__ == "__main__":
    unittest.main()
