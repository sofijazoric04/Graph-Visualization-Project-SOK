from api.plugins.visualizer_plugin import VisualizerPlugin


class SimpleVisualizer(VisualizerPlugin):

    @property
    def name(self):
        return "mock_visualizer"

    def visualize(self, graph):
        return "<div>Mock visualization</div>"