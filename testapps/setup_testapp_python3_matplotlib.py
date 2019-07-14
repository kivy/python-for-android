
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'requirements': 'sdl2,python3,matplotlib,pyparsing,cycler,python-dateutil,numpy,kiwisolver,kivy',
                   'blacklist-requirements': 'openssl,sqlite3',
                   'android-api': 27,
                   'ndk-api': 21,
                   'dist-name': 'matplotlib_testapp',
                   'ndk-version': '10.3.2',
                   'permission': 'VIBRATE',
                   }}

package_data = {'': ['*.py',
                     '*.png']
                }

packages = find_packages()
print('packages are', packages)

setup(
    name='matplotlib_testapp',
    version='0.1',
    description='p4a setup.py test',
    author='Alexander Taylor',
    author_email='alexanderjohntaylor@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp_matplotlib': ['*.py', '*.png']}
)
