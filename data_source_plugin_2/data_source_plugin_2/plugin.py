from api.plugins.data_source_plugin import DataSourcePlugin
from api.graph.Edge import Edge
from api.graph.Graph import Graph
from api.graph.Node import Node

class DataSource2(DataSourcePlugin):

    @property
    def name(self):
        return "mock_data_source_2"

    def load(self, source):
        graph = Graph()
        previous = None
        for label in ("A", "B", "C"):
            node = Node()
            node.add_value("label", label)
            node.add_value("source", source)
            graph.add_node(node)
            if previous is not None:
                graph.add_edge(Edge(previous, node))
            previous = node
        return graph