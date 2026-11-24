from importlib.metadata import entry_points
import logging

from api.plugins.visualizer_plugin import VisualizerPlugin
from api.plugins.data_source_plugin import DataSourcePlugin

logger = logging.getLogger(__name__)

class PluginRegistry:
    VISUALIZER_GROUP = "graph.visualizer"
    DATA_SOURCE_GROUP = "graph.data_source"

    def __init__(self):
        self._visualizers = {}
        self._data_sources = {}

    def discover_plugins(self):
        self.discover_data_sources = {}
        self.discover_visualizers = {}

    def discover_visualizers(self):
        discovered_plugins = entry_points(
            group=self.VISUALIZER_GROUP
        )

        for entry_point in discovered_plugins:
            try:
                plugin_class = entry_point.load()

                if not (isinstance(plugin_class, type) and issubclass(plugin_class, VisualizerPlugin)):
                    logger.warning("Plugin doesnt have Visualizer Plugin")
                    continue

                plugin = plugin_class()

                if plugin.name in self._visualizers:
                    logger.warning("Visualizer already registered")
                    continue

                self._visualizers[plugin.name] = plugin

                logger.info("Visualizer registered")

            except Exception:
                logger.exception("Visualizer failed to register")


    def get_visualizer(self, name):
        return self._visualizers.get(name)


    def get_visualizers(self):
        return self._visualizers


    def discover_data_sources(self):
        discovered_plugins = entry_points(
            group=self.DATA_SOURCE_GROUP
        )

        for entry_point in discovered_plugins:
            try:
                plugin_class = entry_point.load()

                if not (
                    isinstance(plugin_class, type)
                    and issubclass(plugin_class, DataSourcePlugin)
                ):
                    logger.warning(
                        "Plugin doesnt have DataSourcePlugin.",
                    )
                    continue

                plugin = plugin_class()

                if plugin.name in self._data_sources:
                    logger.warning(
                        "Plugin is already registered.",
                    )
                    continue

                self._data_sources[plugin.name] = plugin

                logger.info(
                    "Data source successfully registered.",
                )

            except Exception:
                logger.exception(
                    "Failed to register data source",
                )

    def get_data_source(self, name):
        return self._data_sources.get(name)

    def get_data_sources(self):
        return self._data_sources.copy()
