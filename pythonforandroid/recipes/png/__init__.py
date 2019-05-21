from pythonforandroid.recipe import NDKRecipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint

import sh

from os.path import join


class PngRecipe(NDKRecipe):
    name = 'png'
    # This version is the last `sha commit` published in the repo (it's more
    # than one year old...) and it's for libpng version `1.6.29`. We set a
    # commit for a version because the author of the github's repo never
    # released/tagged it, despite He performed the necessary changes in
    # master branch.
    version = 'b43b4c6'

    # TODO: Try to move the repo to mainline
    url = 'https://github.com/julienr/libpng-android/archive/{version}.zip'

    patches = ['build_shared_library.patch']

    generated_libraries = ['libpng.so']

    def build_arch(self, arch):
        super(PngRecipe, self).build_arch(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            shprint(
                sh.cp,
                join(
                    self.get_build_dir(arch.arch),
                    'libs',
                    arch.arch,
                    'libpng.so'),
                join(self.ctx.get_libs_dir(arch.arch), 'libpng16.so'))
                    
                                
            pass

recipe = PngRecipe()
