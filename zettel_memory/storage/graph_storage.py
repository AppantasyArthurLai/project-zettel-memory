import networkx as nx
import os
import json
from typing import List, Tuple, Dict, Any

class NetworkXStorage:
    def __init__(self, persist_path: str = "./brain_data/graph.gml"):
        self.persist_path = persist_path
        self.graph = nx.Graph()
        self._ensure_dir()
        self.load()

    def _ensure_dir(self):
        directory = os.path.dirname(self.persist_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def add_node(self, note_id: str, **attrs):
        self.graph.add_node(note_id, **attrs)
        self.save()

    def remove_node(self, note_id: str):
        if self.graph.has_node(note_id):
            self.graph.remove_node(note_id)
            self.save()

    def add_edge(self, source_id: str, target_id: str, **attrs):
        if not self.graph.has_node(source_id) or not self.graph.has_node(target_id):
            # In a real app we might raise an error or auto-create, 
            # here we assume nodes are added via vector storage sync or implicitly
            pass
        self.graph.add_edge(source_id, target_id, **attrs)
        self.save()

    def get_neighbors(self, note_id: str, hops: int = 1) -> List[str]:
        if not self.graph.has_node(note_id):
            return []
        
        # Simple BFS 1-hop for now as per MVP
        # For variable hops, we could use nx.single_source_shortest_path_length
        return list(self.graph.neighbors(note_id))

    def save(self):
        # Using GML or similar that supports attributes well. 
        # JSON is also an option but node-link-data format is verbose.
        # GraphML is standard.
        nx.write_graphml(self.graph, self.persist_path.replace(".gml", ".graphml"))

    def load(self):
        path = self.persist_path.replace(".gml", ".graphml")
        if os.path.exists(path):
            self.graph = nx.read_graphml(path)
