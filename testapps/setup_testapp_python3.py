
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'requirements': 'sdl2,numpy,pyjnius,kivy,python3,hostpython3',
                   'blacklist-requirements': 'openssl,sqlite3',
                   'android-api': 27,
                   'ndk-api': 21,
                   'dist-name': 'bdisttest_python3_googlendk',
                   'ndk-version': '10.3.2',
                   'permission': 'VIBRATE',
                   }}

package_data = {'': ['*.py',
                     '*.png']
                }

packages = find_packages()
print('packages are', packages)

setup(
    name='python3_googlendk',
    version='1.1',
    description='p4a setup.py test',
    author='Alexander Taylor',
    author_email='alexanderjohntaylor@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp': ['*.py', '*.png']}
)
