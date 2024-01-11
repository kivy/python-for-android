
from unittest import TestCase
from .mixin import PythonTestMixIn


class NumpyTestCase(PythonTestMixIn, TestCase):
    module_import = 'numpy'

    def test_run_module(self):
        import numpy as np

        arr = np.random.random((3, 3))
        det = np.linalg.det(arr)

class ScipyTestCase(PythonTestMixIn, TestCase):
    module_import = 'scipy'

    def test_run_module(self):
        import numpy as np
        from scipy.cluster.vq import vq, kmeans, whiten
        features  = np.array([[ 1.9,2.3],
                        [ 1.5,2.5],
                        [ 0.8,0.6],
                        [ 0.4,1.8],
                        [ 0.1,0.1],
                        [ 0.2,1.8],
                        [ 2.0,0.5],
                        [ 0.3,1.5],
                        [ 1.0,1.0]])
        whitened = whiten(features)
        book = np.array((whitened[0],whitened[2]))
        print('kmeans', kmeans(whitened,book))


class OpensslTestCase(PythonTestMixIn, TestCase):
    module_import = '_ssl'

    def test_run_module(self):
        import ssl

        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.options &= ~ssl.OP_NO_SSLv3


class Sqlite3TestCase(PythonTestMixIn, TestCase):
    module_import = 'sqlite3'

    def test_run_module(self):
        import sqlite3

        conn = sqlite3.connect('example.db')
        conn.cursor()


class KivyTestCase(PythonTestMixIn, TestCase):
    module_import = 'kivy'

    def test_run_module(self):
        # This import has side effects, if it works then it's an
        # indication that Kivy is okay
        from kivy.core.window import Window


class PyjniusTestCase(PythonTestMixIn, TestCase):
    module_import = 'jnius'

    def test_run_module(self):
        from jnius import autoclass

        autoclass('org.kivy.android.PythonActivity')


class LibffiTestCase(PythonTestMixIn, TestCase):
    module_import = 'ctypes'

    def test_run_module(self):
        from os import environ
        from ctypes import cdll

        if "ANDROID_APP_PATH" in environ:
            libc = cdll.LoadLibrary("libc.so")
        else:
            from ctypes.util import find_library
            path_libc = find_library("c")
            libc = cdll.LoadLibrary(path_libc)
        libc.printf(b"%s\n", b"Using the C printf function from Python ... ")


class RequestsTestCase(PythonTestMixIn, TestCase):
    module_import = 'requests'

    def test_run_module(self):
        import requests

        requests.get('https://kivy.org/')


class PillowTestCase(PythonTestMixIn, TestCase):
    module_import = 'PIL'

    def test_run_module(self):
        import os
        from PIL import (
            Image as PilImage,
            ImageOps,
            ImageFont,
            ImageDraw,
            ImageFilter,
            ImageChops,
        )

        text_to_draw = "Kivy"
        img_target = "pillow_text_draw.png"
        image_width = 200
        image_height = 100

        img = PilImage.open("static/colours.png")
        img = img.resize((image_width, image_height), PilImage.ANTIALIAS)
        font = ImageFont.truetype("static/Blanka-Regular.otf", 55)

        draw = ImageDraw.Draw(img)
        for n in range(2, image_width, 2):
            draw.rectangle(
                (n, n, image_width - n, image_height - n), outline="black"
            )
        img.filter(ImageFilter.GaussianBlur(radius=1.5))

        text_pos = (image_width / 2.0 - 55, 5)
        halo = PilImage.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(halo).text(
            text_pos, text_to_draw, font=font, fill="black"
        )
        blurred_halo = halo.filter(ImageFilter.BLUR)
        ImageDraw.Draw(blurred_halo).text(
            text_pos, text_to_draw, font=font, fill="white"
        )
        img = PilImage.composite(
            img, blurred_halo, ImageChops.invert(blurred_halo)
        )

        img.save(img_target, "PNG")
        self.assertTrue(os.path.isfile(img_target))


class MatplotlibTestCase(PythonTestMixIn, TestCase):
    module_import = 'matplotlib'

    def test_run_module(self):
        import os
        import numpy as np
        from matplotlib import pyplot as plt

        fig, ax = plt.subplots()
        ax.set_xlabel('test xlabel')
        ax.set_ylabel('test ylabel')
        ax.plot(np.random.random(50))
        ax.plot(np.sin(np.linspace(0, 3 * np.pi, 30)))

        ax.legend(['random numbers', 'sin'])

        fig.set_size_inches((5, 4))
        fig.tight_layout()

        fig.savefig('matplotlib_test.png', dpi=150)
        self.assertTrue(os.path.isfile("matplotlib_test.png"))


class CryptographyTestCase(PythonTestMixIn, TestCase):
    module_import = 'cryptography'

    def test_run_module(self):
        from cryptography.fernet import Fernet

        key = Fernet.generate_key()
        f = Fernet(key)
        cryptography_encrypted = f.encrypt(
            b'A really secret message. Not for prying eyes.')
        cryptography_decrypted = f.decrypt(cryptography_encrypted)


class PycryptoTestCase(PythonTestMixIn, TestCase):
    module_import = 'Crypto'

    def test_run_module(self):
        from Crypto.Hash import SHA256

        crypto_hash_message = 'A secret message'
        hash = SHA256.new()
        hash.update(crypto_hash_message)
        crypto_hash_hexdigest = hash.hexdigest()


class PycryptodomeTestCase(PythonTestMixIn, TestCase):
    module_import = 'Crypto'

    def test_run_module(self):
        import os
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
            'ok' if os.path.exists("rsa_key.bin") else 'fail'))
        self.assertTrue(os.path.exists("rsa_key.bin"))

        print('\t -> Testing Public key:'.format(key.publickey().export_key()))


class ScryptTestCase(PythonTestMixIn, TestCase):
    module_import = 'scrypt'

    def test_run_module(self):
        import scrypt
        h1 = scrypt.hash('password', 'random salt')
        # The hash should be 64 bytes (default value)
        self.assertEqual(64, len(h1))


class M2CryptoTestCase(PythonTestMixIn, TestCase):
    module_import = 'M2Crypto'

    def test_run_module(self):
        from M2Crypto import SSL
        ctx = SSL.Context('sslv23')


class Pysha3TestCase(PythonTestMixIn, TestCase):
    module_import = 'sha3'

    def test_run_module(self):
        import sha3

        print('Ok imported pysha3, testing some basic operations...')
        k = sha3.keccak_512()
        k.update(b"data")
        print('Test pysha3 operation (keccak_512): {}'.format(k.hexdigest()))


class LibtorrentTestCase(PythonTestMixIn, TestCase):
    module_import = 'libtorrent'

    def test_run_module(self):
        import libtorrent as lt

        print('Imported libtorrent version {}'.format(lt.version))


class Pyside6TestCase(PythonTestMixIn, TestCase):
    module_import = 'PySide6'

    def test_run_module(self):
        import PySide6
        from PySide6.QtCore import QDateTime
        from PySide6 import QtWidgets

        print(f"Imported PySide6 version {PySide6.__version__}")
        print(f"Current date and time obtained from PySide6 : {QDateTime.currentDateTime().toString()}")


class Shiboken6TestCase(PythonTestMixIn, TestCase):
    module_import = 'shiboken6'

    def test_run_module(self):
        import shiboken6
        from shiboken6 import Shiboken

        print('Imported shiboken6 version {}'.format(shiboken6.__version__))
