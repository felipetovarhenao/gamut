# typing
from __future__ import annotations
from collections.abc import Iterable

# gui
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, StringProperty

# gamut
from .config import CORPUS_DIR, MOSAIC_DIR, CORPUS_CACHE, MOSAIC_CACHE, GAMUT_SESSION
from .utils import capture_exceptions, log_done, log_message, UserConfirmation
from .dialogs import LoadDialog
from .buttons import MenuItem

from ..features import Corpus, Mosaic
from ..config import AUDIO_FORMATS

# misc
import os


class MosaicFactoryWidget(Widget):
    delete_mosaic_button = ObjectProperty(None)
    create_mosaic_button = ObjectProperty(None)
    mosaic_name = ObjectProperty(None)
    target = StringProperty('')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.has_name = False
        Clock.schedule_once(lambda _: self.mosaic_name.bind(text=self.on_mosaic_name_update), 1)

    def get_selected_corpora(self) -> None:
        return [toggle.value for toggle in App.get_running_app().root.corpus_module.menu.corpora_menu.children if toggle.state == 'down']

    def update_create_mosaic_button(self) -> None:
        value = all([self.has_name, self.get_selected_corpora(), self.target])
        self.create_mosaic_button.set_disabled(not value)

    def on_mosaic_name_update(self, instance: Widget, value: str) -> None:
        self.has_name = bool(value)
        self.update_create_mosaic_button()

    def update_mosaic_menu(self) -> None:
        App.get_running_app().root.mosaic_module.menu.update_mosaic_menu()

    def load_target(self) -> None:
        def on_load(selected: Iterable):
            self.target = selected[0]
            GAMUT_SESSION.set('last_dir', os.path.dirname(self.target))
            self.update_create_mosaic_button()
        LoadDialog(on_load=on_load,
                   title='CHOOSE TARGET',
                   filters=[f"*{ft}" for ft in AUDIO_FORMATS]).open()

    @capture_exceptions
    @log_done
    def create_mosaic(self) -> None:
        mosaic_name = self.mosaic_name.text
        log_message(f"Creating mosaic: {mosaic_name}...")
        corpus_names = self.get_selected_corpora()
        corpora = []
        for corpus_name in corpus_names:
            log_message(f"Loading corpus: {corpus_name}...")
            if corpus_name in CORPUS_CACHE:
                corpora.append(CORPUS_CACHE[corpus_name])
            else:
                path = os.path.join(CORPUS_DIR, f"{corpus_name}.gamut")
                corpus = Corpus().read(path)
                corpora.append(corpus)
                CORPUS_CACHE[corpus_name] = corpus
        log_message(f"Maching segments...")
        global MOSAIC_CACHE
        mosaic = Mosaic(target=self.target, corpus=corpora)
        mosaic.write(os.path.join(MOSAIC_DIR, f'{mosaic_name}.gamut'))
        MOSAIC_CACHE[mosaic_name] = mosaic
        self.update_mosaic_menu()


class MosaicMenuWidget(Widget):
    delete_mosaic_button = ObjectProperty(None)
    mosaic_menu = ObjectProperty(None)
    audio_module = ObjectProperty(None)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selected_mosaic = None
        Clock.schedule_once(lambda _: self.update_mosaic_menu(), 1)

    def update_mosaic_menu(self) -> None:
        last_selected = [toggle.value for toggle in self.get_selected_toggles()]
        self.clear_menu()
        for path in sorted(os.listdir(MOSAIC_DIR)):
            mosaic_name = os.path.basename(os.path.splitext(path)[0])
            state = 'down' if mosaic_name in last_selected else 'normal'
            t = MenuItem(value=mosaic_name,
                         state=state,
                         on_release=lambda toggle: self.exclusive_select(toggle) or self.update_delete_button())
            self.mosaic_menu.add_widget(t)
        self.update_delete_button()

    def clear_menu(self) -> None:
        while self.mosaic_menu.children:
            self.mosaic_menu.clear_widgets()
        self.update_delete_button()

    def exclusive_select(self, toggle: Widget) -> None:
        if toggle.state == 'normal':
            self.selected_mosaic = None
        else:
            for child in self.mosaic_menu.children:
                if child != toggle:
                    child.state = 'normal'
            self.selected_mosaic = toggle.value
        self.update_audio_synth_button()

    def delete_selected_mosaics(self) -> None:
        def on_confirm():
            for toggle in self.get_selected_toggles():
                self.mosaic_menu.remove_widget(toggle)
                os.remove(os.path.join(MOSAIC_DIR, f"{toggle.value}.gamut"))
            self.selected_mosaic = None
            self.update_delete_button()
            self.update_audio_synth_button()
            log_message(f"Mosaic deleted", log_type='error')
        UserConfirmation(on_confirm=on_confirm, long_text=f"You're about to delete this mosaic.").open()

    def update_audio_synth_button(self) -> None:
        App.get_running_app().root.mosaic_module.audio_module.synth_button.set_disabled(not bool(self.selected_mosaic))

    def get_selected_toggles(self) -> None:
        return [toggle for toggle in self.mosaic_menu.children if toggle.state == 'down']

    def update_delete_button(self) -> None:
        self.delete_mosaic_button.set_disabled(not bool(self.get_selected_toggles()))


class MosaicWidget(Widget):
    menu = ObjectProperty(None)
    factory = ObjectProperty(None)
