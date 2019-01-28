from pythonforandroid.recipe import PythonRecipe, current_directory, shprint
import sh


class StormRecipe(PythonRecipe):
    version = '0.20'
    url = 'https://launchpad.net/storm/trunk/{version}/+download/storm-{version}.tar.bz2'
    depends = []
    site_packages_name = 'storm'
    call_hostpython_via_targetpython = False

    def prebuild_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            # Cross compiling for 32 bits in 64 bit ubuntu before precise is
            # failing. See
            # https://bugs.launchpad.net/ubuntu/+source/python2.7/+bug/873007
            shprint(sh.sed, '-i',
                    "s|BUILD_CEXTENSIONS = True|BUILD_CEXTENSIONS = False|",
                    'setup.py')


recipe = StormRecipe()
