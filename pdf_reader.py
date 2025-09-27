import os
from PyPDF2 import PdfReader

def extract_text_from_pdf(filename: str) -> str:
    """Reads and extracts full text from a given PDF file using PyPDF2."""
    pdf_path = os.path.join("pdfs", filename)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"❌ File not found: {pdf_path}")

    text = ""
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text.strip()
