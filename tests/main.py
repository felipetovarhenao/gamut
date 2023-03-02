import unittest
from gamut.gui import GUI
from kivy.clock import Clock


class GamutTest(unittest.TestCase):

    def test_gui_run(self):
        gui = GUI()
        Clock.schedule_once(lambda _: gui.stop(), 3)
        gui.run()
