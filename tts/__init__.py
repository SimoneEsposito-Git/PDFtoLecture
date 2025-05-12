from .kokoro import KokoroTTS
from .openai import OpenAITTS
from .base_tts import BaseTTS

__all__ = [
    "OpenAITTS",
    "KokoroTTS",
    "BaseTTS"
]

TTS_REGISTRY = {
    "openai": OpenAITTS,
    "kokoro": KokoroTTS,
}

def get_tts_engine(engine_name, **kwargs):
    if engine_name in TTS_REGISTRY:
        return TTS_REGISTRY[engine_name](**kwargs)
    raise ValueError(f"TTS engine '{engine_name}' not found.")