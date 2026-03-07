from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union

class CodeEmbedder:
    """Service to generate semantic embeddings for code snippets."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the model. 
        Note: all-MiniLM-L6-v2 is lightweight and effective for general semantic similarity.
        """
        self.model = SentenceTransformer(model_name)

    def encode(self, snippets: Union[str, List[str]]) -> np.ndarray:
        """
        Encodes one or more code snippets into vectors.
        Returns a numpy array of embeddings.
        """
        return self.model.encode(snippets)

    def get_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """ Calculates cosine similarity between two embeddings. """
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

if __name__ == "__main__":
    # Internal test
    embedder = CodeEmbedder()
    code1 = "def add(a, b): return a + b"
    code2 = "def sum_nums(x, y): return x + y"
    code3 = "import os; print(os.name)"
    
    vec1 = embedder.encode(code1)
    vec2 = embedder.encode(code2)
    vec3 = embedder.encode(code3)
    
    print(f"Similarity (logic matched): {embedder.get_similarity(vec1, vec2):.4f}")
    print(f"Similarity (logic different): {embedder.get_similarity(vec1, vec3):.4f}")
