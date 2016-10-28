print('main.py was successfully called')

import os
print('imported os')

from kivy import platform

if platform == 'android':
    print('contents of ./lib/python2.7/site-packages/ etc.')
    print(os.listdir('./lib'))
    print(os.listdir('./lib/python2.7'))
    print(os.listdir('./lib/python2.7/site-packages'))

    print('this dir is', os.path.abspath(os.curdir))

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
#:import Window kivy.core.window.Window

<FixedSizeButton@Button>:
    size_hint_y: None
    height: dp(60)


BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: None
        height: dp(50)
        orientation: 'horizontal'
        Button:
            text: 'None'
            on_press: Window.softinput_mode = ''
        Button:
            text: 'pan'
            on_press: Window.softinput_mode = 'pan'
        Button:
            text: 'below_target'
            on_press: Window.softinput_mode = 'below_target'
        Button:
            text: 'resize'
            on_press: Window.softinput_mode = 'resize'
    Widget:
        Scatter:
            id: scatter
            size_hint: None, None
            size: dp(300), dp(80)
            on_parent: self.pos = (300, 100)
            BoxLayout:
                size: scatter.size
                orientation: 'horizontal'
                canvas:
                    Color:
                        rgba: 1, 0, 0, 1
                    Rectangle:
                        pos: 0, 0
                        size: self.size
                Widget:
                    size_hint_x: None
                    width: dp(30)
                TextInput:
                    text: 'type in me'
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

    def test_ctypes(self, *args):
        import ctypes
            
    def test_numpy(self, *args):
        import numpy

        print(numpy.zeros(5))
        print(numpy.arange(5))
        print(numpy.random.random((3, 3)))

TestApp().run()
