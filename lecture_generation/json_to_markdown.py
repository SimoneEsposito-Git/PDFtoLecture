from PIL import Image
import json

def json_to_content(json_path):
    """
    Convert a JSON file to a list of content objects for LLM processing.

    Args:
        json_path (str): Path to the JSON file.

    Returns:
        list: A list of content objects including instructions, prompts, slide text, and visuals.
    """
    with open(json_path, "r") as json_file:
        data = json.load(json_file)
    
    content = []
    for item in data:
        if "instruction" in item:
            content.append(item["instruction"])
        
        if "prompt" in item:
            content.append(item["prompt"])
            
        if "page" in item:
            content.append(f"Slide {item['page']}")
            
        if "text_content" in item:
            content.append(item["text_content"])
        
        if "visuals" in item:
            for visual in item["visuals"]:
                image_path = visual["file_path"]
                image = Image.open(image_path)
                content.append(image)
    
    return content