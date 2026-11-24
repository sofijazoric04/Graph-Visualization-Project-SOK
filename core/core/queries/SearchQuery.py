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
        for name, value in node.get_values().items():
            if query in str(name).lower():
                return True
            if query in self._value_to_text(value):
                return True
        return False

    @staticmethod
    def _value_to_text(value) -> str:
        # turns values into text only for searching needs
        if isinstance(value, (date, datetime)):
            return value.isoformat().lower()
        return str(value).lower()

    def __str__(self) -> str:
        return f"search: '{self.text}'"