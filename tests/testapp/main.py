print('main.py was successfully called')

import os
print('imported os')

print('contents of ./lib/python2.7/site-packages/kivy etc.')
print(os.listdir('./lib'))
print(os.listdir('./lib/python2.7'))
print(os.listdir('./lib/python2.7/site-packages'))
print(os.listdir('./lib/python2.7/site-packages/kivy'))

print('contents of this dir', os.listdir('./'))

with open('./lib/python2.7/site-packages/kivy/app.pyo', 'rb') as fileh:
    print('app.pyo size is', len(fileh.read()))

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


kv = '''
#:import Metrics kivy.metrics.Metrics

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
        Widget:
            size_hint_y: None
            height: 1000
            on_touch_down: print 'touched at', args[-1].pos

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
            from jnius import autoclass
        except ImportError:
            raise_error('Could not import pyjnius')
            return
        
        print('Attempting to vibrate with pyjnius')
        # PythonActivity = autoclass('org.renpy.android.PythonActivity')
        # activity = PythonActivity.mActivity
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        Intent = autoclass('android.content.Intent')
        Context = autoclass('android.content.Context')
        vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)

        vibrator.vibrate(1000)


TestApp().run()
