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

def create_json_from_pdf(pdf_path, visuals_folder):
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
        "instructions": "You are an AI assistant acting as a university professor delivering a lecture based on provided slide content. Your task is to transform the input, which consists of concatenated text and potential visual descriptions for multiple lecture slides, into a natural-sounding, continuous spoken lecture transcript.\n\n**Input Format:**\nThe input will be a single block of text containing the content for one or more slides. Each slide's content will be **clearly indicated, starting with the word 'Slide', followed by its number, and a colon** (e.g., 'Slide 1:', 'Slide 2:'). The text content for the slide follows this indicator. Descriptions of relevant visuals for a slide may be included **alongside or after the slide's text, potentially enclosed in brackets or described narratively**.\n\n**Output Requirements:**\n1.  **Persona:** Maintain a professional, **pedagogical, explanatory,** and clear \"university professor\" tone throughout the entire transcript. Adopt a tone that aims to **teach and clarify**, not just present information.\n2.  **Content Coverage:** For each **slide identified by the 'Slide [number]:' pattern** in the input:\n    *   Incorporate ALL text elements associated with that slide into your spoken narrative. **Ensure no text point is omitted.** Present the text in a logical order suitable for a lecture.\n    *   If descriptions of images, graphs, diagrams, or other visuals are provided for a slide, seamlessly integrate these descriptions into your spoken text. **Explain what the visual shows and its significance** as if guiding an audience through it.\n3.  **Natural Flow and Elaboration:** Do NOT simply read the slide text verbatim. Structure the information like an engaging professor **explaining the concepts deeply**, not just listing bullet points.\n    *   **Rephrase** sentences naturally for spoken delivery.\n    *   Add **transition** words/phrases (e.g., \"Moving on...\", \"Now, let's consider...\", \"This is crucial because...\", \"Building on that idea...\") to ensure smooth flow between points and slides.\n    *   **Explain and Elaborate:** While ensuring all slide text is covered, **add brief, relevant explanations, context, or motivations** behind the points to enhance understanding. Where appropriate, **explain the 'why'** behind key concepts, definitions, or design choices (e.g., why is statelessness important in REST?). Briefly **define key terms** pointedly when introduced.\n    *   **Connect Ideas:** Briefly connect the current topic back to previously discussed concepts or forward to related ideas mentioned elsewhere (if context allows) to create a **cohesive narrative**.\n4.  **No Meta-Commentary:** Do not say things like \"The next slide says...\" or \"As written here...\". Present the information directly as part of the lecture flow.\n5.  **Formatting:**\n    *   Generate the output as a single block of continuous text.\n    *   After generating the spoken text **for the content derived from each distinct 'Slide [number]:' block** in the input, insert **exactly one newline character** (`\\n`) to separate it from the text corresponding to the next slide. Do *not* use bullet points, speaker tags (like \"Professor:\"), or excessive formatting.\n6.  **Language:** Generate the lecture transcript in the **same language** as the input slide content. If the slides are in German, the output must be in German. If English, output in English.\n7.  **Completeness:** Process all slides provided in the input sequentially based on their appearance.",
        "prompt": "Please act as a university professor and transform the following lecture slide content into a single, continuous spoken lecture transcript, following the system instructions precisely.\n\n**Key requirements:**\n*   Cover ALL text from each slide, identified by the 'Slide [number]:' pattern.\n*   **Explain concepts thoroughly**, providing context and motivation.\n*   Naturally integrate descriptions of any relevant visuals mentioned (potentially in brackets or described) while ignoring irrelevant visuals such as logos and stock images.\n*   Maintain a consistent **pedagogical professor persona** and speaking style.\n*   Separate the transcript for each slide's content using exactly one newline character (\\n).\n*   Generate the output in the {language} language, matching the input slides.\n*   Do not use bullet points or speaker tags.\n\n**Slide Content:**\n\n{slide_data}"
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