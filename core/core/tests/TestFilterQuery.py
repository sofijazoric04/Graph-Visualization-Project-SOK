import unittest
from datetime import date
from core.queries.FilterQuery import FilterQuery

class FakeNode:
    def __init__(self, values):
        self.values = values

    def get_values(self):
        return self.values


class TestFilterQuery(unittest.TestCase):
    def test_integer_filter(self):
        query = FilterQuery("age >= 25")

        node = FakeNode({"age": 30})

        self.assertTrue(query.matches(node))

    def test_integer_filter_false(self):
        query = FilterQuery("age > 25")

        node = FakeNode({"age": 20})

        self.assertFalse(query.matches(node))

    def test_string_filter(self):
        query = FilterQuery('name == "Marko"')

        node = FakeNode({"name": "Marko"})

        self.assertTrue(query.matches(node))

    def test_missing_attribute(self):
        query = FilterQuery("age > 20")

        node = FakeNode({"name": "Marko"})

        self.assertFalse(query.matches(node))

    def test_boolean_filter(self):
        query = FilterQuery("active == true")

        node = FakeNode({"active": True})

        self.assertTrue(query.matches(node))

    def test_date_filter(self):
        query = FilterQuery("created > 2025-01-01")

        node = FakeNode({
            "created": date(2025, 5, 1)
        })

        self.assertTrue(query.matches(node))

    def test_invalid_integer_value(self):
        query = FilterQuery("age > abc")

        node = FakeNode({"age": 25})

        with self.assertRaises(ValueError):
            query.matches(node)

    def test_invalid_query(self):
        with self.assertRaises(ValueError):
            FilterQuery("age approximately 25")

    def test_empty_query(self):
        with self.assertRaises(ValueError):
            FilterQuery("")

    def test_string_representation(self):
        query = FilterQuery("age >= 25")

        self.assertEqual(str(query), "filter: age >= 25")


if __name__ == "__main__":
    unittest.main()
