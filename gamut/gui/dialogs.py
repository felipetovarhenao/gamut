from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from .config import GAMUT_SESSION
from collections.abc import Callable, Iterable


class BaseDialog(FloatLayout):
    def __init__(self,
                 title: str = 'LOAD FILE OR FOLDER',
                 **kwargs):
        self.popup = None
        self.title = title
        self.last_path = GAMUT_SESSION.get('last_dir')
        super().__init__(**kwargs)

    def open(self):
        self.popup = Popup(title=self.get_popup_title(),
                           content=self,
                           size_hint=(0.9, 0.9))
        self.popup.open()

    def on_cancel(self):
        self.popup.dismiss()

    def on_entry_added(self, chooser):
        if chooser.path != self.last_path:
            chooser.selection = []
            self.last_path = chooser.path
            self.popup.title = self.get_popup_title()

    def get_popup_title(self):
        return f"{self.title}: {self.last_path}"


class LoadDialog(BaseDialog):
    def __init__(self,
                 on_load: Callable = None,
                 multiselect: bool = False,
                 dirselect: bool = False,
                 filters: Iterable = None,
                 **kwargs):
        self.on_load = on_load or (lambda path, selection: print(path, selection))
        self.multiselect = multiselect
        self.dirselect = dirselect
        self.filters = filters or []
        super().__init__(**kwargs)


class SaveDialog(BaseDialog):
    text_input = ObjectProperty(None)
    save_button = ObjectProperty(None)

    def __init__(self, on_save: Callable, title: str = 'LOAD FILE OR FOLDER', **kwargs):
        self.on_save = on_save  # a callable that takes two arguments: path, and filename
        super().__init__(title, **kwargs)
        Clock.schedule_once(lambda _: self.text_input.bind(text=self.on_text_change), 1)

    def on_text_change(self, instance, value):
        self.save_button.set_disabled(not value)
