from __future__ import print_function
from setuptools import Command
from pythonforandroid import toolchain
import sys

def argv_contains(t):
    for arg in sys.argv:
        if arg.startswith(t):
            return True
    return False


def register_args(*args):
    print('argv before is', sys.argv)
    if len(sys.argv) < 2:
        return
    if sys.argv[1] == 'bdist_apk':
        print('Detected bdist_apk build, registering args {}'.format(args))
        sys.argv.extend(args)

    print('new args are', sys.argv)
    _set_user_options()


class BdistAPK(Command):
    description = 'Create an APK with python-for-android'

    user_options = []

    def initialize_options(self):
        for option in self.user_options:
            setattr(self, option[0].strip('=').replace('-', '_'), None)

    def finalize_options(self):

        # Inject some argv options from setup.py if the user did not
        # provide them
        if not argv_contains('--name'):
            name = self.distribution.get_name()
            print('name is', name)
            sys.argv.append('--name={}'.format(name))
            self.name = name

        if not argv_contains('--package'):
            package = 'org.test.{}'.format(self.name.lower().replace(' ', ''))
            print('WARNING: You did not supply an Android package '
                  'identifier, trying {} instead.'.format(package))
            print('         This may fail if this is not a valid identifier')
            sys.argv.append('--package={}'.format(package))

        if not argv_contains('--version'):
            version = self.distribution.get_version()
            print('version is', version)
            sys.argv.append('--version={}'.format(version))
                    

    def run(self):
        print('running')
        from pythonforandroid.toolchain import main
        sys.argv[1] = 'apk'
        main()



def _set_user_options():
    # This seems like a silly way to do things, but not sure if there's a
    # better way to pass arbitrary options onwards to p4a
    user_options = [('requirements=', None, None),]
    for i, arg in enumerate(sys.argv):
        if arg.startswith('--'):
            if ('=' in arg or
                (i < (len(sys.argv) - 1) and not sys.argv[i+1].startswith('-'))):
                user_options.append((arg[2:].split('=')[0] + '=', None, None))
            else:
                user_options.append((arg[2:], None, None))

    BdistAPK.user_options = user_options
        
