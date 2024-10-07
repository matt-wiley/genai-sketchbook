import faiss
import numpy as np
import os
from typing import List, Dict, Any

class FAISSStorage:
    def __init__(self, index_path: str, dimension: int):
        self.index_path = index_path
        self.dimension = dimension
        self.index = self._load_or_create_index()
        self.id_to_path: Dict[int, str] = {}
        self.next_id = 0

    def _load_or_create_index(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        if os.path.exists(self.index_path):
            return faiss.read_index(self.index_path)
        else:
            index = faiss.IndexFlatL2(self.dimension)
            faiss.write_index(index, self.index_path)
            return index

    def store_embedding(self, file_path: str, embedding: List[float]):
        embedding_np = np.array([embedding], dtype=np.float32)
        self.index.add(embedding_np)
        self.id_to_path[self.next_id] = file_path
        self.next_id += 1
        self._save_index()

    def _save_index(self):
        faiss.write_index(self.index, self.index_path)

    def search_similar(self, query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        query_np = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_np, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1:  # FAISS uses -1 for empty slots
                results.append({
                    "file_path": self.id_to_path[idx],
                    "distance": float(dist)
                })
        
        return results

    def get_all_embeddings(self) -> Dict[str, List[float]]:
        all_embeddings = {}
        for i in range(self.index.ntotal):
            embedding = self.index.reconstruct(i)
            file_path = self.id_to_path[i]
            all_embeddings[file_path] = embedding.tolist()
        return all_embeddings

    def __len__(self):
        return self.index.ntotal
