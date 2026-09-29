import unittest

from pythonforandroid.recipes.ffmpeg import FFMpegRecipe


class TestFFMpegRecipe(unittest.TestCase):
    """TestCase for recipe :mod:`~pythonforandroid.recipes.ffmpeg`."""

    def test_base_configure_flags_keep_disable_everything(self):
        """
        Hardware acceleration flags must append to ``--disable-everything``,
        not replace it (issue #3382).
        """
        flags = FFMpegRecipe.get_base_configure_flags()
        self.assertEqual(flags[0], "--disable-everything")
        self.assertIn("--enable-jni", flags)
        self.assertIn("--enable-mediacodec", flags)
