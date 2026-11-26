from api.plugins.data_source_plugin import DataSourcePlugin


class DataSource2(DataSourcePlugin):

    @property
    def name(self):
        return "mock_data_source_2"

    def load(self, source):
        return {
            "source": source,
            "nodes": ["A", "B", "C"],
            "edges": [("A", "B"), ("B", "C")]
        }