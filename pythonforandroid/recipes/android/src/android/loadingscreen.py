
from jnius import autoclass

from android.config import ACTIVITY_CLASS_NAME


def hide_loading_screen():
    python_activity = autoclass(ACTIVITY_CLASS_NAME)
    python_activity.removeLoadingScreen()
