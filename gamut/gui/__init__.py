from __future__ import annotations

# import all widgets
from .__gui_init__ import *
from .buttons import *
from .corpus import *
from .audio import *
from .mosaic import *

# misc
from .theme import Theme
from .config import GAMUT_FILES_DIRECTORY, CORPUS_DIR, MOSAIC_DIR

# kivy imports
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.app import App
import os


class Main(Widget):
    """
    Main UI Widget, containing all modules.
    Child widgets are included through the .kv file
    """
    header = ObjectProperty(None)
    body = ObjectProperty(None)
    footer = ObjectProperty(None)
    console = ObjectProperty(None)
    mosaic_module = ObjectProperty(None)
    corpus_module = ObjectProperty(None)


class GUI(App):
    """
    GAMuT Graphical User Interface class
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__create_root_directory()
        self.theme = Theme()

    def __create_root_directory(self) -> None:
        """ Create storage directories """
        for _dir in [GAMUT_FILES_DIRECTORY, CORPUS_DIR, MOSAIC_DIR]:
            if not os.path.exists(_dir):
                os.mkdir(_dir)

    def build(self):
        self.title = 'GAMuT user interface'
        self.icon = 'data/images/icon.png'
        return Main()
