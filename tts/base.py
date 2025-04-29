from abc import ABC, abstractmethod

class BaseTTS(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        """
        Initialize the TTS engine with optional parameters.
        """
        pass
    
    @abstractmethod
    def synthesize(self, text, output_path, **kwargs):
        """
        Convert text to speech and save it to the output path.

        Args:
            text (str): The text to convert.
            output_path (str): Path to save the audio file.
        """
        pass