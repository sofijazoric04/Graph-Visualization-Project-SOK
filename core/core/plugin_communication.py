from inspect import signature

from api.graph.Graph import Graph


class PluginCommunicationError(Exception):
    """Report invalid plugin requests and plugin failures."""


class PluginCommunicationService:
    def __init__(self, registry, workspace_manager):
        self._registry = registry
        self._workspace_manager = workspace_manager

    def load_graph(self, data_source_name, params):
        plugin = self._registry.get_data_source(data_source_name)
        if plugin is None:
            raise PluginCommunicationError(f"Unknown data source: {data_source_name}")

        try:
            signature(plugin.load).bind(**params)
        except TypeError as error:
            raise PluginCommunicationError(
                f"Invalid parameters for data source '{data_source_name}': {error}"
            ) from error

        try:
            graph = plugin.load(**params)
        except Exception as error:
            raise PluginCommunicationError(
                f"Data source '{data_source_name}' failed: {error}"
            ) from error

        if not isinstance(graph, Graph):
            raise PluginCommunicationError(
                f"Data source '{data_source_name}' must return a Graph"
            )

        return self._workspace_manager.create_workspace(data_source_name, params, graph)

    def render(self, workspace, visualizer_name):
        plugin = self._registry.get_visualizer(visualizer_name)
        if plugin is None:
            raise PluginCommunicationError(f"Unknown visualizer: {visualizer_name}")

        try:
            html = plugin.visualize(workspace.current_graph)
        except Exception as error:
            raise PluginCommunicationError(
                f"Visualizer '{visualizer_name}' failed: {error}"
            ) from error

        if not isinstance(html, str):
            raise PluginCommunicationError(
                f"Visualizer '{visualizer_name}' must return HTML as a string"
            )

        return html