import unittest

from pythonforandroid.recipes.ffmpeg import FFMpegRecipe


class TestFFMpegRecipe(unittest.TestCase):
    """TestCase for recipe :mod:`~pythonforandroid.recipes.ffmpeg`."""

    def test_base_configure_flags(self):
        """
        Hardware acceleration flags are enabled and ``--disable-everything``
        is not passed, so FFmpeg's default components (e.g. MediaCodec
        decoders, HLS demuxer) stay available (issue #3382).
        """
        flags = FFMpegRecipe.get_base_configure_flags()
        self.assertNotIn("--disable-everything", flags)
        self.assertIn("--enable-jni", flags)
        self.assertIn("--enable-mediacodec", flags)
