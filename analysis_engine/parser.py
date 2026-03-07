import os
from pathlib import Path
from typing import List, Dict

class CodebaseParser:
    """Orchestrates the parsing of a cloned codebase."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.files: List[Path] = []

    def scan_files(self, extensions: List[str] = [".py", ".js", ".ts", ".tsx", ".java"]) -> List[str]:
        """Scans the directory for files with specific extensions."""
        self.files = []
        for ext in extensions:
            self.files.extend(list(self.root_path.rglob(f"*{ext}")))
        
        return [str(f.relative_to(self.root_path)) for f in self.files]

    def parse_structure(self) -> Dict:
        """
        Skeleton for architectural parsing. 
        Will integrate with Tree-sitter in Phase 2.
        """
        structure = {
            "root": str(self.root_path),
            "file_count": len(self.files),
            "modules": {}
        }
        
        # Initial logic to group by directory
        for file_path in self.files:
            rel_path = file_path.relative_to(self.root_path)
            parts = rel_path.parts
            if len(parts) > 1:
                module_name = parts[0]
                if module_name not in structure["modules"]:
                    structure["modules"][module_name] = []
                structure["modules"][module_name].append(str(rel_path))
                
        return structure

if __name__ == "__main__":
    # Test execution
    parser = CodebaseParser(".")
    found_files = parser.scan_files()
    print(f"Found {len(found_files)} files.")
    print(parser.parse_structure())
