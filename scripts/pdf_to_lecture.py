from pathlib import Path
from pdf_processing.parsing import create_json_from_pdf
from lecture_generation.llm_client import LLMClient
from tts.kokoro import tts, tts_with_timestamps

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
    print(f"Converting PDF to JSON: {json_path}")
    json_data = create_json_from_pdf(
        pdf_path=str(pdf_path),
        visuals_folder=str(visuals_path)
    )
    
    # Save JSON data to file
    with open(json_path, "w", encoding="utf-8") as json_file:
        import json
        json.dump(json_data, json_file, indent=4)
    
    # Step 2: Generate lecture markdown from JSON
    md_path = output_dir / f"{base_name}.md"
    print(f"Generating lecture markdown: {md_path}")
    llm_client = LLMClient(api_key="AIzaSyD-fDcgWt9-U6MEb8VfP6L6Jn3YoHPa-lw")
    markdown_text = llm_client.generate_lecture(str(json_path), 'gemini-2.0-flash')
    
    # Save markdown to file
    with open(md_path, 'w', encoding='utf-8') as md_file:
        md_file.write(markdown_text)
    
    # Step 3: Convert markdown to audio using TTS
    mp3_path = output_dir / f"{base_name}.mp3"
    print(f"Converting lecture to audio: {mp3_path}")
    
    # Run TTS on the markdown file
    tts_with_timestamps(
        input_text=markdown_text.splitlines(),
        output_audio_path=str(mp3_path),
        debug=debug
    )
    
    return json_path, md_path, mp3_path