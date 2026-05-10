"""Touch interception helpers for Python for Android.

This module exposes two utilities to hook into the Android SDL surface's
intercept touch mechanism via pyjnius:

- `OnInterceptTouchListener`: a thin bridge class that implements the
  Java interface `SDLSurface.OnInterceptTouchListener` and delegates to a
  provided Python callable.
- `TouchListener`: a convenience class with helpers to register/unregister
  the intercept listener and a hit-testing routine against the Kivy
  `Window` to decide whether a touch should be consumed.
- `TouchListener.register_listener` requires a `target_widget` argument,
  which is used for hit-testing to decide whether to consume touches.
- Touch coordinates are taken from pointer index 0 and converted to Kivy's
  coordinate system by inverting Y relative to `Window.height`.

Dependencies: pyjnius for bridging to Android, and Kivy for window and
widget traversal used in hit-testing.
"""

from jnius import PythonJavaClass, java_method, autoclass
from android.config import ACTIVITY_CLASS_NAME

__all__ = ('OnInterceptTouchListener', 'TouchListener')


class OnInterceptTouchListener(PythonJavaClass):
    """Bridge for Android's `SDLSurface.OnInterceptTouchListener`.

    Instances of this class can be passed to the SDL surface so that touch
    events can be intercepted before they reach the normal Android/Kivy
    dispatch pipeline. The Python callable provided at construction time is
    invoked for each `MotionEvent` and should return a boolean indicating
    whether the touch was consumed.
    """

    __javacontext__ = 'app'
    __javainterfaces__ = [
        'org/libsdl/app/SDLSurface$OnInterceptTouchListener']

    def __init__(self, listener):
        """Create a new intercept touch listener.

        Parameters:
            listener (Callable[[object], bool]): A callable that receives the
                Android `MotionEvent` instance and returns `True` if the
                touch should be consumed (intercepted), or `False` to let it
                propagate normally.
        """
        self.listener = listener

    @java_method('(Landroid/view/MotionEvent;)Z')
    def onTouch(self, event):
        """Handle an incoming `MotionEvent`.

        Parameters:
            event: The Android `MotionEvent` object delivered by the SDL
                surface.

        Returns:
            bool: The boolean returned by the user-provided `listener`, where
            `True` indicates the event was consumed and should not propagate
            further; `False` lets normal processing continue.
        """
        return self.listener(event)


class TouchListener:
    """Convenience API to register a global Android intercept touch listener.

    This class manages a singleton instance of `OnInterceptTouchListener`
    that is attached to the app's `PythonActivity.mSurface`. It also stores
    a reference to a specific `target_widget` used during hit-testing to
    decide whether touches should be consumed.

    A small hit-testing helper walks the Kivy `Window` widget tree to
    determine whether a touch should be intercepted (consumed) or allowed to
    propagate.

    Notes:
    - The intercept listener affects the entire SDL surface and thus the
      whole app; use with care.
    - The internal `__listener` attribute stores the active listener
      instance when registered, or `None` when not set.
    - The internal `__target_widget` holds the widget against which the
      hit-test is compared and is cleared on `unregister_listener()`.
    """
    __listener = None
    __target_widget = None

    @classmethod
    def register_listener(cls, target_widget):
        """Register the global intercept touch listener if not already set.

        This creates a singleton `OnInterceptTouchListener` that delegates to
        `TouchListener._on_touch_listener` and installs it on
        `PythonActivity.mSurface` via pyjnius.

        Parameters:
            target_widget: The widget used as the reference during hit-testing.
                If the touch lands on this widget and no other widget is found
                under the touch, the event will be consumed by the intercept
                listener.
        """
        if cls.__listener:
            return
        cls.__target_widget = target_widget
        cls.__listener = OnInterceptTouchListener(cls._on_touch_listener)
        PythonActivity = autoclass(ACTIVITY_CLASS_NAME)
        PythonActivity.mSurface.setInterceptTouchListener(cls.__listener)

    @classmethod
    def unregister_listener(cls):
        """Unregister the global intercept touch listener, if any.

        Removes the previously installed listener from
        `PythonActivity.mSurface` by setting it to `None`. This does not
        modify the stored reference in `__listener`.
        """
        PythonActivity = autoclass(ACTIVITY_CLASS_NAME)
        PythonActivity.mSurface.setInterceptTouchListener(None)
        cls.__target_widget = None

    @classmethod
    def is_listener_set(cls):
        """Report whether the intercept listener reference is set.

        Returns:
            bool: `False` if a listener instance is currently stored in
            `__listener` (i.e. registered), `True` if no listener is stored.
            Note: this method reflects the current implementation which
            returns the negation of the internal reference.
        """
        return not cls.__listener

    @classmethod
    def _on_touch_listener(cls, event):
        """Default callback used by the installed intercept listener.

        What it does now (current behavior):
        - Reads touch coordinates from pointer index 0 using `event.getX(0)`
          and `event.getY(0)`.
        - Converts Android coordinates to Kivy coordinates by inverting the Y
          axis relative to `Window.height`.
        - Iterates over `Window.children` in reverse (front-to-back) and uses
          `TouchListener._pick` to select the deepest widget under the touch
          for each top-level child.
        - Compares the picked widget with the internally stored
          `__target_widget` that was provided to `register_listener(...)`.
        - Returns `True` (consume/intercept) only when the picked widget is
          exactly `__target_widget` and no other widget was found under the
          touch. Otherwise returns `False`.

        Important notes and limitations:
        - There is no filtering by MotionEvent action; all actions reaching
          this callback are evaluated the same way.
        - Only pointer index 0 is considered; multi-touch pointers other than
          index 0 are ignored.
        - The check is identity-based (`is`) against `__target_widget`.
        - If another widget (other than `__target_widget`) is hit, the event
          is not intercepted and will propagate normally.

        Parameters:
            event: The Android `MotionEvent` that triggered the listener.

        Returns:
            bool: `True` to consume the touch when the hit-test selects the
            `__target_widget` and no other widget is found; otherwise `False`
            to allow normal dispatch.
        """
        from kivy.core.window import Window

        x = event.getX(0)
        y = event.getY(0)

        # invert Y !
        y = Window.height - y
        # x, y are in Window coordinate. Try to select the widget under the
        # touch.
        me = None
        for child in reversed(Window.children):
            widget = cls._pick(child, x, y)
            if not widget:
                continue
            if cls.__target_widget is widget:
                me = widget
                # keep scanning to ensure no other widget is hit
                continue
            # any non-target hit means we should not intercept
            return False
        return cls.__target_widget is me

    @classmethod
    def _pick(cls, widget, x, y):
        """Pick the deepest child widget at coordinates.

        Parameters:
            widget: The root widget from which to start the search.
            x (float): X coordinate in the local space of `widget`.
            y (float): Y coordinate in the local space of `widget`.

        Returns:
            The deepest child that collides with the given point, or the
            highest-level `widget` itself if it collides and no deeper child
            does; otherwise `None` if no collision.
        """
        # Fast exit if the root doesn't collide
        if not widget.collide_point(x, y):
            return None

        # Always descend through the first colliding child in z-order
        current = widget
        lx, ly = x, y
        while True:
            # Transform coordinates once per level
            nlx, nly = current.to_local(lx, ly)
            hit_child = None
            for child in reversed(current.children):
                if child.collide_point(nlx, nly):
                    # keep the last colliding child in this order, matching
                    # the original recursive implementation's semantics
                    hit_child = child
            if hit_child is None:
                # No deeper child collides; current is the deepest hit
                return current
            # Prepare for next level using parent's local coords; we'll
            # convert again at the next iteration relative to the new
            # current widget.
            lx, ly = nlx, nly
            # Continue descent into the chosen child
            current = hit_child
