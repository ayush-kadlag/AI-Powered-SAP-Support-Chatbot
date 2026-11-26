
def chunk_text(text, chunk_size=150, overlap=30):
    """
    Divide text into smaller chunks using words.
    """

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size")

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk_words = words[start:end]

        chunk = " ".join(chunk_words)

        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def chunk_documents(pages, chunk_size=150, overlap=30):
    """
    Create chunks while preserving document metadata.
    """

    all_chunks = []

    for page in pages:

        text = page["text"]

        page_chunks = chunk_text(
            text,
            chunk_size,
            overlap
        )

        for chunk_number, chunk in enumerate(page_chunks, start=1):

            all_chunks.append({
                "source": page["source"],
                "page": page["page"],
                "chunk_id": chunk_number,
                "text": chunk
            })

    return all_chunks


if __name__ == "__main__":

    from document_loader import extract_text_from_pdf
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent

    pdf_path = project_root / "data" / "raw" / "sap_s4hana_2025.pdf"

    pages = extract_text_from_pdf(pdf_path)

    chunks = chunk_documents(
        pages,
        chunk_size=500,
        overlap=50
    )

    print("Total pages:", len(pages))
    print("Total chunks:", len(chunks))

    if chunks:

        print("\nFirst chunk:")
        print(chunks[0]["text"])

        print("\nFirst chunk metadata:")
        print({
            "source": chunks[0]["source"],
            "page": chunks[0]["page"],
            "chunk_id": chunks[0]["chunk_id"]
        })
