from pythonforandroid.recipe import CompiledComponentsPythonRecipe

class AtomRecipe(CompiledComponentsPythonRecipe):
    site_packages_name = 'atom'
    version = '0.3.10'
    url = 'https://github.com/nucleic/atom/archive/master.zip'
    depends = ['python2']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(AtomRecipe, self).get_recipe_env(arch)
        keys = dict(
            ctx=self.ctx,
            arch=arch,
            arch_noeabi=arch.arch.replace('eabi', ''),
            pyroot=self.ctx.get_python_install_dir()
        )
        #env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'

        env['CFLAGS'] += " -I{pyroot}/include/python2.7 " \
                        " -I{ctx.ndk_dir}/platforms/android-{ctx.android_api}/arch-{arch_noeabi}/usr/include" \
                        " -I{ctx.ndk_dir}/sources/cxx-stl/gnu-libstdc++/{ctx.toolchain_version}/include" \
                        " -I{ctx.ndk_dir}/sources/cxx-stl/gnu-libstdc++/{ctx.toolchain_version}/libs/{arch.arch}/include".format(**keys)
         
        env['LDFLAGS'] += " -L{ctx.ndk_dir}/sources/cxx-stl/gnu-libstdc++/{ctx.toolchain_version}/libs/{arch.arch}" \
                " -lgnustl_shared".format(**keys)
        return env
    
recipe = AtomRecipe()
