import io
import os
import sys
import pytest
from unittest import mock
from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import ToolchainCL
from pythonforandroid.util import BuildInterruptingException


def patch_sys_argv(argv):
    return mock.patch('sys.argv', argv)


def patch_argparse_print_help():
    return mock.patch('argparse.ArgumentParser.print_help')


def patch_sys_stdout():
    return mock.patch('sys.stdout', new_callable=io.StringIO)


def raises_system_exit():
    return pytest.raises(SystemExit)


class TestToolchainCL:

    def test_help(self):
        """
        Calling with `--help` should print help and exit 0.
        """
        argv = ['toolchain.py', '--help', '--storage-dir=/tmp']
        with patch_sys_argv(argv), raises_system_exit(
                ) as ex_info, patch_argparse_print_help() as m_print_help:
            ToolchainCL()
        assert ex_info.value.code == 0
        assert m_print_help.call_args_list == [mock.call()]

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires python3")
    def test_unknown(self):
        """
        Calling with unknown args should print help and exit 1.
        """
        argv = ['toolchain.py', '--unknown']
        with patch_sys_argv(argv), raises_system_exit(
        ) as ex_info, patch_argparse_print_help() as m_print_help:
            ToolchainCL()
        assert ex_info.value.code == 1
        assert m_print_help.call_args_list == [mock.call()]

    def test_create(self):
        """
        Basic `create` distribution test.
        """
        argv = [
            'toolchain.py',
            'create',
            '--sdk-dir=/tmp/android-sdk',
            '--ndk-dir=/tmp/android-ndk',
            '--bootstrap=service_only',
            '--requirements=python3',
            '--dist-name=test_toolchain',
            '--activity-class-name=abc.myapp.android.CustomPythonActivity',
            '--service-class-name=xyz.myapp.android.CustomPythonService',
            '--arch=arm64-v8a',
            '--arch=armeabi-v7a'
        ]
        with patch_sys_argv(argv), mock.patch(
            'pythonforandroid.build.get_available_apis'
        ) as m_get_available_apis, mock.patch(
            'pythonforandroid.toolchain.build_recipes'
        ) as m_build_recipes, mock.patch(
            'pythonforandroid.bootstraps.service_only.'
            'ServiceOnlyBootstrap.assemble_distribution'
        ) as m_run_distribute:
            m_get_available_apis.return_value = [27]
            tchain = ToolchainCL()
            assert tchain.ctx.activity_class_name == 'abc.myapp.android.CustomPythonActivity'
            assert tchain.ctx.service_class_name == 'xyz.myapp.android.CustomPythonService'
        assert m_get_available_apis.call_args_list in [
            [mock.call('/tmp/android-sdk')],  # linux case
            [mock.call('/private/tmp/android-sdk')]  # macos case
        ]
        build_order = [
            'hostpython3', 'libffi', 'openssl', 'sqlite3', 'python3',
            'genericndkbuild', 'setuptools', 'six', 'pyjnius', 'android',
        ]
        python_modules = []
        context = mock.ANY
        project_dir = None
        assert m_build_recipes.call_args_list == [
            mock.call(
                build_order,
                python_modules,
                context,
                project_dir,
                ignore_project_setup_py=False
            )
        ]
        assert m_run_distribute.call_args_list == [mock.call()]

    @mock.patch(
        'pythonforandroid.build.environ',
        # Make sure that no environ variable modifies `sdk_dir`
        {'ANDROIDSDK': None, 'ANDROID_HOME': None})
    def test_create_no_sdk_dir(self):
        """
        The `--sdk-dir` is mandatory to `create` a distribution.
        """
        argv = ['toolchain.py', 'create', '--arch=arm64-v8a', '--arch=armeabi-v7a']
        with patch_sys_argv(argv), pytest.raises(
            BuildInterruptingException
        ) as ex_info:
            ToolchainCL()
        assert ex_info.value.message == (
            'Android SDK dir was not specified, exiting.')

    def test_create_with_complex_requirements(self):
        requirements = [
            'python3==3.8.10',  # direct requirement with recipe using version constraint
            'pandas',           # direct requirement with recipe (no version constraint)
            'mfpymake==1.2.2',  # direct requirement without recipe using version constraint
            'telenium',         # direct requirement without recipe (no version constraint)
            'numpy==1.21.4',    # indirect requirement with recipe using version constraint
            'mako==1.1.5',      # indirect requirement without recipe using version constraint
            # There's no reason to specify an indirect requirement unless we want to install a specific version.
        ]
        argv = [
            'toolchain.py',
            'create',
            '--sdk-dir=/tmp/android-sdk',
            '--ndk-dir=/tmp/android-ndk',
            '--bootstrap=service_only',
            '--requirements={}'.format(','.join(requirements)),
            '--dist-name=test_toolchain',
            '--activity-class-name=abc.myapp.android.CustomPythonActivity',
            '--service-class-name=xyz.myapp.android.CustomPythonService',
            '--arch=arm64-v8a',
            '--arch=armeabi-v7a'
        ]
        with patch_sys_argv(argv), mock.patch(
            'pythonforandroid.build.get_available_apis'
        ) as m_get_available_apis, mock.patch(
            'pythonforandroid.build.get_toolchain_versions'
        ) as m_get_toolchain_versions, mock.patch(
            'pythonforandroid.build.get_ndk_sysroot'
        ) as m_get_ndk_sysroot, mock.patch(
            'pythonforandroid.toolchain.build_recipes'
        ) as m_build_recipes, mock.patch(
            'pythonforandroid.toolchain.__run_pip_compile'
        ) as m_run_pip_compile, mock.patch(
            'pythonforandroid.bootstraps.service_only.'
            'ServiceOnlyBootstrap.assemble_distribution'
        ) as m_run_distribute:
            m_get_available_apis.return_value = [27]
            m_get_toolchain_versions.return_value = (['4.9'], True)

            # pip-compile can give different outputs depending many factors
            # Here we use a sample output generated using python3.8
            m_run_pip_compile.return_value = \
                "#\n" \
                "# This file is autogenerated by pip-compile with python 3.9\n" \
                "# To update, run:\n" \
                "#\n" \
                "#    pip-compile --annotation-style=line\n" \
                "#\n" \
                "certifi==2021.10.8        # via requests\n" \
                "charset-normalizer==2.0.9  # via requests\n" \
                "cheroot==8.5.2            # via cherrypy\n" \
                "cherrypy==18.6.1          # via telenium\n" \
                "idna==3.3                 # via requests\n" \
                "importlib-resources==5.4.0  # via jaraco.text\n" \
                "jaraco.classes==3.2.1     # via jaraco.collections\n" \
                "jaraco.collections==3.4.0  # via cherrypy\n" \
                "jaraco.functools==3.5.0   # via cheroot, jaraco.text, tempora\n" \
                "jaraco.text==3.6.0        # via jaraco.collections\n" \
                "json-rpc==1.13.0          # via telenium\n" \
                "mako==1.1.5               # via -r requirements.in, telenium\n" \
                "markupsafe==2.0.1         # via mako\n" \
                "mfpymake==1.2.2           # via -r requirements.in\n" \
                "more-itertools==8.12.0    # via cheroot, cherrypy, jaraco.classes, jaraco.functools\n" \
                "networkx==2.6.3           # via mfpymake\n" \
                "numpy==1.21.5             # via mfpymake\n" \
                "portend==3.1.0            # via cherrypy\n" \
                "pytz==2021.3              # via tempora\n" \
                "requests==2.26.0          # via mfpymake\n" \
                "six==1.16.0               # via cheroot\n" \
                "telenium==0.5.0           # via -r requirements.in\n" \
                "tempora==4.1.2            # via portend\n" \
                "urllib3==1.26.7           # via requests\n" \
                "werkzeug==2.0.2           # via telenium\n" \
                "ws4py==0.5.1              # via telenium\n" \
                "zc.lockfile==2.0          # via cherrypy\n" \
                "zipp==3.6.0               # via importlib-resources\n" \
                "\n" \
                "# The following packages are considered to be unsafe in a requirements file:\n" \
                "# setuptools\n" \
                "Dry-run, so nothing updated.\n"
            m_get_ndk_sysroot.return_value = (
                join(get_ndk_standalone("/tmp/android-ndk"), "sysroot"),
                True,
            )
            tchain = ToolchainCL()
            assert tchain.ctx.activity_class_name == 'abc.myapp.android.CustomPythonActivity'
            assert tchain.ctx.service_class_name == 'xyz.myapp.android.CustomPythonService'
        assert m_get_available_apis.call_args_list in [
            [mock.call('/tmp/android-sdk')],  # linux case
            [mock.call('/private/tmp/android-sdk')]  # macos case
        ]
        for callargs in m_get_toolchain_versions.call_args_list:
            assert callargs in [
                mock.call("/tmp/android-ndk", mock.ANY),  # linux case
                mock.call("/private/tmp/android-ndk", mock.ANY),  # macos case
            ]
        build_order = [
            'android', 'cython', 'genericndkbuild', 'hostpython3', 'libbz2',
            'libffi', 'liblzma', 'numpy', 'openssl', 'pandas', 'pyjnius',
            'python3', 'pytz', 'setuptools', 'six', 'sqlite3'
        ]
        python_modules = [
            'certifi', 'charset-normalizer', 'cheroot', 'cherrypy',
            'idna', 'importlib-resources', 'jaraco.classes',
            'jaraco.collections', 'jaraco.functools', 'jaraco.text',
            'json-rpc', 'mako', 'markupsafe', 'mfpymake', 'more-itertools',
            'networkx', 'portend', 'python-dateutil', 'requests', 'telenium',
            'tempora', 'urllib3', 'werkzeug', 'ws4py', 'zc.lockfile', 'zipp'
        ]
        context = mock.ANY
        project_dir = None

        # For wtv reason, the build_order and python_modules list elements
        # aren't always generated in the same order.
        m_build_recipes_call_args = mock.call(
            sorted(m_build_recipes.call_args_list[0][0][0]),
            sorted(m_build_recipes.call_args_list[0][0][1]),
            m_build_recipes.call_args_list[0][0][2],
            m_build_recipes.call_args_list[0][0][3],
            ignore_project_setup_py=m_build_recipes.call_args_list[0][1]['ignore_project_setup_py']
        )
        assert m_build_recipes_call_args == mock.call(
            sorted(build_order),
            sorted(python_modules),
            context,
            project_dir,
            ignore_project_setup_py=False
        )
        assert m_run_pip_compile.call_args_list == [mock.call(
            ['mfpymake==1.2.2', 'telenium', 'mako==1.1.5']
        )]
        assert m_run_distribute.call_args_list == [mock.call()]
        assert 'VERSION_python3' in os.environ and os.environ['VERSION_python3'] == '3.8.10'
        assert 'VERSION_mfpymake' in os.environ and os.environ['VERSION_mfpymake'] == '1.2.2'
        assert 'VERSION_numpy' in os.environ and os.environ['VERSION_numpy'] == '1.21.4'
        assert 'VERSION_mako' in os.environ and os.environ['VERSION_mako'] == '1.1.5'

    @pytest.mark.skipif(sys.version_info < (3, 0), reason="requires python3")
    def test_recipes(self):
        """
        Checks the `recipes` command prints out recipes information without crashing.
        """
        argv = ['toolchain.py', 'recipes']
        with patch_sys_argv(argv), patch_sys_stdout() as m_stdout:
            ToolchainCL()
        # check if we have common patterns in the output
        expected_strings = (
            'conflicts:',
            'depends:',
            'kivy',
            'optional depends:',
            'python3',
            'sdl2',
        )
        for expected_string in expected_strings:
            assert expected_string in m_stdout.getvalue()
        # deletes static attribute to not mess with other tests
        del Recipe.recipes

    def test_local_recipes_dir(self):
        """
        Checks the `local_recipes` attribute in the Context is absolute.
        """
        cwd = os.path.realpath(os.getcwd())
        common_args = [
            'toolchain.py',
            'recommendations',
        ]

        # Check the default ./p4a-recipes becomes absolute.
        argv = common_args
        with patch_sys_argv(argv):
            toolchain = ToolchainCL()
        expected_local_recipes = os.path.join(cwd, 'p4a-recipes')
        assert toolchain.ctx.local_recipes == expected_local_recipes

        # Check a supplied relative directory becomes absolute.
        argv = common_args + ['--local-recipes=foo']
        with patch_sys_argv(argv):
            toolchain = ToolchainCL()
        expected_local_recipes = os.path.join(cwd, 'foo')
        assert toolchain.ctx.local_recipes == expected_local_recipes

        # An absolute directory should remain unchanged.
        local_recipes = os.path.join(cwd, 'foo')
        argv = common_args + ['--local-recipes={}'.format(local_recipes)]
        with patch_sys_argv(argv):
            toolchain = ToolchainCL()
        assert toolchain.ctx.local_recipes == local_recipes
