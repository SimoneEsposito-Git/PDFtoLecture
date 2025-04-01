import logging
import threading
import time

class ProcessingAnimation:
    def __init__(self, description):
        self.description = description
        self.animation_chars = ['|', '/', '-', '\\']
        self.running = False
        self.thread = None
        self.start_time = None
        
    def animate(self):
        i = 0
        while self.running:
            print(f"\r{self.description} {self.animation_chars[i % len(self.animation_chars)]}", end='')
            time.sleep(0.1)
            i += 1
            
    def __enter__(self):
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self.animate)
        self.thread.daemon = True
        self.thread.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        elapsed_time = time.time() - self.start_time
        if self.thread:
            self.thread.join(0.2)
        print(f"\r{self.description} ✓ (took {elapsed_time:.2f}s)")

def configure_logging(log_file_path=None, log_level=logging.INFO):
    """
    Configure logging for the application.

    Args:
        log_file_path (str, optional): Path to the log file. If None, logs are printed to the console.
        log_level (int): Logging level (e.g., logging.INFO, logging.DEBUG).
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if log_file_path:
        logging.basicConfig(
            filename=log_file_path,
            level=log_level,
            format=log_format,
            filemode="a",
        )
    else:
        logging.basicConfig(
            level=log_level,
            format=log_format,
        )
    logging.info("Logging configured successfully.")