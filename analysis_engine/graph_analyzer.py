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

import os # Required for basename
