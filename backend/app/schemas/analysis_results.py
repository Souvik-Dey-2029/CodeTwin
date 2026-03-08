from pydantic import BaseModel
from typing import List, Dict, Any

class GraphNode(BaseModel):
    id: str
    name: str
    complexity: float
    centrality: float
    pagerank: float

class GraphLink(BaseModel):
    source: str
    target: str

class GraphDataOut(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]

from typing import List, Dict, Any, Optional

class HeatmapItem(BaseModel):
    id: str
    value: float
    color: Optional[str] = None
