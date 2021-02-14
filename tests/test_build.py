import unittest
from unittest import mock

import jinja2

from pythonforandroid.build import run_pymodules_install


class TestBuildBasic(unittest.TestCase):

    def test_run_pymodules_install_optional_project_dir(self):
        """
        Makes sure the `run_pymodules_install()` doesn't crash when the
        `project_dir` optional parameter is None, refs #1898
        """
        ctx = mock.Mock()
        modules = []
        project_dir = None
        with mock.patch('pythonforandroid.build.info') as m_info:
            assert run_pymodules_install(ctx, modules, project_dir) is None
        assert m_info.call_args_list[-1] == mock.call(
            'No Python modules and no setup.py to process, skipping')

    def test_strip_if_with_debug_symbols(self):
        ctx = mock.Mock()
        ctx.python_recipe.major_minor_version_string = "python3.6"
        ctx.get_site_packages_dir.return_value = "test-doesntexist"
        ctx.build_dir = "nonexistant_directory"
        ctx.archs = ["arm64"]

        modules = ["mymodule"]
        project_dir = None
        with mock.patch('pythonforandroid.build.info'), \
                mock.patch('sh.Command'),\
                mock.patch('pythonforandroid.build.open'),\
                mock.patch('pythonforandroid.build.shprint'),\
                mock.patch('pythonforandroid.build.current_directory'),\
                mock.patch('pythonforandroid.build.CythonRecipe') as m_CythonRecipe, \
                mock.patch('pythonforandroid.build.project_has_setup_py') as m_project_has_setup_py, \
                mock.patch('pythonforandroid.build.run_setuppy_install'):
            m_project_has_setup_py.return_value = False

            # Make sure it is NOT called when `with_debug_symbols` is true:
            ctx.with_debug_symbols = True
            assert run_pymodules_install(ctx, modules, project_dir) is None
            assert m_CythonRecipe().strip_object_files.called is False

            # Make sure strip object files IS called when
            # `with_debug_symbols` is fasle:
            ctx.with_debug_symbols = False
            assert run_pymodules_install(ctx, modules, project_dir) is None
            assert m_CythonRecipe().strip_object_files.called is True


class TestTemplates(unittest.TestCase):

    def test_android_manifest_xml(self):
        args = mock.Mock()
        args.min_sdk_version = 12
        args.build_mode = 'debug'
        args.native_services = ['abcd', ]
        args.permissions = []
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
            loader=jinja2.FileSystemLoader('pythonforandroid/bootstraps/sdl2/build/templates/')
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
        # TODO: potentially some other checks to be added here to cover other "logic" (flags and loops) in the template
