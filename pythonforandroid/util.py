import contextlib
from os.path import exists, join
from os import getcwd, chdir, makedirs, walk
import io
import json
import shutil
import sys
from fnmatch import fnmatch
from tempfile import mkdtemp
try:
    from urllib.request import FancyURLopener
except ImportError:
    from urllib import FancyURLopener

from pythonforandroid.logger import (logger, Err_Fore)

IS_PY3 = sys.version_info[0] >= 3


class WgetDownloader(FancyURLopener):
    version = ('Wget/1.17.1')


urlretrieve = WgetDownloader().retrieve


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


class JsonStore(object):
    """Replacement of shelve using json, needed for support python 2 and 3.
    """

    def __init__(self, filename):
        super(JsonStore, self).__init__()
        self.filename = filename
        self.data = {}
        if exists(filename):
            try:
                with io.open(filename, encoding='utf-8') as fd:
                    self.data = json.load(fd)
            except ValueError:
                print("Unable to read the state.db, content will be replaced.")

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.sync()

    def __delitem__(self, key):
        del self.data[key]
        self.sync()

    def __contains__(self, item):
        return item in self.data

    def get(self, item, default=None):
        return self.data.get(item, default)

    def keys(self):
        return self.data.keys()

    def remove_all(self, prefix):
        for key in self.data.keys()[:]:
            if not key.startswith(prefix):
                continue
            del self.data[key]
        self.sync()

    def sync(self):
        # http://stackoverflow.com/questions/12309269/write-json-data-to-file-in-python/14870531#14870531
        if IS_PY3:
            with open(self.filename, 'w') as fd:
                json.dump(self.data, fd, ensure_ascii=False)
        else:
            with io.open(self.filename, 'w', encoding='utf-8') as fd:
                fd.write(unicode(json.dumps(self.data, ensure_ascii=False)))  # noqa F821


def which(program, path_env):
    '''Locate an executable in the system.'''
    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in path_env.split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


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
