import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """
    Extracts text content from all pages of a PDF.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        list: A list of strings, where each string contains the text of a page.
    """
    text_content_list = []
    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            text_content_list.append(page.get_text())
    return text_content_list