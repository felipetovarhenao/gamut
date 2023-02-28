from __future__ import annotations
import tkinter as tk
from kivy.config import Config
from kivy.resources import resource_add_path
from kivy.lang import Builder
from ..sys import set_vebosity
import os

# disable GAMuT CLI messages
set_vebosity(False)

# enable tK for regular file system, but remove window on load
window = tk.Tk()
window.geometry('300x300-300-300')
window.withdraw()

# set default kivy window configuration on open
for key, val in [('resizable', False), ('width', '1360'), ('height', '850'), ('top', '100'), ('left', '100')]:
    Config.set('graphics', key, val)


def __load_kv_files__() -> None:
    """ Points Kivy to .kv file directory """
    root_dir = os.path.dirname(__file__)
    kv_dir = os.path.join(root_dir, 'data/kv')
    resource_add_path(root_dir)

    for file in os.listdir(kv_dir):
        Builder.load_file(os.path.join(kv_dir, file))


# load all available .kv files
__load_kv_files__()
