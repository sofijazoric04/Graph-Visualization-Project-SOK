"za pretragu regexa koristimo re"
import re
import ast
from datetime import date, datetime

from .GraphQuery import GraphQuery
from .operators import compare


class FilterQuery(GraphQuery):

    QUERY_PATTERN = re.compile(
        r"^\s*(.+?)\s*(==|!=|>=|<=|>|<)\s*(.*?)\s*$"
    )

    def __init__(self, text: str):
        if text is None:
            raise ValueError("Filter text cant be empty")

        match = self.QUERY_PATTERN.match(text)

        if not match:
            raise ValueError("Invalid filter format. Expected: <attribute> <operator> <value>")

        self.attribute = match.group(1).strip()
        self.operator = match.group(2)
        self.raw_value = match.group(3).strip()

        if not self.attribute:
            raise ValueError("Attribute name cannot be empty")

        if not self.raw_value:
            raise ValueError("Filter value cannot be empty")

        self._parse_quoted_value()

    def _parse_quoted_value(self):
        if self.raw_value.startswith(("'", '"')):
            try:
                value = ast.literal_eval(self.raw_value)
            except (ValueError, SyntaxError) as exc:
                raise ValueError("Invalid string literal") from exc

            if not isinstance(value, str):
                raise ValueError("Quoted filter values must be strings")

            return value

        return self.raw_value

    def _convert_value(self, node_value):
        value = self._parse_quoted_value()

        if isinstance(node_value, bool):
            if value.lower() not in ("true", "false"):
                raise ValueError("Expected a boolean value")
            return value.lower() == "true"

        if isinstance(node_value, datetime):
            try:
                return datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("Invalid datetime value") from exc

        if isinstance(node_value, date):
            try:
                return date.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("Invalid date value") from exc

        if isinstance(node_value, int):
            try:
                return int(value)
            except ValueError as exc:
                raise ValueError("Expected an integer value") from exc

        if isinstance(node_value, float):
            try:
                return float(value)
            except ValueError as exc:
                raise ValueError("Expected a float value") from exc

        if isinstance(node_value, str):
            return value

        raise ValueError("Unsupported attribute type: ", type(node_value).__name__)

    def matches(self, node) -> bool:
        values = node.get_values()

        if self.attribute not in values:
            return False

        node_value = values[self.attribute]
        filter_value = self._convert_value(node_value)

        return compare(
            node_value,
            self.operator,
            filter_value
        )

    def __str__(self):
        return "filter: "+ self.attribute+ " "+ self.operator+ " "+ self.raw_value
