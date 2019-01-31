
from main import PythonTestMixIn
from unittest import TestCase


class NumpyTestCase(PythonTestMixIn, TestCase):
    module_import = 'numpy'

    def test_run_module(self):
        import numpy as np

        arr = np.random.random((3, 3))
        det = np.linalg.det(arr)


class OpensslTestCase(PythonTestMixIn, TestCase):
    module_import = '_ssl'

    def test_run_module(self):
        import ssl

        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.options &= ~ssl.OP_NO_SSLv3
        

class SqliteTestCase(PythonTestMixIn, TestCase):
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
