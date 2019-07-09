
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'debug': None,
                   'requirements': 'sdl2,pyjnius,kivy,python3',
                   'blacklist-requirements': 'openssl,sqlite3',
                   'android-api': 27,
                   'ndk-api': 21,
                   'ndk-dir': '/home/asandy/android/android-ndk-r17c',
                   'dist-name': 'bdisttest',
                   'ndk-version': '10.3.2',
                   'permission': 'VIBRATE',
                   }}

package_data = {'': ['*.py',
                     '*.png']
                }

packages = find_packages()
print('packages are', packages)

setup(
    name='testapp_keyboard',
    version='1.1',
    description='p4a setup.py test',
    author='Alexander Taylor',
    author_email='alexanderjohntaylor@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'setup_keyboard': ['*.py', '*.png']}
)
