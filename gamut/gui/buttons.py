# typing
from __future__ import annotations

# ui
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton

import os


class BaseButton(Button):
    pass


class LargeButton(BaseButton):
    pass


class LargeDangerButton(LargeButton):
    pass


class LargeSuccessButton(LargeButton):
    pass


class MenuItem(ToggleButton):
    def __init__(self, value: str = 'item', **kwargs) -> None:
        self.value = value
        super().__init__(**kwargs)
        self.text = os.path.basename(self.value)
