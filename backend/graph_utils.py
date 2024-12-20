import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from database import User, NetworkEdge
import io
import base64

class NetworkGraph:
    def __init__(self, db_session):
        self.db_session = db_session
        self.graph = nx.Graph()
        self.load_graph()

    def load_graph(self):
        """Load the network graph from database"""
        # Load all users as nodes
        users = self.db_session.query(User).all()
        for user in users:
            self.graph.add_node(user.node_id, username=user.username)

        # Load all edges
        edges = self.db_session.query(NetworkEdge).all()
        for edge in edges:
            self.graph.add_edge(edge.node1_id, edge.node2_id, weight=edge.weight)

    def add_node(self, node_id: int, username: str):
        """Add a new node to the graph"""
        self.graph.add_node(node_id, username=username)

    def remove_node(self, node_id: int):
        """Remove a node from the graph"""
        self.graph.remove_node(node_id)
        # Clean up database
        self.db_session.query(NetworkEdge).filter(
            (NetworkEdge.node1_id == node_id) | (NetworkEdge.node2_id == node_id)
        ).delete()
        self.db_session.commit()

    def add_edge(self, node1_id: int, node2_id: int, weight: int = 1):
        """Add an edge between two nodes"""
        self.graph.add_edge(node1_id, node2_id, weight=weight)
        
        # Add to database
        edge = NetworkEdge(node1_id=node1_id, node2_id=node2_id, weight=weight)
        self.db_session.add(edge)
        self.db_session.commit()

    def remove_edge(self, node1_id: int, node2_id: int):
        """Remove an edge between two nodes"""
        self.graph.remove_edge(node1_id, node2_id)
        
        # Remove from database
        self.db_session.query(NetworkEdge).filter(
            ((NetworkEdge.node1_id == node1_id) & (NetworkEdge.node2_id == node2_id)) |
            ((NetworkEdge.node1_id == node2_id) & (NetworkEdge.node2_id == node1_id))
        ).delete()
        self.db_session.commit()

    def get_shortest_path(self, source_id: int, target_id: int) -> List[int]:
        """Find the shortest path between two nodes using Dijkstra's algorithm"""
        try:
            path = nx.dijkstra_path(self.graph, source_id, target_id, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return None

    def get_node_connections(self, node_id: int) -> List[Tuple[int, str]]:
        """Get all nodes connected to a given node"""
        if node_id in self.graph:
            neighbors = self.graph.neighbors(node_id)
            return [(n, self.graph.nodes[n]['username']) for n in neighbors]
        return []

    def get_network_status(self) -> Dict:
        """Get overall network statistics"""
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'average_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes() if self.graph.number_of_nodes() > 0 else 0,
            'diameter': nx.diameter(self.graph) if nx.is_connected(self.graph) and self.graph.number_of_nodes() > 0 else float('inf'),
            'density': nx.density(self.graph),
            'is_connected': nx.is_connected(self.graph)
        }

    def get_node_centrality(self, node_id: int) -> Dict:
        """Calculate various centrality metrics for a node"""
        degree_centrality = nx.degree_centrality(self.graph)[node_id]
        betweenness_centrality = nx.betweenness_centrality(self.graph)[node_id]
        closeness_centrality = nx.closeness_centrality(self.graph)[node_id]
        
        return {
            'degree_centrality': degree_centrality,
            'betweenness_centrality': betweenness_centrality,
            'closeness_centrality': closeness_centrality
        }

    def visualize_graph(self) -> str:
        """Generate a visualization of the network graph"""
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(self.graph)
        
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, node_color='lightblue', 
                             node_size=500)
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos)
        
        # Draw labels
        labels = nx.get_node_attributes(self.graph, 'username')
        nx.draw_networkx_labels(self.graph, pos, labels)
        
        # Save plot to a base64 string
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        
        return base64.b64encode(img.getvalue()).decode()

    def create_demo_graph(self):
        """Create a demo graph with 6 nodes"""
        # Clear existing graph
        self.graph.clear()
        
        # Add nodes
        demo_users = [
            ('user1', 'upassword1'),
            ('user2', 'upassword2'),
            ('user3', 'upassword3'),
            ('user4', 'upassword4'),
            ('user5', 'upassword5'),
            ('user6', 'upassword6')
        ]
        
        for i, (username, password) in enumerate(demo_users, 1):
            self.add_node(i, username)
            
        # Add edges to create a complex network
        edges = [
            (1, 2), (1, 3), (2, 4), (3, 4), (3, 5),
            (4, 5), (4, 6), (5, 6), (2, 3), (1, 6)
        ]
        
        for node1, node2 in edges:
            self.add_edge(node1, node2)

    def get_all_paths(self, source_id: int, target_id: int) -> List[List[int]]:
        """Get all possible paths between two nodes"""
        try:
            return list(nx.all_simple_paths(self.graph, source_id, target_id))
        except nx.NetworkXNoPath:
            return []

    def get_path_security_metric(self, path: List[int]) -> float:
        """Calculate security metric for a path based on node centrality"""
        if not path:
            return 0.0
        
        # Calculate average betweenness centrality of nodes in path
        centralities = nx.betweenness_centrality(self.graph)
        path_centralities = [centralities[node] for node in path]
        return sum(path_centralities) / len(path_centralities)