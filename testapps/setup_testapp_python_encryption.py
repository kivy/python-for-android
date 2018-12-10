
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'requirements': 'libffi,openssl,sdl2,pyjnius,kivy,python2,'
                                   'cryptography,pycrypto,scrypt,libtorrent',
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

packages = find_packages()
print('packages are', packages)

setup(
    name='testapp_encryption',
    version='1.0',
    description='p4a setup.py test',
    author='Alexander Taylor',
    author_email='alexanderjohntaylor@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp_encryption': ['*.py', '*.png']}
)
