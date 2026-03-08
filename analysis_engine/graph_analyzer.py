import networkx as nx
from typing import Dict, Any, List

class GraphAnalyzer:
    """
    Analyzes the dependency graph to identify architectural hubs and risks.
    """
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def calculate_metrics(self) -> Dict[str, Dict[str, float]]:
        """
        Calculates PageRank and Betweenness Centrality for all nodes.
        """
        if not self.graph.nodes:
            return {}

        pagerank = nx.pagerank(self.graph)
        try:
            betweenness = nx.betweenness_centrality(self.graph)
        except:
            betweenness = {node: 0.0 for node in self.graph.nodes}
        
        metrics = {}
        for node in self.graph.nodes:
            metrics[node] = {
                "pagerank": pagerank.get(node, 0.0),
                "centrality": betweenness.get(node, 0.0)
            }
        return metrics

    def get_risk_scores(self, file_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculates a weighted risk score for each file.
        Risk = (Complexity * 0.4) + (Centrality * 0.4) + (Maintainability_Penalty * 0.2)
        """
        graph_metrics = self.calculate_metrics()
        scores = {}

        for file_path, metrics in file_metrics.items():
            complexity = metrics.get("complexity", 0)
            maintainability = metrics.get("maintainability", 100)
            
            # Normalize complexity (capped at 50 for scaling)
            norm_complexity = min(complexity / 50.0, 1.0)
            
            # Maintainability penalty (lower is worse)
            norm_maint_penalty = (100.0 - maintainability) / 100.0
            
            # Centrality from graph
            centrality = graph_metrics.get(file_path, {}).get("centrality", 0.0)
            
            # Weighted Score (0-100)
            score = (norm_complexity * 0.4 + centrality * 0.4 + norm_maint_penalty * 0.2) * 100
            scores[file_path] = round(score, 2)
            
        return scores

    def get_d3_data(self, file_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Formats the graph as nodes and links for D3.js.
        """
        nodes = []
        links = []
        graph_metrics = self.calculate_metrics()

        for node in self.graph.nodes:
            metrics = file_metrics.get(node, {})
            nodes.append({
                "id": node,
                "name": os.path.basename(node),
                "complexity": metrics.get("complexity", 0),
                "centrality": graph_metrics.get(node, {}).get("centrality", 0.0),
                "pagerank": graph_metrics.get(node, {}).get("pagerank", 0.0)
            })

        for source, target in self.graph.edges:
            links.append({
                "source": source,
                "target": target
            })

        return {"nodes": nodes, "links": links}

    def detect_god_objects(self, file_metrics: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identifies 'God Objects' based on complexity and centrality.
        """
        graph_metrics = self.calculate_metrics()
        candidates = []

        for file_path, metrics in file_metrics.items():
            complexity = metrics.get("complexity", 0)
            centrality = graph_metrics.get(file_path, {}).get("centrality", 0.0)

            # Heuristic: Complexity > 40 AND Centrality > 0.7
            if complexity > 40 or centrality > 0.7:
                candidates.append({
                    "file_path": file_path,
                    "complexity": complexity,
                    "centrality": round(centrality, 2),
                    "reason": "High complexity and architectural centrality detected."
                })
        
        return candidates

    def simulate_blast_radius(self, target_file: str) -> Dict[str, Any]:
        """
        Simulates the impact of changing a specific file.
        """
        if target_file not in self.graph:
            return {"impact_score": 0, "affected_nodes": []}

        # Use BFS to find nodes up to 2 degrees of separation (incoming and outgoing)
        undirected = self.graph.to_undirected()
        try:
            affected = nx.single_source_shortest_path_length(undirected, target_file, cutoff=2)
        except:
            affected = {target_file: 0}

        graph_metrics = self.calculate_metrics()
        nodes = []
        total_centrality = 0.0

        for node, distance in affected.items():
            centrality = graph_metrics.get(node, {}).get("centrality", 0.0)
            total_centrality += centrality
            nodes.append({
                "id": node,
                "distance": distance,
                "centrality": round(centrality, 2)
            })

        impact_score = min((total_centrality * 10) + (len(nodes) * 2), 100)

        return {
            "target": target_file,
            "impact_score": round(impact_score, 2),
            "affected_nodes": nodes
        }

    def get_heatmap_data(self, file_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates hierarchical Treemap data based on risk scores.
        """
        risk_scores = self.get_risk_scores(file_metrics)
        root = {"name": "root", "children": []}
        
        # Build nested structure based on file paths
        for file_path, score in risk_scores.items():
            parts = file_path.split("/")
            current = root
            for i, part in enumerate(parts[:-1]):
                found = False
                if "children" not in current:
                    current["children"] = []
                for child in current["children"]:
                    if child.get("name") == part:
                        current = child
                        found = True
                        break
                if not found:
                    new_node = {"name": part, "children": []}
                    current["children"].append(new_node)
                    current = new_node
            
            # Leaf node
            if "children" not in current:
                current["children"] = []
            current["children"].append({
                "name": parts[-1],
                "value": score
            })
            
        return root

import os # Required for basename
