import pdfplumber

def pdf_to_text(pdf_path: str):
    with pdfplumber.open(pdf_path) as pdf:
        return [page.extract_text() or "" for page in pdf.pages]
