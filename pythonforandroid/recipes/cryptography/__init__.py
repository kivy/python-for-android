from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class CryptographyRecipe(CompiledComponentsPythonRecipe):
    name = 'cryptography'
    version = 'master'
    url = 'git+file:///home/enoch/cryptography'
    depends = ['host_cffi', 'host_cython', 'host_setuptools', 'host_sh',
               'idna', 'asn1crypto', 'six', 'cffi',
               'enum34', 'ipaddress', 'openssl']

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(CryptographyRecipe, self).get_recipe_env(arch)
        recipe = self.get_recipe('libffi', self.ctx)
        dirs = recipe.get_include_dirs(arch)
        recipe = self.get_recipe('openssl', self.ctx)
        dirs += recipe.get_include_dirs(arch)
        # Required: ln -s \
        # ~/Android/Sdk/ndk-bundle/sysroot/usr/include/arm-linux-androideabi/asm/unistd-common.h \
        # ~/Android/CrystaX/platforms/android-19/arch-arm/usr/include
        env['CFLAGS'] += (' -include unistd-common.h' +
                          ''.join([' -I' + dir for dir in dirs]))
        return env


recipe = CryptographyRecipe()
