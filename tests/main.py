import unittest
from gamut.gui import GUI
from kivy.clock import Clock


class GamutTest(unittest.TestCase):

    def test_gui_run(self):
        GUI().run(test=1.5)
