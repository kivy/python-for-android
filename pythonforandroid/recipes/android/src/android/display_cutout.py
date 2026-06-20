from android import mActivity
from android.runnable import run_on_ui_thread
from jnius import autoclass, java_method, PythonJavaClass
from typing import Literal

from kivy.core.window import Window

__all__ = (
    "get_cutout_pos",
    "get_cutout_size",
    "get_width_of_bar",
    "get_height_of_bar",
    "get_size_of_bar",
    "get_width_of_bar",
    "get_cutout_mode",
    "update_system_ui",
)

Color = autoclass("android.graphics.Color")
Build_VERSION = autoclass("android.os.Build$VERSION")
WindowInsetsType = autoclass("android.view.WindowInsets$Type")
View = autoclass("android.view.View")
window = mActivity.getWindow()
decor_view = window.getDecorView()
content_view = window.findViewById(autoclass("android.R$id").content)


def parse_color(value):
    if isinstance(value, str):
        return Color.parseColor(value)
    elif isinstance(value, (list, tuple)) and len(value) == 4:
        r, g, b, a = value
        return Color.argb(a, r, g, b)
    else:
        raise ValueError("Color must be hex string or RGBA tuple")


# Oops!! android 15+ needs a listener
if Build_VERSION.SDK_INT >= 35:

    class InsetsListener(PythonJavaClass):
        __javainterfaces__ = ["android/view/View$OnApplyWindowInsetsListener"]
        __javacontext__ = "app"

        def __init__(self, status_color, navigation_color, pad_status, pad_nav):
            super().__init__()
            self.status_color = status_color
            self.navigation_color = navigation_color
            self.pad_status = pad_status
            self.pad_nav = pad_nav

        @java_method(
            "(Landroid/view/View;Landroid/view/WindowInsets;)Landroid/view/WindowInsets;"
        )
        def onApplyWindowInsets(self, view, insets):
            try:
                status_insets = insets.getInsets(WindowInsetsType.statusBars())
                nav_insets = insets.getInsets(WindowInsetsType.navigationBars())

                top_pad = status_insets.top if self.pad_status else 0
                bottom_pad = nav_insets.bottom if self.pad_nav else 0

                content_view.setPadding(0, top_pad, 0, bottom_pad)
                content_view.setBackgroundColor(self.status_color)

                window.setNavigationBarColor(self.navigation_color)
            except Exception as e:
                print("Insets error:", e)
                import traceback

                traceback.print_exc()
            return insets

    _global_listener: InsetsListener = None


def _core_cutout():
    decorview = mActivity.getWindow().getDecorView()
    cutout = decorview.rootWindowInsets.displayCutout

    return cutout.boundingRects.get(0)


def get_cutout_pos():
    """Get position of the display-cutout.
    Returns integer for each positions (xy)
    """
    try:
        cutout = _core_cutout()
        return int(cutout.left), int(Window.height - cutout.height())
    except Exception:
        # Doesn't have a camera builtin with the display
        return 0, 0


def get_cutout_size():
    """Get the size (xy) of the front camera.
    Returns size with float values
    """
    try:
        cutout = _core_cutout()
        return float(cutout.width()), float(cutout.height())
    except Exception:
        # Doesn't have a camera builtin with the display
        return 0.0, 0.0


def get_height_of_bar(bar_target=None):
    """Get the height of either statusbar or navigationbar
    bar_target = status or navigation and defaults to status
    """
    bar_target = bar_target or "status"

    if bar_target not in ("status", "navigation"):
        raise Exception("bar_target must be 'status' or 'navigation'")

    try:
        displayMetrics = autoclass("android.util.DisplayMetrics")
        mActivity.getWindowManager().getDefaultDisplay().getMetrics(displayMetrics())
        resources = mActivity.getResources()
        resourceId = resources.getIdentifier(
            f"{bar_target}_bar_height", "dimen", "android"
        )

        return float(max(resources.getDimensionPixelSize(resourceId), 0))
    except Exception:
        # Getting the size is not supported on older Androids
        return 0.0


def get_width_of_bar(bar_target=None):
    """Get the width of the bar"""
    return Window.width


def get_size_of_bar(bar_target=None):
    """Get the size of either statusbar or navigationbar
    bar_target = status or navigation and defaults to status
    """
    return get_width_of_bar(), get_height_of_bar(bar_target)


def get_heights_of_both_bars():
    """Return heights of both bars"""
    return get_height_of_bar("status"), get_height_of_bar("navigation")


def get_cutout_mode():
    """Return mode for cutout supported applications"""
    BuildVersion = autoclass("android.os.Build$VERSION")
    cutout_modes = {}

    if BuildVersion.SDK_INT >= 28:
        LayoutParams = autoclass("android.view.WindowManager$LayoutParams")
        window = mActivity.getWindow()
        layout_params = window.getAttributes()
        cutout_mode = layout_params.layoutInDisplayCutoutMode
        cutout_modes.update(
            {
                LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_DEFAULT: "default",
                LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES: "shortEdges",
            }
        )

        if BuildVersion.SDK_INT >= 30:
            cutout_modes[LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS] = "always"

        return cutout_modes.get(cutout_mode, "never")

    return None


@run_on_ui_thread
def set_immersive_mode(hide_nav=True, hide_status=True, disable_contrast=True):
    """
    Configures Android UI visibility, optionally hiding the navigation and status bars,
    and optionally disabling system bar contrast on Android Q (API 29+).
    """
    if not mActivity:
        return

    window = mActivity.getWindow()
    decor_view = window.getDecorView()

    ui_flags = View.SYSTEM_UI_FLAG_LAYOUT_STABLE

    if hide_nav:
        ui_flags |= View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
        ui_flags |= View.SYSTEM_UI_FLAG_HIDE_NAVIGATION

    if hide_status:
        ui_flags |= View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
        ui_flags |= View.SYSTEM_UI_FLAG_FULLSCREEN

    if hide_nav or hide_status:
        ui_flags |= View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY

    decor_view.setSystemUiVisibility(ui_flags)

    if disable_contrast and Build_VERSION.SDK_INT >= 29:
        window.setNavigationBarContrastEnforced(False)
        window.setStatusBarContrastEnforced(False)


@run_on_ui_thread
def update_system_ui(
    status_bar_color: list[float] | str,
    navigation_bar_color: list[float] | str,
    icon_style: Literal["Light", "Dark"] = "Dark",
    pad_status: bool = True,
    pad_nav: bool = False,
) -> None:
    """
    Provides control of colors for the status and navigation bar and also handle insets padding on Android 15 and above.

    For `status_bar_color` and `navigation_bar_color` either provide a hex color code or rgba (tuple or list) values.
    `pad_status` and `pad_nav` will take effect only above Android 15.
    IF `icon_style` IS `Dark` THE ICONS WILL BE DARK.
    IF `icon_style` IS `Light` THE ICONS WILL BE LIGHT.

    Adapted from https://github.com/CarbonKivy/CarbonKivy/blob/39e360314a3885f3b462add4475e6c609b5bef53/carbonkivy/utils.py#L43
    """

    try:
        WindowCompat = autoclass("androidx.core.view.WindowCompat")
        inset_controller = WindowCompat.getInsetsController(window, decor_view)
    except Exception:
        inset_controller = None

    status_color_int = parse_color(status_bar_color)
    navigation_color_int = parse_color(navigation_bar_color)

    # Beleive me, I once drew `dark icons over dark` and `light icons over light` but this won't happen ever again!
    if Build_VERSION.SDK_INT >= 30:
        # API 30+ (Android 10+)
        if inset_controller and "WindowInsetsControllerCompat" in str(
            type(inset_controller)
        ):
            # Compat wrapper (AndroidX)
            # I suggest to include androidx in builds, it actually helps!
            if icon_style == "Light":
                inset_controller.setAppearanceLightStatusBars(False)
                inset_controller.setAppearanceLightNavigationBars(False)
            else:
                inset_controller.setAppearanceLightStatusBars(True)
                inset_controller.setAppearanceLightNavigationBars(True)
        else:
            # Platform controller
            controller = window.getInsetsController()
            WindowInsetsController = autoclass("android.view.WindowInsetsController")
            if icon_style == "Light":
                controller.setSystemBarsAppearance(
                    0,
                    WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS
                    | WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS,
                )
            else:
                controller.setSystemBarsAppearance(
                    WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS
                    | WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS,
                    WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS
                    | WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS,
                )
    else:
        # Legacy flags for API 23–29
        # Yepp, python3.14 with ndk 28c doesn't support building for android <= 11 with 32 bit armeabi-v7a cpu so this may never be called but who knows??
        visibility_flags = decor_view.getSystemUiVisibility()

        if icon_style == "Light":
            visibility_flags &= ~View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
            if Build_VERSION.SDK_INT >= 26:
                visibility_flags &= ~View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR
        else:
            visibility_flags |= View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
            if Build_VERSION.SDK_INT >= 26:
                visibility_flags |= View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR

        decor_view.setSystemUiVisibility(visibility_flags)

    if Build_VERSION.SDK_INT >= 35:
        # I don't know why but sometimes pyjnius failed to find invoke, maybe due to garbage collection and so I made a reference
        global _global_listener
        _global_listener = InsetsListener(
            status_color_int, navigation_color_int, pad_status, pad_nav
        )
        decor_view.setOnApplyWindowInsetsListener(_global_listener)
        decor_view.requestApplyInsets()
    else:
        window.setStatusBarColor(status_color_int)
        window.setNavigationBarColor(navigation_color_int)
