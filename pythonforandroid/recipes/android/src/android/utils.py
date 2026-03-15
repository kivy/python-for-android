from android import mActivity
from android.runnable import run_on_ui_thread
from jnius import autoclass, java_method, PythonJavaClass
from typing import Literal

__all__ = ("update_system_ui")


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
        __javainterfaces__ = [
            "android/view/View$OnApplyWindowInsetsListener"
        ]
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
                status_insets = insets.getInsets(
                    WindowInsetsType.statusBars()
                )
                nav_insets = insets.getInsets(
                    WindowInsetsType.navigationBars()
                )

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

    _global_listener: InsetsListener

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
    if (Build_VERSION.SDK_INT >= 30):
        # API 30+ (Android 10+)
        if inset_controller and "WindowInsetsControllerCompat" in str(type(inset_controller)):
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
        _global_listener = InsetsListener(status_color_int, navigation_color_int, pad_status, pad_nav)
        decor_view.setOnApplyWindowInsetsListener(_global_listener)
        decor_view.requestApplyInsets()
    else:
        window.setStatusBarColor(status_color_int)
        window.setNavigationBarColor(navigation_color_int)
