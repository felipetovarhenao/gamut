from __future__ import annotations
from pathlib import Path
import os


GAMUT_FILES_DIRECTORY = os.path.join(Path.home(), '.gamut')
CORPUS_DIR = os.path.join(GAMUT_FILES_DIRECTORY, 'corpora')
MOSAIC_DIR = os.path.join(GAMUT_FILES_DIRECTORY, 'mosaics')
CORPUS_CACHE = {}
MOSAIC_CACHE = {}