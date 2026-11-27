import operator

OPERATORS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}


def compare(left, operator_symbol: str, right) -> bool:

    if operator_symbol not in OPERATORS:
        raise ValueError("unsupported operator:", operator_symbol)

    try:
        return OPERATORS[operator_symbol](left, right)
    except TypeError as exc:
        raise ValueError("Cannot compare these types: ", type(left).__name__, " ", type(right).__name__) from exc