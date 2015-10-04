from pythonforandroid.toolchain import Bootstrap, shprint, current_directory, info, warning, ArchAndroid, logger, info_main, which
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
