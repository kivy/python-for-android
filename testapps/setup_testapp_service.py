
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'debug': None,
                   'requirements': 'python2,genericndkbuild',
                   'android-api': 27,
                   'ndk-api': 21,
                   'ndk-dir': '/home/asandy/android/crystax-ndk-10.3.2',
                   'dist-name': 'testapp_service',
                   'ndk-version': '10.3.2',
                   'bootstrap': 'service_only',
                   'permissions': ['INTERNET', 'VIBRATE'],
                   'arch': 'armeabi-v7a',
                   }}

package_data = {'': ['*.py']}

packages = find_packages()
print('packages are', packages)

setup(
    name='testapp_service',
    version='1.0',
    description='p4a service testapp',
    author='Alexander Taylor',
    author_email='alexanderjohntaylor@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp_service': ['*.py']}
)
