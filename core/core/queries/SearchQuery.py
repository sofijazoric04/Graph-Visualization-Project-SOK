from datetime import date, datetime
from .GraphQuery import GraphQuery

class SearchQuery(GraphQuery):

    def __init__(self, text: str):
        if text is None:
            raise ValueError("Search text cannot be None")
        self.text = text.strip()

    def matches(self, node) -> bool:
        query = self.text.lower()
        # empty query returns the whole graph
        if not query:
            return True
        return self._matches_attribute_name(node, query) or self._matches_attribute_value(node, query)

    # true if some attribute name contains the query
    @staticmethod
    def _matches_attribute_name(node, query: str):
        for name in node.get_values().keys():
            if query in str(name).lower():
                return True
        return False

    # true if some attribute value contains the query
    @classmethod
    def _matches_attribute_value(cls, node, query: str):
        for value in node.get_values().values():
            if query in cls._value_to_text(value):
                return True
        return False

    # turns values into text only for searching needs
    @staticmethod
    def _value_to_text(value):
        if isinstance(value, (date, datetime)):
            return value.isoformat().lower()
        return str(value).lower()

    def __str__(self):
        return f"search: '{self.text}'"