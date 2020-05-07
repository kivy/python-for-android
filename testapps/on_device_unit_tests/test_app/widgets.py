# -*- coding: utf-8 -*-

from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.vector import Vector
from tools import load_kv_from

load_kv_from('widgets.kv')


class Spacer20(Widget):
    pass


class TestImage(BoxLayout):
    text = StringProperty()
    source = StringProperty()


class CircularButton(ButtonBehavior, Widget):
    def collide_point(self, x, y):
        return Vector(x, y).distance(self.center) <= self.width / 2


class ErrorPopup(Popup):
    error_text = StringProperty('')
