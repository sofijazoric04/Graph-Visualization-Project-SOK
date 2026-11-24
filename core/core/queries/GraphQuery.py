from abc import ABC, abstractmethod
from api.graph.Graph import Graph

class GraphQuery(ABC):
    def apply(self, graph: Graph) -> Graph:
        subgraph = Graph(directed=graph.is_directed())
        for node_id, node in graph.get_nodes().items():
            if self.matches(node):
                subgraph.add_node(node)
        kept_nodes = subgraph.get_nodes()
        for edge_id, edge in graph.get_edges().items():
            if edge.source in kept_nodes and edge.target in kept_nodes:
                subgraph.add_edge(edge)
        return subgraph

    # true if node satisfies the query
    @abstractmethod
    def matches(self, node) -> bool:
        pass

    # shows all searches and filters that are apllied
    @abstractmethod
    def __str__(self) -> str:
        pass