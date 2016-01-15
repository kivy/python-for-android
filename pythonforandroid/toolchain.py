#!/usr/bin/env python
"""
Tool for compiling Android toolchain
====================================

This tool intend to replace all the previous tools/ in shell script.
"""

from __future__ import print_function

import sys
from sys import platform
from os.path import (join, dirname, realpath, exists, expanduser)
import os
import glob
import shutil
import re
import imp
import logging
import shlex
from functools import wraps

import argparse
import sh


from pythonforandroid.recipe import (Recipe, PythonRecipe, CythonRecipe,
                                     CompiledComponentsPythonRecipe,
                                     BootstrapNDKRecipe, NDKRecipe)
from pythonforandroid.archs import (ArchARM, ArchARMv7_a, Archx86)
from pythonforandroid.logger import (logger, info, warning, debug,
                                     Out_Style, Out_Fore, Err_Style, Err_Fore,
                                     info_notify, info_main, shprint,
                                     Null_Fore, Null_Style)
from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.bootstrap import Bootstrap
from pythonforandroid.distribution import Distribution, pretty_log_dists
from pythonforandroid.graph import get_recipe_order_and_bootstrap
from pythonforandroid.build import Context, build_recipes

user_dir = dirname(realpath(os.path.curdir))
toolchain_dir = dirname(__file__)
sys.path.insert(0, join(toolchain_dir, "tools", "external"))


info(''.join(
    [Err_Style.BRIGHT, Err_Fore.RED,
     'This python-for-android revamp is an experimental alpha release!',
     Err_Style.RESET_ALL]))
info(''.join(
    [Err_Fore.RED,
     ('It should work (mostly), but you may experience '
      'missing features or bugs.'),
     Err_Style.RESET_ALL]))


def add_boolean_option(parser, names, no_names=None,
                       default=True, dest=None, description=None):
    group = parser.add_argument_group(description=description)
    if not isinstance(names, (list, tuple)):
        names = [names]
    if dest is None:
        dest = names[0].strip("-").replace("-", "_")

    def add_dashes(x):
        return x if x.startswith("-") else "--"+x

    opts = [add_dashes(x) for x in names]
    group.add_argument(
        *opts, help=("(this is the default)" if default else None),
        dest=dest, action='store_true')
    if no_names is None:
        def add_no(x):
            x = x.lstrip("-")
            return ("no_"+x) if "_" in x else ("no-"+x)
        no_names = [add_no(x) for x in names]
    opts = [add_dashes(x) for x in no_names]
    group.add_argument(
        *opts, help=(None if default else "(this is the default)"),
        dest=dest, action='store_false')
    parser.set_defaults(**{dest: default})


def require_prebuilt_dist(func):
    '''Decorator for ToolchainCL methods. If present, the method will
    automatically make sure a dist has been built before continuing
    or, if no dists are present or can be obtained, will raise an
    error.

    '''

    @wraps(func)
    def wrapper_func(self, args):
        ctx = self.ctx
        ctx.set_archs(self._archs)
        ctx.prepare_build_environment(user_sdk_dir=self.sdk_dir,
                                      user_ndk_dir=self.ndk_dir,
                                      user_android_api=self.android_api,
                                      user_ndk_ver=self.ndk_version)
        dist = self._dist
        dist_args, args = parse_dist_args(args)
        if dist.needs_build:
            info_notify('No dist exists that meets your requirements, '
                        'so one will be built.')
            build_dist_from_args(ctx, dist, dist_args)
        func(self, args)
    return wrapper_func


def dist_from_args(ctx, dist_args):
    '''Parses out any distribution-related arguments, and uses them to
    obtain a Distribution class instance for the build.
    '''
    return Distribution.get_distribution(
        ctx,
        name=dist_args.dist_name,
        recipes=split_argument_list(dist_args.requirements),
        allow_download=dist_args.allow_download,
        allow_build=dist_args.allow_build,
        extra_dist_dirs=split_argument_list(dist_args.extra_dist_dirs),
        require_perfect_match=dist_args.require_perfect_match)


def build_dist_from_args(ctx, dist, args):
    '''Parses out any bootstrap related arguments, and uses them to build
    a dist.'''
    bs = Bootstrap.get_bootstrap(args.bootstrap, ctx)
    build_order, python_modules, bs \
        = get_recipe_order_and_bootstrap(ctx, dist.recipes, bs)
    ctx.recipe_build_order = build_order

    info('The selected bootstrap is {}'.format(bs.name))
    info_main('# Creating dist with {} bootstrap'.format(bs.name))
    bs.distribution = dist
    info_notify('Dist will have name {} and recipes ({})'.format(
        dist.name, ', '.join(dist.recipes)))

    ctx.dist_name = bs.distribution.name
    ctx.prepare_bootstrap(bs)
    ctx.prepare_dist(ctx.dist_name)

    build_recipes(build_order, python_modules, ctx)

    ctx.bootstrap.run_distribute()

    info_main('# Your distribution was created successfully, exiting.')
    info('Dist can be found at (for now) {}'
         .format(join(ctx.dist_dir, ctx.dist_name)))


def parse_dist_args(args_list):
    parser = argparse.ArgumentParser(
            description='Create a newAndroid project')
    parser.add_argument(
            '--bootstrap',
            help=('The name of the bootstrap type, \'pygame\' '
                  'or \'sdl2\', or leave empty to let a '
                  'bootstrap be chosen automatically from your '
                  'requirements.'),
            default=None)
    args, unknown = parser.parse_known_args(args_list)
    return args, unknown


def split_argument_list(l):
    if not len(l):
        return []
    return re.split(r'[ ,]*', l)


class ToolchainCL(object):

    def __init__(self):
        self._ctx = None

        parser = argparse.ArgumentParser(
                description="Tool for managing the Android / Python toolchain",
                usage="""toolchain <command> [<args>]

Available commands:
adb           Runs adb binary from the detected SDK dir
apk           Create an APK using the given distribution
bootstraps    List all the bootstraps available to build with.
build_status  Informations about the current build
create        Build an android project with all recipes
clean_all     Delete all build components
clean_builds  Delete all build caches
clean_dists   Delete all compiled distributions
clean_download_cache Delete any downloaded recipe packages
clean_recipe_build   Delete the build files of a recipe
distributions List all distributions
export_dist   Copies a created dist to an output directory
logcat        Runs logcat from the detected SDK dir
print_context_info   Prints debug informations
recipes       List all the available recipes
sdk_tools     Runs android binary from the detected SDK dir
symlink_dist  Symlinks a created dist to an output directory

Planned commands:
build_dist
""")
        parser.add_argument("command", help="Command to run")

        # General options
        parser.add_argument(
            '--debug', dest='debug', action='store_true',
            help='Display debug output and all build info')
        parser.add_argument(
            '--sdk_dir', dest='sdk_dir', default='',
            help='The filepath where the Android SDK is installed')
        parser.add_argument(
            '--ndk_dir', dest='ndk_dir', default='',
            help='The filepath where the Android NDK is installed')
        parser.add_argument(
            '--android_api', dest='android_api', default=0, type=int,
            help='The Android API level to build against.')
        parser.add_argument(
            '--ndk_version', dest='ndk_version', default='',
            help=('The version of the Android NDK. This is optional, '
                  'we try to work it out automatically from the ndk_dir.'))

        # AND: This option doesn't really fit in the other categories, the
        # arg structure needs a rethink
        parser.add_argument(
            '--arch',
            help='The archs to build for, separated by commas.',
            default='armeabi')

        # Options for specifying the Distribution
        parser.add_argument(
            '--dist_name',
            help='The name of the distribution to use or create',
            default='')
        parser.add_argument(
            '--requirements',
            help=('Dependencies of your app, should be recipe names or '
                  'Python modules'),
            default='')

        add_boolean_option(
            parser, ["allow-download"],
            default=False,
            description='Whether to allow binary dist download:')

        add_boolean_option(
            parser, ["allow-build"],
            default=True,
            description='Whether to allow compilation of a new distribution:')

        add_boolean_option(
            parser, ["force-build"],
            default=False,
            description='Whether to force compilation of a new distribution:')

        parser.add_argument(
            '--extra-dist-dirs', '--extra_dist_dirs',
            dest='extra_dist_dirs', default='',
            help='Directories in which to look for distributions')

        add_boolean_option(
            parser, ["require-perfect-match"],
            default=False,
            description=('Whether the dist recipes must perfectly match '
                         'those requested'))

        parser.add_argument(
            '--local-recipes', '--local_recipes',
            dest='local_recipes', default='./p4a-recipes',
            help='Directory to look for local recipes')

        add_boolean_option(
            parser, ['copy-libs'],
            default=False,
            description='Copy libraries instead of using biglink (Android 4.3+)')

        self._read_configuration()

        args, unknown = parser.parse_known_args(sys.argv[1:])
        self.dist_args = args

        # strip version from requirements, and put them in environ
        requirements = []
        for requirement in split_argument_list(args.requirements):
            if "==" in requirement:
                requirement, version = requirement.split(u"==", 1)
                os.environ["VERSION_{}".format(requirement)] = version
                info('Recipe {}: version "{}" requested'.format(
                    requirement, version))
            requirements.append(requirement)
        args.requirements = u",".join(requirements)

        if args.debug:
            logger.setLevel(logging.DEBUG)
        self.sdk_dir = args.sdk_dir
        self.ndk_dir = args.ndk_dir
        self.android_api = args.android_api
        self.ndk_version = args.ndk_version

        self._archs = split_argument_list(args.arch)

        # AND: Fail nicely if the args aren't handled yet
        if args.extra_dist_dirs:
            warning('Received --extra_dist_dirs but this arg currently is not '
                    'handled, exiting.')
            exit(1)
        if args.allow_download:
            warning('Received --allow_download but this arg currently is not '
                    'handled, exiting.')
            exit(1)
        # if args.allow_build:
        #     warning('Received --allow_build but this arg currently is not '
        #             'handled, exiting.')
        #     exit(1)

        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)

        self.ctx.local_recipes = args.local_recipes
        self.ctx.copy_libs = args.copy_libs

        getattr(self, args.command)(unknown)

    def _read_configuration(self):
        # search for a .p4a configuration file in the current directory
        if not exists(".p4a"):
            return
        info("Reading .p4a configuration")
        with open(".p4a") as fd:
            lines = fd.readlines()
        lines = [shlex.split(line)
                 for line in lines if not line.startswith("#")]
        for line in lines:
            for arg in line:
                sys.argv.append(arg)

    @property
    def ctx(self):
        if self._ctx is None:
            self._ctx = Context()
        return self._ctx

    def recipes(self, args):
        parser = argparse.ArgumentParser(
                description="List all the available recipes")
        parser.add_argument(
                "--compact", action="store_true", default=False,
                help="Produce a compact list suitable for scripting")

        add_boolean_option(
                parser, ["color"],
                default=True,
                description='Whether the output should be colored:')

        args = parser.parse_args(args)

        Fore = Out_Fore
        Style = Out_Style
        if not args.color:
            Fore = Null_Fore
            Style = Null_Style

        ctx = self.ctx
        if args.compact:
            print(" ".join(set(Recipe.list_recipes(ctx))))
        else:
            for name in sorted(Recipe.list_recipes(ctx)):
                recipe = Recipe.get_recipe(name, ctx)
                version = str(recipe.version)
                print('{Fore.BLUE}{Style.BRIGHT}{recipe.name:<12} '
                      '{Style.RESET_ALL}{Fore.LIGHTBLUE_EX}'
                      '{version:<8}{Style.RESET_ALL}'.format(
                        recipe=recipe, Fore=Fore, Style=Style,
                        version=version))
                print('    {Fore.GREEN}depends: {recipe.depends}'
                      '{Fore.RESET}'.format(recipe=recipe, Fore=Fore))
                if recipe.conflicts:
                    print('    {Fore.RED}conflicts: {recipe.conflicts}'
                          '{Fore.RESET}'
                          .format(recipe=recipe, Fore=Fore))
                if recipe.opt_depends:
                    print('    {Fore.YELLOW}optional depends: '
                          '{recipe.opt_depends}{Fore.RESET}'
                          .format(recipe=recipe, Fore=Fore))

    def bootstraps(self, args):
        '''List all the bootstraps available to build with.'''
        for bs in Bootstrap.list_bootstraps():
            bs = Bootstrap.get_bootstrap(bs, self.ctx)
            print('{Fore.BLUE}{Style.BRIGHT}{bs.name}{Style.RESET_ALL}'
                  .format(bs=bs, Fore=Out_Fore, Style=Out_Style))
            print('    {Fore.GREEN}depends: {bs.recipe_depends}{Fore.RESET}'
                  .format(bs=bs, Fore=Out_Fore))

    def clean_all(self, args):
        '''Delete all build components; the package cache, package builds,
        bootstrap builds and distributions.'''
        parser = argparse.ArgumentParser(
                description="Clean the build cache, downloads and dists")
        parsed_args = parser.parse_args(args)
        self.clean_dists(args)
        self.clean_builds(args)
        self.clean_download_cache(args)

    def clean_dists(self, args):
        '''Delete all compiled distributions in the internal distribution
        directory.'''
        parser = argparse.ArgumentParser(
                description="Delete any distributions that have been built.")
        args = parser.parse_args(args)
        ctx = Context()
        if exists(ctx.dist_dir):
            shutil.rmtree(ctx.dist_dir)

    def clean_builds(self, args):
        '''Delete all build caches for each recipe, python-install, java code
        and compiled libs collection.

        This does *not* delete the package download cache or the final
        distributions.  You can also use clean_recipe_build to delete the build
        of a specific recipe.
        '''
        parser = argparse.ArgumentParser(
                description="Delete all build files (but not download caches)")
        args = parser.parse_args(args)
        ctx = Context()
        # if exists(ctx.dist_dir):
        #     shutil.rmtree(ctx.dist_dir)
        if exists(ctx.build_dir):
            shutil.rmtree(ctx.build_dir)
        if exists(ctx.python_installs_dir):
            shutil.rmtree(ctx.python_installs_dir)
        libs_dir = join(self.ctx.build_dir, 'libs_collections')
        if exists(libs_dir):
            shutil.rmtree(libs_dir)

    def clean_recipe_build(self, args):
        '''Deletes the build files of the given recipe.

        This is intended for debug purposes, you may experience
        strange behaviour or problems with some recipes (if their
        build has done unexpected state changes). If this happens, run
        clean_builds, or attempt to clean other recipes until things
        work again.
        '''
        parser = argparse.ArgumentParser(
            description="Delete all build files for the given recipe name.")
        parser.add_argument('recipe', help='The recipe name')
        args = parser.parse_args(args)

        recipe = Recipe.get_recipe(args.recipe, self.ctx)
        info('Cleaning build for {} recipe.'.format(recipe.name))
        recipe.clean_build()

    def clean_download_cache(self, args):
        '''
        Deletes any downloaded recipe packages.

        This does *not* delete the build caches or final distributions.
        '''
        parser = argparse.ArgumentParser(
                description="Delete all download caches")
        args = parser.parse_args(args)
        ctx = Context()
        if exists(ctx.packages_path):
            shutil.rmtree(ctx.packages_path)

    @require_prebuilt_dist
    def export_dist(self, args):
        '''Copies a created dist to an output dir.

        This makes it easy to navigate to the dist to investigate it
        or call build.py, though you do not in general need to do this
        and can use the apk command instead.
        '''
        parser = argparse.ArgumentParser(
            description='Copy a created dist to a given directory')
        parser.add_argument('--output', help=('The output dir to copy to'),
                            required=True)
        args = parser.parse_args(args)

        ctx = self.ctx
        dist = dist_from_args(ctx, self.dist_args)
        if dist.needs_build:
            info('You asked to export a dist, but there is no dist '
                 'with suitable recipes available. For now, you must '
                 ' create one first with the create argument.')
            exit(1)
        shprint(sh.cp, '-r', dist.dist_dir, args.output)

    @require_prebuilt_dist
    def symlink_dist(self, args):
        '''Symlinks a created dist to an output dir.

        This makes it easy to navigate to the dist to investigate it
        or call build.py, though you do not in general need to do this
        and can use the apk command instead.

        '''
        parser = argparse.ArgumentParser(
            description='Symlink a created dist to a given directory')
        parser.add_argument('--output', help=('The output dir to copy to'),
                            required=True)
        args = parser.parse_args(args)

        ctx = self.ctx
        dist = dist_from_args(ctx, self.dist_args)
        if dist.needs_build:
            info('You asked to symlink a dist, but there is no dist '
                 'with suitable recipes available. For now, you must '
                 'create one first with the create argument.')
            exit(1)
        shprint(sh.ln, '-s', dist.dist_dir, args.output)

    # def _get_dist(self):
    #     ctx = self.ctx
    #     dist = dist_from_args(ctx, self.dist_args)

    @property
    def _dist(self):
        ctx = self.ctx
        dist = dist_from_args(ctx, self.dist_args)
        return dist

    @require_prebuilt_dist
    def apk(self, args):
        '''Create an APK using the given distribution.'''

        # AND: Need to add a parser here for any extra options
        # parser = argparse.ArgumentParser(
        #     description='Build an APK')
        # args = parser.parse_args(args)

        ctx = self.ctx
        dist = self._dist

        # Manually fixing these arguments at the string stage is
        # unsatisfactory and should probably be changed somehow, but
        # we can't leave it until later as the build.py scripts assume
        # they are in the current directory.
        for i, arg in enumerate(args[:-1]):
            if arg in ('--dir', '--private'):
                args[i+1] = realpath(expanduser(args[i+1]))

        build = imp.load_source('build', join(dist.dist_dir, 'build.py'))
        with current_directory(dist.dist_dir):
            build.parse_args(args)
            shprint(sh.ant, 'debug', _tail=20, _critical=True)

        # AND: This is very crude, needs improving. Also only works
        # for debug for now.
        info_main('# Copying APK to current directory')
        apks = glob.glob(join(dist.dist_dir, 'bin', '*-*-debug.apk'))
        if len(apks) == 0:
            raise ValueError('Couldn\'t find the built APK')
        if len(apks) > 1:
            info('More than one built APK found...guessing you '
                 'just built {}'.format(apks[-1]))
        shprint(sh.cp, apks[-1], './')

    @require_prebuilt_dist
    def create(self, args):
        '''Create a distribution directory if it doesn't already exist, run
        any recipes if necessary, and build the apk.
        '''
        pass  # The decorator does this for us
        # ctx = self.ctx

        # dist = dist_from_args(ctx, self.dist_args)
        # if not dist.needs_build:
        #     info('You asked to create a distribution, but a dist with '
        #          'this name already exists. If you don\'t want to use '
        #          'it, you must delete it and rebuild, or create your '
        #          'new dist with a different name.')
        #     exit(1)
        # info('Ready to create dist {}, contains recipes {}'.format(
        #     dist.name, ', '.join(dist.recipes)))

        # build_dist_from_args(ctx, dist, args)

    def print_context_info(self, args):
        '''Prints some debug information about which system paths
        python-for-android will internally use for package building, along
        with information about where the Android SDK and NDK will be called
        from.'''
        ctx = Context()
        for attribute in ('root_dir', 'build_dir', 'dist_dir', 'libs_dir',
                          'ccache', 'cython', 'sdk_dir', 'ndk_dir',
                          'ndk_platform', 'ndk_ver', 'android_api'):
            print('{} is {}'.format(attribute, getattr(ctx, attribute)))

    def archs(self, args):
        '''List the target architectures available to be built for.'''
        print('{Style.BRIGHT}Available target architectures are:'
              '{Style.RESET_ALL}'.format(Style=Out_Style))
        for arch in self.ctx.archs:
            print('    {}'.format(arch.arch))

    def dists(self, args):
        '''The same as :meth:`distributions`.'''
        self.distributions(args)

    def distributions(self, args):
        '''Lists all distributions currently available (i.e. that have already
        been built).'''
        ctx = Context()
        dists = Distribution.get_distributions(ctx)

        if dists:
            print('{Style.BRIGHT}Distributions currently installed are:'
                  '{Style.RESET_ALL}'.format(Style=Out_Style, Fore=Out_Fore))
            pretty_log_dists(dists, print)
        else:
            print('{Style.BRIGHT}There are no dists currently built.'
                  '{Style.RESET_ALL}'.format(Style=Out_Style))

    def delete_dist(self, args):
        dist = self._dist
        if dist.needs_build:
            info('No dist exists that matches your specifications, '
                 'exiting without deleting.')
        shutil.rmtree(dist.dist_dir)

    def sdk_tools(self, args):
        '''Runs the android binary from the detected SDK directory, passing
        all arguments straight to it. This binary is used to install
        e.g. platform-tools for different API level targets. This is
        intended as a convenience function if android is not in your
        $PATH.
        '''
        parser = argparse.ArgumentParser(
            description='Run a binary from the /path/to/sdk/tools directory')
        parser.add_argument('tool', help=('The tool binary name to run'))
        args, unknown = parser.parse_known_args(args)

        ctx = self.ctx
        ctx.prepare_build_environment(user_sdk_dir=self.sdk_dir,
                                      user_ndk_dir=self.ndk_dir,
                                      user_android_api=self.android_api,
                                      user_ndk_ver=self.ndk_version)
        android = sh.Command(join(ctx.sdk_dir, 'tools', args.tool))
        output = android(
            *unknown, _iter=True, _out_bufsize=1, _err_to_out=True)
        for line in output:
            sys.stdout.write(line)
            sys.stdout.flush()

    def adb(self, args):
        '''Runs the adb binary from the detected SDK directory, passing all
        arguments straight to it. This is intended as a convenience
        function if adb is not in your $PATH.
        '''
        ctx = self.ctx
        ctx.prepare_build_environment(user_sdk_dir=self.sdk_dir,
                                      user_ndk_dir=self.ndk_dir,
                                      user_android_api=self.android_api,
                                      user_ndk_ver=self.ndk_version)
        if platform in ('win32', 'cygwin'):
            adb = sh.Command(join(ctx.sdk_dir, 'platform-tools', 'adb.exe'))
        else:
            adb = sh.Command(join(ctx.sdk_dir, 'platform-tools', 'adb'))
        info_notify('Starting adb...')
        output = adb(args, _iter=True, _out_bufsize=1, _err_to_out=True)
        for line in output:
            sys.stdout.write(line)
            sys.stdout.flush()

    def logcat(self, args):
        '''Runs ``adb logcat`` using the adb binary from the detected SDK
        directory. All extra args are passed as arguments to logcat.'''
        self.adb(['logcat'] + args)

    def build_status(self, args):

        print('{Style.BRIGHT}Bootstraps whose core components are probably '
              'already built:{Style.RESET_ALL}'.format(Style=Out_Style))
        for filen in os.listdir(join(self.ctx.build_dir, 'bootstrap_builds')):
            print('    {Fore.GREEN}{Style.BRIGHT}{filen}{Style.RESET_ALL}'
                  .format(filen=filen, Fore=Out_Fore, Style=Out_Style))

        print('{Style.BRIGHT}Recipes that are probably already built:'
              '{Style.RESET_ALL}'.format(Style=Out_Style))
        if exists(join(self.ctx.build_dir, 'other_builds')):
            for filen in sorted(
                    os.listdir(join(self.ctx.build_dir, 'other_builds'))):
                name = filen.split('-')[0]
                dependencies = filen.split('-')[1:]
                recipe_str = ('    {Style.BRIGHT}{Fore.GREEN}{name}'
                              '{Style.RESET_ALL}'.format(
                                  Style=Out_Style, name=name, Fore=Out_Fore))
                if dependencies:
                    recipe_str += (
                        ' ({Fore.BLUE}with ' + ', '.join(dependencies) +
                        '{Fore.RESET})').format(Fore=Out_Fore)
                recipe_str += '{Style.RESET_ALL}'.format(Style=Out_Style)
                print(recipe_str)


def main():
    ToolchainCL()

if __name__ == "__main__":
    main()
