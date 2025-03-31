from google import genai
from google.genai import types
from lecture_generation.json_to_markdown import json_to_content

class LLMClient:
    """
    A wrapper for interacting with the LLM (e.g., Google GenAI).
    """
    def __init__(self, api_key):
        """
        Initialize the LLM client.

        Args:
            api_key (str): API key for the LLM service.
        """
        self.client = genai.Client(api_key=api_key)

    def generate_lecture(self, json_path, llm_model):
        """
        Generate lecture content using the LLM.

        Args:
            json_path (str): Path to the JSON file containing slide data.
            llm_model (str): The LLM model to use for content generation.

        Returns:
            str: The generated lecture content.
        """
        content = json_to_content(json_path)
        response = self.client.models.generate_content(
            model=llm_model,
            contents=content[1:],  # Exclude the first item (instruction) from the content
            config=types.GenerateContentConfig(
                system_instruction=content[0],  # Use the first item as the system instruction
            )
        )
        return response.text