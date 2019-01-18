import unittest
from mock import patch
from pythonforandroid.archs import ArchARMv7_a
from pythonforandroid.build import Context
from pythonforandroid.recipe import Recipe


class TestGeventRecipe(unittest.TestCase):

    def setUp(self):
        """
        Setups recipe and context.
        """
        self.context = Context()
        self.context.ndk_api = 21
        self.context.android_api = 27
        self.arch = ArchARMv7_a(self.context)
        self.recipe = Recipe.get_recipe('gevent', self.context)

    def test_get_recipe_env(self):
        """
        Makes sure `get_recipe_env()` sets compilation flags properly.
        """
        mocked_cflags = (
            '-DANDROID -fomit-frame-pointer -D__ANDROID_API__=27 -mandroid '
            '-isystem /path/to/isystem '
            '-I/path/to/include1 '
            '-isysroot /path/to/sysroot '
            '-I/path/to/include2 '
            '-march=armv7-a -mfloat-abi=softfp -mfpu=vfp -mthumb '
            '-I/path/to/python3-libffi-openssl/include'
        )
        mocked_ldflags = (
            ' --sysroot /path/to/sysroot '
            '-lm '
            '-L/path/to/library1 '
            '-L/path/to/library2 '
            '-lpython3.7m '
            # checks the regex doesn't parse `python3-libffi-openssl` as a `-libffi`
            '-L/path/to/python3-libffi-openssl/library3 '
        )
        mocked_env = {
            'CFLAGS': mocked_cflags,
            'LDFLAGS': mocked_ldflags,
        }
        with patch('pythonforandroid.recipe.CythonRecipe.get_recipe_env') as m_get_recipe_env:
            m_get_recipe_env.return_value = mocked_env
            env = self.recipe.get_recipe_env()
        expected_cflags = (
            ' -fomit-frame-pointer -mandroid -isystem /path/to/isystem'
            ' -isysroot /path/to/sysroot'
            ' -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -mthumb'
        )
        expected_cppflags = (
            '-DANDROID -D__ANDROID_API__=27 '
            '-I/path/to/include1 '
            '-I/path/to/include2 '
            '-I/path/to/python3-libffi-openssl/include'
        )
        expected_ldflags = (
            ' --sysroot /path/to/sysroot'
            ' -L/path/to/library1'
            ' -L/path/to/library2'
            ' -L/path/to/python3-libffi-openssl/library3 '
        )
        expected_libs = '-lm -lpython3.7m'
        expected_env = {
            'CFLAGS': expected_cflags,
            'CPPFLAGS': expected_cppflags,
            'LDFLAGS': expected_ldflags,
            'LIBS': expected_libs,
        }
        self.assertEqual(expected_env, env)
