import sh
from os.path import join
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

    @property
    def librt_path(self):
        return join(self.ctx.ndk_platform, 'usr', 'lib', 'librt')

    def build_arch(self, arch):
        shprint(sh.ln, '-sf', self.libc_path + '.so', self.librt_path + '.so')
        shprint(sh.ln, '-sf', self.libc_path + '.a', self.librt_path + '.a')

    def postbuild_arch(self, arch):
        shprint(sh.rm, self.librt_path + '.so')
        shprint(sh.rm, self.librt_path + '.a')


recipe = LibRt()
