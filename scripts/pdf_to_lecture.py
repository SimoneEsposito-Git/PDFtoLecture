import time
import threading
from pathlib import Path
from pdf_processing.parsing import create_json_from_pdf
from lecture_generation.llm_client import LLMClient
from tts.kokoro import tts, tts_with_timestamps, tts_parallel
from tts import get_tts_engine
from utils.logging_utils import ProcessingAnimation

INSTRUCTIONS = """
    You are an AI assistant acting as a university professor delivering a lecture based on provided slide content. 
    Your task is to transform the input, which consists of concatenated text and potential visual descriptions for multiple lecture slides, 
    into a natural-sounding, continuous spoken lecture transcript.\n\n**Input Format:**\n
    The input will be a single block of text containing the content for one or more slides. 
    Each slide's content will be **clearly indicated, starting with the word 'Slide', followed by its number, and a colon** (e.g., 'Slide 1:', 'Slide 2:'). 
    The text content for the slide follows this indicator. Descriptions of relevant visuals for a slide may be included **alongside or after the slide's text, 
    potentially enclosed in brackets or described narratively**.\n\n**Output Requirements:**\n
    1.  **Persona:** Maintain a professional, **pedagogical, explanatory,** and clear \"university professor\" tone throughout the entire transcript. 
        Adopt a tone that aims to **teach and clarify**, not just present information.\n
    2.  **Content Coverage:** For each **slide** in the input:\n    
        *   Incorporate ALL text elements associated with that slide into your spoken narrative. 
            **Ensure no text point is omitted.** Present the text in a logical order suitable for a lecture.\n    
        *   If descriptions of images, graphs, diagrams, or other visuals are provided for a slide, seamlessly integrate these descriptions into your spoken text. 
        **Explain what the visual shows and its significance** as if guiding an audience through it.\n
    3.  **Natural Flow and Elaboration:** Do NOT simply read the slide text verbatim. 
        Structure the information like an engaging professor **explaining the concepts deeply**, not just listing bullet points.\n    
        *   **Rephrase** sentences naturally for spoken delivery.\n    
        *   Add **transition** words/phrases (e.g., \"Moving on...\", \"Now, let's consider...\", \"This is crucial because...\", \"Building on that idea...\") 
            to ensure smooth flow between points and slides.\n    *   **Explain and Elaborate:** While ensuring all slide text is covered, 
            **add brief, relevant explanations, context, or motivations** behind the points to enhance understanding. 
            Where appropriate, **explain the 'why'** behind key concepts, definitions, or design choices (e.g., why is statelessness important in REST?). 
            Briefly **define key terms** pointedly when introduced.\n    
        *   **Connect Ideas:** Briefly connect the current topic back to previously discussed concepts or forward to related ideas mentioned elsewhere (if context allows) to create a **cohesive narrative**.\n
    4.  **No Meta-Commentary:** Do not say things like \"The next slide says...\" or \"As written here...\". Present the information directly as part of the lecture flow.\n
    5.  **Formatting:**\n    
        *   Generate the output as a single block of continuous text.\n    
        *   After generating the spoken text **for the content derived from each distinct 
        'Slide [number]:' block** in the input, insert **exactly one newline character** (`\\n`) to separate it from the text corresponding to the next slide. 
        Do *not* use bullet points, speaker tags (like \"Professor:\"), or excessive formatting.\n
    6.  Do Not use 'Slide ...' in the output  **Language:** Generate the lecture transcript in the **same language** as the input slide content. 
        If the slides are in German, the output must be in German. If English, output in English.\n
    7.  **Completeness:** Process all slides provided in the input sequentially based on their appearance."""

PROMPT = """
    Please act as a university professor and transform the following lecture slide content into a single, continuous spoken lecture transcript, following the system instructions precisely.\n\n
    **Key requirements:**\n*   
        Cover ALL text from each slide\n
        *   **Explain concepts thoroughly**, providing context and motivation.\n
        *   Naturally integrate descriptions of any relevant visuals mentioned (potentially in brackets or described) while ignoring irrelevant visuals such as logos and stock images.\n
        *   Maintain a consistent **pedagogical professor persona** and speaking style.\n
        *   Separate the transcript for each slide's content using exactly one newline character (\\n).\n
        *   Generate the output in the correct language, matching the input slides.\n
        *   Do not use bullet points or speaker tags.\n\n**Slide Content:**\n\n"""

def pdf_to_lecture(pdf_path, output_dir=None, visuals_dir="visuals", debug=False):
    """
    Convert a PDF file to a lecture with text (.md) and audio (.mp3).
    
    Args:
        pdf_path (str): Path to the PDF file.
        output_dir (str): Directory to save output files (default: same as PDF).
        visuals_dir (str): Directory to save visuals (default: 'visuals').
        debug (bool): Whether to generate debug information for TTS (default: False).
    
    Returns:
        tuple: Paths to the generated (json_file, md_file, mp3_file).
    """
    # Setup paths
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Use PDF directory as output directory if not specified
    if output_dir is None:
        output_dir = pdf_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
    
    # Create visuals directory (relative to output_dir)
    visuals_path = Path(output_dir) / visuals_dir
    visuals_path.mkdir(exist_ok=True)
    
    # Generate base filename from PDF name
    base_name = pdf_path.stem
    
    # Step 1: Convert PDF to JSON
    json_path = output_dir / f"{base_name}.json"
    with ProcessingAnimation(f"Converting PDF to JSON: {json_path}"):
        json_data = create_json_from_pdf(
            pdf_path=str(pdf_path),
            visuals_folder=str(visuals_path),
            prompt=PROMPT,
            instructions=INSTRUCTIONS
        )
    
    # Save JSON data to file
    with open(json_path, "w", encoding="utf-8") as json_file:
        import json
        json.dump(json_data, json_file, indent=4)
    
    # Step 2: Generate lecture markdown from JSON
    md_path = output_dir / f"{base_name}.md"
    with ProcessingAnimation(f"Generating lecture markdown: {md_path}"):
        llm_client = LLMClient(api_key="AIzaSyD-fDcgWt9-U6MEb8VfP6L6Jn3YoHPa-lw")
        markdown_text = llm_client.generate_lecture(str(json_path), 'gemini-2.0-flash')
    
    # Save markdown to file
    with open(md_path, 'w', encoding='utf-8') as md_file:
        md_file.write(markdown_text)
    
    # Step 3: Convert markdown to audio using TTS
    tts = get_tts_engine("openai")
    mp3_path = output_dir / f"{base_name}.mp3"
    with ProcessingAnimation(f"Converting lecture to audio: {mp3_path}"):
        # Run TTS on the markdown file
        # tts(
        #     text=markdown_text,
        #     output_path=str(mp3_path),
        #     debug=debug
        # )
        tts.synthesize(
            text=markdown_text,
            output_path=str(mp3_path),
            voice="alloy"
        )
    
    return json_path, md_path, mp3_path