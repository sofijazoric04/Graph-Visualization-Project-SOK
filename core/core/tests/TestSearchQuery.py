import unittest
from datetime import date, datetime
from api.graph.Graph import Graph
from api.graph.Node import Node
from api.graph.Edge import Edge
from core.queries.SearchQuery import SearchQuery
# running tests:
# cd core
# python -m unittest core.tests.TestSearchQuery -v

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

def edge_pairs(graph):
    return {(e.source, e.target) for e in graph.get_edges().values()}

# base class, a family tree (John -> Mike, John -> Lucy)
class _FamilyGraphMixin:
    directed = True

    def build_family(self):
        self.graph = Graph(directed=self.directed)
        self.john = make_node(first="John", last="Doe", years=53)
        self.mike = make_node(first="Mike", last="Doe", years=25)
        self.lucy = make_node(first="Lucy", last="Doe", years=15)
        for n in (self.john, self.mike, self.lucy):
            self.graph.add_node(n)
        self.e_john_mike = Edge(self.john, self.mike)
        self.e_john_lucy = Edge(self.john, self.lucy)
        self.graph.add_edge(self.e_john_mike)
        self.graph.add_edge(self.e_john_lucy)


# directed graph
class TestSearchDirectedGraph(unittest.TestCase, _FamilyGraphMixin):
    directed = True

    def setUp(self):
        self.build_family()

    def test_result_stays_directed(self):
        result = SearchQuery("doe").apply(self.graph)
        self.assertTrue(result.is_directed())

    def test_edge_direction_is_preserved(self):
        result = SearchQuery("doe").apply(self.graph)
        self.assertEqual(
            edge_pairs(result),
            {(self.john.node_id, self.mike.node_id),
             (self.john.node_id, self.lucy.node_id)},
        )

    # John is the source of both edges, Mike stays alone
    def test_edge_dropped_when_source_removed(self):
        result = SearchQuery("mike").apply(self.graph)
        self.assertEqual(node_ids(result), {self.mike.node_id})
        self.assertEqual(edge_ids(result), set())

    def test_edge_dropped_when_target_removed(self):
        result = SearchQuery("john").apply(self.graph)
        self.assertEqual(node_ids(result), {self.john.node_id})
        self.assertEqual(edge_ids(result), set())

    # in a directed graph A->B and B->A are two separate edges
    def test_both_directions_a_to_b_and_b_to_a_are_kept(self):
        back = Edge(self.mike, self.john)
        self.graph.add_edge(back)
        result = SearchQuery("doe").apply(self.graph)
        self.assertIn((self.john.node_id, self.mike.node_id), edge_pairs(result))
        self.assertIn((self.mike.node_id, self.john.node_id), edge_pairs(result))
        self.assertEqual(len(result.get_edges()), 3)

# undirected graph
class TestSearchUndirectedGraph(unittest.TestCase, _FamilyGraphMixin):
    directed = False

    def setUp(self):
        self.build_family()

    def test_result_stays_undirected(self):
        result = SearchQuery("doe").apply(self.graph)
        self.assertFalse(result.is_directed())

    # "first" is an attribute name on every node -> all edges stay
    def test_edge_kept_when_both_ends_match(self):
        result = SearchQuery("first").apply(self.graph)
        self.assertEqual(edge_ids(result), {self.e_john_mike.edge_id, self.e_john_lucy.edge_id})

    # edge stored as Lucy -> Mike must be kept when both are in result
    def test_edge_kept_regardless_of_stored_orientation(self):
        e = Edge(self.lucy, self.mike)
        g = Graph(directed=False)
        for n in (self.mike, self.lucy):
            g.add_node(n)
        g.add_edge(e)
        result = SearchQuery("doe").apply(g)
        self.assertEqual(edge_ids(result), {e.edge_id})

    def test_edge_removed_when_one_end_missing(self):
        result = SearchQuery("lucy").apply(self.graph)
        self.assertEqual(node_ids(result), {self.lucy.node_id})
        self.assertEqual(len(result.get_edges()), 0)

# acyclic graph
class TestSearchAcyclicGraph(unittest.TestCase):
    def setUp(self):
        # a -> b -> c -> d and a -> c
        self.graph = Graph(directed=True)
        self.a = make_node(label="root-node", level=0, tag="key")
        self.b = make_node(label="mid-1", level=1)
        self.c = make_node(label="mid-2", level=2, tag="key")
        self.d = make_node(label="leaf-node", level=3)
        for n in (self.a, self.b, self.c, self.d):
            self.graph.add_node(n)
        self.ab = Edge(self.a, self.b)
        self.bc = Edge(self.b, self.c)
        self.cd = Edge(self.c, self.d)
        self.ac = Edge(self.a, self.c)
        for e in (self.ab, self.bc, self.cd, self.ac):
            self.graph.add_edge(e)

    def test_search_on_chain_keeps_inner_edges(self):
        result = SearchQuery("mid").apply(self.graph)
        self.assertEqual(node_ids(result), {self.b.node_id, self.c.node_id})
        self.assertEqual(edge_ids(result), {self.bc.edge_id})

    # root and leaf are not directly connected, no edges
    def test_removing_middle_nodes_breaks_chain(self):
        result = SearchQuery("node").apply(self.graph)
        self.assertEqual(node_ids(result), {self.a.node_id, self.d.node_id})
        self.assertEqual(len(result.get_edges()), 0)

    def test_whole_dag_kept(self):
        result = SearchQuery("level").apply(self.graph)
        self.assertEqual(len(result.get_nodes()), 4)
        self.assertEqual(len(result.get_edges()), 4)

    # path a->b->c is broken, but direct edge a->c survives
    def test_shortcut_edge_kept(self):
        result = SearchQuery("key").apply(self.graph)
        self.assertEqual(node_ids(result), {self.a.node_id, self.c.node_id})
        self.assertEqual(edge_ids(result), {self.ac.edge_id})


# cyclic graph
class TestSearchCyclicGraph(unittest.TestCase):
    # x -> y -> z -> x   (cycle of length 3)
    def setUp(self):
        self.graph = Graph(directed=True)
        self.x = make_node(name="X-ray")
        self.y = make_node(name="Yellow")
        self.z = make_node(name="Zulu")
        for n in (self.x, self.y, self.z):
            self.graph.add_node(n)
        self.xy = Edge(self.x, self.y)
        self.yz = Edge(self.y, self.z)
        self.zx = Edge(self.z, self.x)
        for e in (self.xy, self.yz, self.zx):
            self.graph.add_edge(e)

    def test_whole_cycle_is_kept(self):
        result = SearchQuery("name").apply(self.graph)
        self.assertEqual(len(result.get_nodes()), 3)
        self.assertEqual(edge_ids(result), {self.xy.edge_id, self.yz.edge_id, self.zx.edge_id})

    # "l" -> Yellow and Zulu; X-ray removed -> only y->z survives, cycle gone
    def test_cycle_is_broken_when_node_removed(self):
        result = SearchQuery("l").apply(self.graph)
        self.assertEqual(node_ids(result), {self.y.node_id, self.z.node_id})
        self.assertEqual(edge_ids(result), {self.yz.edge_id})

    def test_two_node_cycle_directed_kept(self):
        back = Edge(self.z, self.y)
        self.graph.add_edge(back)
        result = SearchQuery("l").apply(self.graph)
        self.assertEqual(edge_ids(result), {self.yz.edge_id, back.edge_id})

    def test_search_does_not_recurse_infinitely(self):
        result = SearchQuery("zulu").apply(self.graph)
        self.assertEqual(node_ids(result), {self.z.node_id})
        self.assertEqual(len(result.get_edges()), 0)

    def test_self_loop_is_kept(self):
        loop = Edge(self.x, self.x)
        self.graph.add_edge(loop)
        result = SearchQuery("x-ray").apply(self.graph)
        self.assertEqual(node_ids(result), {self.x.node_id})
        self.assertEqual(edge_ids(result), {loop.edge_id})

    def test_two_node_cycle_undirected(self):
        g = Graph(directed=False)
        a = make_node(name="A")
        b = make_node(name="B")
        g.add_node(a)
        g.add_node(b)
        e1 = Edge(a, b)
        e2 = Edge(b, a)
        g.add_edge(e1)
        g.add_edge(e2)
        result = SearchQuery("name").apply(g)
        self.assertEqual(edge_ids(result), {e1.edge_id, e2.edge_id})

# cConnected / disconnected graph
class TestSearchConnectedAndDisconnectedGraph(unittest.TestCase):
    # component 1: p1 - p2 ; component 2: c1 - c2 ; isolated node: iso
    def setUp(self):
        self.graph = Graph(directed=False)
        self.p1 = make_node(type="person", name="Ana")
        self.p2 = make_node(type="person", name="Marko")
        self.c1 = make_node(type="city", name="Beograd")
        self.c2 = make_node(type="city", name="Novi Sad")
        self.iso = make_node(type="planet", name="Mars")
        for n in (self.p1, self.p2, self.c1, self.c2, self.iso):
            self.graph.add_node(n)
        self.pp = Edge(self.p1, self.p2)
        self.cc = Edge(self.c1, self.c2)
        self.graph.add_edge(self.pp)
        self.graph.add_edge(self.cc)

    def test_search_keeps_single_component(self):
        result = SearchQuery("person").apply(self.graph)
        self.assertEqual(node_ids(result), {self.p1.node_id, self.p2.node_id})
        self.assertEqual(edge_ids(result), {self.pp.edge_id})

    # "ar" -> Marko, Mars
    def test_search_across_components_result_disconnected(self):
        result = SearchQuery("ar").apply(self.graph)
        self.assertEqual(node_ids(result), {self.p2.node_id, self.iso.node_id})
        self.assertEqual(len(result.get_edges()), 0)

    def test_isolated_node_can_be_found(self):
        result = SearchQuery("planet").apply(self.graph)
        self.assertEqual(node_ids(result), {self.iso.node_id})

    # connected path s1 - s2 - s3; removing s2 disconnects s1 and s3
    def test_search_on_connected_graph_can_produce_disconnected_subgraph(self):
        g = Graph(directed=False)
        s1 = make_node(tag="end-left")
        s2 = make_node(tag="middle")
        s3 = make_node(tag="end-right")
        for n in (s1, s2, s3):
            g.add_node(n)
        g.add_edge(Edge(s1, s2))
        g.add_edge(Edge(s2, s3))
        result = SearchQuery("end").apply(g)
        self.assertEqual(node_ids(result), {s1.node_id, s3.node_id})
        self.assertEqual(len(result.get_edges()), 0)

    def test_all_edges_kept_when_all_nodes_match(self):
        result = SearchQuery("type").apply(self.graph)
        self.assertEqual(len(result.get_nodes()), 5)
        self.assertEqual(edge_ids(result), {self.pp.edge_id, self.cc.edge_id})

# empty graph and graph without edges
class TestSearchEmptyAndEdgelessGraph(unittest.TestCase):
    def test_empty_graph_returns_empty_graph(self):
        g = Graph(directed=True)
        result = SearchQuery("anything").apply(g)
        self.assertEqual(len(result.get_nodes()), 0)
        self.assertEqual(len(result.get_edges()), 0)

    def test_empty_query_on_empty_graph(self):
        result = SearchQuery("").apply(Graph())
        self.assertEqual(len(result.get_nodes()), 0)

    def test_graph_without_edges(self):
        g = Graph()
        a = make_node(name="one")
        b = make_node(name="two")
        g.add_node(a)
        g.add_node(b)
        result = SearchQuery("o").apply(g)
        self.assertEqual(node_ids(result), {a.node_id, b.node_id})
        self.assertEqual(len(result.get_edges()), 0)

    def test_node_without_attributes_matches_only_empty_query(self):
        g = Graph()
        empty = Node()
        g.add_node(empty)
        self.assertEqual(len(SearchQuery("x").apply(g).get_nodes()), 0)
        self.assertEqual(len(SearchQuery("").apply(g).get_nodes()), 1)

# 7. value types: int, str, float, date (and datetime)

class TestSearchValueTypes(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(directed=True)
        self.n_int = make_node(age=42)
        self.n_float = make_node(height=1.85)
        self.n_str = make_node(city="Kragujevac")
        self.n_date = make_node(born=date(2001, 3, 9))
        self.n_dt = make_node(created=datetime(2024, 12, 31, 23, 59))
        for n in (self.n_int, self.n_float, self.n_str, self.n_date, self.n_dt):
            self.graph.add_node(n)

    def test_int_value_contains(self):
        result = SearchQuery("42").apply(self.graph)
        self.assertEqual(node_ids(result), {self.n_int.node_id})

    def test_int_partial_contains(self):
        result = SearchQuery("4").apply(self.graph)
        self.assertIn(self.n_int.node_id, node_ids(result))

    def test_float_value_contains(self):
        result = SearchQuery("1.85").apply(self.graph)
        self.assertEqual(node_ids(result), {self.n_float.node_id})

    def test_float_partial_contains_decimal_point(self):
        result = SearchQuery(".8").apply(self.graph)
        self.assertEqual(node_ids(result), {self.n_float.node_id})

    def test_string_value_contains_case_insensitive(self):
        result = SearchQuery("KRAGU").apply(self.graph)
        self.assertEqual(node_ids(result), {self.n_str.node_id})

    def test_date_full_iso(self):
        result = SearchQuery("2001-03-09").apply(self.graph)
        self.assertEqual(node_ids(result), {self.n_date.node_id})

    def test_date_partial_year_month(self):
        result = SearchQuery("2001-03").apply(self.graph)
        self.assertEqual(node_ids(result), {self.n_date.node_id})

    def test_datetime_iso(self):
        result = SearchQuery("2024-12-31").apply(self.graph)
        self.assertEqual(node_ids(result), {self.n_dt.node_id})

    def test_datetime_time_part(self):
        result = SearchQuery("23:59").apply(self.graph)
        self.assertEqual(node_ids(result), {self.n_dt.node_id})

    def test_values_are_not_mutated_to_string(self):
        SearchQuery("42").apply(self.graph)
        self.assertIsInstance(self.n_int.get_value("age"), int)
        self.assertIsInstance(self.n_float.get_value("height"), float)
        self.assertIsInstance(self.n_date.get_value("born"), date)

    def test_attribute_name_of_typed_value(self):
        result = SearchQuery("born").apply(self.graph)
        self.assertEqual(node_ids(result), {self.n_date.node_id})

# 8. contains semantics: attribute name OR value
class TestSearchContainsSemantics(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        self.only_name = make_node(salary=1000)          # match by name "sal"
        self.only_value = make_node(job="salesman")      # match by value "sal"
        self.none = make_node(hobby="chess")
        for n in (self.only_name, self.only_value, self.none):
            self.graph.add_node(n)

    def test_match_by_name_or_value(self):
        result = SearchQuery("sal").apply(self.graph)
        self.assertEqual(node_ids(result), {self.only_name.node_id, self.only_value.node_id})

    def test_substring_in_middle(self):
        result = SearchQuery("ess").apply(self.graph)
        self.assertEqual(node_ids(result), {self.none.node_id})

    def test_leading_trailing_whitespace_is_ignored(self):
        result = SearchQuery("   chess   ").apply(self.graph)
        self.assertEqual(node_ids(result), {self.none.node_id})

    def test_internal_whitespace_is_respected(self):
        g = Graph()
        n = make_node(city="Novi Sad")
        g.add_node(n)
        self.assertEqual(len(SearchQuery("novi sad").apply(g).get_nodes()), 1)
        self.assertEqual(len(SearchQuery("novisad").apply(g).get_nodes()), 0)

    def test_node_id_is_not_searched(self):
        g = Graph()
        n = make_node(name="abc")
        g.add_node(n)
        result = SearchQuery(str(n.node_id) + "zzz").apply(g)
        self.assertEqual(len(result.get_nodes()), 0)

    def test_edge_attributes_are_not_searched(self):
        g = Graph()
        a = make_node(name="a")
        b = make_node(name="b")
        g.add_node(a)
        g.add_node(b)
        e = Edge(a, b)
        e.add_attribute("relation", "siblings")
        g.add_edge(e)
        result = SearchQuery("siblings").apply(g)
        self.assertEqual(len(result.get_nodes()), 0)

    def test_special_characters(self):
        g = Graph()
        n = make_node(email="ana@ftn.uns.ac.rs")
        g.add_node(n)
        self.assertEqual(len(SearchQuery("@ftn").apply(g).get_nodes()), 1)

# subgraph properties (immutability of original graph)
class TestSearchSubgraphProperties(unittest.TestCase, _FamilyGraphMixin):
    def setUp(self):
        self.build_family()

    def test_original_graph_unchanged(self):
        SearchQuery("mike").apply(self.graph)
        self.assertEqual(len(self.graph.get_nodes()), 3)
        self.assertEqual(len(self.graph.get_edges()), 2)

    def test_result_is_new_graph_object(self):
        result = SearchQuery("doe").apply(self.graph)
        self.assertIsNot(result, self.graph)
        self.assertNotEqual(result.graph_id, self.graph.graph_id)

    def test_result_nodes_subset_of_original(self):
        result = SearchQuery("y").apply(self.graph)
        self.assertTrue(node_ids(result).issubset(node_ids(self.graph)))
        self.assertTrue(edge_ids(result).issubset(edge_ids(self.graph)))

    def test_every_result_edge_has_both_ends_in_result(self):
        result = SearchQuery("m").apply(self.graph)
        for e in result.get_edges().values():
            self.assertIn(e.source, result.get_nodes())
            self.assertIn(e.target, result.get_nodes())

    def test_query_is_reusable(self):
        q = SearchQuery("lucy")
        r1 = q.apply(self.graph)
        r2 = q.apply(self.graph)
        self.assertEqual(node_ids(r1), node_ids(r2))

    def test_str_representation(self):
        self.assertEqual(str(SearchQuery("  Tom ")), "search: 'Tom'")

# successive application (G1 -> G2 -> G3 ...)
class TestSuccessiveSearch(unittest.TestCase):
    # cyclic directed graph, mixed types
    def setUp(self):
        self.g1 = Graph(directed=True)
        self.a = make_node(name="Alice", age=25, city="Novi Sad")
        self.b = make_node(name="Bob", age=30, city="Novi Sad")
        self.c = make_node(name="Carol", age=35, city="Beograd")
        self.d = make_node(name="Dave", age=40, city="Novi Sad")
        for n in (self.a, self.b, self.c, self.d):
            self.g1.add_node(n)
        self.ab = Edge(self.a, self.b)
        self.bc = Edge(self.b, self.c)
        self.cd = Edge(self.c, self.d)
        self.da = Edge(self.d, self.a)  # closes the cycle
        self.bd = Edge(self.b, self.d)
        for e in (self.ab, self.bc, self.cd, self.da, self.bd):
            self.g1.add_edge(e)

    def test_two_successive_searches(self):
        g2 = SearchQuery("novi sad").apply(self.g1)
        self.assertEqual(node_ids(g2), {self.a.node_id, self.b.node_id, self.d.node_id})
        self.assertEqual(edge_ids(g2), {self.ab.edge_id, self.da.edge_id, self.bd.edge_id})

        g3 = SearchQuery("b").apply(g2)  # only Bob (Carol/Beograd already removed)
        self.assertEqual(node_ids(g3), {self.b.node_id})
        self.assertEqual(len(g3.get_edges()), 0)

    def test_three_successive_searches_narrow_result(self):
        g2 = SearchQuery("sad").apply(self.g1)   # Alice, Bob, Dave
        self.assertEqual(node_ids(g2), {self.a.node_id, self.b.node_id, self.d.node_id})
        g3 = SearchQuery("0").apply(g2)          # Bob (30), Dave (40)
        self.assertEqual(node_ids(g3), {self.b.node_id, self.d.node_id})
        self.assertEqual(edge_ids(g3), {self.bd.edge_id})
        g4 = SearchQuery("dave").apply(g3)
        self.assertEqual(node_ids(g4), {self.d.node_id})
        self.assertEqual(len(g4.get_edges()), 0)
        self.assertTrue(node_ids(g4) <= node_ids(g3) <= node_ids(g2) <= node_ids(self.g1))

    def test_successive_search_preserves_direction(self):
        g2 = SearchQuery("novi").apply(self.g1)
        g3 = SearchQuery("age").apply(g2)
        self.assertTrue(g3.is_directed())
        self.assertIn((self.d.node_id, self.a.node_id), edge_pairs(g3))

    def test_successive_search_to_empty_and_further(self):
        g2 = SearchQuery("nobody").apply(self.g1)
        g3 = SearchQuery("alice").apply(g2)
        self.assertEqual(len(g3.get_nodes()), 0)

    def test_order_of_successive_searches_is_commutative(self):
        r1 = SearchQuery("bob").apply(SearchQuery("novi").apply(self.g1))
        r2 = SearchQuery("novi").apply(SearchQuery("bob").apply(self.g1))
        self.assertEqual(node_ids(r1), node_ids(r2))
        self.assertEqual(edge_ids(r1), edge_ids(r2))

    def test_return_to_initial_graph(self):
        SearchQuery("bob").apply(SearchQuery("novi").apply(self.g1))
        # original G1 is untouched, so it can be shown again
        self.assertEqual(len(self.g1.get_nodes()), 4)
        self.assertEqual(len(self.g1.get_edges()), 5)

# larger graph (spec requires >= 200 nodes)
class TestSearchLargeGraph(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(directed=True)
        self.nodes = []
        for i in range(250):
            n = make_node(index=i, group="even" if i % 2 == 0 else "odd")
            self.graph.add_node(n)
            self.nodes.append(n)
        # ring: 0->1->...->249->0  (cyclic)
        for i in range(250):
            self.graph.add_edge(Edge(self.nodes[i], self.nodes[(i + 1) % 250]))

    def test_large_cyclic_graph_whole(self):
        result = SearchQuery("group").apply(self.graph)
        self.assertEqual(len(result.get_nodes()), 250)
        self.assertEqual(len(result.get_edges()), 250)

    # in the ring every edge connects even and odd -> no edge survives
    def test_large_graph_half_nodes_no_edges(self):
        result = SearchQuery("even").apply(self.graph)
        self.assertEqual(len(result.get_nodes()), 125)
        self.assertEqual(len(result.get_edges()), 0)

    # indexes containing "99": 99, 199
    def test_large_graph_substring_on_int(self):
        result = SearchQuery("99").apply(self.graph)
        self.assertEqual(node_ids(result), {self.nodes[99].node_id, self.nodes[199].node_id})

if __name__ == "__main__":
    unittest.main()