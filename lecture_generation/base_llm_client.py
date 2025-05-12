class BaseLLMClient:
    """
    A wrapper for interacting with the LLM (e.g., Google GenAI).
    """
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
    
    def process_text(self, prompt, text, instructions = None) -> str:
        """
        Generate lecture content using the LLM.
    
        Args:
            prompt (str): Text prompt to be processed by the LLM.
    
        Returns:
            str: The generated lecture content.
        """
        raise NotImplementedError("Subclasses should implement this method.")