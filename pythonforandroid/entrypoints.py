from pythonforandroid.recommendations import check_python_version
from pythonforandroid.util import BuildInterruptingException, handle_build_exception


def main():
    """
    Main entrypoint for running python-for-android as a script.
    """

    try:
        # Check the Python version before importing anything heavier than
        # the util functions.  This lets us provide a nice message about
        # incompatibility rather than having the interpreter crash if it
        # reaches unsupported syntax from a newer Python version.
        check_python_version()

        from pythonforandroid.toolchain import ToolchainCL
        ToolchainCL()
    except BuildInterruptingException as exc:
        handle_build_exception(exc)
