import unittest
from datetime import date
from api.graph.Graph import Graph
from api.graph.Node import Node
from api.graph.Edge import Edge
from core.queries.SearchQuery import SearchQuery

class TestSearchQuery(unittest.TestCase):

    def setUp(self):
        self.graph = Graph(directed=True)

        self.alice = Node()
        self.alice.add_value("Name", "Alice")
        self.alice.add_value("Age", 25)

        self.tom = Node()
        self.tom.add_value("Name", "Tom")
        self.tom.add_value("Height", 175)

        self.city = Node()
        self.city.add_value("City", "Novi Sad")
        self.city.add_value("Founded", date(1694, 1, 1))

        for n in (self.alice, self.tom, self.city):
            self.graph.add_node(n)

        self.edge_alice_tom = Edge(self.alice, self.tom)
        self.edge_tom_city = Edge(self.tom, self.city)
        self.graph.add_edge(self.edge_alice_tom)
        self.graph.add_edge(self.edge_tom_city)

    def test_match_by_attribute_name(self):
        # "height" exists only as an attribute name on Tom
        result = SearchQuery("height").apply(self.graph)
        self.assertEqual(set(result.get_nodes().keys()), {self.tom.node_id})

    def test_match_by_attribute_value(self):
        result = SearchQuery("alice").apply(self.graph)
        self.assertEqual(set(result.get_nodes().keys()), {self.alice.node_id})

    def test_name_match_is_case_insensitive(self):
        result = SearchQuery("AGE").apply(self.graph)
        self.assertEqual(set(result.get_nodes().keys()), {self.alice.node_id})

    def test_shared_attribute_name_matches_all(self):
        # "Name" is an attribute of Alice and Tom
        result = SearchQuery("name").apply(self.graph)
        self.assertEqual(set(result.get_nodes().keys()), {self.alice.node_id, self.tom.node_id})
        # edge between two kept nodes stays, edge to removed node is dropped
        self.assertEqual(set(result.get_edges().keys()), {self.edge_alice_tom.edge_id})

    def test_date_value_match(self):
        result = SearchQuery("1694").apply(self.graph)
        self.assertEqual(set(result.get_nodes().keys()), {self.city.node_id})

    def test_no_match_returns_empty_graph(self):
        result = SearchQuery("xyz").apply(self.graph)
        self.assertEqual(len(result.get_nodes()), 0)
        self.assertEqual(len(result.get_edges()), 0)

    def test_empty_query_returns_whole_graph(self):
        result = SearchQuery("   ").apply(self.graph)
        self.assertEqual(len(result.get_nodes()), 3)
        self.assertEqual(len(result.get_edges()), 2)

    def test_none_query_raises(self):
        with self.assertRaises(ValueError):
            SearchQuery(None)

if __name__ == "__main__":
    unittest.main()