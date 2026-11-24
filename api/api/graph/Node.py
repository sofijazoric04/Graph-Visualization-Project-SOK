class Node :
    next_id=1
    def __init__(self):
        #povecavamo brojac na nivou klase
        self.node_id = Node.next_id
        Node.next_id+=1
        self.values={}

    def add_value(self,name,value):
        self.values[name]=value

    def get_value(self,name):
        return self.values.get(name)

    def get_values(self):
        return self.values.copy()

    def update_value(self,name,value):
        if name not in self.values.keys():
            raise KeyError(f"Attribute '{name}' does not exist")
        self.values[name]=value

    def delete_value(self,name):
        del self.values[name]


