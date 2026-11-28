import unittest

from api.graph.Graph import Graph
from api.graph.Node import Node
from api.plugins.data_source_plugin import DataSourcePlugin
from api.plugins.visualizer_plugin import VisualizerPlugin
from core.graph_storage import InMemoryGraphRepository, WorkspaceManager
from core.plugin_communication import PluginCommunicationError, PluginCommunicationService
from core.queries.FilterQuery import FilterQuery
from core.queries.SearchQuery import SearchQuery


class StubDataSourcePlugin(DataSourcePlugin):
    @property
    def name(self):
        return "stub_source"

    def __init__(self):
        self.received_source = None
        self.graph = Graph()
        for name, age in (("Ana", 20), ("Mila", 25), ("Mina", 18)):
            node = Node()
            node.add_value("name", name)
            node.add_value("age", age)
            self.graph.add_node(node)

    def load(self, source):
        self.received_source = source
        if source == "invalid":
            raise ValueError("Cannot read the source")
        return self.graph


class StubVisualizerPlugin(VisualizerPlugin):
    @property
    def name(self):
        return "stub_visualizer"

    def __init__(self):
        self.received_graph = None
        self.html = "<p>Rendered graph</p>"

    def visualize(self, graph):
        self.received_graph = graph
        return self.html


class StubRegistry:
    def __init__(self, source, visualizer):
        self._sources = {source.name: source}
        self._visualizers = {visualizer.name: visualizer}

    def get_data_source(self, name):
        return self._sources.get(name)

    def get_visualizer(self, name):
        return self._visualizers.get(name)


class TestPluginCommunication(unittest.TestCase):
    def setUp(self):
        self.source = StubDataSourcePlugin()
        self.visualizer = StubVisualizerPlugin()
        registry = StubRegistry(self.source, self.visualizer)
        self.repository = InMemoryGraphRepository()
        self.manager = WorkspaceManager(self.repository)
        self.service = PluginCommunicationService(registry, self.manager)

    def test_load_store_and_render(self):
        workspace = self.service.load_graph(self.source.name, {"source": "example"})
        self.assertEqual(self.source.received_source, "example")
        self.assertEqual(
            workspace.original_graph.get_nodes().keys(),
            self.source.graph.get_nodes().keys(),
        )
        self.assertIs(self.repository.get(workspace.workspace_id), workspace.original_graph)
        self.assertIs(self.manager.active_workspace, workspace)
        self.assertEqual(self.service.render(workspace, self.visualizer.name), self.visualizer.html)
        self.assertIs(self.visualizer.received_graph, workspace.current_graph)
        self.assertEqual(len(self.visualizer.received_graph.get_nodes()), 3)

    def test_render_after_search_and_filter(self):
        workspace = self.service.load_graph(self.source.name, {"source": "example"})

        workspace.apply_query(SearchQuery("mi"))
        self.assertEqual(self.service.render(workspace, self.visualizer.name), self.visualizer.html)
        self.assertIs(self.visualizer.received_graph, workspace.current_graph)
        self.assertEqual(len(self.visualizer.received_graph.get_nodes()), 2)

        workspace.apply_query(FilterQuery("age >= 20"))
        self.assertEqual(self.service.render(workspace, self.visualizer.name), self.visualizer.html)
        self.assertIs(self.visualizer.received_graph, workspace.current_graph)
        names = []
        for node in self.visualizer.received_graph.get_nodes().values():
            names.append(node.get_value("name"))
        self.assertEqual(names, ["Mila"])
        self.assertEqual(len(workspace.original_graph.get_nodes()), 3)
        self.assertEqual(len(workspace.active_operations), 2)

        workspace.reset()
        self.assertEqual(len(workspace.current_graph.get_nodes()), 3)
        self.assertEqual(workspace.active_operations, [])

    def test_missing_parameter_is_rejected_before_calling_plugin(self):
        with self.assertRaisesRegex(PluginCommunicationError, "Invalid parameters.*source"):
            self.service.load_graph(self.source.name, {})
        self.assertIsNone(self.source.received_source)
        self.assertIsNone(self.manager.active_workspace)

    def test_plugin_error_is_reported(self):
        with self.assertRaisesRegex(PluginCommunicationError, "Cannot read the source"):
            self.service.load_graph(self.source.name, {"source": "invalid"})
        self.assertIsNone(self.manager.active_workspace)

    def test_unknown_plugin_names(self):
        with self.assertRaisesRegex(PluginCommunicationError, "Unknown data source"):
            self.service.load_graph("unknown", {})

        workspace = self.service.load_graph(self.source.name, {"source": "example"})
        with self.assertRaisesRegex(PluginCommunicationError, "Unknown visualizer"):
            self.service.render(workspace, "unknown")