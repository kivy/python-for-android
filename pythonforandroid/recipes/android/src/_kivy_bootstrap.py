"""python-for-android's implementation of Kivy's Android bootstrap contract.

Kivy 3 holds no bootstrap class name of its own: it imports ``_kivy_bootstrap``
and asks it for the current ``android.app.Activity`` instead.  Kivy pulls on
first use rather than having the bootstrap register at startup, which suits p4a:
``start.c`` runs the user's ``main.py`` as the process entry point, so there is
no p4a-owned Python before the app to register from.  It also means p4a never
imports Kivy, which would otherwise fix Kivy's ``KIVY_*`` environment and config
before the app had a chance to set them.

The activity class comes from the build-time generated ``android.config``, so a
custom activity set with ``--activity-class-name`` is honoured rather than
assumed to be the default.

Besides the required ``get_activity()``, this implements the contract's optional
``remove_presplash()``.  ``get_context()`` is not implemented: p4a's Activity can
always supply the Application context, and Kivy falls back to deriving it.

This module deliberately holds no state beyond the resolved class: the Activity
is read fresh on every call, so it stays correct across the recreation Android
performs on rotation, configuration changes and process death.
"""

from jnius import autoclass

from android.config import ACTIVITY_CLASS_NAME

_activity_class = None


def get_activity():
    """Return the current ``android.app.Activity``, or ``None`` if there is none.

    ``None`` is a legitimate answer — a p4a service runs without an Activity.
    """
    global _activity_class
    if _activity_class is None:
        # Resolved on first use rather than at import so that reflection
        # failures surface from the call, not from Kivy's discovery import.
        _activity_class = autoclass(ACTIVITY_CLASS_NAME)
    return _activity_class.mActivity


def remove_presplash():
    """Dismiss the loading screen, if this build has one.

    Kivy calls this once it has drawn its first frame — the moment only Kivy
    knows.  How the splash goes away is p4a's business: here it means removing
    the View that ``PythonActivity`` laid over the app, which the Java method
    marshals onto the UI thread itself, so there is nothing to arrange here.

    Not every p4a build has a splash to remove: ``service_only`` has no
    ``removeLoadingScreen`` at all, and a custom ``--activity-class-name`` need
    not inherit one.  So the activity is asked, rather than a hardcoded list of
    bootstraps consulted — that list has already drifted once, ``android``'s own
    ``remove_presplash`` being gated to sdl2/sdl3 though the webview activity has
    the method too.  Doing nothing is a valid outcome and Kivy treats it as one.
    """
    activity = get_activity()
    if activity is None:
        return
    remove = getattr(activity, "removeLoadingScreen", None)
    if remove is not None:
        remove()
