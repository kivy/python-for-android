from typing import Callable

from jnius import PythonJavaClass, java_method, autoclass
from android.config import ACTIVITY_CLASS_NAME, ACTIVITY_CLASS_NAMESPACE

_listener = None


class DarkModeListener(PythonJavaClass):
    """
    A listener class for detecting and handling dark mode changes.

    This class implements the `DarkModeListener` interface in a Python-Java
    hybrid context through Kivy Android functionality. It listens for changes
    in the system's dark mode settings and executes a callback upon detecting
    a change.

    Attributes:
        on_dark_mode_changed (Callable[[bool], None]): A callback function to
            handle the event when dark mode status changes. The callback
            receives a single parameter `is_dark_mode`, which is a boolean
            indicating whether dark mode is currently enabled.
    """
    __javacontext__ = "app"
    __javainterfaces__ = ["org/kivy/android/PythonActivity$DarkModeListener"]

    def __init__(self, on_dark_mode_changed: Callable[[bool], None]):
        self.on_dark_mode_changed = on_dark_mode_changed

    @java_method("(Z)V")
    def onDarkModeChanged(self, is_dark_mode):
        self.on_dark_mode_changed(is_dark_mode)


def set_dark_mode_listener(on_dark_mode_changed: Callable[[bool], None] | None) -> None:
    """
    Sets a listener to monitor changes in the dark mode state.

    This function assigns a provided callback to handle changes in the
    dark mode settings. The callback will be invoked with a boolean
    argument indicating the current dark mode state.

    Args:
        on_dark_mode_changed: A callable that accepts a single boolean
            parameter indicating whether dark mode is active.

    Returns:
        None
    """
    global _listener
    activity = autoclass(ACTIVITY_CLASS_NAME).mActivity
    if on_dark_mode_changed:
        _listener = DarkModeListener(on_dark_mode_changed)
        activity.setDarkModeListener(_listener)
    else:
        activity.setDarkModeListener(on_dark_mode_changed)
        _listener = None
