
from retriever import load_vector_database

# Test questions
TEST_QUESTIONS = [
    "What is SAP S/4HANA?",
    "What are the main features of SAP S/4HANA?",
    "Explain SAP business processes.",
    "What is the capital of Japan?"
]

# Thresholds to compare
THRESHOLDS = [0.30, 0.40, 0.45, 0.50, 0.55, 0.60]


def evaluate_retrieval(model, store):

    print("\nLoading retrieval evaluation...")

    all_results = []

    for question in TEST_QUESTIONS:

        query_embedding = model.encode(
            question,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        results = store.search(query_embedding, top_k=3)

        all_results.append({
            "question": question,
            "results": results
        })

    print("\n" + "=" * 65)
    print("RETRIEVAL SIMILARITY EVALUATION")
    print("=" * 65)

    for item in all_results:

        print("\nQuestion:", item["question"])

        for result in item["results"]:
            print(
                f"Score: {result['score']:.4f} | "
                f"Page: {result['page']} | "
                f"Chunk: {result['chunk_id']}"
            )

    print("\n" + "=" * 65)
    print("THRESHOLD COMPARISON")
    print("=" * 65)

    for threshold in THRESHOLDS:

        print(f"\nThreshold: {threshold:.2f}")

        for item in all_results:

            accepted = [
                result for result in item["results"]
                if result["score"] >= threshold
            ]

            print(
                f"{item['question']} "
                f"-> {len(accepted)} relevant chunks retained"
            )


if __name__ == "__main__":

    model, store = load_vector_database()

    evaluate_retrieval(model, store)
