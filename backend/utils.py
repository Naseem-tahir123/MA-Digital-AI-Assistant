# backend/utils.py

import os
import json
from dotenv import load_dotenv

def load_env():
    """Loads environment variables from a .env file."""
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")

def ensure_dir(path: str):
    """Creates directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def save_json(data, filename: str):
    """Save Python dict or list to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(filename: str):
    """Load data from a JSON file."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)
