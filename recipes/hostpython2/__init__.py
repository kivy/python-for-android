
from toolchain import Recipe, shprint, get_directory
from os.path import join
import sh


class Hostpython2Recipe(Recipe):
    version = '2.7.2'
    url = 'http://python.org/ftp/python/{version}/Python-{version}.tar.bz2'
    name = 'hostpython2'

    def prebuild_armeabi(self):
        # Override hostpython Setup?
        print('Running hostpython2 prebuild')
        shprint(sh.cp, join(self.get_recipe_dir(), 'Setup'),
                join(self.get_build_dir('armeabi'),
                     get_directory(self.versioned_url),
                     'Modules', 'Setup'))


recipe = Hostpython2Recipe()
