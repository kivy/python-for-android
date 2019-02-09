
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'requirements': 'sdl2,pyjnius,kivy,python3,cryptography,'
                                   'pycrypto,scrypt,m2crypto,pysha3,'
                                   'pycryptodome,libtorrent',
                   'blacklist-requirements': 'sqlite3',
                   'android-api': 27,
                   'ndk-api': 21,
                   'dist-name': 'bdisttest_encryption',
                   'ndk-version': '10.3.2',
                   'arch': 'armeabi-v7a',
                   'permissions': ['INTERNET', 'VIBRATE'],
                   }}

package_data = {'': ['*.py',
                     '*.png']
                }

setup(
    name='testapp_encryption',
    version='1.0',
    description='p4a setup.py test',
    author='Pol Canelles',
    author_email='canellestudi@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp_encryption': ['*.py', '*.png']}
)
