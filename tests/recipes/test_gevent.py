import unittest
from unittest.mock import patch
from tests.recipes.recipe_ctx import RecipeCtx


class TestGeventRecipe(RecipeCtx, unittest.TestCase):

    recipe_name = "gevent"

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
        mocked_ldlibs = ' -lm'
        mocked_env = {
            'CFLAGS': mocked_cflags,
            'LDFLAGS': mocked_ldflags,
            'LDLIBS': mocked_ldlibs,
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
        expected_ldlibs = mocked_ldlibs
        expected_libs = '-lm -lpython3.7m -lm'
        expected_env = {
            'CFLAGS': expected_cflags,
            'CPPFLAGS': expected_cppflags,
            'LDFLAGS': expected_ldflags,
            'LDLIBS': expected_ldlibs,
            'LIBS': expected_libs,
        }
        self.assertEqual(expected_env, env)
