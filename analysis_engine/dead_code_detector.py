"""
Dead Code Detection Module for JavaScript/Node.js codebases.
Identifies unused functions, unused imports, and unreachable code.
"""

import os
import re
from typing import Dict, List, Set, Tuple
from pathlib import Path
import json

class DeadCodeDetector:
    """Detects dead code patterns in JavaScript/Node.js projects."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.js_files: List[Path] = []
        self.function_definitions: Dict[str, List[Dict]] = {}
        self.function_calls: Dict[str, Set[str]] = {}
        self.imports: Dict[str, Set[str]] = {}
        self.dead_functions: List[Dict] = []
        self.dead_imports: List[Dict] = []
        
    def scan_js_files(self) -> List[str]:
        """Scan for all JavaScript/TypeScript files."""
        self.js_files = []
        for ext in [".js", ".jsx", ".ts", ".tsx"]:
            self.js_files.extend(list(self.root_path.rglob(f"*{ext}")))
        return [str(f.relative_to(self.root_path)) for f in self.js_files]
    
    def extract_function_definitions(self, code: str, file_path: str) -> List[Dict]:
        """Extract function definitions from code."""
        functions = []
        
        # Function declarations: function foo() {}
        func_decl = re.finditer(r'\bfunction\s+(\w+)\s*\(', code)
        for match in func_decl:
            functions.append({
                "name": match.group(1),
                "type": "function_declaration",
                "file": file_path,
                "line": code[:match.start()].count('\n') + 1
            })
        
        # Arrow functions: const foo = () => {}
        arrow_funcs = re.finditer(r'\bconst\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>', code)
        for match in arrow_funcs:
            functions.append({
                "name": match.group(1),
                "type": "arrow_function",
                "file": file_path,
                "line": code[:match.start()].count('\n') + 1
            })
        
        # Method definitions: foo() {} or foo: () => {}
        methods = re.finditer(r'^\s*(\w+)\s*(?:\([^)]*\))?\s*[:{]', code, re.MULTILINE)
        for match in methods:
            method_name = match.group(1)
            # Avoid duplicates and common keywords
            if method_name not in [f["name"] for f in functions] and \
               method_name not in ["if", "for", "while", "switch", "catch", "async", "await"]:
                functions.append({
                    "name": method_name,
                    "type": "method",
                    "file": file_path,
                    "line": code[:match.start()].count('\n') + 1
                })
        
        return functions
    
    def extract_function_calls(self, code: str) -> Set[str]:
        """Extract all function calls from code."""
        calls = set()
        
        # Function calls: foo(), this.foo(), obj.foo()
        call_pattern = re.finditer(r'(?:^|\W)(?:this\.)?(\w+)\s*\(', code)
        for match in call_pattern:
            calls.add(match.group(1))
        
        return calls
    
    def extract_imports(self, code: str) -> Set[str]:
        """Extract imported identifiers from code."""
        imports = set()
        
        # ES6 imports: import { foo } from 'module'
        import_pattern = re.finditer(r'import\s+(?:{([^}]+)}|(\w+))\s+from', code)
        for match in import_pattern:
            items = match.group(1) or match.group(2)
            if items:
                for item in items.split(','):
                    name = item.strip().split(' as ')[-1].strip()
                    if name:
                        imports.add(name)
        
        # CommonJS requires: const foo = require('module')
        require_pattern = re.finditer(r'(?:const|let|var)\s+(\w+)\s*=\s*require\s*\(', code)
        for match in require_pattern:
            imports.add(match.group(1))
        
        return imports
    
    def analyze_file(self, file_path: Path) -> Tuple[List[Dict], Set[str], Set[str]]:
        """Analyze a single file for function definitions and calls."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
        except Exception:
            return [], set(), set()
        
        relative_path = str(file_path.relative_to(self.root_path))
        
        functions = self.extract_function_definitions(code, relative_path)
        calls = self.extract_function_calls(code)
        imports = self.extract_imports(code)
        
        if relative_path not in self.function_definitions:
            self.function_definitions[relative_path] = functions
        if relative_path not in self.function_calls:
            self.function_calls[relative_path] = calls
        if relative_path not in self.imports:
            self.imports[relative_path] = imports
        
        return functions, calls, imports
    
    def detect_dead_functions(self) -> List[Dict]:
        """Identify functions that are never called."""
        dead_functions = []
        
        # Collect all function names
        all_functions = {}
        for file_path, funcs in self.function_definitions.items():
            for func in funcs:
                all_functions[func["name"]] = func
        
        # Collect all function calls
        all_calls = set()
        for calls in self.function_calls.values():
            all_calls.update(calls)
        
        # Add common built-ins and exported functions
        all_calls.update(['main', 'module', 'exports', 'default', 'constructor', 
                         'render', 'component', 'app', 'server', 'useState', 'useEffect'])
        
        # Find unused functions
        for name, func in all_functions.items():
            if name not in all_calls and not name.startswith('_'):
                dead_functions.append({
                    "name": name,
                    "file": func["file"],
                    "line": func["line"],
                    "type": func["type"],
                    "confidence": 0.85 if len(name) > 3 else 0.65  # More confident for longer names
                })
        
        return sorted(dead_functions, key=lambda x: x["confidence"], reverse=True)
    
    def detect_unused_imports(self, max_results: int = 20) -> List[Dict]:
        """Identify imports that are never used in the file."""
        unused_imports = []
        
        for file_path, imports in self.imports.items():
            calls = self.function_calls.get(file_path, set())
            
            for imported_name in imports:
                # Skip common utilities
                if imported_name in ['React', 'jsx', 'Component', 'Fragment']:
                    continue
                
                # Check if the imported name is used anywhere in the file
                if imported_name not in calls:
                    unused_imports.append({
                        "name": imported_name,
                        "file": file_path,
                        "type": "unused_import",
                        "confidence": 0.75
                    })
        
        return sorted(unused_imports[:max_results], key=lambda x: x["confidence"], reverse=True)
    
    def run(self) -> Dict:
        """Run the complete dead code detection analysis."""
        self.scan_js_files()
        
        for file_path in self.js_files:
            self.analyze_file(file_path)
        
        dead_functions = self.detect_dead_functions()
        unused_imports = self.detect_unused_imports()
        
        return {
            "dead_functions": dead_functions[:20],  # Top 20
            "unused_imports": unused_imports[:20],  # Top 20
            "total_functions_analyzed": sum(len(f) for f in self.function_definitions.values()),
            "total_files_analyzed": len(self.js_files),
            "total_issues": len(dead_functions) + len(unused_imports)
        }
