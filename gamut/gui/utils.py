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


class ErrorPopup(Popup):
    def __init__(self, text: str = 'This is an error popup', **kwargs):
        super().__init__(**kwargs)
        self.title = 'ERROR'
        self.text = Label(text=text)
        self.size_hint = (None, None)
        self.size = (400, 400)


def log_message(text: str | Iterable) -> None:
    """ Logs a message in the GUI console window """
    root = App.get_running_app().root
    logs = [text] if isinstance(text, str) else text
    for log in logs:
        l = Factory.ConsoleLog(text=log)
        root.console.add_widget(l)
    if len(root.console.children) > 6:
        root.console.parent.scroll_to(l)


def capture_exceptions(func):
    """ Decorator to prevent crashing by printing error in GUI console window """
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_type = type(e).__name__
            log_message([traceback.format_exc(), f"{error_type}: {str(e)}", '---'])
    return decorator


def log_done(func):
    """ Decorator for logging successful callback execution """
    def decorator(*args, **kwargs):
        out = func(*args, **kwargs)
        log_message("Done!\n---")
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
