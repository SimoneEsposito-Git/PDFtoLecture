# PDF to Lecture Converter

This project converts PDF files (e.g., lecture slides) into a complete lecture with:
- **Text**: A Markdown file containing the lecture transcript.
- **Audio**: An MP3 file generated using a text-to-speech (TTS) engine.

The workflow includes:
1. Extracting text and visuals from PDFs.
2. Generating a lecture transcript using an LLM (e.g., Google GenAI).
3. Converting the transcript into audio using Kokoro ONNX-based TTS.

---

## Features

- **PDF Parsing**: Extracts text and images from PDFs.
- **Lecture Generation**: Uses an LLM to create a natural-sounding lecture transcript.
- **Text-to-Speech**: Converts the transcript into high-quality audio.
- **Modular Design**: Easily extendable for additional features or formats.

---

## Installation

### Prerequisites
- Python 3.10 
- `ffmpeg` installed and available in your system's PATH (required for audio processing).

### Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/pdf-to-lecture.git
   cd pdf-to-lecture

2. Download the TTS models
    https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
    https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
   and save them to a folder models/

3. Install uv from https://docs.astral.sh/uv/getting-started/installation

4. Run
   ```
   uv venv .venv -p 3.12
   source .venv/bin/activate
   uv pip install -U requirements.txt
   uv run -m scripts.main input/example.pdf --output output/ --visuals visuals