
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
  if ((file = fopen(filename, "r"))) {
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

  LOGP("Initializing Python for Android");

  // Set a couple of built-in environment vars:
  setenv("P4A_BOOTSTRAP", bootstrap_name, 1);  // env var to identify p4a to applications
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

  // Set additional file-provided environment vars:
  LOGP("Setting additional env vars from p4a_env_vars.txt");
  char env_file_path[256];
  snprintf(env_file_path, sizeof(env_file_path),
           "%s/p4a_env_vars.txt", getenv("ANDROID_UNPACK"));
  FILE *env_file_fd = fopen(env_file_path, "r");
  if (env_file_fd) {
    char* line = NULL;
    size_t len = 0;
    while (getline(&line, &len, env_file_fd) != -1) {
      if (strlen(line) > 0) {
        char *eqsubstr = strstr(line, "=");
        if (eqsubstr) {
          size_t eq_pos = eqsubstr - line;

          // Extract name:
          char env_name[256];
          strncpy(env_name, line, sizeof(env_name));
          env_name[eq_pos] = '\0';

          // Extract value (with line break removed:
          char env_value[256];
          strncpy(env_value, (char*)(line + eq_pos + 1), sizeof(env_value));
          if (strlen(env_value) > 0 &&
              env_value[strlen(env_value)-1] == '\n') {
            env_value[strlen(env_value)-1] = '\0';
            if (strlen(env_value) > 0 &&
                env_value[strlen(env_value)-1] == '\r') {
              // Also remove windows line breaks (\r\n)
              env_value[strlen(env_value)-1] = '\0';
            } 
          }

          // Set value:
          setenv(env_name, env_value, 1);
        }
      }
    }
    fclose(env_file_fd);
  } else {
    LOGP("Warning: no p4a_env_vars.txt found / failed to open!");
  }

  LOGP("Changing directory to the one provided by ANDROID_ARGUMENT");
  LOGP(env_argument);
  chdir(env_argument);

#if PY_MAJOR_VERSION < 3
  Py_NoSiteFlag=1;
#endif

#if PY_MAJOR_VERSION < 3
  Py_SetProgramName("android_python");
#else
  Py_SetProgramName(L"android_python");
#endif

#if PY_MAJOR_VERSION >= 3
  /* our logging module for android
   */
  PyImport_AppendInittab("androidembed", initandroidembed);
#endif

  LOGP("Preparing to initialize python");

  // Set up the python path
  char paths[256];

  char python_bundle_dir[256];
  snprintf(python_bundle_dir, 256,
           "%s/_python_bundle", getenv("ANDROID_UNPACK"));
  if (dir_exists(python_bundle_dir)) {
    LOGP("_python_bundle dir exists");
    snprintf(paths, 256,
            "%s/stdlib.zip:%s/modules",
            python_bundle_dir, python_bundle_dir);

    LOGP("calculated paths to be...");
    LOGP(paths);

    #if PY_MAJOR_VERSION >= 3
        wchar_t *wchar_paths = Py_DecodeLocale(paths, NULL);
        Py_SetPath(wchar_paths);
    #endif

        LOGP("set wchar paths...");
  } else {
      LOGP("_python_bundle does not exist...this not looks good, all python"
           " recipes should have this folder, should we expect a crash soon?");
  }

  Py_Initialize();
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
  PyRun_SimpleString("import io, sys, posix\n");

  char add_site_packages_dir[256];

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
      "class LogFile(io.IOBase):\n"
      "    def __init__(self):\n"
      "        self.__buffer = ''\n"
      "    def readable(self):\n"
      "        return False\n"
      "    def writable(self):\n"
      "        return True\n"
      "    def write(self, s):\n"
      "        s = self.__buffer + s\n"
      "        lines = s.split('\\n')\n"
      "        for l in lines[:-1]:\n"
      "            androidembed.log(l.replace('\\x00', ''))\n"
      "        self.__buffer = lines[-1]\n"
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

  /* Get the entrypoint, search the .pyc then .py
   */
  char *dot = strrchr(env_entrypoint, '.');
  char *ext = ".pyc";
  if (dot <= 0) {
    LOGP("Invalid entrypoint, abort.");
    return -1;
  }
  if (strlen(env_entrypoint) > ENTRYPOINT_MAXLEN - 2) {
      LOGP("Entrypoint path is too long, try increasing ENTRYPOINT_MAXLEN.");
      return -1;
  }
  if (!strcmp(dot, ext)) {
    if (!file_exists(env_entrypoint)) {
      /* fallback on .py */
      strcpy(entrypoint, env_entrypoint);
      entrypoint[strlen(env_entrypoint) - 1] = '\0';
      LOGP(entrypoint);
      if (!file_exists(entrypoint)) {
        LOGP("Entrypoint not found (.pyc, fallback on .py), abort");
        return -1;
      }
    } else {
      strcpy(entrypoint, env_entrypoint);
    }
  } else if (!strcmp(dot, ".py")) {
    /* if .py is passed, check the pyc version first */
    strcpy(entrypoint, env_entrypoint);
    entrypoint[strlen(env_entrypoint) + 1] = '\0';
    entrypoint[strlen(env_entrypoint)] = 'c';
    if (!file_exists(entrypoint)) {
      /* fallback on pure python version */
      if (!file_exists(env_entrypoint)) {
        LOGP("Entrypoint not found (.py), abort.");
        return -1;
      }
      strcpy(entrypoint, env_entrypoint);
    }
  } else {
    LOGP("Entrypoint have an invalid extension (must be .py or .pyc), abort.");
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
  fclose(fd);

  if (PyErr_Occurred() != NULL) {
    ret = 1;
    PyErr_Print(); /* This exits with the right code if SystemExit. */
    PyObject *f = PySys_GetObject("stdout");
    if (PyFile_WriteString("\n", f))
      PyErr_Clear();
  }

  LOGP("Python for android ended.");

  /* Shut down: since regular shutdown causes issues sometimes
     (seems to be an incomplete shutdown breaking next launch)
     we'll use sys.exit(ret) to shutdown, since that one works.

     Reference discussion:

     https://github.com/kivy/kivy/pull/6107#issue-246120816
   */
  char terminatecmd[256];
  snprintf(
    terminatecmd, sizeof(terminatecmd),
    "import sys; sys.exit(%d)\n", ret
  );
  PyRun_SimpleString(terminatecmd);

  /* This should never actually be reached, but we'll leave the clean-up
   * here just to be safe.
   */
#if PY_MAJOR_VERSION < 3
  Py_Finalize();
  LOGP("Unexpectedly reached Py_FinalizeEx(), but was successful.");
#else
  if (Py_FinalizeEx() != 0)  // properly check success on Python 3
    LOGP("Unexpectedly reached Py_FinalizeEx(), and got error!");
  else
    LOGP("Unexpectedly reached Py_FinalizeEx(), but was successful.");
#endif

  return ret;
}

JNIEXPORT void JNICALL Java_org_kivy_android_PythonService_nativeStart(
    JNIEnv *env,
    jobject thiz,
    jstring j_android_private,
    jstring j_android_argument,
    jstring j_service_entrypoint,
    jstring j_python_name,
    jstring j_python_home,
    jstring j_python_path,
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
  setenv("P4A_BOOTSTRAP", bootstrap_name, 1);

  char *argv[] = {"."};
  /* ANDROID_ARGUMENT points to service subdir,
   * so main() will run main.py from this dir
   */
  main(1, argv);
}

#if defined(BOOTSTRAP_NAME_WEBVIEW) || defined(BOOTSTRAP_NAME_SERVICEONLY)
// Webview and service_only uses some more functions:

void Java_org_kivy_android_PythonActivity_nativeSetenv(
                                    JNIEnv* env, jclass cls,
                                    jstring name, jstring value)
//JNIEXPORT void JNICALL SDL_JAVA_INTERFACE(nativeSetenv)(
//                                    JNIEnv* env, jclass cls,
//                                    jstring name, jstring value)
{
    const char *utfname = (*env)->GetStringUTFChars(env, name, NULL);
    const char *utfvalue = (*env)->GetStringUTFChars(env, value, NULL);

    setenv(utfname, utfvalue, 1);

    (*env)->ReleaseStringUTFChars(env, name, utfname);
    (*env)->ReleaseStringUTFChars(env, value, utfvalue);
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
