from pythonforandroid.toolchain import Recipe, shprint, current_directory
from os.path import exists, join
import sh


class DocutilsRecipe(Recipe):

    url = ('http://prdownloads.sourceforge.net/docutils/'
           'docutils-{version}.tar.gz')
    # md5sum = '4f3dc9a9d857734a488bcbefd9cd64ed'    add later
    site_packages_name = 'docutils'
    depends = ['pil', ]
    version = '0.9.1'
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

    def prebuild_arch(self, arch):
        super(DocutilsRecipe, self).prebuild_arch(arch)
        return True

    def build_arch(self, arch):
        super(DocutilsRecipe, self).build_arch(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            env = super(DocutilsRecipe, self).get_recipe_env(arch)
            env['LDFLAGS'] = ' '.join([env['LDFLAGS'],
                                      '-L'+self.ctx.get_libs_dir(arch.arch)])
            hostpython = sh.Command(self.ctx.hostpython)

            if self.ctx.python_recipe.from_crystax:
                env['LDSHARED'] = env['CC'] + ' -shared'
            else:
                env['LDSHARED'] = join(self.ctx.root_dir,
                                       'tools', 'liblink.sh')

            shprint(hostpython, 'setup.py', 'build_ext')
            shprint(sh.Command('find'), '.', '-name', "'*.pyx'",
                    '-exec', 'cython', '{}', ';')
            shprint(hostpython, 'setup.py', 'build_ext', '-v')
            shprint(hostpython, 'setup.py', 'install', '-O2')
            env['LDSHARED'] = None

    def postbuild_arch(self, arch):
        super(DocutilsRecipe, self).build_arch(arch)
        return True

recipe = DocutilsRecipe()
