# config.py
import json
import os

CONFIG_FILE = "config.json"

# Default config
default_config = {
    "max_retries": 3,
    "backoff_base": 2
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(default_config)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def set_config(key, value):
    config = load_config()
    config[key] = value
    save_config(config)

def get_config(key):
    config = load_config()
    return config.get(key, default_config.get(key))
