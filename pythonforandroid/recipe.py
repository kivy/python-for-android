from os.path import basename, dirname, exists, isdir, isfile, join, realpath, split
import glob

import hashlib
from re import match

import sh
import shutil
import fnmatch
import urllib.request
from urllib.request import urlretrieve
from os import listdir, unlink, environ, curdir, walk
from sys import stdout
import time
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import packaging.version

from pythonforandroid.logger import (
    logger, info, warning, debug, shprint, info_main)
from pythonforandroid.util import (
    current_directory, ensure_dir, BuildInterruptingException, rmdir, move,
    touch)
from pythonforandroid.util import load_source as import_recipe


url_opener = urllib.request.build_opener()
url_orig_headers = url_opener.addheaders
urllib.request.install_opener(url_opener)


class RecipeMeta(type):
    def __new__(cls, name, bases, dct):
        if name != 'Recipe':
            if 'url' in dct:
                dct['_url'] = dct.pop('url')
            if 'version' in dct:
                dct['_version'] = dct.pop('version')

        return super().__new__(cls, name, bases, dct)


class Recipe(metaclass=RecipeMeta):
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

    sha512sum = None
    '''The sha512sum of the source from the :attr:`url`. Non-essential, but
    you should try to include this, it is used to check that the download
    finished correctly.
    '''

    blake2bsum = None
    '''The blake2bsum of the source from the :attr:`url`. Non-essential, but
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

    built_libraries = {}
    """Each recipe that builds a system library (e.g.:libffi, openssl, etc...)
    should contain a dict holding the relevant information of the library. The
    keys should be the generated libraries and the values the relative path of
    the library inside his build folder. This dict will be used to perform
    different operations:
        - copy the library into the right location, depending on if it's shared
          or static)
        - check if we have to rebuild the library

    Here an example of how it would look like for `libffi` recipe:

        - `built_libraries = {'libffi.so': '.libs'}`

    .. note:: in case that the built library resides in recipe's build
              directory, you can set the following values for the relative
              path: `'.', None or ''`
    """

    need_stl_shared = False
    '''Some libraries or python packages may need the c++_shared in APK.
    We can automatically do this for any recipe if we set this property to
    `True`'''

    stl_lib_name = 'c++_shared'
    '''
    The default STL shared lib to use: `c++_shared`.

    .. note:: Android NDK version > 17 only supports 'c++_shared', because
        starting from NDK r18 the `gnustl_shared` lib has been deprecated.
    '''

    def get_stl_library(self, arch):
        return join(
            arch.ndk_lib_dir,
            'lib{name}.so'.format(name=self.stl_lib_name),
        )

    def install_stl_lib(self, arch):
        if not self.ctx.has_lib(
            arch.arch, 'lib{name}.so'.format(name=self.stl_lib_name)
        ):
            self.install_libs(arch, self.get_stl_library(arch))

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
                if "CI" not in environ:
                    stdout.write('- Download {}\r'.format(progression))
                    stdout.flush()

            if exists(target):
                unlink(target)

            # Download item with multiple attempts (for bad connections):
            attempts = 0
            seconds = 1
            while True:
                try:
                    # jqueryui.com returns a 403 w/ the default user agent
                    # Mozilla/5.0 doesnt handle redirection for liblzma
                    url_opener.addheaders = [('User-agent', 'Wget/1.0')]
                    urlretrieve(url, target, report_hook)
                except OSError as e:
                    attempts += 1
                    if attempts >= 5:
                        raise
                    stdout.write('Download failed: {}; retrying in {} second(s)...'.format(e, seconds))
                    time.sleep(seconds)
                    seconds *= 2
                    continue
                finally:
                    url_opener.addheaders = url_orig_headers
                break
            return target
        elif parsed_url.scheme in ('git', 'git+file', 'git+ssh', 'git+http', 'git+https'):
            if not isdir(target):
                if url.startswith('git+'):
                    url = url[4:]
                # if 'version' is specified, do a shallow clone
                if self.version:
                    ensure_dir(target)
                    with current_directory(target):
                        shprint(sh.git, 'init')
                        shprint(sh.git, 'remote', 'add', 'origin', url)
                else:
                    shprint(sh.git, 'clone', '--recursive', url, target)
            with current_directory(target):
                if self.version:
                    shprint(sh.git, 'fetch', '--depth', '1', 'origin', self.version)
                    shprint(sh.git, 'checkout', self.version)
                branch = sh.git('branch', '--show-current')
                if branch:
                    shprint(sh.git, 'pull')
                    shprint(sh.git, 'pull', '--recurse-submodules')
                shprint(sh.git, 'submodule', 'update', '--recursive', '--init', '--depth', '1')
            return target

    def apply_patch(self, filename, arch, build_dir=None):
        """
        Apply a patch from the current recipe directory into the current
        build directory.

        .. versionchanged:: 0.6.0
            Add ability to apply patch from any dir via kwarg `build_dir`'''
        """
        info("Applying patch {}".format(filename))
        build_dir = build_dir if build_dir else self.get_build_dir(arch)
        filename = join(self.get_recipe_dir(), filename)
        shprint(sh.patch, "-t", "-d", build_dir, "-p1",
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

    def get_opt_depends_in_list(self, recipes):
        '''Given a list of recipe names, returns those that are also in
        self.opt_depends.
        '''
        return [recipe for recipe in recipes if recipe in self.opt_depends]

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
        expected_digests = {}
        for alg in set(hashlib.algorithms_guaranteed) | set(('md5', 'sha512', 'blake2b')):
            expected_digest = getattr(self, alg + 'sum') if hasattr(self, alg + 'sum') else None
            ma = match(u'^(.+)#' + alg + u'=([0-9a-f]{32,})$', url)
            if ma:                # fragmented URL?
                if expected_digest:
                    raise ValueError(
                        ('Received {}sum from both the {} recipe '
                         'and its url').format(alg, self.name))
                url = ma.group(1)
                expected_digest = ma.group(2)
            if expected_digest:
                expected_digests[alg] = expected_digest

        ensure_dir(join(self.ctx.packages_path, self.name))

        with current_directory(join(self.ctx.packages_path, self.name)):
            filename = shprint(sh.basename, url).stdout[:-1].decode('utf-8')

            do_download = True
            marker_filename = '.mark-{}'.format(filename)
            if exists(filename) and isfile(filename):
                if not exists(marker_filename):
                    shprint(sh.rm, filename)
                else:
                    for alg, expected_digest in expected_digests.items():
                        current_digest = algsum(alg, filename)
                        if current_digest != expected_digest:
                            debug('* Generated {}sum: {}'.format(alg,
                                                                 current_digest))
                            debug('* Expected {}sum: {}'.format(alg,
                                                                expected_digest))
                            raise ValueError(
                                ('Generated {0}sum does not match expected {0}sum '
                                 'for {1} recipe').format(alg, self.name))
                    do_download = False

            # If we got this far, we will download
            if do_download:
                debug('Downloading {} from {}'.format(self.name, url))

                shprint(sh.rm, '-f', marker_filename)
                self.download_file(self.versioned_url, filename)
                touch(marker_filename)

                if exists(filename) and isfile(filename):
                    for alg, expected_digest in expected_digests.items():
                        current_digest = algsum(alg, filename)
                        if current_digest != expected_digest:
                            debug('* Generated {}sum: {}'.format(alg,
                                                                 current_digest))
                            debug('* Expected {}sum: {}'.format(alg,
                                                                expected_digest))
                            raise ValueError(
                                ('Generated {0}sum does not match expected {0}sum '
                                 'for {1} recipe').format(alg, self.name))
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
            rmdir(build_dir)
            ensure_dir(build_dir)
            shprint(sh.cp, '-a', user_dir, self.get_build_dir(arch))
            return

        if self.url is None:
            info('Skipping {} unpack as no URL is set'.format(self.name))
            return

        filename = shprint(
            sh.basename, self.versioned_url).stdout[:-1].decode('utf-8')
        ma = match(u'^(.+)#[a-z0-9_]{3,}=([0-9a-f]{32,})$', filename)
        if ma:                  # fragmented URL?
            filename = ma.group(1)

        with current_directory(build_dir):
            directory_name = self.get_build_dir(arch)

            if not exists(directory_name) or not isdir(directory_name):
                extraction_filename = join(
                    self.ctx.packages_path, self.name, filename)
                if isfile(extraction_filename):
                    if extraction_filename.endswith(('.zip', '.whl')):
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
                            move(root_directory, directory_name)
                    elif extraction_filename.endswith(
                            ('.tar.gz', '.tgz', '.tar.bz2', '.tbz2', '.tar.xz', '.txz')):
                        sh.tar('xf', extraction_filename)
                        root_directory = sh.tar('tf', extraction_filename).stdout.decode(
                                'utf-8').split('\n')[0].split('/')[0]
                        if root_directory != basename(directory_name):
                            move(root_directory, directory_name)
                    else:
                        raise Exception(
                            'Could not extract {} download, it must be .zip, '
                            '.tar.gz or .tar.bz2 or .tar.xz'.format(extraction_filename))
                elif isdir(extraction_filename):
                    ensure_dir(directory_name)
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
        env = arch.get_env(with_flags_in_cc=with_flags_in_cc)
        return env

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

    def apply_patches(self, arch, build_dir=None):
        '''Apply any patches for the Recipe.

        .. versionchanged:: 0.6.0
            Add ability to apply patches from any dir via kwarg `build_dir`'''
        if self.patches:
            info_main('Applying patches for {}[{}]'
                      .format(self.name, arch.arch))

            if self.is_patched(arch):
                info_main('{} already patched, skipping'.format(self.name))
                return

            build_dir = build_dir if build_dir else self.get_build_dir(arch.arch)
            for patch in self.patches:
                if isinstance(patch, (tuple, list)):
                    patch, patch_check = patch
                    if not patch_check(arch=arch, recipe=self):
                        continue

                self.apply_patch(
                        patch.format(version=self.version, arch=arch.arch),
                        arch.arch, build_dir=build_dir)

            touch(join(build_dir, '.patched'))

    def should_build(self, arch):
        '''Should perform any necessary test and return True only if it needs
        building again. Per default we implement a library test, in case that
        we detect so.

        '''
        if self.built_libraries:
            return not all(
                exists(lib) for lib in self.get_libraries(arch.arch)
            )
        return True

    def build_arch(self, arch):
        '''Run any build tasks for the Recipe. By default, this checks if
        any build_archname methods exist for the archname of the current
        architecture, and runs them if so.'''
        build = "build_{}".format(arch.arch)
        if hasattr(self, build):
            getattr(self, build)()

    def install_libraries(self, arch):
        '''This method is always called after `build_arch`. In case that we
        detect a library recipe, defined by the class attribute
        `built_libraries`, we will copy all defined libraries into the
         right location.
        '''
        if not self.built_libraries:
            return
        shared_libs = [
            lib for lib in self.get_libraries(arch) if lib.endswith(".so")
        ]
        self.install_libs(arch, *shared_libs)

    def postbuild_arch(self, arch):
        '''Run any post-build tasks for the Recipe. By default, this checks if
        any postbuild_archname methods exist for the archname of the
        current architecture, and runs them if so.
        '''
        postbuild = "postbuild_{}".format(arch.arch)
        if hasattr(self, postbuild):
            getattr(self, postbuild)()

        if self.need_stl_shared:
            self.install_stl_lib(arch)

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
            rmdir(directory)

        # Delete any Python distributions to ensure the recipe build
        # doesn't persist in site-packages
        rmdir(self.ctx.python_installs_dir)

    def install_libs(self, arch, *libs):
        libs_dir = self.ctx.get_libs_dir(arch.arch)
        if not libs:
            warning('install_libs called with no libraries to install!')
            return
        args = libs + (libs_dir,)
        shprint(sh.cp, *args)

    def has_libs(self, arch, *libs):
        return all(map(lambda lib: self.ctx.has_lib(arch.arch, lib), libs))

    def get_libraries(self, arch_name, in_context=False):
        """Return the full path of the library depending on the architecture.
        Per default, the build library path it will be returned, unless
        `get_libraries` has been called with kwarg `in_context` set to
        True.

        .. note:: this method should be used for library recipes only
        """
        recipe_libs = set()
        if not self.built_libraries:
            return recipe_libs
        for lib, rel_path in self.built_libraries.items():
            if not in_context:
                abs_path = join(self.get_build_dir(arch_name), rel_path, lib)
                if rel_path in {".", "", None}:
                    abs_path = join(self.get_build_dir(arch_name), lib)
            else:
                abs_path = join(self.ctx.get_libs_dir(arch_name), lib)
            recipe_libs.add(abs_path)
        return recipe_libs

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
        name = name.lower()
        if not hasattr(cls, "recipes"):
            cls.recipes = {}
        if name in cls.recipes:
            return cls.recipes[name]

        recipe_file = None
        for recipes_dir in cls.recipe_dirs(ctx):
            if not exists(recipes_dir):
                continue
            # Find matching folder (may differ in case):
            for subfolder in listdir(recipes_dir):
                if subfolder.lower() == name:
                    recipe_file = join(recipes_dir, subfolder, '__init__.py')
                    if exists(recipe_file):
                        name = subfolder  # adapt to actual spelling
                        break
                    recipe_file = None
            if recipe_file is not None:
                break

        else:
            raise ValueError('Recipe does not exist: {}'.format(name))

        mod = import_recipe('pythonforandroid.recipes.{}'.format(name), recipe_file)
        if len(logger.handlers) > 1:
            logger.removeHandler(logger.handlers[1])
        recipe = mod.recipe
        recipe.ctx = ctx
        cls.recipes[name.lower()] = recipe
        return recipe


class IncludedFilesBehaviour(object):
    '''Recipe mixin class that will automatically unpack files included in
    the recipe directory.'''
    src_filename = None

    def prepare_build_dir(self, arch):
        if self.src_filename is None:
            raise BuildInterruptingException(
                'IncludedFilesBehaviour failed: no src_filename specified')
        rmdir(self.get_build_dir(arch))
        shprint(sh.cp, '-a', join(self.get_recipe_dir(), self.src_filename),
                self.get_build_dir(arch))


class BootstrapNDKRecipe(Recipe):
    '''A recipe class for recipes built in an Android project jni dir with
    an Android.mk. These are not cached separatly, but built in the
    bootstrap's own building directory.

    To build an NDK project which is not part of the bootstrap, see
    :class:`~pythonforandroid.recipe.NDKRecipe`.

    To link with python, call the method :meth:`get_recipe_env`
    with the kwarg *with_python=True*.
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

    def get_recipe_env(self, arch=None, with_flags_in_cc=True, with_python=False):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        if not with_python:
            return env

        env['PYTHON_INCLUDE_ROOT'] = self.ctx.python_recipe.include_root(arch.arch)
        env['PYTHON_LINK_ROOT'] = self.ctx.python_recipe.link_root(arch.arch)
        env['EXTRA_LDLIBS'] = ' -lpython{}'.format(
            self.ctx.python_recipe.link_version)
        return env


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
        super().build_arch(arch)

        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(
                sh.Command(join(self.ctx.ndk_dir, "ndk-build")),
                'V=1',
                'NDK_DEBUG=' + ("1" if self.ctx.build_as_debuggable else "0"),
                'APP_PLATFORM=android-' + str(self.ctx.ndk_api),
                'APP_ABI=' + arch.arch,
                *extra_args, _env=env
            )


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
    '''List of extra arguments to pass to setup.py'''

    depends = ['python3']
    '''
    .. note:: it's important to keep this depends as a class attribute outside
              `__init__` because sometimes we only initialize the class, so the
              `__init__` call won't be called and the deps would be missing
              (which breaks the dependency graph computation)

    .. warning:: don't forget to call `super().__init__()` in any recipe's
                 `__init__`, or otherwise it may not be ensured that it depends
                 on python2 or python3 which can break the dependency graph
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'python3' not in self.depends:
            # We ensure here that the recipe depends on python even it overrode
            # `depends`. We only do this if it doesn't already depend on any
            # python, since some recipes intentionally don't depend on/work
            # with all python variants
            depends = self.depends
            depends.append('python3')
            depends = list(set(depends))
            self.depends = depends

    def clean_build(self, arch=None):
        super().clean_build(arch=arch)
        name = self.folder_name
        python_install_dirs = glob.glob(join(self.ctx.python_installs_dir, '*'))
        for python_install in python_install_dirs:
            site_packages_dir = glob.glob(join(python_install, 'lib', 'python*',
                                               'site-packages'))
            if site_packages_dir:
                build_dir = join(site_packages_dir[0], name)
                if exists(build_dir):
                    info('Deleted {}'.format(build_dir))
                    rmdir(build_dir)

    @property
    def real_hostpython_location(self):
        host_name = 'host{}'.format(self.ctx.python_recipe.name)
        if host_name == 'hostpython3':
            python_recipe = Recipe.get_recipe(host_name, self.ctx)
            return python_recipe.python_exe
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
        env = super().get_recipe_env(arch, with_flags_in_cc)

        env['PYTHONNOUSERSITE'] = '1'

        # Set the LANG, this isn't usually important but is a better default
        # as it occasionally matters how Python e.g. reads files
        env['LANG'] = "en_GB.UTF-8"

        if not self.call_hostpython_via_targetpython:
            env['CFLAGS'] += ' -I{}'.format(
                self.ctx.python_recipe.include_root(arch.arch)
            )
            env['LDFLAGS'] += ' -L{} -lpython{}'.format(
                self.ctx.python_recipe.link_root(arch.arch),
                self.ctx.python_recipe.link_version,
            )

            hppath = []
            hppath.append(join(dirname(self.hostpython_location), 'Lib'))
            hppath.append(join(hppath[0], 'site-packages'))
            builddir = join(dirname(self.hostpython_location), 'build')
            if exists(builddir):
                hppath += [join(builddir, d) for d in listdir(builddir)
                           if isdir(join(builddir, d))]
            if len(hppath) > 0:
                if 'PYTHONPATH' in env:
                    env['PYTHONPATH'] = ':'.join(hppath + [env['PYTHONPATH']])
                else:
                    env['PYTHONPATH'] = ':'.join(hppath)
        return env

    def should_build(self, arch):
        name = self.folder_name
        if self.ctx.has_package(name, arch):
            info('Python package already exists in site-packages')
            return False
        info('{} apparently isn\'t already in site-packages'.format(name))
        return True

    def build_arch(self, arch):
        '''Install the Python module by calling setup.py install with
        the target Python dir.'''
        super().build_arch(arch)
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

        hostpython = sh.Command(self.hostpython_location)
        hpenv = env.copy()
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(hostpython, 'setup.py', 'install', '-O2',
                    '--root={}'.format(self.ctx.get_python_install_dir(arch.arch)),
                    '--install-lib=.',
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
        hostpython = sh.Command(self.hostpython_location)
        with current_directory(self.get_build_dir(arch.arch)):
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
        super().install_hostpython_package(arch)

    def rebuild_compiled_components(self, arch, env):
        info('Rebuilding compiled components in {}'.format(self.name))

        hostpython = sh.Command(self.real_hostpython_location)
        shprint(hostpython, 'setup.py', 'clean', '--all', _env=env)
        shprint(hostpython, 'setup.py', self.build_cmd, '-v', _env=env,
                *self.setup_extra_args)


class CppCompiledComponentsPythonRecipe(CompiledComponentsPythonRecipe):
    """ Extensions that require the cxx-stl """
    call_hostpython_via_targetpython = False
    need_stl_shared = True


class CythonRecipe(PythonRecipe):
    pre_build_ext = False
    cythonize = True
    cython_args = []
    call_hostpython_via_targetpython = False

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

        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)
            shprint(hostpython, '-c', 'import sys; print(sys.path)', _env=env)
            debug('cwd is {}'.format(realpath(curdir)))
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

            if not self.ctx.with_debug_symbols:
                self.strip_object_files(arch, env)

    def strip_object_files(self, arch, env, build_dir=None):
        if build_dir is None:
            build_dir = self.get_build_dir(arch.arch)
        with current_directory(build_dir):
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
        python_command = sh.Command("python{}".format(
            self.ctx.python_recipe.major_minor_version_string.split(".")[0]
        ))
        shprint(python_command, "-c"
                "import sys; from Cython.Compiler.Main import setuptools_main; sys.exit(setuptools_main());",
                filename, *self.cython_args, _env=cyenv)

    def cythonize_build(self, env, build_dir="."):
        if not self.cythonize:
            info('Running cython cancelled per recipe setting')
            return
        info('Running cython where appropriate')
        for root, dirnames, filenames in walk("."):
            for filename in fnmatch.filter(filenames, "*.pyx"):
                self.cythonize_file(env, build_dir, join(root, filename))

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{} '.format(
            self.ctx.get_libs_dir(arch.arch) +
            ' -L{} '.format(self.ctx.libs_dir) +
            ' -L{}'.format(join(self.ctx.bootstrap.build_dir, 'obj', 'local',
                                arch.arch)))

        env['LDSHARED'] = env['CC'] + ' -shared'
        # shprint(sh.whereis, env['LDSHARED'], _env=env)
        env['LIBLINK'] = 'NOTNONE'
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

    def __init__(self, *args, **kwargs):
        self._ctx = None
        super().__init__(*args, **kwargs)

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        self.ctx.python_recipe = self

    def include_root(self, arch):
        '''The root directory from which to include headers.'''
        raise NotImplementedError('Not implemented in TargetPythonRecipe')

    def link_root(self):
        raise NotImplementedError('Not implemented in TargetPythonRecipe')

    @property
    def major_minor_version_string(self):
        parsed_version = packaging.version.parse(self.version)
        return f"{parsed_version.major}.{parsed_version.minor}"

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
            # PySide6 libraries end with .abi3.so
            if parts[1] == "abi3":
                continue
            move(filen, join(file_dirname, parts[0] + '.so'))


def algsum(alg, filen):
    '''Calculate the digest of a file.
    '''
    with open(filen, 'rb') as fileh:
        digest = getattr(hashlib, alg)(fileh.read())

    return digest.hexdigest()
