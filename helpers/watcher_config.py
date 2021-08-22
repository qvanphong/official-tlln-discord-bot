import json

import definition

_config: dict = None


def load_config():
    global _config
    with open(definition.get_path("watcher_config.json"), 'r') as f:
        _config = json.load(f)
        f.close()


def get_config(key: str):
    global _config
    if _config is None:
        load_config()

    if key in _config:
        return _config[key]
    else:
        raise KeyError(f"config attribute \"{key}\" is not found.")

