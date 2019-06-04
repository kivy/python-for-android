import os

import unittest

try:
    from unittest import mock
except ImportError:
    # `Python 2` or lower than `Python 3.3` does not
    # have the `unittest.mock` module built-in
    import mock
from pythonforandroid.bootstrap import Bootstrap
from pythonforandroid.distribution import Distribution
from pythonforandroid.recipe import Recipe
from pythonforandroid.build import Context
from pythonforandroid.util import BuildInterruptingException
from pythonforandroid.archs import (
    Arch,
    ArchARM,
    ArchARMv7_a,
    ArchAarch_64,
    Archx86,
    Archx86_64,
)

expected_env_gcc_keys = {
    "CFLAGS",
    "LDFLAGS",
    "CXXFLAGS",
    "TOOLCHAIN_PREFIX",
    "TOOLCHAIN_VERSION",
    "CC",
    "CXX",
    "AR",
    "RANLIB",
    "LD",
    "LDSHARED",
    "STRIP",
    "MAKE",
    "READELF",
    "NM",
    "BUILDLIB_PATH",
    "PATH",
    "ARCH",
    "NDK_API",
}


class ArchSetUpBaseClass(object):
    ctx = None

    def setUp(self):
        self.ctx = Context()
        self.ctx.ndk_api = 21
        self.ctx.android_api = 27
        self.ctx._sdk_dir = "/opt/android/android-sdk"
        self.ctx._ndk_dir = "/opt/android/android-ndk"
        self.ctx.setup_dirs(os.getcwd())
        self.ctx.bootstrap = Bootstrap().get_bootstrap("sdl2", self.ctx)
        self.ctx.bootstrap.distribution = Distribution.get_distribution(
            self.ctx, name="sdl2", recipes=["python3", "kivy"]
        )
        self.ctx.python_recipe = Recipe.get_recipe("python3", self.ctx)


class TestArch(ArchSetUpBaseClass, unittest.TestCase):
    def test_arch(self):
        arch = Arch(self.ctx)
        with self.assertRaises(AttributeError) as e1:
            arch.__str__()
        self.assertEqual(
            e1.exception.args[0], "'Arch' object has no attribute 'arch'"
        )
        with self.assertRaises(AttributeError) as e2:
            getattr(arch, "target")
        self.assertEqual(
            e2.exception.args[0], "'NoneType' object has no attribute 'split'"
        )
        self.assertIsNone(arch.toolchain_prefix)
        self.assertIsNone(arch.command_prefix)
        self.assertIsInstance(arch.include_dirs, list)


class TestArchARM(ArchSetUpBaseClass, unittest.TestCase):
    # Here we mock two functions:
    # - `ensure_dir` because we don't want to create any directory
    # - `find_executable` because otherwise we will
    #   get an error when trying to find the compiler (we are setting some fake
    #   paths for our android sdk and ndk so probably will not exist)
    @mock.patch("pythonforandroid.archs.find_executable")
    @mock.patch("pythonforandroid.build.ensure_dir")
    def test_arch_arm(self, mock_ensure_dir, mock_find_executable):
        mock_find_executable.return_value = "arm-linux-androideabi-gcc"
        mock_ensure_dir.return_value = True

        arch = ArchARM(self.ctx)
        self.assertEqual(arch.arch, "armeabi")
        self.assertEqual(arch.__str__(), "armeabi")
        self.assertEqual(arch.toolchain_prefix, "arm-linux-androideabi")
        self.assertEqual(arch.command_prefix, "arm-linux-androideabi")
        self.assertEqual(arch.target, "armv7a-none-linux-androideabi")
        self.assertEqual(arch.platform_dir, "arch-arm")
        arch = ArchARM(self.ctx)

        # Check environment flags
        env = arch.get_env()
        self.assertIsInstance(env, dict)
        self.assertEqual(
            expected_env_gcc_keys, set(env.keys()) & expected_env_gcc_keys
        )

        # check gcc compilers
        self.assertEqual(env["CC"].split()[0], "arm-linux-androideabi-gcc")
        self.assertEqual(env["CXX"].split()[0], "arm-linux-androideabi-g++")
        # check android binaries
        self.assertEqual(env["AR"], "arm-linux-androideabi-ar")
        self.assertEqual(env["LD"], "arm-linux-androideabi-ld")
        self.assertEqual(env["RANLIB"], "arm-linux-androideabi-ranlib")
        self.assertEqual(
            env["STRIP"].split()[0], "arm-linux-androideabi-strip"
        )
        self.assertEqual(
            env["READELF"].split()[0], "arm-linux-androideabi-readelf"
        )
        self.assertEqual(env["NM"].split()[0], "arm-linux-androideabi-nm")

        # check that cflags are in gcc
        self.assertIn(env["CFLAGS"], env["CC"])

        # check that flags aren't in gcc and also check ccache
        self.ctx.ccache = "/usr/bin/ccache"
        env = arch.get_env(with_flags_in_cc=False)
        self.assertNotIn(env["CFLAGS"], env["CC"])
        self.assertEqual(env["USE_CCACHE"], "1")
        self.assertEqual(env["NDK_CCACHE"], "/usr/bin/ccache")

        # Check exception in case that CC is not found
        mock_find_executable.return_value = None
        with self.assertRaises(BuildInterruptingException) as e:
            arch.get_env()
        self.assertEqual(
            e.exception.args[0],
            "Couldn't find executable for CC. This indicates a problem "
            "locating the arm-linux-androideabi-gcc executable in the Android "
            "NDK, not that you don't have a normal compiler installed. "
            "Exiting.",
        )


class TestArchARMv7a(ArchSetUpBaseClass, unittest.TestCase):
    # Here we mock the same functions than the previous tests plus `glob`,
    # so we make sure that the glob result is the expected even if the folder
    # doesn't exist, which is probably the case. This has to be done because
    # here we tests the `get_env` with clang
    @mock.patch("pythonforandroid.archs.glob")
    @mock.patch("pythonforandroid.archs.find_executable")
    @mock.patch("pythonforandroid.build.ensure_dir")
    def test_arch_armv7a(
        self, mock_ensure_dir, mock_find_executable, mock_glob
    ):
        mock_find_executable.return_value = "arm-linux-androideabi-gcc"
        mock_ensure_dir.return_value = True
        mock_glob.return_value = ["llvm"]

        arch = ArchARMv7_a(self.ctx)
        self.assertEqual(arch.arch, "armeabi-v7a")
        self.assertEqual(arch.__str__(), "armeabi-v7a")
        self.assertEqual(arch.toolchain_prefix, "arm-linux-androideabi")
        self.assertEqual(arch.command_prefix, "arm-linux-androideabi")
        self.assertEqual(arch.target, "armv7a-none-linux-androideabi")
        self.assertEqual(arch.platform_dir, "arch-arm")

        env = arch.get_env(clang=True)
        # check clang
        build_platform = "{system}-{machine}".format(
            system=os.uname()[0], machine=os.uname()[-1]
        ).lower()
        self.assertEqual(
            env["CC"].split()[0],
            "{ndk_dir}/toolchains/llvm/prebuilt/"
            "{build_platform}/bin/clang".format(
                ndk_dir=self.ctx._ndk_dir, build_platform=build_platform
            ),
        )
        self.assertEqual(
            env["CXX"].split()[0],
            "{ndk_dir}/toolchains/llvm/prebuilt/"
            "{build_platform}/bin/clang++".format(
                ndk_dir=self.ctx._ndk_dir, build_platform=build_platform
            ),
        )

        # For armeabi-v7a we expect some extra cflags
        self.assertIn(
            " -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -mthumb",
            env["CFLAGS"],
        )


class TestArchX86(ArchSetUpBaseClass, unittest.TestCase):
    @mock.patch("pythonforandroid.archs.find_executable")
    @mock.patch("pythonforandroid.build.ensure_dir")
    def test_arch_x86(self, mock_ensure_dir, mock_find_executable):
        mock_find_executable.return_value = "arm-linux-androideabi-gcc"
        mock_ensure_dir.return_value = True

        arch = Archx86(self.ctx)
        self.assertEqual(arch.arch, "x86")
        self.assertEqual(arch.__str__(), "x86")
        self.assertEqual(arch.toolchain_prefix, "x86")
        self.assertEqual(arch.command_prefix, "i686-linux-android")
        self.assertEqual(arch.target, "i686-none-linux-android")
        self.assertEqual(arch.platform_dir, "arch-x86")

        # For x86 we expect some extra cflags in our `environment`
        env = arch.get_env()
        self.assertIn(
            " -march=i686 -mtune=intel -mssse3 -mfpmath=sse -m32",
            env["CFLAGS"],
        )


class TestArchX86_64(ArchSetUpBaseClass, unittest.TestCase):
    @mock.patch("pythonforandroid.archs.find_executable")
    @mock.patch("pythonforandroid.build.ensure_dir")
    def test_arch_x86_64(self, mock_ensure_dir, mock_find_executable):
        mock_find_executable.return_value = "arm-linux-androideabi-gcc"
        mock_ensure_dir.return_value = True

        arch = Archx86_64(self.ctx)
        self.assertEqual(arch.arch, "x86_64")
        self.assertEqual(arch.__str__(), "x86_64")
        self.assertEqual(arch.toolchain_prefix, "x86_64")
        self.assertEqual(arch.command_prefix, "x86_64-linux-android")
        self.assertEqual(arch.target, "x86_64-none-linux-android")
        self.assertEqual(arch.platform_dir, "arch-x86_64")

        # For x86_64 we expect some extra cflags in our `environment`
        env = arch.get_env()
        self.assertIn(
            " -march=x86-64 -msse4.2 -mpopcnt -m64 -mtune=intel", env["CFLAGS"]
        )


class TestArchAArch64(ArchSetUpBaseClass, unittest.TestCase):
    @mock.patch("pythonforandroid.archs.find_executable")
    @mock.patch("pythonforandroid.build.ensure_dir")
    def test_arch_aarch_64(self, mock_ensure_dir, mock_find_executable):
        mock_find_executable.return_value = "arm-linux-androideabi-gcc"
        mock_ensure_dir.return_value = True

        arch = ArchAarch_64(self.ctx)
        self.assertEqual(arch.arch, "arm64-v8a")
        self.assertEqual(arch.__str__(), "arm64-v8a")
        self.assertEqual(arch.toolchain_prefix, "aarch64-linux-android")
        self.assertEqual(arch.command_prefix, "aarch64-linux-android")
        self.assertEqual(arch.target, "aarch64-none-linux-android")
        self.assertEqual(arch.platform_dir, "arch-arm64")

        # For x86_64 we expect to find an extra key in`environment`
        env = arch.get_env()
        self.assertIn("EXTRA_CFLAGS", env.keys())
