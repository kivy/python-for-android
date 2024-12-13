from pythonforandroid.recipe import PyProjectRecipe


class KiwiSolverRecipe(PyProjectRecipe):
    site_packages_name = 'kiwisolver'
    version = '1.4.5'
    url = 'git+https://github.com/nucleic/kiwi'
    depends = ['cppy']
    need_stl_shared = True


recipe = KiwiSolverRecipe()
