
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'requirements': 'sdl2,pyjnius,kivy,python2,openssl,requests,peewee,sqlite3',
                   'android-api': 19,
                   'ndk-api': 19,
                   'ndk-dir': '/home/sandy/android/crystax-ndk-10.3.2',
                   'dist-name': 'bdisttest_python2_sqlite_openssl',
                   'ndk-version': '10.3.2',
                   'permission': 'VIBRATE',
                   'permission': 'INTERNET',
                   'arch': 'armeabi-v7a',
                   'window': None,
                   }}

packages = find_packages()
print('packages are', packages)

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
