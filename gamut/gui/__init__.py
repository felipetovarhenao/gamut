# typing
from __future__ import annotations

# import all widgets
from .__gui_init__ import *
from .buttons import *
from .corpus import *
from .audio import *
from .mosaic import *

# gamut
from ..__version__ import __version__
from .theme import Theme
from .utils import log_message

# kivy imports
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.clock import Clock


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
        self.theme = Theme()
        self.version = f"v{__version__}"

    def build(self) -> Widget:
        """ Returns root widget """
        self.title = 'GAMuT user interface'
        self.icon = 'data/images/icon.png'
        return Main()

    def run(self, test: int | None = None) -> None:
        if test:
            Clock.schedule_once(lambda _: self.stop(), test)
        super().run()
