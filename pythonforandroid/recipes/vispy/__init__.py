from pythonforandroid.recipe import PythonRecipe


class VispyRecipe(PythonRecipe):
    version = '0.4.0'
    url = 'https://github.com/vispy/vispy/archive/v{version}.tar.gz'
    depends = ['numpy', 'pysdl2']
    patches = ['disable_freetype.patch',
               'disable_font_triage.patch',
               'use_es2.patch',
               'remove_ati_check.patch']


recipe = VispyRecipe()
