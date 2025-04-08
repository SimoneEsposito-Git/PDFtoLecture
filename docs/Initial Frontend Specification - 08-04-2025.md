**Project: Interactive Lecture Player - Front-End Requirements Specification**

**1. Overview**

This document outlines the requirements for the Front-End (GUI) of the Interactive Lecture Player application. The application transforms static PDF lecture slides into an interactive experience combining the original PDF visuals with synchronized audio narration, clickable elements, and an integrated LLM chat for Q&A. The Front-End will provide the user interface for importing PDFs, controlling playback, interacting with content, managing settings, and saving/loading lecture sessions.

**2. Target Users**

Students, educators, or anyone wishing to review lecture material in a more engaging format than a static PDF.

**3. General GUI Requirements**

*   **Platform:** Cross-platform (Specify target OS: Windows, macOS, Linux - this influences GUI framework choice like PyQt, Kivy, Electron, etc.).
*   **Responsiveness:** The UI should remain responsive during potentially long-running Back-End operations (lecture generation, LLM queries) using asynchronous calls and appropriate progress indicators.
*   **Error Handling:** Display user-friendly error messages for Back-End failures (e.g., PDF parsing error, API key invalid, TTS failure, file not found).
*   **Progress Indication:** Provide clear visual feedback (e.g., progress bars, spinners, status messages) during lecture generation and LLM queries.
*   **Theme:** Support Light and Dark themes (configurable in Settings).

**4. Functional Requirements**

**4.1 File Handling & Lecture Management**

*   **4.1.1 PDF Import (Menu):**
    *   Provide a menu item: `File > Import PDF`.
    *   Action: Opens a native file dialog filtered for PDF files (`.pdf`).
    *   On selection: Trigger Back-End lecture generation process (See 4.2) for the selected PDF.
*   **4.1.2 PDF Import (Drag & Drop):**
    *   Designate a main area or the entire window as a drop target for PDF files.
    *   Action: On dropping a valid PDF file, trigger Back-End lecture generation (See 4.2).
    *   Visual Feedback: Indicate when a dragged file is over the target and whether it's a valid type.
*   **4.1.3 Open Lecture:**
    *   Provide a menu item: `File > Open Lecture...`.
    *   Action: Opens a native file dialog filtered for the custom lecture format (`.lect`).
    *   On selection: Trigger Back-End function to load the lecture data. The FE then populates the playback view (See 4.3) with the loaded data.
*   **4.1.4 Save Lecture:**
    *   Provide a menu item: `File > Save`.
    *   Action: If the current lecture has been saved before, trigger Back-End function to overwrite the existing `.lect` file with the current state (if any state needs saving, e.g., bookmarks, last position - TBD). If not saved before, behave like "Save As".
*   **4.1.5 Save Lecture As:**
    *   Provide a menu item: `File > Save Lecture As...`.
    *   Action: Opens a native file dialog to specify a filename and location for saving the current lecture in the `.lect` format. Trigger Back-End function to save the lecture data.

**4.2 Lecture Generation Process (FE Perspective)**

*   **4.2.1 Triggering:** Initiated by PDF Import (4.1.1, 4.1.2).
*   **4.2.2 Progress Display:**
    *   Show a clear, non-blocking progress indicator (e.g., status bar message, modal dialog with progress bar/spinner). Examples: "Processing PDF...", "Generating script...", "Synthesizing audio page 5/20...".
    *   Disable relevant UI elements (e.g., import options, playback controls) during generation. Allow cancellation if feasible via Back-End support.
*   **4.2.3 Completion:** On successful generation, the Back-End should notify the FE with the necessary data to load the lecture into the playback view (See 4.3).
*   **4.2.4 Failure:** On failure, display a user-friendly error message describing the issue (e.g., "Failed to extract text from PDF", "TTS service unavailable"). Re-enable UI elements.

**4.3 Lecture Playback Interface**

*   **4.3.1 Main View:**
    *   Display the current PDF page clearly. Rendering must be accurate.
    *   Support zooming and panning of the PDF view.
*   **4.3.2 Status/Seek Bar:**
    *   Located typically below the main view.
    *   Visually represent the entire lecture audio duration.
    *   Divide the bar into segments corresponding to PDF pages. The *width* of each segment should be proportional to the duration of audio associated with that page.
    *   Display current audio playback time marker.
    *   On hover over a segment: Show a tooltip with the Page number (e.g., "Page 5").
    *   On click:
        *   If "Always Sync" (See 5.1.4) is OFF: Seek audio playback to the corresponding time. *Do not* change the displayed PDF page immediately. Update the Resync button state (See 4.3.5).
        *   If "Always Sync" is ON: Seek audio playback *and* change the displayed PDF page to the one corresponding to the clicked segment/time.
*   **4.3.3 Playback Controls:**
    *   **Play/Pause Button:** Toggles audio playback. Icon should change accordingly (e.g., Play icon, Pause icon).
    *   **Next Slide Button:** Advances the displayed PDF page to the next page. If "Always Sync" is OFF, this desynchronizes audio playback (audio continues from its current position). Update Resync button state. If "Always Sync" is ON, seeks audio to the start of the next page's segment *and* changes the page.
    *   **Previous Slide Button:** Moves the displayed PDF page to the previous page. Behavior regarding sync mirrors the Next Slide button.
*   **4.3.4 Synchronization Indicator & Control:**
    *   **Resync Button:**
        *   Enabled only when playback is desynchronized (i.e., current audio time corresponds to a different page than the one displayed) AND "Always Sync" is OFF.
        *   Visually indicate desynchronization (e.g., button changes color, an icon appears).
        *   Action: When clicked, find the PDF page corresponding to the *current audio playback time* and display that page. The button becomes disabled/normal color again.
*   **4.3.5 Fullscreen Button:** Toggles the application window into/out of fullscreen mode, maximizing the content viewing area.
*   **4.3.6 Slide Navigator:**
    *   Display thumbnails of all PDF pages (e.g., in a scrollable sidebar or an auto-hiding overlay).
    *   Highlight the currently displayed page thumbnail.
    *   On click of a thumbnail: Display the corresponding PDF page. Behavior regarding sync mirrors the Next/Previous Slide buttons (desyncs if "Always Sync" is OFF).
*   **4.3.7 Interactive Graphics:**
    *   Graphics detected by the Back-End should have a subtle visual indicator on hover within the PDF view (e.g., border highlight).
    *   **On single click:**
        1.  Pause the main lecture audio playback.
        2.  Briefly highlight the clicked graphic more prominently.
        3.  Seek audio playback to the *start timestamp* of the *page* the graphic is on.
        4.  Resume audio playback from that page's start.
        5.  (This keeps the user on the relevant page audio).
    *   (Note: Ensure this interaction feels intuitive. User feedback may lead to refinements like double-click actions if needed later).

**4.4 LLM Chat Interface**

*   **4.4.1 UI Components:**
    *   Chat History Area: Scrollable area displaying the conversation (user prompts and LLM responses). Format clearly.
    *   Input Text Box: Multi-line text area for users to type questions.
    *   Send Button: Triggers sending the query to the LLM via the Back-End.
    *   (Optional) Context Buttons: Buttons like "Ask about Current Slide" or "Use Selection" could pre-fill context hints.
*   **4.4.2 Interaction:**
    *   User types a question in the input box.
    *   User can optionally select text within the PDF view *before* sending the query. The FE should capture this selection.
    *   User clicks Send (or presses Enter).
    *   FE sends the query text, context type, and relevant context data (page number, selected text) to the Back-End.
    *   Display a "Thinking..." or similar indicator while waiting for the Back-End response. Disable input/send button.
    *   On receiving the response from the Back-End, display it in the Chat History area. Re-enable input/send button.
    *   Handle potential errors from the LLM (e.g., API error, no response) by displaying a message in the chat history.
*   **4.4.3 Context Management:** The FE primarily tells the Back-End *what* the context is (whole lecture, current page, text selection). The Back-End manages the actual context details/session. The FE may need to provide options like "Reset Chat Session" which triggers a corresponding Back-End call.

**4.5 Menu Bar & Settings**

*   **4.5.1 Menu Structure:**
    *   `File`: Import PDF, Open Lecture, Save, Save Lecture As..., Exit
    *   `Edit`: (Optional: Copy text from PDF/Chat)
    *   `View`: Toggle Slide Navigator, Fullscreen, Theme (Light/Dark)
    *   `Settings`: Open Settings Dialog
    *   `Help`: About, Check for Updates (Optional)
*   **4.5.2 Settings Dialog:**
    *   Open via `Settings` menu. Should be a modal window.
    *   Organize settings logically (e.g., tabs for General, Models, Appearance).
    *   **Models Tab:**
        *   LLM Selection: Dropdown populated with available LLMs (display names) from Back-End.
        *   TTS Selection: Dropdown populated with available TTS engines (display names) from Back-End.
        *   Model Configuration: Display configuration options relevant to the *selected* LLM and TTS engines (e.g., API key input field - show as password, voice selection dropdown for TTS). Load current values from Back-End.
    *   **General Tab:**
        *   Preferred Language: Dropdown (e.g., English, German, French, "Auto-Detect"). Selection passed to Back-End for generation/chat.
        *   "Always Sync Playback" Checkbox: Controls the behavior of Next/Prev/Seek actions (See 4.3).
    *   **Appearance Tab:**
        *   Theme Selection: Radio buttons or dropdown for "Light", "Dark", "System Default".
    *   **Actions:** "Save"/"Apply" button to trigger Back-End saving of settings. "Cancel" button to discard changes. Load current settings when the dialog opens.

**5. Back-End Interface Specification (Functions FE needs to call)**

*(Note: Function signatures use Python type hints for clarity. Actual implementation might use different mechanisms like signals/slots, callbacks, or APIs depending on FE/BE communication method. Asynchronous operations are crucial where noted.)*

*   **Lecture Generation & Management:**
    *   `start_lecture_generation(pdf_path: str) -> None`: (Async) Initiates the PDF processing and lecture generation. Should provide progress updates (e.g., via callbacks/signals) like `on_generation_progress(stage: str, current: int, total: int)` and a completion signal `on_generation_complete(success: bool, result_data: dict | None, error_message: str | None)`. `result_data` contains paths or data needed to load the lecture.
    *   `load_lecture(lecture_path: str) -> dict`: Loads data from a `.lect` file. Returns a dictionary containing PDF reference, audio path, timestamp data, image bounding boxes, etc., needed by the FE.
    *   `save_lecture(lecture_data_to_save: dict, output_path: str) -> bool`: Saves the current lecture state into a `.lect` file. Returns success status.
    *   `cancel_generation() -> None`: (Optional, Async) Attempts to cancel an ongoing lecture generation process.
*   **Settings Management:**
    *   `get_settings() -> dict`: Returns the current application settings (selected models, configs, theme, language, etc.).
    *   `save_settings(settings_data: dict) -> bool`: Saves the provided settings dictionary to persistent storage. Returns success status.
    *   `get_available_models(model_type: str) -> dict[str, str]`: Returns available models ('llm' or 'tts'). Input `model_type`, returns `{key: display_name}`.
*   **LLM Interaction:**
    *   `query_llm(query: str, context_type: str, context_data: str | int | None) -> None`: (Async) Sends a query to the LLM. `context_type` could be 'lecture', 'page', 'selection'. `context_data` could be page number or selected text. Should provide the response via a callback/signal `on_llm_response(success: bool, response_text: str | None, error_message: str | None)`.
    *   `reset_chat_session() -> None`: Tells the Back-End to clear the current LLM conversation history/context.
*   **Data Retrieval (Needed for Playback):**
    *   (These might be part of the data returned by `load_lecture` or `on_generation_complete`)
    *   `get_pdf_document()`: Returns a reference/path to the PDF file for display.
    *   `get_audio_file_path() -> str`: Returns the path to the main lecture audio file.
    *   `get_page_timestamps() -> list[dict]`: Returns timestamp data, e.g., `[{'page': 0, 'start_time': 0.0, 'end_time': 15.2}, {'page': 1, 'start_time': 15.2, 'end_time': 45.5}, ...]`.
    *   `get_image_bboxes() -> dict[int, list[dict]]`: Returns bounding boxes for interactive graphics, e.g., `{0: [{'bbox': [x0, y0, x1, y1]}, ...], 1: [...]}` where page numbers are keys.

**6. Data Formats (FE <-> BE)**

*   **`.lect` File Format (Conceptual):**
    *   A ZIP archive renamed to `.lect`.
    *   Contains:
        *   `lecture.json`: Metadata (original PDF name, generation settings, language).
        *   `script.txt`: The full text script generated by the LLM.
        *   `audio.mp3` (or `.wav`): The synthesized lecture audio.
        *   `timestamps.json`: Data mapping audio time to pages (structure as in 5. Back-End Interface).
        *   `visuals.json`: Image bounding box data (structure as in 5. Back-End Interface).
        *   `document.pdf` (Optional): Embed the original PDF for portability.
*   **Timestamp Data:** List of dictionaries: `[{'page': int, 'start_time': float, 'end_time': float}, ...]`. Page numbers are 0-indexed. Times are in seconds.
*   **Image Bounding Box Data:** Dictionary where keys are 0-indexed page numbers, and values are lists of dictionaries: `{ page_num: [{'bbox': [float, float, float, float]}, ...], ...}`. Bbox coordinates relate to the PDF page dimensions.

---

**Modification: Export As**

**4. Functional Requirements**

**4.1 File Handling & Lecture Management (Interactions with Backend Slots)**

*   (4.1.1 - 4.1.5 remain the same as previous FE spec: Import PDF, Drag & Drop, Open, Save, Save As)
*   **4.1.6 Export Lecture As (New):**
    *   Provide a `QAction` in the `File` menu: "Export Lecture As...". Enable only when a lecture is loaded.
    *   Action:
        1.  Opens a `QFileDialog::getSaveFileName` dialog.
        2.  Set appropriate name filters for supported export formats (e.g., "Video Files (*.mp4 *.mov);;Audio Files (*.mp3 *.wav)").
        3.  Retrieve the chosen filename/path and the selected filter (which determines the format).
        4.  Gather necessary data about the currently loaded lecture (e.g., paths to PDF, audio, timestamp data stored in the main window/controller).
        5.  Call the Backend `ExportWorker`'s `start_export` slot, passing the lecture data, selected format string (e.g., 'mp4', 'mp3'), and output path.
        6.  Initiate progress display (See 4.6).

**4.2 Lecture Generation Process (Responding to Backend Signals)**

*(Remains the same as previous FE spec - Handles `progress_update`, `page_ready`, `generation_complete`, `error_occurred` signals from `GenerationWorker`)*

**4.3 Lecture Playback Interface**

*(Remains the same as previous FE spec - Handles PDF display, seek bar, playback controls, sync, fullscreen, slide navigator, interactive graphics)*

**4.4 LLM Chat Interface**

*(Remains the same as previous FE spec - Handles chat UI, interaction, context management, signals from `ChatWorker`)*

**4.5 Menu Bar & Settings**

*   **4.5.1 Menu Structure:**
    *   `File`: Import PDF, Open Lecture, Save, Save Lecture As..., **Export Lecture As... (New)**, Exit
    *   (Other menus Edit, View, Settings, Help remain the same)
*   **4.5.2 Settings Dialog:** *(Remains the same as previous FE spec)*

**4.6 Lecture Export Process (FE Perspective - New Section)**

*   **4.6.1 Triggering:** Initiated by user action (4.1.6) calling the Backend `ExportWorker`'s `start_export` slot.
*   **4.6.2 Progress Handling:** Implement slots connected to the `ExportWorker`'s signals:
    *   **`on_export_progress(percentage: int)`:** Updates a progress indicator dedicated to the export process (e.g., a `QProgressDialog` shown modally or updates in the `QStatusBar`). Display percentage. Disable relevant UI (Export menu item, potentially main controls).
    *   **`on_export_complete(result_dict: dict)`:** Handles export completion.
        *   If `result_dict['success']` is True: Show a success message (e.g., `QMessageBox::information` or status bar update like "Export successful: [output_path]"). Close the progress indicator. Re-enable UI.
        *   If `result_dict['success']` is False: Show an error message using `QMessageBox::warning` with `result_dict['error_message']`. Close the progress indicator. Re-enable UI.
*   **4.6.3 Cancellation:** (Optional) If the Backend `ExportWorker` supports cancellation, provide a "Cancel" button on the progress indicator that calls the corresponding worker slot.

**5. Backend Communication**

*   The Frontend instantiates Backend worker objects (`GenerationWorker`, `ChatWorker`, **`ExportWorker`**) and moves them to separate `QThread`s.
*   Connections are established between Frontend widget signals (e.g., `QAction::triggered`) and worker slots (`@pyqtSlot`).
*   Connections are established between worker signals (`pyqtSignal` like `generation_complete`, `response_ready`, **`export_complete`**) and Frontend slots (`@pyqtSlot`) for receiving results and errors.

**6. Data Formats**

*(No changes needed from previous FE spec regarding how data is received/handled via signals)*

---

Generated with Google Gemini 2.5 Pro
