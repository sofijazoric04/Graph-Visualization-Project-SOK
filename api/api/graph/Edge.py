class Edge:
    next_id=1
    def __init__(self, source, target):
        self.edge_id = Edge.next_id
        Edge.next_id+=1
        self.source = source.node_id
        self.target = target.node_id
        self.attributes={}

    def add_attribute(self, name, value):
        self.attributes[name] = value

    def update_attribute(self, name, value):
        if name not in self.attributes.keys():
            raise KeyError(f"Attribute '{name}' does not exist")
        self.attributes[name] = value

    def get_attribute(self, name):
        return self.attributes.get(name)

    def delete_attribute(self, name):
        del self.attributes[name]
