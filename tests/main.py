import unittest
from gamut.gui import GUI
from kivy.clock import Clock


class GamutTest(unittest.TestCase):

    def test_gui_build(self):
        GUI().build()
