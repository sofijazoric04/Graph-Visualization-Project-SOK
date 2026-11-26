class Graph:
    next_id=1
    def __init__(self,directed=False):
        self.graph_id=Graph.next_id
        Graph.next_id+=1
        self.nodes={}
        self.edges={}
        self.directed=directed

    #da ne vraca stvarnu referencu stavljamo copy
    def get_nodes(self):
        return self.nodes.copy()

    def get_edges(self):
        return self.edges.copy()

    def add_node(self,node):
        if node.node_id in self.nodes:
            raise ValueError("Node already exists")
        self.nodes[node.node_id]=node

    def add_edge(self,edge):
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError("Both nodes must belong to the graph")

        if edge.edge_id in self.edges:
            raise ValueError("Edge already exists")

        self.edges[edge.edge_id]=edge

    def delete_node(self,node_id):
        if node_id not in self.nodes:
            raise KeyError("Node does not exist")

        #brisemo i sve grane
        edges_to_delete = []
        for edge_id,edge in self.edges.items():
            if edge.source == node_id or edge.target == node_id:
                edges_to_delete.append(edge_id)

        for edge_id in edges_to_delete:
            del self.edges[edge_id]

        del self.nodes[node_id]

    def delete_edge(self,edge_id):
        if edge_id not in self.edges:
            raise KeyError("Edge does not exist")

        del self.edges[edge_id]

    #radimo pretragu po dubini dfs
    def is_cycled(self):
        neighborhood = {node_id: [] for node_id in self.nodes}

        for edge_id,edge in self.edges.items():
            neighborhood[edge.source].append((edge.target,edge_id))

            if not self.directed:
                neighborhood[edge.target].append((edge.source,edge_id))

        if self.directed:
            visited=set()
            recursion_stack=set()

            def dfs(node_id):
                visited.add(node_id)
                recursion_stack.add(node_id)
                for neighbor,edge_id in neighborhood[node_id]:
                    if neighbor in recursion_stack:
                        return True
                    if neighbor not in visited:
                        if dfs(neighbor):
                            return True
                recursion_stack.remove(node_id)
                return False

            for node_id in self.nodes.keys():
                if node_id not in visited:
                    if dfs(node_id):
                        return True
            return False
        else:
            visited=set()
            def dfs(node_id,parent_edge):
                visited.add(node_id)
                for neighbor,edge_id in neighborhood[node_id]:
                    if edge_id==parent_edge:
                        continue
                    if neighbor in visited:
                        return True
                    if neighbor not in visited:
                        if dfs(neighbor,edge_id):
                            return True
                return False

            for node_id in self.nodes.keys():
                if node_id not in visited:
                    if dfs(node_id,None):
                        return True
            return False

    def is_directed(self):
        return self.directed

    def find_node(self, node_id):
        return self.nodes.get(node_id)