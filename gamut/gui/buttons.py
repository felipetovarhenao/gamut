# typing
from __future__ import annotations

# ui
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import ListProperty

import os
from kivy.core.window import Window


class BaseButton(Button):
    bg_color = ListProperty((0, 0, 0, 0))
    bg_color_down = ListProperty((0, 0, 0, 0))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_hover)

    def on_hover(self, w, p):
        """ Highlighted button color on hover """
        if self.disabled:
            return
        if not hasattr(self, 'bg_color_hover'):
            self.bg_color_normal = self.bg_color
            self.bg_color_hover = tuple(min(1, x*1.25) for x in self.bg_color)
        self.bg_color = self.bg_color_hover if self.collide_point(*p) else self.bg_color_normal


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
