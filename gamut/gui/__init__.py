# typing
from __future__ import annotations

# import all widgets
from .__gui_init__ import *
from .buttons import *
from .corpus import *
from .audio import *
from .mosaic import *

# gamut
from .theme import Theme
from .config import GAMUT_FILES_DIRECTORY, CORPUS_DIR, MOSAIC_DIR
from .utils import log_message

# kivy imports
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.clock import Clock

# misc
import os


class Main(Widget):
    """
    Main UI Widget, containing all modules.
    Child widgets are included through the .kv file
    """
    console = ObjectProperty(None)
    mosaic_module = ObjectProperty(None)
    corpus_module = ObjectProperty(None)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        Clock.schedule_once(lambda _: log_message("GAMuT session intialized"), 1)


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

    def build(self) -> Widget:
        """ Returns root widget """
        self.title = 'GAMuT user interface'
        self.icon = 'data/images/icon.png'
        return Main()

    def run(self, test: int | None = None) -> None:
        if test:
            Clock.schedule_once(lambda _: self.stop(), test)
        super().run()
