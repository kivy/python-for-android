from os import makedirs, remove
from os.path import exists, join
import sh

from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint


class LibRt(Recipe):
    '''
    This is a dumb recipe. We may need this because some recipes inserted some
    flags `-lrt` without our control, case of:

        - :class:`~pythonforandroid.recipes.gevent.GeventRecipe`
        - :class:`~pythonforandroid.recipes.lxml.LXMLRecipe`

    .. note:: the librt doesn't exist in android but it is integrated into
        libc, so we create a symbolic link which we will remove when our build
        finishes'''

    @property
    def libc_path(self):
        return join(self.ctx.ndk_platform, 'usr', 'lib', 'libc')

    def build_arch(self, arch):
        # Create a temporary folder to add to link path with a fake librt.so:
        fake_librt_temp_folder = join(
            self.get_build_dir(arch.arch),
            "p4a-librt-recipe-tempdir"
        )
        if not exists(fake_librt_temp_folder):
            makedirs(fake_librt_temp_folder)

        # Set symlinks, and make sure to update them on every build run:
        if exists(join(fake_librt_temp_folder, "librt.so")):
            remove(join(fake_librt_temp_folder, "librt.so"))
        shprint(sh.ln, '-sf',
                self.libc_path + '.so',
                join(fake_librt_temp_folder, "librt.so"),
                )
        if exists(join(fake_librt_temp_folder, "librt.a")):
            remove(join(fake_librt_temp_folder, "librt.a"))
        shprint(sh.ln, '-sf',
                self.libc_path + '.a',
                join(fake_librt_temp_folder, "librt.a"),
               )

        # Add folder as -L link option for all recipes if not done yet:
        if fake_librt_temp_folder not in arch.extra_global_link_paths:
            arch.extra_global_link_paths.append(
                fake_librt_temp_folder
            )


recipe = LibRt()
