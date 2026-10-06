import json
from pathlib import Path

DATA_DIR = Path(__file__).parent


def load_json(name, default):
    path = DATA_DIR / name
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def save_json(name, data):
    path = DATA_DIR / name
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")