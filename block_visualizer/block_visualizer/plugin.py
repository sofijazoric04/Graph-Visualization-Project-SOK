from api.plugins.visualizer_plugin import VisualizerPlugin


class BlockVisualizer(VisualizerPlugin):

    @property
    def name(self):
        return "mock_block_visualizer"

    def visualize(self, graph):
        return "<div>Mock visualization</div>"