from pythonforandroid.recipe import CythonRecipe, IncludedFilesBehaviour
from pythonforandroid.util import current_directory
from pythonforandroid.patching import will_build
from pythonforandroid import logger

from os.path import join


class AndroidRecipe(IncludedFilesBehaviour, CythonRecipe):
    # name = 'android'
    version = None
    url = None

    src_filename = 'src'

    depends = [('pygame', 'sdl2', 'genericndkbuild'),
               ('python2', 'python3crystax', 'python3')]

    config_env = {}

    def get_recipe_env(self, arch):
        env = super(AndroidRecipe, self).get_recipe_env(arch)
        env.update(self.config_env)
        return env

    def prebuild_arch(self, arch):
        super(AndroidRecipe, self).prebuild_arch(arch)

        tpxi = 'DEF {} = {}\n'
        th = '#define {} {}\n'
        tpy = '{} = {}\n'

        bootstrap = bootstrap_name = self.ctx.bootstrap.name
        is_sdl2 = bootstrap_name in ('sdl2', 'sdl2python3', 'sdl2_gradle')
        is_pygame = bootstrap_name in ('pygame',)
        is_webview = bootstrap_name in ('webview',)

        if is_sdl2 or is_webview:
            if is_sdl2:
                bootstrap = 'sdl2'
            java_ns = 'org.kivy.android'
            jni_ns = 'org/kivy/android'
        elif is_pygame:
            java_ns = 'org.renpy.android'
            jni_ns = 'org/renpy/android'
        else:
            logger.error('unsupported bootstrap for android recipe: {}'.format(bootstrap_name))
            exit(1)

        config = {
            'BOOTSTRAP': bootstrap,
            'IS_SDL2': int(is_sdl2),
            'IS_PYGAME': int(is_pygame),
            'PY2': int(will_build('python2')(self)),
            'JAVA_NAMESPACE': java_ns,
            'JNI_NAMESPACE': jni_ns,
        }

        with (
                current_directory(self.get_build_dir(arch.arch))), (
                open(join('android', 'config.pxi'), 'w')) as fpxi, (
                open(join('android', 'config.h'), 'w')) as fh, (
                open(join('android', 'config.py'), 'w')) as fpy:
            for key, value in config.items():
                fpxi.write(tpxi.format(key, repr(value)))
                fpy.write(tpy.format(key, repr(value)))
                fh.write(th.format(key,
                                   value if isinstance(value, int)
                                   else '"{}"'.format(value)))
                self.config_env[key] = str(value)

            if is_sdl2:
                fh.write('JNIEnv *SDL_AndroidGetJNIEnv(void);\n')
                fh.write('#define SDL_ANDROID_GetJNIEnv SDL_AndroidGetJNIEnv\n')
            elif is_pygame:
                fh.write('JNIEnv *SDL_ANDROID_GetJNIEnv(void);\n')


recipe = AndroidRecipe()
