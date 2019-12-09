print('main.py was successfully called')

import os

print('imported os')

print('this dir is', os.path.abspath(os.curdir))

print('contents of this dir', os.listdir('./'))

import sys

print('pythonpath is', sys.path)

import kivy

print('imported kivy')
print('file is', kivy.__file__)

from kivy.app import App

from kivy.lang import Builder
from kivy.properties import StringProperty

from kivy.uix.popup import Popup
from kivy.clock import Clock

print('Imported kivy')
from kivy.utils import platform

print('platform is', platform)

# Test cryptography
try:
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
    f = Fernet(key)
    cryptography_encrypted = f.encrypt(
        b'A really secret message. Not for prying eyes.')
    cryptography_decrypted = f.decrypt(cryptography_encrypted)
except Exception as e1:
    print('**************************')
    print('Error on cryptography operations:\n{}'.format(e1))
    print('**************************')
    cryptography_encrypted = 'Error'
    cryptography_decrypted = 'Error'

# Test pycrypto
crypto_hash_message = 'A secret message'
try:
    from Crypto.Hash import SHA256

    hash = SHA256.new()
    hash.update(crypto_hash_message)
    crypto_hash_hexdigest = hash.hexdigest()
except Exception as e2:
    print('**************************')
    print('Error on Crypto operations:\n{}'.format(e2))
    print('**************************')
    crypto_hash_hexdigest = 'Error'

# Test scrypt
try:
    from scrypt import *

    status_import_scrypt = 'Success'
except ImportError as e3:
    print('**************************')
    print('Unable to import scrypt:\n{}'.format(e3))
    print('**************************')
    status_import_scrypt = 'Error'

# Test M2Crypto
try:
    from M2Crypto import *

    status_import_m2crypto = 'Success'
except ImportError as e5:
    print('**************************')
    print('Unable to import M2Crypto:\n{}'.format(e5))
    print('**************************\n')
    status_import_m2crypto = 'Error'

# Test pysha3
try:
    import sha3

    print('Ok imported pysha3, testing some basic operations...')
    k = sha3.keccak_512()
    k.update(b"data")
    print('Test pysha3 operation (keccak_512): {}'.format(k.hexdigest()))
    status_import_pysha3 = 'Success'
except ImportError as e6:
    print('**************************')
    print('Unable to import/operate with pysha3:\n{}'.format(e6))
    print('**************************')
    status_import_pysha3 = 'Error'

# Test pycryptodome
try:
    from Crypto.PublicKey import RSA

    print('Ok imported pycryptodome, testing some basic operations...')
    secret_code = "Unguessable"
    key = RSA.generate(2048)
    encrypted_key = key.export_key(passphrase=secret_code, pkcs=8,
                                   protection="scryptAndAES128-CBC")
    print('\t -> Testing key for secret code "Unguessable": {}'.format(
        encrypted_key))

    file_out = open("rsa_key.bin", "wb")
    file_out.write(encrypted_key)
    print('\t -> Testing key write: {}'.format(
        'ok' if os.path.exists(file_out) else 'fail'))

    print('\t -> Testing Public key:'.format(key.publickey().export_key()))
    status_import_pycryptodome = 'Success (import and doing simple operations)'
except ImportError as e6:
    print('**************************')
    print('Unable to import/operate with pycryptodome:\n{}'.format(e6))
    print('**************************')
    status_import_pycryptodome = 'Error'

# Test libtorrent
try:
    import libtorrent as lt

    print('Imported libtorrent version {}'.format(lt.version))
    status_import_libtorrent = 'Success (version is: {})'.format(lt.version)
except Exception as e4:
    print('**************************')
    print('Unable to import libtorrent:\n{}'.format(e4))
    print('**************************')
    status_import_libtorrent = 'Error'

kv = '''
#:import Metrics kivy.metrics.Metrics
#:import sys sys

<FixedSizeButton@Button>:
    size_hint_y: None
    height: dp(60)

<TestImport@BoxLayout>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    test_module: ''
    test_result: ''
    Label:
        height: self.texture_size[1]
        size_hint_y: None
        text_size: self.size[0], None
        markup: True
        text: '[b]*** TEST {} MODULE ***[/b]'.format(self.parent.test_module)
        halign: 'center'
    Label:
        height: self.texture_size[1]
        size_hint_y: None
        text_size: self.size[0], None
        markup: True
        text:
            'Import {}: [color=a0a0a0]{}[/color]'.format(
            self.parent.test_module, self.parent.test_result)
        halign: 'left'
    Widget:
        size_hint_y: None
        height: 20


ScrollView:
    GridLayout:
        cols: 1
        size_hint_y: None
        height: self.minimum_height
        FixedSizeButton:
            text: 'test pyjnius'
            on_press: app.test_pyjnius()
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            text_size: self.size[0], None
            markup: True
            text: '[b]*** TEST CRYPTOGRAPHY MODULE ***[/b]'
            halign: 'center'
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            text_size: self.size[0], None
            markup: True
            text: 
                'Cryptography decrypted:\\n[color=a0a0a0]%s[/color]\\n' \\
                'Cryptography encrypted:\\n[color=a0a0a0]%s[/color]' % (
                app.cryptography_decrypted, app.cryptography_encrypted)
            halign: 'left'
        Widget:
            size_hint_y: None
            height: 20
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            text_size: self.size[0], None
            markup: True
            text: '[b]*** TEST CRYPTO MODULE ***[/b]'
            halign: 'center'
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            text_size: self.size[0], None
            markup: True
            text:
                'Crypto message: \\n[color=a0a0a0]%s[/color]\\n'\\
                'Crypto hex: \\n[color=a0a0a0]%s[/color]' % (
                app.crypto_hash_message, app.crypto_hash_hexdigest)
            halign: 'left'
        Widget:
            size_hint_y: None
            height: 20
        TestImport:
            test_module: 'scrypt'
            test_result: app.status_import_scrypt
        TestImport:
            test_module: 'm2crypto'
            test_result: app.status_import_m2crypto
        TestImport:
            test_module: 'pysha3'
            test_result: app.status_import_pysha3
        TestImport:
            test_module: 'pycryptodome'
            test_result: app.status_import_pycryptodome
        TestImport:
            test_module: 'libtorrent'
            test_result: app.status_import_libtorrent
        Image:
            keep_ratio: False
            allow_stretch: True
            source: 'colours.png'
            size_hint_y: None
            height: dp(100)
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            font_size: 100
            text_size: self.size[0], None
            markup: True
            text: '[b]Kivy[/b] on [b]SDL2[/b] on [b]Android[/b]!'
            halign: 'center'
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            text_size: self.size[0], None
            markup: True
            text: sys.version
            halign: 'center'
            padding_y: dp(10)
        Widget:
            size_hint_y: None
            height: 20
        Label:
            height: self.texture_size[1]
            size_hint_y: None
            font_size: 50
            text_size: self.size[0], None
            markup: True
            text:
                'dpi: [color=a0a0a0]%s[/color]\\n'\\
                'density: [color=a0a0a0]%s[/color]\\n'\\
                'fontscale: [color=a0a0a0]%s[/color]' % (
                Metrics.dpi, Metrics.density, Metrics.fontscale)
            halign: 'center'
        FixedSizeButton:
            text: 'test ctypes'
            on_press: app.test_ctypes()
        Widget:
            size_hint_y: None
            height: 1000
            on_touch_down: print('touched at', args[-1].pos)

<ErrorPopup>:
    title: 'Error' 
    size_hint: 0.75, 0.75
    Label:
        text: root.error_text
'''


class ErrorPopup(Popup):
    error_text = StringProperty('')


def raise_error(error):
    print('ERROR:', error)
    ErrorPopup(error_text=error).open()


class TestApp(App):
    cryptography_encrypted = cryptography_encrypted
    cryptography_decrypted = cryptography_decrypted
    crypto_hash_message = crypto_hash_message
    crypto_hash_hexdigest = crypto_hash_hexdigest
    status_import_scrypt = status_import_scrypt
    status_import_m2crypto = status_import_m2crypto
    status_import_pysha3 = status_import_pysha3
    status_import_pycryptodome = status_import_pycryptodome
    status_import_libtorrent = status_import_libtorrent

    def build(self):
        root = Builder.load_string(kv)
        Clock.schedule_interval(self.print_something, 2)
        # Clock.schedule_interval(self.test_pyjnius, 5)
        print('testing metrics')
        from kivy.metrics import Metrics
        print('dpi is', Metrics.dpi)
        print('density is', Metrics.density)
        print('fontscale is', Metrics.fontscale)
        return root

    def print_something(self, *args):
        print('App print tick', Clock.get_boottime())

    def on_pause(self):
        return True

    def test_pyjnius(self, *args):
        try:
            from jnius import autoclass, cast
        except ImportError:
            raise_error('Could not import pyjnius')
            return
        print('Attempting to vibrate with pyjnius')
        ANDROID_VERSION = autoclass('android.os.Build$VERSION')
        SDK_INT = ANDROID_VERSION.SDK_INT

        Context = autoclass("android.content.Context")
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity

        vibrator_service = activity.getSystemService(Context.VIBRATOR_SERVICE)
        vibrator = cast("android.os.Vibrator", vibrator_service)

        if vibrator and SDK_INT >= 26:
            print("Using android's `VibrationEffect` (SDK >= 26)")
            VibrationEffect = autoclass("android.os.VibrationEffect")
            vibrator.vibrate(
                VibrationEffect.createOneShot(
                    1000, VibrationEffect.DEFAULT_AMPLITUDE,
                ),
            )
        elif vibrator:
            print("Using deprecated android's vibrate (SDK < 26)")
            vibrator.vibrate(1000)
        else:
            print('Something happened...vibrator service disabled?')

    def test_ctypes(self, *args):
        import ctypes


TestApp().run()
