import unittest

from api.graph.Edge import Edge
from api.graph.Graph import Graph
from api.graph.Node import Node
from core.graph_storage import InMemoryGraphRepository, WorkspaceManager


class TestGraphStorage(unittest.TestCase):
    def setUp(self):
        self.repository = InMemoryGraphRepository()
        self.manager = WorkspaceManager(self.repository)

    def test_save_and_get_graph_types(self):
        for directed in (False, True):
            for cyclic in (False, True):
                for connected in (False, True):
                    with self.subTest(directed=directed, cyclic=cyclic, connected=connected):
                        graph = Graph(directed=directed)
                        first, second, third = Node(), Node(), Node()
                        graph.add_node(first)
                        graph.add_node(second)
                        graph.add_node(third)
                        graph.add_edge(Edge(first, second))
                        if connected:
                            graph.add_edge(Edge(second, third))
                        if cyclic:
                            graph.add_edge(Edge(second, first))

                        storage_id = self.repository.save(graph)
                        self.assertIs(self.repository.get(storage_id), graph)

    def test_delete_graph_and_reject_unknown_ids(self):
        storage_id = self.repository.save(Graph())
        self.repository.delete(storage_id)
        with self.assertRaises(KeyError):
            self.repository.get(storage_id)
        with self.assertRaises(KeyError):
            self.repository.delete(storage_id)
        with self.assertRaises(KeyError):
            self.manager.switch_workspace(storage_id)

    def test_switch_between_workspaces_and_keep_graphs_independent(self):
        graph = Graph()
        node = Node()
        node.add_value("name", "Original")
        graph.add_node(node)
        first = self.manager.create_workspace("example", {"source": "one"}, graph)
        second = self.manager.create_workspace("example", {"source": "two"}, graph)

        self.assertIs(self.manager.active_workspace, second)
        self.assertIs(self.manager.switch_workspace(first.workspace_id), first)

        first_node = first.current_graph.find_node(node.node_id)
        first_node.update_value("name", "Changed")

        second_node = second.current_graph.find_node(node.node_id)
        original_node = first.original_graph.find_node(node.node_id)
        self.assertEqual(second_node.get_value("name"), "Original")
        self.assertEqual(original_node.get_value("name"), "Original")

        first.reset()
        reset_node = first.current_graph.find_node(node.node_id)
        self.assertEqual(reset_node.get_value("name"), "Original")

    def test_delete_active_workspace(self):
        workspace = self.manager.create_workspace("example", {}, Graph())
        self.manager.delete_workspace(workspace.workspace_id)
        self.assertIsNone(self.manager.active_workspace)
        with self.assertRaises(KeyError):
            self.repository.get(workspace.workspace_id)