"""Simple functions for checking dependency versions."""

import sys
from os.path import join

import packaging.version

from pythonforandroid.logger import info, warning
from pythonforandroid.util import BuildInterruptingException

# We only check the NDK major version
MIN_NDK_VERSION = 25
MAX_NDK_VERSION = 25

# DO NOT CHANGE LINE FORMAT: buildozer parses the existence of a RECOMMENDED_NDK_VERSION
RECOMMENDED_NDK_VERSION = "25b"

NDK_DOWNLOAD_URL = "https://developer.android.com/ndk/downloads/"

# Important log messages
NEW_NDK_MESSAGE = 'Newer NDKs may not be fully supported by p4a.'
UNKNOWN_NDK_MESSAGE = (
    'Could not determine NDK version, no source.properties in the NDK dir.'
)
PARSE_ERROR_NDK_MESSAGE = (
    'Could not parse $NDK_DIR/source.properties, not checking NDK version.'
)
READ_ERROR_NDK_MESSAGE = (
    'Unable to read the NDK version from the given directory {ndk_dir}.'
)
ENSURE_RIGHT_NDK_MESSAGE = (
    'Make sure your NDK version is greater than {min_supported}. If you get '
    'build errors, download the recommended NDK {rec_version} from {ndk_url}.'
)
NDK_LOWER_THAN_SUPPORTED_MESSAGE = (
    'The minimum supported NDK version is {min_supported}. '
    'You can download it from {ndk_url}.'
)
UNSUPPORTED_NDK_API_FOR_ARMEABI_MESSAGE = (
    'Asked to build for armeabi architecture with API '
    '{req_ndk_api}, but API {max_ndk_api} or greater does not support armeabi.'
)
CURRENT_NDK_VERSION_MESSAGE = (
    'Found NDK version {ndk_version}'
)
RECOMMENDED_NDK_VERSION_MESSAGE = (
    'Maximum recommended NDK version is {recommended_ndk_version}, but newer versions may work.'
)


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
    ndk_version = read_ndk_version(ndk_dir)

    if ndk_version is None:
        warning(READ_ERROR_NDK_MESSAGE.format(ndk_dir=ndk_dir))
        warning(
            ENSURE_RIGHT_NDK_MESSAGE.format(
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
    string_version = f"{ndk_version.major}{minor_to_letter[ndk_version.minor]}"

    info(CURRENT_NDK_VERSION_MESSAGE.format(ndk_version=string_version))

    if ndk_version.major < MIN_NDK_VERSION:
        raise BuildInterruptingException(
            NDK_LOWER_THAN_SUPPORTED_MESSAGE.format(
                min_supported=MIN_NDK_VERSION, ndk_url=NDK_DOWNLOAD_URL
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
    elif ndk_version.major > MAX_NDK_VERSION:
        warning(
            RECOMMENDED_NDK_VERSION_MESSAGE.format(
                recommended_ndk_version=RECOMMENDED_NDK_VERSION
            )
        )
        warning(NEW_NDK_MESSAGE)


def read_ndk_version(ndk_dir):
    """Read the NDK version from the NDK dir, if possible"""
    try:
        with open(join(ndk_dir, 'source.properties')) as fileh:
            ndk_data = fileh.read()
    except IOError:
        info(UNKNOWN_NDK_MESSAGE)
        return

    for line in ndk_data.split('\n'):
        if line.startswith('Pkg.Revision'):
            break
    else:
        info(PARSE_ERROR_NDK_MESSAGE)
        return

    # Line should have the form "Pkg.Revision = ..."
    unparsed_ndk_version = line.split('=')[-1].strip()

    return packaging.version.parse(unparsed_ndk_version)


MIN_TARGET_API = 30

# highest version tested to work fine with SDL2
# should be a good default for other bootstraps too
RECOMMENDED_TARGET_API = 33

ARMEABI_MAX_TARGET_API = 21
OLD_API_MESSAGE = (
    'Target APIs lower than 30 are no longer supported on Google Play, '
    'and are not recommended. Note that the Target API can be higher than '
    'your device Android version, and should usually be as high as possible.')


def check_target_api(api, arch):
    """Warn if the user's target API is less than the current minimum
    recommendation
    """

    # FIXME: Should We remove support for armeabi (ARMv5)?
    if api >= ARMEABI_MAX_TARGET_API and arch == 'armeabi':
        raise BuildInterruptingException(
            UNSUPPORTED_NDK_API_FOR_ARMEABI_MESSAGE.format(
                req_ndk_api=api, max_ndk_api=ARMEABI_MAX_TARGET_API
            ),
            instructions='You probably want to build with --arch=armeabi-v7a instead')

    if api < MIN_TARGET_API:
        warning('Target API {} < {}'.format(api, MIN_TARGET_API))
        warning(OLD_API_MESSAGE)


MIN_NDK_API = 21
RECOMMENDED_NDK_API = 21
OLD_NDK_API_MESSAGE = ('NDK API less than {} is not supported'.format(MIN_NDK_API))
TARGET_NDK_API_GREATER_THAN_TARGET_API_MESSAGE = (
    'Target NDK API is {ndk_api}, '
    'higher than the target Android API {android_api}.'
)


def check_ndk_api(ndk_api, android_api):
    """Warn if the user's NDK is too high or low."""
    if ndk_api > android_api:
        raise BuildInterruptingException(
            TARGET_NDK_API_GREATER_THAN_TARGET_API_MESSAGE.format(
                ndk_api=ndk_api, android_api=android_api
            ),
            instructions=('The NDK API is a minimum supported API number and must be lower '
                          'than the target Android API'))

    if ndk_api < MIN_NDK_API:
        warning(OLD_NDK_API_MESSAGE)


MIN_PYTHON_MAJOR_VERSION = 3
MIN_PYTHON_MINOR_VERSION = 6
MIN_PYTHON_VERSION = packaging.version.Version(
    f"{MIN_PYTHON_MAJOR_VERSION}.{MIN_PYTHON_MINOR_VERSION}"
)
PY2_ERROR_TEXT = (
    'python-for-android no longer supports running under Python 2. Either upgrade to '
    'Python {min_version} or higher (recommended), or revert to python-for-android 2019.07.08.'
).format(min_version=MIN_PYTHON_VERSION)

PY_VERSION_ERROR_TEXT = (
    'Your Python version {user_major}.{user_minor} is not supported by python-for-android, '
    'please upgrade to {min_version} or higher.'
    ).format(
        user_major=sys.version_info.major,
        user_minor=sys.version_info.minor,
        min_version=MIN_PYTHON_VERSION)


def check_python_version():
    # Python 2 special cased because it's a major transition. In the
    # future the major or minor versions can increment more quietly.
    if sys.version_info.major == 2:
        raise BuildInterruptingException(PY2_ERROR_TEXT)

    if (
        sys.version_info.major < MIN_PYTHON_MAJOR_VERSION or
        sys.version_info.minor < MIN_PYTHON_MINOR_VERSION
    ):

        raise BuildInterruptingException(PY_VERSION_ERROR_TEXT)


def print_recommendations():
    """
    Print the main recommended dependency versions as simple key-value pairs.
    """
    print('Min supported NDK version: {}'.format(MIN_NDK_VERSION))
    print('Recommended NDK version: {}'.format(RECOMMENDED_NDK_VERSION))
    print('Min target API: {}'.format(MIN_TARGET_API))
    print('Recommended target API: {}'.format(RECOMMENDED_TARGET_API))
    print('Min NDK API: {}'.format(MIN_NDK_API))
    print('Recommended NDK API: {}'.format(RECOMMENDED_NDK_API))
