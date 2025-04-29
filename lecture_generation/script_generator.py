from PIL import Image
import json
from lecture_generation.base_llm_client import BaseLLMClient

def generate_script_for_page(llm_client: BaseLLMClient, prompt: str, page_data: dict, previous_page_data: dict = None,instruction: str = None):
    """
    Convert a JSON file to a list of content objects for LLM processing.

    Args:
        json_path (str): Path to the JSON file.

    Returns:
        list: A list of content objects including instructions, prompts, slide text, and visuals.
    """
    content = []
    content.append(prompt)
    
    if previous_page_data:
        content.append("**PREVIOUS TEXT DATA:**\n")
        if "text_content" in previous_page_data:
            content.append(previous_page_data["text_content"])
        if "visuals" in previous_page_data:
            for visual in previous_page_data["visuals"]:
                if visual["type"] == "image":
                    image_path = visual["uri"]
                    image = Image.open(image_path)
                    content.append(image)
    
    if page_data:
        content.append("**PAGE DATA:**\n")                 
        if "text_content" in page_data:
                content.append(page_data["text_content"])

        if "visuals" in page_data:
            for visual in page_data["visuals"]:
                if visual["type"] == "image":
                    image_path = visual["uri"]
                    image = Image.open(image_path)
                    content.append(image)
                    
    # llm_client.add_system_instruction(instruction)
    response = llm_client.process_text(content)
    
    return response
    
    