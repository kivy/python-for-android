from distutils.core import setup
from setuptools import find_packages

options = {'apk': {'debug': None,
                   'bootstrap': 'pygame',
                   'launcher': None,
                   'requirements': (
                        'python2,pygame,'
                        'sqlite3,docutils,pygments,kivy,pyjnius,plyer,'
                        'audiostream,cymunk,lxml,pil,'  # ffmpeg, openssl
                        'twisted,numpy'),  # pyopenssl
                   'android-api': 14,
                   'dist-name': 'launchertest_pygame',
                   'name': 'TestLauncher-pygame',
                   'package': 'org.kivy.testlauncher_pygame',
                   'permissions': [
                        'ACCESS_COARSE_LOCATION', 'ACCESS_FINE_LOCATION',
                        'BLUETOOTH', 'BODY_SENSORS', 'CAMERA', 'INTERNET',
                        'NFC', 'READ_EXTERNAL_STORAGE', 'RECORD_AUDIO',
                        'USE_FINGERPRINT', 'VIBRATE', 'WAKE_LOCK',
                        'WRITE_EXTERNAL_STORAGE']
                   }}

setup(
    name='testlauncher_pygame',
    version='1.0',
    description='p4a pygame.py apk',
    author='Peter Badida',
    options=options
)
