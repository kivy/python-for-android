
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

#include "SDL.h"
#include "android/log.h"
#include "SDL_opengles2.h"

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

/* int main(int argc, char **argv) { */
int main(int argc, char *argv[]) {

  char *env_argument = NULL;
  char *env_entrypoint = NULL;
  char *env_logname = NULL;
  char entrypoint[ENTRYPOINT_MAXLEN];
  int ret = 0;
  FILE *fd;

  /* AND: Several filepaths are hardcoded here, these must be made
     configurable */
  /* AND: P4A uses env vars...not sure what's best */
  LOGP("Initialize Python for Android");
  env_argument = getenv("ANDROID_ARGUMENT");
  setenv("ANDROID_APP_PATH", env_argument, 1);
  env_entrypoint = getenv("ANDROID_ENTRYPOINT");
  env_logname = getenv("PYTHON_NAME");
  
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

  if (dir_exists("crystax_python/")) {
    LOGP("crystax_python exists");
    char paths[256];
    snprintf(paths, 256,
             "%s/crystax_python/stdlib.zip:%s/crystax_python/modules",
             env_argument, env_argument);
    /* snprintf(paths, 256, "%s/stdlib.zip:%s/modules", env_argument,
     * env_argument); */
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
    LOGP("crystax_python does not exist");
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
    LOGP("Setting up python from ANDROID_PRIVATE");
    PyRun_SimpleString("private = posix.environ['ANDROID_APP_PATH']\n"
                       "argument = posix.environ['ANDROID_ARGUMENT']\n"
                       "sys.path[:] = [ \n"
                       "    private + '/lib/python27.zip', \n"
                       "    private + '/lib/python2.7/', \n"
                       "    private + '/lib/python2.7/lib-dynload/', \n"
                       "    private + '/lib/python2.7/site-packages/', \n"
                       "    argument ]\n");
  }

  if (dir_exists("crystax_python")) {
    char add_site_packages_dir[256];
    snprintf(add_site_packages_dir, 256,
             "sys.path.append('%s/crystax_python/site-packages')",
             env_argument);

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
    JNIEnv *env, jobject thiz, jstring j_android_private,
    jstring j_android_argument, jstring j_service_entrypoint,
    jstring j_python_name, jstring j_python_home, jstring j_python_path,
    jstring j_arg) {
  jboolean iscopy;
  const char *android_private =
      (*env)->GetStringUTFChars(env, j_android_private, &iscopy);
  const char *android_argument =
      (*env)->GetStringUTFChars(env, j_android_argument, &iscopy);
  const char *service_entrypoint =
      (*env)->GetStringUTFChars(env, j_service_entrypoint, &iscopy);
  const char *python_name =
      (*env)->GetStringUTFChars(env, j_python_name, &iscopy);
  const char *python_home =
      (*env)->GetStringUTFChars(env, j_python_home, &iscopy);
  const char *python_path =
      (*env)->GetStringUTFChars(env, j_python_path, &iscopy);
  const char *arg = (*env)->GetStringUTFChars(env, j_arg, &iscopy);

  setenv("ANDROID_PRIVATE", android_private, 1);
  setenv("ANDROID_ARGUMENT", android_argument, 1);
  setenv("ANDROID_APP_PATH", android_argument, 1);
  setenv("ANDROID_ENTRYPOINT", service_entrypoint, 1);
  setenv("PYTHONOPTIMIZE", "2", 1);
  setenv("PYTHON_NAME", python_name, 1);
  setenv("PYTHONHOME", python_home, 1);
  setenv("PYTHONPATH", python_path, 1);
  setenv("PYTHON_SERVICE_ARGUMENT", arg, 1);

  char *argv[] = {"."};
  /* ANDROID_ARGUMENT points to service subdir,
   * so main() will run main.py from this dir
   */
  main(1, argv);
}

#endif
