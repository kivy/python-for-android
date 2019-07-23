import sys
import pytest
import mock
from pythonforandroid.toolchain import ToolchainCL
from pythonforandroid.util import BuildInterruptingException


def patch_sys_argv(argv):
    return mock.patch('sys.argv', argv)


def patch_argparse_print_help():
    return mock.patch('argparse.ArgumentParser.print_help')


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
            '--dist-name=test_toolchain',
        ]
        with patch_sys_argv(argv), mock.patch(
            'pythonforandroid.build.get_available_apis'
        ) as m_get_available_apis, mock.patch(
            'pythonforandroid.build.get_toolchain_versions'
        ) as m_get_toolchain_versions, mock.patch(
            'pythonforandroid.build.get_ndk_platform_dir'
        ) as m_get_ndk_platform_dir, mock.patch(
            'pythonforandroid.build.get_cython_path'
        ) as m_get_cython_path, mock.patch(
            'pythonforandroid.toolchain.build_dist_from_args'
        ) as m_build_dist_from_args:
            m_get_available_apis.return_value = [27]
            m_get_toolchain_versions.return_value = (['4.9'], True)
            m_get_ndk_platform_dir.return_value = (
                '/tmp/android-ndk/platforms/android-21/arch-arm', True)
            ToolchainCL()
        assert m_get_available_apis.call_args_list == [
            mock.call('/tmp/android-sdk')]
        assert m_get_toolchain_versions.call_args_list == [
            mock.call('/tmp/android-ndk', mock.ANY)]
        assert m_get_cython_path.call_args_list == [mock.call()]
        assert m_build_dist_from_args.call_count == 1

    def test_create_no_sdk_dir(self):
        """
        The `--sdk-dir` is mandatory to `create` a distribution.
        """
        argv = ['toolchain.py', 'create']
        with mock.patch('sys.argv', argv), pytest.raises(
            BuildInterruptingException
        ) as ex_info:
            ToolchainCL()
        assert ex_info.value.message == (
            'Android SDK dir was not specified, exiting.')
