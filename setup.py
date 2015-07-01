
from setuptools import setup, find_packages

# NOTE: All package data is set in MANIFEST.in

setup(name='python-for-android',
      version='0.1',
      description='Android APK packager for Python scripts and apps',
      author='Alexander Taylor',
      author_email='kivy-dev@googlegroups.com',
      url='https://github.com/inclement/python-for-android-revamp', 
      license='MIT', 
      install_requires=['appdirs', 'colorama', 'sh'],
      entry_points={
          'console_scripts': [
              'python-for-android = pythonforandroid.toolchain:ToolchainCL',
              ],
          'distutils.commands': [
              'apktest = pythonforandroid.bdist_apk:BdistAPK',
              ],
          },
      )
