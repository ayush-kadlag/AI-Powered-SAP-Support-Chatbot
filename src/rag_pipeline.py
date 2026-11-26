
from retriever import load_vector_database
from prompt_builder import build_sap_prompt
from llm import generate_response


# Provisional threshold based on our evaluation.
MIN_SIMILARITY_SCORE = 0.60


def retrieve_context(model, store, question, top_k=3):
    query_embedding = model.encode(
        question,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    results = store.search(query_embedding, top_k=top_k)

    relevant_results = [
        result for result in results
        if result["score"] >= MIN_SIMILARITY_SCORE
    ]

    return relevant_results


def prepare_context(results):
    context_parts = []

    for i, result in enumerate(results, start=1):
        document = f"""
Document {i}

Source: {result['source']}
Page: {result['page']}
Chunk ID: {result['chunk_id']}
Similarity Score: {result['score']}

Content:
{result['text']}
"""
        context_parts.append(document.strip())

    return "\n\n".join(context_parts)


def ask_sap_question(question, model, store):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    print("\nRetrieving SAP information...")

    results = retrieve_context(model, store, question)

    print("Relevant chunks found:", len(results))
    print("Minimum similarity threshold:", MIN_SIMILARITY_SCORE)

    if not results:
        return {
            "question": question,
            "answer": (
                "I could not find sufficiently relevant information "
                "in the SAP documentation to answer this question."
            ),
            "sources": []
        }

    context = prepare_context(results)

    print("\nBuilding structured prompt...")

    prompt = build_sap_prompt(
        context=context,
        question=question
    )

    print("Prompt created successfully!")

    print("\nSending information to Gemini...")

    answer = generate_response(prompt)

    return {
        "question": question,
        "answer": answer,
        "sources": results
    }


if __name__ == "__main__":

    print("\n" + "=" * 55)
    print("AI-POWERED SAP SUPPORT CHATBOT")
    print("=" * 55)

    try:
        model, store = load_vector_database()

        print("\nSAP chatbot is ready!")

        while True:

            question = input(
                "\nAsk your SAP question (or type exit): "
            )

            if question.strip().lower() == "exit":
                print("\nClosing SAP chatbot.")
                break

            if not question.strip():
                print("Please enter a question.")
                continue

            try:
                result = ask_sap_question(
                    question,
                    model,
                    store
                )

                print("\n" + "=" * 55)
                print("GENERATED SAP ANSWER")
                print("=" * 55)

                print(result["answer"])

                print("\n" + "=" * 55)
                print("RETRIEVED SOURCES")
                print("=" * 55)

                if not result["sources"]:
                    print("No sufficiently relevant sources found.")

                for i, source in enumerate(
                    result["sources"],
                    start=1
                ):
                    print(f"\nSource {i}")
                    print("File:", source["source"])
                    print("Page:", source["page"])
                    print("Chunk ID:", source["chunk_id"])
                    print("Similarity:", source["score"])

            except Exception as error:
                print("\nQuestion processing failed!")
                print("Error:", str(error))

    except Exception as error:
        print("\nChatbot initialization failed!")
        print("Error:", str(error))
