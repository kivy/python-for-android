
from setuptools import setup

setup(name='python-for-android',
      version='0.1',
      description='Android APK packager for Python scripts and apps',
      author='Alexander Taylor',
      author_email='kivy-dev@googlegroups.com',
      url='https://github.com/inclement/p4a-experiment/', 
      license='MIT', 
      packages=['pythonforandroid'],
      install_requires=['appdirs', 'colorama', 'sh'],
      entry_points={
          'console_scripts': [
              'python-for-android = pythonforandroid.toolchain:ToolchainCL'
              ],
          }
      )

