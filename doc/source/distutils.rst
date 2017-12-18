
distutils/setuptools integration
================================

Instead of running p4a via the command line, you can integrate with
distutils and setup.py.

The base command is::

    python setup.py apk

The files included in the APK will be all those specified in the
``package_data`` argument to setup. For instance, the following
example will include all .py and .png files in the ``testapp``
folder::

    from distutils.core import setup
    from setuptools import find_packages

    setup(
        name='testapp_setup',
        version='1.1',
        description='p4a setup.py example',
        author='Your Name',
        author_email='youremail@address.com',
        packages=find_packages(),
        options=options,
        package_data={'testapp': ['*.py', '*.png']}
    )

The app name and version will also be read automatically from the
setup.py.

The Android package name uses ``org.test.lowercaseappname``
if not set explicitly.

The ``--private`` argument is set automatically using the
package_data, you should *not* set this manually.

The target architecture defaults to ``--armeabi``.

All of these automatic arguments can be overridden by passing them manually on the command line, e.g.::

    python setup.py apk --name="Testapp Setup" --version=2.5

Adding p4a arguments in setup.py
--------------------------------

Instead of providing extra arguments on the command line, you can
store them in setup.py by passing the ``options`` parameter to
:code:`setup`. For instance::

    from distutils.core import setup
    from setuptools import find_packages

    options = {'apk': {'debug': None,  # use None for arguments that don't pass a value
                       'requirements': 'sdl2,pyjnius,kivy,python2',
                       'android-api': 19,
                       'ndk-dir': '/path/to/ndk',
                       'dist-name': 'bdisttest',
                       }}

    packages = find_packages()
    print('packages are', packages)

    setup(
        name='testapp_setup',
        version='1.1',
        description='p4a setup.py example',
        author='Your Name',
        author_email='youremail@address.com',
        packages=find_packages(),
        options=options,
        package_data={'testapp': ['*.py', '*.png']}
    )

These options will be automatically included when you run ``python
setup.py apk``. Any options passed on the command line will override
these values.

Adding p4a arguments in setup.cfg
---------------------------------

You can also provide p4a arguments in the setup.cfg file, as normal
for distutils. The syntax is::

    [apk]

    argument=value

    requirements=sdl2,kivy
