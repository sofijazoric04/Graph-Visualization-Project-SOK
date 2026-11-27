from api.graph.Graph import Graph
from .GraphQuery import GraphQuery

# keeps the original graph and an ordered list of applied queriew
# every new query is applied to the result of the previous one
class QueryHistory:

    def __init__(self, original: Graph):
        if original is None:
            raise ValueError("Original graph cannot be None")
        self._original = original
        # list of (query, resulting_graph), in the order they were applied
        self._steps = []

    # current graph is either the result of the last query, or the original graph
    def current(self) -> Graph:
        if not self._steps:
            return self._original
        return self._steps[-1][1]

    def original(self) -> Graph:
        return self._original

    def apply(self, query: GraphQuery) -> Graph:
        if not isinstance(query, GraphQuery):
            raise TypeError("Query must be an instance of GraphQuery")
        result = query.apply(self.current())
        # we only get here if apply did not raise an exception
        self._steps.append((query, result))
        return result

    # removes the last query, returns it, or None if there was nothing to undo
    def undo(self):
        if not self._steps:
            return None
        query, _ = self._steps.pop()
        return query

    def reset(self) -> Graph:
        self._steps.clear()
        return self._original

    # keeps only the first `count` queries (ex. user clicks on the 2nd operation in the UI)
    def revert_to(self, count: int) -> Graph:
        if count < 0 or count > len(self._steps):
            raise IndexError(f"Invalid number of operations: {count}")
        del self._steps[count:]
        return self.current()

    # list of queries in the order they were applied
    def get_operations(self):
        return [query for query, _ in self._steps]

    # text description of the applied queries, for the UI
    def describe(self):
        return [str(query) for query, _ in self._steps]

    def has_operations(self):
        return len(self._steps) > 0

    def __len__(self):
        return len(self._steps)