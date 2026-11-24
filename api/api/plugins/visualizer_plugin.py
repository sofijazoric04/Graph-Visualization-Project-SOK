from abc import ABC, abstractmethod

class VisualizerPlugin(ABC):

    @abstractmethod
    def visualize(self, graph):
        pass

    @abstractmethod
    def name(self):
        pass