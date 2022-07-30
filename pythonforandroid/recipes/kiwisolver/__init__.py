from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class KiwiSolverRecipe(CppCompiledComponentsPythonRecipe):
    site_packages_name = 'kiwisolver'
    # Pin to commit `docs: attempt to fix doc building`, the latest one
    # at the time of writing, just to be sure that we have te most up to date
    # version, but it should be pinned to an official release once the c++
    # changes that we want to include are merged to master branch
    #   Note: the commit we want to include is
    #         `Cppy use update and c++11 compatibility` (4858730)
    version = '1.3.2'
    url = 'https://github.com/nucleic/kiwi/archive/{version}.zip'
    depends = ['cppy']


recipe = KiwiSolverRecipe()
