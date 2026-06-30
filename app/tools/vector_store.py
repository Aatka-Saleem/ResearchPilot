import os
import json
import faiss
import numpy as np
from typing import List, Dict, Any

class FAISSVectorStore:
    """A clean wrapper around FAISS to manage document embedding index and text metadata."""
    def __init__(self, dimension: int = None):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension) if dimension is not None else None
        self.documents: List[str] = []

    def add_documents(self, docs: List[str], embeddings: List[List[float]]):
        """Adds documents and their corresponding embeddings to the index."""
        if not docs or not embeddings:
            return
        if len(docs) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings.")
            
        self.documents.extend(docs)
        embeddings_np = np.array(embeddings, dtype=np.float32)
        
        if self.index is None:
            self.dimension = embeddings_np.shape[1]
            self.index = faiss.IndexFlatL2(self.dimension)
            
        self.index.add(embeddings_np)

    def save(self, filepath_prefix: str):
        """Saves the FAISS index and the corresponding document texts to disk."""
        # Ensure directories exist
        os.makedirs(os.path.dirname(filepath_prefix), exist_ok=True)
        
        # Save FAISS index binary
        index_path = f"{filepath_prefix}.index"
        faiss.write_index(self.index, index_path)
        
        # Save documents as JSON mapping
        docs_path = f"{filepath_prefix}.docs.json"
        with open(docs_path, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)

    def load(self, filepath_prefix: str):
        """Loads the FAISS index and the documents from disk."""
        index_path = f"{filepath_prefix}.index"
        docs_path = f"{filepath_prefix}.docs.json"
        
        if not os.path.exists(index_path) or not os.path.exists(docs_path):
            raise FileNotFoundError(f"FAISS index files not found at prefix: {filepath_prefix}")
            
        self.index = faiss.read_index(index_path)
        with open(docs_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

    def search(self, query_embedding: List[float], k: int = 3) -> List[Dict[str, Any]]:
        """Queries the vector index using the query embedding and returns the top k matches."""
        query_np = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_np, k)
        
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if 0 <= idx < len(self.documents):
                results.append({
                    "document": self.documents[idx],
                    "score": float(distance) # L2 distance (lower is closer/better)
                })
        return results
