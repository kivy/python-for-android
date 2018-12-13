
from jnius import autoclass


def hide_loading_screen():
    python_activity = autoclass('org.kivy.android.PythonActivity')
    python_activity.removeLoadingScreen()
