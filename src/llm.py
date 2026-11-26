
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_PATH)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.6-flash"


# --------------------------------------------------
# 2. RETRY CONFIGURATION
# --------------------------------------------------

MAX_RETRIES = 3
BASE_DELAY_SECONDS = 2

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


# --------------------------------------------------
# 3. GENERATE RESPONSE
# --------------------------------------------------

def generate_response(prompt: str) -> str:

    """
    Send a prompt to Gemini and return its response.

    Automatically retries temporary API failures.
    Also displays generation diagnostics.
    """

    if not API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found. Check your .env file."
        )

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    client = genai.Client(api_key=API_KEY)

    for attempt in range(MAX_RETRIES + 1):

        try:

            print(
                f"Sending API request "
                f"(Attempt {attempt + 1}/{MAX_RETRIES + 1})..."
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=800
                )
            )

            # --------------------------------------
            # GENERATION DIAGNOSTICS
            # --------------------------------------

            print("\n========== GEMINI DIAGNOSTICS ==========")

            candidates = response.candidates or []

            if candidates:
                candidate = candidates[0]
                print("Finish reason:", candidate.finish_reason)
            else:
                print("Finish reason: No candidates returned")

            usage = response.usage_metadata

            if usage:
                print(
                    "Prompt tokens:",
                    usage.prompt_token_count
                )
                print(
                    "Output tokens:",
                    usage.candidates_token_count
                )
                print(
                    "Total tokens:",
                    usage.total_token_count
                )
            else:
                print("Token usage information unavailable.")

            answer = response.text

            if not answer:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            print("Response characters:", len(answer))
            print("========================================\n")

            return answer

        except APIError as error:

            status = getattr(error, "code", None)

            if status in RETRYABLE_STATUS_CODES:

                if attempt == MAX_RETRIES:
                    break

                delay = BASE_DELAY_SECONDS * (2 ** attempt)

                print(
                    f"API error {status}. "
                    f"Retrying in {delay} seconds..."
                )

                time.sleep(delay)
                continue

            if status == 400:
                message = "Invalid request. Check your prompt."

            elif status == 403:
                message = "API access denied. Check permissions."

            elif status == 404:
                message = "Model not found. Check model name."

            else:
                message = "Gemini API request failed."

            raise RuntimeError(
                f"{message} Details: {error}"
            ) from error

    if status == 429:
        message = (
            "Gemini rate limit or quota exceeded. "
            "Check your API usage and limits."
        )

    elif status == 503:
        message = (
            "Gemini service is temporarily overloaded. "
            "Please try again later."
        )

    else:
        message = (
            "Gemini API is temporarily unavailable. "
            "Please try again later."
        )

    raise RuntimeError(
        f"{message} Details: {error}"
    ) from error


# --------------------------------------------------
# 4. TEST GEMINI API CONNECTION
# --------------------------------------------------

if __name__ == "__main__":

    test_prompt = """
    Explain SAP S/4HANA in simple language.

    Give:
    1. A simple definition.
    2. Two important features.
    3. One real-world example.

    Keep the answer beginner-friendly.
    """

    print("\nConnecting to Gemini API...\n")

    try:

        answer = generate_response(test_prompt)

        print("\nGemini API connection successful!")
        print("\nGenerated Answer:\n")
        print(answer)

    except Exception as error:

        print("\nAPI connection failed!")
        print("Error:", error)
