
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'debug': None,
                   'requirements': 'python3,genericndkbuild,pyjnius',
                   'blacklist-requirements': 'openssl,sqlite3',
                   'android-api': 27,
                   'ndk-api': 21,
                   'sdk-dir':'/opt/android/android-sdk/',
                   'ndk-dir':'/opt/android/android-ndk-r17c/',
                   'dist-name': 'testapp_service',
                   'ndk-version': '10.3.2',
                   'bootstrap': 'service_only',
                   'permissions': ['INTERNET', 'VIBRATE'],
                   'arch': 'armeabi-v7a',
                   'service': 'time:p4atime.py',
                   }}

package_data = {'': ['*.py']}

packages = find_packages()
print('packages are', packages)

setup(
    name='testapp_service',
    version='1.1',
    description='p4a service testapp',
    author='Alexander Taylor',
    author_email='alexanderjohntaylor@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp_service': ['*.py']}
)
