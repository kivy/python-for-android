from setuptools import setup, find_packages

options = {'apk': {'debug': None,
                   'requirements': 'python3,vispy',
                   'blacklist-requirements': 'openssl,sqlite3',
                   'android-api': 27,
                   'ndk-api': 21,
                   'bootstrap': 'empty',
                   'ndk-dir': '/home/asandy/android/android-ndk-r17c',
                   'dist-name': 'bdisttest',
                   'ndk-version': '10.3.2',
                   'permission': 'VIBRATE',
                   }}

package_data = {'': ['*.py',
                     '*.png']
                }

packages = find_packages()
print('packages are', packages)

setup(
    name='testapp_vispy',
    version='1.1',
    description='p4a setup.py test',
    author='Alexander Taylor',
    author_email='alexanderjohntaylor@gmail.com',
    packages=find_packages(),
    options=options,
    package_data={'testapp_vispy': ['*.py', '*.png']}
)
