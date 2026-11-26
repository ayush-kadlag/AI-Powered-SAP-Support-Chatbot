from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from document_loader import extract_text_from_pdf
from text_chunker import chunk_documents


# 1. Select the embedding model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_embedding_model():
    """Load the pretrained sentence embedding model."""
    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)
    print("Embedding model loaded successfully!")
    print("Maximum input tokens:", model.max_seq_length)
    return model


def generate_embeddings(model, chunks):
    """Convert document chunks into numerical vectors."""
    texts = [chunk["text"] for chunk in chunks]

    print("Generating embeddings...")
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return np.asarray(embeddings, dtype=np.float32)


if __name__ == "__main__":

    # 2. Find the project folder
    project_root = Path(__file__).resolve().parent.parent

    # 3. Load the SAP PDF
    pdf_path = project_root / "data" / "raw" / "sap_s4hana_2025.pdf"

    print("Reading SAP PDF...")
    pages = extract_text_from_pdf(pdf_path)

    # 4. Split extracted pages into smaller chunks
    chunks = chunk_documents(
        pages,
        chunk_size=150,
        overlap=30
    )

    print("Total chunks:", len(chunks))

    if not chunks:
        raise ValueError("No text chunks found. Check the SAP PDF extraction.")

    # 5. Load the embedding model
    model = load_embedding_model()

    # 6. Convert chunks into vectors
    embeddings = generate_embeddings(model, chunks)

    # 7. Display the results
    print("\nEMBEDDING RESULTS")
    print("-----------------")
    print("Number of chunks:", len(chunks))
    print("Embedding shape:", embeddings.shape)
    print("Numbers in each vector:", embeddings.shape[1])

    print("\nFirst chunk:")
    print(chunks[0]["text"][:300])

    print("\nFirst 10 numbers of its embedding:")
    print(embeddings[0][:10])

    print("\nVector length:", np.linalg.norm(embeddings[0]))

    print("\nEmbeddings generated successfully!")