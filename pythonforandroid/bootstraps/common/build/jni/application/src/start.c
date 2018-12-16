
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#ifndef Py_PYTHON_H
#error Python headers needed to compile C extensions, please install development version of Python.
#else

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <dirent.h>
#include <jni.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>

#include "bootstrap_name.h"
#ifndef BOOTSTRAP_USES_NO_SDL_HEADERS
#include "SDL.h"
#include "SDL_opengles2.h"
#endif
#ifdef BOOTSTRAP_NAME_PYGAME
#include "jniwrapperstuff.h"
#endif
#include "android/log.h"

#define ENTRYPOINT_MAXLEN 128
#define LOG(n, x) __android_log_write(ANDROID_LOG_INFO, (n), (x))
#define LOGP(x) LOG("python", (x))

static PyObject *androidembed_log(PyObject *self, PyObject *args) {
  char *logstr = NULL;
  if (!PyArg_ParseTuple(args, "s", &logstr)) {
    return NULL;
  }
  LOG(getenv("PYTHON_NAME"), logstr);
  Py_RETURN_NONE;
}

static PyMethodDef AndroidEmbedMethods[] = {
    {"log", androidembed_log, METH_VARARGS, "Log on android platform"},
    {NULL, NULL, 0, NULL}};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef androidembed = {PyModuleDef_HEAD_INIT, "androidembed",
                                          "", -1, AndroidEmbedMethods};

PyMODINIT_FUNC initandroidembed(void) {
  return PyModule_Create(&androidembed);
}
#else
PyMODINIT_FUNC initandroidembed(void) {
  (void)Py_InitModule("androidembed", AndroidEmbedMethods);
}
#endif

int dir_exists(char *filename) {
  struct stat st;
  if (stat(filename, &st) == 0) {
    if (S_ISDIR(st.st_mode))
      return 1;
  }
  return 0;
}

int file_exists(const char *filename) {
  FILE *file;
  if (file = fopen(filename, "r")) {
    fclose(file);
    return 1;
  }
  return 0;
}

/* Helper function to escape all occurrences of ' as \', and all
 * occurrences of \n and \r with \\n and \\r for inline string literals.
 * (Unix paths can contain line breaks, so to be super safe, we need this).
 * NOTE: return value needs to be free()'d after use by the caller!!
 */
char *escape_quotes_of_inline_string(const char* inline_code_arg) {
  char *result_buf = malloc(strlen(inline_code_arg) * 2 + 1);
  // (buffer size is large enough for worst case of every char escaped)
  int targetoffset = 0;
  int sourceoffset = 0;
  while (sourceoffset <= strlen(inline_code_arg)) {
    if (inline_code_arg[sourceoffset] == '\'') {
      result_buf[targetoffset] = '\\';
      targetoffset++;
      result_buf[targetoffset] = '\'';
    } else if (inline_code_arg[sourceoffset] == '\n') {
      result_buf[targetoffset] = '\\';
      targetoffset++;
      result_buf[targetoffset] = 'n';
    } else if (inline_code_arg[sourceoffset] == '\r') {
      result_buf[targetoffset] = '\\';
      targetoffset++;
      result_buf[targetoffset] = 'r';
    } else {
      result_buf[targetoffset] = inline_code_arg[sourceoffset];
    }
    sourceoffset++;
    targetoffset++;
  }
  return result_buf;
}

/* int main(int argc, char **argv) { */
int main(int argc, char *argv[]) {

  char *env_argument = NULL;
  char *env_entrypoint = NULL;
  char *env_logname = NULL;
  char entrypoint[ENTRYPOINT_MAXLEN];
  int ret = 0;
  FILE *fd;

  setenv("P4A_BOOTSTRAP", bootstrap_name, 1);  // env var to identify p4a to applications

  LOGP("Initializing Python for Android");
  env_argument = getenv("ANDROID_ARGUMENT");
  setenv("ANDROID_APP_PATH", env_argument, 1);
  env_entrypoint = getenv("ANDROID_ENTRYPOINT");
  env_logname = getenv("PYTHON_NAME");

  if (!getenv("ANDROID_UNPACK")) {
    /* ANDROID_UNPACK currently isn't set in services */
    setenv("ANDROID_UNPACK", env_argument, 1);
  }
  
  if (env_logname == NULL) {
    env_logname = "python";
    setenv("PYTHON_NAME", "python", 1);
  }

  LOGP("Changing directory to the one provided by ANDROID_ARGUMENT");
  LOGP(env_argument);
  chdir(env_argument);

  Py_SetProgramName(L"android_python");

#if PY_MAJOR_VERSION >= 3
  /* our logging module for android
   */
  PyImport_AppendInittab("androidembed", initandroidembed);
#endif

  LOGP("Preparing to initialize python");

  // Set up the python path
  char paths[256];

  char crystax_python_dir[256];
  snprintf(crystax_python_dir, 256,
           "%s/crystax_python", getenv("ANDROID_UNPACK"));
  char python_bundle_dir[256];
  snprintf(python_bundle_dir, 256,
           "%s/_python_bundle", getenv("ANDROID_UNPACK"));
  if (dir_exists(crystax_python_dir) || dir_exists(python_bundle_dir)) {
    if (dir_exists(crystax_python_dir)) {
        LOGP("crystax_python exists");
        snprintf(paths, 256,
                "%s/stdlib.zip:%s/modules",
                crystax_python_dir, crystax_python_dir);
    }

    if (dir_exists(python_bundle_dir)) {
        LOGP("_python_bundle dir exists");
        snprintf(paths, 256,
                "%s/stdlib.zip:%s/modules",
                python_bundle_dir, python_bundle_dir);
    }

    LOGP("calculated paths to be...");
    LOGP(paths);

    #if PY_MAJOR_VERSION >= 3
        wchar_t *wchar_paths = Py_DecodeLocale(paths, NULL);
        Py_SetPath(wchar_paths);
    #else
        char *wchar_paths = paths;
        LOGP("Can't Py_SetPath in python2, so crystax python2 doesn't work yet");
        exit(1);
    #endif

        LOGP("set wchar paths...");
  } else {
      // We do not expect to see crystax_python any more, so no point
      // reminding the user about it. If it does exist, we'll have
      // logged it earlier.
      LOGP("_python_bundle does not exist");
  }

  Py_Initialize();

#if PY_MAJOR_VERSION < 3
  PySys_SetArgv(argc, argv);
#endif

  LOGP("Initialized python");

  /* ensure threads will work.
   */
  LOGP("AND: Init threads");
  PyEval_InitThreads();

#if PY_MAJOR_VERSION < 3
  initandroidembed();
#endif

  PyRun_SimpleString("import androidembed\nandroidembed.log('testing python "
                     "print redirection')");

  /* inject our bootstrap code to redirect python stdin/stdout
   * replace sys.path with our path
   */
  PyRun_SimpleString("import sys, posix\n");
  if (dir_exists("lib")) {
    /* If we built our own python, set up the paths correctly */
    LOGP("Setting up python from ANDROID_APP_PATH");
    PyRun_SimpleString("private = posix.environ['ANDROID_APP_PATH']\n"
                       "argument = posix.environ['ANDROID_ARGUMENT']\n"
                       "sys.path[:] = [ \n"
                       "    private + '/lib/python27.zip', \n"
                       "    private + '/lib/python2.7/', \n"
                       "    private + '/lib/python2.7/lib-dynload/', \n"
                       "    private + '/lib/python2.7/site-packages/', \n"
                       "    argument ]\n");
  }

  char add_site_packages_dir[256];
  if (dir_exists(crystax_python_dir)) {
    snprintf(add_site_packages_dir, 256,
             "sys.path.append('%s/site-packages')",
             crystax_python_dir);

    PyRun_SimpleString("import sys\n"
                       "sys.argv = ['notaninterpreterreally']\n"
                       "from os.path import realpath, join, dirname");
    PyRun_SimpleString(add_site_packages_dir);
    /* "sys.path.append(join(dirname(realpath(__file__)), 'site-packages'))") */
    PyRun_SimpleString("sys.path = ['.'] + sys.path");
  }

  if (dir_exists(python_bundle_dir)) {
    snprintf(add_site_packages_dir, 256,
             "sys.path.append('%s/site-packages')",
             python_bundle_dir);

    PyRun_SimpleString("import sys\n"
                       "sys.argv = ['notaninterpreterreally']\n"
                       "from os.path import realpath, join, dirname");
    PyRun_SimpleString(add_site_packages_dir);
    /* "sys.path.append(join(dirname(realpath(__file__)), 'site-packages'))") */
    PyRun_SimpleString("sys.path = ['.'] + sys.path");
  }

  PyRun_SimpleString(
      "class LogFile(object):\n"
      "    def __init__(self):\n"
      "        self.buffer = ''\n"
      "    def write(self, s):\n"
      "        s = self.buffer + s\n"
      "        lines = s.split(\"\\n\")\n"
      "        for l in lines[:-1]:\n"
      "            androidembed.log(l)\n"
      "        self.buffer = lines[-1]\n"
      "    def flush(self):\n"
      "        return\n"
      "sys.stdout = sys.stderr = LogFile()\n"
      "print('Android path', sys.path)\n"
      "import os\n"
      "print('os.environ is', os.environ)\n"
      "print('Android kivy bootstrap done. __name__ is', __name__)");

#if PY_MAJOR_VERSION < 3
  PyRun_SimpleString("import site; print site.getsitepackages()\n");
#endif
  LOGP("AND: Ran string");

#if PY_MAJOR_VERSION >= 3
  /* Workaround crash in ctypes.find_library() which is caused by its
   * internal use of /bin/sh, and looking in the wrong folders on Android.
   *
   * The code needs 'env_argument' as baked path, so we need to insert this:
   */
  LOGP("ctypes workaround insert");
  char code_with_placeholder[] = (""
    "orig_func = None\n"
    "try:\n"
    "    import ctypes.util\n"
    "    orig_func = ctypes.util.find_library\n"
    "except ImportError:\n"
    "    print('Could not import ctypes, build your app with '\n"
    "          'libffi if you want ctypes to be present')\n"
    "def create_closure(orig_func):\n"
    "    def android_find_library_hack(*args):\n"
    "        import os\n"
    "        name = args[0]\n"
    "        \n"
    "        # Truncate ending for easier comparison:\n"
    "        if name.find('.so.') >= 0:\n"
    "            name = name.partition('.so.')[0]\n"
    "        if name.endswith('.so'):\n"
    "            name = name[:-len('.so')]\n"
    "        if not name.endswith('.'):\n"
    "            name += '.'\n"
    "        \n"
    "        # Helper function to check lib name:\n"
    "        def check_name(lib_name, search_name):\n"
    "            if filename.endswith('.so') and (\n"
    "                    filename.startswith('lib' + search_name) or\n"
    "                    filename.startswith(search_name)):\n"
    "                return True\n"
    "            return False\n"
    "        \n"
    "        # Check the user app lib dir and system dir:\n"
    "        app_root = os.path.normpath(os.path.abspath(os.path.join(\n"
    "            '%s', '..', '..', 'lib')))\n"
    "        app_root_arm = os.path.join(app_root,\n"
    "                                    'arm')  # fixme: other archs?\n"
    "        sys_dir = '/system/lib'\n"
    "        for lib_search in [app_root, app_root_arm, sys_dir]:\n"
    "            if not os.path.exists(lib_search):\n"
    "                continue\n"
    "            for filename in os.listdir(lib_search):\n"
    "                if check_name(filename, name):\n"
    "                    return os.path.join(lib_search, filename)\n"
    "        try:\n"
    "            return orig_func(*args)\n"
    "        except OSError:\n"  // catch bogus error about missing "sh"
    "            return None\n"
    "    return lambda *args: android_find_library_hack(*args)\n"
    "if orig_func is not None:\n"
    "    ctypes.util.find_library = create_closure(orig_func)\n"
    "del(orig_func)\n"
    "del(create_closure)\n");
  char *escaped_path_arg = escape_quotes_of_inline_string(env_argument);
  int final_code_buf_size = (strlen(code_with_placeholder) +
    strlen(escaped_path_arg) + 1);  // slightly too large, but good enough
  char *final_ctypes_code = malloc(final_code_buf_size);
  snprintf(final_ctypes_code, final_code_buf_size, code_with_placeholder,
    escaped_path_arg);
  free(escaped_path_arg);
  PyRun_SimpleString(final_ctypes_code);
  free(final_ctypes_code);
#endif

  /* run it !
   */
  LOGP("Run user program, change dir and execute entrypoint");

  /* Get the entrypoint, search the .pyo then .py
   */
  char *dot = strrchr(env_entrypoint, '.');
  if (dot <= 0) {
    LOGP("Invalid entrypoint, abort.");
    return -1;
  }
  if (strlen(env_entrypoint) > ENTRYPOINT_MAXLEN - 2) {
      LOGP("Entrypoint path is too long, try increasing ENTRYPOINT_MAXLEN.");
      return -1;
  }
  if (!strcmp(dot, ".pyo")) {
    if (!file_exists(env_entrypoint)) {
      /* fallback on .py */
      strcpy(entrypoint, env_entrypoint);
      entrypoint[strlen(env_entrypoint) - 1] = '\0';
      LOGP(entrypoint);
      if (!file_exists(entrypoint)) {
        LOGP("Entrypoint not found (.pyo, fallback on .py), abort");
        return -1;
      }
    } else {
      strcpy(entrypoint, env_entrypoint);
    }
  } else if (!strcmp(dot, ".py")) {
    /* if .py is passed, check the pyo version first */
    strcpy(entrypoint, env_entrypoint);
    entrypoint[strlen(env_entrypoint) + 1] = '\0';
    entrypoint[strlen(env_entrypoint)] = 'o';
    if (!file_exists(entrypoint)) {
      /* fallback on pure python version */
      if (!file_exists(env_entrypoint)) {
        LOGP("Entrypoint not found (.py), abort.");
        return -1;
      }
      strcpy(entrypoint, env_entrypoint);
    }
  } else {
    LOGP("Entrypoint have an invalid extension (must be .py or .pyo), abort.");
    return -1;
  }
  // LOGP("Entrypoint is:");
  // LOGP(entrypoint);
  fd = fopen(entrypoint, "r");
  if (fd == NULL) {
    LOGP("Open the entrypoint failed");
    LOGP(entrypoint);
    return -1;
  }

  /* run python !
   */
  ret = PyRun_SimpleFile(fd, entrypoint);

  if (PyErr_Occurred() != NULL) {
    ret = 1;
    PyErr_Print(); /* This exits with the right code if SystemExit. */
    PyObject *f = PySys_GetObject("stdout");
    if (PyFile_WriteString(
            "\n", f)) /* python2 used Py_FlushLine, but this no longer exists */
      PyErr_Clear();
  }

  /* close everything
   */
  Py_Finalize();
  fclose(fd);

  LOGP("Python for android ended.");
  return ret;
}

JNIEXPORT void JNICALL Java_org_kivy_android_PythonService_nativeStart(
    JNIEnv *env,
    jobject thiz,
    jstring j_android_private,
    jstring j_android_argument,
#if (!defined(BOOTSTRAP_NAME_PYGAME))
    jstring j_service_entrypoint,
    jstring j_python_name,
#endif
    jstring j_python_home,
    jstring j_python_path,
    jstring j_arg) {
  jboolean iscopy;
  const char *android_private =
      (*env)->GetStringUTFChars(env, j_android_private, &iscopy);
  const char *android_argument =
      (*env)->GetStringUTFChars(env, j_android_argument, &iscopy);
#if (!defined(BOOTSTRAP_NAME_PYGAME))
  const char *service_entrypoint =
      (*env)->GetStringUTFChars(env, j_service_entrypoint, &iscopy);
  const char *python_name =
      (*env)->GetStringUTFChars(env, j_python_name, &iscopy);
#else
  const char python_name[] = "python2";
#endif
  const char *python_home =
      (*env)->GetStringUTFChars(env, j_python_home, &iscopy);
  const char *python_path =
      (*env)->GetStringUTFChars(env, j_python_path, &iscopy);
  const char *arg = (*env)->GetStringUTFChars(env, j_arg, &iscopy);

  setenv("ANDROID_PRIVATE", android_private, 1);
  setenv("ANDROID_ARGUMENT", android_argument, 1);
  setenv("ANDROID_APP_PATH", android_argument, 1);

#if (!defined(BOOTSTRAP_NAME_PYGAME))
  setenv("ANDROID_ENTRYPOINT", service_entrypoint, 1);
#endif
  setenv("PYTHONOPTIMIZE", "2", 1);
  setenv("PYTHON_NAME", python_name, 1);
  setenv("PYTHONHOME", python_home, 1);
  setenv("PYTHONPATH", python_path, 1);
  setenv("PYTHON_SERVICE_ARGUMENT", arg, 1);
  setenv("P4A_BOOTSTRAP", bootstrap_name, 1);

  char *argv[] = {"."};
  /* ANDROID_ARGUMENT points to service subdir,
   * so main() will run main.py from this dir
   */
  main(1, argv);
}

#ifdef BOOTSTRAP_NAME_WEBVIEW
// Webview uses some more functions:

void Java_org_kivy_android_PythonActivity_nativeSetEnv(
                                    JNIEnv* env, jclass jcls,
                                    jstring j_name, jstring j_value)
/* JNIEXPORT void JNICALL Java_org_libsdl_app_SDLActivity_nativeSetEnv( */
/*                                     JNIEnv* env, jclass jcls, */
/*                                     jstring j_name, jstring j_value) */
{
    jboolean iscopy;
    const char *name = (*env)->GetStringUTFChars(env, j_name, &iscopy);
    const char *value = (*env)->GetStringUTFChars(env, j_value, &iscopy);
    setenv(name, value, 1);
    (*env)->ReleaseStringUTFChars(env, j_name, name);
    (*env)->ReleaseStringUTFChars(env, j_value, value);
}


void Java_org_kivy_android_PythonActivity_nativeInit(JNIEnv* env, jclass cls, jobject obj)
{
  /* This nativeInit follows SDL2 */

  /* This interface could expand with ABI negotiation, calbacks, etc. */
  /* SDL_Android_Init(env, cls); */

  /* SDL_SetMainReady(); */

  /* Run the application code! */
  int status;
  char *argv[2];
  argv[0] = "Python_app";
  argv[1] = NULL;
  /* status = SDL_main(1, argv); */

  main(1, argv);

  /* Do not issue an exit or the whole application will terminate instead of just the SDL thread */
  /* exit(status); */
}
#endif

#endif
