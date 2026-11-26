
from pathlib import Path
import pymupdf


def extract_text_from_pdf(pdf_path):
    """
    Open a PDF and extract text from every page.
    """

    pdf_path = Path(pdf_path)

    # Check whether the PDF exists
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    extracted_pages = []

    # Open the PDF
    with pymupdf.open(pdf_path) as pdf:

        print("Total pages:", len(pdf))

        # Read each page
        for page_number, page in enumerate(pdf, start=1):

            text = page.get_text("text").strip()

            # Store pages containing text
            if text:
                extracted_pages.append({
                    "source": pdf_path.name,
                    "page": page_number,
                    "text": text
                })

    return extracted_pages


def save_extracted_text(pages, output_path):
    """
    Save extracted PDF text into a TXT file.
    """

    output_path = Path(output_path)

    # Create output folder if it doesn't exist
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_path, "w", encoding="utf-8") as file:

        for page in pages:

            file.write(
                f"\n--- Page {page['page']} ---\n"
            )

            file.write(page["text"])
            file.write("\n")

    print("Extracted text saved:", output_path)


if __name__ == "__main__":

    # Main project folder
    project_root = Path(__file__).resolve().parent.parent

    # PDF input location
    pdf_path = project_root / "data" / "raw" / "sap_s4hana_2025.pdf"

    # Text output location
    output_path = (
        project_root
        / "data"
        / "processed"
        / "sap_extracted.txt"
    )

    print("Starting PDF extraction...")

    pages = extract_text_from_pdf(pdf_path)

    if not pages:
        print("No selectable text found. This PDF may need OCR.")
    else:
        save_extracted_text(pages, output_path)

        print("Pages containing text:", len(pages))

        print("\nFirst 1000 characters:")
        print(pages[0]["text"][:1000])

    print("\nPDF processing completed!")
