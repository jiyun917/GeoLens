import json
import os
from typing import List, Optional

from ..models import Manual

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
MANUALS_FILE = os.path.join(DATA_DIR, "manuals.json")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_manuals() -> List[Manual]:
    _ensure_data_dir()
    if not os.path.exists(MANUALS_FILE):
        return []
    with open(MANUALS_FILE, "r") as f:
        data = json.load(f)
    return [Manual(**item) for item in data]


def save_manuals(manuals: List[Manual]):
    _ensure_data_dir()
    with open(MANUALS_FILE, "w") as f:
        json.dump([m.model_dump() for m in manuals], f, indent=2)


def add_manual(manual: Manual):
    manuals = load_manuals()
    manuals.append(manual)
    save_manuals(manuals)


def update_manual(manual_id: str, **kwargs):
    manuals = load_manuals()
    for m in manuals:
        if m.id == manual_id:
            for key, value in kwargs.items():
                setattr(m, key, value)
            break
    save_manuals(manuals)


def get_manual(manual_id: str) -> Optional[Manual]:
    manuals = load_manuals()
    for m in manuals:
        if m.id == manual_id:
            return m
    return None


def delete_manual(manual_id: str):
    manuals = load_manuals()
    manuals = [m for m in manuals if m.id != manual_id]
    save_manuals(manuals)
