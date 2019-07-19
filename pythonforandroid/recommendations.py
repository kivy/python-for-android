"""Simple functions for checking dependency versions."""

from distutils.version import LooseVersion
from os.path import join
from pythonforandroid.logger import info, warning
from pythonforandroid.util import BuildInterruptingException

# We only check the NDK major version
MIN_NDK_VERSION = 17
MAX_NDK_VERSION = 17

RECOMMENDED_NDK_VERSION = '17c'
NEW_NDK_MESSAGE = 'Newer NDKs may not be fully supported by p4a.'
NDK_DOWNLOAD_URL = 'https://developer.android.com/ndk/downloads/'


def check_ndk_version(ndk_dir):
    """
    Check the NDK version against what is currently recommended and raise an
    exception of :class:`~pythonforandroid.util.BuildInterruptingException` in
    case that the user tries to use an NDK lower than minimum supported,
    specified via attribute `MIN_NDK_VERSION`.

    .. versionchanged:: 2019.06.06.1.dev0
        Added the ability to get android's NDK `letter version` and also
        rewrote to raise an exception in case that an NDK version lower than
        the minimum supported is detected.
    """
    version = read_ndk_version(ndk_dir)

    if version is None:
        warning(
            'Unable to read the NDK version from the given directory '
            '{}'.format(ndk_dir)
        )
        warning(
            "Make sure your NDK version is greater than {min_supported}. "
            "If you get build errors, download the recommended NDK "
            "{rec_version} from {ndk_url}".format(
                min_supported=MIN_NDK_VERSION,
                rec_version=RECOMMENDED_NDK_VERSION,
                ndk_url=NDK_DOWNLOAD_URL,
            )
        )
        return

    # create a dictionary which will describe the relationship of the android's
    # NDK minor version with the `human readable` letter version, egs:
    # Pkg.Revision = 17.1.4828580 => ndk-17b
    # Pkg.Revision = 17.2.4988734 => ndk-17c
    # Pkg.Revision = 19.0.5232133 => ndk-19 (No letter)
    minor_to_letter = {0: ''}
    minor_to_letter.update(
        {n + 1: chr(i) for n, i in enumerate(range(ord('b'), ord('b') + 25))}
    )

    major_version = version.version[0]
    letter_version = minor_to_letter[version.version[1]]
    string_version = '{major_version}{letter_version}'.format(
        major_version=major_version, letter_version=letter_version
    )

    info('Found NDK version {}'.format(string_version))

    if major_version < MIN_NDK_VERSION:
        raise BuildInterruptingException(
            'The minimum supported NDK version is {min_supported}. You can '
            'download it from {ndk_url}'.format(
                min_supported=MIN_NDK_VERSION, ndk_url=NDK_DOWNLOAD_URL,
            ),
            instructions=(
                'Please, go to the android NDK page ({ndk_url}) and download a'
                ' supported version.\n*** The currently recommended NDK'
                ' version is {rec_version} ***'.format(
                    ndk_url=NDK_DOWNLOAD_URL,
                    rec_version=RECOMMENDED_NDK_VERSION,
                )
            ),
        )
    elif major_version > MAX_NDK_VERSION:
        warning(
            'Maximum recommended NDK version is {}'.format(
                RECOMMENDED_NDK_VERSION
            )
        )
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
