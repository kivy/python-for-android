from pythonforandroid.toolchain import Recipe, shprint, current_directory
from os.path import exists, join
import sh


class DocutilsRecipe(Recipe):

    url = ('http://prdownloads.sourceforge.net/docutils/'
           'docutils-{version}.tar.gz')
    # md5sum = '4622263b62c5c771c03502afa3157768'
    site_packages_name = 'docutils'
    depends = ['pil', ]  # 'lxml', ]

    version = '0.12'
    conflicts = []

    def should_build(self, arch):
        name = self.site_packages_name
        if name is None:
            name = self.name
        if self.ctx.has_package(name):
            shprint(sh.echo, 'Python package already exists in site-packages')
            return False
        shprint(sh.echo,
                '{} apparently isn\'t already in site-packages'.format(name))
        return True

    def build_arch(self, arch):
        super(DocutilsRecipe, self).build_arch(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            env = super(DocutilsRecipe, self).get_recipe_env(arch)
            hostpython = sh.Command(self.ctx.hostpython)

            shprint(hostpython, 'setup.py', 'build_ext')
            shprint(hostpython, 'setup.py', 'build_ext', '-v')
            shprint(hostpython, 'setup.py', 'install', '-O2')

recipe = DocutilsRecipe()
