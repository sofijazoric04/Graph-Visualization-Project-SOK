from abc import ABC, abstractmethod

class DataSourcePlugin(ABC):

    @abstractmethod
    def load(self, graph):
        pass

    @abstractmethod
    def name(self):
        pass