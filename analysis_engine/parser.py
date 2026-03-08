import os
import tree_sitter
import networkx as nx
from pathlib import Path
from typing import List, Dict, Any
from analysis_engine.language_specs import PYTHON_QUERIES, JAVASCRIPT_QUERIES
from analysis_engine.metrics import MetricsCollector

class CodebaseParser:
    """Orchestrates the parsing of a codebase using Tree-sitter."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.files: List[Path] = []
        self.languages: Dict[str, Any] = {}
        self.graph = nx.DiGraph()

    def scan_files(self, extensions: List[str] = [".py", ".js", ".ts"]) -> List[str]:
        """Scans the directory for files with specific extensions."""
        self.files = []
        for ext in extensions:
            self.files.extend(list(self.root_path.rglob(f"*{ext}")))
        return [str(f.relative_to(self.root_path)) for f in self.files]

    def _get_tree_sitter_query(self, extension: str, query_type: str) -> str:
        """Returns the appropriate Tree-sitter query for the language."""
        if extension == ".py":
            return PYTHON_QUERIES.get(query_type, "")
        elif extension in [".js", ".ts", ".tsx"]:
            return JAVASCRIPT_QUERIES.get(query_type, "")
        return ""

    def parse_file(self, file_path: Path) -> Dict:
        """Parses a single file using Tree-sitter to extract metadata."""
        try:
            content = file_path.read_bytes()
            ext = file_path.suffix
            
            # This is a placeholder for actual tree-sitter language loading logic
            # In a real environment, you'd use tree_sitter_languages.get_language(lang)
            # or load from a compiled .so file
            
            metadata = {
                "path": str(file_path.relative_to(self.root_path)),
                "symbols": [],
                "imports": [],
                "metrics": {}
            }

            # If the file is Python, we can calculate metrics using Radon
            if ext == ".py":
                try:
                    code_str = content.decode("utf-8")
                    metadata["metrics"] = MetricsCollector.analyze_file(code_str)
                except Exception as e:
                    print(f"Failed to decode or analyze metrics for {file_path}: {e}")

            # Fallback: Basic dependency resolution based on filename pattern matching
            # logic for dependency resolution (simplified)
            rel_path = str(file_path.relative_to(self.root_path))
            self.graph.add_node(rel_path)
            
            # Simple heuristic: files in the same directory often depend on each other
            # or 'main' files depend on others.
            for other_file in self.files:
                other_rel = str(other_file.relative_to(self.root_path))
                if other_rel != rel_path:
                    # If this is a main file, add links to others in the same subtree
                    if "main" in rel_path.lower() or "app" in rel_path.lower():
                        if os.path.dirname(rel_path) == os.path.dirname(other_rel):
                            self.graph.add_edge(rel_path, other_rel)
            
            # If we had the language and parser initialized, we would do deeper AST analysis.
            # But the current fallback ensures we always have a graph to visualize.
            
            return metadata
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return {}

    def parse_structure(self) -> Dict:
        """Aggregates parsing results for the entire codebase."""
        structure = {
            "root": str(self.root_path),
            "file_count": len(self.files),
            "files": []
        }
        
        for file_path in self.files:
            file_meta = self.parse_file(file_path)
            if file_meta:
                structure["files"].append(file_meta)
                
        return structure

if __name__ == "__main__":
    parser = CodebaseParser(".")
    parser.scan_files()
    print(parser.parse_structure())
