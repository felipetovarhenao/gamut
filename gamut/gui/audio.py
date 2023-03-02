# typing
from __future__ import annotations

# kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, StringProperty

# gamut
from .config import MOSAIC_CACHE, MOSAIC_DIR, GAMUT_SESSION
from .utils import parse_param_string, capture_exceptions, log_done, log_message
from .dialogs import SaveDialog
from ..features import Mosaic

# misc
import os


class Param(Widget):
    """
    Audio parameter widget
    """
    label = StringProperty('')
    value = StringProperty('')

    def list_filter(self, value: str, from_undo: bool = False) -> str | None:
        """ Text input filter for list-compatible parameters """
        if value.isdigit() or value in ['.', '(', ')', ' ']:
            return value

    def window_filter(self, value: str, from_undo: bool = False) -> str | None:
        """ Text input filter for list- and string-compatible parameters """
        if self.list_filter(value, from_undo) or value.isalpha():
            return value


class AudioWidget(Widget):
    """
    Audio module widget
    """
    params = ObjectProperty(None)
    synth_button = ObjectProperty(None)
    save_button = ObjectProperty(None)
    play_button = ObjectProperty(None)
    stop_button = ObjectProperty(None)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.audio_buffer = None

    def get_selected_mosaic(self) -> Widget:
        """ Short hand method to access selected mosaic in MosaicWidget """
        return App.get_running_app().root.mosaic_module.menu.selected_mosaic

    @capture_exceptions
    def get_parsed_params(self):
        """ Parse input audio parameters """
        params = {}
        for param in self.params.children:
            value = parse_param_string(param.text_input.text)
            params[param.key] = value
        return params

    @capture_exceptions
    @log_done
    def synth_audio(self) -> None:
        """ Triggers audio mosaic synthesis """
        self.stop_audio()
        mosaic_name = self.get_selected_mosaic()
        log_message(f'Synthesizing mosaic: {mosaic_name}...')
        params = self.get_parsed_params()
        if mosaic_name in MOSAIC_CACHE:
            mosaic = MOSAIC_CACHE[mosaic_name]
        else:
            path = os.path.join(MOSAIC_DIR, f"{mosaic_name}.gamut")
            mosaic = Mosaic().read(path)
        self.audio_buffer = mosaic.to_audio(**params)
        self.update_play_and_save_buttons()

    def update_play_and_save_buttons(self) -> None:
        """ Updates disabled state of buttons based on presence of audio buffer """
        val = not bool(self.audio_buffer)
        self.play_button.set_disabled(val)
        self.save_button.set_disabled(val)
        self.stop_button.set_disabled(val)

    def play_audio(self) -> None:
        """ Writes audio file at chosen directory """
        self.audio_buffer.play(blocking=False)

    def stop_audio(self) -> None:
        """ Stops audio buffer playback """
        if self.audio_buffer:
            self.audio_buffer.stop()

    @capture_exceptions
    @log_done
    def save_audio(self) -> None:
        """ Writes audio file at chosen directory """
        def on_save(path, text):
            GAMUT_SESSION.set('last_dir', os.path.dirname(path))
            filename = os.path.join(path, text)
            filename = f"{os.path.splitext(filename)[0]}.wav"
            log_message(f'Saving audio file: {filename}')
            self.audio_buffer.write(filename)
        SaveDialog(title="SAVE AUDIO MOSAIC", on_save=on_save).open()
