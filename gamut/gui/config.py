# typing
from __future__ import annotations

# misc
from pathlib import Path
import os
import json


GAMUT_FILES_DIRECTORY = os.path.join(Path.home(), '.gamut')
CORPUS_DIR = os.path.join(GAMUT_FILES_DIRECTORY, 'corpora')
MOSAIC_DIR = os.path.join(GAMUT_FILES_DIRECTORY, 'mosaics')
SESSION_DATA_FILE = os.path.join(GAMUT_FILES_DIRECTORY, 'session_data.json')
CORPUS_CACHE = {}
MOSAIC_CACHE = {}


class GamutSession:

    def __init__(self) -> None:
        self.last_dir = None
        self.load()

    def clean_last_dir(self, attr: str, value: str | float | int) -> str | float | int:
        if os.path.exists(value):
            return value
        default = self.get_default_attrs()[attr]
        setattr(self, attr, default)
        return default

    def get_default_attrs(self) -> dict:
        return {
            'last_dir': str(Path.home()),
        }

    def load(self) -> None:
        # create session file if it doesn't exist
        if not os.path.exists(SESSION_DATA_FILE):
            os.makedirs(os.path.dirname(SESSION_DATA_FILE))
            with open(SESSION_DATA_FILE, 'w') as f:
                json.dump(self.get_default_attrs(), f)

        # open file an populate attributes
        with open(SESSION_DATA_FILE, 'rb') as f:
            data = json.load(f)
            default_attrs = self.get_default_attrs()
            for attr in vars(self):
                setattr(self, attr, data[attr] if attr in data else default_attrs[attr])

    def save(self) -> None:
        with open(SESSION_DATA_FILE, 'w') as f:
            json.dump(vars(self), f)

    def get(self, attr: str) -> str | float | int:
        value = getattr(self, attr)
        cleaner = getattr(self, f"clean_{attr}")
        if cleaner:
            clean_value = cleaner(attr, value)
            if clean_value != value:
                self.set(attr, clean_value)
            return clean_value
        return value

    def set(self, attr: str, value: str | float | int) -> str | float | int:
        setattr(self, attr, value)
        self.save()


GAMUT_SESSION = GamutSession()
