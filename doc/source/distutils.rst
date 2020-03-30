
distutils/setuptools integration
================================

Have `p4a apk` run setup.py (replaces ``--requirements``)
---------------------------------------------------------

If your project has a `setup.py` file, then it can be executed by
`p4a` when your app is packaged such that your app properly ends up
in the packaged site-packages. (Use ``--use-setup-py`` to enable this,
``--ignore-setup-py`` to prevent it)

This is functionality to run **setup.py INSIDE `p4a apk`,** as opposed
to the other section below, which is about running
*p4a inside setup.py*.

This however has these caveats:

- **Only your ``main.py`` from your app's ``--private`` data is copied
  into the .apk!** Everything else needs to be installed by your
  ``setup.py`` into the site-packages, or it won't be packaged.

- All dependencies that map to recipes can only be pinned to exact
  versions, all other constraints will either just plain not work
  or even cause build errors. (Sorry, our internal processing is
  just not smart enough to honor them properly at this point)

- The dependency analysis at the start may be quite slow and delay
  your build

Reasons why you would want to use a `setup.py` to be processed (and
omit specifying ``--requirements``):

- You want to use a more standard mechanism to specify dependencies
  instead of ``--requirements``

- You already use a `setup.py` for other platforms

- Your application imports itself
  in a way that won't work unless installed to site-packages)


Reasons **not** to use a `setup.py` (that is to use the usual
``--requirements`` mechanism instead):

- You don't use a `setup.py` yet, and prefer the simplicity of
  just specifying ``--requirements``

- Your `setup.py` assumes a desktop platform and pulls in
  Android-incompatible dependencies, and you are not willing
  to change this, or you want to keep it separate from Android
  deployment for other organizational reasons

- You need data files to be around that aren't installed by
  your `setup.py` into the site-packages folder


Use your setup.py to call p4a
-----------------------------

Instead of running p4a via the command line, you can call it via
`setup.py` instead, by it integrating with distutils and setup.py.

This is functionality to run **p4a INSIDE setup.py,** as opposed
to the other section above, which is about running
*setup.py inside `p4a apk`*.

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
package_data. You should *not* set this manually.

The target architecture defaults to ``--armeabi``.

All of these automatic arguments can be overridden by passing them manually on the command line, e.g.::

    python setup.py apk --name="Testapp Setup" --version=2.5

Adding p4a arguments in setup.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of providing extra arguments on the command line, you can
store them in setup.py by passing the ``options`` parameter to
:code:`setup`. For instance::

    from distutils.core import setup
    from setuptools import find_packages

    options = {'apk': {'debug': None,  # use None for arguments that don't pass a value
                       'requirements': 'sdl2,pyjnius,kivy,python3',
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also provide p4a arguments in the setup.cfg file, as normal
for distutils. The syntax is::

    [apk]

    argument=value

    requirements=sdl2,kivy
