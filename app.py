
import sys
from pathlib import Path

import streamlit as st


# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

PROJECT_DIR = Path(__file__).resolve().parent
SRC_DIR = PROJECT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

from retriever import load_vector_database
from rag_pipeline import ask_sap_question


# ==================================================
# 2. STREAMLIT PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="SAP AI Support Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# 3. CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.main-title {
    font-size: 36px;
    font-weight: 700;
}

.subtitle {
    color: #808080;
    font-size: 16px;
}

.source-card {
    padding: 12px;
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# 4. LOAD BACKEND ONLY ONCE
# ==================================================

@st.cache_resource(show_spinner="Loading SAP knowledge base...")

def load_backend():

    model, store = load_vector_database()

    return model, store


# ==================================================
# 5. SOURCE DOCUMENT DISPLAY
# ==================================================

def display_sources(sources):

    if not sources:

        st.info("No supporting SAP document sources found.")

        return

    st.markdown("#### 📚 Retrieved SAP Sources")

    for i, source in enumerate(sources, start=1):

        score = float(source["score"])

        with st.expander(
            f"Source {i} | Page {source['page']} | Similarity: {score:.3f}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                st.write("**Document**")

                st.write(source["source"])

                st.write("**Page Number**")

                st.write(source["page"])

            with col2:

                st.write("**Chunk ID**")

                st.write(source["chunk_id"])

                st.write("**Similarity Score**")

                st.metric(
                    label="Cosine Similarity",
                    value=f"{score:.4f}"
                )

            st.divider()

            st.markdown("**Retrieved Document Content**")

            st.write(source["text"])


# ==================================================
# 6. INITIALIZE SESSION STATE
# ==================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ==================================================
# 7. SIDEBAR
# ==================================================

with st.sidebar:

    st.title("🤖 SAP Assistant")

    st.caption("AI-powered SAP knowledge assistant")

    st.divider()

    st.markdown("### Conversation")

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.markdown("### Project Technologies")

    technologies = [
        "Python",
        "Streamlit",
        "Google Gemini API",
        "Sentence Transformers",
        "FAISS",
        "NumPy",
        "RAG Architecture"
    ]

    for technology in technologies:

        st.write(f"• {technology}")

    st.divider()

    st.markdown("### About")

    st.caption(
        "This chatbot retrieves relevant information "
        "from SAP documentation and uses Gemini "
        "to generate answers."
    )


# ==================================================
# 8. MAIN PAGE HEADER
# ==================================================

st.markdown(
    '<div class="main-title">SAP AI Support Assistant 🤖</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask questions about SAP S/4HANA using Retrieval-Augmented Generation.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==================================================
# 9. LOAD BACKEND
# ==================================================

try:

    model, store = load_backend()

    st.success("SAP knowledge base connected successfully.")

except Exception:

    st.error(
        "Unable to load the SAP knowledge base. "
        "Please check the backend configuration."
    )

    with st.expander("Technical error details"):

        st.exception(Exception("Backend initialization failed. Check terminal output."))

    st.stop()


# ==================================================
# 10. EXAMPLE QUESTIONS
# ==================================================

if not st.session_state.messages:

    st.markdown("### Welcome!")

    st.write(
        "You can start by asking a question about SAP S/4HANA."
    )

    st.markdown("**Example questions:**")

    example_questions = [
        "What is SAP S/4HANA?",
        "What are the main features of SAP S/4HANA?",
        "Explain SAP business processes."
    ]

    for example in example_questions:

        if st.button(example, use_container_width=True):

            st.session_state.pending_question = example

            st.rerun()


# ==================================================
# 11. DISPLAY CHAT HISTORY
# ==================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            display_sources(
                message.get("sources", [])
            )


# ==================================================
# 12. GET USER QUESTION
# ==================================================

question = st.chat_input(
    "Ask your SAP question here..."
)

# Support example-question buttons.
if "pending_question" in st.session_state:

    question = st.session_state.pop("pending_question")


# ==================================================
# 13. PROCESS USER QUESTION
# ==================================================

if question:

    question = question.strip()

    if question:

        # Display user question.

        st.session_state.messages.append({

            "role": "user",

            "content": question

        })

        with st.chat_message("user"):

            st.markdown(question)

        # Generate assistant response.

        with st.chat_message("assistant"):

            try:

                with st.spinner(
                    "Searching SAP documents and generating your answer..."
                ):

                    result = ask_sap_question(
                        question=question,
                        model=model,
                        store=store
                    )

                answer = result["answer"]

                sources = result["sources"]

                st.markdown(answer)

                display_sources(sources)

                # Save complete assistant response.

                st.session_state.messages.append({

                    "role": "assistant",

                    "content": answer,

                    "sources": sources

                })

            except Exception as error:

                st.error(
                    "Something went wrong while processing "
                    "your question. Please try again."
                )

                # Keep detailed diagnostics in the terminal.
                print("Question processing failed:", repr(error))

                st.session_state.messages.append({

                    "role": "assistant",

                    "content": (
                        "Sorry, I could not process your question. "
                        "Please try again."
                    ),

                    "sources": []

                })


# ==================================================
# 14. FOOTER
# ==================================================

st.divider()

st.caption(
    "AI-Powered SAP Support Chatbot | "
    "Built using Python, FAISS, RAG and Google Gemini"
)
