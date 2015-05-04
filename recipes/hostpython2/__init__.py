
from toolchain import Recipe, shprint
import sh


class Hostpython2Recipe(Recipe):
    version = '2.7.2'
    url = 'http://python.org/ftp/python/{version}/Python-{version}.tar.bz2'
    name = 'hostpython2'


recipe = Hostpython2Recipe()
