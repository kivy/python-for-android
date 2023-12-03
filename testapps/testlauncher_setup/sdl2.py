from setuptools import setup

options = {'apk': {'debug': None,
                   'bootstrap': 'sdl2',
                   'launcher': None,
                   'requirements': (
                        'python3,sdl2,android,'
                        'sqlite3,docutils,pygments,kivy,pyjnius,plyer,'
                        'cymunk,lxml,pil,openssl,pyopenssl,'
                        'twisted'),  # audiostream, ffmpeg, numpy
                   'android-api': 14,
                   'dist-name': 'launchertest_sdl2',
                   'name': 'TestLauncher-sdl2',
                   'package': 'org.kivy.testlauncher_sdl2',
                   'permissions': [
                        'ACCESS_COARSE_LOCATION', 'ACCESS_FINE_LOCATION',
                        'BLUETOOTH', 'BODY_SENSORS', 'CAMERA', 'INTERNET',
                        'NFC', 'READ_EXTERNAL_STORAGE', 'RECORD_AUDIO',
                        'USE_FINGERPRINT', 'VIBRATE', 'WAKE_LOCK',
                        'WRITE_EXTERNAL_STORAGE']
                   }}

setup(
    name='testlauncher_sdl2',
    version='1.0',
    description='p4a sdl2.py apk',
    author='Peter Badida',
    options=options
)
