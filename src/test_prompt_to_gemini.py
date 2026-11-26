
from prompt_builder import build_sap_prompt
from llm import generate_response


def test_prompt_to_gemini():

    # Sample context for this connection test.
    # Later, we will replace this with actual FAISS results.
    sample_context = """
    SAP S/4HANA is an enterprise resource planning system.
    It supports integrated business processes.
    It helps organizations manage business operations
    using an integrated system.
    """

    question = "What is SAP S/4HANA?"

    print("\nBuilding SAP prompt...")

    prompt = build_sap_prompt(
        context=sample_context,
        question=question
    )

    print("\nSending prompt to Gemini...\n")

    answer = generate_response(prompt)

    print("=" * 50)
    print("GEMINI RESPONSE")
    print("=" * 50)

    print(answer)


if __name__ == "__main__":
    test_prompt_to_gemini()
