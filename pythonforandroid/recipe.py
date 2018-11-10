from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split
import importlib
import glob
from shutil import rmtree
from six import PY2, with_metaclass

import hashlib
from re import match

import sh
import shutil
import fnmatch
from os import listdir, unlink, environ, mkdir, curdir, walk
from sys import stdout
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
from pythonforandroid.logger import (logger, info, warning, error, debug, shprint, info_main)
from pythonforandroid.util import (urlretrieve, current_directory, ensure_dir)

# this import is necessary to keep imp.load_source from complaining :)
if PY2:
    import imp
    import_recipe = imp.load_source
else:
    import importlib.util
    if hasattr(importlib.util, 'module_from_spec'):
        def import_recipe(module, filename):
            spec = importlib.util.spec_from_file_location(module, filename)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    else:
        from importlib.machinery import SourceFileLoader

        def import_recipe(module, filename):
            return SourceFileLoader(module, filename).load_module()


class RecipeMeta(type):
    def __new__(cls, name, bases, dct):
        if name != 'Recipe':
            if 'url' in dct:
                dct['_url'] = dct.pop('url')
            if 'version' in dct:
                dct['_version'] = dct.pop('version')

        return super(RecipeMeta, cls).__new__(cls, name, bases, dct)


class Recipe(with_metaclass(RecipeMeta)):
    _url = None
    '''The address from which the recipe may be downloaded. This is not
    essential, it may be omitted if the source is available some other
    way, such as via the :class:`IncludedFilesBehaviour` mixin.

    If the url includes the version, you may (and probably should)
    replace this with ``{version}``, which will automatically be
    replaced by the :attr:`version` string during download.

    .. note:: Methods marked (internal) are used internally and you
              probably don't need to call them, but they are available
              if you want.
    '''

    _version = None
    '''A string giving the version of the software the recipe describes,
    e.g. ``2.0.3`` or ``master``.'''

    md5sum = None
    '''The md5sum of the source from the :attr:`url`. Non-essential, but
    you should try to include this, it is used to check that the download
    finished correctly.
    '''

    depends = []
    '''A list containing the names of any recipes that this recipe depends on.
    '''

    conflicts = []
    '''A list containing the names of any recipes that are known to be
    incompatible with this one.'''

    opt_depends = []
    '''A list of optional dependencies, that must be built before this
    recipe if they are built at all, but whose presence is not essential.'''

    patches = []
    '''A list of patches to apply to the source. Values can be either a string
    referring to the patch file relative to the recipe dir, or a tuple of the
    string patch file and a callable, which will receive the kwargs `arch` and
    `recipe`, which should return True if the patch should be applied.'''

    python_depends = []
    '''A list of pure-Python packages that this package requires. These
    packages will NOT be available at build time, but will be added to the
    list of pure-Python packages to install via pip. If you need these packages
    at build time, you must create a recipe.'''

    archs = ['armeabi']  # Not currently implemented properly

    @property
    def version(self):
        key = 'VERSION_' + self.name
        return environ.get(key, self._version)

    @property
    def url(self):
        key = 'URL_' + self.name
        return environ.get(key, self._url)

    @property
    def versioned_url(self):
        '''A property returning the url of the recipe with ``{version}``
        replaced by the :attr:`url`. If accessing the url, you should use this
        property, *not* access the url directly.'''
        if self.url is None:
            return None
        return self.url.format(version=self.version)

    def download_file(self, url, target, cwd=None):
        """
        (internal) Download an ``url`` to a ``target``.
        """
        if not url:
            return
        info('Downloading {} from {}'.format(self.name, url))

        if cwd:
            target = join(cwd, target)

        parsed_url = urlparse(url)
        if parsed_url.scheme in ('http', 'https'):
            def report_hook(index, blksize, size):
                if size <= 0:
                    progression = '{0} bytes'.format(index * blksize)
                else:
                    progression = '{0:.2f}%'.format(
                        index * blksize * 100. / float(size))
                stdout.write('- Download {}\r'.format(progression))
                stdout.flush()

            if exists(target):
                unlink(target)

            urlretrieve(url, target, report_hook)
            return target
        elif parsed_url.scheme in ('git', 'git+file', 'git+ssh', 'git+http', 'git+https'):
            if isdir(target):
                with current_directory(target):
                    shprint(sh.git, 'fetch', '--tags')
                    if self.version:
                        shprint(sh.git, 'checkout', self.version)
                    shprint(sh.git, 'pull')
                    shprint(sh.git, 'pull', '--recurse-submodules')
                    shprint(sh.git, 'submodule', 'update', '--recursive')
            else:
                if url.startswith('git+'):
                    url = url[4:]
                shprint(sh.git, 'clone', '--recursive', url, target)
                if self.version:
                    with current_directory(target):
                        shprint(sh.git, 'checkout', self.version)
                        shprint(sh.git, 'submodule', 'update', '--recursive')
            return target

    def apply_patch(self, filename, arch):
        """
        Apply a patch from the current recipe directory into the current
        build directory.
        """
        info("Applying patch {}".format(filename))
        filename = join(self.get_recipe_dir(), filename)
        shprint(sh.patch, "-t", "-d", self.get_build_dir(arch), "-p1",
                "-i", filename, _tail=10)

    def copy_file(self, filename, dest):
        info("Copy {} to {}".format(filename, dest))
        filename = join(self.get_recipe_dir(), filename)
        dest = join(self.build_dir, dest)
        shutil.copy(filename, dest)

    def append_file(self, filename, dest):
        info("Append {} to {}".format(filename, dest))
        filename = join(self.get_recipe_dir(), filename)
        dest = join(self.build_dir, dest)
        with open(filename, "rb") as fd:
            data = fd.read()
        with open(dest, "ab") as fd:
            fd.write(data)

    @property
    def name(self):
        '''The name of the recipe, the same as the folder containing it.'''
        modname = self.__class__.__module__
        return modname.split(".", 2)[-1]

    @property
    def filtered_archs(self):
        '''Return archs of self.ctx that are valid build archs
        for the Recipe.'''
        result = []
        for arch in self.ctx.archs:
            if not self.archs or (arch.arch in self.archs):
                result.append(arch)
        return result

    def check_recipe_choices(self):
        '''Checks what recipes are being built to see which of the alternative
        and optional dependencies are being used,
        and returns a list of these.'''
        recipes = []
        built_recipes = self.ctx.recipe_build_order
        for recipe in self.depends:
            if isinstance(recipe, (tuple, list)):
                for alternative in recipe:
                    if alternative in built_recipes:
                        recipes.append(alternative)
                        break
        for recipe in self.opt_depends:
            if recipe in built_recipes:
                recipes.append(recipe)
        return sorted(recipes)

    def get_build_container_dir(self, arch):
        '''Given the arch name, returns the directory where it will be
        built.

        This returns a different directory depending on what
        alternative or optional dependencies are being built.
        '''
        dir_name = self.get_dir_name()
        return join(self.ctx.build_dir, 'other_builds',
                    dir_name, '{}__ndk_target_{}'.format(arch, self.ctx.ndk_api))

    def get_dir_name(self):
        choices = self.check_recipe_choices()
        dir_name = '-'.join([self.name] + choices)
        return dir_name

    def get_build_dir(self, arch):
        '''Given the arch name, returns the directory where the
        downloaded/copied package will be built.'''

        return join(self.get_build_container_dir(arch), self.name)

    def get_recipe_dir(self):
        """
        Returns the local recipe directory or defaults to the core recipe
        directory.
        """
        if self.ctx.local_recipes is not None:
            local_recipe_dir = join(self.ctx.local_recipes, self.name)
            if exists(local_recipe_dir):
                return local_recipe_dir
        return join(self.ctx.root_dir, 'recipes', self.name)

    # Public Recipe API to be subclassed if needed

    def download_if_necessary(self):
        info_main('Downloading {}'.format(self.name))
        user_dir = environ.get('P4A_{}_DIR'.format(self.name.lower()))
        if user_dir is not None:
            info('P4A_{}_DIR is set, skipping download for {}'.format(
                self.name, self.name))
            return
        self.download()

    def download(self):
        if self.url is None:
            info('Skipping {} download as no URL is set'.format(self.name))
            return

        url = self.versioned_url
        ma = match(u'^(.+)#md5=([0-9a-f]{32})$', url)
        if ma:                  # fragmented URL?
            if self.md5sum:
                raise ValueError(
                    ('Received md5sum from both the {} recipe '
                     'and its url').format(self.name))
            url = ma.group(1)
            expected_md5 = ma.group(2)
        else:
            expected_md5 = self.md5sum

        shprint(sh.mkdir, '-p', join(self.ctx.packages_path, self.name))

        with current_directory(join(self.ctx.packages_path, self.name)):
            filename = shprint(sh.basename, url).stdout[:-1].decode('utf-8')

            do_download = True
            marker_filename = '.mark-{}'.format(filename)
            if exists(filename) and isfile(filename):
                if not exists(marker_filename):
                    shprint(sh.rm, filename)
                elif expected_md5:
                    current_md5 = md5sum(filename)
                    if current_md5 != expected_md5:
                        debug('* Generated md5sum: {}'.format(current_md5))
                        debug('* Expected md5sum: {}'.format(expected_md5))
                        raise ValueError(
                            ('Generated md5sum does not match expected md5sum '
                             'for {} recipe').format(self.name))
                    do_download = False
                else:
                    do_download = False

            # If we got this far, we will download
            if do_download:
                debug('Downloading {} from {}'.format(self.name, url))

                shprint(sh.rm, '-f', marker_filename)
                self.download_file(self.versioned_url, filename)
                shprint(sh.touch, marker_filename)

                if exists(filename) and isfile(filename) and expected_md5:
                    current_md5 = md5sum(filename)
                    if expected_md5 is not None:
                        if current_md5 != expected_md5:
                            debug('* Generated md5sum: {}'.format(current_md5))
                            debug('* Expected md5sum: {}'.format(expected_md5))
                            raise ValueError(
                                ('Generated md5sum does not match expected md5sum '
                                 'for {} recipe').format(self.name))
            else:
                info('{} download already cached, skipping'.format(self.name))

    def unpack(self, arch):
        info_main('Unpacking {} for {}'.format(self.name, arch))

        build_dir = self.get_build_container_dir(arch)

        user_dir = environ.get('P4A_{}_DIR'.format(self.name.lower()))
        if user_dir is not None:
            info('P4A_{}_DIR exists, symlinking instead'.format(
                self.name.lower()))
            if exists(self.get_build_dir(arch)):
                return
            shprint(sh.rm, '-rf', build_dir)
            shprint(sh.mkdir, '-p', build_dir)
            shprint(sh.rmdir, build_dir)
            ensure_dir(build_dir)
            shprint(sh.cp, '-a', user_dir, self.get_build_dir(arch))
            return

        if self.url is None:
            info('Skipping {} unpack as no URL is set'.format(self.name))
            return

        filename = shprint(
            sh.basename, self.versioned_url).stdout[:-1].decode('utf-8')
        ma = match(u'^(.+)#md5=([0-9a-f]{32})$', filename)
        if ma:                  # fragmented URL?
            filename = ma.group(1)

        with current_directory(build_dir):
            directory_name = self.get_build_dir(arch)

            if not exists(directory_name) or not isdir(directory_name):
                extraction_filename = join(
                    self.ctx.packages_path, self.name, filename)
                if isfile(extraction_filename):
                    if extraction_filename.endswith('.zip'):
                        try:
                            sh.unzip(extraction_filename)
                        except (sh.ErrorReturnCode_1, sh.ErrorReturnCode_2):
                            # return code 1 means unzipping had
                            # warnings but did complete,
                            # apparently happens sometimes with
                            # github zips
                            pass
                        import zipfile
                        fileh = zipfile.ZipFile(extraction_filename, 'r')
                        root_directory = fileh.filelist[0].filename.split('/')[0]
                        if root_directory != basename(directory_name):
                            shprint(sh.mv, root_directory, directory_name)
                    elif (extraction_filename.endswith('.tar.gz') or
                          extraction_filename.endswith('.tgz') or
                          extraction_filename.endswith('.tar.bz2') or
                          extraction_filename.endswith('.tbz2') or
                          extraction_filename.endswith('.tar.xz') or
                          extraction_filename.endswith('.txz')):
                        sh.tar('xf', extraction_filename)
                        root_directory = shprint(
                            sh.tar, 'tf', extraction_filename).stdout.decode(
                                'utf-8').split('\n')[0].split('/')[0]
                        if root_directory != directory_name:
                            shprint(sh.mv, root_directory, directory_name)
                    else:
                        raise Exception(
                            'Could not extract {} download, it must be .zip, '
                            '.tar.gz or .tar.bz2 or .tar.xz'.format(extraction_filename))
                elif isdir(extraction_filename):
                    mkdir(directory_name)
                    for entry in listdir(extraction_filename):
                        if entry not in ('.git',):
                            shprint(sh.cp, '-Rv',
                                    join(extraction_filename, entry),
                                    directory_name)
                else:
                    raise Exception(
                        'Given path is neither a file nor a directory: {}'
                        .format(extraction_filename))

            else:
                info('{} is already unpacked, skipping'.format(self.name))

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        """Return the env specialized for the recipe
        """
        if arch is None:
            arch = self.filtered_archs[0]
        return arch.get_env(with_flags_in_cc=with_flags_in_cc)

    def prebuild_arch(self, arch):
        '''Run any pre-build tasks for the Recipe. By default, this checks if
        any prebuild_archname methods exist for the archname of the current
        architecture, and runs them if so.'''
        prebuild = "prebuild_{}".format(arch.arch.replace('-', '_'))
        if hasattr(self, prebuild):
            getattr(self, prebuild)()
        else:
            info('{} has no {}, skipping'.format(self.name, prebuild))

    def is_patched(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        return exists(join(build_dir, '.patched'))

    def apply_patches(self, arch):
        '''Apply any patches for the Recipe.'''
        if self.patches:
            info_main('Applying patches for {}[{}]'
                      .format(self.name, arch.arch))

            if self.is_patched(arch):
                info_main('{} already patched, skipping'.format(self.name))
                return

            for patch in self.patches:
                if isinstance(patch, (tuple, list)):
                    patch, patch_check = patch
                    if not patch_check(arch=arch, recipe=self):
                        continue

                self.apply_patch(
                        patch.format(version=self.version, arch=arch.arch),
                        arch.arch)

            shprint(sh.touch, join(self.get_build_dir(arch.arch), '.patched'))

    def should_build(self, arch):
        '''Should perform any necessary test and return True only if it needs
        building again.

        '''
        return True

    def build_arch(self, arch):
        '''Run any build tasks for the Recipe. By default, this checks if
        any build_archname methods exist for the archname of the current
        architecture, and runs them if so.'''
        build = "build_{}".format(arch.arch)
        if hasattr(self, build):
            getattr(self, build)()

    def postbuild_arch(self, arch):
        '''Run any post-build tasks for the Recipe. By default, this checks if
        any postbuild_archname methods exist for the archname of the
        current architecture, and runs them if so.
        '''
        postbuild = "postbuild_{}".format(arch.arch)
        if hasattr(self, postbuild):
            getattr(self, postbuild)()

    def prepare_build_dir(self, arch):
        '''Copies the recipe data into a build dir for the given arch. By
        default, this unpacks a downloaded recipe. You should override
        it (or use a Recipe subclass with different behaviour) if you
        want to do something else.
        '''
        self.unpack(arch)

    def clean_build(self, arch=None):
        '''Deletes all the build information of the recipe.

        If arch is not None, only this arch dir is deleted. Otherwise
        (the default) all builds for all archs are deleted.

        By default, this just deletes the main build dir. If the
        recipe has e.g. object files biglinked, or .so files stored
        elsewhere, you should override this method.

        This method is intended for testing purposes, it may have
        strange results. Rebuild everything if this seems to happen.

        '''
        if arch is None:
            base_dir = join(self.ctx.build_dir, 'other_builds', self.name)
        else:
            base_dir = self.get_build_container_dir(arch)
        dirs = glob.glob(base_dir + '-*')
        if exists(base_dir):
            dirs.append(base_dir)
        if not dirs:
            warning('Attempted to clean build for {} but found no existing '
                    'build dirs'.format(self.name))

        for directory in dirs:
            if exists(directory):
                info('Deleting {}'.format(directory))
                shutil.rmtree(directory)

        # Delete any Python distributions to ensure the recipe build
        # doesn't persist in site-packages
        shutil.rmtree(self.ctx.python_installs_dir)

    def install_libs(self, arch, *libs):
        libs_dir = self.ctx.get_libs_dir(arch.arch)
        if not libs:
            warning('install_libs called with no libraries to install!')
            return
        args = libs + (libs_dir,)
        shprint(sh.cp, *args)

    def has_libs(self, arch, *libs):
        return all(map(lambda l: self.ctx.has_lib(arch.arch, l), libs))

    @classmethod
    def recipe_dirs(cls, ctx):
        recipe_dirs = []
        if ctx.local_recipes is not None:
            recipe_dirs.append(realpath(ctx.local_recipes))
        if ctx.storage_dir:
            recipe_dirs.append(join(ctx.storage_dir, 'recipes'))
        recipe_dirs.append(join(ctx.root_dir, "recipes"))
        return recipe_dirs

    @classmethod
    def list_recipes(cls, ctx):
        forbidden_dirs = ('__pycache__', )
        for recipes_dir in cls.recipe_dirs(ctx):
            if recipes_dir and exists(recipes_dir):
                for name in listdir(recipes_dir):
                    if name in forbidden_dirs:
                        continue
                    fn = join(recipes_dir, name)
                    if isdir(fn):
                        yield name

    @classmethod
    def get_recipe(cls, name, ctx):
        '''Returns the Recipe with the given name, if it exists.'''
        if not hasattr(cls, "recipes"):
            cls.recipes = {}
        if name in cls.recipes:
            return cls.recipes[name]

        recipe_file = None
        for recipes_dir in cls.recipe_dirs(ctx):
            recipe_file = join(recipes_dir, name, '__init__.py')
            if exists(recipe_file):
                break
            recipe_file = None

        if not recipe_file:
            raise IOError('Recipe does not exist: {}'.format(name))

        mod = import_recipe('pythonforandroid.recipes.{}'.format(name), recipe_file)
        if len(logger.handlers) > 1:
            logger.removeHandler(logger.handlers[1])
        recipe = mod.recipe
        recipe.ctx = ctx
        cls.recipes[name] = recipe
        return recipe


class IncludedFilesBehaviour(object):
    '''Recipe mixin class that will automatically unpack files included in
    the recipe directory.'''
    src_filename = None

    def prepare_build_dir(self, arch):
        if self.src_filename is None:
            print('IncludedFilesBehaviour failed: no src_filename specified')
            exit(1)
        shprint(sh.rm, '-rf', self.get_build_dir(arch))
        shprint(sh.cp, '-a', join(self.get_recipe_dir(), self.src_filename),
                self.get_build_dir(arch))


class BootstrapNDKRecipe(Recipe):
    '''A recipe class for recipes built in an Android project jni dir with
    an Android.mk. These are not cached separatly, but built in the
    bootstrap's own building directory.

    To build an NDK project which is not part of the bootstrap, see
    :class:`~pythonforandroid.recipe.NDKRecipe`.
    '''

    dir_name = None  # The name of the recipe build folder in the jni dir

    def get_build_container_dir(self, arch):
        return self.get_jni_dir()

    def get_build_dir(self, arch):
        if self.dir_name is None:
            raise ValueError('{} recipe doesn\'t define a dir_name, but '
                             'this is necessary'.format(self.name))
        return join(self.get_build_container_dir(arch), self.dir_name)

    def get_jni_dir(self):
        return join(self.ctx.bootstrap.build_dir, 'jni')


class NDKRecipe(Recipe):
    '''A recipe class for any NDK project not included in the bootstrap.'''

    generated_libraries = []

    def should_build(self, arch):
        lib_dir = self.get_lib_dir(arch)

        for lib in self.generated_libraries:
            if not exists(join(lib_dir, lib)):
                return True

        return False

    def get_lib_dir(self, arch):
        return join(self.get_build_dir(arch.arch), 'obj', 'local', arch.arch)

    def get_jni_dir(self, arch):
        return join(self.get_build_dir(arch.arch), 'jni')

    def build_arch(self, arch, *extra_args):
        super(NDKRecipe, self).build_arch(arch)

        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.ndk_build, 'V=1', 'APP_ABI=' + arch.arch, *extra_args, _env=env)


class PythonRecipe(Recipe):
    site_packages_name = None
    '''The name of the module's folder when installed in the Python
    site-packages (e.g. for pyjnius it is 'jnius')'''

    call_hostpython_via_targetpython = True
    '''If True, tries to install the module using the hostpython binary
    copied to the target (normally arm) python build dir. However, this
    will fail if the module tries to import e.g. _io.so. Set this to False
    to call hostpython from its own build dir, installing the module in
    the right place via arguments to setup.py. However, this may not set
    the environment correctly and so False is not the default.'''

    install_in_hostpython = False
    '''If True, additionally installs the module in the hostpython build
    dir. This will make it available to other recipes if
    call_hostpython_via_targetpython is False.
    '''

    install_in_targetpython = True
    '''If True, installs the module in the targetpython installation dir.
    This is almost always what you want to do.'''

    setup_extra_args = []
    '''List of extra arugments to pass to setup.py'''

    def __init__(self, *args, **kwargs):
        super(PythonRecipe, self).__init__(*args, **kwargs)
        depends = self.depends
        depends.append(('python2', 'python3', 'python3crystax'))
        depends = list(set(depends))
        self.depends = depends

    def clean_build(self, arch=None):
        super(PythonRecipe, self).clean_build(arch=arch)
        name = self.folder_name
        python_install_dirs = glob.glob(join(self.ctx.python_installs_dir, '*'))
        for python_install in python_install_dirs:
            site_packages_dir = glob.glob(join(python_install, 'lib', 'python*',
                                               'site-packages'))
            if site_packages_dir:
                build_dir = join(site_packages_dir[0], name)
                if exists(build_dir):
                    info('Deleted {}'.format(build_dir))
                    rmtree(build_dir)

    @property
    def real_hostpython_location(self):
        if 'hostpython2' in self.ctx.recipe_build_order:
            return join(
                Recipe.get_recipe('hostpython2', self.ctx).get_build_dir(),
                'hostpython')
        elif 'hostpython3crystax' in self.ctx.recipe_build_order:
            return join(
                Recipe.get_recipe('hostpython3crystax', self.ctx).get_build_dir(),
                'hostpython')
        elif 'hostpython3' in self.ctx.recipe_build_order:
            return join(Recipe.get_recipe('hostpython3', self.ctx).get_build_dir(),
                        'native-build', 'python')
        else:
            python_recipe = self.ctx.python_recipe
            return 'python{}'.format(python_recipe.version)

    @property
    def hostpython_location(self):
        if not self.call_hostpython_via_targetpython:
            return self.real_hostpython_location
        return self.ctx.hostpython

    @property
    def folder_name(self):
        '''The name of the build folders containing this recipe.'''
        name = self.site_packages_name
        if name is None:
            name = self.name
        return name

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(PythonRecipe, self).get_recipe_env(arch, with_flags_in_cc)

        env['PYTHONNOUSERSITE'] = '1'

        if not self.call_hostpython_via_targetpython:
            # sets python headers/linkages...depending on python's recipe
            python_version = self.ctx.python_recipe.version
            python_short_version = '.'.join(python_version.split('.')[:2])
            if 'python2' in self.ctx.recipe_build_order:
                env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
                env['CFLAGS'] += ' -I' + env[
                    'PYTHON_ROOT'] + '/include/python2.7'
                env['LDFLAGS'] += (
                    ' -L' + env['PYTHON_ROOT'] + '/lib' + ' -lpython2.7')
            elif self.ctx.python_recipe.from_crystax:
                ndk_dir_python = join(self.ctx.ndk_dir, 'sources',
                                      'python', python_version)
                env['CFLAGS'] += ' -I{} '.format(
                    join(ndk_dir_python, 'include',
                         'python'))
                env['LDFLAGS'] += ' -L{}'.format(
                    join(ndk_dir_python, 'libs', arch.arch))
                env['LDFLAGS'] += ' -lpython{}m'.format(python_short_version)
            elif 'python3' in self.ctx.recipe_build_order:
                env['CFLAGS'] += ' -I{}'.format(self.ctx.python_recipe.include_root(arch.arch))
                env['LDFLAGS'] += ' -L{} -lpython{}m'.format(
                    self.ctx.python_recipe.link_root(arch.arch),
                    self.ctx.python_recipe.major_minor_version_string)

            hppath = []
            hppath.append(join(dirname(self.hostpython_location), 'Lib'))
            hppath.append(join(hppath[0], 'site-packages'))
            builddir = join(dirname(self.hostpython_location), 'build')
            hppath += [join(builddir, d) for d in listdir(builddir)
                       if isdir(join(builddir, d))]
            if 'PYTHONPATH' in env:
                env['PYTHONPATH'] = ':'.join(hppath + [env['PYTHONPATH']])
            else:
                env['PYTHONPATH'] = ':'.join(hppath)
        return env

    def should_build(self, arch):
        name = self.folder_name
        if self.ctx.has_package(name):
            info('Python package already exists in site-packages')
            return False
        info('{} apparently isn\'t already in site-packages'.format(name))
        return True

    def build_arch(self, arch):
        '''Install the Python module by calling setup.py install with
        the target Python dir.'''
        super(PythonRecipe, self).build_arch(arch)
        self.install_python_package(arch)

    def install_python_package(self, arch, name=None, env=None, is_dir=True):
        '''Automate the installation of a Python package (or a cython
        package where the cython components are pre-built).'''
        # arch = self.filtered_archs[0]  # old kivy-ios way
        if name is None:
            name = self.name
        if env is None:
            env = self.get_recipe_env(arch)

        info('Installing {} into site-packages'.format(self.name))

        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.hostpython_location)

            if (self.ctx.python_recipe.from_crystax or
                self.ctx.python_recipe.name == 'python3'):
                hpenv = env.copy()
                shprint(hostpython, 'setup.py', 'install', '-O2',
                        '--root={}'.format(self.ctx.get_python_install_dir()),
                        '--install-lib=.',
                        _env=hpenv, *self.setup_extra_args)
            elif self.call_hostpython_via_targetpython:
                shprint(hostpython, 'setup.py', 'install', '-O2', _env=env,
                        *self.setup_extra_args)
            else:
                hppath = join(dirname(self.hostpython_location), 'Lib',
                              'site-packages')
                hpenv = env.copy()
                if 'PYTHONPATH' in hpenv:
                    hpenv['PYTHONPATH'] = ':'.join([hppath] +
                                                   hpenv['PYTHONPATH'].split(':'))
                else:
                    hpenv['PYTHONPATH'] = hppath
                shprint(hostpython, 'setup.py', 'install', '-O2',
                        '--root={}'.format(self.ctx.get_python_install_dir()),
                        '--install-lib=lib/python2.7/site-packages',
                        _env=hpenv, *self.setup_extra_args)

            # If asked, also install in the hostpython build dir
            if self.install_in_hostpython:
                self.install_hostpython_package(arch)

    def get_hostrecipe_env(self, arch):
        env = environ.copy()
        env['PYTHONPATH'] = join(dirname(self.real_hostpython_location), 'Lib', 'site-packages')
        return env

    def install_hostpython_package(self, arch):
        env = self.get_hostrecipe_env(arch)
        real_hostpython = sh.Command(self.real_hostpython_location)
        shprint(real_hostpython, 'setup.py', 'install', '-O2',
                '--root={}'.format(dirname(self.real_hostpython_location)),
                '--install-lib=Lib/site-packages',
                _env=env, *self.setup_extra_args)


class CompiledComponentsPythonRecipe(PythonRecipe):
    pre_build_ext = False

    build_cmd = 'build_ext'

    def build_arch(self, arch):
        '''Build any cython components, then install the Python module by
        calling setup.py install with the target Python dir.
        '''
        Recipe.build_arch(self, arch)
        self.build_compiled_components(arch)
        self.install_python_package(arch)

    def build_compiled_components(self, arch):
        info('Building compiled components in {}'.format(self.name))

        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.hostpython_location)
            if self.install_in_hostpython:
                shprint(hostpython, 'setup.py', 'clean', '--all', _env=env)
            shprint(hostpython, 'setup.py', self.build_cmd, '-v',
                    _env=env, *self.setup_extra_args)
            build_dir = glob.glob('build/lib.*')[0]
            shprint(sh.find, build_dir, '-name', '"*.o"', '-exec',
                    env['STRIP'], '{}', ';', _env=env)

    def install_hostpython_package(self, arch):
        env = self.get_hostrecipe_env(arch)
        self.rebuild_compiled_components(arch, env)
        super(CompiledComponentsPythonRecipe, self).install_hostpython_package(arch)

    def rebuild_compiled_components(self, arch, env):
        info('Rebuilding compiled components in {}'.format(self.name))

        hostpython = sh.Command(self.real_hostpython_location)
        shprint(hostpython, 'setup.py', 'clean', '--all', _env=env)
        shprint(hostpython, 'setup.py', self.build_cmd, '-v', _env=env,
                *self.setup_extra_args)


class CppCompiledComponentsPythonRecipe(CompiledComponentsPythonRecipe):
    """ Extensions that require the cxx-stl """
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(CppCompiledComponentsPythonRecipe, self).get_recipe_env(arch)
        keys = dict(
            ctx=self.ctx,
            arch=arch,
            arch_noeabi=arch.arch.replace('eabi', '')
        )
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        env['CFLAGS'] += (
            " -I{ctx.ndk_dir}/platforms/android-{ctx.android_api}/arch-{arch_noeabi}/usr/include" +
            " -I{ctx.ndk_dir}/sources/cxx-stl/gnu-libstdc++/{ctx.toolchain_version}/include" +
            " -I{ctx.ndk_dir}/sources/cxx-stl/gnu-libstdc++/{ctx.toolchain_version}/libs/{arch.arch}/include").format(**keys)
        env['CXXFLAGS'] = env['CFLAGS'] + ' -frtti -fexceptions'
        env['LDFLAGS'] += (
            " -L{ctx.ndk_dir}/sources/cxx-stl/gnu-libstdc++/{ctx.toolchain_version}/libs/{arch.arch}" +
            " -lgnustl_shared").format(**keys)

        return env

    def build_compiled_components(self, arch):
        super(CppCompiledComponentsPythonRecipe, self).build_compiled_components(arch)

        # Copy libgnustl_shared.so
        with current_directory(self.get_build_dir(arch.arch)):
            sh.cp(
                "{ctx.ndk_dir}/sources/cxx-stl/gnu-libstdc++/{ctx.toolchain_version}/libs/{arch.arch}/libgnustl_shared.so".format(ctx=self.ctx, arch=arch),
                self.ctx.get_libs_dir(arch.arch)
            )


class CythonRecipe(PythonRecipe):
    pre_build_ext = False
    cythonize = True
    cython_args = []
    call_hostpython_via_targetpython = False

    def __init__(self, *args, **kwargs):
        super(CythonRecipe, self).__init__(*args, **kwargs)
        depends = self.depends
        depends.append(('python2', 'python3', 'python3crystax'))
        depends = list(set(depends))
        self.depends = depends

    def build_arch(self, arch):
        '''Build any cython components, then install the Python module by
        calling setup.py install with the target Python dir.
        '''
        Recipe.build_arch(self, arch)
        self.build_cython_components(arch)
        self.install_python_package(arch)

    def build_cython_components(self, arch):
        info('Cythonizing anything necessary in {}'.format(self.name))

        env = self.get_recipe_env(arch)

        if self.ctx.python_recipe.from_crystax:
            command = sh.Command('python{}'.format(self.ctx.python_recipe.version))
            site_packages_dirs = command(
                '-c', 'import site; print("\\n".join(site.getsitepackages()))')
            site_packages_dirs = site_packages_dirs.stdout.decode('utf-8').split('\n')
            if 'PYTHONPATH' in env:
                env['PYTHONPATH'] = env['PYTHONPATH'] + ':{}'.format(':'.join(site_packages_dirs))
            else:
                env['PYTHONPATH'] = ':'.join(site_packages_dirs)

        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)
            shprint(hostpython, '-c', 'import sys; print(sys.path)', _env=env)
            print('cwd is', realpath(curdir))
            info('Trying first build of {} to get cython files: this is '
                 'expected to fail'.format(self.name))

            manually_cythonise = False
            try:
                shprint(hostpython, 'setup.py', 'build_ext', '-v', _env=env,
                        *self.setup_extra_args)
            except sh.ErrorReturnCode_1:
                print()
                info('{} first build failed (as expected)'.format(self.name))
                manually_cythonise = True

            if manually_cythonise:
                self.cythonize_build(env=env)
                shprint(hostpython, 'setup.py', 'build_ext', '-v', _env=env,
                        _tail=20, _critical=True, *self.setup_extra_args)
            else:
                info('First build appeared to complete correctly, skipping manual'
                     'cythonising.')

            if 'python2' in self.ctx.recipe_build_order:
                info('Stripping object files')
                build_lib = glob.glob('./build/lib*')
                shprint(sh.find, build_lib[0], '-name', '*.o', '-exec',
                        env['STRIP'], '{}', ';', _env=env)

            else:  # python3crystax or python3
                info('Stripping object files')
                shprint(sh.find, '.', '-iname', '*.so', '-exec',
                        '/usr/bin/echo', '{}', ';', _env=env)
                shprint(sh.find, '.', '-iname', '*.so', '-exec',
                        env['STRIP'].split(' ')[0], '--strip-unneeded',
                        # '/usr/bin/strip', '--strip-unneeded',
                        '{}', ';', _env=env)

    def cythonize_file(self, env, build_dir, filename):
        short_filename = filename
        if filename.startswith(build_dir):
            short_filename = filename[len(build_dir) + 1:]
        info(u"Cythonize {}".format(short_filename))
        cyenv = env.copy()
        if 'CYTHONPATH' in cyenv:
            cyenv['PYTHONPATH'] = cyenv['CYTHONPATH']
        elif 'PYTHONPATH' in cyenv:
            del cyenv['PYTHONPATH']
        if 'PYTHONNOUSERSITE' in cyenv:
            cyenv.pop('PYTHONNOUSERSITE')
        cython = 'cython' if self.ctx.python_recipe.from_crystax else self.ctx.cython
        cython_command = sh.Command(cython)
        shprint(cython_command, filename, *self.cython_args, _env=cyenv)

    def cythonize_build(self, env, build_dir="."):
        if not self.cythonize:
            info('Running cython cancelled per recipe setting')
            return
        info('Running cython where appropriate')
        for root, dirnames, filenames in walk("."):
            for filename in fnmatch.filter(filenames, "*.pyx"):
                self.cythonize_file(env, build_dir, join(root, filename))

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        env = super(CythonRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{} '.format(
            self.ctx.get_libs_dir(arch.arch) +
            ' -L{} '.format(self.ctx.libs_dir) +
            ' -L{}'.format(join(self.ctx.bootstrap.build_dir, 'obj', 'local',
                                arch.arch)))
        if self.ctx.python_recipe.from_crystax:
            env['LDFLAGS'] = (env['LDFLAGS'] +
                              ' -L{}'.format(join(self.ctx.bootstrap.build_dir, 'libs', arch.arch)))

        if self.ctx.python_recipe.from_crystax or self.ctx.python_recipe.name == 'python3':
            env['LDSHARED'] = env['CC'] + ' -shared'
        else:
            env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink.sh')
        # shprint(sh.whereis, env['LDSHARED'], _env=env)
        env['LIBLINK'] = 'NOTNONE'
        env['NDKPLATFORM'] = self.ctx.ndk_platform
        if self.ctx.copy_libs:
            env['COPYLIBS'] = '1'

        # Every recipe uses its own liblink path, object files are
        # collected and biglinked later
        liblink_path = join(self.get_build_container_dir(arch.arch),
                            'objects_{}'.format(self.name))
        env['LIBLINK_PATH'] = liblink_path
        ensure_dir(liblink_path)

        return env


class TargetPythonRecipe(Recipe):
    '''Class for target python recipes. Sets ctx.python_recipe to point to
    itself, so as to know later what kind of Python was built or used.'''

    from_crystax = False
    '''True if the python is used from CrystaX, False otherwise (i.e. if
    it is built by p4a).'''

    def __init__(self, *args, **kwargs):
        self._ctx = None
        super(TargetPythonRecipe, self).__init__(*args, **kwargs)

    def prebuild_arch(self, arch):
        super(TargetPythonRecipe, self).prebuild_arch(arch)
        if self.from_crystax and self.ctx.ndk != 'crystax':
            error('The {} recipe can only be built when '
                  'using the CrystaX NDK. Exiting.'.format(self.name))
            exit(1)
        self.ctx.python_recipe = self

    def include_root(self, arch):
        '''The root directory from which to include headers.'''
        raise NotImplementedError('Not implemented in TargetPythonRecipe')

    def link_root(self):
        raise NotImplementedError('Not implemented in TargetPythonRecipe')

    @property
    def major_minor_version_string(self):
        from distutils.version import LooseVersion
        return '.'.join([str(v) for v in LooseVersion(self.version).version[:2]])

    def create_python_bundle(self, dirn, arch):
        """
        Create a packaged python bundle in the target directory, by
        copying all the modules and standard library to the right
        place.
        """
        raise NotImplementedError('{} does not implement create_python_bundle'.format(self))

    def reduce_object_file_names(self, dirn):
        """Recursively renames all files named XXX.cpython-...-linux-gnu.so"
        to "XXX.so", i.e. removing the erroneous architecture name
        coming from the local system.
        """
        py_so_files = shprint(sh.find, dirn, '-iname', '*.so')
        filens = py_so_files.stdout.decode('utf-8').split('\n')[:-1]
        for filen in filens:
            file_dirname, file_basename = split(filen)
            parts = file_basename.split('.')
            if len(parts) <= 2:
                continue
            shprint(sh.mv, filen, join(file_dirname, parts[0] + '.so'))


def md5sum(filen):
    '''Calculate the md5sum of a file.
    '''
    with open(filen, 'rb') as fileh:
        md5 = hashlib.md5(fileh.read())

    return md5.hexdigest()
