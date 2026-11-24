from __future__ import annotations
from abc import ABC, abstractmethod
from graph_api.graph.Graph import Graph
from graph_api.graph.Node import Node

# only matches and describe should be inherited
class GraphQuery(ABC):
    def apply(self, graph: Graph) -> Graph:
        subgraph = type(graph)(directed=graph.is_directed())
        matched_ids = set()
        # checking nodes
        for node in graph.get_nodes().values():
            if self.matches(node):
                subgraph.add_node(node)
                matched_ids.add(node.node_id)
        # checking if both nodes of an edge are matching
        for edge in graph.get_edges().values():
            if edge.source in matched_ids and edge.target in matched_ids:
                subgraph.add_edge(edge)
        return subgraph

    # check if node mathes the query
    @abstractmethod
    def matches(self, node: Node) -> bool:
        raise NotImplementedError

    # for describing all active queries in the workspace
    # ex. "search: ana" or "filter: age>30"
    @abstractmethod
    def describe(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.describe()