from jnius import autoclass
from android import mActivity

__all__ = ('ensure_display_cutout', 'get_cutout_size', 'get_size_of_bar')


def _decorview():
    return mActivity.getWindow().getDecorView()


def get_cutout_size():
    " Get the size of the front camera "
    try:
        cutout = _decorview().rootWindowInsets.displayCutout
        rect = cutout.boundingRects.get(0)

        return float(rect.width()), float(rect.height())

    except Exception:
        return 0., 0.


def ensure_display_cutout():
    """ Ensure display cutout is taking place on newer androids
        To be used with on_start with Kivy.
        Also needs the decorator run_on_ui_thread
    """
    AndroidView = autoclass('android.view.View')
    _decorview().setSystemUiVisibility(
        AndroidView.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION |
        AndroidView.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
        AndroidView.SYSTEM_UI_FLAG_IMMERSIVE_STICKY)

    return True


def get_size_of_bar(bar_target=None):
    """ Get the size of either statusbar or navigationbar
        bar_target = status or navigation and defaults to status
    """
    bar_target = bar_target or 'status'

    if bar_target not in ('status', 'navigation'):
        raise Exception("bar_target must be 'status' or 'navigation'")

    try:
        displayMetrics = autoclass('android.util.DisplayMetrics')
        mActivity.getWindowManager().getDefaultDisplay().getMetrics(displayMetrics())
        resources = mActivity.getResources()
        resourceId = resources.getIdentifier(f'{bar_target}_bar_height', 'dimen',
                                             'android')

        return float(max(resources.getDimensionPixelSize(resourceId), 0))

    except Exception:
        return 0.
