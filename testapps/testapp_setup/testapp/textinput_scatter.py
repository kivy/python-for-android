print('main.py was successfully called')

import os
print('imported os')

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


###########
from kivy import platform
if platform == 'android':
    from jnius import PythonJavaClass, java_method, autoclass

    _PythonActivity = autoclass('org.kivy.android.PythonActivity')


    class Runnable(PythonJavaClass):
        '''Wrapper around Java Runnable class. This class can be used to schedule a
        call of a Python function into the PythonActivity thread.
        '''

        __javainterfaces__ = ['java/lang/Runnable']
        __runnables__ = []

        def __init__(self, func):
            super(Runnable, self).__init__()
            self.func = func

        def __call__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            Runnable.__runnables__.append(self)
            _PythonActivity.mActivity.runOnUiThread(self)

        @java_method('()V')
        def run(self):
            try:
                self.func(*self.args, **self.kwargs)
            except:
                import traceback
                traceback.print_exc()

            Runnable.__runnables__.remove(self)

    def run_on_ui_thread(f):
        '''Decorator to create automatically a :class:`Runnable` object with the
        function. The function will be delayed and call into the Activity thread.
        '''
        def f2(*args, **kwargs):
            Runnable(f)(*args, **kwargs)
        return f2

else:
    def run_on_ui_thread(f):
        return f
#############


kv = '''
#:import Metrics kivy.metrics.Metrics

<FixedSizeButton@Button>:
    size_hint_y: None
    height: dp(60)


BoxLayout:
    orientation: 'vertical'
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
    TextInput:
        size_hint_y: None
        height: dp(100)
        text: 'textinput!'

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
        Clock.schedule_once(self.android_init, 0)
        return root

    def android_init(self, *args):
        self.set_softinput_mode()

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

    @run_on_ui_thread
    def set_softinput_mode(self):
        return
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        WindowManager = autoclass('android.view.WindowManager')
        LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
        activity = PythonActivity.mActivity

        activity.getWindow().setSoftInputMode(LayoutParams.SOFT_INPUT_ADJUST_PAN)
                    

TestApp().run()
