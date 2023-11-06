"""
This is the `setup.py` file for the `on device unit test app`.

In this module we can control how will be built our test app. Depending on
our requirements we can build an kivy, flask or a non-gui app. We default to an
kivy app, since the python-for-android project its a sister project of kivy.

The parameter `requirements` is crucial to determine the unit tests we will
perform with our app, so we must explicitly name the recipe we want to test
and, of course, we should have the proper test for the given recipe at
`tests.test_requirements.py` or nothing will be tested. We control our default
app requirements via the dictionary `options`. Here you have some examples
to build the supported app modes::

  - kivy *basic*: `sqlite3,libffi,openssl,pyjnius,kivy,python3,requests,
    urllib3,chardet,idna`
  - kivy *images/graphs*: `kivy,python3,numpy,matplotlib,Pillow`
  - kivy *encryption*: `kivy,python3,cryptography,pycryptodome,scrypt,
    m2crypto,pysha3`
  - flask (with webview bootstrap): `sqlite3,libffi,openssl,pyjnius,flask,
    python3,genericndkbuild`


.. note:: just noting that, for the `kivy basic` app, we add the requirements:
          `sqlite3,libffi,openssl` so this way we will trigger the unit tests
          that we have for such recipes.

.. tip:: to force `python-for-android` generate an `flask` app without using
         the kwarg `bootstrap`, we add the recipe `genericndkbuild`, which will
         trigger the `webview bootstrap` at build time.
"""

import os
import sys

from setuptools import setup, find_packages

# define a basic test app, which can be override passing the proper args to cli
options = {
    'apk':
        {
            'requirements':
                'sqlite3,libffi,openssl,pyjnius,kivy,python3,requests,urllib3,'
                'chardet,idna',
            'android-api': 27,
            'ndk-api': 21,
            'dist-name': 'bdist_unit_tests_app',
            'arch': 'armeabi-v7a',
            'bootstrap' : 'sdl2',
            'permissions': ['INTERNET', 'VIBRATE'],
            'orientation': ['portrait', 'landscape'],
            'service': 'P4a_test_service:app_service.py',
        },
    'aab':
        {
            'requirements':
                'sqlite3,libffi,openssl,pyjnius,kivy,python3,requests,urllib3,'
                'chardet,idna',
            'android-api': 27,
            'ndk-api': 21,
            'dist-name': 'bdist_unit_tests_app',
            'arch': 'armeabi-v7a',
            'bootstrap' : 'sdl2',
            'permissions': ['INTERNET', 'VIBRATE'],
            'orientation': ['portrait', 'landscape'],
            'service': 'P4a_test_service:app_service.py',
        },
    'aar':
        {
            'requirements' : 'python3',
            'android-api': 27,
            'ndk-api': 21,
            'dist-name': 'bdist_unit_tests_app',
            'arch': 'arm64-v8a',
            'bootstrap' : 'service_library',
            'permissions': ['INTERNET', 'VIBRATE'],
            'service': 'P4a_test_service:app_service.py',
        }
}

# check if we overwrote the default test_app requirements via `cli`
requirements = options['apk']['requirements'].rsplit(',')
for n, arg in enumerate(sys.argv):
    if arg == '--requirements':
        print('found requirements')
        requirements = sys.argv[n + 1].rsplit(',')
        break

# remove `orientation` in case that we don't detect a kivy or flask app,
# since the `service_only` bootstrap does not support such argument
if not ({'kivy', 'flask'} & set(requirements)):
    options['apk'].pop('orientation')

# write a file to let the test_app know which requirements we want to test
# Note: later, when running the app, we will guess if we have the right test.
app_requirements_txt = os.path.join(
    os.path.split(__file__)[0],
    'test_app',
    'app_requirements.txt',
)
with open(app_requirements_txt, 'w') as requirements_file:
    for req in requirements:
        requirements_file.write(f'{req.split("==")[0]}\n')

# run the install
setup(
    name='unit_tests_app',
    version='1.1',
    description='p4a on device unit test app',
    author='Alexander Taylor, Pol Canelles',
    author_email='alexanderjohntaylor@gmail.com, canellestudi@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={
        'test_app': ['*.py', '*.kv', '*.txt'],
        'test_app/static': ['*.png', '*.css', '*.otf'],
        'test_app/templates': ['*.html'],
        'test_app/tests': ['*.py'],
    }
)
