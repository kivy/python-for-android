"""Simple functions for checking dependency versions."""

from distutils.version import LooseVersion
from os.path import join
from pythonforandroid.logger import info, warning
from pythonforandroid.util import BuildInterruptingException

# We only check the NDK major version
MIN_NDK_VERSION = 17
MAX_NDK_VERSION = 17

RECOMMENDED_NDK_VERSION = '17c'
OLD_NDK_MESSAGE = 'Older NDKs may not be compatible with all p4a features.'
NEW_NDK_MESSAGE = 'Newer NDKs may not be fully supported by p4a.'


def check_ndk_version(ndk_dir):
    # Check the NDK version against what is currently recommended
    version = read_ndk_version(ndk_dir)

    if version is None:
        return  # if we failed to read the version, just don't worry about it

    major_version = version.version[0]

    info('Found NDK revision {}'.format(version))

    if major_version < MIN_NDK_VERSION:
        warning('Minimum recommended NDK version is {}'.format(
            RECOMMENDED_NDK_VERSION))
        warning(OLD_NDK_MESSAGE)
    elif major_version > MAX_NDK_VERSION:
        warning('Maximum recommended NDK version is {}'.format(
            RECOMMENDED_NDK_VERSION))
        warning(NEW_NDK_MESSAGE)


def read_ndk_version(ndk_dir):
    """Read the NDK version from the NDK dir, if possible"""
    try:
        with open(join(ndk_dir, 'source.properties')) as fileh:
            ndk_data = fileh.read()
    except IOError:
        info('Could not determine NDK version, no source.properties '
             'in the NDK dir')
        return

    for line in ndk_data.split('\n'):
        if line.startswith('Pkg.Revision'):
            break
    else:
        info('Could not parse $NDK_DIR/source.properties, not checking '
             'NDK version')
        return

    # Line should have the form "Pkg.Revision = ..."
    ndk_version = LooseVersion(line.split('=')[-1].strip())

    return ndk_version


MIN_TARGET_API = 26

# highest version tested to work fine with SDL2
# should be a good default for other bootstraps too
RECOMMENDED_TARGET_API = 27

ARMEABI_MAX_TARGET_API = 21
OLD_API_MESSAGE = (
    'Target APIs lower than 26 are no longer supported on Google Play, '
    'and are not recommended. Note that the Target API can be higher than '
    'your device Android version, and should usually be as high as possible.')


def check_target_api(api, arch):
    """Warn if the user's target API is less than the current minimum
    recommendation
    """

    if api >= ARMEABI_MAX_TARGET_API and arch == 'armeabi':
        raise BuildInterruptingException(
            'Asked to build for armeabi architecture with API '
            '{}, but API {} or greater does not support armeabi'.format(
                api, ARMEABI_MAX_TARGET_API),
            instructions='You probably want to build with --arch=armeabi-v7a instead')

    if api < MIN_TARGET_API:
        warning('Target API {} < {}'.format(api, MIN_TARGET_API))
        warning(OLD_API_MESSAGE)


MIN_NDK_API = 21
RECOMMENDED_NDK_API = 21
OLD_NDK_API_MESSAGE = ('NDK API less than {} is not supported'.format(MIN_NDK_API))


def check_ndk_api(ndk_api, android_api):
    """Warn if the user's NDK is too high or low."""
    if ndk_api > android_api:
        raise BuildInterruptingException(
            'Target NDK API is {}, higher than the target Android API {}.'.format(
                ndk_api, android_api),
            instructions=('The NDK API is a minimum supported API number and must be lower '
                          'than the target Android API'))

    if ndk_api < MIN_NDK_API:
        warning(OLD_NDK_API_MESSAGE)
