# recipe for aubio package
from pythonforandroid.recipe import CompiledComponentsPythonRecipe, CythonRecipe
from os.path import join


class AubioRecipe(CythonRecipe):
    version = '0.4.7'
    #source_dir = '/home/jk/Downloads/aubio-0.4.7/'
    url = 'https://aubio.org/pub/aubio-{version}.tar.bz2'
    #url = source_dir
    depends = ['numpy']  # Make sure 'samplerate' is included as a dependency
    patches =[join('patches', 'build_ext.patch')]
    #install_in_hostpython = True
    #call_hostpython_via_targetpython = False
    

#    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
#        env = super().get_recipe_env(arch, with_flags_in_cc=True)
#        # Add the WAFOPTS variable to disable specific features
#        env['WAFOPTS'] = '--disable-avcodec --disable-samplerate --disable-jack --disable-sndfile' 
#        env['PKG_CONFIG_PATH'] = '/home/jk/Downloads/aubio-0.4.7/build/' + env.get('PKG_CONFIG_PATH', '') 
#        env['LD_LIBRARY_PATH'] = '/home/jk/Downloads/aubio-0.4.7/build/src/'
#
##        env['CFLAGS'] += ' -I/usr/lib/x86_64-linux-gnu/'
#        #env['CFLAGS'] += ' -DHAVE_SAMPLERATE=0'
##        env['CC'] += '/home/jk/Downloads/aubio-0.4.7/contrib/toolchain-android-19-arm/bin/arm-linux-androideabi-gcc-4.9'
#        return env
##
##    def build_arch(self, arch):
##        super().build_arch(arch)
##        # You may need to perform additional build steps specific to aubio
##        # For example:
##        # self.run_python('-m pip install --no-deps --force-reinstall --target={} .'.format(self.get_build_dir(arch.arch)))
##
##    def install(self):
##        super().install()
##        # You may need to perform additional installation steps specific to aubio
##        # For example:
##        # self.run_python('-m pip install --no-deps --force-reinstall --target={} .'.format(self.get_install_dir()))
##
##    def get_recipe_depends(self, arch):
##        depends = super().get_recipe_depends(arch)
##        # You may need to include additional dependencies specific to aubio
##        # For example:
##        # depends['python3'] = self.ctx.python_recipe
##        return depends


recipe = AubioRecipe()

