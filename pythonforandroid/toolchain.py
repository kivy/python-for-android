#!/usr/bin/env python
"""
Tool for packaging Python apps for Android
==========================================

This module defines the entry point for command line and programmatic use.
"""

from os import environ
from pythonforandroid import __version__
from pythonforandroid.pythonpackage import get_dep_names_of_package
from pythonforandroid.recommendations import (
    RECOMMENDED_NDK_API, RECOMMENDED_TARGET_API, print_recommendations)
from pythonforandroid.util import BuildInterruptingException, load_source
from pythonforandroid.entrypoints import main
from pythonforandroid.prerequisites import check_and_install_default_prerequisites


def check_python_dependencies():
    # Check if the Python requirements are installed. This appears
    # before the imports because otherwise they're imported elsewhere.

    # Using the ok check instead of failing immediately so that all
    # errors are printed at once

    from distutils.version import LooseVersion
    from importlib import import_module
    import sys

    ok = True

    modules = [('colorama', '0.3.3'), 'appdirs', ('sh', '1.10'), 'jinja2',
               'six']

    for module in modules:
        if isinstance(module, tuple):
            module, version = module
        else:
            version = None

        try:
            import_module(module)
        except ImportError:
            if version is None:
                print('ERROR: The {} Python module could not be found, please '
                      'install it.'.format(module))
                ok = False
            else:
                print('ERROR: The {} Python module could not be found, '
                      'please install version {} or higher'.format(
                          module, version))
                ok = False
        else:
            if version is None:
                continue
            try:
                cur_ver = sys.modules[module].__version__
            except AttributeError:  # this is sometimes not available
                continue
            if LooseVersion(cur_ver) < LooseVersion(version):
                print('ERROR: {} version is {}, but python-for-android needs '
                      'at least {}.'.format(module, cur_ver, version))
                ok = False

    if not ok:
        print('python-for-android is exiting due to the errors logged above')
        exit(1)


if not environ.get('SKIP_PREREQUISITES_CHECK', '0') == '1':
    check_and_install_default_prerequisites()
check_python_dependencies()


import sys
from sys import platform
from os.path import (join, dirname, realpath, exists, expanduser, basename)
import os
import glob
import shutil
import re
import shlex
from functools import wraps

import argparse
import sh
from appdirs import user_data_dir
import logging
from distutils.version import LooseVersion

from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import (logger, info, warning, setup_color,
                                     Out_Style, Out_Fore,
                                     info_notify, info_main, shprint)
from pythonforandroid.util import current_directory
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
    """Decorator for ToolchainCL methods. If present, the method will
    automatically make sure a dist has been built before continuing
    or, if no dists are present or can be obtained, will raise an
    error.
    """

    @wraps(func)
    def wrapper_func(self, args, **kw):
        ctx = self.ctx
        ctx.set_archs(self._archs)
        ctx.prepare_build_environment(user_sdk_dir=self.sdk_dir,
                                      user_ndk_dir=self.ndk_dir,
                                      user_android_api=self.android_api,
                                      user_ndk_api=self.ndk_api)
        dist = self._dist
        if dist.needs_build:
            if dist.folder_exists():  # possible if the dist is being replaced
                dist.delete()
            info_notify('No dist exists that meets your requirements, '
                        'so one will be built.')
            build_dist_from_args(ctx, dist, args)
        func(self, args, **kw)
    return wrapper_func


def dist_from_args(ctx, args):
    """Parses out any distribution-related arguments, and uses them to
    obtain a Distribution class instance for the build.
    """
    return Distribution.get_distribution(
        ctx,
        name=args.dist_name,
        recipes=split_argument_list(args.requirements),
        archs=args.arch,
        ndk_api=args.ndk_api,
        force_build=args.force_build,
        require_perfect_match=args.require_perfect_match,
        allow_replace_dist=args.allow_replace_dist)


def build_dist_from_args(ctx, dist, args):
    """Parses out any bootstrap related arguments, and uses them to build
    a dist."""
    bs = Bootstrap.get_bootstrap(args.bootstrap, ctx)
    blacklist = getattr(args, "blacklist_requirements", "").split(",")
    if len(blacklist) == 1 and blacklist[0] == "":
        blacklist = []
    build_order, python_modules, bs = (
        get_recipe_order_and_bootstrap(
            ctx, dist.recipes, bs,
            blacklist=blacklist
        ))
    assert set(build_order).intersection(set(python_modules)) == set()
    ctx.recipe_build_order = build_order
    ctx.python_modules = python_modules

    info('The selected bootstrap is {}'.format(bs.name))
    info_main('# Creating dist with {} bootstrap'.format(bs.name))
    bs.distribution = dist
    info_notify('Dist will have name {} and requirements ({})'.format(
        dist.name, ', '.join(dist.recipes)))
    info('Dist contains the following requirements as recipes: {}'.format(
        ctx.recipe_build_order))
    info('Dist will also contain modules ({}) installed from pip'.format(
        ', '.join(ctx.python_modules)))
    info(
        'Dist will be build in mode {build_mode}{with_debug_symbols}'.format(
            build_mode='debug' if ctx.build_as_debuggable else 'release',
            with_debug_symbols=' (with debug symbols)'
            if ctx.with_debug_symbols
            else '',
        )
    )

    ctx.distribution = dist
    ctx.prepare_bootstrap(bs)
    if dist.needs_build:
        ctx.prepare_dist()

    build_recipes(build_order, python_modules, ctx,
                  getattr(args, "private", None),
                  ignore_project_setup_py=getattr(
                      args, "ignore_setup_py", False
                  ),
                 )

    ctx.bootstrap.assemble_distribution()

    info_main('# Your distribution was created successfully, exiting.')
    info('Dist can be found at (for now) {}'
         .format(join(ctx.dist_dir, ctx.distribution.dist_dir)))


def split_argument_list(arg_list):
    if not len(arg_list):
        return []
    return re.split(r'[ ,]+', arg_list)


class NoAbbrevParser(argparse.ArgumentParser):
    """We want to disable argument abbreviation so as not to interfere
    with passing through arguments to build.py, but in python2 argparse
    doesn't have this option.

    This subclass alternative is follows the suggestion at
    https://bugs.python.org/issue14910.
    """
    def _get_option_tuples(self, option_string):
        return []


class ToolchainCL:

    def __init__(self):

        argv = sys.argv
        self.warn_on_carriage_return_args(argv)
        # Buildozer used to pass these arguments in a now-invalid order
        # If that happens, apply this fix
        # This fix will be removed once a fixed buildozer is released
        if (len(argv) > 2
                and argv[1].startswith('--color')
                and argv[2].startswith('--storage-dir')):
            argv.append(argv.pop(1))  # the --color arg
            argv.append(argv.pop(1))  # the --storage-dir arg

        parser = NoAbbrevParser(
            description='A packaging tool for turning Python scripts and apps '
                        'into Android APKs')

        generic_parser = argparse.ArgumentParser(
            add_help=False,
            description='Generic arguments applied to all commands')
        argparse.ArgumentParser(
            add_help=False, description='Arguments for dist building')

        generic_parser.add_argument(
            '--debug', dest='debug', action='store_true', default=False,
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
            '--android-api',
            '--android_api',
            dest='android_api',
            default=0,
            type=int,
            help=('The Android API level to build against defaults to {} if '
                  'not specified.').format(RECOMMENDED_TARGET_API))
        generic_parser.add_argument(
            '--ndk-version', '--ndk_version', dest='ndk_version', default=None,
            help=('DEPRECATED: the NDK version is now found automatically or '
                  'not at all.'))
        generic_parser.add_argument(
            '--ndk-api', type=int, default=None,
            help=('The Android API level to compile against. This should be your '
                  '*minimal supported* API, not normally the same as your --android-api. '
                  'Defaults to min(ANDROID_API, {}) if not specified.').format(RECOMMENDED_NDK_API))
        generic_parser.add_argument(
            '--symlink-bootstrap-files', '--ssymlink_bootstrap_files',
            action='store_true',
            dest='symlink_bootstrap_files',
            default=False,
            help=('If True, symlinks the bootstrap files '
                  'creation. This is useful for development only, it could also'
                  ' cause weird problems.'))

        default_storage_dir = user_data_dir('python-for-android')
        if ' ' in default_storage_dir:
            default_storage_dir = '~/.python-for-android'
        generic_parser.add_argument(
            '--storage-dir', dest='storage_dir', default=default_storage_dir,
            help=('Primary storage directory for downloads and builds '
                  '(default: {})'.format(default_storage_dir)))

        generic_parser.add_argument(
            '--arch', help='The archs to build for.',
            action='append', default=[])

        # Options for specifying the Distribution
        generic_parser.add_argument(
            '--dist-name', '--dist_name',
            help='The name of the distribution to use or create', default='')

        generic_parser.add_argument(
            '--requirements',
            help=('Dependencies of your app, should be recipe names or '
                  'Python modules. NOT NECESSARY if you are using '
                  'Python 3 with --use-setup-py'),
            default='')

        generic_parser.add_argument(
            '--recipe-blacklist',
            help=('Blacklist an internal recipe from use. Allows '
                  'disabling Python 3 core modules to save size'),
            dest="recipe_blacklist",
            default='')

        generic_parser.add_argument(
            '--blacklist-requirements',
            help=('Blacklist an internal recipe from use. Allows '
                  'disabling Python 3 core modules to save size'),
            dest="blacklist_requirements",
            default='')

        generic_parser.add_argument(
            '--bootstrap',
            help='The bootstrap to build with. Leave unset to choose '
                 'automatically.',
            default=None)

        generic_parser.add_argument(
            '--hook',
            help='Filename to a module that contains python-for-android hooks',
            default=None)

        add_boolean_option(
            generic_parser, ["force-build"],
            default=False,
            description='Whether to force compilation of a new distribution')

        add_boolean_option(
            generic_parser, ["require-perfect-match"],
            default=False,
            description=('Whether the dist recipes must perfectly match '
                         'those requested'))

        add_boolean_option(
            generic_parser, ["allow-replace-dist"],
            default=True,
            description='Whether existing dist names can be automatically replaced'
            )

        generic_parser.add_argument(
            '--local-recipes', '--local_recipes',
            dest='local_recipes', default='./p4a-recipes',
            help='Directory to look for local recipes')

        generic_parser.add_argument(
            '--activity-class-name',
            dest='activity_class_name', default='org.kivy.android.PythonActivity',
            help='The full java class name of the main activity')

        generic_parser.add_argument(
            '--service-class-name',
            dest='service_class_name', default='org.kivy.android.PythonService',
            help='Full java package name of the PythonService class')

        generic_parser.add_argument(
            '--java-build-tool',
            dest='java_build_tool', default='auto',
            choices=['auto', 'ant', 'gradle'],
            help=('The java build tool to use when packaging the APK, defaults '
                  'to automatically selecting an appropriate tool.'))

        add_boolean_option(
            generic_parser, ['copy-libs'],
            default=False,
            description='Copy libraries instead of using biglink (Android 4.3+)'
        )

        self._read_configuration()

        subparsers = parser.add_subparsers(dest='subparser_name',
                                           help='The command to run')

        def add_parser(subparsers, *args, **kwargs):
            """
            argparse in python2 doesn't support the aliases option,
            so we just don't provide the aliases there.
            """
            if 'aliases' in kwargs and sys.version_info.major < 3:
                kwargs.pop('aliases')
            return subparsers.add_parser(*args, **kwargs)

        add_parser(
            subparsers,
            'recommendations',
            parents=[generic_parser],
            help='List recommended p4a dependencies')
        parser_recipes = add_parser(
            subparsers,
            'recipes',
            parents=[generic_parser],
            help='List the available recipes')
        parser_recipes.add_argument(
            "--compact",
            action="store_true", default=False,
            help="Produce a compact list suitable for scripting")
        add_parser(
            subparsers, 'bootstraps',
            help='List the available bootstraps',
            parents=[generic_parser])
        add_parser(
            subparsers, 'clean_all',
            aliases=['clean-all'],
            help='Delete all builds, dists and caches',
            parents=[generic_parser])
        add_parser(
            subparsers, 'clean_dists',
            aliases=['clean-dists'],
            help='Delete all dists',
            parents=[generic_parser])
        add_parser(
            subparsers, 'clean_bootstrap_builds',
            aliases=['clean-bootstrap-builds'],
            help='Delete all bootstrap builds',
            parents=[generic_parser])
        add_parser(
            subparsers, 'clean_builds',
            aliases=['clean-builds'],
            help='Delete all builds',
            parents=[generic_parser])

        parser_clean = add_parser(
            subparsers, 'clean',
            help='Delete build components.',
            parents=[generic_parser])
        parser_clean.add_argument(
            'component', nargs='+',
            help=('The build component(s) to delete. You can pass any '
                  'number of arguments from "all", "builds", "dists", '
                  '"distributions", "bootstrap_builds", "downloads".'))

        parser_clean_recipe_build = add_parser(
            subparsers,
            'clean_recipe_build', aliases=['clean-recipe-build'],
            help=('Delete the build components of the given recipe. '
                  'By default this will also delete built dists'),
            parents=[generic_parser])
        parser_clean_recipe_build.add_argument(
            'recipe', help='The recipe name')
        parser_clean_recipe_build.add_argument(
            '--no-clean-dists', default=False,
            dest='no_clean_dists',
            action='store_true',
            help='If passed, do not delete existing dists')

        parser_clean_download_cache = add_parser(
            subparsers,
            'clean_download_cache', aliases=['clean-download-cache'],
            help='Delete cached downloads for requirement builds',
            parents=[generic_parser])
        parser_clean_download_cache.add_argument(
            'recipes',
            nargs='*',
            help='The recipes to clean (space-separated). If no recipe name is'
                  ' provided, the entire cache is cleared.')

        parser_export_dist = add_parser(
            subparsers,
            'export_dist', aliases=['export-dist'],
            help='Copy the named dist to the given path',
            parents=[generic_parser])
        parser_export_dist.add_argument('output_dir',
                                        help='The output dir to copy to')
        parser_export_dist.add_argument(
            '--symlink',
            action='store_true',
            help='Symlink the dist instead of copying')

        parser_packaging = argparse.ArgumentParser(
            parents=[generic_parser],
            add_help=False,
            description='common options for packaging (apk, aar)')

        # This is actually an internal argument of the build.py
        # (see pythonforandroid/bootstraps/common/build/build.py).
        # However, it is also needed before the distribution is finally
        # assembled for locating the setup.py / other build systems, which
        # is why we also add it here:
        parser_packaging.add_argument(
            '--add-asset', dest='assets',
            action="append", default=[],
            help='Put this in the assets folder in the apk.')
        parser_packaging.add_argument(
            '--private', dest='private',
            help='the directory with the app source code files' +
                 ' (containing your main.py entrypoint)',
            required=False, default=None)
        parser_packaging.add_argument(
            '--use-setup-py', dest="use_setup_py",
            action='store_true', default=False,
            help="Process the setup.py of a project if present. " +
                 "(Experimental!")
        parser_packaging.add_argument(
            '--ignore-setup-py', dest="ignore_setup_py",
            action='store_true', default=False,
            help="Don't run the setup.py of a project if present. " +
                 "This may be required if the setup.py is not " +
                 "designed to work inside p4a (e.g. by installing " +
                 "dependencies that won't work or aren't desired " +
                 "on Android")
        parser_packaging.add_argument(
            '--release', dest='build_mode', action='store_const',
            const='release', default='debug',
            help='Build your app as a non-debug release build. '
                 '(Disables gdb debugging among other things)')
        parser_packaging.add_argument(
            '--with-debug-symbols', dest='with_debug_symbols',
            action='store_const', const=True, default=False,
            help='Will keep debug symbols from `.so` files.')
        parser_packaging.add_argument(
            '--keystore', dest='keystore', action='store', default=None,
            help=('Keystore for JAR signing key, will use jarsigner '
                  'default if not specified (release build only)'))
        parser_packaging.add_argument(
            '--signkey', dest='signkey', action='store', default=None,
            help='Key alias to sign PARSER_APK. with (release build only)')
        parser_packaging.add_argument(
            '--keystorepw', dest='keystorepw', action='store', default=None,
            help='Password for keystore')
        parser_packaging.add_argument(
            '--signkeypw', dest='signkeypw', action='store', default=None,
            help='Password for key alias')

        add_parser(
            subparsers,
            'aar', help='Build an AAR',
            parents=[parser_packaging])

        add_parser(
            subparsers,
            'apk', help='Build an APK',
            parents=[parser_packaging])

        add_parser(
            subparsers,
            'aab', help='Build an AAB',
            parents=[parser_packaging])

        add_parser(
            subparsers,
            'create', help='Compile a set of requirements into a dist',
            parents=[generic_parser])
        add_parser(
            subparsers,
            'archs', help='List the available target architectures',
            parents=[generic_parser])
        add_parser(
            subparsers,
            'distributions', aliases=['dists'],
            help='List the currently available (compiled) dists',
            parents=[generic_parser])
        add_parser(
            subparsers,
            'delete_dist', aliases=['delete-dist'], help='Delete a compiled dist',
            parents=[generic_parser])

        parser_sdk_tools = add_parser(
            subparsers,
            'sdk_tools', aliases=['sdk-tools'],
            help='Run the given binary from the SDK tools dis',
            parents=[generic_parser])
        parser_sdk_tools.add_argument(
            'tool', help='The binary tool name to run')

        add_parser(
            subparsers,
            'adb', help='Run adb from the given SDK',
            parents=[generic_parser])
        add_parser(
            subparsers,
            'logcat', help='Run logcat from the given SDK',
            parents=[generic_parser])
        add_parser(
            subparsers,
            'build_status', aliases=['build-status'],
            help='Print some debug information about current built components',
            parents=[generic_parser])

        parser.add_argument('-v', '--version', action='version',
                            version=__version__)

        args, unknown = parser.parse_known_args(sys.argv[1:])
        args.unknown_args = unknown

        if hasattr(args, "private") and args.private is not None:
            # Pass this value on to the internal bootstrap build.py:
            args.unknown_args += ["--private", args.private]
        if hasattr(args, "build_mode") and args.build_mode == "release":
            args.unknown_args += ["--release"]
        if hasattr(args, "with_debug_symbols") and args.with_debug_symbols:
            args.unknown_args += ["--with-debug-symbols"]
        if hasattr(args, "ignore_setup_py") and args.ignore_setup_py:
            args.use_setup_py = False
        if hasattr(args, "activity_class_name") and args.activity_class_name != 'org.kivy.android.PythonActivity':
            args.unknown_args += ["--activity-class-name", args.activity_class_name]
        if hasattr(args, "service_class_name") and args.service_class_name != 'org.kivy.android.PythonService':
            args.unknown_args += ["--service-class-name", args.service_class_name]

        self.args = args

        if args.subparser_name is None:
            parser.print_help()
            exit(1)

        setup_color(args.color)

        if args.debug:
            logger.setLevel(logging.DEBUG)

        self.ctx = Context()
        self.ctx.use_setup_py = getattr(args, "use_setup_py", True)
        self.ctx.build_as_debuggable = getattr(
            args, "build_mode", "debug"
        ) == "debug"
        self.ctx.with_debug_symbols = getattr(
            args, "with_debug_symbols", False
        )

        have_setup_py_or_similar = False
        if getattr(args, "private", None) is not None:
            project_dir = getattr(args, "private")
            if (os.path.exists(os.path.join(project_dir, "setup.py")) or
                    os.path.exists(os.path.join(project_dir,
                                                "pyproject.toml"))):
                have_setup_py_or_similar = True

        # Process requirements and put version in environ
        if hasattr(args, 'requirements'):
            requirements = []

            # Add dependencies from setup.py, but only if they are recipes
            # (because otherwise, setup.py itself will install them later)
            if (have_setup_py_or_similar and
                    getattr(args, "use_setup_py", False)):
                try:
                    info("Analyzing package dependencies. MAY TAKE A WHILE.")
                    # Get all the dependencies corresponding to a recipe:
                    dependencies = [
                        dep.lower() for dep in
                        get_dep_names_of_package(
                            args.private,
                            keep_version_pins=True,
                            recursive=True,
                            verbose=True,
                        )
                    ]
                    info("Dependencies obtained: " + str(dependencies))
                    all_recipes = [
                        recipe.lower() for recipe in
                        set(Recipe.list_recipes(self.ctx))
                    ]
                    dependencies = set(dependencies).intersection(
                        set(all_recipes)
                    )
                    # Add dependencies to argument list:
                    if len(dependencies) > 0:
                        if len(args.requirements) > 0:
                            args.requirements += u","
                        args.requirements += u",".join(dependencies)
                except ValueError:
                    # Not a python package, apparently.
                    warning(
                        "Processing failed, is this project a valid "
                        "package? Will continue WITHOUT setup.py deps."
                    )

            # Parse --requirements argument list:
            for requirement in split_argument_list(args.requirements):
                if "==" in requirement:
                    requirement, version = requirement.split(u"==", 1)
                    os.environ["VERSION_{}".format(requirement)] = version
                    info('Recipe {}: version "{}" requested'.format(
                        requirement, version))
                requirements.append(requirement)
            args.requirements = u",".join(requirements)

        self.warn_on_deprecated_args(args)

        self.storage_dir = args.storage_dir
        self.ctx.setup_dirs(self.storage_dir)
        self.sdk_dir = args.sdk_dir
        self.ndk_dir = args.ndk_dir
        self.android_api = args.android_api
        self.ndk_api = args.ndk_api
        self.ctx.symlink_bootstrap_files = args.symlink_bootstrap_files
        self.ctx.java_build_tool = args.java_build_tool

        self._archs = args.arch

        self.ctx.local_recipes = args.local_recipes
        self.ctx.copy_libs = args.copy_libs

        self.ctx.activity_class_name = args.activity_class_name
        self.ctx.service_class_name = args.service_class_name

        # Each subparser corresponds to a method
        command = args.subparser_name.replace('-', '_')
        getattr(self, command)(args)

    @staticmethod
    def warn_on_carriage_return_args(args):
        for check_arg in args:
            if '\r' in check_arg:
                warning("Argument '{}' contains a carriage return (\\r).".format(str(check_arg.replace('\r', ''))))
                warning("Invoking this program via scripts which use CRLF instead of LF line endings will have undefined behaviour.")

    def warn_on_deprecated_args(self, args):
        """
        Print warning messages for any deprecated arguments that were passed.
        """

        # Output warning if setup.py is present and neither --ignore-setup-py
        # nor --use-setup-py was specified.
        if getattr(args, "private", None) is not None and \
                (os.path.exists(os.path.join(args.private, "setup.py")) or
                 os.path.exists(os.path.join(args.private, "pyproject.toml"))
                ):
            if not getattr(args, "use_setup_py", False) and \
                    not getattr(args, "ignore_setup_py", False):
                warning("  **** FUTURE BEHAVIOR CHANGE WARNING ****")
                warning("Your project appears to contain a setup.py file.")
                warning("Currently, these are ignored by default.")
                warning("This will CHANGE in an upcoming version!")
                warning("")
                warning("To ensure your setup.py is ignored, please specify:")
                warning("    --ignore-setup-py")
                warning("")
                warning("To enable what will some day be the default, specify:")
                warning("    --use-setup-py")

        # NDK version is now determined automatically
        if args.ndk_version is not None:
            warning('--ndk-version is deprecated and no longer necessary, '
                    'the value you passed is ignored')
        if 'ANDROIDNDKVER' in environ:
            warning('$ANDROIDNDKVER is deprecated and no longer necessary, '
                    'the value you set is ignored')

    def hook(self, name):
        if not self.args.hook:
            return
        if not hasattr(self, "hook_module"):
            # first time, try to load the hook module
            self.hook_module = load_source(
                "pythonforandroid.hook", self.args.hook)
        if hasattr(self.hook_module, name):
            info("Hook: execute {}".format(name))
            getattr(self.hook_module, name)(self)
        else:
            info("Hook: ignore {}".format(name))

    @property
    def default_storage_dir(self):
        udd = user_data_dir('python-for-android')
        if ' ' in udd:
            udd = '~/.python-for-android'
        return udd

    @staticmethod
    def _read_configuration():
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
        """
        Prints recipes basic info, e.g.
        .. code-block:: bash
            python3      3.7.1
                depends: ['hostpython3', 'sqlite3', 'openssl', 'libffi']
                conflicts: []
                optional depends: ['sqlite3', 'libffi', 'openssl']
        """
        ctx = self.ctx
        if args.compact:
            print(" ".join(set(Recipe.list_recipes(ctx))))
        else:
            for name in sorted(Recipe.list_recipes(ctx)):
                try:
                    recipe = Recipe.get_recipe(name, ctx)
                except (IOError, ValueError):
                    warning('Recipe "{}" could not be loaded'.format(name))
                except SyntaxError:
                    import traceback
                    traceback.print_exc()
                    warning(('Recipe "{}" could not be loaded due to a '
                             'syntax error').format(name))
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

    def bootstraps(self, _args):
        """List all the bootstraps available to build with."""
        for bs in Bootstrap.all_bootstraps():
            bs = Bootstrap.get_bootstrap(bs, self.ctx)
            print('{Fore.BLUE}{Style.BRIGHT}{bs.name}{Style.RESET_ALL}'
                  .format(bs=bs, Fore=Out_Fore, Style=Out_Style))
            print('    {Fore.GREEN}depends: {bs.recipe_depends}{Fore.RESET}'
                  .format(bs=bs, Fore=Out_Fore))

    def clean(self, args):
        components = args.component

        component_clean_methods = {
            'all': self.clean_all,
            'dists': self.clean_dists,
            'distributions': self.clean_dists,
            'builds': self.clean_builds,
            'bootstrap_builds': self.clean_bootstrap_builds,
            'downloads': self.clean_download_cache}

        for component in components:
            if component not in component_clean_methods:
                raise BuildInterruptingException((
                    'Asked to clean "{}" but this argument is not '
                    'recognised'.format(component)))
            component_clean_methods[component](args)

    def clean_all(self, args):
        """Delete all build components; the package cache, package builds,
        bootstrap builds and distributions."""
        self.clean_dists(args)
        self.clean_builds(args)
        self.clean_download_cache(args)

    def clean_dists(self, _args):
        """Delete all compiled distributions in the internal distribution
        directory."""
        ctx = self.ctx
        if exists(ctx.dist_dir):
            shutil.rmtree(ctx.dist_dir)

    def clean_bootstrap_builds(self, _args):
        """Delete all the bootstrap builds."""
        if exists(join(self.ctx.build_dir, 'bootstrap_builds')):
            shutil.rmtree(join(self.ctx.build_dir, 'bootstrap_builds'))
        # for bs in Bootstrap.all_bootstraps():
        #     bs = Bootstrap.get_bootstrap(bs, self.ctx)
        #     if bs.build_dir and exists(bs.build_dir):
        #         info('Cleaning build for {} bootstrap.'.format(bs.name))
        #         shutil.rmtree(bs.build_dir)

    def clean_builds(self, _args):
        """Delete all build caches for each recipe, python-install, java code
        and compiled libs collection.

        This does *not* delete the package download cache or the final
        distributions.  You can also use clean_recipe_build to delete the build
        of a specific recipe.
        """
        ctx = self.ctx
        if exists(ctx.build_dir):
            shutil.rmtree(ctx.build_dir)
        if exists(ctx.python_installs_dir):
            shutil.rmtree(ctx.python_installs_dir)
        libs_dir = join(self.ctx.build_dir, 'libs_collections')
        if exists(libs_dir):
            shutil.rmtree(libs_dir)

    def clean_recipe_build(self, args):
        """Deletes the build files of the given recipe.

        This is intended for debug purposes. You may experience
        strange behaviour or problems with some recipes if their
        build has made unexpected state changes. If this happens, run
        clean_builds, or attempt to clean other recipes until things
        work again.
        """
        recipe = Recipe.get_recipe(args.recipe, self.ctx)
        info('Cleaning build for {} recipe.'.format(recipe.name))
        recipe.clean_build()
        if not args.no_clean_dists:
            self.clean_dists(args)

    def clean_download_cache(self, args):
        """ Deletes a download cache for recipes passed as arguments. If no
        argument is passed, it'll delete *all* downloaded caches. ::

            p4a clean_download_cache kivy,pyjnius

        This does *not* delete the build caches or final distributions.
        """
        ctx = self.ctx
        if hasattr(args, 'recipes') and args.recipes:
            for package in args.recipes:
                remove_path = join(ctx.packages_path, package)
                if exists(remove_path):
                    shutil.rmtree(remove_path)
                    info('Download cache removed for: "{}"'.format(package))
                else:
                    warning('No download cache found for "{}", skipping'.format(
                        package))
        else:
            if exists(ctx.packages_path):
                shutil.rmtree(ctx.packages_path)
                info('Download cache removed.')
            else:
                print('No cache found at "{}"'.format(ctx.packages_path))

    @require_prebuilt_dist
    def export_dist(self, args):
        """Copies a created dist to an output dir.

        This makes it easy to navigate to the dist to investigate it
        or call build.py, though you do not in general need to do this
        and can use the apk command instead.
        """
        ctx = self.ctx
        dist = dist_from_args(ctx, args)
        if dist.needs_build:
            raise BuildInterruptingException(
                'You asked to export a dist, but there is no dist '
                'with suitable recipes available. For now, you must '
                ' create one first with the create argument.')
        if args.symlink:
            shprint(sh.ln, '-s', dist.dist_dir, args.output_dir)
        else:
            shprint(sh.cp, '-r', dist.dist_dir, args.output_dir)

    @property
    def _dist(self):
        ctx = self.ctx
        dist = dist_from_args(ctx, self.args)
        ctx.distribution = dist
        return dist

    @staticmethod
    def _fix_args(args):
        """
        Manually fixing these arguments at the string stage is
        unsatisfactory and should probably be changed somehow, but
        we can't leave it until later as the build.py scripts assume
        they are in the current directory.
        works in-place
        :param args: parser args
        """

        fix_args = ('--dir', '--private', '--add-jar', '--add-source',
                    '--whitelist', '--blacklist', '--presplash', '--icon')
        unknown_args = args.unknown_args

        for asset in args.assets:
            if ":" in asset:
                asset_src, asset_dest = asset.split(":")
            else:
                asset_src = asset_dest = asset
            # take abspath now, because build.py will be run in bootstrap dir
            unknown_args += ["--asset", os.path.abspath(asset_src)+":"+asset_dest]
        for i, arg in enumerate(unknown_args):
            argx = arg.split('=')
            if argx[0] in fix_args:
                if len(argx) > 1:
                    unknown_args[i] = '='.join(
                        (argx[0], realpath(expanduser(argx[1]))))
                elif i + 1 < len(unknown_args):
                    unknown_args[i+1] = realpath(expanduser(unknown_args[i+1]))

    @staticmethod
    def _prepare_release_env(args):
        """
        prepares envitonment dict with the necessary flags for signing an apk
        :param args: parser args
        """
        env = os.environ.copy()
        if args.build_mode == 'release':
            if args.keystore:
                env['P4A_RELEASE_KEYSTORE'] = realpath(expanduser(args.keystore))
            if args.signkey:
                env['P4A_RELEASE_KEYALIAS'] = args.signkey
            if args.keystorepw:
                env['P4A_RELEASE_KEYSTORE_PASSWD'] = args.keystorepw
            if args.signkeypw:
                env['P4A_RELEASE_KEYALIAS_PASSWD'] = args.signkeypw
            elif args.keystorepw and 'P4A_RELEASE_KEYALIAS_PASSWD' not in env:
                env['P4A_RELEASE_KEYALIAS_PASSWD'] = args.keystorepw

        return env

    def _build_package(self, args, package_type):
        """
        Creates an android package using gradle
        :param args: parser args
        :param package_type: one of 'apk', 'aar', 'aab'
        :return (gradle output, build_args)
        """
        ctx = self.ctx
        dist = self._dist
        bs = Bootstrap.get_bootstrap(args.bootstrap, ctx)
        ctx.prepare_bootstrap(bs)
        self._fix_args(args)
        env = self._prepare_release_env(args)

        with current_directory(dist.dist_dir):
            self.hook("before_apk_build")
            os.environ["ANDROID_API"] = str(self.ctx.android_api)
            build = load_source('build', join(dist.dist_dir, 'build.py'))
            build_args = build.parse_args_and_make_package(
                args.unknown_args
            )

            self.hook("after_apk_build")
            self.hook("before_apk_assemble")
            build_tools_versions = os.listdir(join(ctx.sdk_dir,
                                                   'build-tools'))
            build_tools_versions = sorted(build_tools_versions,
                                          key=LooseVersion)
            build_tools_version = build_tools_versions[-1]
            info(('Detected highest available build tools '
                  'version to be {}').format(build_tools_version))

            if build_tools_version < '25.0':
                raise BuildInterruptingException(
                    'build_tools >= 25 is required, but %s is installed' % build_tools_version)
            if not exists("gradlew"):
                raise BuildInterruptingException("gradlew file is missing")

            env["ANDROID_NDK_HOME"] = self.ctx.ndk_dir
            env["ANDROID_HOME"] = self.ctx.sdk_dir

            gradlew = sh.Command('./gradlew')

            if exists('/usr/bin/dos2unix'):
                # .../dists/bdisttest_python3/gradlew
                # .../build/bootstrap_builds/sdl2-python3/gradlew
                # if docker on windows, gradle contains CRLF
                output = shprint(
                    sh.Command('dos2unix'), gradlew._path.decode('utf8'),
                    _tail=20, _critical=True, _env=env
                )
            if args.build_mode == "debug":
                if package_type == "aab":
                    raise BuildInterruptingException(
                        "aab is meant only for distribution and is not available in debug mode. "
                        "Instead, you can use apk while building for debugging purposes."
                    )
                gradle_task = "assembleDebug"
            elif args.build_mode == "release":
                if package_type in ["apk", "aar"]:
                    gradle_task = "assembleRelease"
                elif package_type == "aab":
                    gradle_task = "bundleRelease"
            else:
                raise BuildInterruptingException(
                    "Unknown build mode {} for apk()".format(args.build_mode))
            output = shprint(gradlew, gradle_task, _tail=20,
                             _critical=True, _env=env)
        return output, build_args

    def _finish_package(self, args, output, build_args, package_type, output_dir):
        """
        Finishes the package after the gradle script run
        :param args: the parser args
        :param output: RunningCommand output
        :param build_args: build args as returned by build.parse_args
        :param package_type: one of 'apk', 'aar', 'aab'
        :param output_dir: where to put the package file
        """

        package_glob = "*-{}.%s" % package_type
        package_add_version = True

        self.hook("after_apk_assemble")

        info_main('# Copying android package to current directory')

        package_re = re.compile(r'.*Package: (.*\.apk)$')
        package_file = None
        for line in reversed(output.splitlines()):
            m = package_re.match(line)
            if m:
                package_file = m.groups()[0]
                break
        if not package_file:
            info_main('# Android package filename not found in build output. Guessing...')
            if args.build_mode == "release":
                suffixes = ("release", "release-unsigned")
            else:
                suffixes = ("debug", )
            for suffix in suffixes:

                package_files = glob.glob(join(output_dir, package_glob.format(suffix)))
                if package_files:
                    if len(package_files) > 1:
                        info('More than one built APK found... guessing you '
                             'just built {}'.format(package_files[-1]))
                    package_file = package_files[-1]
                    break
            else:
                raise BuildInterruptingException('Couldn\'t find the built APK')

        info_main('# Found android package file: {}'.format(package_file))
        package_extension = f".{package_type}"
        if package_add_version:
            info('# Add version number to android package')
            package_name = basename(package_file)[:-len(package_extension)]
            package_file_dest = "{}-{}-{}".format(
                package_name, build_args.version, package_extension)
            info('# Android package renamed to {}'.format(package_file_dest))
            shprint(sh.cp, package_file, package_file_dest)
        else:
            shprint(sh.cp, package_file, './')

    @require_prebuilt_dist
    def apk(self, args):
        output, build_args = self._build_package(args, package_type='apk')
        output_dir = join(self._dist.dist_dir, "build", "outputs", 'apk', args.build_mode)
        self._finish_package(args, output, build_args, 'apk', output_dir)

    @require_prebuilt_dist
    def aar(self, args):
        output, build_args = self._build_package(args, package_type='aar')
        output_dir = join(self._dist.dist_dir, "build", "outputs", 'aar')
        self._finish_package(args, output, build_args, 'aar', output_dir)

    @require_prebuilt_dist
    def aab(self, args):
        output, build_args = self._build_package(args, package_type='aab')
        output_dir = join(self._dist.dist_dir, "build", "outputs", 'bundle', args.build_mode)
        self._finish_package(args, output, build_args, 'aab', output_dir)

    @require_prebuilt_dist
    def create(self, args):
        """Create a distribution directory if it doesn't already exist, run
        any recipes if necessary, and build the apk.
        """
        pass  # The decorator does everything

    def archs(self, _args):
        """List the target architectures available to be built for."""
        print('{Style.BRIGHT}Available target architectures are:'
              '{Style.RESET_ALL}'.format(Style=Out_Style))
        for arch in self.ctx.archs:
            print('    {}'.format(arch.arch))

    def dists(self, args):
        """The same as :meth:`distributions`."""
        self.distributions(args)

    def distributions(self, _args):
        """Lists all distributions currently available (i.e. that have already
        been built)."""
        ctx = self.ctx
        dists = Distribution.get_distributions(ctx)

        if dists:
            print('{Style.BRIGHT}Distributions currently installed are:'
                  '{Style.RESET_ALL}'.format(Style=Out_Style))
            pretty_log_dists(dists, print)
        else:
            print('{Style.BRIGHT}There are no dists currently built.'
                  '{Style.RESET_ALL}'.format(Style=Out_Style))

    def delete_dist(self, _args):
        dist = self._dist
        if not dist.folder_exists():
            info('No dist exists that matches your specifications, '
                 'exiting without deleting.')
            return
        dist.delete()

    def sdk_tools(self, args):
        """Runs the android binary from the detected SDK directory, passing
        all arguments straight to it. This binary is used to install
        e.g. platform-tools for different API level targets. This is
        intended as a convenience function if android is not in your
        $PATH.
        """
        ctx = self.ctx
        ctx.prepare_build_environment(user_sdk_dir=self.sdk_dir,
                                      user_ndk_dir=self.ndk_dir,
                                      user_android_api=self.android_api,
                                      user_ndk_api=self.ndk_api)
        android = sh.Command(join(ctx.sdk_dir, 'tools', args.tool))
        output = android(
            *args.unknown_args, _iter=True, _out_bufsize=1, _err_to_out=True)
        for line in output:
            sys.stdout.write(line)
            sys.stdout.flush()

    def adb(self, args):
        """Runs the adb binary from the detected SDK directory, passing all
        arguments straight to it. This is intended as a convenience
        function if adb is not in your $PATH.
        """
        self._adb(args.unknown_args)

    def logcat(self, args):
        """Runs ``adb logcat`` using the adb binary from the detected SDK
        directory. All extra args are passed as arguments to logcat."""
        self._adb(['logcat'] + args.unknown_args)

    def _adb(self, commands):
        """Call the adb executable from the SDK, passing the given commands as
        arguments."""
        ctx = self.ctx
        ctx.prepare_build_environment(user_sdk_dir=self.sdk_dir,
                                      user_ndk_dir=self.ndk_dir,
                                      user_android_api=self.android_api,
                                      user_ndk_api=self.ndk_api)
        if platform in ('win32', 'cygwin'):
            adb = sh.Command(join(ctx.sdk_dir, 'platform-tools', 'adb.exe'))
        else:
            adb = sh.Command(join(ctx.sdk_dir, 'platform-tools', 'adb'))
        info_notify('Starting adb...')
        output = adb(*commands, _iter=True, _out_bufsize=1, _err_to_out=True)
        for line in output:
            sys.stdout.write(line)
            sys.stdout.flush()

    def recommendations(self, args):
        print_recommendations()

    def build_status(self, _args):
        """Print the status of the specified build. """
        print('{Style.BRIGHT}Bootstraps whose core components are probably '
              'already built:{Style.RESET_ALL}'.format(Style=Out_Style))

        bootstrap_dir = join(self.ctx.build_dir, 'bootstrap_builds')
        if exists(bootstrap_dir):
            for filen in os.listdir(bootstrap_dir):
                print('    {Fore.GREEN}{Style.BRIGHT}{filen}{Style.RESET_ALL}'
                      .format(filen=filen, Fore=Out_Fore, Style=Out_Style))

        print('{Style.BRIGHT}Recipes that are probably already built:'
              '{Style.RESET_ALL}'.format(Style=Out_Style))
        other_builds_dir = join(self.ctx.build_dir, 'other_builds')
        if exists(other_builds_dir):
            for filen in sorted(os.listdir(other_builds_dir)):
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


if __name__ == "__main__":
    main()
