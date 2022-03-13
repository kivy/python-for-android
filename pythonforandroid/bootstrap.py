import functools
import glob
import importlib
import os
from os.path import (join, dirname, isdir, normpath, splitext, basename)
from os import listdir, walk, sep
import sh
import shlex
import shutil

from pythonforandroid.logger import (shprint, info, logger, debug)
from pythonforandroid.util import (
    current_directory, ensure_dir, temp_directory, BuildInterruptingException)
from pythonforandroid.recipe import Recipe


def copy_files(src_root, dest_root, override=True, symlink=False):
    for root, dirnames, filenames in walk(src_root):
        for filename in filenames:
            subdir = normpath(root.replace(src_root, ""))
            if subdir.startswith(sep):  # ensure it is relative
                subdir = subdir[1:]
            dest_dir = join(dest_root, subdir)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            src_file = join(root, filename)
            dest_file = join(dest_dir, filename)
            if os.path.isfile(src_file):
                if override and os.path.exists(dest_file):
                    os.unlink(dest_file)
                if not os.path.exists(dest_file):
                    if symlink:
                        os.symlink(src_file, dest_file)
                    else:
                        shutil.copy(src_file, dest_file)
            else:
                os.makedirs(dest_file)


default_recipe_priorities = [
    "webview", "sdl2", "service_only"  # last is highest
]
# ^^ NOTE: these are just the default priorities if no special rules
# apply (which you can find in the code below), so basically if no
# known graphical lib or web lib is used - in which case service_only
# is the most reasonable guess.


def _cmp_bootstraps_by_priority(a, b):
    def rank_bootstrap(bootstrap):
        """ Returns a ranking index for each bootstrap,
            with higher priority ranked with higher number. """
        if bootstrap.name in default_recipe_priorities:
            return default_recipe_priorities.index(bootstrap.name) + 1
        return 0

    # Rank bootstraps in order:
    rank_a = rank_bootstrap(a)
    rank_b = rank_bootstrap(b)
    if rank_a != rank_b:
        return (rank_b - rank_a)
    else:
        if a.name < b.name:  # alphabetic sort for determinism
            return -1
        else:
            return 1


class Bootstrap:
    '''An Android project template, containing recipe stuff for
    compilation and templated fields for APK info.
    '''
    name = ''
    jni_subdir = '/jni'
    ctx = None

    bootstrap_dir = None

    build_dir = None
    dist_name = None
    distribution = None

    # All bootstraps should include Python in some way:
    recipe_depends = ['python3', 'android']

    can_be_chosen_automatically = True
    '''Determines whether the bootstrap can be chosen as one that
    satisfies user requirements. If False, it will not be returned
    from Bootstrap.get_bootstrap_from_recipes.
    '''

    # Other things a Bootstrap might need to track (maybe separately):
    # ndk_main.c
    # whitelist.txt
    # blacklist.txt

    @property
    def dist_dir(self):
        '''The dist dir at which to place the finished distribution.'''
        if self.distribution is None:
            raise BuildInterruptingException(
                'Internal error: tried to access {}.dist_dir, but {}.distribution '
                'is None'.format(self, self))
        return self.distribution.dist_dir

    @property
    def jni_dir(self):
        return self.name + self.jni_subdir

    def check_recipe_choices(self):
        '''Checks what recipes are being built to see which of the alternative
        and optional dependencies are being used,
        and returns a list of these.'''
        recipes = []
        built_recipes = self.ctx.recipe_build_order or []
        for recipe in self.recipe_depends:
            if isinstance(recipe, (tuple, list)):
                for alternative in recipe:
                    if alternative in built_recipes:
                        recipes.append(alternative)
                        break
        return sorted(recipes)

    def get_build_dir_name(self):
        choices = self.check_recipe_choices()
        dir_name = '-'.join([self.name] + choices)
        return dir_name

    def get_build_dir(self):
        return join(self.ctx.build_dir, 'bootstrap_builds', self.get_build_dir_name())

    def get_dist_dir(self, name):
        return join(self.ctx.dist_dir, name)

    @property
    def name(self):
        modname = self.__class__.__module__
        return modname.split(".", 2)[-1]

    def get_bootstrap_dirs(self):
        """get all bootstrap directories, following the MRO path"""

        # get all bootstrap names along the __mro__, cutting off Bootstrap and object
        classes = self.__class__.__mro__[:-2]
        bootstrap_names = [cls.name for cls in classes] + ['common']
        bootstrap_dirs = [
            join(self.ctx.root_dir, 'bootstraps', bootstrap_name)
            for bootstrap_name in reversed(bootstrap_names)
        ]
        return bootstrap_dirs

    def _copy_in_final_files(self):
        if self.name == "sdl2":
            # Get the paths for copying SDL2's java source code:
            sdl2_recipe = Recipe.get_recipe("sdl2", self.ctx)
            sdl2_build_dir = sdl2_recipe.get_jni_dir()
            src_dir = join(sdl2_build_dir, "SDL", "android-project",
                           "app", "src", "main", "java",
                           "org", "libsdl", "app")
            target_dir = join(self.dist_dir, 'src', 'main', 'java', 'org',
                              'libsdl', 'app')

            # Do actual copying:
            info('Copying in SDL2 .java files from: ' + str(src_dir))
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            copy_files(src_dir, target_dir, override=True)

    def prepare_build_dir(self):
        """Ensure that a build dir exists for the recipe. This same single
        dir will be used for building all different archs."""
        bootstrap_dirs = self.get_bootstrap_dirs()
        # now do a cumulative copy of all bootstrap dirs
        self.build_dir = self.get_build_dir()
        for bootstrap_dir in bootstrap_dirs:
            copy_files(join(bootstrap_dir, 'build'), self.build_dir, symlink=self.ctx.symlink_bootstrap_files)

        with current_directory(self.build_dir):
            with open('project.properties', 'w') as fileh:
                fileh.write('target=android-{}'.format(self.ctx.android_api))

    def prepare_dist_dir(self):
        ensure_dir(self.dist_dir)

    def assemble_distribution(self):
        ''' Copies all the files into the distribution (this function is
            overridden by the specific bootstrap classes to do this)
            and add in the distribution info.
        '''
        self._copy_in_final_files()
        self.distribution.save_info(self.dist_dir)

    @classmethod
    def all_bootstraps(cls):
        '''Find all the available bootstraps and return them.'''
        forbidden_dirs = ('__pycache__', 'common')
        bootstraps_dir = join(dirname(__file__), 'bootstraps')
        result = set()
        for name in listdir(bootstraps_dir):
            if name in forbidden_dirs:
                continue
            filen = join(bootstraps_dir, name)
            if isdir(filen):
                result.add(name)
        return result

    @classmethod
    def get_usable_bootstraps_for_recipes(cls, recipes, ctx):
        '''Returns all bootstrap whose recipe requirements do not conflict
        with the given recipes, in no particular order.'''
        info('Trying to find a bootstrap that matches the given recipes.')
        bootstraps = [cls.get_bootstrap(name, ctx)
                      for name in cls.all_bootstraps()]
        acceptable_bootstraps = set()

        # Find out which bootstraps are acceptable:
        for bs in bootstraps:
            if not bs.can_be_chosen_automatically:
                continue
            possible_dependency_lists = expand_dependencies(bs.recipe_depends, ctx)
            for possible_dependencies in possible_dependency_lists:
                ok = True
                # Check if the bootstap's dependencies have an internal conflict:
                for recipe in possible_dependencies:
                    recipe = Recipe.get_recipe(recipe, ctx)
                    if any(conflict in recipes for conflict in recipe.conflicts):
                        ok = False
                        break
                # Check if bootstrap's dependencies conflict with chosen
                # packages:
                for recipe in recipes:
                    try:
                        recipe = Recipe.get_recipe(recipe, ctx)
                    except ValueError:
                        conflicts = []
                    else:
                        conflicts = recipe.conflicts
                    if any(conflict in possible_dependencies
                            for conflict in conflicts):
                        ok = False
                        break
                if ok and bs not in acceptable_bootstraps:
                    acceptable_bootstraps.add(bs)

        info('Found {} acceptable bootstraps: {}'.format(
            len(acceptable_bootstraps),
            [bs.name for bs in acceptable_bootstraps]))
        return acceptable_bootstraps

    @classmethod
    def get_bootstrap_from_recipes(cls, recipes, ctx):
        '''Picks a single recommended default bootstrap out of
           all_usable_bootstraps_from_recipes() for the given reicpes,
           and returns it.'''

        known_web_packages = {"flask"}  # to pick webview over service_only
        recipes_with_deps_lists = expand_dependencies(recipes, ctx)
        acceptable_bootstraps = cls.get_usable_bootstraps_for_recipes(
            recipes, ctx
        )

        def have_dependency_in_recipes(dep):
            for dep_list in recipes_with_deps_lists:
                if dep in dep_list:
                    return True
            return False

        # Special rule: return SDL2 bootstrap if there's an sdl2 dep:
        if (have_dependency_in_recipes("sdl2") and
                "sdl2" in [b.name for b in acceptable_bootstraps]
                ):
            info('Using sdl2 bootstrap since it is in dependencies')
            return cls.get_bootstrap("sdl2", ctx)

        # Special rule: return "webview" if we depend on common web recipe:
        for possible_web_dep in known_web_packages:
            if have_dependency_in_recipes(possible_web_dep):
                # We have a web package dep!
                if "webview" in [b.name for b in acceptable_bootstraps]:
                    info('Using webview bootstrap since common web packages '
                         'were found {}'.format(
                             known_web_packages.intersection(recipes)
                         ))
                    return cls.get_bootstrap("webview", ctx)

        prioritized_acceptable_bootstraps = sorted(
            list(acceptable_bootstraps),
            key=functools.cmp_to_key(_cmp_bootstraps_by_priority)
        )

        if prioritized_acceptable_bootstraps:
            info('Using the highest ranked/first of these: {}'
                 .format(prioritized_acceptable_bootstraps[0].name))
            return prioritized_acceptable_bootstraps[0]
        return None

    @classmethod
    def get_bootstrap(cls, name, ctx):
        '''Returns an instance of a bootstrap with the given name.

        This is the only way you should access a bootstrap class, as
        it sets the bootstrap directory correctly.
        '''
        if name is None:
            return None
        if not hasattr(cls, 'bootstraps'):
            cls.bootstraps = {}
        if name in cls.bootstraps:
            return cls.bootstraps[name]
        mod = importlib.import_module('pythonforandroid.bootstraps.{}'
                                      .format(name))
        if len(logger.handlers) > 1:
            logger.removeHandler(logger.handlers[1])
        bootstrap = mod.bootstrap
        bootstrap.bootstrap_dir = join(ctx.root_dir, 'bootstraps', name)
        bootstrap.ctx = ctx
        return bootstrap

    def distribute_libs(self, arch, src_dirs, wildcard='*', dest_dir="libs"):
        '''Copy existing arch libs from build dirs to current dist dir.'''
        info('Copying libs')
        tgt_dir = join(dest_dir, arch.arch)
        ensure_dir(tgt_dir)
        for src_dir in src_dirs:
            libs = glob.glob(join(src_dir, wildcard))
            if libs:
                shprint(sh.cp, '-a', *libs, tgt_dir)

    def distribute_javaclasses(self, javaclass_dir, dest_dir="src"):
        '''Copy existing javaclasses from build dir to current dist dir.'''
        info('Copying java files')
        ensure_dir(dest_dir)
        filenames = glob.glob(javaclass_dir)
        shprint(sh.cp, '-a', *filenames, dest_dir)

    def distribute_aars(self, arch):
        '''Process existing .aar bundles and copy to current dist dir.'''
        info('Unpacking aars')
        for aar in glob.glob(join(self.ctx.aars_dir, '*.aar')):
            self._unpack_aar(aar, arch)

    def _unpack_aar(self, aar, arch):
        '''Unpack content of .aar bundle and copy to current dist dir.'''
        with temp_directory() as temp_dir:
            name = splitext(basename(aar))[0]
            jar_name = name + '.jar'
            info("unpack {} aar".format(name))
            debug("  from {}".format(aar))
            debug("  to {}".format(temp_dir))
            shprint(sh.unzip, '-o', aar, '-d', temp_dir)

            jar_src = join(temp_dir, 'classes.jar')
            jar_tgt = join('libs', jar_name)
            debug("copy {} jar".format(name))
            debug("  from {}".format(jar_src))
            debug("  to {}".format(jar_tgt))
            ensure_dir('libs')
            shprint(sh.cp, '-a', jar_src, jar_tgt)

            so_src_dir = join(temp_dir, 'jni', arch.arch)
            so_tgt_dir = join('libs', arch.arch)
            debug("copy {} .so".format(name))
            debug("  from {}".format(so_src_dir))
            debug("  to {}".format(so_tgt_dir))
            ensure_dir(so_tgt_dir)
            so_files = glob.glob(join(so_src_dir, '*.so'))
            shprint(sh.cp, '-a', *so_files, so_tgt_dir)

    def strip_libraries(self, arch):
        info('Stripping libraries')
        env = arch.get_env()
        tokens = shlex.split(env['STRIP'])
        strip = sh.Command(tokens[0])
        if len(tokens) > 1:
            strip = strip.bake(tokens[1:])

        libs_dir = join(self.dist_dir, f'_python_bundle__{arch.arch}',
                        '_python_bundle', 'modules')
        filens = shprint(sh.find, libs_dir, join(self.dist_dir, 'libs'),
                         '-iname', '*.so', _env=env).stdout.decode('utf-8')

        logger.info('Stripping libraries in private dir')
        for filen in filens.split('\n'):
            if not filen:
                continue  # skip the last ''
            try:
                strip(filen, _env=env)
            except sh.ErrorReturnCode_1:
                logger.debug('Failed to strip ' + filen)

    def fry_eggs(self, sitepackages):
        info('Frying eggs in {}'.format(sitepackages))
        for d in listdir(sitepackages):
            rd = join(sitepackages, d)
            if isdir(rd) and d.endswith('.egg'):
                info('  ' + d)
                files = [join(rd, f) for f in listdir(rd) if f != 'EGG-INFO']
                if files:
                    shprint(sh.mv, '-t', sitepackages, *files)
                shprint(sh.rm, '-rf', d)


def expand_dependencies(recipes, ctx):
    """ This function expands to lists of all different available
        alternative recipe combinations, with the dependencies added in
        ONLY for all the not-with-alternative recipes.
        (So this is like the deps graph very simplified and incomplete, but
         hopefully good enough for most basic bootstrap compatibility checks)
    """

    # Add in all the deps of recipes where there is no alternative:
    recipes_with_deps = list(recipes)
    for entry in recipes:
        if not isinstance(entry, (tuple, list)) or len(entry) == 1:
            if isinstance(entry, (tuple, list)):
                entry = entry[0]
            try:
                recipe = Recipe.get_recipe(entry, ctx)
                recipes_with_deps += recipe.depends
            except ValueError:
                # it's a pure python package without a recipe, so we
                # don't know the dependencies...skipping for now
                pass

    # Split up lists by available alternatives:
    recipe_lists = [[]]
    for recipe in recipes_with_deps:
        if isinstance(recipe, (tuple, list)):
            new_recipe_lists = []
            for alternative in recipe:
                for old_list in recipe_lists:
                    new_list = [i for i in old_list]
                    new_list.append(alternative)
                    new_recipe_lists.append(new_list)
            recipe_lists = new_recipe_lists
        else:
            for existing_list in recipe_lists:
                existing_list.append(recipe)
    return recipe_lists
