
import os
import sh
import unittest

from unittest import mock

from pythonforandroid.bootstrap import (
    _cmp_bootstraps_by_priority, Bootstrap, expand_dependencies,
)
from pythonforandroid.distribution import Distribution
from pythonforandroid.recipe import Recipe
from pythonforandroid.archs import ArchARMv7_a
from pythonforandroid.build import Context
from pythonforandroid.util import BuildInterruptingException
from pythonforandroid.androidndk import AndroidNDK

from test_graph import get_fake_recipe


class BaseClassSetupBootstrap(object):
    """
    An class object which is intended to be used as a base class to configure
    an inherited class of `unittest.TestCase`. This class will override the
    `setUp` and `tearDown` methods.
    """

    TEST_ARCH = 'armeabi-v7a'

    def setUp(self):
        Recipe.recipes = {}  # clear Recipe class cache
        self.ctx = Context()
        self.ctx.ndk_api = 21
        self.ctx.android_api = 27
        self.ctx._sdk_dir = "/opt/android/android-sdk"
        self.ctx._ndk_dir = "/opt/android/android-ndk"
        self.ctx.ndk = AndroidNDK(self.ctx._ndk_dir)
        self.ctx.setup_dirs(os.getcwd())
        self.ctx.recipe_build_order = [
            "hostpython3",
            "python3",
            "sdl2",
            "kivy",
        ]

    def setUp_distribution_with_bootstrap(self, bs):
        """
        Extend the setUp by configuring a distribution, because some test
        needs a distribution to be set to be properly tested
        """
        self.ctx.bootstrap = bs
        self.ctx.bootstrap.distribution = Distribution.get_distribution(
            self.ctx, name="test_prj",
            recipes=["python3", "kivy"],
            archs=[self.TEST_ARCH],
        )

    def tearDown(self):
        """
        Extend the `tearDown` by configuring a distribution, because some test
        needs a distribution to be set to be properly tested
        """
        self.ctx.bootstrap = None


class TestBootstrapBasic(BaseClassSetupBootstrap, unittest.TestCase):
    """
    An inherited class of `BaseClassSetupBootstrap` and `unittest.TestCase`
    which will be used to perform tests for the methods/attributes shared
    between all bootstraps which inherits from class
    :class:`~pythonforandroid.bootstrap.Bootstrap`.
    """

    def test_attributes(self):
        """A test which will initialize a bootstrap and will check if the
        values are the expected.
        """
        bs = Bootstrap().get_bootstrap("sdl2", self.ctx)
        self.assertEqual(bs.name, "sdl2")
        self.assertEqual(bs.jni_dir, "sdl2/jni")
        self.assertEqual(bs.get_build_dir_name(), "sdl2")

        # bs.dist_dir should raise an error if there is no distribution to query
        bs.distribution = None
        with self.assertRaises(BuildInterruptingException):
            bs.dist_dir

        # test dist_dir success
        self.setUp_distribution_with_bootstrap(bs)
        expected_folder_name = 'test_prj'
        self.assertTrue(
            bs.dist_dir.endswith(f"dists/{expected_folder_name}"))

    def test_build_dist_dirs(self):
        """A test which will initialize a bootstrap and will check if the
        directories we set has the values that we expect. Here we test methods:

            - :meth:`~pythonforandroid.bootstrap.Bootstrap.get_build_dir`
            - :meth:`~pythonforandroid.bootstrap.Bootstrap.get_dist_dir`
            - :meth:`~pythonforandroid.bootstrap.Bootstrap.get_common_dir`
        """
        bs = Bootstrap.get_bootstrap("sdl2", self.ctx)

        self.assertTrue(
            bs.get_build_dir().endswith("build/bootstrap_builds/sdl2")
        )
        self.assertTrue(bs.get_dist_dir("test_prj").endswith("dists/test_prj"))

    def test__cmp_bootstraps_by_priority(self):
        # Test service_only has higher priority than sdl2:
        # (higher priority = smaller number/comes first)
        self.assertTrue(_cmp_bootstraps_by_priority(
            Bootstrap.get_bootstrap("service_only", self.ctx),
            Bootstrap.get_bootstrap("sdl2", self.ctx)
        ) < 0)

        # Test a random bootstrap is always lower priority than sdl2:
        class _FakeBootstrap(object):
            def __init__(self, name):
                self.name = name
        bs1 = _FakeBootstrap("alpha")
        bs2 = _FakeBootstrap("zeta")
        self.assertTrue(_cmp_bootstraps_by_priority(
            bs1,
            Bootstrap.get_bootstrap("sdl2", self.ctx)
        ) > 0)
        self.assertTrue(_cmp_bootstraps_by_priority(
            bs2,
            Bootstrap.get_bootstrap("sdl2", self.ctx)
        ) > 0)

        # Test bootstraps that aren't otherwise recognized are ranked
        # alphabetically:
        self.assertTrue(_cmp_bootstraps_by_priority(
            bs2,
            bs1,
        ) > 0)
        self.assertTrue(_cmp_bootstraps_by_priority(
            bs1,
            bs2,
        ) < 0)

    def test_all_bootstraps(self):
        """A test which will initialize a bootstrap and will check if the
        method :meth:`~pythonforandroid.bootstrap.Bootstrap.all_bootstraps `
        returns the expected values, which should be: `empty", `service_only`,
        `webview`, `sdl2` and `qt`
        """
        expected_bootstraps = {"empty", "service_only", "service_library", "webview", "sdl2", "qt"}
        set_of_bootstraps = Bootstrap.all_bootstraps()
        self.assertEqual(
            expected_bootstraps, expected_bootstraps & set_of_bootstraps
        )
        self.assertEqual(len(expected_bootstraps), len(set_of_bootstraps))

    def test_expand_dependencies(self):
        # Test dependency expansion of a recipe with no alternatives:
        expanded_result_1 = expand_dependencies(["pysdl2"], self.ctx)
        self.assertTrue(
            {"sdl2", "pysdl2", "python3"} in
            [set(s) for s in expanded_result_1]
        )

        # Test expansion of a single element but as tuple:
        expanded_result_1 = expand_dependencies([("pysdl2",)], self.ctx)
        self.assertTrue(
            {"sdl2", "pysdl2", "python3"} in
            [set(s) for s in expanded_result_1]
        )

        # Test all alternatives are listed (they won't have dependencies
        # expanded since expand_dependencies() is too simplistic):
        expanded_result_2 = expand_dependencies([("pysdl2", "kivy")], self.ctx)
        self.assertEqual([["pysdl2"], ["kivy"]], expanded_result_2)

    def test_expand_dependencies_with_pure_python_package(self):
        """Check that `expanded_dependencies`, with a pure python package as
        one of the dependencies, returns a list of dependencies
        """
        expanded_result = expand_dependencies(
            ["python3", "kivy", "peewee"], self.ctx
        )
        # we expect to one results for python3
        self.assertEqual(len(expanded_result), 1)
        self.assertIsInstance(expanded_result, list)
        for i in expanded_result:
            self.assertIsInstance(i, list)

    def test_get_bootstraps_from_recipes(self):
        """A test which will initialize a bootstrap and will check if the
        method :meth:`~pythonforandroid.bootstrap.Bootstrap.
        get_bootstraps_from_recipes` returns the expected values
        """

        import pythonforandroid.recipe
        original_get_recipe = pythonforandroid.recipe.Recipe.get_recipe

        # Test that SDL2 works with kivy:
        recipes_sdl2 = {"sdl2", "python3", "kivy"}
        bs = Bootstrap.get_bootstrap_from_recipes(recipes_sdl2, self.ctx)
        self.assertEqual(bs.name, "sdl2")

        # Test that pysdl2 or kivy alone will also yield SDL2 (dependency):
        recipes_pysdl2_only = {"pysdl2"}
        bs = Bootstrap.get_bootstrap_from_recipes(
            recipes_pysdl2_only, self.ctx
        )
        self.assertEqual(bs.name, "sdl2")
        recipes_kivy_only = {"kivy"}
        bs = Bootstrap.get_bootstrap_from_recipes(
            recipes_kivy_only, self.ctx
        )
        self.assertEqual(bs.name, "sdl2")

        with mock.patch("pythonforandroid.recipe.Recipe.get_recipe") as \
                mock_get_recipe:
            # Test that something conflicting with sdl2 won't give sdl2:
            def _add_sdl2_conflicting_recipe(name, ctx):
                if name == "conflictswithsdl2":
                    if name not in pythonforandroid.recipe.Recipe.recipes:
                        pythonforandroid.recipe.Recipe.recipes[name] = (
                            get_fake_recipe("sdl2", conflicts=["sdl2"])
                        )
                return original_get_recipe(name, ctx)
            mock_get_recipe.side_effect = _add_sdl2_conflicting_recipe
            recipes_with_sdl2_conflict = {"python3", "conflictswithsdl2"}
            bs = Bootstrap.get_bootstrap_from_recipes(
                recipes_with_sdl2_conflict, self.ctx
            )
            self.assertNotEqual(bs.name, "sdl2")

        # Test using flask will default to webview:
        recipes_with_flask = {"python3", "flask"}
        bs = Bootstrap.get_bootstrap_from_recipes(
            recipes_with_flask, self.ctx
        )
        self.assertEqual(bs.name, "webview")

        # Test using random packages will default to service_only:
        recipes_with_no_sdl2_or_web = {"python3", "numpy"}
        bs = Bootstrap.get_bootstrap_from_recipes(
            recipes_with_no_sdl2_or_web, self.ctx
        )
        self.assertEqual(bs.name, "service_only")

    @mock.patch("pythonforandroid.bootstrap.ensure_dir")
    def test_prepare_dist_dir(self, mock_ensure_dir):
        """A test which will initialize a bootstrap and will check if the
        method :meth:`~pythonforandroid.bootstrap.Bootstrap.prepare_dist_dir`
        successfully calls once the method `endure_dir`
        """
        bs = Bootstrap().get_bootstrap("sdl2", self.ctx)

        bs.prepare_dist_dir()
        mock_ensure_dir.assert_called_once()

    @mock.patch("pythonforandroid.bootstrap.open", create=True)
    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.bootstrap.shutil.copy")
    @mock.patch("pythonforandroid.bootstrap.os.makedirs")
    def test_bootstrap_prepare_build_dir(
        self, mock_os_makedirs, mock_shutil_copy, mock_chdir, mock_open
    ):
        """A test which will initialize a bootstrap and will check if the
        method :meth:`~pythonforandroid.bootstrap.Bootstrap.prepare_build_dir`
        successfully calls the methods that we need to prepare a build dir.
        """

        # prepare bootstrap
        bs = Bootstrap().get_bootstrap("service_only", self.ctx)
        self.ctx.bootstrap = bs

        # test that prepare_build_dir runs (notice that we mock
        # any file/dir creation so we can speed up the tests)
        bs.prepare_build_dir()

        # make sure that the open command has been called only once
        mock_open.assert_called_once_with("project.properties", "w")

        # check that the other mocks we made are actually called
        mock_os_makedirs.assert_called()
        mock_shutil_copy.assert_called()
        mock_chdir.assert_called()

    @mock.patch("pythonforandroid.bootstrap.os.path.isfile")
    @mock.patch("pythonforandroid.bootstrap.os.path.exists")
    @mock.patch("pythonforandroid.bootstrap.os.unlink")
    @mock.patch("pythonforandroid.bootstrap.open", create=True)
    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.bootstrap.listdir")
    def test_bootstrap_prepare_build_dir_with_java_src(
        self,
        mock_listdir,
        mock_chdir,
        mock_open,
        mock_os_unlink,
        mock_os_path_exists,
        mock_os_path_isfile,
    ):
        """A test which will initialize a bootstrap and will check perform
        another test for method
        :meth:`~pythonforandroid.bootstrap.Bootstrap.prepare_build_dir`. In
        here we will simulate that we have `with_java_src` set to some value.
        """
        self.ctx.symlink_bootstrap_files = True
        mock_listdir.return_value = [
            "jnius",
            "kivy",
            "Kivy-1.11.0.dev0-py3.7.egg-info",
            "pyjnius-1.2.1.dev0-py3.7.egg",
        ]

        # prepare bootstrap
        bs = Bootstrap().get_bootstrap("sdl2", self.ctx)
        self.ctx.bootstrap = bs

        # test that prepare_build_dir runs (notice that we mock
        # any file/dir creation so we can speed up the tests)
        bs.prepare_build_dir()
        # make sure that the open command has been called only once
        mock_open.assert_called_with("project.properties", "w")

        # check that the other mocks we made are actually called
        mock_chdir.assert_called()
        mock_os_unlink.assert_called()
        mock_os_path_exists.assert_called()
        mock_os_path_isfile.assert_called()


class GenericBootstrapTest(BaseClassSetupBootstrap):
    """
    An inherited class of `BaseClassSetupBootstrap` which will extends his
    functionality by adding some generic bootstrap tests, so this way we can
    test all our sub modules of :mod:`~pythonforandroid.bootstraps` from within
    this module.

    .. warning:: This is supposed to be used as a base class, so please, don't
                 use this directly.
    """

    @property
    def bootstrap_name(self):
        """Subclasses must have property 'bootstrap_name'. It should be the
        name of the bootstrap to test"""
        raise NotImplementedError("Not implemented in GenericBootstrapTest")

    @mock.patch("pythonforandroid.bootstraps.qt.open", create=True)
    @mock.patch("pythonforandroid.bootstraps.service_only.open", create=True)
    @mock.patch("pythonforandroid.bootstraps.webview.open", create=True)
    @mock.patch("pythonforandroid.bootstraps.sdl2.open", create=True)
    @mock.patch("pythonforandroid.distribution.open", create=True)
    @mock.patch("pythonforandroid.bootstrap.Bootstrap.strip_libraries")
    @mock.patch("pythonforandroid.util.exists")
    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.bootstrap.listdir")
    @mock.patch("pythonforandroid.bootstraps.sdl2.rmdir")
    @mock.patch("pythonforandroid.bootstraps.service_only.rmdir")
    @mock.patch("pythonforandroid.bootstraps.webview.rmdir")
    @mock.patch("pythonforandroid.bootstrap.sh.cp")
    def test_assemble_distribution(
        self,
        mock_sh_cp,
        mock_rmdir1,
        mock_rmdir2,
        mock_rmdir3,
        mock_listdir,
        mock_chdir,
        mock_ensure_dir,
        mock_strip_libraries,
        mock_open_dist_files,
        mock_open_sdl2_files,
        mock_open_webview_files,
        mock_open_service_only_files,
        mock_open_qt_files
    ):
        """
        A test for any overwritten method of
        `~pythonforandroid.bootstrap.Bootstrap.assemble_distribution`. Here we mock
        any file/dir operation that it could slow down our tests, and there is
        a lot to mock, because the `assemble_distribution` method it should take care
        of prepare all compiled files to generate the final `apk`. The targets
        of this test will be:

            - :meth:`~pythonforandroid.bootstraps.sdl2.BootstrapSdl2
              .assemble_distribution`
            - :meth:`~pythonforandroid.bootstraps.service_only
              .ServiceOnlyBootstrap.assemble_distribution`
            - :meth:`~pythonforandroid.bootstraps.webview.WebViewBootstrap
               .assemble_distribution`
            - :meth:`~pythonforandroid.bootstraps.empty.EmptyBootstrap.
              assemble_distribution`

        Here we will tests all those methods that are specific for each class.
        """
        # prepare bootstrap and distribution
        bs = Bootstrap.get_bootstrap(self.bootstrap_name, self.ctx)
        self.assertNotEqual(bs.ctx, None)
        bs.build_dir = bs.get_build_dir()
        self.setUp_distribution_with_bootstrap(bs)

        self.ctx.hostpython = "/some/fake/hostpython3"
        self.ctx.python_recipe = Recipe.get_recipe("python3", self.ctx)
        self.ctx.python_recipe.create_python_bundle = mock.MagicMock()
        self.ctx.python_modules = ["requests"]
        self.ctx.archs = [ArchARMv7_a(self.ctx)]
        self.ctx.bootstrap = bs

        bs.assemble_distribution()

        mock_open_dist_files.assert_called_once_with("dist_info.json", "w")
        mock_open_bootstraps = {
            "sdl2": mock_open_sdl2_files,
            "webview": mock_open_webview_files,
            "service_only": mock_open_service_only_files,
            "qt": mock_open_qt_files
        }
        expected_open_calls = {
            "sdl2": [
                mock.call("local.properties", "w"),
                mock.call("blacklist.txt", "a"),
            ],
            "webview": [mock.call("local.properties", "w")],
            "service_only": [mock.call("local.properties", "w")],
            "qt": [mock.call("local.properties", "w")]
        }
        mock_open_bs = mock_open_bootstraps[self.bootstrap_name]
        # test that the expected calls has been called
        for expected_call in expected_open_calls[self.bootstrap_name]:
            self.assertIn(expected_call, mock_open_bs.call_args_list)
        # test that the write function has been called with the expected args
        self.assertIn(
            mock.call().__enter__().write("sdk.dir=/opt/android/android-sdk"),
            mock_open_bs.mock_calls,
        )
        if self.bootstrap_name == "sdl2":
            self.assertIn(
                mock.call()
                .__enter__()
                .write("\nsqlite3/*\nlib-dynload/_sqlite3.so\n"),
                mock_open_bs.mock_calls,
            )

        # check that the other mocks we made are actually called
        mock_sh_cp.assert_called()
        mock_chdir.assert_called()
        mock_listdir.assert_called()
        mock_strip_libraries.assert_called()
        expected__python_bundle = os.path.join(
            self.ctx.dist_dir,
            self.ctx.bootstrap.distribution.name,
            f"_python_bundle__{self.TEST_ARCH}",
            "_python_bundle",
        )
        self.assertIn(
            mock.call(expected__python_bundle, self.ctx.archs[0]),
            self.ctx.python_recipe.create_python_bundle.call_args_list,
        )

    @mock.patch("pythonforandroid.bootstrap.shprint")
    @mock.patch("pythonforandroid.bootstrap.glob.glob")
    @mock.patch("pythonforandroid.bootstrap.ensure_dir")
    @mock.patch("pythonforandroid.build.ensure_dir")
    def test_distribute_methods(
        self, mock_build_dir, mock_bs_dir, mock_glob, mock_shprint
    ):
        # prepare arch, bootstrap and distribution
        arch = ArchARMv7_a(self.ctx)
        bs = Bootstrap().get_bootstrap(self.bootstrap_name, self.ctx)
        self.setUp_distribution_with_bootstrap(bs)

        # a convenient method to reset mocks in one shot
        def reset_mocks():
            mock_glob.reset_mock()
            mock_shprint.reset_mock()
            mock_build_dir.reset_mock()
            mock_bs_dir.reset_mock()

        # test distribute_libs
        mock_glob.return_value = [
            "/fake_dir/libsqlite3.so",
            "/fake_dir/libpng16.so",
        ]
        bs.distribute_libs(arch, [self.ctx.get_libs_dir(arch.arch)])
        libs_dir = os.path.join("libs", arch.arch)
        # we expect two calls to glob/copy command via shprint
        self.assertEqual(len(mock_glob.call_args_list), 2)
        self.assertEqual(len(mock_shprint.call_args_list), 1)
        self.assertEqual(
            mock_shprint.call_args_list,
            [mock.call(sh.cp, "-a", *mock_glob.return_value, libs_dir)]
        )
        mock_build_dir.assert_called()
        mock_bs_dir.assert_called_once_with(libs_dir)
        reset_mocks()

        # test distribute_javaclasses
        mock_glob.return_value = ["/fakedir/java_file.java"]
        bs.distribute_javaclasses(self.ctx.javaclass_dir)
        mock_glob.assert_called_once_with(self.ctx.javaclass_dir)
        mock_build_dir.assert_called_with(self.ctx.javaclass_dir)
        mock_bs_dir.assert_called_once_with("src")
        self.assertEqual(
            mock_shprint.call_args,
            mock.call(sh.cp, "-a", "/fakedir/java_file.java", "src"),
        )
        reset_mocks()

        # test distribute_aars
        mock_glob.return_value = ["/fakedir/file.aar"]
        bs.distribute_aars(arch)
        mock_build_dir.assert_called_with(self.ctx.aars_dir)
        # We expect three calls to shprint: unzip, cp, cp
        zip_call, kw = mock_shprint.call_args_list[0]
        self.assertEqual(zip_call[0], sh.unzip)
        self.assertEqual(zip_call[2], "/fakedir/file.aar")
        cp_java_call, kw = mock_shprint.call_args_list[1]
        self.assertEqual(cp_java_call[0], sh.cp)
        self.assertTrue(cp_java_call[2].endswith("classes.jar"))
        self.assertEqual(cp_java_call[3], "libs/file.jar")
        cp_libs_call, kw = mock_shprint.call_args_list[2]
        self.assertEqual(cp_libs_call[0], sh.cp)
        self.assertEqual(cp_libs_call[2], "/fakedir/file.aar")
        self.assertEqual(cp_libs_call[3], libs_dir)
        mock_bs_dir.assert_has_calls([mock.call("libs"), mock.call(libs_dir)])
        mock_glob.assert_called()

    @mock.patch("pythonforandroid.bootstrap.shprint")
    @mock.patch("pythonforandroid.bootstrap.sh.Command")
    @mock.patch("pythonforandroid.build.ensure_dir")
    @mock.patch("shutil.which")
    def test_bootstrap_strip(
        self,
        mock_shutil_which,
        mock_ensure_dir,
        mock_sh_command,
        mock_sh_print,
    ):
        mock_shutil_which.return_value = os.path.join(
            self.ctx._ndk_dir,
            f"toolchains/llvm/prebuilt/{self.ctx.ndk.host_tag}/bin/clang",
        )
        # prepare arch, bootstrap, distribution and PythonRecipe
        arch = ArchARMv7_a(self.ctx)
        bs = Bootstrap().get_bootstrap(self.bootstrap_name, self.ctx)
        self.setUp_distribution_with_bootstrap(bs)
        self.ctx.python_recipe = Recipe.get_recipe("python3", self.ctx)

        # test that strip_libraries runs with a fake distribution
        bs.strip_libraries(arch)

        self.assertEqual(
            mock_shutil_which.call_args[0][0],
            mock_shutil_which.return_value,
        )
        mock_sh_command.assert_called_once_with(
            os.path.join(
                self.ctx._ndk_dir,
                f"toolchains/llvm/prebuilt/{self.ctx.ndk.host_tag}/bin",
                "llvm-strip",
            )
        )
        # check that the other mocks we made are actually called
        mock_ensure_dir.assert_called()
        mock_sh_print.assert_called()

    @mock.patch("pythonforandroid.bootstrap.listdir")
    @mock.patch("pythonforandroid.bootstrap.rmdir")
    @mock.patch("pythonforandroid.bootstrap.move")
    @mock.patch("pythonforandroid.bootstrap.isdir")
    def test_bootstrap_fry_eggs(
        self, mock_isdir, mock_move, mock_rmdir, mock_listdir
    ):
        mock_listdir.return_value = [
            "jnius",
            "kivy",
            "Kivy-1.11.0.dev0-py3.7.egg-info",
            "pyjnius-1.2.1.dev0-py3.7.egg",
        ]

        # prepare bootstrap, context and distribution
        bs = Bootstrap().get_bootstrap(self.bootstrap_name, self.ctx)
        self.setUp_distribution_with_bootstrap(bs)

        # test that fry_eggs runs with a fake distribution
        site_packages = os.path.join(
            bs.dist_dir, "_python_bundle", "_python_bundle"
        )
        bs.fry_eggs(site_packages)

        mock_listdir.assert_has_calls(
            [
                mock.call(site_packages),
                mock.call(
                    os.path.join(site_packages, "pyjnius-1.2.1.dev0-py3.7.egg")
                ),
            ]
        )
        self.assertEqual(
            mock_rmdir.call_args[0][0], "pyjnius-1.2.1.dev0-py3.7.egg"
        )
        # check that the other mocks we made are actually called
        mock_isdir.assert_called()
        mock_move.assert_called()


class TestBootstrapSdl2(GenericBootstrapTest, unittest.TestCase):
    """
    An inherited class of `GenericBootstrapTest` and `unittest.TestCase` which
    will be used to perform tests for
    :class:`~pythonforandroid.bootstraps.sdl2.BootstrapSdl2`.
    """

    @property
    def bootstrap_name(self):
        return "sdl2"


class TestBootstrapServiceOnly(GenericBootstrapTest, unittest.TestCase):
    """
    An inherited class of `GenericBootstrapTest` and `unittest.TestCase` which
    will be used to perform tests for
    :class:`~pythonforandroid.bootstraps.service_only.ServiceOnlyBootstrap`.
    """

    @property
    def bootstrap_name(self):
        return "service_only"


class TestBootstrapWebview(GenericBootstrapTest, unittest.TestCase):
    """
    An inherited class of `GenericBootstrapTest` and `unittest.TestCase` which
    will be used to perform tests for
    :class:`~pythonforandroid.bootstraps.webview.WebViewBootstrap`.
    """

    @property
    def bootstrap_name(self):
        return "webview"


class TestBootstrapEmpty(GenericBootstrapTest, unittest.TestCase):
    """
    An inherited class of `GenericBootstrapTest` and `unittest.TestCase` which
    will be used to perform tests for
    :class:`~pythonforandroid.bootstraps.empty.EmptyBootstrap`.

    .. note:: here will test most of the base class methods, because we only
              overwrite :meth:`~pythonforandroid.bootstraps.empty.
              EmptyBootstrap.assemble_distribution`
    """

    @property
    def bootstrap_name(self):
        return "empty"

    def test_assemble_distribution(self, *args):
        # prepare bootstrap
        bs = Bootstrap().get_bootstrap(self.bootstrap_name, self.ctx)
        self.ctx.bootstrap = bs

        # test dist_dir error
        with self.assertRaises(SystemExit) as e:
            bs.assemble_distribution()
        self.assertEqual(e.exception.args[0], 1)


class TestBootstrapQt(GenericBootstrapTest, unittest.TestCase):
    """
    An inherited class of `GenericBootstrapTest` and `unittest.TestCase` which
    will be used to perform tests for
    :class:`~pythonforandroid.bootstraps.qt.BootstrapQt`.
    """

    @property
    def bootstrap_name(self):
        return "qt"
