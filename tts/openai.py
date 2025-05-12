from openai import OpenAI
from tts.base_tts import BaseTTS

class OpenAITTS(BaseTTS):
    def __init__(self, api_key=None, model="gpt-3.5-turbo", temperature=0.7):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        # self.client = OpenAI(api_key=self.api_key)

    def synthesize(self, text, output_path, voice="alloy", instructions="Calm, Professional and Engaging"):
        """
        Convert text to speech and save it to the output path.
        Args:
            text (str): The text to convert.
            output_path (str): Path to save the audio file.
            voice (str): Voice to use for TTS.
            instructions (str): Instructions for the TTS model.
        """
        # Ensure the output directory exists
        import os
       
        output_dir = os.path.dirname(output_path)
        file_name = os.path.basename(output_path).split(".")[0]
        
        os.makedirs(file_name, exist_ok=True)
        
        chunks = text.split("\n")
        for i, chunk in enumerate(chunks):
            self.client = OpenAI(api_key=self.api_key)
            # output path parent directory
            
            with self.client.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice=voice,
                input=chunk,
                instructions=instructions,
            ) as response:
                response.stream_to_file(f"{output_dir}/{file_name}/chunk_{i}.mp3")
        
        # Combine the audio files into one
        from pydub import AudioSegment
        combined = AudioSegment.empty()
        for i in range(len(chunks)):
            audio = AudioSegment.from_file(f"{output_dir}/{file_name}_{i}.mp3")
            combined += audio
        combined.export(output_path, format="mp3")
        