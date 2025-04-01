import fitz  # PyMuPDF
import os
from pathlib import Path
from pdf_processing.ocr import extract_text_from_pdf

def extract_images_from_pdf(pdf_path, visuals_folder):
    """
    Extracts images from a PDF and saves them to the specified folder.

    Args:
        pdf_path (str): Path to the PDF file.
        visuals_folder (str): Path to the folder where extracted images will be saved.

    Returns:
        list: A list of dictionaries containing metadata about the extracted images.
    """
    visuals = []
    Path(visuals_folder).mkdir(parents=True, exist_ok=True)

    with fitz.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf, start=1):
            for img_index, img in enumerate(page.get_images(full=True), start=1):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = f"page_{page_num}_img_{img_index}.{image_ext}"
                image_path = os.path.join(visuals_folder, image_filename)

                # Save the image
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                # Add metadata to visuals list
                visuals.append({
                    "page": page_num,
                    "image_index": img_index,
                    "file_path": image_path,
                    "prompt_hint": f"page {page_num}"
                })
    return visuals

def create_json_from_pdf(pdf_path, visuals_folder, instructions=None, prompt=None):
    """
    Extracts text and images from a PDF and creates a JSON-like structure.

    Args:
        pdf_path (str): Path to the PDF file.
        visuals_folder (str): Path to the folder where extracted images will be saved.

    Returns:
        list: A list of dictionaries containing text and visuals for each page.
    """
    # Extract text for all pages
    text_content_list = extract_text_from_pdf(pdf_path)

    # Extract images for all pages
    all_visuals = extract_images_from_pdf(pdf_path, visuals_folder)

    # Create results for all pages
    results = []
    results.append({
        "instructions": instructions,
        "prompt": prompt
    })
    for page_idx, text in enumerate(text_content_list):
        page_num = page_idx + 1

        # Filter visuals for this page
        page_visuals = [v for v in all_visuals if v["page"] == page_num]

        # Create page data
        page_data = {
            "page": page_num,
            "text_content": text,
            "visuals": page_visuals
        }
        results.append(page_data)

    return results