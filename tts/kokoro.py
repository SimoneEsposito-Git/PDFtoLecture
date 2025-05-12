import os
import onnxruntime
from onnxruntime import InferenceSession, GraphOptimizationLevel
import soundfile as sf
import logging
import numpy as np
from kokoro_onnx import Kokoro
from tts.base_tts import BaseTTS
    
class KokoroTTS(BaseTTS):
    def __init__(self, **kwargs):
        """
        Initialize the Kokoro TTS engine with optional parameters.

        Args:
            **kwargs: Optional parameters for TTS initialization.
        """
        super().__init__(**kwargs)
        self.session = self.create_session()
        self.kokoro = Kokoro.from_session(self.session, "models/voices-v1.0.bin")
        if not self.kokoro:
            raise ValueError("Failed to initialize Kokoro TTS engine.")
        if kwargs.get("debug", False):
            print("Kokoro TTS engine initialized successfully.")
        self.debug = kwargs.get("debug", False)
        logging.getLogger("kokoro_onnx").setLevel(logging.DEBUG if self.debug else logging.WARNING)
        
    def synthesize(self, text, output_path, voice="af_sarah", speed=1.0, lang="en-us", debug=False):
        """
        Convert text to speech and save it to the output path.

        Args:
            text (str): The text to convert.
            output_path (str): Path to save the audio file.
            voice (str): Voice to use for TTS.
            speed (float): Speed of the speech.
            lang (str): Language of the text.
            debug (bool): Whether to print debug information.

        Returns:
            tuple: (samples, sample_rate) of the generated audio.
        """
        # Generate speech
        samples, sample_rate = self.kokoro.create(
            text, voice=voice, speed=speed, lang=lang
        )

        # Use float32 explicitly for better performance
        samples = np.array(samples, dtype=np.float32)

        # Write output
        sf.write(output_path, samples, sample_rate)

        if debug:
            print(f"Created audio at {output_path}")

        return samples, sample_rate

    def create_session(self, model_path="models/kokoro-v1.0.onnx", debug = False):
        """
        Create and configure an ONNX Runtime session.

        Args:
            model_path (str): Path to the ONNX model file.

        Returns:
            InferenceSession: Configured ONNX Runtime session.
        """
        providers = onnxruntime.get_available_providers()

        if debug:
            print(f"Available ONNX Runtime providers: {providers}")

        # Prioritize fastest providers
        preferred_providers = []
        if 'CUDAExecutionProvider' in providers:
            preferred_providers.append('CUDAExecutionProvider')
        elif 'DnnlExecutionProvider' in providers:
            preferred_providers.append('DnnlExecutionProvider')
        elif 'CPUExecutionProvider' in providers:
            preferred_providers.append('CPUExecutionProvider')

        if not preferred_providers:
            preferred_providers = providers

        sess_options = onnxruntime.SessionOptions()

        # Set optimization level to maximum
        sess_options.graph_optimization_level = GraphOptimizationLevel.ORT_ENABLE_ALL

        # Optimize threading based on CPU
        cpu_count = os.cpu_count()
        if debug:
            print(f"Setting threads to CPU cores count: {cpu_count}")
        sess_options.intra_op_num_threads = cpu_count
        # sess_options.inter_op_num_threads = 1

        # Enable memory optimizations
        sess_options.enable_mem_pattern = True
        sess_options.enable_cpu_mem_arena = True

        # Create and return the session
        session = InferenceSession(
            model_path, providers=preferred_providers, sess_options=sess_options
        )
        return session