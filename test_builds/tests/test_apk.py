
from pythonforandroid.toolchain import main
from pythonforandroid.recipe import Recipe

from os import path
import sys

import pytest

# Set these values manually before testing (for now)
ndk_dir = '/home/asandy/android/crystax-ndk-10.3.2'
ndk_version='crystax-ndk-10.3.2'

cur_dir = path.dirname(path.abspath(__file__))
testapps_dir = path.join(path.split(path.split(cur_dir)[0])[0], 'testapps')

orig_argv = sys.argv[:]

def set_argv(argv):
    while sys.argv:
        sys.argv.pop()
    sys.argv.append(orig_argv[0])
    for item in argv:
        sys.argv.append(item)
    for item in orig_argv[1:]:
        if item == '-s':
            continue
        sys.argv.append(item)


argument_combinations = [{'app_dir': path.join(testapps_dir, 'testapp'),
                          'requirements': 'python2,pyjnius,kivy',
                          'packagename': 'p4a_test_sdl2',
                          'bootstrap': 'sdl2',
                          'ndk_dir': ndk_dir,
                          'ndk_version': ndk_version},
                         {'app_dir': path.join(testapps_dir, 'testapp'),
                          'requirements': 'python2,pyjnius,kivy',
                          'packagename': 'p4a_test_pygame',
                          'bootstrap': 'pygame',
                          'ndk_dir': ndk_dir,
                          'ndk_version': ndk_version},
                         {'app_dir': path.join(testapps_dir, 'testapp_flask'),
                          'requirements': 'python2,flask,pyjnius',
                          'packagename': 'p4a_test_flask',
                          'bootstrap': 'webview',
                          'ndk_dir': ndk_dir,
                          'ndk_version': ndk_version},
                         ]

                          
@pytest.mark.parametrize('args', argument_combinations)
def test_build_sdl2(args):

    Recipe.recipes = {}

    set_argv(('apk --requirements={requirements} --private '
              '{app_dir} --package=net.p4a.{packagename} --name={packagename} '
              '--version=0.1 --bootstrap={bootstrap} --android_api=19 '
              '--ndk_dir={ndk_dir} --ndk_version={ndk_version} --debug '
              '--permission VIBRATE '
              '--symlink-java-src '
              '--orientation portrait --dist_name=test-{packagename}').format(
                  **args).split(' '))

    print('argv are', sys.argv)

    main()
    
