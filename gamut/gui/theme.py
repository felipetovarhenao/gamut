from __future__ import annotations


def rgba(hex: str) -> tuple:
    """ HEX to RGBA conversion """
    return *tuple(int(hex[int(hex[0] == '#'):][i:i+2], 16)/255.0 for i in (0, 2, 4)), 1


class ColorPalette:
    """ Entrypoint for all RGBA-formatted theme colors """

    def __init__(self) -> None:
        self.bg1 = rgba("1d1f25")
        self.bg2 = rgba("272931")
        self.bg3 = rgba("30323b")
        self.bg4 = rgba("3E404A")
        self.txt1 = rgba("e1e1e1")
        self.txt2 = rgba("d6d6d6")
        self.txt3 = rgba("c1c1c1")
        self.txt_hl = rgba("C7D0FF")
        self.txt_neg = rgba("ffffff")
        self.primary = rgba("4d5360")
        self.secondary = rgba("5b6476")
        self.success = rgba("60799f")
        self.success_hl = rgba("718cb5")
        self.danger = rgba("A05F5F")
        self.danger_hl = rgba("E97575")
        self.border = rgba("474A53")
        self.disabled_mask = (0, 0, 0, 0.4)


class Font:
    """
    Utility class to create consistent tkinter font tuples
    """

    def __init__(self,
                 font_name: str = "Roboto",
                 xs: int | float = 9,
                 sm: int | float = 10,
                 ms: int | float = 12,
                 md: int | float = 14,
                 ml: int | float = 16,
                 lg: int | float = 18,
                 xl: int | float = 20,
                 xxl: int | float = 22) -> None:
        self.name = font_name
        self._xs = xs
        self._sm = sm
        self._ms = ms
        self._md = md
        self._ml = ml
        self._lg = lg
        self._xl = xl
        self._xxl = xxl

    def size(self, size: str | None = None):
        """ Font size getter """
        return str(getattr(self, f"_{size or 'md'}")) + 'dp'


class Theme:
    """ Entrypoint for GUI theme properties """

    def __init__(self) -> None:
        self.colors = ColorPalette()
        self.font = Font()
        self.spacing = 10

    def pad(self, n: int = 1):
        return f'{3*n}dp'
