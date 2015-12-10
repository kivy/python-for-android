
from pythonforandroid.toolchain import PythonRecipe


class VispyRecipe(PythonRecipe):
    # version = 'v0.4.0'
    version = 'master'
    url = 'https://github.com/vispy/vispy/archive/{version}.tar.gz'
    # version = 'campagnola-scenegraph-update'
    # url = 'https://github.com/campagnola/vispy/archive/scenegraph-update.zip'
    # version = '???'
    # url = 'https://github.com/inclement/vispy/archive/Eric89GXL-arcball.zip'

    depends = ['python2', 'numpy', 'pysdl2']

    patches = ['disable_freetype.patch',
               'disable_font_triage.patch',
               'use_es2.patch',
               'remove_ati_check.patch']


recipe = VispyRecipe()
