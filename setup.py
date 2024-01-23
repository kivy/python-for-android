
import glob
from io import open  # for open(..,encoding=...) parameter in python 2
from os import walk
from os.path import join, dirname, sep
import re
from setuptools import setup, find_packages

# NOTE: All package data should also be set in MANIFEST.in

packages = find_packages()

package_data = {'': ['*.tmpl',
                     '*.patch',
                     '*.diff', ], }

data_files = []


# must be a single statement since buildozer is currently parsing it, refs:
# https://github.com/kivy/buildozer/issues/722
install_reqs = [
    'appdirs', 'colorama>=0.3.3', 'jinja2',
    'sh>=1.10, <2.0; sys_platform!="win32"',
    'build', 'toml', 'packaging', 'setuptools'
]
# (build and toml are used by pythonpackage.py)


# By specifying every file manually, package_data will be able to
# include them in binary distributions. Note that we have to add
# everything as a 'pythonforandroid' rule, using '' apparently doesn't
# work.
def recursively_include(results, directory, patterns):
    for root, subfolders, files in walk(directory):
        for fn in files:
            if not any(
                    glob.fnmatch.fnmatch(fn, pattern) for pattern in patterns):
                continue
            filename = join(root, fn)
            directory = 'pythonforandroid'
            if directory not in results:
                results[directory] = []
            results[directory].append(join(*filename.split(sep)[1:]))


recursively_include(package_data, 'pythonforandroid/recipes',
                    ['*.patch', 'Setup*', '*.pyx', '*.py', '*.c', '*.h',
                     '*.mk', '*.jam', '*.diff', ])
recursively_include(package_data, 'pythonforandroid/bootstraps',
                    [
                        '*.properties', '*.xml', '*.java', '*.tmpl', '*.txt',
                        '*.png', '*.mk', '*.c', '*.h', '*.py', '*.sh', '*.jpg',
                        '*.aidl', '*.gradle', '.gitkeep', 'gradlew*', '*.jar',
                        '*.patch',
                    ])
recursively_include(package_data, 'pythonforandroid/bootstraps',
                    ['sdl-config', ])
recursively_include(package_data, 'pythonforandroid/bootstraps/webview',
                    ['*.html', ])
recursively_include(package_data, 'pythonforandroid',
                    ['liblink', 'biglink', 'liblink.sh'])

with open(join(dirname(__file__), 'README.md'),
          encoding="utf-8",
          errors="replace", ) as fileh:
    long_description = fileh.read()

init_filen = join(dirname(__file__), 'pythonforandroid', '__init__.py')
version = None
try:
    with open(init_filen,
              encoding="utf-8",
              errors="replace") as fileh:
        lines = fileh.readlines()
except IOError:
    pass
else:
    for line in lines:
        line = line.strip()
        if line.startswith('__version__ = '):
            matches = re.findall(r'["\'].+["\']', line)
            if matches:
                version = matches[0].strip("'").strip('"')
                break
if version is None:
    raise Exception(
        'Error: version could not be loaded from {}'.format(init_filen))

setup(name='python-for-android',
      version=version,
      description=(
          'A development tool that packages Python apps into '
          'binaries that can run on Android devices.'
      ),
      long_description=long_description,
      long_description_content_type='text/markdown',
      python_requires=">=3.7.0",
      author='Kivy Team and other contributors',
      author_email='kivy-dev@googlegroups.com',
      url='https://github.com/kivy/python-for-android',
      license='MIT',
      install_requires=install_reqs,
      entry_points={
          'console_scripts': [
              'python-for-android = pythonforandroid.entrypoints:main',
              'p4a = pythonforandroid.entrypoints:main',
              ],
          'distutils.commands': [
              'apk = pythonforandroid.bdistapk:BdistAPK',
              'aar = pythonforandroid.bdistapk:BdistAAR',
              'aab = pythonforandroid.bdistapk:BdistAAB',
              ],
          },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: OS Independent',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Android',
          'Programming Language :: C',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Topic :: Software Development',
          'Topic :: Utilities',
          ],
      packages=packages,
      package_data=package_data,
      project_urls={
          'Documentation': "https://python-for-android.readthedocs.io",
          'Source': "https://github.com/kivy/python-for-android",
          'Bug Reports': "https://github.com/kivy/python-for-android/issues",
      },

      )
