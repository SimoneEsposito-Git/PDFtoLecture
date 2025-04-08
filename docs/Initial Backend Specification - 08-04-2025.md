**Project: Interactive Lecture Player - Backend Requirements Specification**

**1. Overview**

This document outlines the requirements for the Backend system of the Interactive Lecture Player application. The Backend is responsible for all core processing tasks, including parsing PDF documents, generating lecture scripts using Large Language Models (LLMs), synthesizing audio using Text-to-Speech (TTS) engines, managing synchronization data (timestamps), handling interactive chat queries, managing application settings, and saving/loading lecture data in a custom format (`.lect`).

The Backend operates asynchronously to avoid blocking the Frontend PyQt GUI and communicates progress, results, and errors via the Qt Signals and Slots mechanism.

**2. System Architecture**

*   **Modular Design:** The Backend is composed of distinct Python modules with specific responsibilities (`pdf_processing`, `lecture_generation`, `tts`, `utils`, `backend`).
*   **Asynchronous Operations & PyQt Integration:** All potentially time-consuming tasks (I/O, API calls, CPU-intensive processing) must be executed in background `QThread`s. Backend worker components responsible for these tasks will be implemented as `QObject` subclasses.
*   **Communication via Signals and Slots:** The Backend worker objects will communicate results, progress, and errors back to the Frontend GUI thread by emitting Qt signals (`pyqtSignal`). The Frontend will connect these signals to its slots (methods) for UI updates.
*   **Stateless Core Logic / Stateful Orchestration:** While core LLM/TTS API calls might be stateless, the Backend orchestration layer will manage state where necessary (e.g., chat history, sequential generation progress).
*   **Configuration Driven:** LLM and TTS engine selection and configuration are managed via a central `settings.json` file accessed through the `SettingsManager`.

**3. Backend Workspace File Structure**

```
.
├── .gitignore
├── backend/                   # Main Backend orchestration and interface logic
│   ├── __init__.py
│   ├── worker.py              # Defines QObject worker classes (e.g., GenerationWorker, ChatWorker)
│   └── interface.py           # (Optional) Facade to simplify Frontend calls to worker methods
├── frontend/                  # GUI Code (PyQt - Separate)
│   └── ...
├── input/
│   └── (Example PDFs go here)
├── lecture_generation/        # Core LLM-related logic
│   ├── __init__.py            # LLM Registry/Factory
│   ├── base_llm_client.py     # Abstract base class for LLM clients
│   ├── openai_llm_client.py   # Implementation for OpenAI
│   # └── (Future LLM clients)
│   ├── script_generator.py    # Logic for generating script + transitions (Strategy 2)
│   └── chat_handler.py        # Manages chat history and context preparation
├── models/                    # ML models (e.g., local TTS/LLM)
│   └── kokoro-v1.0.onnx
├── output/                    # Default output location
│   ├── visuals/
│   └── (Generated .lect files, intermediate files if not cleaned up)
├── pdf_processing/            # PDF parsing and data extraction
│   ├── __init__.py
│   ├── ocr.py                 # OCR implementation
│   └── parsing.py             # Text, image bbox extraction, language detection
├── README.md
├── requirements.txt           # Core Backend dependencies (+ potentially shared utils)
├── settings.json              # Central configuration file
├── tts/                       # Core TTS-related logic
│   ├── __init__.py            # TTS Registry/Factory
│   ├── base_tts.py            # Abstract base class for TTS engines
│   ├── kokoro.py              # Implementation for Kokoro TTS
│   ├── openai_tts.py          # Implementation for OpenAI TTS
│   # └── (Future TTS engines)
└── utils/                     # Shared Backend utilities
    ├── __init__.py
    ├── audio_utils.py         # Audio processing (get duration, concatenate)
    ├── lecture_io.py          # Handling .lect file packaging/unpackaging
    ├── logging_utils.py       # Logging setup, animations (used by CLI)
    └── settings_manager.py    # Loading/Saving settings.json
```

**4. Core Modules Specification**

*(These define the core logic, independent of Qt, but will be called by the Qt Workers)*

*   **`pdf_processing`**:
    *   `parsing.py`:
        *   `create_json_from_pdf(pdf_path: str, use_ocr: bool = False) -> list[dict]`: Parses the PDF page-by-page. Extracts text (via direct extraction or OCR fallback), detects language (e.g., using `langdetect`), extracts image bounding boxes (`fitz.Rect` converted to `[x0,y0,x1,y1]`). Returns a list of dictionaries, one per page: `{'page_num': int, 'text': str, 'language': str, 'images': [{'bbox': list[float]}]}`.
    *   `ocr.py`:
        *   `perform_ocr(image_data_or_path, language: str | None = None) -> str`: Takes image data (e.g., from `page.get_pixmap()`) or path and performs OCR, returning extracted text. Handles language hints.
*   **`lecture_generation`**:
    *   `__init__.py`: `get_language_model(model_key: str, config: dict) -> BaseLLMClient`, `list_available_llms()`. Factory for LLM client instances.
    *   `base_llm_client.py`: Defines `BaseLLMClient` ABC with `process_text(self, text: str, **kwargs) -> str`.
    *   `openai_llm_client.py` (and others): Implementations of `BaseLLMClient`.
    *   `script_generator.py`:
        *   `generate_script_for_page(llm_client: BaseLLMClient, current_page_data: dict, previous_page_data: dict | None) -> str`: Constructs the prompt using Strategy 2 (look-behind for transitions), calls `llm_client.process_text`, and returns the cleaned script string (including transition if applicable) for the current page.
    *   `chat_handler.py`:
        *   `ChatSessionManager`: (Class) Manages conversation history for a chat session. Stores pairs of (user_query, llm_response). Implements logic for truncating history based on token limits.
        *   `prepare_chat_prompt(session_manager: ChatSessionManager, user_query: str, context_type: str, context_data: any, lecture_script: dict) -> str`: Takes the user query, context info (page number, selection, graphic info), the full lecture script (mapping page -> text), and the chat history. Constructs the final prompt string to be sent to the LLM, incorporating relevant lecture context and conversation history.
*   **`tts`**:
    *   `__init__.py`: `get_tts_engine(engine_key: str, config: dict) -> BaseTTS`, `list_available_tts_engines()`. Factory for TTS engine instances.
    *   `base_tts.py`: Defines `BaseTTS` ABC with `synthesize(self, text: str, output_path: str, **kwargs) -> None`.
    *   `kokoro.py`, `openai_tts.py` (and others): Implementations of `BaseTTS`.
*   **`utils`**:
    *   `settings_manager.py`: `SettingsManager` class to load, get, update, and save settings from `settings.json`. Handles API key resolution from environment variables. Provides `get_available_models()`.
    *   `audio_utils.py`:
        *   `get_audio_duration(file_path: str) -> float`: Returns the duration of the audio file in seconds (using `mutagen`, `soundfile`, `pydub`, etc.).
        *   `concatenate_audio(file_list: list[str], output_path: str) -> None`: Concatenates audio files in the specified order into a single output file (using `pydub` or `ffmpeg` bindings).
    *   `lecture_io.py`:
        *   `save_lecture_to_lect(output_path: str, lecture_data: dict) -> None`: Packages necessary files (e.g., `lecture.json` metadata, `script.txt`, `audio.mp3`, `timestamps.json`, `visuals.json`, potentially original PDF) into a ZIP archive named `output_path` (`.lect`). `lecture_data` contains paths/data to package.
        *   `load_lecture_from_lect(lect_path: str, extract_to_temp_dir: str) -> dict`: Unpacks a `.lect` file into a temporary directory and returns a dictionary containing paths to the unpacked components and loaded metadata/timestamp/visual data. Handles cleanup of temp dir eventually.
    *   `logging_utils.py`: Standard logging setup helpers.

**5. Backend Worker Specification (`backend/worker.py`)**

This module defines `QObject` subclasses designed to run in separate `QThread`s. They contain the slots (methods) that the Frontend calls to initiate tasks and define the signals used to communicate back.

*   **`class GenerationWorker(QObject)`**:
    *   **Signals:**
        *   `progress_update = pyqtSignal(dict)`: Emits progress dictionaries like `{'type': 'progress', 'message': str, 'current': int, 'total': int}`.
        *   `page_ready = pyqtSignal(dict)`: Emits page data dictionaries like `{'type': 'page_ready', 'page_num': int, 'start_time': float, 'end_time': float, 'total_duration_so_far': float}` as each page's audio is processed.
        *   `generation_complete = pyqtSignal(dict)`: Emits the final result dictionary on success: `{'type': 'generation_complete', 'success': True, 'data': dict}`. `data` contains paths/info for the generated lecture.
        *   `error_occurred = pyqtSignal(dict)`: Emits error details: `{'type': 'error', 'message': str}`.
    *   **Slots (Methods callable by Frontend):**
        *   `@pyqtSlot(str, str)` `def start_generation(self, pdf_path: str, output_dir: str)`: Initiates the sequential lecture generation process. Contains the main loop calling core logic modules (`parsing`, `script_generator`, `tts`, `audio_utils`), emitting signals at appropriate stages. This method runs entirely within the worker thread.
        *   `@pyqtSlot()` `def cancel_generation(self)`: (Optional) Implements logic to gracefully stop the ongoing generation loop if possible.
*   **`class ChatWorker(QObject)`**:
    *   **Signals:**
        *   `response_ready = pyqtSignal(dict)`: Emits the LLM response: `{'type': 'llm_response', 'success': True, 'text': str}`.
        *   `error_occurred = pyqtSignal(dict)`: Emits error details: `{'type': 'error', 'message': str}`.
    *   **Slots (Methods callable by Frontend):**
        *   `@pyqtSlot(str, str, object, str, dict)` `def process_query(self, user_query: str, context_type: str, context_data: any, chat_session_id: str, lecture_script_data: dict)`: Handles a single chat query. Calls `chat_handler.prepare_chat_prompt`, makes the LLM API call via the appropriate client, manages the session via `ChatSessionManager`, and emits `response_ready` or `error_occurred`.
        *   `@pyqtSlot(str)` `def reset_session(self, chat_session_id: str)`: Clears the history for the given session ID in the `ChatSessionManager`.
*   **`class FileWorker(QObject)`**: (Optional, if saving/loading is slow)
    *   **Signals:** `load_complete = pyqtSignal(dict)`, `save_complete = pyqtSignal(bool)`, `error_occurred = pyqtSignal(dict)`.
    *   **Slots:** `load_lecture(lect_path: str)`, `save_lecture(lecture_data: dict, output_path: str)`. Calls `lecture_io` functions.

**6. Backend Interface (`backend/interface.py` - Optional Facade)**

This module could provide a simpler interface layer for the Frontend, managing the creation and interaction with Worker objects and Threads.

*   `class BackendInterface(QObject)`:
    *   Manages instances of `GenerationWorker`, `ChatWorker`, etc., and their associated `QThread`s.
    *   Provides high-level methods like `request_generation(pdf_path, output_dir)` which internally finds/starts the appropriate worker and connects signals.
    *   Forwards signals from workers to potentially simplified signals defined on the `BackendInterface` itself, making FE connections cleaner.
    *   Handles thread lifecycle management (starting, stopping).

**7. Data Formats**

*   **Internal Page Data (from Parsing):** `{'page_num': int, 'text': str, 'language': str, 'images': [{'bbox': list[float]}]}`
*   **Timestamp Data:** `list[dict]`: `[{'page': int, 'start_time': float, 'end_time': float}, ...]` (0-indexed pages, times in seconds).
*   **Visuals Data:** `dict[int, list[dict]]`: `{ page_num: [{'bbox': [float, float, float, float]}, ...], ...}` (0-indexed pages).
*   **`.lect` Format:** ZIP archive containing `lecture.json` (metadata), `script.txt`, `audio.mp3` (or wav), `timestamps.json`, `visuals.json`, [Optional] `document.pdf`.
*   **Signal Payload Dictionaries:** As defined in section 5 (Worker Specification). Must contain a `'type'` key for easy identification by Frontend slots.

**8. Non-Functional Requirements**

*   **Error Handling:** Gracefully handle errors during PDF parsing, API calls (rate limits, auth errors, timeouts), TTS synthesis, file operations. Emit informative error signals.
*   **Logging:** Implement structured logging throughout the backend modules for debugging and monitoring.
*   **Configuration:** Utilize `settings.json` via `SettingsManager` for all configurable parameters (API keys, model choices, paths).
*   **Resource Management:** Ensure proper cleanup of temporary files (audio segments) and release of resources (file handles, potentially model sessions). `QThread`s should be properly quit and waited upon application exit.
*   **Threading:** Backend worker tasks must run in non-GUI `QThread`s. Worker objects must be correctly instantiated and moved to their threads. Signal emissions are the only safe way to communicate back to the GUI thread.
*   **Concurrency Safety:** Ensure shared resources (like `SettingsManager` or `ChatSessionManager` instances if accessed by multiple workers, though unlikely in this design) are handled appropriately. The signal/slot mechanism ensures safe cross-thread calls for GUI updates.

---
**Modification: Export As**
**4. Core Modules Specification**

*(No changes to `pdf_processing`, `lecture_generation`, `tts`, `utils/settings_manager`, `utils/lecture_io`, `utils/logging_utils` core logic definitions from previous spec)*

*   **`utils/audio_utils.py` (Updated):**
    *   `get_audio_duration(file_path: str) -> float`: (Existing)
    *   `concatenate_audio(file_list: list[str], output_path: str) -> None`: (Existing)
    *   **`convert_audio_format(input_path: str, output_path: str, target_format: str) -> None`**: (New) Converts audio between formats (e.g., WAV to MP3) using `pydub` or `ffmpeg`. `target_format` is e.g., 'mp3', 'wav'.
*   **`utils/video_utils.py` (New):**
    *   `create_video_from_images_and_audio(image_files: list[str], durations: list[float], audio_path: str, output_path: str, progress_callback: callable | None = None) -> None`: Creates a video file (e.g., MP4). Renders static images (`image_files`) for specified `durations`, synchronized with the `audio_path`. Uses FFmpeg (via `subprocess` or bindings). The optional `progress_callback` is called with percentage completion (0-100) if possible to parse from FFmpeg output.
    *   `render_pdf_pages_to_images(pdf_path: str, output_dir: str, resolution: int = 150) -> list[str]`: Renders all pages of a PDF to individual image files (e.g., PNG) in the specified directory using `PyMuPDF`. Returns a list of the generated image file paths in page order.

**5. Backend Worker Specification (`backend/worker.py`)**

*(Includes previous `GenerationWorker` and `ChatWorker` definitions)*

*   **`class ExportWorker(QObject)` (New):**
    *   **Signals:**
        *   `export_progress = pyqtSignal(int)`: Emits percentage complete (0-100) during video export.
        *   `export_complete = pyqtSignal(dict)`: Emits result on completion: `{'type': 'export_complete', 'success': bool, 'output_path': str | None, 'error_message': str | None}`.
    *   **Slots:**
        *   `@pyqtSlot(dict, str, str)` `def start_export(self, lecture_data: dict, export_format: str, output_path: str)`: Initiates the export process.
            *   **Args:**
                *   `lecture_data`: Dictionary containing paths/data for the loaded lecture (e.g., `{'pdf_path': str, 'audio_path': str, 'timestamp_data': list, ...}`).
                *   `export_format`: Target format ('mp3', 'wav', 'mp4', 'mov').
                *   `output_path`: Full path for the exported file chosen by the user.
            *   **Logic:**
                1.  Validate inputs (`lecture_data`, `export_format`, `output_path`).
                2.  If `export_format` is 'mp3' or 'wav':
                    *   Call `utils.audio_utils.convert_audio_format` if needed, or just copy the existing audio file. Emit `export_complete`.
                3.  If `export_format` is 'mp4' or 'mov':
                    *   Render PDF pages to temporary images using `utils.video_utils.render_pdf_pages_to_images`. Handle potential errors.
                    *   Extract page durations from `lecture_data['timestamp_data']`.
                    *   Define a progress callback function that emits the `export_progress` signal.
                    *   Call `utils.video_utils.create_video_from_images_and_audio`, passing image paths, durations, audio path, output path, and the progress callback.
                    *   Cleanup temporary image files.
                    *   Emit `export_complete`.
                4.  Emit `export_complete` with `success=False` and an error message on any failure.

**6. Backend Interface (`backend/interface.py` - Optional Facade)**

*   If using this facade, add methods like `request_export(lecture_data, export_format, output_path)` which manage an `ExportWorker` instance and its thread, connecting signals appropriately.

**7. Data Formats**

*(No changes to internal data, timestamps, visuals, `.lect` format definitions)*

*   **Signal Payload Dictionaries (Additions):**
    *   `export_progress`: Integer payload (0-100).
    *   `export_complete`: `{'type': 'export_complete', 'success': bool, 'output_path': str | None, 'error_message': str | None}`.

**8. Non-Functional Requirements**

*   **(Updated) Dependencies:** The Backend now has a potential dependency on **FFmpeg** being installed and accessible in the system's PATH (if using `subprocess`) or on Python bindings like `ffmpeg-python` or `pydub` (which often wraps FFmpeg). This needs to be documented for users/developers.
*   **(New) Resource Intensive Export:** Video export can be very CPU and memory intensive. The implementation should be mindful of this, especially regarding temporary file storage and potential long processing times.
*   (Existing requirements for Error Handling, Logging, Configuration, Threading, Concurrency Safety remain).

---

Generated with Google Gemini 2.5 Pro