from setuptools import setup, find_packages

options = {'apk': {'requirements': 'requests,peewee,sdl2,pyjnius,kivy,python3',
                   'android-api': 27,
                   'ndk-api': 21,
                   'bootstrap': 'sdl2',
                   'dist-name': 'bdisttest_python3_sqlite_openssl_googlendk',
                   'ndk-version': '10.3.2',
                   'arch': 'armeabi-v7a',
                   'permissions': ['INTERNET', 'VIBRATE'],
                   }}

setup(
    name='testapp_python3_sqlite_openssl_googlendk',
    version='1.1',
    description='p4a setup.py test',
    author='Alexander Taylor',
    author_email='alexanderjohntaylor@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp_sqlite_openssl': ['*.py', '*.png']}
)
