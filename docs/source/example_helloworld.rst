Hello world
-----------

If you don't know how to start with Python for Android, here is a simple
tutorial for creating an UI using `Kivy <http://kivy.org/>`_, and make an APK
with this project.

.. note::

    Don't forget that Python for Android is not Kivy only, and you
    might want to use other toolkit libraries. When other toolkits
    will be available, this documentation will be enhanced.

Let's create a simple Hello world application, with one Label and one Button.

#. Ensure you've correctly installed and configured the project as said in the
   :doc:`prerequisites`

#. Create a directory named ``helloworld``::

    mkdir helloworld
    cd helloworld

#. Create a file named ``main.py``, with this content::

    import kivy
    kivy.require('1.0.9')
    from kivy.lang import Builder
    from kivy.uix.gridlayout import GridLayout
    from kivy.properties import NumericProperty
    from kivy.app import App

    Builder.load_string('''
    <HelloWorldScreen>:
        cols: 1
        Label:
            text: 'Welcome to the Hello world'
        Button:
            text: 'Click me! %d' % root.counter
            on_release: root.my_callback()
    ''')

    class HelloWorldScreen(GridLayout):
        counter = NumericProperty(0)
        def my_callback(self):
            print 'The button has been pushed'
            self.counter += 1

    class HelloWorldApp(App):
        def build(self):
            return HelloWorldScreen()

    if __name__ == '__main__':
        HelloWorldApp().run()

#. Go to the ``python-for-android`` directory

#. Create a distribution with kivy::

    ./distribute.sh -m kivy

#. Go to the newly created ``default`` distribution::

    cd dist/default

#. Plug your android device, and ensure you can install development
   application

#. Build your hello world application in debug mode::

    ./build.py --package org.hello.world --name "Hello world" \
    --version 1.0 --dir /PATH/TO/helloworld debug installd

#. Take your device, and start the application!

#. If something goes wrong, open the logcat by doing::

    adb logcat

The final debug APK will be located in ``bin/hello-world-1.0-debug.apk``.

If you want to release your application instead of just making a debug APK, you must:

#. Generate a non-signed APK::

    ./build.py --package org.hello.world --name "Hello world" \
    --version 1.0 --dir /PATH/TO/helloworld release

#. Continue by reading http://developer.android.com/guide/publishing/app-signing.html


.. seealso::

    `Kivy demos <https://github.com/kivy/kivy/tree/master/examples/demo>`_
        You can use them for creating APK too.

