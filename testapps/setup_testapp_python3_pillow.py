
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'requirements': 'harfbuzz,sdl2,pillow,kivy,python3',
                   'blacklist-requirements': 'sqlite3',
                   'android-api': 27,
                   'ndk-api': 21,
                   'dist-name': 'pillow_testapp',
                   'arch': 'armeabi-v7a',
                   'permissions': ['VIBRATE'],
                   }}

package_data = {'': ['*.py',
                     '*.png']
                }

setup(
    name='testapp_pillow',
    version='1.0',
    description='p4a setup.py test',
    author='Pol Canelles',
    author_email='canellestudi@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp_pillow': ['*.py', '*.png', '*.ttf']}
)
