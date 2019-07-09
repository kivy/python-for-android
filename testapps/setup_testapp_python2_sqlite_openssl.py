
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'requirements': 'sdl2,pyjnius,kivy,python2,openssl,requests,peewee,sqlite3',
                   'android-api': 27,
                   'ndk-api': 21,
                   'ndk-dir': '/home/sandy/android/android-ndk-r17c',
                   'dist-name': 'bdisttest_python2_sqlite_openssl',
                   'ndk-version': '10.3.2',
                   'permissions': ['INTERNET', 'VIBRATE'],
                   'arch': 'armeabi-v7a',
                   'window': None,
                   }}

setup(
    name='testapp_python2_sqlite_openssl',
    version='1.1',
    description='p4a setup.py test',
    author='Alexander Taylor',
    author_email='alexanderjohntaylor@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp_sqlite_openssl': ['*.py', '*.png']}
)
