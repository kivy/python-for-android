
from setuptools import setup, find_packages

# NOTE: All package data is set in MANIFEST.in

setup(name='python-for-android',
      version='0.1',
      description='Android APK packager for Python scripts and apps',
      author='Alexander Taylor',
      author_email='kivy-dev@googlegroups.com',
      url='https://github.com/inclement/python-for-android-revamp', 
      license='MIT', 
      install_requires=['appdirs', 'colorama', 'sh', 'jinja2'],
      entry_points={
          'console_scripts': [
              'python-for-android = pythonforandroid.toolchain:ToolchainCL',
              'p4a = pythonforandroid.toolchain:ToolchainCL',
              ],
          'distutils.commands': [
              'bdist_apk = pythonforandroid.bdist_apk:BdistAPK',
              ],
          },
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: OS Independent',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: C',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development',
          'Topic :: Utilities',
          ],
      )
