
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'requirements': 'sdl2,pyjnius,kivy,python3crystax',
                   'android-api': 19,
                   'ndk-api': 19,
                   'ndk-dir': '/home/asandy/android/crystax-ndk-10.3.2',
                   'dist-name': 'bdisttest_python3',
                   'ndk-version': '10.3.2',
                   'arch': 'armeabi-v7a',
                   'permission': 'VIBRATE',
                   }}

package_data = {'': ['*.py',
                     '*.png']
                }

packages = find_packages()
print('packages are', packages)

setup(
    name='testapp_python3',
    version='1.1',
    description='p4a setup.py test',
    author='Alexander Taylor',
    author_email='alexanderjohntaylor@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp': ['*.py', '*.png']}
)
