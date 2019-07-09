from pythonforandroid.recipe import PythonRecipe


class JediRecipe(PythonRecipe):
    version = 'v0.9.0'
    url = 'https://github.com/davidhalter/jedi/archive/{version}.tar.gz'

    patches = ['fix_MergedNamesDict_get.patch']
    # This apparently should be fixed in jedi 0.10 (not released to
    # pypi yet), but it still occurs on Android, I could not reproduce
    # on desktop.

    call_hostpython_via_targetpython = False


recipe = JediRecipe()
