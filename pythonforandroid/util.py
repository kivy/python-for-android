import contextlib
from os.path import exists, join
from os import getcwd, chdir, makedirs, walk, uname
import shutil
from fnmatch import fnmatch
from tempfile import mkdtemp

from urllib.request import FancyURLopener

from pythonforandroid.logger import (logger, Err_Fore, error, info)


class WgetDownloader(FancyURLopener):
    version = ('Wget/1.17.1')


urlretrieve = WgetDownloader().retrieve


build_platform = '{system}-{machine}'.format(
    system=uname()[0], machine=uname()[-1]).lower()
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


def ensure_dir(filename):
    if not exists(filename):
        makedirs(filename)


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
