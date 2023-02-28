from __future__ import annotations
from collections.abc import Iterable

# misc
from ast import literal_eval
import traceback
import re

# kivy
from kivy.factory import Factory
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label


class ConsoleLog(Factory.TextLabel):
    def __init__(self, *args, index, **kwargs) -> None:
        self.index = index
        super().__init__(*args, **kwargs)


class ErrorPopup(Popup):
    def __init__(self, text: str = 'This is an error popup', **kwargs):
        super().__init__(**kwargs)
        self.title = 'ERROR'
        self.text = Label(text=text)
        self.size_hint = (None, None)
        self.size = (400, 400)


APP = None


def get_log_style(key):
    app = get_app()
    log_styles = {
        'normal': {
            'color': app.theme.colors.txt3,
        },
        'error': {
            'color': app.theme.colors.danger,
            'bold': True
        },
        'success': {
            'color': app.theme.colors.txt_hl
        },
    }
    return log_styles[key]


def get_app():
    global APP
    if not APP:
        APP = App.get_running_app()
    return APP


def log_message(text: str | Iterable, log_type: str = 'normal') -> None:
    """ Logs a message in the GUI console window """
    root = get_app().root
    logs = [text] if isinstance(text, str) else text
    style = get_log_style(log_type)
    for log in logs:
        l = ConsoleLog(text=log, index=len(root.console.children), **style)
        root.console.add_widget(l)
    if len(root.console.children) > 16:
        root.console.parent.scroll_to(l)


def capture_exceptions(func):
    """ Decorator to prevent crashing by printing error in GUI console window """
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_type = type(e).__name__
            msg = remove_ansi(str(e))
            log_message([f"{error_type}: {msg}"], 'error')
    return decorator


def log_done(func):
    """ Decorator for logging successful callback execution """
    def decorator(*args, **kwargs):
        out = func(*args, **kwargs)
        log_message("Done!", 'success')
        return out
    return decorator


def remove_ansi(text):
    """ Removes ANSI stuff from string """
    ansi_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_pattern.sub('', text)


def parse_param_string(raw_string: str):
    """ Parses a lisp-like formatted list string as Python list """
    # remove spacing at both ends
    value = raw_string.strip()

    # return if a it's simple string
    if value.isalpha():
        return value

    # remove parentheses-adjacent spaces between
    paren_spaces = re.compile(r' +(?=\))|(?<=\() +')
    value = paren_spaces.sub('', value)

    # replace duplicated spaces with single ones
    dup_spaces = re.compile(r' +')
    value = dup_spaces.sub(' ', value)

    # replace chars before literal eval
    for before, after in [('(', '['), (' ', ','), (')', ']')]:
        value = value.replace(before, after)
    return literal_eval(value)
