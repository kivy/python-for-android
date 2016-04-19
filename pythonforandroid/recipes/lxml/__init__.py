from pythonforandroid.toolchain import Recipe, shprint, shutil, current_directory
from os.path import exists, join
import sh

class LXMLRecipe(Recipe):
    version = '3.6.0'
    url = 'https://pypi.python.org/packages/source/l/lxml/lxml-{version}.tar.gz'
    depends = ['python2', 'libxml2', 'libxslt']

    def should_build(self, arch):
        super(LXMLRecipe, self).should_build(arch)
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'liblxml.so'))

    def build_arch(self, arch):
        super(LXMLRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            #chmod +x $BUILD_libxslt/xslt-config
            bash = sh.Command('bash')
            shprint(bash, 'configure', '--enable-minimal', '--disable-soname-versions', '--host=arm-linux-androideabi', '--enable-shared', _env=env)
            shprint(sh.make, _env=env)
            shutil.copyfile('src/liblxml/.libs/libsodium.so', join(self.ctx.get_libs_dir(arch.arch), 'libsodium.so'))


            """	try $HOSTPYTHON setup.py build_ext -I$BUILD_libxml2/include -I$BUILD_libxslt
	try find . -iname '*.pyx' -exec $CYTHON {} \;
	try $HOSTPYTHON setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;

	export PYTHONPATH=$BUILD_hostpython/Lib/site-packages
	try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

	unset LDSHARED
	pop_arm"""

    def get_recipe_env(self, arch):
        env = super(LibsodiumRecipe, self).get_recipe_env(arch)
        env['CC'] += "-I$BUILD_libxml2/include -I$BUILD_libxslt"
        env['LDFLAGS'] = "-L$BUILD_libxslt/libxslt/.libs -L$BUILD_libxslt/libexslt/.libs -L$BUILD_libxml2/.libs -L$BUILD_libxslt/libxslt -L$BUILD_libxslt/libexslt -L$BUILD_libxml2/ " + env['LDFLAGS']
        env['LDSHARED'] = "$LIBLINK"
        env['PATH'] += ":$BUILD_libxslt"
        env['CFLAGS'] += ' -Os'
        return env

recipe = LXMLRecipe()
