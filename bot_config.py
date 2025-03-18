import configparser
import os

class BotConfig:
    _config = None

    @staticmethod
    def _load_config():
        """Load the configuration file if not already loaded."""
        if BotConfig._config is None:
            # Determine the path to the config file (assuming it's in the same directory)
            config_file = 'bot_config.ini'
            if not os.path.exists(config_file):
                raise FileNotFoundError(f"Bot Config file '{config_file}' not found.")
            
            # Initialize configparser and load the file
            BotConfig._config = configparser.ConfigParser()
            BotConfig._config.read(config_file)

    @staticmethod
    def get(section, key, fallback=None):
        """Get a configuration value, optionally with a fallback."""
        BotConfig._load_config()
        return BotConfig._config.get(section, key, fallback=fallback)
    
    @staticmethod
    def get_int(section, key, fallback=None):
        """Get a configuration value, optionally with a fallback."""
        BotConfig._load_config()
        return int(BotConfig._config.get(section, key, fallback=fallback))

