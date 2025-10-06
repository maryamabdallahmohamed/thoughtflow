from pathlib import Path
from PyPDF2 import PdfReader

def pdf_to_paragraphs(pdf_path: str) -> list[str]:
    """
    Extract text from a PDF and return it as a list of paragraphs.
    Each paragraph will be cleaned of empty lines.
    """
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"File not found: {pdf_file}")

    reader = PdfReader(pdf_file)
    paragraphs = []

    for page in reader.pages:
        text = page.extract_text() or ""
        # Split into paragraphs
        parts = [p.strip() for p in text.split("\n") if p.strip()]
        paragraphs.extend(parts)

    return paragraphs

#returns a list of paragraphs
