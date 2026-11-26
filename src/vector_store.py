
import faiss
import numpy as np
import json

from pathlib import Path


class VectorStore:

    def __init__(self, dimension):
        self.dimension = dimension

        # Create FAISS inner product index
        self.index = faiss.IndexFlatIP(dimension)

        # Store original document chunks
        self.text_chunks = []

    def add_embeddings(self, embeddings, chunks):

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32
        )

        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be 2D")

        if embeddings.shape[1] != self.dimension:
            raise ValueError("Embedding dimension mismatch")

        if len(embeddings) != len(chunks):
            raise ValueError("Chunks and embeddings mismatch")

        self.index.add(embeddings)
        self.text_chunks.extend(chunks)

        print(f"Stored {len(chunks)} vectors in FAISS!")

    def search(self, query_embedding, top_k=3):

        if self.index.ntotal == 0:
            raise ValueError("FAISS index is empty")

        query_embedding = np.asarray(
            [query_embedding],
            dtype=np.float32
        )

        if query_embedding.shape[1] != self.dimension:
            raise ValueError("Query embedding dimension mismatch")

        scores, indices = self.index.search(
            query_embedding,
            min(top_k, self.index.ntotal)
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx != -1:
                results.append({
                    "text": self.text_chunks[idx]["text"],
                    "source": self.text_chunks[idx]["source"],
                    "page": self.text_chunks[idx]["page"],
                    "chunk_id": self.text_chunks[idx]["chunk_id"],
                    "score": float(score)
                })

        return results

    def save(self, folder_path):

        folder = Path(folder_path)
        folder.mkdir(parents=True, exist_ok=True)

        index_path = folder / "faiss_index.bin"
        chunks_path = folder / "chunks.json"

        # Save FAISS index
        faiss.write_index(
            self.index,
            str(index_path)
        )

        # Save document chunks and metadata
        with open(chunks_path, "w", encoding="utf-8") as file:
            json.dump(
                self.text_chunks,
                file,
                ensure_ascii=False,
                indent=4
            )

        print("FAISS database saved successfully!")

    @classmethod
    def load(cls, folder_path):

        folder = Path(folder_path)

        index_path = folder / "faiss_index.bin"
        chunks_path = folder / "chunks.json"

        if not index_path.exists() or not chunks_path.exists():
            raise FileNotFoundError(
                "FAISS database files not found!"
            )

        # Load FAISS index
        index = faiss.read_index(str(index_path))

        # Create VectorStore object
        store = cls(index.d)

        store.index = index

        # Load original document chunks
        with open(chunks_path, "r", encoding="utf-8") as file:
            store.text_chunks = json.load(file)

        # Validate index and chunks
        if store.index.ntotal != len(store.text_chunks):
            raise ValueError(
                "FAISS index and chunk count do not match"
            )

        print("FAISS database loaded successfully!")

        return store
