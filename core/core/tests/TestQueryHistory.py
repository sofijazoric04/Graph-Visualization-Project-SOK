import unittest
from datetime import date, datetime
from api.graph.Graph import Graph
from api.graph.Node import Node
from api.graph.Edge import Edge
from core.queries.SearchQuery import SearchQuery
from core.queries.FilterQuery import FilterQuery
from core.queries.QueryHistory import QueryHistory
# running tests:
# cd core
# python -m unittest core.tests.TestQueryHistory -v

# helpers
def make_node(**values):
    node = Node()
    for name, value in values.items():
        node.add_value(name, value)
    return node

def node_ids(graph):
    return set(graph.get_nodes().keys())

def edge_ids(graph):
    return set(graph.get_edges().keys())

# general history
class TestQueryHistory(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(directed=True)
        self.john = make_node(first="John", last="Doe", years=53, born=date(1972, 3, 1))
        self.mike = make_node(first="Mike", last="Doe", years=25, born=date(2000, 6, 15))
        self.lucy = make_node(first="Lucy", last="Doe", years=15, born=date(2010, 9, 20))
        self.anna = make_node(first="Anna", last="Smith", years=40, born=date(1985, 1, 10))
        self.mark = make_node(first="Mark", last="Smith", years=30, born=date(1995, 11, 5))
        for n in (self.john, self.mike, self.lucy, self.anna, self.mark):
            self.graph.add_node(n)
        self.edges = [
            Edge(self.john, self.mike),
            Edge(self.john, self.lucy),
            Edge(self.mike, self.john),   # cycle
            Edge(self.anna, self.mark),
            Edge(self.mark, self.john),
        ]
        for e in self.edges:
            self.graph.add_edge(e)
        self.history = QueryHistory(self.graph)

    # without operations the current graph is the original
    def test_initial_state_is_original(self):
        self.assertIs(self.history.current(), self.graph)
        self.assertEqual(self.history.get_operations(), [])
        self.assertFalse(self.history.has_operations())

    def test_filter_search_filter_gives_expected_g4(self):
        g2 = self.history.apply(FilterQuery("years > 20"))
        self.assertEqual(node_ids(g2), {self.john.node_id, self.mike.node_id, self.anna.node_id, self.mark.node_id})

        g3 = self.history.apply(SearchQuery("doe"))
        self.assertEqual(node_ids(g3), {self.john.node_id, self.mike.node_id})
        self.assertEqual(edge_ids(g3), {self.edges[0].edge_id, self.edges[2].edge_id})

        g4 = self.history.apply(FilterQuery("years < 50"))
        self.assertEqual(node_ids(g4), {self.mike.node_id})
        self.assertEqual(edge_ids(g4), set())
        self.assertIs(self.history.current(), g4)

    def test_chain_with_date_and_string_filter(self):
        self.history.apply(FilterQuery("born >= 1990-01-01"))
        self.history.apply(SearchQuery("o"))
        result = self.history.apply(FilterQuery('last == "Smith"'))
        self.assertEqual(node_ids(result), {self.mark.node_id})

    # each query works on the previous result, not on the original
    def test_query_is_applied_to_previous_result(self):
        self.history.apply(SearchQuery("smith"))
        result = self.history.apply(SearchQuery("doe"))
        self.assertEqual(node_ids(result), set())

    def test_edges_are_kept_between_remaining_nodes(self):
        self.history.apply(SearchQuery("doe"))
        result = self.history.apply(FilterQuery("years >= 25"))
        self.assertEqual(edge_ids(result), {self.edges[0].edge_id, self.edges[2].edge_id})

    def test_result_keeps_directed_flag(self):
        result = self.history.apply(SearchQuery("doe"))
        self.assertTrue(result.is_directed())

    def test_reset_returns_original_at_any_point(self):
        queries = [FilterQuery("years > 20"), SearchQuery("doe"), FilterQuery("years < 50")]
        for query in queries:
            self.history.apply(query)
            result = self.history.reset()
            self.assertIs(result, self.graph)
            self.assertIs(self.history.current(), self.graph)
            self.assertEqual(node_ids(result), node_ids(self.graph))
            self.assertEqual(edge_ids(result), edge_ids(self.graph))
            self.assertEqual(self.history.get_operations(), [])

    def test_reset_in_the_middle_of_chain(self):
        self.history.apply(FilterQuery("years > 20"))
        self.history.apply(SearchQuery("doe"))
        self.history.reset()
        result = self.history.apply(SearchQuery("smith"))
        self.assertEqual(node_ids(result), {self.anna.node_id, self.mark.node_id})
        self.assertEqual(len(self.history), 1)

    def test_reset_does_not_change_original_graph(self):
        before_nodes, before_edges = node_ids(self.graph), edge_ids(self.graph)
        self.history.apply(SearchQuery("smith"))
        self.history.reset()
        self.assertEqual(node_ids(self.graph), before_nodes)
        self.assertEqual(edge_ids(self.graph), before_edges)

    def test_operations_are_in_applied_order(self):
        q1 = FilterQuery("years > 20")
        q2 = SearchQuery("doe")
        q3 = FilterQuery("years < 50")
        for q in (q1, q2, q3):
            self.history.apply(q)
        self.assertEqual(self.history.get_operations(), [q1, q2, q3])
        self.assertEqual(
            self.history.describe(),
            ["filter: years > 20", "search: 'doe'", "filter: years < 50"],
        )

    # returned list is a copy, UI can not break the history
    def test_operations_list_is_a_copy(self):
        self.history.apply(SearchQuery("doe"))
        self.history.get_operations().clear()
        self.assertEqual(len(self.history), 1)

    # years is int, "abc" can not be converted -> ValueError, state stays the same
    def test_failed_filter_value_does_not_change_state(self):
        g2 = self.history.apply(SearchQuery("doe"))
        ops_before = self.history.get_operations()
        with self.assertRaises(ValueError):
            self.history.apply(FilterQuery("years > abc"))
        self.assertIs(self.history.current(), g2)
        self.assertEqual(self.history.get_operations(), ops_before)

    def test_failed_date_value_does_not_change_state(self):
        with self.assertRaises(ValueError):
            self.history.apply(FilterQuery("born > not-a-date"))
        self.assertIs(self.history.current(), self.graph)
        self.assertEqual(len(self.history), 0)

    def test_invalid_query_object_is_rejected(self):
        with self.assertRaises(TypeError):
            self.history.apply("years > 20")
        self.assertIs(self.history.current(), self.graph)

    def test_undo_removes_last_operation(self):
        q1 = SearchQuery("doe")
        g2 = self.history.apply(q1)
        q2 = FilterQuery("years > 20")
        self.history.apply(q2)
        self.assertIs(self.history.undo(), q2)
        self.assertIs(self.history.current(), g2)
        self.assertEqual(self.history.get_operations(), [q1])

    def test_undo_on_empty_history(self):
        self.assertIsNone(self.history.undo())
        self.assertIs(self.history.current(), self.graph)

    def test_undo_all_returns_original(self):
        self.history.apply(SearchQuery("doe"))
        self.history.apply(SearchQuery("john"))
        self.history.undo()
        self.history.undo()
        self.assertIs(self.history.current(), self.graph)

    def test_revert_to(self):
        q1 = SearchQuery("doe")
        g2 = self.history.apply(q1)
        self.history.apply(FilterQuery("years > 20"))
        self.history.apply(SearchQuery("john"))
        self.assertIs(self.history.revert_to(1), g2)
        self.assertEqual(self.history.get_operations(), [q1])
        self.assertIs(self.history.revert_to(0), self.graph)

    def test_revert_to_invalid_index(self):
        self.history.apply(SearchQuery("doe"))
        with self.assertRaises(IndexError):
            self.history.revert_to(5)
        with self.assertRaises(IndexError):
            self.history.revert_to(-1)
        self.assertEqual(len(self.history), 1)

    # new operation after undo continues from the current graph
    def test_apply_after_undo(self):
        self.history.apply(SearchQuery("doe"))
        self.history.apply(SearchQuery("lucy"))
        self.history.undo()
        result = self.history.apply(SearchQuery("mike"))
        self.assertEqual(node_ids(result), {self.mike.node_id})
        self.assertEqual(len(self.history), 2)

    def test_none_graph_is_rejected(self):
        with self.assertRaises(ValueError):
            QueryHistory(None)

if __name__ == "__main__":
    unittest.main()