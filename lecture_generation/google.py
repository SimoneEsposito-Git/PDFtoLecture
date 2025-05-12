from google import genai
from google.genai import types
from lecture_generation.base_llm_client import BaseLLMClient

class GoogleLLMClient(BaseLLMClient):
    """
    A wrapper for interacting with the LLM (e.g., Google GenAI).
    """
    def __init__(self, model, api_key):
        """
        Initialize the LLM client.

        Args:
            api_key (str): API key for the LLM service.
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def process_text(self, prompt, text, instruction=None):
        """
        Generate lecture content using the LLM.

        Args:
            json_path (str): Path to the JSON file containing slide data.
            llm_model (str): The LLM model to use for content generation.

        Returns:
            str: The generated lecture content.
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt + "\n\n" + text,  # Exclude the first item (instruction) from the content
            config=types.GenerateContentConfig(
                system_instruction=instruction,  # Use the first item as the system instruction
            )
        )
        return response.text