from setuptools import Command

import sys
from os.path import realpath, join, exists, dirname, curdir, basename, split
from os import makedirs
from glob import glob
from shutil import rmtree, copyfile


def argv_contains(t):
    for arg in sys.argv:
        if arg.startswith(t):
            return True
    return False


class Bdist(Command):

    user_options = []
    package_type = None

    def initialize_options(self):
        for option in self.user_options:
            setattr(self, option[0].strip('=').replace('-', '_'), None)

        option_dict = self.distribution.get_option_dict(self.package_type)

        # This is a hack, we probably aren't supposed to loop through
        # the option_dict so early because distutils does exactly the
        # same thing later to check that we support the
        # options. However, it works...
        for (option, (source, value)) in option_dict.items():
            setattr(self, option, str(value))

    def finalize_options(self):

        setup_options = self.distribution.get_option_dict(self.package_type)
        for (option, (source, value)) in setup_options.items():
            if source == 'command line':
                continue
            if not argv_contains('--' + option):
                # allow 'permissions': ['permission', 'permission] in apk
                if option == 'permissions':
                    for perm in value:
                        sys.argv.append('--permission={}'.format(perm))
                elif value in (None, 'None'):
                    sys.argv.append('--{}'.format(option))
                else:
                    sys.argv.append('--{}={}'.format(option, value))

        # Inject some argv options from setup.py if the user did not
        # provide them
        if not argv_contains('--name'):
            name = self.distribution.get_name()
            sys.argv.append('--name="{}"'.format(name))
            self.name = name

        if not argv_contains('--package'):
            package = 'org.test.{}'.format(self.name.lower().replace(' ', ''))
            print('WARNING: You did not supply an Android package '
                  'identifier, trying {} instead.'.format(package))
            print('         This may fail if this is not a valid identifier')
            sys.argv.append('--package={}'.format(package))

        if not argv_contains('--version'):
            version = self.distribution.get_version()
            sys.argv.append('--version={}'.format(version))

        if not argv_contains('--arch'):
            arch = 'armeabi-v7a'
            self.arch = arch
            sys.argv.append('--arch={}'.format(arch))

    def run(self):
        self.prepare_build_dir()

        from pythonforandroid.entrypoints import main
        sys.argv[1] = self.package_type
        main()

    def prepare_build_dir(self):

        if argv_contains('--private') and not argv_contains('--launcher'):
            print('WARNING: Received --private argument when this would '
                  'normally be generated automatically.')
            print('         This is probably bad unless you meant to do '
                  'that.')

        bdist_dir = 'build/bdist.android-{}'.format(self.arch)
        if exists(bdist_dir):
            rmtree(bdist_dir)
        makedirs(bdist_dir)

        globs = []
        for directory, patterns in self.distribution.package_data.items():
            for pattern in patterns:
                globs.append(join(directory, pattern))

        filens = []
        for pattern in globs:
            filens.extend(glob(pattern))

        main_py_dirs = []
        if not argv_contains('--launcher'):
            for filen in filens:
                new_dir = join(bdist_dir, dirname(filen))
                if not exists(new_dir):
                    makedirs(new_dir)
                print('Including {}'.format(filen))
                copyfile(filen, join(bdist_dir, filen))
                if basename(filen) in ('main.py', 'main.pyo'):
                    main_py_dirs.append(filen)

        # This feels ridiculous, but how else to define the main.py dir?
        # Maybe should just fail?
        if not main_py_dirs and not argv_contains('--launcher'):
            print('ERROR: Could not find main.py, so no app build dir defined')
            print('You should name your app entry point main.py')
            exit(1)
        if len(main_py_dirs) > 1:
            print('WARNING: Multiple main.py dirs found, using the shortest path')
        main_py_dirs = sorted(main_py_dirs, key=lambda j: len(split(j)))

        if not argv_contains('--launcher'):
            sys.argv.append('--private={}'.format(
                join(realpath(curdir), bdist_dir, dirname(main_py_dirs[0])))
            )


class BdistAPK(Bdist):
    """distutil command handler for 'apk'."""
    description = 'Create an APK with python-for-android'
    package_type = 'apk'


class BdistAAR(Bdist):
    """distutil command handler for 'aar'."""
    description = 'Create an AAR with python-for-android'
    package_type = 'aar'


class BdistAAB(Bdist):
    """distutil command handler for 'aab'."""
    description = 'Create an AAB with python-for-android'
    package_type = 'aab'


def _set_user_options():
    # This seems like a silly way to do things, but not sure if there's a
    # better way to pass arbitrary options onwards to p4a
    user_options = [('requirements=', None, None), ]
    for i, arg in enumerate(sys.argv):
        if arg.startswith('--'):
            if ('=' in arg or
                    (i < (len(sys.argv) - 1) and not sys.argv[i+1].startswith('-'))):
                user_options.append((arg[2:].split('=')[0] + '=', None, None))
            else:
                user_options.append((arg[2:], None, None))

    BdistAPK.user_options = user_options
    BdistAAB.user_options = user_options
    BdistAAR.user_options = user_options


_set_user_options()
