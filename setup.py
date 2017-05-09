
from setuptools import setup, find_packages
from os import walk
from os.path import join, dirname, sep
import os
import glob

# NOTE: All package data should also be set in MANIFEST.in

packages = find_packages()

package_data = {'': ['*.tmpl',
                     '*.patch', ], }

data_files = []


if os.name == 'nt':
    install_reqs = ['appdirs', 'colorama>=0.3.3', 'jinja2',
                        'six']
else:
    install_reqs = ['appdirs', 'colorama>=0.3.3', 'sh>=1.10', 'jinja2',
                        'six']

# By specifying every file manually, package_data will be able to
# include them in binary distributions. Note that we have to add
# everything as a 'pythonforandroid' rule, using '' apparently doesn't
# work.
def recursively_include(results, directory, patterns):
    for root, subfolders, files in walk(directory):
        for fn in files:
            if not any([glob.fnmatch.fnmatch(fn, pattern) for pattern in patterns]):
                continue
            filename = join(root, fn)
            directory = 'pythonforandroid'
            if directory not in results:
                results[directory] = []
            results[directory].append(join(*filename.split(sep)[1:]))

recursively_include(package_data, 'pythonforandroid/recipes',
                    ['*.patch', 'Setup*', '*.pyx', '*.py', '*.c', '*.h',
                     '*.mk', '*.jam', ])
recursively_include(package_data, 'pythonforandroid/bootstraps',
                    ['*.properties', '*.xml', '*.java', '*.tmpl', '*.txt', '*.png',
                     '*.mk', '*.c', '*.h', '*.py', '*.sh', '*.jpg', '*.aidl',
                     '*.gradle', ])
recursively_include(package_data, 'pythonforandroid/bootstraps',
                    ['sdl-config', ])
recursively_include(package_data, 'pythonforandroid/bootstraps/webview',
                    ['*.html', ])
recursively_include(package_data, 'pythonforandroid',
                    ['liblink', 'biglink', 'liblink.sh'])

setup(name='python-for-android',
      version='0.5',
      description='Android APK packager for Python scripts and apps',
      author='The Kivy team',
      author_email='kivy-dev@googlegroups.com',
      url='https://github.com/kivy/python-for-android', 
      license='MIT', 
      install_requires=install_reqs,
      entry_points={
          'console_scripts': [
              'python-for-android = pythonforandroid.toolchain:main',
              'p4a = pythonforandroid.toolchain:main',
              ],
          'distutils.commands': [
              'apk = pythonforandroid.bdistapk:BdistAPK',
              ],
          },
      classifiers = [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: OS Independent',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Android',
          'Programming Language :: C',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development',
          'Topic :: Utilities',
          ],
      packages=packages,
      package_data=package_data,
      )
