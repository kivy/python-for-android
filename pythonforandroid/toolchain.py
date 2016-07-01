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
from appdirs import user_data_dir

from pythonforandroid.recipe import (Recipe, PythonRecipe, CythonRecipe,
                                     CompiledComponentsPythonRecipe,
                                     BootstrapNDKRecipe, NDKRecipe)
from pythonforandroid.archs import (ArchARM, ArchARMv7_a, Archx86)
from pythonforandroid.logger import (logger, info, warning, setup_color,
                                     Out_Style, Out_Fore, Err_Style, Err_Fore,
                                     info_notify, info_main, shprint, error)
from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.bootstrap import Bootstrap
from pythonforandroid.distribution import Distribution, pretty_log_dists
from pythonforandroid.graph import get_recipe_order_and_bootstrap
from pythonforandroid.build import Context, build_recipes

user_dir = dirname(realpath(os.path.curdir))
toolchain_dir = dirname(__file__)
sys.path.insert(0, join(toolchain_dir, "tools", "external"))


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
        if dist.needs_build:
            info_notify('No dist exists that meets your requirements, '
                        'so one will be built.')
            build_dist_from_args(ctx, dist, args)
        func(self, args)
    return wrapper_func


def dist_from_args(ctx, args):
    '''Parses out any distribution-related arguments, and uses them to
    obtain a Distribution class instance for the build.
    '''
    return Distribution.get_distribution(
        ctx,
        name=args.dist_name,
        recipes=split_argument_list(args.requirements),
        extra_dist_dirs=split_argument_list(args.extra_dist_dirs),
        require_perfect_match=args.require_perfect_match)


def build_dist_from_args(ctx, dist, args):
    '''Parses out any bootstrap related arguments, and uses them to build
    a dist.'''
    bs = Bootstrap.get_bootstrap(args.bootstrap, ctx)
    build_order, python_modules, bs \
        = get_recipe_order_and_bootstrap(ctx, dist.recipes, bs)
    ctx.recipe_build_order = build_order
    ctx.python_modules = python_modules

    if python_modules and hasattr(sys, 'real_prefix'):
        error('virtualenv is needed to install pure-Python modules, but')
        error('virtualenv does not support nesting, and you are running')
        error('python-for-android in one. Please run p4a outside of a')
        error('virtualenv instead.')
        exit(1)

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


def split_argument_list(l):
    if not len(l):
        return []
    return re.split(r'[ ,]+', l)


# class NewToolchainCL(object):
#     def __init__(self):
#         parser = argparse.ArgumentParser(
#             description=('A packaging tool for turning Python scripts and apps '
#                          'into Android APKs'))

#         parser.add_argument(
#             '--debug', dest='debug', action='store_true',
#             help='Display debug output and all build info')
#         parser.add_argument(
#             '--color', dest='color', choices=['always', 'never', 'auto'],
#             help='Enable or disable color output (default enabled on tty)')
#         parser.add_argument(
#             '--sdk-dir', '--sdk_dir', dest='sdk_dir', default='',
#             help='The filepath where the Android SDK is installed')
#         parser.add_argument(
#             '--ndk-dir', '--ndk_dir', dest='ndk_dir', default='',
#             help='The filepath where the Android NDK is installed')
#         parser.add_argument(
#             '--android-api', '--android_api', dest='android_api', default=0, type=int,
#             help='The Android API level to build against.')
#         parser.add_argument(
#             '--ndk-version', '--ndk_version', dest='ndk_version', default='',
#             help=('The version of the Android NDK. This is optional, '
#                   'we try to work it out automatically from the ndk_dir.'))

#         default_storage_dir = user_data_dir('python-for-android')
#         if ' ' in default_storage_dir:
#             default_storage_dir = '~/.python-for-android'
#         parser.add_argument(
#             '--storage-dir', dest='storage_dir',
#             default=default_storage_dir,
#             help=('Primary storage directory for downloads and builds '
#                   '(default: {})'.format(default_storage_dir)))

#         # AND: This option doesn't really fit in the other categories, the
#         # arg structure needs a rethink
#         parser.add_argument(
#             '--arch',
#             help='The archs to build for, separated by commas.',
#             default='armeabi')

#         # Options for specifying the Distribution
#         parser.add_argument(
#             '--dist-name', '--dist_name',
#             help='The name of the distribution to use or create',
#             default='')

#         parser.add_argument(
#             '--requirements',
#             help=('Dependencies of your app, should be recipe names or '
#                   'Python modules'),
#             default='')
        
#         parser.add_argument(
#             '--bootstrap',
#             help='The bootstrap to build with. Leave unset to choose automatically.',
#             default=None)

#         add_boolean_option(
#             parser, ["allow-download"],
#             default=False,
#             description='Whether to allow binary dist download:')

#         add_boolean_option(
#             parser, ["allow-build"],
#             default=True,
#             description='Whether to allow compilation of a new distribution:')

#         add_boolean_option(
#             parser, ["force-build"],
#             default=False,
#             description='Whether to force compilation of a new distribution:')

#         parser.add_argument(
#             '--extra-dist-dirs', '--extra_dist_dirs',
#             dest='extra_dist_dirs', default='',
#             help='Directories in which to look for distributions')

#         add_boolean_option(
#             parser, ["require-perfect-match"],
#             default=False,
#             description=('Whether the dist recipes must perfectly match '
#                          'those requested'))

#         parser.add_argument(
#             '--local-recipes', '--local_recipes',
#             dest='local_recipes', default='./p4a-recipes',
#             help='Directory to look for local recipes')

#         add_boolean_option(
#             parser, ['copy-libs'],
#             default=False,
#             description='Copy libraries instead of using biglink (Android 4.3+)')


#         subparsers = parser.add_subparsers(dest='subparser_name',
#                                            help='The command to run')

#         parser_recipes = subparsers.add_parser(
#             'recipes', help='List the available recipes')
#         parser_recipes.add_argument(
#                 "--compact", action="store_true", default=False,
#                 help="Produce a compact list suitable for scripting")

#         parser_bootstraps = subparsers.add_parser(
#             'bootstraps', help='List the available bootstraps')
#         parser_clean_all = subparsers.add_parser(
#             'clean_all', aliases=['clean-all'],
#             help='Delete all builds, dists and caches')
#         parser_clean_dists = subparsers.add_parser(
#             'clean_dists', aliases=['clean-dists'],
#             help='Delete all dists')
#         parser_clean_bootstrap_builds = subparsers.add_parser(
#             'clean_bootstrap_builds', aliases=['clean-bootstrap-builds'],
#             help='Delete all bootstrap builds')
#         parser_clean_builds = subparsers.add_parser(
#             'clean_builds', aliases=['clean-builds'],
#             help='Delete all builds')

#         parser_clean_recipe_build = subparsers.add_parser(
#             'clean_recipe_build', aliases=['clean-recipe-build'],
#             help='Delete the build info for the given recipe')
#         parser_clean_recipe_build.add_argument('recipe', help='The recipe name')

#         parser_clear_download_cache= subparsers.add_parser(
#             'clear_download_cache', aliases=['clear-download-cache'],
#             help='Delete any cached recipe downloads')
#         parser_export_dist = subparsers.add_parser(
#             'export_dist', aliases=['export-dist'],
#             help='Copy the named dist to the given path')
#         parser_symlink_dist = subparsers.add_parser(
#             'symlink_dist', aliases=['symlink-dist'],
#             help='Symlink the named dist at the given path')
#         # todo: make symlink an option of export
#         parser_apk = subparsers.add_parser(
#             'apk', help='Build an APK')
#         parser_create = subparsers.add_parser(
#             'create', help='Compile a set of requirements into a dist')
#         parser_context_info = subparsers.add_parser(
#             'context_info', aliases=['context-info'],
#             help='Print some debug information about the build context')
#         parser_archs = subparsers.add_parser(
#             'archs', help='List the available target architectures')
#         parser_distributions = subparsers.add_parser(
#             'distributions', aliases=['dists'],
#             help='List the currently available (compiled) dists')
#         parser_delete_dist = subparsers.add_parser(
#             'delete_dist', aliases=['delete-dist'], help='Delete a compiled dist')

#         parser_sdk_tools = subparsers.add_parser(
#             'sdk_tools', aliases=['sdk-tools'],
#             help='Run the given binary from the SDK tools dis')
#         parser_sdk_tools.add_argument('tool', help=('The tool binary name to run'))

#         parser_adb = subparsers.add_parser(
#             'adb', help='Run adb from the given SDK')
#         parser_logcat = subparsers.add_parser(
#             'logcat', help='Run logcat from the given SDK')
#         parser_build_status = subparsers.add_parser(
#             'build_status', aliases=['build-status'],
#             help='Print some debug information about current built components')

#         parser_distributions.set_defaults(func=self.distributions)

#         print('ready to parse')
#         args = parser.parse_args(sys.argv[1:])
#         print('parsed')

#         setup_color(args.color)

#         # strip version from requirements, and put them in environ
#         requirements = []
#         for requirement in split_argument_list(args.requirements):
#             if "==" in requirement:
#                 requirement, version = requirement.split(u"==", 1)
#                 os.environ["VERSION_{}".format(requirement)] = version
#                 info('Recipe {}: version "{}" requested'.format(
#                     requirement, version))
#             requirements.append(requirement)
#         args.requirements = u",".join(requirements)

#         self.ctx = Context()
#         self.storage_dir = args.storage_dir
#         self.ctx.setup_dirs(self.storage_dir)
#         self.sdk_dir = args.sdk_dir
#         self.ndk_dir = args.ndk_dir
#         self.android_api = args.android_api
#         self.ndk_version = args.ndk_version

#         self._archs = split_argument_list(args.arch)

#         # AND: Fail nicely if the args aren't handled yet
#         if args.extra_dist_dirs:
#             warning('Received --extra_dist_dirs but this arg currently is not '
#                     'handled, exiting.')
#             exit(1)

#         self.ctx.local_recipes = args.local_recipes
#         self.ctx.copy_libs = args.copy_libs

#         # Each subparser corresponds to a method
#         getattr(self, args.subparser_name.replace('-', '_'))(args)

#     def dists(self, args):
#         print('args', args)
#         self.distributions(args)

#     def distributions(self, args):
#         '''Lists all distributions currently available (i.e. that have already
#         been built).'''
#         ctx = self.ctx
#         dists = Distribution.get_distributions(ctx)

#         if dists:
#             print('{Style.BRIGHT}Distributions currently installed are:'
#                   '{Style.RESET_ALL}'.format(Style=Out_Style, Fore=Out_Fore))
#             pretty_log_dists(dists, print)
#         else:
#             print('{Style.BRIGHT}There are no dists currently built.'
#                   '{Style.RESET_ALL}'.format(Style=Out_Style))

#     def context_info(self, args):
#         '''Prints some debug information about which system paths
#         python-for-android will internally use for package building, along
#         with information about where the Android SDK and NDK will be called
#         from.'''
#         ctx = self.ctx
#         for attribute in ('root_dir', 'build_dir', 'dist_dir', 'libs_dir',
#                           'eccache', 'cython', 'sdk_dir', 'ndk_dir',
#                           'ndk_platform', 'ndk_ver', 'android_api'):
#             print('{} is {}'.format(attribute, getattr(ctx, attribute)))

#     def archs(self, args):
#         '''List the target architectures available to be built for.'''
#         print('{Style.BRIGHT}Available target architectures are:'
#               '{Style.RESET_ALL}'.format(Style=Out_Style))
#         for arch in self.ctx.archs:
#             print('    {}'.format(arch.arch))

#     def delete_dist(self, args):
#         dist = self._dist
#         if dist.needs_build:
#             info('No dist exists that matches your specifications, '
#                  'exiting without deleting.')
#         shutil.rmtree(dist.dist_dir)

#     def sdk_tools(self, args):
#         '''Runs the android binary from the detected SDK directory, passing
#         all arguments straight to it. This binary is used to install
#         e.g. platform-tools for different API level targets. This is
#         intended as a convenience function if android is not in your
#         $PATH.
#         '''
#         ctx = self.ctx
#         ctx.prepare_build_environment(user_sdk_dir=self.sdk_dir,
#                                       user_ndk_dir=self.ndk_dir,
#                                       user_android_api=self.android_api,
#                                       user_ndk_ver=self.ndk_version)
#         android = sh.Command(join(ctx.sdk_dir, 'tools', args.tool))
#         output = android(
#             *unknown, _iter=True, _out_bufsize=1, _err_to_out=True)
#         for line in output:
#             sys.stdout.write(line)
#             sys.stdout.flush()

#     def adb(self, args):
#         '''Runs the adb binary from the detected SDK directory, passing all
#         arguments straight to it. This is intended as a convenience
#         function if adb is not in your $PATH.
#         '''
#         ctx = self.ctx
#         ctx.prepare_build_environment(user_sdk_dir=self.sdk_dir,
#                                       user_ndk_dir=self.ndk_dir,
#                                       user_android_api=self.android_api,
#                                       user_ndk_ver=self.ndk_version)
#         if platform in ('win32', 'cygwin'):
#             adb = sh.Command(join(ctx.sdk_dir, 'platform-tools', 'adb.exe'))
#         else:
#             adb = sh.Command(join(ctx.sdk_dir, 'platform-tools', 'adb'))
#         info_notify('Starting adb...')
#         output = adb(args, _iter=True, _out_bufsize=1, _err_to_out=True)
#         for line in output:
#             sys.stdout.write(line)
#             sys.stdout.flush()

#     def logcat(self, args):
#         '''Runs ``adb logcat`` using the adb binary from the detected SDK
#         directory. All extra args are passed as arguments to logcat.'''
#         self.adb(['logcat'] + args)


#     def build_status(self, args):

#         print('{Style.BRIGHT}Bootstraps whose core components are probably '
#               'already built:{Style.RESET_ALL}'.format(Style=Out_Style))
#         for filen in os.listdir(join(self.ctx.build_dir, 'bootstrap_builds')):
#             print('    {Fore.GREEN}{Style.BRIGHT}{filen}{Style.RESET_ALL}'
#                   .format(filen=filen, Fore=Out_Fore, Style=Out_Style))

#         print('{Style.BRIGHT}Recipes that are probably already built:'
#               '{Style.RESET_ALL}'.format(Style=Out_Style))
#         if exists(join(self.ctx.build_dir, 'other_builds')):
#             for filen in sorted(
#                     os.listdir(join(self.ctx.build_dir, 'other_builds'))):
#                 name = filen.split('-')[0]
#                 dependencies = filen.split('-')[1:]
#                 recipe_str = ('    {Style.BRIGHT}{Fore.GREEN}{name}'
#                               '{Style.RESET_ALL}'.format(
#                                   Style=Out_Style, name=name, Fore=Out_Fore))
#                 if dependencies:
#                     recipe_str += (
#                         ' ({Fore.BLUE}with ' + ', '.join(dependencies) +
#                         '{Fore.RESET})').format(Fore=Out_Fore)
#                 recipe_str += '{Style.RESET_ALL}'.format(Style=Out_Style)
#                 print(recipe_str)


class ToolchainCL(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description=('A packaging tool for turning Python scripts and apps '
                         'into Android APKs'))

        generic_parser = argparse.ArgumentParser(
            add_help=False,
            description=('Generic arguments applied to all commands'))
        dist_parser = argparse.ArgumentParser(
            add_help=False,
            description=('Arguments for dist building'))

        generic_parser.add_argument(
            '--debug', dest='debug', action='store_true',
            default=False,
            help='Display debug output and all build info')
        generic_parser.add_argument(
            '--color', dest='color', choices=['always', 'never', 'auto'],
            help='Enable or disable color output (default enabled on tty)')
        generic_parser.add_argument(
            '--sdk-dir', '--sdk_dir', dest='sdk_dir', default='',
            help='The filepath where the Android SDK is installed')
        generic_parser.add_argument(
            '--ndk-dir', '--ndk_dir', dest='ndk_dir', default='',
            help='The filepath where the Android NDK is installed')
        generic_parser.add_argument(
            '--android-api', '--android_api', dest='android_api', default=0, type=int,
            help='The Android API level to build against.')
        generic_parser.add_argument(
            '--ndk-version', '--ndk_version', dest='ndk_version', default='',
            help=('The version of the Android NDK. This is optional, '
                  'we try to work it out automatically from the ndk_dir.'))

        default_storage_dir = user_data_dir('python-for-android')
        if ' ' in default_storage_dir:
            default_storage_dir = '~/.python-for-android'
        generic_parser.add_argument(
            '--storage-dir', dest='storage_dir',
            default=default_storage_dir,
            help=('Primary storage directory for downloads and builds '
                  '(default: {})'.format(default_storage_dir)))

        # AND: This option doesn't really fit in the other categories, the
        # arg structure needs a rethink
        generic_parser.add_argument(
            '--arch',
            help='The archs to build for, separated by commas.',
            default='armeabi')

        # Options for specifying the Distribution
        generic_parser.add_argument(
            '--dist-name', '--dist_name',
            help='The name of the distribution to use or create',
            default='')

        generic_parser.add_argument(
            '--requirements',
            help=('Dependencies of your app, should be recipe names or '
                  'Python modules'),
            default='')
        
        generic_parser.add_argument(
            '--bootstrap',
            help='The bootstrap to build with. Leave unset to choose automatically.',
            default=None)

        add_boolean_option(
            generic_parser, ["force-build"],
            default=False,
            description='Whether to force compilation of a new distribution:')

        generic_parser.add_argument(
            '--extra-dist-dirs', '--extra_dist_dirs',
            dest='extra_dist_dirs', default='',
            help='Directories in which to look for distributions')

        add_boolean_option(
            generic_parser, ["require-perfect-match"],
            default=False,
            description=('Whether the dist recipes must perfectly match '
                         'those requested'))

        generic_parser.add_argument(
            '--local-recipes', '--local_recipes',
            dest='local_recipes', default='./p4a-recipes',
            help='Directory to look for local recipes')

        add_boolean_option(
            generic_parser, ['copy-libs'],
            default=False,
            description='Copy libraries instead of using biglink (Android 4.3+)')

        subparsers = parser.add_subparsers(dest='subparser_name',
                                           help='The command to run')

        parser_recipes = subparsers.add_parser(
            'recipes',
            parents=[generic_parser],
            help='List the available recipes')
        parser_recipes.add_argument(
                "--compact", action="store_true", default=False,
                help="Produce a compact list suitable for scripting")

        parser_bootstraps = subparsers.add_parser(
            'bootstraps', help='List the available bootstraps',
            parents=[generic_parser])
        parser_clean_all = subparsers.add_parser(
            'clean_all', aliases=['clean-all'],
            help='Delete all builds, dists and caches',
            parents=[generic_parser])
        parser_clean_dists = subparsers.add_parser(
            'clean_dists', aliases=['clean-dists'],
            help='Delete all dists',
            parents=[generic_parser])
        parser_clean_bootstrap_builds = subparsers.add_parser(
            'clean_bootstrap_builds', aliases=['clean-bootstrap-builds'],
            help='Delete all bootstrap builds',
            parents=[generic_parser])
        parser_clean_builds = subparsers.add_parser(
            'clean_builds', aliases=['clean-builds'],
            help='Delete all builds',
            parents=[generic_parser])

        parser_clean_recipe_build = subparsers.add_parser(
            'clean_recipe_build', aliases=['clean-recipe-build'],
            help='Delete the build info for the given recipe',
            parents=[generic_parser])
        parser_clean_recipe_build.add_argument('recipe', help='The recipe name')

        parser_clear_download_cache= subparsers.add_parser(
            'clear_download_cache', aliases=['clear-download-cache'],
            help='Delete any cached recipe downloads',
            parents=[generic_parser])

        parser_export_dist = subparsers.add_parser(
            'export_dist', aliases=['export-dist'],
            help='Copy the named dist to the given path',
            parents=[generic_parser])
        parser_export_dist.add_argument('--output', help=('The output dir to copy to'),
                                        required=True)

        parser_symlink_dist = subparsers.add_parser(
            'symlink_dist', aliases=['symlink-dist'],
            help='Symlink the named dist at the given path',
            parents=[generic_parser])
        parser_symlink_dist.add_argument('--output', help=('The output dir to copy to'),
                                         required=True)
        # todo: make symlink an option of export

        parser_apk = subparsers.add_parser(
            'apk', help='Build an APK',
            parents=[generic_parser])
        parser_apk.add_argument('--release', dest='build_mode', action='store_const',
                        const='release', default='debug',
                        help='Build the PARSER_APK. in Release mode')
        parser_apk.add_argument('--keystore', dest='keystore', action='store', default=None,
                        help=('Keystore for JAR signing key, will use jarsigner '
                              'default if not specified (release build only)'))
        parser_apk.add_argument('--signkey', dest='signkey', action='store', default=None,
                        help='Key alias to sign PARSER_APK. with (release build only)')
        parser_apk.add_argument('--keystorepw', dest='keystorepw', action='store', default=None,
                        help='Password for keystore')
        parser_apk.add_argument('--signkeypw', dest='signkeypw', action='store', default=None,
                        help='Password for key alias')

        parser_create = subparsers.add_parser(
            'create', help='Compile a set of requirements into a dist',
            parents=[generic_parser])
        parser_context_info = subparsers.add_parser(
            'context_info', aliases=['context-info'],
            help='Print some debug information about the build context',
            parents=[generic_parser])
        parser_archs = subparsers.add_parser(
            'archs', help='List the available target architectures',
            parents=[generic_parser])
        parser_distributions = subparsers.add_parser(
            'distributions', aliases=['dists'],
            help='List the currently available (compiled) dists',
            parents=[generic_parser])
        parser_delete_dist = subparsers.add_parser(
            'delete_dist', aliases=['delete-dist'], help='Delete a compiled dist',
            parents=[generic_parser])

        parser_sdk_tools = subparsers.add_parser(
            'sdk_tools', aliases=['sdk-tools'],
            help='Run the given binary from the SDK tools dis',
            parents=[generic_parser])
        parser_sdk_tools.add_argument(
            'tool', help=('The tool binary name to run'))

        parser_adb = subparsers.add_parser(
            'adb', help='Run adb from the given SDK',
            parents=[generic_parser])
        parser_logcat = subparsers.add_parser(
            'logcat', help='Run logcat from the given SDK',
            parents=[generic_parser])
        parser_build_status = subparsers.add_parser(
            'build_status', aliases=['build-status'],
            help='Print some debug information about current built components',
            parents=[generic_parser])

        args, unknown = parser.parse_known_args(sys.argv[1:])
        args.unknown_args = unknown

        self.args = args

        setup_color(args.color)

        # strip version from requirements, and put them in environ
        if hasattr(args, 'requirements'):
            requirements = []
            for requirement in split_argument_list(args.requirements):
                if "==" in requirement:
                    requirement, version = requirement.split(u"==", 1)
                    os.environ["VERSION_{}".format(requirement)] = version
                    info('Recipe {}: version "{}" requested'.format(
                        requirement, version))
                requirements.append(requirement)
            args.requirements = u",".join(requirements)

        self.ctx = Context()
        self.storage_dir = args.storage_dir
        self.ctx.setup_dirs(self.storage_dir)
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

        self.ctx.local_recipes = args.local_recipes
        self.ctx.copy_libs = args.copy_libs

        # Each subparser corresponds to a method
        getattr(self, args.subparser_name.replace('-', '_'))(args)

    @property
    def default_storage_dir(self):
        udd = user_data_dir('python-for-android')
        if ' ' in udd:
            udd = '~/.python-for-android'
        return udd

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

    def recipes(self, args):
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
                        recipe=recipe, Fore=Out_Fore, Style=Out_Style,
                        version=version))
                print('    {Fore.GREEN}depends: {recipe.depends}'
                      '{Fore.RESET}'.format(recipe=recipe, Fore=Out_Fore))
                if recipe.conflicts:
                    print('    {Fore.RED}conflicts: {recipe.conflicts}'
                          '{Fore.RESET}'
                          .format(recipe=recipe, Fore=Out_Fore))
                if recipe.opt_depends:
                    print('    {Fore.YELLOW}optional depends: '
                          '{recipe.opt_depends}{Fore.RESET}'
                          .format(recipe=recipe, Fore=Out_Fore))

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
        self.clean_dists(args)
        self.clean_builds(args)
        self.clean_download_cache(args)

    def clean_dists(self, args):
        '''Delete all compiled distributions in the internal distribution
        directory.'''
        ctx = self.ctx
        if exists(ctx.dist_dir):
            shutil.rmtree(ctx.dist_dir)

    def clean_bootstrap_builds(self, args):
        '''Delete all the bootstrap builds.'''
        for bs in Bootstrap.list_bootstraps():
            bs = Bootstrap.get_bootstrap(bs, self.ctx)
            if bs.build_dir and exists(bs.build_dir):
                info('Cleaning build for {} bootstrap.'.format(bs.name))
                shutil.rmtree(bs.build_dir)

    def clean_builds(self, args):
        '''Delete all build caches for each recipe, python-install, java code
        and compiled libs collection.

        This does *not* delete the package download cache or the final
        distributions.  You can also use clean_recipe_build to delete the build
        of a specific recipe.
        '''
        ctx = self.ctx
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
        recipe = Recipe.get_recipe(args.recipe, self.ctx)
        info('Cleaning build for {} recipe.'.format(recipe.name))
        recipe.clean_build()

    def clean_download_cache(self, args):
        '''
        Deletes any downloaded recipe packages.

        This does *not* delete the build caches or final distributions.
        '''
        ctx = self.ctx
        if exists(ctx.packages_path):
            shutil.rmtree(ctx.packages_path)

    @require_prebuilt_dist
    def export_dist(self, args):
        '''Copies a created dist to an output dir.

        This makes it easy to navigate to the dist to investigate it
        or call build.py, though you do not in general need to do this
        and can use the apk command instead.
        '''
        ctx = self.ctx
        dist = dist_from_args(ctx, args)
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
        ctx = self.ctx
        dist = dist_from_args(ctx, args)
        if dist.needs_build:
            info('You asked to symlink a dist, but there is no dist '
                 'with suitable recipes available. For now, you must '
                 'create one first with the create argument.')
            exit(1)
        shprint(sh.ln, '-s', dist.dist_dir, args.output)

    # def _get_dist(self):
    #     ctx = self.ctx
    #     dist = dist_from_args(ctx, self.args)

    @property
    def _dist(self):
        ctx = self.ctx
        dist = dist_from_args(ctx, self.args)
        return dist

    @require_prebuilt_dist
    def apk(self, args):
        '''Create an APK using the given distribution.'''

        ctx = self.ctx
        dist = self._dist

        # Manually fixing these arguments at the string stage is
        # unsatisfactory and should probably be changed somehow, but
        # we can't leave it until later as the build.py scripts assume
        # they are in the current directory.
        fix_args = ('--dir', '--private', '--add-jar', '--add-source',
                    '--whitelist', '--blacklist', '--presplash', '--icon')
        for i, arg in enumerate(args[:-1]):
            argx = arg.split('=')
            if argx[0] in fix_args:
                if len(argx) > 1:
                    args[i] = '='.join((argx[0],
                                        realpath(expanduser(argx[1]))))
                else:
                    args[i+1] = realpath(expanduser(args[i+1]))

        env = os.environ.copy()
        if apk_args.build_mode == 'release':
            if apk_args.keystore:
                env['P4A_RELEASE_KEYSTORE'] = realpath(expanduser(apk_args.keystore))
            if apk_args.signkey:
                env['P4A_RELEASE_KEYALIAS'] = apk_args.signkey
            if apk_args.keystorepw:
                env['P4A_RELEASE_KEYSTORE_PASSWD'] = apk_args.keystorepw
            if apk_args.signkeypw:
                env['P4A_RELEASE_KEYALIAS_PASSWD'] = apk_args.signkeypw
            elif apk_args.keystorepw and 'P4A_RELEASE_KEYALIAS_PASSWD' not in env:
                env['P4A_RELEASE_KEYALIAS_PASSWD'] = apk_args.keystorepw

        build = imp.load_source('build', join(dist.dist_dir, 'build.py'))
        with current_directory(dist.dist_dir):
            build_args = build.parse_args(args.unknown_args)
            output = shprint(sh.ant, apk_args.build_mode, _tail=20, _critical=True, _env=env)

        info_main('# Copying APK to current directory')

        apk_re = re.compile(r'.*Package: (.*\.apk)$')
        apk_file = None
        for line in reversed(output.splitlines()):
            m = apk_re.match(line)
            if m:
                apk_file = m.groups()[0]
                break

        if not apk_file:
            info_main('# APK filename not found in build output, trying to guess')
            apks = glob.glob(join(dist.dist_dir, 'bin', '*-*-{}.apk'.format(apk_args.build_mode)))
            if len(apks) == 0:
                raise ValueError('Couldn\'t find the built APK')
            if len(apks) > 1:
                info('More than one built APK found...guessing you '
                     'just built {}'.format(apks[-1]))
            apk_file = apks[-1]

        info_main('# Found APK file: {}'.format(apk_file))
        shprint(sh.cp, apk_file, './')

    @require_prebuilt_dist
    def create(self, args):
        '''Create a distribution directory if it doesn't already exist, run
        any recipes if necessary, and build the apk.
        '''
        pass  # The decorator does this for us
        # ctx = self.ctx

        # dist = dist_from_args(ctx, self.args)
        # if not dist.needs_build:
        #     info('You asked to create a distribution, but a dist with '
        #          'this name already exists. If you don\'t want to use '
        #          'it, you must delete it and rebuild, or create your '
        #          'new dist with a different name.')
        #     exit(1)
        # info('Ready to create dist {}, contains recipes {}'.format(
        #     dist.name, ', '.join(dist.recipes)))

        # build_dist_from_args(ctx, dist, args)

    def context_info(self, args):
        '''Prints some debug information about which system paths
        python-for-android will internally use for package building, along
        with information about where the Android SDK and NDK will be called
        from.'''
        ctx = self.ctx
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
        ctx = self.ctx
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
        self.adb(['logcat'] + args.unknown_args)

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
    # NewToolchainCL()

if __name__ == "__main__":
    new_main()
