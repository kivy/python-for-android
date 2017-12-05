from pythonforandroid.toolchain import Bootstrap
from os.path import join, exists
from os import walk
import glob
import sh


class EmptyBootstrap(Bootstrap):
    name = 'empty'

    recipe_depends = []

    can_be_chosen_automatically = False

    def run_distribute(self):
        print('empty bootstrap has no distribute')
        exit(1)

bootstrap = EmptyBootstrap()
