
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'requirements': 'sdl2,pyjnius,kivy,python2legacy,'
                                   'openssl,requests,peewee,sqlite3',
                   'android-api': 27,
                   'ndk-api': 19,
                   'ndk-dir': '/home/sandy/android/crystax-ndk-10.3.2',
                   'dist-name': 'bdisttest_python2legacy_sqlite_openssl',
                   'ndk-version': '10.3.2',
                   'permissions': ['INTERNET', 'VIBRATE'],
                   'arch': 'armeabi-v7a',
                   'window': None,
                   }}

setup(
    name='testapp_python2legacy_sqlite_openssl',
    version='1.1',
    description='p4a setup.py test',
    author='Pol Canelles',
    author_email='canellestudi@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp_sqlite_openssl': ['*.py', '*.png']}
)
