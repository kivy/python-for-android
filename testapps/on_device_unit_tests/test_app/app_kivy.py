# -*- coding: utf-8 -*-

import subprocess

from os.path import split

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    ListProperty,
    StringProperty,
)
from kivy.lang import Builder

from constants import RUNNING_ON_ANDROID
from tools import (
    get_android_python_activity,
    get_failed_unittests_from,
    get_images_with_extension,
    load_kv_from,
    raise_error,
    run_test_suites_into_buffer,
    setup_lifecycle_callbacks,
    vibrate_with_pyjnius,
)
from widgets import TestImage

# define our app's screen manager and load the screen templates
screen_manager_app = '''
ScreenManager:
    ScreenUnittests:
    ScreenKeyboard:
    ScreenOrientation:
    ScreenService:
'''
load_kv_from('screen_unittests.kv')
load_kv_from('screen_keyboard.kv')
load_kv_from('screen_orientation.kv')
load_kv_from('screen_service.kv')


class TestKivyApp(App):

    tests_to_perform = DictProperty()
    unittest_error_text = StringProperty('Running unittests...')
    test_packages = StringProperty('Unittest recipes:')
    generated_images = ListProperty()
    service_running = BooleanProperty(False)

    def build(self):
        self.reset_unittests_results()
        self.sm = Builder.load_string(screen_manager_app)
        return self.sm

    def on_start(self):
        setup_lifecycle_callbacks()

    def reset_unittests_results(self, refresh_ui=False):
        for img in get_images_with_extension():
            subprocess.call(["rm", "-r", img])
            print('removed image: ', img)
        if refresh_ui:
            self.set_color_for_tested_modules(restart=True)
            self.unittest_error_text = ''
            screen_unittests = self.sm.get_screen('unittests')
            images_box = screen_unittests.ids.test_images_box
            images_box.clear_widgets()
            self.generated_images = []

    def on_tests_to_perform(self, *args):
        """
        Check `test_to_perform` so we can build some special tests in our ui.
        Also will schedule the run of our tests.
        """
        print('on_tests_to_perform: ', self.tests_to_perform.keys())
        self.set_color_for_tested_modules(restart=True)
        Clock.schedule_once(self.run_unittests, 3)

    def run_unittests(self, *args):
        import unittest
        print('Imported unittest')

        print("loading tests...")
        suites = unittest.TestLoader().loadTestsFromNames(
            list(self.tests_to_perform.values()),
        )
        self.test_packages = ', '.join(self.tests_to_perform.keys())

        print("running unittest...")
        self.unittest_error_text = run_test_suites_into_buffer(suites)

        print("unittest result is:")
        print(self.unittest_error_text)
        print('Ran tests')

        self.set_color_for_tested_modules()

        # check generated images by unittests
        self.generated_images = get_images_with_extension()

    def set_color_for_tested_modules(self, restart=False):
        tests_made = sorted(list(self.tests_to_perform.keys()))
        failed_tests = get_failed_unittests_from(
            self.unittest_error_text,
            self.tests_to_perform.values(),
        )

        modules_text = 'Unittest recipes: '
        for n, module in enumerate(tests_made):
            base_text = '[color={color}]{module}[/color]'
            if restart:
                color = '#838383'  # grey
            elif self.tests_to_perform[module] in failed_tests:
                color = '#ff0000'  # red
            else:
                color = '#5d8000'  # green
            if n != len(tests_made) - 1:
                base_text += ', '

            modules_text += base_text.format(color=color, module=module)

        self.test_packages = modules_text

    def on_generated_images(self, *args):
        screen_unittests = self.sm.get_screen('unittests')
        images_box = screen_unittests.ids.test_images_box
        for i in self.generated_images:
            img = TestImage(
                text='Generated image by unittests: {}'.format(split(i)[1]),
                source=i,
            )
            images_box.add_widget(img)

    def test_vibration_with_pyjnius(self, *args):
        vibrate_with_pyjnius()

    @property
    def service_time(self):
        from jnius import autoclass

        return autoclass('org.test.unit_tests_app.ServiceP4a_test_service')

    def on_service_running(self, *args):
        if RUNNING_ON_ANDROID:
            if self.service_running:
                print('Starting service')
                self.start_service()
            else:
                print('Stopping service')
                self.stop_service()
        else:
            raise_error('Service test not supported on desktop')

    def start_service(self):
        activity = get_android_python_activity()
        service = self.service_time
        try:
            service.start(activity, 'Some argument')
        except Exception as err:
            raise_error(str(err))

    def stop_service(self):
        service = self.service_time
        activity = get_android_python_activity()
        service.stop(activity)
