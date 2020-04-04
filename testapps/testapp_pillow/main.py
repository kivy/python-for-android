print("main.py was successfully called")

import os
import subprocess
from threading import Thread
from functools import partial

import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty, ListProperty

try:
    from PIL import (
        Image as PilImage,
        ImageOps,
        ImageFont,
        ImageDraw,
        ImageFilter,
        ImageChops,
    )

    status_import_pil = "Succeed"
except Exception as e1:
    print("Error on import Pil:\n{}".format(e1))
    status_import_pil = "Errored"


def start_func_thread(func, *args, **kwargs):
    """Take a function as an argument and start a thread to execute it"""
    func_thread = Thread(None, target=func, args=args, kwargs=kwargs)
    func_thread.setDaemon(True)
    func_thread.start()


def add_processed_image(image_path, evt):
    """A function that gets our running app and add the processed image we
    provide via argument to the ListProperty :attr:`TestApp.processed_images`,
    so our app can automatically display the image via kivy's events.
    """
    app = App.get_running_app()
    app.processed_images.append(image_path)


def remove_test_file_if_exist(file_name):
    """Check if the provided file (as an argument), exists and remove it in
    case that exists."""
    if os.path.isfile(file_name):
        print("\t- Removing test file: {}".format(file_name))
        subprocess.call(["rm", file_name])


def test_pil_draw(
    text_to_draw="Kivy",
    img_target="text_draw.png",
    image_width=180,
    image_height=100,
):
    """A method to test some of the `Pillow`'s package operations:

        - `Image.open`
        - `ImageDraw.Draw`
        - `ImageFont.truetype` (here we will now if our freetype's recipe
            (:class:`~pythonforandroid.recipes.freetype.FreetypeRecipe`) works
            as expected
        - `ImageFilter.GaussianBlur`
        - `Image.composite`
        - `ImageChops.invert`

    .. note:: With this test we will know if our freetype library
         (:class:`~pythonforandroid.recipes.freetype.FreetypeRecipe`) is
         working as expected because we load the default kivy's font (Roboto)
         and we use it to draw a text
    """
    print(
        "Test draw font with pil: {} [width: {}]".format(
            text_to_draw, image_width
        )
    )
    remove_test_file_if_exist(img_target)

    try:
        ttf_font = os.path.join(
            os.path.dirname(kivy.__file__),
            "data",
            "fonts",
            "Roboto-Regular.ttf",
        )
        img = PilImage.open("colours.png")
        img = img.resize((image_width, image_height), PilImage.ANTIALIAS)
        font = ImageFont.truetype(ttf_font, int(sp(55)))

        draw = ImageDraw.Draw(img)
        for n in range(2, image_width, 2):
            draw.rectangle(
                (n, n, image_width - n, image_height - n), outline="black"
            )
        img.filter(ImageFilter.GaussianBlur(radius=1.5))

        text_pos = (image_width / 2.0 - int(sp(40)), int(sp(15)))
        halo = PilImage.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(halo).text(
            text_pos, text_to_draw, font=font, fill="black"
        )
        blurred_halo = halo.filter(ImageFilter.BLUR)
        ImageDraw.Draw(blurred_halo).text(
            text_pos, text_to_draw, font=font, fill="white"
        )
        img = PilImage.composite(
            img, blurred_halo, ImageChops.invert(blurred_halo)
        )

        img.save(img_target, "PNG")
    except Exception as e:
        print("Cannot draw text with pil, error: {}".format(e))

    if os.path.isfile(img_target):
        Clock.schedule_once(partial(add_processed_image, img_target), 0.1)
    else:
        raise_error("Could not draw text with pil")


def test_pil_filter(img_source="text_draw.png", img_target="text_blur.png"):
    """A method to test `Pillows`'s `ImageFilter.GaussianBlur`."""
    print("Test pil's gaussian filter: {}".format(img_source))
    remove_test_file_if_exist(img_target)
    img = PilImage.open(img_source)
    gaussian_image = img.filter(ImageFilter.GaussianBlur(radius=1.5))
    gaussian_image.save(img_target)
    if os.path.isfile(img_target):
        Clock.schedule_once(partial(add_processed_image, img_target), 0.1)
    else:
        raise_error("Could not draw text with pil")


def test_pil_mirror(img_source="text_draw.png", img_target="text_mirror.png"):
    """A method to test `Pillows`'s `ImageOps.mirror`."""
    print("Test convert image to mirror: {}".format(img_source))
    remove_test_file_if_exist(img_target)

    try:
        im = PilImage.open(img_source)
        mirror_image = ImageOps.mirror(im)
        mirror_image.save(img_target)
    except Exception as e:
        print(
            "Cannot make mirrored image for `{}` [ERROR: {}]".format(
                img_source, e
            )
        )

    if os.path.isfile(img_target):
        Clock.schedule_once(partial(add_processed_image, img_target), 0.1)
    else:
        raise_error("Could not create a mirrored image")


def test_pil_rotate(
    img_source="text_draw.png", img_target="text_draw_rotated.png"
):
    """A method to test `Pillows`'s `Image.rotate`."""
    print("Test image rotate with image: {}".format(img_source))
    remove_test_file_if_exist(img_target)

    try:
        im = PilImage.open(img_source)
        im.rotate(180, expand=True).save(img_target, "png")
    except Exception as e:
        print("Cannot rotate image `{}` [ERROR: {}]".format(img_source, e))

    if os.path.isfile(img_target):
        Clock.schedule_once(partial(add_processed_image, img_target), 0.1)
    else:
        raise_error("Could not rotate image")


kv = """
#:import Metrics kivy.metrics.Metrics
#:import sys sys

<FixedSizeButton@Button>:
    size_hint_y: None
    height: dp(100)

ScrollView:
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height
        spacing: dp(10)
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
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            text_size: self.size[0], None
            font_size: 50
            markup: True
            text: '[color=a0a0a0]{}[/color]'.format(sys.version)
            halign: 'center'
            padding_y: dp(10)
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            font_size: 50
            text_size: self.size[0], None
            markup: True
            text:
                'dpi: [color=a0a0a0]{}[/color]\\n'\\
                'density: [color=a0a0a0]{}[/color]\\n'\\
                'fontscale: [color=a0a0a0]{}[/color]'.format(
                Metrics.dpi, Metrics.density, Metrics.fontscale)
            halign: 'center'
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            text_size: self.size[0], None
            text_color: "0c8916" if "Succeed" in self.text else "bc1607"
            font_size: 50
            markup: True
            text:
                'Import PIL module: [color={}]{}[/color]'.format(
                self.text_color, app.status_import_pil)
            halign: 'center'
        FixedSizeButton:
            text: 'test ctypes'
            on_press: app.test_ctypes()
            height: dp(60)
        FixedSizeButton:
            text: 'test pyjnius'
            on_press: app.test_pyjnius()
            height: dp(60)
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(430)
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(10)
                FixedSizeButton:
                    text: 'test Pil draw text'
                    disabled:
                        ("Error" in app.status_import_pil or app.processed_draw)
                    on_release: app.test_pil_draw()
                FixedSizeButton:
                    text: 'test Pil gaussian filter'
                    disabled: (not app.processed_draw or app.processed_filter)
                    on_release: app.test_pil_filter()
                FixedSizeButton:
                    text: 'test Pil mirror'
                    disabled: (not app.processed_filter or app.processed_mirror)
                    on_release: app.test_pil_mirror()
                FixedSizeButton:
                    text: 'test Pil rotate 180'
                    disabled: (not app.processed_mirror or app.processed_rotate)
                    on_release: app.test_pil_rotate()
            Widget:
                size_hint_x: None
                width: dp(10)
            BoxLayout:
                id: images_container
                orientation: 'vertical'
                spacing: dp(10)
                Widget:
                    size_hint_y: None
                    height: dp(430 - 110 * (len(self.parent.children) - 1))
                    canvas.before:
                        Color:
                            rgba:
                                (.1, .1, .1,
                                1 if len(self.parent.children) < 5
                                else 0)
                        Rectangle:
                            pos: self.pos[0], self.pos[1] + dp(2)
                            size: self.size
        Widget:
            size_hint_y: None
            height: dp(10)

<ErrorPopup>:
    title: 'Error' 
    size_hint: 0.75, 0.75
    Label:
        text: root.error_text
"""


class ErrorPopup(Popup):
    """A pop intended to be used to display error messages"""
    error_text = StringProperty("")


def raise_error(error):
    """Method that will take a message as an argument and will display it in a
    a Popup :class:`ErrorPopup`."""
    print("ERROR:", error)
    ErrorPopup(error_text=error).open()


class TestApp(App):
    status_import_pil = status_import_pil
    processed_draw = BooleanProperty(False)
    processed_filter = BooleanProperty(False)
    processed_rotate = BooleanProperty(False)
    processed_mirror = BooleanProperty(False)
    processed_images = ListProperty()

    def build(self):
        return Builder.load_string(kv)

    def on_pause(self):
        return True

    def on_stop(self):
        print("Removing generated test images...")
        for w in self.root.ids.images_container.children[:]:
            if hasattr(w, "source"):
                self.root.ids.images_container.remove_widget(w)
                remove_test_file_if_exist(w.source)

    def test_pyjnius(self, *args):
        try:
            from jnius import autoclass, cast
        except ImportError:
            raise_error('Could not import pyjnius')
            return
        print('Attempting to vibrate with pyjnius')
        ANDROID_VERSION = autoclass('android.os.Build$VERSION')
        SDK_INT = ANDROID_VERSION.SDK_INT

        Context = autoclass("android.content.Context")
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity

        vibrator_service = activity.getSystemService(Context.VIBRATOR_SERVICE)
        vibrator = cast("android.os.Vibrator", vibrator_service)

        if vibrator and SDK_INT >= 26:
            print("Using android's `VibrationEffect` (SDK >= 26)")
            VibrationEffect = autoclass("android.os.VibrationEffect")
            vibrator.vibrate(
                VibrationEffect.createOneShot(
                    1000, VibrationEffect.DEFAULT_AMPLITUDE,
                ),
            )
        elif vibrator:
            print("Using deprecated android's vibrate (SDK < 26)")
            vibrator.vibrate(1000)
        else:
            print('Something happened...vibrator service disabled?')

    def test_ctypes(self, *args):
        try:
            import ctypes
        except ImportError:
            raise_error("Could not import ctypes")
            return

    def test_pil_draw(self, *args):
        self.processed_draw = True
        start_func_thread(
            test_pil_draw,
            image_width=int(self.root.width / 2.0),
            image_height=int(dp(100)),
        )

    def test_pil_filter(self, *args):
        self.processed_filter = True
        start_func_thread(test_pil_filter)

    def test_pil_mirror(self, *args):
        self.processed_mirror = True
        start_func_thread(test_pil_mirror)

    def test_pil_rotate(self, *args):
        self.processed_rotate = True
        start_func_thread(test_pil_rotate)

    def on_processed_images(self, *args):
        print(
            "New processed images detected [{} image/s]".format(
                len(self.processed_images)
            )
        )
        # Display the processed images
        while self.processed_images:
            img_path = self.processed_images.pop(-1)
            print("Building image widget for: {}".format(img_path))
            im = Image(
                source=img_path,
                size_hint=(1.0, None),
                height=dp(100),
                keep_ratio=True,
                allow_stretch=True,
            )
            self.root.ids.images_container.add_widget(im, index=1)


TestApp().run()
