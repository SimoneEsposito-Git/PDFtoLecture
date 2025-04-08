from .session import create_session
from .kokoro import tts, KokoroTTS
from .openai import OpenAITTS
from .base import TTS

__all__ = [
    "create_session",
    "tts",
    "TTS"
]

TTS_REGISTRY = {
    "openai": OpenAITTS,
    "kokoro": KokoroTTS,
}

def get_tts_engine(engine_name, **kwargs):
    if engine_name in TTS_REGISTRY:
        return TTS_REGISTRY[engine_name](**kwargs)
    raise ValueError(f"TTS engine '{engine_name}' not found.")