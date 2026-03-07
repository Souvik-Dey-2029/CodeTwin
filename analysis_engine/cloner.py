import os
import subprocess
import shutil
from pathlib import Path

class RepositoryCloner:
    """Utility to clone GitHub repositories for analysis."""
    
    def __init__(self, base_work_dir: str = "/tmp/codetwin"):
        self.base_work_dir = Path(base_work_dir)
        self.base_work_dir.mkdir(parents=True, exist_ok=True)

    def clone(self, github_url: str, repo_id: str) -> str:
        """
        Clones a repository to a local directory.
        Returns the path to the cloned repository.
        """
        target_dir = self.base_work_dir / repo_id
        
        # Clean up if directory already exists
        if target_dir.exists():
            shutil.rmtree(target_dir)
            
        print(f"Cloning {github_url} into {target_dir}...")
        
        try:
            # Perform a shallow clone to save time and space
            subprocess.run(
                ["git", "clone", "--depth", "1", github_url, str(target_dir)],
                check=True,
                capture_output=True,
                text=True
            )
            return str(target_dir)
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e.stderr}")
            raise Exception(f"Failed to clone repository: {e.stderr}")

    def cleanup(self, path: str):
        """Removes the cloned repository from disk."""
        if os.path.exists(path):
            shutil.rmtree(path)
