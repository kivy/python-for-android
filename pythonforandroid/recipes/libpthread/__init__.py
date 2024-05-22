from os import makedirs, remove
from os.path import exists, join
import sh

from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint


class LibPthread(Recipe):
    '''
    This is a dumb recipe. We may need this because some recipes inserted some
    flags `-lpthread` without our control, case of:

        - :class:`~pythonforandroid.recipes.uvloop.UvloopRecipe`

    .. note:: the libpthread doesn't exist in android but it is integrated into
        libc, so we create a symbolic link which we will remove when our build
        finishes'''

    def build_arch(self, arch):
        libc_path = join(arch.ndk_lib_dir_versioned, 'libc')
        # Create a temporary folder to add to link path with a fake libpthread.so:
        fake_libpthread_temp_folder = join(
            self.get_build_dir(arch.arch),
            "p4a-libpthread-recipe-tempdir"
        )
        if not exists(fake_libpthread_temp_folder):
            makedirs(fake_libpthread_temp_folder)

        # Set symlinks, and make sure to update them on every build run:
        if exists(join(fake_libpthread_temp_folder, "libpthread.so")):
            remove(join(fake_libpthread_temp_folder, "libpthread.so"))
        shprint(sh.ln, '-sf',
                libc_path + '.so',
                join(fake_libpthread_temp_folder, "libpthread.so"),
                )
        if exists(join(fake_libpthread_temp_folder, "libpthread.a")):
            remove(join(fake_libpthread_temp_folder, "libpthread.a"))
        shprint(sh.ln, '-sf',
                libc_path + '.a',
                join(fake_libpthread_temp_folder, "libpthread.a"),
               )

        # Add folder as -L link option for all recipes if not done yet:
        if fake_libpthread_temp_folder not in arch.extra_global_link_paths:
            arch.extra_global_link_paths.append(
                fake_libpthread_temp_folder
            )


recipe = LibPthread()
