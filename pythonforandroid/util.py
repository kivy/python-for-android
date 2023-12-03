import contextlib
from fnmatch import fnmatch
import logging
from os.path import exists, join
from os import getcwd, chdir, makedirs, walk
from pathlib import Path
from platform import uname
import shutil
from tempfile import mkdtemp

import packaging.version

from pythonforandroid.logger import (logger, Err_Fore, error, info)

LOGGER = logging.getLogger("p4a.util")

build_platform = "{system}-{machine}".format(
    system=uname().system, machine=uname().machine
).lower()
"""the build platform in the format `system-machine`. We use
this string to define the right build system when compiling some recipes or
to get the right path for clang compiler"""


@contextlib.contextmanager
def current_directory(new_dir):
    cur_dir = getcwd()
    logger.info(''.join((Err_Fore.CYAN, '-> directory context ', new_dir,
                         Err_Fore.RESET)))
    chdir(new_dir)
    yield
    logger.info(''.join((Err_Fore.CYAN, '<- directory context ', cur_dir,
                         Err_Fore.RESET)))
    chdir(cur_dir)


@contextlib.contextmanager
def temp_directory():
    temp_dir = mkdtemp()
    try:
        logger.debug(''.join((Err_Fore.CYAN, ' + temp directory used ',
                              temp_dir, Err_Fore.RESET)))
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)
        logger.debug(''.join((Err_Fore.CYAN, ' - temp directory deleted ',
                              temp_dir, Err_Fore.RESET)))


def walk_valid_filens(base_dir, invalid_dir_names, invalid_file_patterns):
    """Recursively walks all the files and directories in ``dirn``,
    ignoring directories that match any pattern in ``invalid_dirns``
    and files that patch any pattern in ``invalid_filens``.

    ``invalid_dirns`` and ``invalid_filens`` should both be lists of
    strings to match. ``invalid_dir_patterns`` expects a list of
    invalid directory names, while ``invalid_file_patterns`` expects a
    list of glob patterns compared against the full filepath.

    File and directory paths are evaluated as full paths relative to ``dirn``.

    """

    for dirn, subdirs, filens in walk(base_dir):

        # Remove invalid subdirs so that they will not be walked
        for i in reversed(range(len(subdirs))):
            subdir = subdirs[i]
            if subdir in invalid_dir_names:
                subdirs.pop(i)

        for filen in filens:
            for pattern in invalid_file_patterns:
                if fnmatch(filen, pattern):
                    break
            else:
                yield join(dirn, filen)


def load_source(module, filename):
    # Python 3.5+
    import importlib.util
    if hasattr(importlib.util, 'module_from_spec'):
        spec = importlib.util.spec_from_file_location(module, filename)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    else:
        # Python 3.3 and 3.4:
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader(module, filename).load_module()


class BuildInterruptingException(Exception):
    def __init__(self, message, instructions=None):
        super().__init__(message, instructions)
        self.message = message
        self.instructions = instructions


def handle_build_exception(exception):
    """
    Handles a raised BuildInterruptingException by printing its error
    message and associated instructions, if any, then exiting.
    """
    error('Build failed: {}'.format(exception.message))
    if exception.instructions is not None:
        info('Instructions: {}'.format(exception.instructions))
    exit(1)


def rmdir(dn, ignore_errors=False):
    if not exists(dn):
        return
    LOGGER.debug("Remove directory and subdirectory {}".format(dn))
    shutil.rmtree(dn, ignore_errors)


def ensure_dir(dn):
    if exists(dn):
        return
    LOGGER.debug("Create directory {0}".format(dn))
    makedirs(dn)


def move(source, destination):
    LOGGER.debug("Moving {} to {}".format(source, destination))
    shutil.move(source, destination)


def touch(filename):
    Path(filename).touch()


def build_tools_version_sort_key(
    version_string: str,
) -> packaging.version.Version:
    """
    Returns a packaging.version.Version object for comparison purposes.
    It includes canonicalization of the version string to allow for
    comparison of versions with spaces in them (historically, RC candidates)

    If the version string is invalid, it returns a version object with
    version 0, which will be sorted at worst position.
    """

    try:
        # Historically, Android build release candidates have had
        # spaces in the version number.
        return packaging.version.Version(version_string.replace(" ", ""))
    except packaging.version.InvalidVersion:
        # Put badly named versions at worst position.
        return packaging.version.Version("0")


def max_build_tool_version(
    build_tools_versions: list,
) -> str:
    """
    Returns the maximum build tools version from a list of build tools
    versions. It uses the :meth:`build_tools_version_sort_key` function to
    canonicalize the version strings and then returns the maximum version.
    """

    return max(build_tools_versions, key=build_tools_version_sort_key)
