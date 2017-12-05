
from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'debug': None,
                   'requirements': 'python2,flask,pyjnius',
                   'android-api': 19,
                   'ndk-dir': '/home/asandy/android/crystax-ndk-10.3.2',
                   'dist-name': 'testapp_flask',
                   'ndk-version': '10.3.2',
                   'bootstrap': 'webview',
                   'permissions': ['INTERNET', 'VIBRATE'],
                   'arch': 'armeabi-v7a',
                   'window': None,
                   }}

package_data = {'': ['*.py',
                     '*.png']
                }

packages = find_packages()
print('packages are', packages)

setup(
    name='testapp_flask',
    version='1.0',
    description='p4a flask testapp',
    author='Alexander Taylor',
    author_email='alexanderjohntaylor@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp_flask': ['*.py', '*.png'],
                  'testapp_flask/static': ['*.png', '*.css'],
                  'testapp_flask/templates': ['*.html']}
)
