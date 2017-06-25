'''
Notes: stdin is not handled very well, needs to be tested. Similary for
chaining funtion calls using args.
'''


import subprocess as subp
import sys
import traceback
import os
import re
from itertools import chain
import glob as glob_module
from types import ModuleType
from functools import partial
import warnings
import platform
import shlex
from locale import getpreferredencoding

DEFAULT_ENCODING = getpreferredencoding() or "UTF-8"

IS_PY3 = sys.version_info[0] == 3
if IS_PY3:
    raw_input = input
    unicode = str
else:
    pass


if "windows" not in platform.system().lower():
    warnings.simplefilter("always")


def try_decode(s):
    if not isinstance(s, bytes):
        return s

    try:
        return s.decode(DEFAULT_ENCODING)
    except UnicodeEncodeError:
        return s.decode('utf-8', "replace")


def encode_to_py3bytes_or_py2str(s):
    """ takes anything and attempts to return a py2 string or py3 bytes.  this
    is typically used when creating command + arguments to be executed via
    os.exec* """

    fallback_encoding = "utf8"

    if IS_PY3:
        # if we're already bytes, do nothing
        if isinstance(s, bytes):
            pass
        else:
            s = str(s)
            try:
                s = bytes(s, DEFAULT_ENCODING)
            except UnicodeEncodeError:
                s = bytes(s, fallback_encoding)
    else:
        # attempt to convert the thing to unicode from the system's encoding
        try:
            s = unicode(s, DEFAULT_ENCODING)
        # if the thing is already unicode, or it's a number, it can't be
        # coerced to unicode with an encoding argument, but if we leave out
        # the encoding argument, it will convert it to a string, then to unicode
        except TypeError:
            s = unicode(s)

        # now that we have guaranteed unicode, encode to our system encoding,
        # but attempt to fall back to something
        try:
            s = s.encode(DEFAULT_ENCODING)
        except:
            s = s.encode(fallback_encoding, "replace")
    return s


class ErrorReturnCode(Exception):
    truncate_cap = 200

    def __init__(self, full_cmd, stdout, stderr):
        self.full_cmd = full_cmd
        self.stdout = '' if stdout is None else try_decode(stdout)
        self.stderr = '' if stderr is None else try_decode(stderr)

        if stdout is None:
            tstdout = u"<redirected>"
        else:
            tstdout = self.stdout[:self.truncate_cap]
            out_delta = len(self.stdout) - len(tstdout)
            if out_delta:
                tstdout += (u"... (%d more, please see e.stdout)" % out_delta)

        if stderr is None:
            tstderr = u"<redirected>"
        else:
            tstderr = self.stderr[:self.truncate_cap]
            err_delta = len(self.stderr) - len(tstderr)
            if err_delta:
                tstderr += (u"... (%d more, please see e.stderr)" % err_delta)

        msg = u"\n\nRan: %r\n\nSTDOUT:\n\n  %s\n\nSTDERR:\n\n  %s" %\
            (full_cmd, tstdout, tstderr)
        super(ErrorReturnCode, self).__init__(msg)


class CommandNotFound(Exception):
    pass

rc_exc_regex = re.compile("ErrorReturnCode_(\d+)")
rc_exc_cache = {}


def get_rc_exc(rc):
    rc = int(rc)
    try:
        return rc_exc_cache[rc]
    except KeyError:
        pass

    name = "ErrorReturnCode_%d" % rc
    exc = type(name, (ErrorReturnCode,), {})
    rc_exc_cache[rc] = exc
    return exc


def parse_shebang(filename):
    shebang = []
    filename = os.path.abspath(filename)
    if not os.path.exists(filename):
        return []

    with open(filename, 'r') as fh:
        try:
            if fh.read(2) == "#!":
                shebang = shlex.split(fh.readline().strip())
        except UnicodeError:
            pass

    if not shebang:
        return []
    shebang = list(shebang)

    p = resolve_program(shebang[0])
    if not p:
        p = which('cygpath')
        if not p:
            return []

        try:
            shebang[0] = Command(p)('-w', '-a', shebang[0], _cwd=os.path.dirname(filename), _bg=False).stdout.strip()
        except:
            return []

        if not resolve_program(shebang[0]):
            return []
    return shebang


def which(program, path_env=None):
    def is_exe(fpath):
        return (os.path.exists(fpath) and os.access(fpath, os.X_OK)
                and os.path.isfile(os.path.realpath(fpath)))

    fpath, fname = os.path.split(program)
    if fpath:
        program = os.path.abspath(program)
        if is_exe(program):
            return program
        for name in ('.exe', '.bat', '.cmd', '.sh'):
            if is_exe(program + name):
                return program + name
    else:
        for path in (path_env or os.environ["PATH"]).split(os.pathsep):
            path = os.path.abspath(path)
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
            for name in ('.exe', '.bat', '.cmd', '.sh'):
                if is_exe(exe_file + name):
                    return exe_file + name
    return None


def resolve_program(program):
    path = which(program)
    if not path:
        # our actual command might have a dash in it, but we can't call
        # that from python (we have to use underscores), so we'll check
        # if a dash version of our underscore command exists and use that
        # if it does
        if "_" in program:
            path = which(program.replace("_", "-"))
    return path


# we monkey patch glob.  i'm normally generally against monkey patching, but i
# decided to do this really un-intrusive patch because we need a way to detect
# if a list that we pass into an sh command was generated from glob.  the reason
# being that glob returns an empty list if a pattern is not found, and so
# commands will treat the empty list as no arguments, which can be a problem,
# ie:
#
#   ls(glob("*.ojfawe"))
#
# ^ will show the contents of your home directory, because it's essentially
# running ls([]) which, as a process, is just "ls".
#
# so we subclass list and monkey patch the glob function.  nobody should be the
# wiser, but we'll have results that we can make some determinations on
_old_glob = glob_module.glob

class GlobResults(list):
    def __init__(self, path, results):
        self.path = path
        list.__init__(self, results)

def glob(path, *args, **kwargs):
    expanded = GlobResults(path, _old_glob(path, *args, **kwargs))
    return expanded

glob_module.glob = glob


def compile_args(args, kwargs, sep, prefix):
    """ takes args and kwargs, as they were passed into the command instance
    being executed with __call__, and compose them into a flat list that
    will eventually be fed into exec.  example:
    with this call:
        sh.ls("-l", "/tmp", color="never")
    this function receives
        args = ['-l', '/tmp']
        kwargs = {'color': 'never'}
    and produces
        ['-l', '/tmp', '--color=never']

    """
    processed_args = []
    encode = encode_to_py3bytes_or_py2str

    # aggregate positional args
    for arg in args:
        if isinstance(arg, (list, tuple)):
            if isinstance(arg, GlobResults) and not arg:
                arg = [arg.path]

            for sub_arg in arg:
                processed_args.append(encode(sub_arg))
        elif isinstance(arg, dict):
            processed_args += aggregate_keywords(arg, sep, prefix, raw=True)
        else:
            processed_args.append(encode(arg))

    # aggregate the keyword arguments
    processed_args += aggregate_keywords(kwargs, sep, prefix)

    return processed_args


def aggregate_keywords(keywords, sep, prefix, raw=False):
    """ take our keyword arguments, and a separator, and compose the list of
    flat long (and short) arguments.  example
        {'color': 'never', 't': True, 'something': True} with sep '='
    becomes
        ['--color=never', '-t', '--something']
    the `raw` argument indicates whether or not we should leave the argument
    name alone, or whether we should replace "_" with "-".  if we pass in a
    dictionary, like this:
        sh.command({"some_option": 12})
    then `raw` gets set to True, because we want to leave the key as-is, to
    produce:
        ['--some_option=12']
    but if we just use a command's kwargs, `raw` is False, which means this:
        sh.command(some_option=12)
    becomes:
        ['--some-option=12']
    eessentially, using kwargs is a convenience, but it lacks the ability to
    put a '-' in the name, so we do the replacement of '_' to '-' for you.
    but when you really don't want that to happen, you should use a
    dictionary instead with the exact names you want
    """

    processed = []
    encode = encode_to_py3bytes_or_py2str

    for k, v in keywords.items():
        # we're passing a short arg as a kwarg, example:
        # cut(d="\t")
        if len(k) == 1:
            if v is not False:
                processed.append(encode("-" + k))
                if v is not True:
                    processed.append(encode(v))

        # we're doing a long arg
        else:
            if not raw:
                k = k.replace("_", "-")

            if v is True:
                processed.append(encode("--" + k))
            elif v is False:
                pass
            elif sep is None or sep == " ":
                processed.append(encode(prefix + k))
                processed.append(encode(v))
            else:
                arg = encode("%s%s%s%s" % (prefix, k, sep, v))
                processed.append(arg)

    return processed


class RunningCommand(object):
    def __init__(self, command_ran, process, call_args, stdin=None):
        self.command_ran = command_ran
        self.process = process
        self._stdout = ''
        self._stderr = ''
        self.call_args = call_args

        # we're running in the background, return self and let us lazily
        # evaluate
        if self.call_args["bg"] or self.call_args["iter"]:
            return

        # run and block
        self.wait(stdin)

    def __str__(self):
        if IS_PY3:
            return self.__unicode__()
        else:
            return unicode(self).encode(self.call_args["encoding"])

    def __unicode__(self):
        return self.stdout.decode(self.call_args["encoding"],
                                  self.call_args["decode_errors"])

    def __eq__(self, other):
        return self.__unicode__() == unicode(other)

    def __contains__(self, item):
        return item in str(self)

    def __getattr__(self, p):
        # let these three attributes pass through to the Popen object
        if p in ("send_signal", "terminate", "kill"):
            if self.process:
                return getattr(self.process, p)
            else:
                raise AttributeError
        return getattr(self.__unicode__(), p)

    def __repr__(self):
        return "<RunningCommand %r" % self.command_ran

    def __long__(self):
        return long(str(self).strip())

    def __float__(self):
        return float(str(self).strip())

    def __int__(self):
        return int(str(self).strip())

    @property
    def stdout(self):
        self.wait()
        return self._stdout

    @property
    def stderr(self):
        self.wait()
        return self._stderr

    def wait(self, stdin=None):
        if self.process.returncode is not None:
            return

        if stdin:
            if IS_PY3:
                if isinstance(stdin, str):
                    stdin = stdin.encode("utf8")
                elif not isinstance(stdin, bytes):
                    stdin = str(stdin).encode("utf8")
            else:
                if isinstance(stdin, unicode):
                    stdin = stdin.encode("utf8")
                elif not isinstance(stdin, bytes):
                    stdin = str(stdin)

        self._stdout, self._stderr = self.process.communicate(stdin)
        self._handle_exit_code(self.process.wait())
        return self

    def _handle_exit_code(self, rc):
        if rc not in self.call_args["ok_code"]:
            raise get_rc_exc(rc)(
                self.command_ran, self._stdout,
                None if self.call_args['err_to_out'] else self._stderr)

    def __len__(self):
        return len(str(self))

    def __iter__(self):
        return self

    def next(self):
        process = self.process
        if process is None or process.stdout is None:
            raise StopIteration()

        ok = self.call_args["ok_code"]
        lines = iter(process.stdout.readline, '')
        for line in lines:
            self._stdout += line
            return line

            retval = process.poll()
            if retval is None or retval in ok:
                continue
            else:
                break

        stdout, self._stderr = process.communicate()
        self._stdout += stdout
        self._handle_exit_code(self.process.wait())
        raise StopIteration()

    __next__ = next  # python 3


class Command(object):

    call_args = {
        "fg": False, # run command in foreground

        # run a command in the background.  commands run in the background
        # ignore SIGHUP and do not automatically exit when the parent process
        # ends
        "bg": False,

        "in": None,
        "out": None, # redirect STDOUT
        "err": None, # redirect STDERR
        "err_to_out": None, # redirect STDERR to STDOUT

        "out_bufsize": 1,
        "iter": False,

        "env": None,
        "ok_code": 0,
        "cwd": None,

        "decode_errors": "strict",
        "encoding": DEFAULT_ENCODING
    }

    @classmethod
    def _create(cls, program):
        path = resolve_program(program)
        if not path:
            raise CommandNotFound(program)
        return cls(path)

    def __init__(self, path):
        self._path = path
        self._partial = False
        self._partial_baked_args = []
        self._partial_call_args = {}

    def __getattribute__(self, name):
        # convenience
        getattr = partial(object.__getattribute__, self)
        if name.startswith("_"):
            return getattr(name)
        if name == "bake":
            return getattr("bake")
        return getattr("bake")(name)

    @staticmethod
    def _extract_call_args(kwargs):
        kwargs = kwargs.copy()
        call_args = Command.call_args.copy()
        for parg, default in call_args.items():
            key = "_" + parg
            if key in kwargs:
                call_args[parg] = kwargs[key]
                del kwargs[key]
        return call_args, kwargs

    def bake(self, *args, **kwargs):
        fn = Command(self._path)
        fn._partial = True

        call_args, kwargs = self._extract_call_args(kwargs)

        pruned_call_args = call_args
        for k, v in Command.call_args.items():
            try:
                if pruned_call_args[k] == v:
                    del pruned_call_args[k]
            except KeyError:
                continue

        fn._partial_call_args.update(self._partial_call_args)
        fn._partial_call_args.update(pruned_call_args)
        fn._partial_baked_args.extend(self._partial_baked_args)
        fn._partial_baked_args.extend(compile_args(args, kwargs, '=', '--'))
        return fn

    def __str__(self):
        if IS_PY3:
            return self.__unicode__()
        else:
            return self.__unicode__().encode(DEFAULT_ENCODING)

    def __repr__(self):
        return "<Command %r>" % str(self)

    def __eq__(self, other):
        return str(self) == str(other)

    __hash__ = None # Avoid DeprecationWarning in Python < 3

    def __unicode__(self):
        """ a magic method defined for python2.  calling unicode() on a
        self will call this """
        baked_args = " ".join(item.decode(DEFAULT_ENCODING)
                              for item in self._partial_baked_args)
        if baked_args:
            baked_args = " " + baked_args
        return self._path.decode(DEFAULT_ENCODING) + baked_args

    def __call__(self, *args, **kwargs):

        kwargs = kwargs.copy()
        args = list(args)

        cmd = []

        app = resolve_program(self._path) or ''
        if app.endswith('configure'):
            cmd.append(resolve_program('bash'))
            cmd.append(app)
        elif app:
            if os.name == 'nt':
                shebang = parse_shebang(app)
                if shebang:
                    cmd.extend(shebang)
                elif app.endswith('.sh'):
                    name = resolve_program('sh')
                    if name:
                        cmd.append(name)
            cmd.append(app)

        call_args, kwargs = self._extract_call_args(kwargs)
        call_args.update(self._partial_call_args)

        # here we normalize the ok_code to be something we can do
        # "if return_code in call_args["ok_code"]" on
        if not getattr(call_args["ok_code"], "__iter__", None):
            call_args["ok_code"] = [call_args["ok_code"]]

        # set pipe to None if we're outputting straight to CLI
        pipe = subp.PIPE

        # check if we're piping via composition
        stdin = pipe
        actual_stdin = None
        if args:
            first_arg = args.pop(0)
            if isinstance(first_arg, RunningCommand):
                # it makes sense that if the input pipe of a command is running
                # in the background, then this command should run in the
                # background as well
                if first_arg.call_args["bg"]:
                    call_args["bg"] = True
                    stdin = first_arg.process.stdout
                else:
                    actual_stdin = first_arg.stdout
            else:
                args.insert(0, first_arg)

        processed_args = compile_args(args, kwargs, '=', '--')

        # makes sure our arguments are broken up correctly
        split_args = self._partial_baked_args + processed_args
        final_args = split_args

        cmd.extend(final_args)
        command_ran = " ".join(cmd)

        # stdin from string
        input = call_args["in"]
        if input:
            actual_stdin = input

        # stdout redirection
        stdout = pipe
        out = call_args["out"]
        if out:
            if hasattr(out, "write"):
                stdout = out
            else:
                stdout = open(str(out), "w")

        # stderr redirection
        stderr = pipe
        err = call_args["err"]
        if err:
            if hasattr(err, "write"):
                stderr = err
            else:
                stderr = open(str(err), "w")

        if call_args["err_to_out"]:
            stderr = subp.STDOUT

        # leave shell=False
        process = subp.Popen(cmd, shell=False, env=call_args["env"],
            cwd=call_args["cwd"], stdin=stdin, stdout=stdout, stderr=stderr,
            bufsize=call_args['out_bufsize'])

        return RunningCommand(command_ran, process, call_args, actual_stdin)


class Environment(dict):
    '''this class is used directly when we do a "from sh import *".  it allows
    lookups to names that aren't found in the global scope to be searched
    for as a program.  for example, if "ls" isn't found in the program's
    scope, we consider it a system program and try to find it.
    '''
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

        self["Command"] = Command
        self["CommandNotFound"] = CommandNotFound
        self["ErrorReturnCode"] = ErrorReturnCode
        self["ARGV"] = sys.argv[1:]
        self['glob'] = glob
        for i, arg in enumerate(sys.argv):
            self["ARG%d" % i] = arg

        # this needs to be last
        self["env"] = os.environ

    def __setitem__(self, k, v):
        # are we altering an environment variable?
        if "env" in self and k in self["env"]:
            self["env"][k] = v
        # no?  just setting a regular name
        else:
            dict.__setitem__(self, k, v)

    def __missing__(self, k):
        # the only way we'd get to here is if we've tried to
        # import * from a repl.  so, raise an exception, since
        # that's really the only sensible thing to do
        if k == "__all__":
            raise ImportError("Cannot import * from sh. \
Please import sh or import programs individually.")

        # if we end with "_" just go ahead and skip searching
        # our namespace for python stuff.  this was mainly for the
        # command "id", which is a popular program for finding
        # if a user exists, but also a python function for getting
        # the address of an object.  so can call the python
        # version by "id" and the program version with "id_"
        if not k.endswith("_"):
            # check if we're naming a dynamically generated ReturnCode exception
            try:
                return rc_exc_cache[k]
            except KeyError:
                m = rc_exc_regex.match(k)
                if m:
                    return get_rc_exc(int(m.group(1)))

            # are we naming a commandline argument?
            if k.startswith("ARG"):
                return None

            # is it a builtin?
            try:
                return getattr(self["__builtins__"], k)
            except AttributeError:
                pass
        elif not k.startswith("_"):
            k = k.rstrip("_")

        # how about an environment variable?
        try:
            return os.environ[k]
        except KeyError:
            pass

        # is it a custom builtin?
        builtin = getattr(self, "b_"+k, None)
        if builtin:
            return builtin

        # it must be a command then
        return Command._create(k)

    def b_cd(self, path):
        os.chdir(path)

    def b_which(self, program):
        return which(program)


class SelfWrapper(ModuleType):
    '''this is a thin wrapper around THIS module (we patch sys.modules[__name__]).
    this is in the case that the user does a "from pbs import whatever"
    in other words, they only want to import certain programs, not the whole
    system PATH worth of commands.  in this case, we just proxy the
    import lookup to our Environment class
    '''

    def __init__(self, self_module):
        # this is super ugly to have to copy attributes like this,
        # but it seems to be the only way to make reload() behave
        # nicely.  if i make these attributes dynamic lookups in
        # __getattr__, reload sometimes chokes in weird ways...
        for attr in ["__builtins__", "__doc__", "__name__", "__package__"]:
            setattr(self, attr, getattr(self_module, attr))

        self.self_module = self_module
        self.env = Environment(globals())

    def __getattr__(self, name):
        return self.env[name]


if __name__ != "__main__":
    self = sys.modules[__name__]
    sys.modules[__name__] = SelfWrapper(self)
