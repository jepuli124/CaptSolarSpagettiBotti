import json
import os


def get_config(config_name: str) -> str | int:
    config = os.getenv(config_name, None)
    if config is None:
        file_path = os.path.join(os.path.dirname(__file__), "../../config.json")
        with open(file_path, "r", encoding="utf-8") as config_file:
            config = json.loads(config_file.read())[config_name]
    return config
