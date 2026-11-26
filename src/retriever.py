
from pathlib import Path

from embeddings import load_embedding_model
from vector_store import VectorStore


def load_vector_database():

    # Locate project directory
    project_root = Path(__file__).resolve().parent.parent

    # Locate saved database
    database_path = (
        project_root
        / "data"
        / "processed"
    )

    print("\nLoading saved FAISS database...")

    # Load existing FAISS index and chunks
    store = VectorStore.load(database_path)

    print("Total stored vectors:", store.index.ntotal)

    # Load embedding model for user queries
    model = load_embedding_model()

    print("\nDatabase ready for searching!")

    return model, store


def search_sap_documents(model, store, question):

    print("\nSearching SAP documentation...")

    # Convert user question into embedding
    query_embedding = model.encode(
        question,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # Search FAISS database
    results = store.search(
        query_embedding,
        top_k=3
    )

    print("\nTOP RELEVANT SAP DOCUMENTS")
    print("=" * 60)

    for i, result in enumerate(results, start=1):

        print(f"\nResult {i}")
        print("Similarity:", result["score"])
        print("Source:", result["source"])
        print("Page:", result["page"])
        print("Chunk ID:", result["chunk_id"])
        print("Content:", result["text"])
        print("-" * 60)


if __name__ == "__main__":

    # Load existing database instead of rebuilding it
    model, store = load_vector_database()

    while True:

        question = input(
            "\nEnter your SAP question (or type exit): "
        )

        if question.lower().strip() == "exit":
            print("Closing SAP document search.")
            break

        if not question.strip():
            print("Please enter a question.")
            continue

        search_sap_documents(
            model,
            store,
            question
        )
