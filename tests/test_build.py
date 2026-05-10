import os
import unittest
from unittest import mock

import jinja2

from pythonforandroid.build import (
    Context, RECOMMENDED_TARGET_API, run_pymodules_install, process_python_modules, is_wheel_compatible
)
from pythonforandroid.archs import ArchARMv7_a, ArchAarch_64


class TestBuildBasic(unittest.TestCase):

    def test_run_pymodules_install_optional_project_dir(self):
        """
        Makes sure the `run_pymodules_install()` doesn't crash when the
        `project_dir` optional parameter is None, refs #1898
        """
        ctx = mock.Mock(recipe_build_order=[])
        ctx.archs = [ArchARMv7_a(ctx), ArchAarch_64(ctx)]
        modules = []
        project_dir = None
        with mock.patch('pythonforandroid.build.info') as m_info:
            assert run_pymodules_install(ctx, ctx.archs[0], modules, project_dir) is None
        assert m_info.call_args_list[-1] == mock.call(
            'No Python modules and no setup.py to process, skipping')

    def test_python_module_parser(self):
        ctx = mock.Mock(recipe_build_order=[])
        ctx.archs = [ArchARMv7_a(ctx), ArchAarch_64(ctx)]
        ctx.extra_index_urls = []
        ctx.ndk_api = 24
        arch = ctx.archs[0]

        # should not alter original module name (like with adding version number)
        assert "kivy_garden.frostedglass" in process_python_modules(ctx, ["kivy_garden.frostedglass"], arch)

        # should skip urls and other unsupported format
        modules = ["https://example.com/some.zip", "git+https://github.com/kivy/python-for-android@develop"]
        result = process_python_modules(ctx, modules, arch)
        assert modules == result

    def test_is_wheel_compatible(self):
        ctx = mock.Mock(recipe_build_order=[])
        ctx.archs = [ArchARMv7_a(ctx), ArchAarch_64(ctx)]
        ctx.ndk_api = 24
        arch = ctx.archs[0]

        assert is_wheel_compatible("test-7.1.0-0-cp314-cp314-android_24_aarch64.whl", ctx.archs[1], ctx)
        assert is_wheel_compatible("test-7.1.0-0-cp314-cp314-android_24_arm.whl", ctx.archs[0], ctx)
        assert is_wheel_compatible("certifi-2026.1.4-py3-none-any.whl", arch, ctx)

        # arches are diff
        assert not is_wheel_compatible("test-7.1.0-0-cp314-cp314-android_24_aarch64.whl", ctx.archs[0], ctx)

        # other os
        assert not is_wheel_compatible("test-7.1.0-0-cp313-cp313-some_other_os.whl", arch, ctx)
        assert not is_wheel_compatible("mmh3-5.2.0-cp314-cp314t-win_amd64.whl", arch, ctx)

    def test_strip_if_with_debug_symbols(self):
        ctx = mock.Mock(recipe_build_order=[])
        ctx.python_recipe.major_minor_version_string = "3.6"
        ctx.get_site_packages_dir.return_value = "test-doesntexist"
        ctx.build_dir = "nonexistant_directory"
        ctx.extra_index_urls = []
        ctx.archs = [ArchAarch_64(ctx)]

        modules = ["mymodule"]
        project_dir = None
        with mock.patch('pythonforandroid.build.info'), \
                mock.patch('sh.Command'), \
                mock.patch('pythonforandroid.build.open'), \
                mock.patch('pythonforandroid.build.shprint'), \
                mock.patch('pythonforandroid.build.current_directory'), \
                mock.patch('pythonforandroid.build.CythonRecipe') as m_CythonRecipe, \
                mock.patch('pythonforandroid.build.project_has_setup_py') as m_project_has_setup_py, \
                mock.patch('pythonforandroid.build.run_setuppy_install'):
            m_project_has_setup_py.return_value = False

            # Make sure it is NOT called when `with_debug_symbols` is true:
            ctx.with_debug_symbols = True
            assert run_pymodules_install(ctx, ctx.archs[0], modules, project_dir) is None
            assert m_CythonRecipe().strip_object_files.called is False

            # Make sure strip object files IS called when
            # `with_debug_symbols` is false:
            ctx.with_debug_symbols = False
            assert run_pymodules_install(ctx, ctx.archs[0], modules, project_dir) is None
            assert m_CythonRecipe().strip_object_files.called is True


class TestTemplates(unittest.TestCase):

    def test_android_manifest_xml(self):
        args = mock.Mock()
        args.min_sdk_version = 12
        args.build_mode = 'debug'
        args.native_services = ['abcd', ]
        args.permissions = [
            dict(name="android.permission.INTERNET"),
            dict(name="android.permission.WRITE_EXTERNAL_STORAGE", maxSdkVersion=18),
            dict(name="android.permission.BLUETOOTH_SCAN", usesPermissionFlags="neverForLocation")]
        args.add_activity = []
        args.android_used_libs = []
        args.meta_data = []
        args.extra_manifest_xml = '<tag-a><tag-b></tag-b></tag-a>'
        args.extra_manifest_application_arguments = 'android:someParameter="true" android:anotherParameter="false"'
        render_args = {
            "args": args,
            "service": False,
            "service_names": [],
            "android_api": 1234,
            "debug": "debug" in args.build_mode,
            "native_services": args.native_services
        }
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader('pythonforandroid/bootstraps/_sdl_common/build/templates/')
        )
        template = environment.get_template('AndroidManifest.tmpl.xml')
        xml = template.render(**render_args)
        assert xml.count('android:minSdkVersion="12"') == 1
        assert xml.count('android:anotherParameter="false"') == 1
        assert xml.count('android:someParameter="true"') == 1
        assert xml.count('<tag-a><tag-b></tag-b></tag-a>') == 1
        assert xml.count('android:process=":service_') == 0
        assert xml.count('targetSdkVersion="1234"') == 1
        assert xml.count('android:debuggable="true"') == 1
        assert xml.count('<service android:name="abcd" />') == 1
        assert xml.count('<uses-permission android:name="android.permission.INTERNET" />') == 1
        assert xml.count('<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="18" />') == 1
        assert xml.count('<uses-permission android:name="android.permission.BLUETOOTH_SCAN" android:usesPermissionFlags="neverForLocation" />') == 1
        # TODO: potentially some other checks to be added here to cover other "logic" (flags and loops) in the template


class TestContext(unittest.TestCase):

    @mock.patch.dict('pythonforandroid.build.Context.env')
    @mock.patch('pythonforandroid.build.get_available_apis')
    @mock.patch('pythonforandroid.build.ensure_dir')
    def test_sdk_ndk_paths(
            self,
            mock_ensure_dir,
            mock_get_available_apis,
    ):
        mock_get_available_apis.return_value = [RECOMMENDED_TARGET_API]
        context = Context()
        context.setup_dirs(os.getcwd())
        context.prepare_build_environment(
            user_sdk_dir='sdk',
            user_ndk_dir='ndk',
            user_android_api=None,
            user_ndk_api=None,
        )

        # The context was supplied with relative SDK and NDK dirs. Check
        # that it resolved them to absolute paths.
        real_sdk_dir = os.path.join(os.getcwd(), 'sdk')
        real_ndk_dir = os.path.join(os.getcwd(), 'ndk')
        assert context.sdk_dir == real_sdk_dir
        assert context.ndk_dir == real_ndk_dir

        context_paths = context.env['PATH'].split(':')
        assert context_paths[0:3] == [
            f'{real_ndk_dir}/toolchains/llvm/prebuilt/{context.ndk.host_tag}/bin',
            real_ndk_dir,
            f'{real_sdk_dir}/tools'
        ]
