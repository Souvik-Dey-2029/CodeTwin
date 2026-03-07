import radon.complexity as cc
from radon.metrics import mi_visit
from typing import Dict, List, Any

class MetricsCollector:
    """Calculates code metrics (Complexity, Maintainability) using Radon."""
    
    @staticmethod
    def get_complexity(code: str) -> List[Dict[str, Any]]:
        """Calculates Cyclomatic Complexity for functions and classes."""
        try:
            results = cc.cc_visit(code)
            return [
                {
                    "name": item.name,
                    "type": "class" if hasattr(item, "classname") and item.classname else "function",
                    "complexity": item.complexity,
                    "rank": cc.cc_rank(item.complexity),
                    "lineno": item.lineno
                }
                for item in results
            ]
        except Exception as e:
            print(f"Error calculating complexity: {e}")
            return []

    @staticmethod
    def get_maintainability(code: str) -> Dict[str, Any]:
        """Calculates the Maintainability Index of a file."""
        try:
            score = mi_visit(code, multi=True)
            rank = "A" if score > 19 else "B" if score > 9 else "C"
            return {
                "score": round(score, 2),
                "rank": rank
            }
        except Exception as e:
            print(f"Error calculating maintainability: {e}")
            return {"score": 0, "rank": "U"}

    @classmethod
    def analyze_file(cls, code: str) -> Dict[str, Any]:
        """Performs a full metrics analysis on a code string."""
        return {
            "complexity": cls.get_complexity(code),
            "maintainability": cls.get_maintainability(code)
        }
