from pythonforandroid.recipe import CythonRecipe


class CymunkRecipe(CythonRecipe):
    version = 'master'
    url = 'https://github.com/tito/cymunk/archive/{version}.zip'
    name = 'cymunk'

    depends = [('python2', 'python3crystax')]

    def get_recipe_env(self, arch):
        """ 
	    cython has problem with -lpython3.5m , hack to add -L to it

	    roughly adapted from similar numpy (fix-numpy branch) dirty solution
        """

        env = super(CymunkRecipe, self).get_recipe_env(arch)
        #: Hack add path L to crystax as a CFLAG

	if 'python3crystax' not in self.ctx.recipe_build_order:
	    return env

        api_ver = self.ctx.android_api

        flags = " -L{ctx.ndk_dir}/sources/python/3.5/libs/{arch}/"\
                            .format(ctx=self.ctx, arch=arch.arch)
        env['LDFLAGS'] += flags

        return env


recipe = CymunkRecipe()
