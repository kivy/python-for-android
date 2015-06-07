from kivy.app import App

from kivy.lang import Builder
from kivy.properties import StringProperty

from kivy.uix.popup import Popup


kv = '''
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
        return root

    def on_pause(self):
        return True

    def test_pyjnius(self):
        try:
            from jnius import autoclass
        except ImportError:
            raise_error('Could not import pyjnius')
            return
        
        print('Attempting to vibrate with pyjnius')
        PythonActivity = autoclass('org.renpy.android.PythonActivity')
        activity = PythonActivity.mActivity
        Intent = autoclass('android.content.Intent')
        Context = autoclass('android.content.Context')
        vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)

        vibrator.vibrate(1000)


TestApp().run()
