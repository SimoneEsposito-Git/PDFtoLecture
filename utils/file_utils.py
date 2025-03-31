import os
from pathlib import Path

def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists. If it doesn't, create it.

    Args:
        directory_path (str or Path): Path to the directory.
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)

def get_file_name_without_extension(file_path):
    """
    Get the file name without its extension.

    Args:
        file_path (str or Path): Path to the file.

    Returns:
        str: File name without the extension.
    """
    return Path(file_path).stem

def get_file_extension(file_path):
    """
    Get the file extension of a file.

    Args:
        file_path (str or Path): Path to the file.

    Returns:
        str: File extension (e.g., '.pdf', '.json').
    """
    return Path(file_path).suffix

def list_files_in_directory(directory_path, extensions=None):
    """
    List all files in a directory, optionally filtering by extensions.

    Args:
        directory_path (str or Path): Path to the directory.
        extensions (list, optional): List of file extensions to filter by (e.g., ['.pdf', '.json']).

    Returns:
        list: List of file paths.
    """
    directory = Path(directory_path)
    if extensions:
        return [file for file in directory.iterdir() if file.suffix in extensions]
    return [file for file in directory.iterdir() if file.is_file()]