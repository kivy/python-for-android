
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'debug': None,
                   'requirements': 'pygame,pyjnius,kivy,python2,android',
                   'android-api': 19,
                   'ndk-dir': '/home/asandy/android/crystax-ndk-10.3.2',
                   'dist-name': 'bdisttest_pygame',
                   'orientation': 'portrait',
                   'ndk-version': '10.3.2',
                   'permission': 'VIBRATE',
                   }}

package_data = {'': ['*.py',
                     '*.png']
                }

packages = find_packages()
print('packages are', packages)

setup(
    name='testapp_setup_pygame',
    version='1.1',
    description='p4a setup.py test with pygame',
    author='Alexander Taylor',
    author_email='alexanderjohntaylor@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp_pygame': ['*.py', '*.png']}
)
