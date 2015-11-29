
from pythonforandroid.toolchain import PythonRecipe, shprint, current_directory
from os.path import exists, join
import sh
import glob


class VispyRecipe(PythonRecipe):
    # version = 'v0.4.0'
    version = 'master'
    url = 'https://github.com/vispy/vispy/archive/{version}.tar.gz'
    # version = 'campagnola-scenegraph-update'
    # url = 'https://github.com/campagnola/vispy/archive/scenegraph-update.zip'
    # version = '???'
    # url = 'https://github.com/inclement/vispy/archive/Eric89GXL-arcball.zip'

    depends = ['python2', 'numpy', 'pysdl2']

    def prebuild_arch(self, arch):
        super(VispyRecipe, self).prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        if exists(join(build_dir, '.patched')):
            print('vispy already patched, skipping')
            return
        self.apply_patch('disable_freetype.patch', arch.arch)
        self.apply_patch('disable_font_triage.patch', arch.arch)
        self.apply_patch('use_es2.patch', arch.arch)
        self.apply_patch('remove_ati_check.patch', arch.arch)

        self.apply_patch('make_shader_es2_compliant.patch', arch.arch)
        self.apply_patch('detect_finger_events.patch', arch.arch)

        shprint(sh.touch, join(build_dir, '.patched'))

recipe = VispyRecipe()
