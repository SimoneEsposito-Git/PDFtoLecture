import logging

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