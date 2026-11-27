from abc import ABC, abstractmethod
from copy import deepcopy


class GraphRepository(ABC):
    @abstractmethod
    def save(self, graph):
        """Store a graph and return its storage ID."""

    @abstractmethod
    def get(self, storage_id):
        """Return the stored graph."""

    @abstractmethod
    def delete(self, storage_id):
        """Remove the stored graph."""


class InMemoryGraphRepository(GraphRepository):
    def __init__(self):
        self._graphs = {}
        self._next_id = 1

    def save(self, graph):
        storage_id = self._next_id
        self._next_id += 1
        self._graphs[storage_id] = graph
        return storage_id

    def get(self, storage_id):
        return self._graphs[storage_id]

    def delete(self, storage_id):
        del self._graphs[storage_id]


class Workspace:
    def __init__(self, workspace_id, data_source_name, params, original_graph):
        self.workspace_id = workspace_id
        self.data_source_name = data_source_name
        self.params = deepcopy(params)
        self.original_graph = original_graph
        self.current_graph = deepcopy(original_graph)
        self.active_operations = []

    def apply_query(self, query):
        self.current_graph = query.apply(self.current_graph)
        self.active_operations.append(query)
        return self.current_graph

    def reset(self):
        self.current_graph = deepcopy(self.original_graph)
        self.active_operations.clear()


class WorkspaceManager:
    def __init__(self, repository):
        self._repository = repository
        self._workspaces = {}
        self.active_workspace = None

    def create_workspace(self, data_source_name, params, graph):
        original_graph = deepcopy(graph)
        workspace_id = self._repository.save(original_graph)
        workspace = Workspace(workspace_id, data_source_name, params, original_graph)
        self._workspaces[workspace_id] = workspace
        self.active_workspace = workspace
        return workspace

    def switch_workspace(self, workspace_id):
        self.active_workspace = self._workspaces[workspace_id]
        return self.active_workspace

    def delete_workspace(self, workspace_id):
        workspace = self._workspaces[workspace_id]
        self._repository.delete(workspace_id)
        del self._workspaces[workspace_id]
        if self.active_workspace is workspace:
            self.active_workspace = None