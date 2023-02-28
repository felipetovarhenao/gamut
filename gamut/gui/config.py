from __future__ import annotations
from pathlib import Path
import os


LAST_VISITED_DIR = Path.home()
GAMUT_FILES_DIRECTORY = os.path.join(Path.home(), '.gamut')
CORPUS_DIR = os.path.join(GAMUT_FILES_DIRECTORY, 'corpora')
MOSAIC_DIR = os.path.join(GAMUT_FILES_DIRECTORY, 'mosaics')
CORPUS_CACHE = {}
MOSAIC_CACHE = {}
