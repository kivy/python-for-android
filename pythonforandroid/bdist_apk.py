from __future__ import print_function
from setuptools import Command
from pythonforandroid import toolchain

class BdistAPK(Command):
    description = 'Create an APK with python-for-android'
    user_options = []

    def initialize_options(sel):
        print('initialising!')

    def finalize_options(self):
        print('finalising!')

    def run(self):
        print('running!')
