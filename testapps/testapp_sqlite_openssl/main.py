print('main.py was successfully called')

import os
print('imported os')


print('this dir is', os.path.abspath(os.curdir))

print('contents of this dir', os.listdir('./'))

import sys
print('pythonpath is', sys.path)

import kivy
print('imported kivy')
print('file is', kivy.__file__)

from kivy.app import App

from kivy.lang import Builder
from kivy.properties import StringProperty

from kivy.uix.popup import Popup
from kivy.clock import Clock

print('Imported kivy')
from kivy.utils import platform
print('platform is', platform)

import peewee
import requests
import sqlite3


try:
    inclemnet = requests.get('http://inclem.net/')
    print('got inclem.net request')
except:
    inclemnet = 'failed inclemnet'

try:
    kivy = requests.get('https://kivy.org/')
    print('got kivy request (https)')
except:
    kivy = 'failed kivy'

from peewee import *
db = SqliteDatabase('test.db')

class Person(Model):
    name = CharField()
    birthday = DateField()
    is_relative = BooleanField()

    class Meta:
        database = db

    def __repr__(self):
        return '<Person: {}, {}>'.format(self.name, self.birthday)

    def __str__(self):
        return repr(self)

db.connect()
try:
    db.create_tables([Person])
except:
    import traceback
    traceback.print_exc()

import random
from datetime import date
test_person = Person(name='person{}'.format(random.randint(0, 1000)),
                     birthday=date(random.randint(1900, 2000), random.randint(1, 9), random.randint(1, 20)),
                     is_relative=False)
test_person.save()


kv = '''
#:import Metrics kivy.metrics.Metrics
#:import sys sys

<FixedSizeButton@Button>:
    size_hint_y: None
    height: dp(60)


ScrollView:
    GridLayout:
        cols: 1
        size_hint_y: None
        height: self.minimum_height
        FixedSizeButton:
            text: 'test pyjnius'
            on_press: app.test_pyjnius()
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            text_size: self.size[0], None
            markup: True
            text: 'kivy request: {}\\ninclemnet request: {}'.format(app.kivy_request, app.inclemnet_request)
            halign: 'center'
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            text_size: self.size[0], None
            markup: True
            text: 'people: {}'.format(app.people)
            halign: 'center'
        Image:
            keep_ratio: False
            allow_stretch: True
            source: 'colours.png'
            size_hint_y: None
            height: dp(100)
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            font_size: 100
            text_size: self.size[0], None
            markup: True
            text: '[b]Kivy[/b] on [b]SDL2[/b] on [b]Android[/b]!'
            halign: 'center'
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            text_size: self.size[0], None
            markup: True
            text: sys.version
            halign: 'center'
            padding_y: dp(10)
        Widget:
            size_hint_y: None
            height: 20
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            font_size: 50
            text_size: self.size[0], None
            markup: True
            text: 'dpi: {}\\ndensity: {}\\nfontscale: {}'.format(Metrics.dpi, Metrics.density, Metrics.fontscale)
            halign: 'center'
        FixedSizeButton:
            text: 'test ctypes'
            on_press: app.test_ctypes()
        FixedSizeButton:
            text: 'test numpy'
            on_press: app.test_numpy()
        Widget:
            size_hint_y: None
            height: 1000
            on_touch_down: print('touched at', args[-1].pos)

<ErrorPopup>:
    title: 'Error' 
    size_hint: 0.75, 0.75
    Label:
        text: root.error_text
'''


class ErrorPopup(Popup):
    error_text = StringProperty('')

def raise_error(error):
    print('ERROR:',  error)
    ErrorPopup(error_text=error).open()

class TestApp(App):

    kivy_request = kivy
    inclemnet_request = inclemnet

    people = ', '.join(map(str, list(Person.select())))

    def build(self):
        root = Builder.load_string(kv)
        Clock.schedule_interval(self.print_something, 2)
        # Clock.schedule_interval(self.test_pyjnius, 5)
        print('testing metrics')
        from kivy.metrics import Metrics
        print('dpi is', Metrics.dpi)
        print('density is', Metrics.density)
        print('fontscale is', Metrics.fontscale)
        return root

    def print_something(self, *args):
        print('App print tick', Clock.get_boottime())

    def on_pause(self):
        return True

    def test_pyjnius(self, *args):
        try:
            from jnius import autoclass, cast
        except ImportError:
            raise_error('Could not import pyjnius')
            return
        print('Attempting to vibrate with pyjnius')
        ANDROID_VERSION = autoclass('android.os.Build$VERSION')
        SDK_INT = ANDROID_VERSION.SDK_INT

        Context = autoclass("android.content.Context")
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity

        vibrator_service = activity.getSystemService(Context.VIBRATOR_SERVICE)
        vibrator = cast("android.os.Vibrator", vibrator_service)

        if vibrator and SDK_INT >= 26:
            print("Using android's `VibrationEffect` (SDK >= 26)")
            VibrationEffect = autoclass("android.os.VibrationEffect")
            vibrator.vibrate(
                VibrationEffect.createOneShot(
                    1000, VibrationEffect.DEFAULT_AMPLITUDE,
                ),
            )
        elif vibrator:
            print("Using deprecated android's vibrate (SDK < 26)")
            vibrator.vibrate(1000)
        else:
            print('Something happened...vibrator service disabled?')

    def test_ctypes(self, *args):
        pass
            
    def test_numpy(self, *args):
        import numpy

        print(numpy.zeros(5))
        print(numpy.arange(5))
        print(numpy.random.random((3, 3)))
                    

TestApp().run()
