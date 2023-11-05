'''
Clone Python implementation of Kivy Launcher from kivy/kivy-launcher repo,
install deps specified in the OPTIONS['apk']['requirements'] and put it
to a dist named OPTIONS['apk']['dist-name'].

Tested with P4A Dockerfile at 5fc5241e01fbbc2b23b3749f53ab48f22239f4fc,
kivy-launcher at ad5c5c6e886a310bf6dd187e992df972864d1148 on Windows 8.1
with Docker for Windows and running on Samsung Galaxy Note 9, Android 8.1.

docker run \
    --interactive \
    --tty \
    -v "/c/Users/.../python-for-android/testapps":/home/user/testapps \
    -v ".../python-for-android/pythonforandroid":/home/user/pythonforandroid \
    p4a sh -c '\
        . venv/bin/activate \
        && cd testapps/testlauncherreboot_setup \
        && python sdl2.py apk \
            --sdk-dir $ANDROID_SDK_HOME \
            --ndk-dir $ANDROID_NDK_HOME'
'''

# pylint: disable=import-error,no-name-in-module
from subprocess import Popen
from os import listdir
from os.path import join, dirname, abspath, exists
from pprint import pprint
from setuptools import setup, find_packages

ROOT = dirname(abspath(__file__))
LAUNCHER = join(ROOT, 'launcherapp')

if not exists(LAUNCHER):
    PROC = Popen([
        'git', 'clone',
        'https://github.com/kivy/kivy-launcher',
        LAUNCHER
    ])
    PROC.communicate()
    assert PROC.returncode == 0, PROC.returncode

    pprint(listdir(LAUNCHER))
    pprint(listdir(ROOT))


OPTIONS = {
    'apk': {
        'debug': None,
        'bootstrap': 'sdl2',
        'requirements': (
            'python3,sdl2,kivy,android,pyjnius,plyer'
        ),
        # 'sqlite3,docutils,pygments,'
        # 'cymunk,lxml,pil,openssl,pyopenssl,'
        # 'twisted,audiostream,ffmpeg,numpy'

        'android-api': 27,
        'ndk-api': 21,
        'dist-name': 'bdisttest_python3launcher_sdl2_googlendk',
        'name': 'TestLauncherPy3-sdl2',
        'package': 'org.kivy.testlauncherpy3_sdl2_googlendk',
        'ndk-version': '10.3.2',
        'arch': 'armeabi-v7a',
        'permissions': [
            'ACCESS_COARSE_LOCATION', 'ACCESS_FINE_LOCATION',
            'BLUETOOTH', 'BODY_SENSORS', 'CAMERA', 'INTERNET',
            'NFC', 'READ_EXTERNAL_STORAGE', 'RECORD_AUDIO',
            'USE_FINGERPRINT', 'VIBRATE', 'WAKE_LOCK',
            'WRITE_EXTERNAL_STORAGE'
        ]
    }
}

PACKAGE_DATA = {
    'launcherapp': [
        '*.py', '*.png', '*.ttf', '*.eot', '*.svg', '*.woff',
    ],
    'launcherapp/art': [
        '*.py', '*.png', '*.ttf', '*.eot', '*.svg', '*.woff',
    ],
    'launcherapp/art/fontello': [
        '*.py', '*.png', '*.ttf', '*.eot', '*.svg', '*.woff',
    ],
    'launcherapp/data': [
        '*.py', '*.png', '*.ttf', '*.eot', '*.svg', '*.woff',
    ],
    'launcherapp/launcher': [
        '*.py', '*.png', '*.ttf', '*.eot', '*.svg', '*.woff',
    ]
}

PACKAGES = find_packages()
print('packages are', PACKAGES)

setup(
    name='testlauncherpy3_sdl2_googlendk',
    version='1.0',
    description='p4a sdl2.py apk',
    author='Peter Badida',
    author_email='keyweeusr@gmail.com',
    packages=find_packages(),
    options=OPTIONS,
    package_data=PACKAGE_DATA
)
