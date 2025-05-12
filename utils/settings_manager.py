# utils/settings_manager.py

import json
import os
import logging
import copy # Needed for deep merging defaults

logger = logging.getLogger(__name__)

# Define the default structure and values for settings.json
# This serves as the template if the file doesn't exist
# and helps ensure all necessary keys are present after loading.
DEFAULT_SETTINGS = {
  "selected_llm": "openai_gpt3.5", # Default selection
  "selected_tts": "kokoro",       # Default selection
  "general": {                    # New section for general settings
      "preferred_language": "en", # Default language ('auto' could be an option)
      "always_sync_playback": False,
      "theme": "system"           # Options: system, light, dark
  },
  "llm_options": {
    "openai_gpt3.5": {
      "display_name": "OpenAI GPT-3.5 Turbo",
      "api_key_env": "OPENAI_API_KEY",
      "model_name": "gpt-3.5-turbo",
      "max_tokens": 1500
    },
    "openai_gpt4o": {
      "display_name": "OpenAI GPT-4o",
      "api_key_env": "OPENAI_API_KEY",
      "model_name": "gpt-4o",
      "max_tokens": 2000
    }
    # Add configurations for other potential LLMs here
  },
  "tts_options": {
    "openai": {
      "display_name": "OpenAI TTS",
      "api_key_env": "OPENAI_API_KEY",
      "default_voice": "alloy",
      "default_speed": 1.0,
      "model": "tts-1"
    },
    "kokoro": {
      "display_name": "Kokoro TTS (Local)",
      "model_path": "models/kokoro-v1.0.onnx" # Path relative to project root assumed
      # Add other Kokoro specific configurations here if any
    }
    # Add configurations for other potential TTS engines here
  }
}

class SettingsManager:
    """
    Manages loading, saving, and accessing application settings from a JSON file.

    Handles default settings creation, API key resolution from environment variables,
    and relative path resolution.
    """
    def __init__(self, settings_path='settings.json', project_root=None):
        """
        Initializes the SettingsManager.

        Args:
            settings_path (str): Path to the settings JSON file.
            project_root (str, optional): The absolute path to the project's root
                                          directory. If None, it's inferred from
                                          the settings file's location. Used for
                                          resolving relative paths.
        """
        self.settings_path = os.path.abspath(settings_path)
        if project_root:
            self.project_root = os.path.abspath(project_root)
        else:
            # Infer project root as the directory containing the settings file
            self.project_root = os.path.dirname(self.settings_path)
        logger.info(f"SettingsManager initialized. File: '{self.settings_path}', Project Root: '{self.project_root}'")

    def _deep_merge_dicts(self, source, defaults):
        """Recursively merges default values into the source dict for missing keys."""
        result = copy.deepcopy(source)
        for key, value in defaults.items():
            if isinstance(value, dict):
                # Get node or create one
                node = result.setdefault(key, {})
                if isinstance(node, dict):
                    self._deep_merge_dicts(node, value)
                # If source value is not a dict and default is, overwrite (or handle error)
                # For simplicity here, we assume structure alignment or defaults win
            elif key not in result:
                result[key] = value
        return result

    def load_settings(self):
        """
        Loads settings from the JSON file.

        If the file doesn't exist, it creates one with default settings.
        If the file is corrupt, logs an error and returns defaults.
        Merges loaded settings with defaults to ensure all keys are present.

        Returns:
            dict: The loaded and potentially merged settings.
        """
        if not os.path.exists(self.settings_path):
            logger.warning(f"Settings file not found at '{self.settings_path}'. Creating with defaults.")
            try:
                self.save_settings(DEFAULT_SETTINGS) # Save the defaults first
                return copy.deepcopy(DEFAULT_SETTINGS)
            except IOError as e:
                logger.error(f"Failed to create default settings file: {e}")
                return copy.deepcopy(DEFAULT_SETTINGS) # Return defaults anyway

        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                # Merge with defaults to handle potentially missing keys from older files
                merged_settings = self._deep_merge_dicts(loaded_settings, DEFAULT_SETTINGS)
                return merged_settings
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading or decoding settings file '{self.settings_path}': {e}. Returning default settings.")
            # Optional: backup corrupt file here
            # backup_path = self.settings_path + ".corrupt"
            # try:
            #     os.rename(self.settings_path, backup_path)
            #     logger.info(f"Corrupt settings file backed up to {backup_path}")
            # except OSError as backup_e:
            #     logger.error(f"Could not back up corrupt settings file: {backup_e}")
            return copy.deepcopy(DEFAULT_SETTINGS) # Return defaults on error

    def save_settings(self, settings):
        """
        Saves the provided settings dictionary to the JSON file.

        Args:
            settings (dict): The settings dictionary to save.

        Returns:
            bool: True if saving was successful, False otherwise.
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logger.info(f"Settings successfully saved to '{self.settings_path}'")
            return True
        except IOError as e:
            logger.error(f"Error saving settings to '{self.settings_path}': {e}")
            return False
        except TypeError as e:
             logger.error(f"Error serializing settings (check data types): {e}")
             return False

    def get_setting(self, key, default=None):
        """
        Retrieves a specific top-level setting value or a nested value using dot notation.

        Example: get_setting('general.theme')
                 get_setting('selected_llm')

        Args:
            key (str): The key to retrieve (can use dot notation for nested keys).
            default: The value to return if the key is not found.

        Returns:
            The value associated with the key, or the default.
        """
        settings = self.load_settings()
        value = settings
        try:
            for k in key.split('.'):
                if isinstance(value, dict):
                    value = value[k]
                else:
                    # Handle case where intermediate key is not a dict
                    return default
            return value
        except KeyError:
            return default

    def get_selected_model_key(self, model_type: str) -> str | None:
        """
        Gets the key of the currently selected model for a given type ('llm' or 'tts').

        Args:
            model_type (str): 'llm' or 'tts'.

        Returns:
            str or None: The key of the selected model (e.g., 'openai_gpt4o', 'kokoro') or None if not set.
        """
        setting_key = f'selected_{model_type}'
        return self.get_setting(setting_key)

    def _resolve_config_values(self, config: dict) -> dict:
        """Internal helper to resolve special values like env vars and relative paths."""
        resolved_config = copy.deepcopy(config) # Work on a copy

        # --- Resolve API Key from Environment Variable ---
        if 'api_key_env' in resolved_config:
            env_var_name = resolved_config['api_key_env']
            api_key = os.getenv(env_var_name)
            if not api_key:
                logger.warning(f"Environment variable '{env_var_name}' not set for config: {resolved_config.get('display_name', 'Unknown')}")
                resolved_config['api_key'] = None # Set explicitly to None if not found
            else:
                resolved_config['api_key'] = api_key # Add the resolved key
            # Optionally remove api_key_env after resolution? For security?
            # del resolved_config['api_key_env']

        # --- Resolve Relative Paths (e.g., for local models) ---
        if 'model_path' in resolved_config and resolved_config['model_path'] and not os.path.isabs(resolved_config['model_path']):
             relative_path = resolved_config['model_path']
             absolute_path = os.path.join(self.project_root, relative_path)
             # Normalize the path (handles '../' etc.)
             resolved_config['model_path'] = os.path.normpath(absolute_path)
             logger.debug(f"Resolved relative model path '{relative_path}' to '{resolved_config['model_path']}'")

        return resolved_config

    def get_model_config(self, model_type: str, model_key: str) -> dict:
        """
        Retrieves the specific configuration for a given model key ('llm' or 'tts'),
        resolving environment variables for API keys and adjusting relative paths.

        Args:
            model_type (str): 'llm' or 'tts'.
            model_key (str): The specific key of the model (e.g., 'openai_gpt4o').

        Returns:
            dict: The configuration dictionary for the model, including resolved values.
                  Returns an empty dict if the model key is not found.
        """
        options_key = f'{model_type}_options'
        model_config = self.get_setting(f"{options_key}.{model_key}", default={})

        if not model_config:
            logger.warning(f"No configuration found for {model_type} model '{model_key}'.")
            return {}

        # Resolve values like API keys and paths
        return self._resolve_config_values(model_config)

    def get_available_models(self, model_type: str) -> dict[str, str]:
        """
        Gets a dictionary of available models (key: display_name) for UI population.

        Args:
            model_type (str): 'llm' or 'tts'.

        Returns:
            dict: A dictionary mapping model keys to display names (e.g., {'kokoro': 'Kokoro TTS (Local)'}).
        """
        options_key = f'{model_type}_options'
        all_options = self.get_setting(options_key, default={})
        return {key: config.get("display_name", key) for key, config in all_options.items()}

    def update_setting(self, key: str, value) -> bool:
        """
        Updates a specific setting value using dot notation for nested keys and saves.

        Example: update_setting('general.theme', 'dark')
                 update_setting('selected_llm', 'openai_gpt4o')

        Args:
            key (str): The key to update (dot notation for nested).
            value: The new value to set.

        Returns:
            bool: True if successful, False otherwise.
        """
        settings = self.load_settings()
        keys = key.split('.')
        current_level = settings
        try:
            # Traverse dict to the second-to-last key
            for _, k in enumerate(keys[:-1]):
                if k not in current_level or not isinstance(current_level[k], dict):
                    # Create intermediate dicts if they don't exist
                    current_level[k] = {}
                current_level = current_level[k]

            # Set the final key's value
            last_key = keys[-1]
            current_level[last_key] = value

            return self.save_settings(settings)
        except (KeyError, TypeError) as e:
             logger.error(f"Failed to update setting '{key}': {e}")
             return False

# --- Example Usage ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Assuming settings.json is in the same directory as this script for example
    # In a real app, you might pass an explicit path or calculate project root
    manager = SettingsManager('settings_example.json') # Use a different name for testing

    # Load (will create defaults if settings_example.json doesn't exist)
    current_settings = manager.load_settings()
    print("Initial/Loaded Settings:", json.dumps(current_settings, indent=2))

    # Get specific settings
    selected_llm = manager.get_selected_model_key('llm')
    theme = manager.get_setting('general.theme')
    print(f"\nSelected LLM: {selected_llm}")
    print(f"Current Theme: {theme}")

    # Get config for the selected LLM (will resolve API key from env)
    if selected_llm:
        llm_config = manager.get_model_config('llm', selected_llm)
        print(f"\nConfig for {selected_llm}:")
        # Be careful printing resolved API keys in real logs!
        print(json.dumps(llm_config, indent=2))
        if 'api_key' in llm_config:
             print(f"(API Key loaded: {'Yes' if llm_config['api_key'] else 'No - Check OPENAI_API_KEY env var'})")


    # Get config for Kokoro (will resolve model path)
    kokoro_config = manager.get_model_config('tts', 'kokoro')
    print("\nConfig for kokoro:")
    print(json.dumps(kokoro_config, indent=2))


    # Get available models for UI
    available_tts = manager.get_available_models('tts')
    print(f"\nAvailable TTS Engines: {available_tts}")

    # Update a setting
    print("\nUpdating theme to 'dark'...")
    success = manager.update_setting('general.theme', 'dark')
    if success:
        print("Theme updated.")
        print(f"New theme value: {manager.get_setting('general.theme')}")
    else:
        print("Failed to update theme.")

    # Update selected model
    print("\nUpdating selected TTS to 'openai'...")
    success = manager.update_setting('selected_tts', 'openai')
    if success:
         print(f"New selected TTS: {manager.get_selected_model_key('tts')}")
    else:
         print("Failed to update selected TTS.")

    # Clean up example file if needed
    # try:
    #     os.remove('settings_example.json')
    #     print("\nRemoved settings_example.json")
    # except OSError:
    #     pass