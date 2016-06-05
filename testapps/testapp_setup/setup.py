
from pythonforandroid.bdist_apk import register_args

register_args('--requirements=sdl2,pyjnius,kivy,python2',
              '--android-api=19',
              '--ndk-dir=/home/asandy/android/crystax-ndk-10.3.1',
              '--dist-name=bdisttest')

from setuptools import setup, find_packages
from distutils.extension import Extension

setup(
    name='testapp_setup',
    version='1.1',
    description='p4a setup.py test',
    author='Alexander Taylor',
    author_email='alexanderjohntaylor@gmail.com',
)
