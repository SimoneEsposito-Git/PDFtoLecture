**Project: Interactive Lecture Player - Frontend Requirements Specification (PyQt)**

**1. Overview**

This document outlines the requirements for the Frontend PyQt GUI of the Interactive Lecture Player application. The application transforms static PDF lecture slides into an interactive experience combining the original PDF visuals with synchronized audio narration, clickable elements, and an integrated LLM chat for Q&A. The Frontend provides the user interface for importing PDFs, controlling playback, interacting with content, managing settings, and saving/loading lecture sessions, interacting with the Backend via Qt's Signals and Slots mechanism.

**2. Target Users**

Students, educators, or anyone wishing to review lecture material in a more engaging format than a static PDF.

**3. General GUI Requirements**

*   **Platform:** Cross-platform desktop application (Windows, macOS, Linux) built using PyQt6 (or PySide6).
*   **Responsiveness:** The UI must remain fully responsive during all Backend operations. Interaction with the Backend must occur via asynchronous calls to worker slots running in separate `QThread`s. GUI updates happen in response to signals emitted by Backend workers.
*   **Error Handling:** Display user-friendly error messages (e.g., using `QMessageBox` or status bar updates) in response to `error_occurred` signals from the Backend.
*   **Progress Indication:** Provide clear visual feedback (e.g., updates to a `QStatusBar`, potentially a non-modal `QProgressDialog`) in response to `progress_update` and `page_ready` signals from the Backend during lecture generation. Provide visual cues (e.g., spinner icon, disabled send button) during chat queries.
*   **Theme:** Support Light and Dark themes (configurable in Settings, potentially using stylesheets or a library like `qt-material`).

**4. Functional Requirements**

**4.1 File Handling & Lecture Management (Interactions with Backend Slots)**

*   **4.1.1 PDF Import (Menu):**
    *   Provide a `QAction` in the `File` menu: "Import PDF...".
    *   Action: Opens a `QFileDialog::getOpenFileName` filtered for PDF files (`*.pdf`).
    *   On selection: Calls the Backend worker's `start_generation` slot, passing the selected `pdf_path` and a designated output directory path (e.g., a subdirectory in `output/`).
*   **4.1.2 PDF Import (Drag & Drop):**
    *   Implement `dragEnterEvent` and `dropEvent` on the main window or a designated widget to accept PDF files.
    *   Action: On dropping a valid PDF file, call the Backend worker's `start_generation` slot similarly to 4.1.1.
    *   Visual Feedback: Change widget appearance during drag-over to indicate acceptance/rejection.
*   **4.1.3 Open Lecture:**
    *   Provide a `QAction`: "Open Lecture...".
    *   Action: Opens `QFileDialog::getOpenFileName` filtered for the custom lecture format (`*.lect`).
    *   On selection: Call the Backend (potentially `FileWorker`) `load_lecture` slot/method. The returned data (or data from a `load_complete` signal) is used to populate the playback view (See 4.3).
*   **4.1.4 Save Lecture:**
    *   Provide a `QAction`: "Save".
    *   Action: Check if a current save path exists. If yes, call Backend `save_lecture` slot/method with current lecture data and path. If no, trigger "Save As".
*   **4.1.5 Save Lecture As:**
    *   Provide a `QAction`: "Save Lecture As...".
    *   Action: Opens `QFileDialog::getSaveFileName` to specify a `.lect` filename. Call Backend `save_lecture` slot/method with current lecture data and the chosen path. Store the path for future "Save" actions.

**4.2 Lecture Generation Process (Responding to Backend Signals)**

*   **4.2.1 Triggering:** Initiated by user actions (4.1.1, 4.1.2) calling the Backend worker's `start_generation` slot.
*   **4.2.2 Progress Handling:** Implement slots connected to the `GenerationWorker`'s signals:
    *   **`on_progress_update(progress_dict: dict)`:** Updates UI elements like `QStatusBar` message or a `QProgressBar` based on `progress_dict['message']`, `progress_dict['current']`, `progress_dict['total']`. Disable relevant UI (import, playback controls).
    *   **`on_page_ready(page_data: dict)`:** Updates the seek bar (See 4.3.2) to mark the range up to `page_data['page_num']` as available and potentially update the total duration display using `page_data['total_duration_so_far']`. Enable playback controls if Page 0 is ready.
    *   **`on_generation_complete(result_dict: dict)`:** Handles successful completion. If `result_dict['success']` is True, load the full lecture data from `result_dict['data']` into the playback view. Re-enable all relevant UI elements. Update status bar to "Ready".
    *   **`on_error_occurred(error_dict: dict)`:** Handles failures. Display `error_dict['message']` using `QMessageBox::warning`. Re-enable relevant UI elements. Update status bar to "Generation Failed".
*   **4.2.3 Cancellation:** Provide a "Cancel" button during generation (e.g., on a progress dialog). Clicking it calls the Backend worker's `cancel_generation` slot (if implemented).

**4.3 Lecture Playback Interface**

*   **4.3.1 Main View (PDF Display):**
    *   Use a suitable Qt widget for displaying PDF pages (e.g., integrating with `PyMuPDF` for rendering pages onto a `QPixmap` shown in a `QLabel` or `QGraphicsView`, or potentially using `QPdfDocument` if available and suitable).
    *   Implement zoom (e.g., using `QGraphicsView::scale` or re-rendering at higher resolution) and panning (e.g., `QScrollArea` or `QGraphicsView` scrollbars).
*   **4.3.2 Status/Seek Bar:**
    *   Implement a custom `QWidget` or potentially subclass `QSlider` or `QProgressBar`.
    *   Visually divide the bar based on page timestamp data (`start_time`, `end_time`) received from the Backend. Segment widths must be proportional to duration. Use `QPainter` for custom drawing.
    *   Maintain a separate indicator for the current audio playback position (updated by a timer connected to the media player).
    *   Implement `mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent` to handle seeking clicks.
        *   On click, determine the target time and page segment.
        *   Call the audio player's seek function based on the "Always Sync" setting (see below).
        *   If not "Always Sync", update the Resync button state (4.3.4).
    *   Use `QToolTip` to show page number on hover.
    *   Visually differentiate the "buffered" / available range based on `page_ready` signals. Disallow seeking beyond the available range.
*   **4.3.3 Playback Controls:**
    *   Use `QPushButton` with icons (e.g., from `QStyle` standard icons or custom assets).
    *   Connect buttons to slots controlling a media player object (e.g., `QMediaPlayer`):
        *   **Play/Pause:** Call `player.play()` / `player.pause()`. Update button icon based on `player.state()`.
        *   **Next/Previous Slide:** Increment/decrement the currently displayed page index. Render the new page. If "Always Sync" is ON, calculate the start time for the new page using the timestamp data and call `player.setPosition()`. If OFF, update Resync button state.
*   **4.3.4 Synchronization Indicator & Control:**
    *   **Resync Button (`QPushButton`):**
        *   Enabled/Visible only when "Always Sync" is OFF and the player's current position (`player.position()`) corresponds to a different page number (derived from timestamp data) than the currently displayed page index.
        *   May change appearance (e.g., color via stylesheet) when desynchronized.
        *   Connected slot: Finds the page number corresponding to `player.position()`, updates the displayed page index, re-renders the PDF view, and disables/hides the Resync button.
*   **4.3.5 Fullscreen Button (`QPushButton`):** Calls `QMainWindow::showFullScreen()` / `QMainWindow::showNormal()`.
*   **4.3.6 Slide Navigator:**
    *   Use a `QListWidget` or `QGraphicsView` in a `QDockWidget` or overlay panel.
    *   Display `QPixmap` thumbnails of PDF pages (can be generated efficiently by `PyMuPDF`).
    *   Highlight the item corresponding to the currently displayed page index.
    *   Connect `itemClicked` or similar signal to a slot that updates the displayed page index, re-renders the PDF, and potentially seeks audio based on the "Always Sync" setting.
*   **4.3.7 Interactive Graphics:**
    *   Requires the PDF rendering widget to:
        *   Receive image bounding box data (`visuals.json` content) from the Backend.
        *   Detect mouse hovers and clicks within these bounding box areas mapped to widget coordinates.
        *   On hover: Draw a subtle highlight overlay using `QPainter`.
        *   On single click: Execute the pause -> seek page start -> resume logic by calling appropriate slots/methods controlling the audio player (`QMediaPlayer`).

**4.4 LLM Chat Interface**

*   **4.4.1 UI Components:**
    *   Chat History Area: `QTextBrowser` or `QListWidget` styled to look like chat. Must support displaying formatted text (user vs. LLM).
    *   Input Text Box: `QTextEdit` for multi-line input.
    *   Send Button: `QPushButton`.
    *   (Optional) Context Buttons: `QPushButton`s.
*   **4.4.2 Interaction:**
    *   Capture text from `QTextEdit`.
    *   Capture selected text from the PDF view widget (if any).
    *   On Send button click (or Enter press in `QTextEdit`):
        1.  Disable Send button and input `QTextEdit`. Show a "Thinking..." status. Append user query to Chat History Area.
        2.  Determine context (`page`, `selection`, etc.) and gather `context_data` (page number, selected text).
        3.  Call the `ChatWorker`'s `process_query` slot with query, context, session ID, and lecture script data.
    *   Implement slots connected to `ChatWorker` signals:
        *   **`on_llm_response(response_dict: dict)`:** If `response_dict['success']`, append `response_dict['text']` to Chat History Area. Re-enable Send/Input. Clear "Thinking..." status.
        *   **`on_chat_error(error_dict: dict)`:** Append `error_dict['message']` to Chat History Area (formatted as an error). Re-enable Send/Input. Clear "Thinking..." status.
*   **4.4.3 Context Management:**
    *   Provide a "Reset Chat" button/menu item connected to a slot that calls the `ChatWorker`'s `reset_session` slot.
    *   FE sends context type/data with each query.

**4.5 Menu Bar & Settings**

*   **4.5.1 Menu Structure (`QMenuBar`, `QMenu`, `QAction`):** Structure as defined previously. Connect `QAction` triggers to appropriate slots.
*   **4.5.2 Settings Dialog (`QDialog`):**
    *   Use `QTabWidget` for organization (General, Models, Appearance).
    *   **Models Tab:**
        *   Use `QComboBox` for LLM/TTS selection. Populate items using data retrieved synchronously from `utils.settings_manager.get_available_models()` (or via a dedicated Backend call if preferred).
        *   Use `QLineEdit` (with `EchoMode.Password`), `QComboBox`, etc., for model config options. Dynamically show/hide options based on selected model.
        *   Load initial values using `utils.settings_manager.get_settings()`.
    *   **General Tab:**
        *   `QComboBox` for Preferred Language.
        *   `QCheckBox` for "Always Sync Playback".
    *   **Appearance Tab:**
        *   `QComboBox` or `QRadioButton`s for Theme.
    *   **Actions:** "Save"/"Apply" (`QPushButton` connected to `accept()` slot), "Cancel" (`QPushButton` connected to `reject()` slot). Override `accept()` to call `utils.settings_manager.save_settings()` with the dialog's current values before closing.

**5. Backend Communication**

*   The Frontend instantiates the necessary Backend worker objects (`GenerationWorker`, `ChatWorker`, etc.) and moves them to separate `QThread`s managed by the Frontend application.
*   Connections are established between Frontend widget signals (e.g., button clicks) and worker slots (`@pyqtSlot`).
*   Connections are established between worker signals (`pyqtSignal`) and Frontend slots (`@pyqtSlot`) for receiving progress, results, and errors. All Frontend slots connected to worker signals **must** only update GUI elements, as Qt ensures they run in the main GUI thread.

**6. Data Formats**

*   The Frontend primarily interacts with data packaged in Python dictionaries sent via Qt Signals. These dictionaries should follow the structures defined in the Backend specification (e.g., keys like `'type'`, `'page_num'`, `'message'`, `'success'`, `'data'`).
*   The Frontend loads data needed for playback (audio path, timestamp list, visuals data) from the dictionary received via the `generation_complete` or `load_complete` signal.

---

Generated with Google Gemini 2.5 Pro