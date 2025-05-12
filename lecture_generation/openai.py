from openai import OpenAI

class OpenAILLMClient:
    def __init__(self, model, api_key):
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def process_text(self, prompt, text, instruction=None):
        """
        Generate lecture content using the LLM.
        Args:
            prompt (str): Text prompt to be processed by the LLM.
            instruction (str): Optional system instruction for the LLM.
        Returns:
            str: The generated lecture content.
        """
        response = self.client.responses.create(
            model=self.model,
            instructions=instruction,
            input=prompt + "\n\n" + text,
        )
        return response.output_text