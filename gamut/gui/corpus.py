from __future__ import annotations
from tkinter.filedialog import askdirectory, askopenfilenames
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import ObjectProperty
from .config import CORPUS_DIR
from kivy.clock import Clock
import os
from .utils import log_message, capture_exceptions, log_done
from ..features import Corpus
from .config import CORPUS_CACHE
from ..config import AUDIO_FORMATS
from kivy.app import App


def on_toggle_click(self, toggle, name):
    item_list = getattr(self, f'selected_{name}')
    delete_button = getattr(self, f'delete_{name}_button')
    if toggle.state == 'normal':
        item_list.remove(toggle.text)
    else:
        item_list.append(toggle.text)
    delete_button.set_disabled(not bool(item_list))


class CorpusFactoryWidget(Widget):
    sources_menu = ObjectProperty(None)
    features_menu = ObjectProperty(None)
    delete_sources_button = ObjectProperty(None)
    create_corpus_button = ObjectProperty(None)
    corpus_name = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sources = []
        self.selected_sources = []
        self.has_name = False
        self.selected_features = ['timbre']
        Clock.schedule_once(lambda _: self.corpus_name.bind(text=self.corpus_name_filter), 1)

    def update_create_corpus_button(self):
        self.create_corpus_button.set_disabled(not all([self.sources, self.selected_features, self.has_name]))

    def update_corpus_menu(self):
        App.get_running_app().root.corpus_module.menu.update_corpus_menu()

    def corpus_name_filter(self, instance, value):
        self.has_name = bool(value)
        self.update_create_corpus_button()

    def get_existent_corpus_names(self):
        return [toggle.text.lower() for toggle in App.get_running_app().root.corpus_module.menu.corpora_menu.children]

    def load_folder_path(self):
        path = askdirectory(title='Choose corpus source folder')
        if path in self.sources:
            return
        self.sources.append(path)
        self.sources_menu.add_widget(self.make_toggle(text=path, name='sources'))
        self.update_create_corpus_button()

    def load_file_paths(self):
        files = askopenfilenames(filetypes=[("Audio files", " ".join(AUDIO_FORMATS))])
        for file in files:
            if file in self.sources:
                continue
            self.sources.append(file)
            self.sources_menu.add_widget(self.make_toggle(text=file, name='sources'))
        self.update_create_corpus_button()

    def update_selected(self, name):
        setattr(self, f'selected_{name}', [toggle.text for toggle in getattr(
            self, f"{name}_menu").children if toggle.state == 'down'])
        btn_name = f'delete_{name}_button'
        if hasattr(self, btn_name):
            btn = getattr(self, btn_name)
            btn.set_disabled(not bool(getattr(self, f'selected_{name}')))
        self.update_create_corpus_button()

    def delete_selected(self, name):
        selected = getattr(self, f'selected_{name}')
        menu = getattr(self, f'{name}_menu')
        for item in selected:
            if name == 'sources':
                self.sources.remove(item)
            for toggle in menu.children:
                if toggle.text == item:
                    menu.remove_widget(toggle)
                    break
        setattr(self, f'selected_{name}', [])
        getattr(self, f'delete_{name}_button').set_disabled(True)
        self.update_create_corpus_button()

    @capture_exceptions
    @log_done
    def create_corpus(self):
        corpus_name = self.corpus_name.text
        log_message(f'Creating corpus: {self.corpus_name.text}...')
        global CORPUS_CACHE
        corpus = Corpus(source=self.sources, features=self.selected_features)
        corpus.write(os.path.join(CORPUS_DIR, f'{corpus_name}.gamut'))
        CORPUS_CACHE[corpus_name] = corpus
        self.update_corpus_menu()

    def make_toggle(self, text, name):
        return ToggleButton(text=text, on_release=lambda _: self.update_selected(name))


class CorpusMenuWidget(Widget):
    corpora_menu = ObjectProperty(None)
    selected_corpora = ObjectProperty(None)
    delete_corpora_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda _: self.update_corpus_menu(), 1)

    def update_corpus_menu(self):
        self.clear_menu()
        for path in os.listdir(CORPUS_DIR):
            corpus_name = os.path.basename(os.path.splitext(path)[0])
            t = ToggleButton(text=corpus_name, on_release=lambda _: self.update_delete_button() or self.update_create_mosaic_button())
            self.corpora_menu.add_widget(t)
        self.update_delete_button()

    def get_selected_toggles(self):
        return [toggle for toggle in self.corpora_menu.children if toggle.state == 'down']

    def update_create_mosaic_button(self):
        App.get_running_app().root.mosaic_module.factory.update_create_mosaic_button()

    def update_delete_button(self):
        self.delete_corpora_button.set_disabled(not bool(self.get_selected_toggles()))

    def delete_selected_corpora(self):
        for toggle in self.get_selected_toggles():
            self.corpora_menu.remove_widget(toggle)
            os.remove(os.path.join(CORPUS_DIR, f"{toggle.text}.gamut"))
        self.update_delete_button()

    def clear_menu(self):
        while self.corpora_menu.children:
            self.corpora_menu.clear_widgets()
        self.update_delete_button()


class CorpusWidget(Widget):
    menu = ObjectProperty(None)
    factory = ObjectProperty(None)
