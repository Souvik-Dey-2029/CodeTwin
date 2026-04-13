"""
Dependency Analysis Module for JavaScript/Node.js projects.
Identifies unused and zombie dependencies.
"""

import json
import re
from typing import Dict, List, Set
from pathlib import Path

class DependencyAnalyzer:
    """Analyzes dependencies in JavaScript/Node.js projects."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.package_json_path = self.root_path / "package.json"
        self.dependencies: Set[str] = set()
        self.declared_deps: Dict[str, str] = {}
        self.declared_devdeps: Dict[str, str] = {}
        self.used_imports: Set[str] = set()
        
    def load_package_json(self) -> bool:
        """Load package.json and extract declared dependencies."""
        if not self.package_json_path.exists():
            return False
        
        try:
            with open(self.package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            self.declared_deps = package_data.get('dependencies', {})
            self.declared_devdeps = package_data.get('devDependencies', {})
            
            self.dependencies = set(self.declared_deps.keys()) | set(self.declared_devdeps.keys())
            return True
        except Exception as e:
            print(f"Error loading package.json: {e}")
            return False
    
    def extract_imports_from_code(self, code: str) -> Set[str]:
        """Extract all imported module names from code."""
        imports = set()
        
        # ES6 imports: import foo from 'module-name'
        import_pattern = re.finditer(r'import\s+(?:{[^}]*}|[^;]*?)\s+from\s+[\'"]([^\'"]+)[\'"]', code)
        for match in import_pattern:
            module = match.group(1).split('/')[0]  # Get top-level package name
            imports.add(module)
        
        # CommonJS requires: require('module-name')
        require_pattern = re.finditer(r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)', code)
        for match in require_pattern:
            module = match.group(1).split('/')[0]  # Get top-level package name
            imports.add(module)
        
        # Dynamic imports: import('module-name')
        dynamic_pattern = re.finditer(r'import\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)', code)
        for match in dynamic_pattern:
            module = match.group(1).split('/')[0]
            imports.add(module)
        
        return imports
    
    def scan_js_files(self):
        """Scan all JS/TS files and extract imports."""
        js_files = []
        for ext in [".js", ".jsx", ".ts", ".tsx"]:
            js_files.extend(list(self.root_path.rglob(f"*{ext}")))
        
        for file_path in js_files:
            # Skip node_modules and build directories
            if 'node_modules' in str(file_path) or 'dist' in str(file_path) or 'build' in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                    imports = self.extract_imports_from_code(code)
                    self.used_imports.update(imports)
            except Exception:
                continue
    
    def detect_unused_dependencies(self) -> List[Dict]:
        """Identify dependencies declared but never imported."""
        unused = []
        
        for dep_name in self.dependencies:
            # Skip common built-ins and tools
            if dep_name not in self.used_imports and not dep_name.startswith('@types/'):
                is_dev = dep_name in self.declared_devdeps
                version = self.declared_devdeps.get(dep_name) or self.declared_deps.get(dep_name, "unknown")
                
                unused.append({
                    "name": dep_name,
                    "version": version,
                    "type": "devDependency" if is_dev else "dependency",
                    "confidence": 0.80 if is_dev else 0.65,  # Dev deps are more likely unused
                    "suggestion": f"Consider removing '{dep_name}' from {('devDependencies' if is_dev else 'dependencies')} if not used indirectly."
                })
        
        return sorted(unused, key=lambda x: x["confidence"], reverse=True)
    
    def detect_missing_dependencies(self) -> List[Dict]:
        """Identify imports used but not declared."""
        missing = []
        
        for used_import in self.used_imports:
            if used_import not in self.dependencies:
                # Skip built-ins and relative imports
                if used_import not in ['fs', 'path', 'http', 'react', 'react-dom'] and \
                   not used_import.startswith('.'):
                    missing.append({
                        "name": used_import,
                        "type": "missing_dependency",
                        "confidence": 0.70,
                        "suggestion": f"The module '{used_import}' is imported but not declared in package.json."
                    })
        
        return missing
    
    def run(self) -> Dict:
        """Run complete dependency analysis."""
        if not self.load_package_json():
            return {
                "unused_dependencies": [],
                "missing_dependencies": [],
                "total_declared": 0,
                "total_used": 0,
                "issue_count": 0
            }
        
        self.scan_js_files()
        
        unused = self.detect_unused_dependencies()
        missing = self.detect_missing_dependencies()
        
        return {
            "unused_dependencies": unused[:15],  # Top 15
            "missing_dependencies": missing[:10],  # Top 10
            "total_declared": len(self.dependencies),
            "total_used": len(self.used_imports),
            "issue_count": len(unused) + len(missing),
            "summary": f"Found {len(unused)} unused and {len(missing)} missing dependencies"
        }
