import os
import fitz  # PyMuPDF library

def load_pdf_text(file_path):
    """
    Load text from a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Text extracted from the PDF.
    """
    try:
        with fitz.open(file_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            return text
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return ""

def find_page_number(doc, book, chapter):
    """
    Find the page number containing a specific book and chapter in a PDF document.

    Args:
        doc: PyMuPDF document object.
        book (str): Name of the book.
        chapter (str): Chapter number.

    Returns:
        int: Page number containing the specified book and chapter, or None if not found.
    """
    for i in range(len(doc)):
        page = doc.load_page(i)
        text = page.get_text().lower()
        if f"{book} {chapter}" in text:
            return i
    return None
