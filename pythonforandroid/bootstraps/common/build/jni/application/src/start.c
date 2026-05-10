
#define PY_SSIZE_T_CLEAN
#include "Python.h"
#ifndef Py_PYTHON_H
#error Python headers needed to compile C extensions, please install development version of Python.
#else

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <dirent.h>
#include <dlfcn.h>
#include <libgen.h>
#include <jni.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>

#include "bootstrap_name.h"

#ifdef BOOTSTRAP_NAME_SDL2
#include "SDL.h"
#include "SDL_opengles2.h"
#endif

#ifdef BOOTSTRAP_NAME_SDL3
#include "SDL3/SDL.h"
#include "SDL3/SDL_main.h"
#endif

#include "android/log.h"

#define ENTRYPOINT_MAXLEN 128
#define LOG(n, x) __android_log_write(ANDROID_LOG_INFO, (n), (x))
#define P4A_MIN_VER 11
static void LOGP(const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    __android_log_vprint(ANDROID_LOG_INFO, "python", fmt, args);
    va_end(args);
}

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
    return access(filename, F_OK) == 0;
}

static void get_dirname(const char *path, char *dir, size_t size) {
    strncpy(dir, path, size - 1);
    dir[size - 1] = '\0';
    char *last_slash = strrchr(dir, '/');
    if (last_slash) *last_slash = '\0';
    else dir[0] = '\0';
}

// strip "lib" prefix and "bin.so" suffix
static void get_exe_name(const char *filename, char *out, size_t size) {
    size_t len = strlen(filename);
    if (len < 7) {  // too short to be valid
        strncpy(out, filename, size - 1);
        out[size - 1] = '\0';
        return;
    }

    const char *start = filename;
    if (strncmp(filename, "lib", 3) == 0) start += 3;
    size_t start_len = strlen(start);

    if (start_len > 6) {
        size_t copy_len = start_len - 6; // remove "bin.so"
        if (copy_len >= size) copy_len = size - 1;
        strncpy(out, start, copy_len);
        out[copy_len] = '\0';
    } else {
        strncpy(out, start, size - 1);
        out[size - 1] = '\0';
    }
}

char *setup_symlinks() {
    Dl_info info;
    char lib_path[512];
    char *interpreter = NULL;

    if (!(dladdr((void*)setup_symlinks, &info) && info.dli_fname)) {
        LOGP("symlinking failed: failed to get libdir");
        return interpreter;
    }

    strncpy(lib_path, info.dli_fname, sizeof(lib_path) - 1);
    lib_path[sizeof(lib_path) - 1] = '\0';

    char native_lib_dir[512];
    get_dirname(lib_path, native_lib_dir, sizeof(native_lib_dir));
    if (native_lib_dir[0] == '\0') {
        LOGP("symlinking failed: could not determine lib directory");
        return interpreter;
    }

    const char *files_dir_env = getenv("ANDROID_APP_PATH");
    char bin_dir[512];

    snprintf(bin_dir, sizeof(bin_dir), "%s/.bin", files_dir_env);
    if (mkdir(bin_dir, 0755) != 0 && errno != EEXIST) {
        LOGP("Failed to create .bin directory");
        return interpreter;
    }

    DIR *dir = opendir(native_lib_dir);
    if (!dir) {
        LOGP("Failed to open native lib dir");
        return interpreter;
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        const char *name = entry->d_name;
        size_t len = strlen(name);

        if (len < 7) continue; 
        if (strcmp(name + len - 6, "bin.so") != 0) continue; // only bin.so at end

        // get cleaned executable name
        char exe_name[128];
        get_exe_name(name, exe_name, sizeof(exe_name));

        char src[512], dst[512];
        snprintf(src, sizeof(src), "%s/%s", native_lib_dir, name);
        snprintf(dst, sizeof(dst), "%s/%s", bin_dir, exe_name);
  
        // interpreter found?
        if (strcmp(exe_name, "python") == 0) {
          interpreter = strdup(dst);
        }

        struct stat st;
        if (lstat(dst, &st) == 0) continue; // already exists
        if (symlink(src, dst) == 0) {
            LOGP("symlink: %s -> %s", name, exe_name);
        } else {
            LOGP("Symlink failed");
        }
    }

    closedir(dir);

    // append bin_dir to PATH
    const char *old_path = getenv("PATH");
    char new_path[1024];
    if (old_path && strlen(old_path) > 0) {
        snprintf(new_path, sizeof(new_path), "%s:%s", old_path, bin_dir);
    } else {
        snprintf(new_path, sizeof(new_path), "%s", bin_dir);
    }
    setenv("PATH", new_path, 1);

    // set lib path
    setenv("LD_LIBRARY_PATH", native_lib_dir, 1);

  return interpreter;
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

  LOGP("Changing directory to '%s'", env_argument);
  chdir(env_argument);

  char *interpreter = setup_symlinks();

#if PY_MAJOR_VERSION < 3
  Py_NoSiteFlag=1;
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

  #if PY_MAJOR_VERSION >= 3

    #if PY_MINOR_VERSION >= P4A_MIN_VER
      PyConfig config;
      PyConfig_InitPythonConfig(&config);
      config.program_name = L"android_python";
    #else
      Py_SetProgramName(L"android_python");
    #endif

  #else
    Py_SetProgramName("android_python");
  #endif

  if (dir_exists(python_bundle_dir)) {
    LOGP("_python_bundle dir exists");

      #if PY_MAJOR_VERSION >= 3
          #if PY_MINOR_VERSION >= P4A_MIN_VER
            
            wchar_t wchar_zip_path[256];
            wchar_t wchar_modules_path[256];
            swprintf(wchar_zip_path, 256, L"%s/stdlib.zip", python_bundle_dir);
            swprintf(wchar_modules_path, 256, L"%s/modules", python_bundle_dir);

            config.module_search_paths_set = 1;
            PyWideStringList_Append(&config.module_search_paths, wchar_zip_path);
            PyWideStringList_Append(&config.module_search_paths, wchar_modules_path);
        #else
            char paths[512];
            snprintf(paths, 512, "%s/stdlib.zip:%s/modules", python_bundle_dir, python_bundle_dir);
            wchar_t *wchar_paths = Py_DecodeLocale(paths, NULL);
            Py_SetPath(wchar_paths);
        #endif
      
      #endif

    LOGP("set wchar paths...");
  } else {
      LOGP("_python_bundle does not exist...this not looks good, all python"
           " recipes should have this folder, should we expect a crash soon?");
  }

#if PY_MAJOR_VERSION >= 3 && PY_MINOR_VERSION >= P4A_MIN_VER
    PyStatus status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status)) {
        LOGP("Python initialization failed:");
        LOGP(status.err_msg);
    }
#else
    Py_Initialize();
    LOGP("Python initialized using legacy Py_Initialize().");
#endif

  LOGP("Initialized python");

  /* < 3.9 requires explicit GIL initialization
  *  3.9+ PyEval_InitThreads() is deprecated and unnecessary
  */
  #if PY_VERSION_HEX < 0x03090000
    LOGP("Initializing threads (required for Python < 3.9)");
    PyEval_InitThreads();
  #endif

#if PY_MAJOR_VERSION < 3
  initandroidembed();
#endif

  PyRun_SimpleString(
      "import androidembed\n"
      "androidembed.log('testing python print redirection')"

  );

  /* inject our bootstrap code to redirect python stdin/stdout
   * replace sys.path with our path
   */
  PyRun_SimpleString("import io, sys, posix\n");

  char add_site_packages_dir[256];

  if (dir_exists(python_bundle_dir)) {
    snprintf(add_site_packages_dir, 256,
             "sys.path.append('%s/site-packages')",
             python_bundle_dir);

    PyRun_SimpleString("import sys, os\n"
                      "from os.path import realpath, join, dirname");

    char buf_exec[512];
    char buf_argv[512];
    snprintf(buf_exec, sizeof(buf_exec), "sys.executable = '%s'\n", interpreter);
    snprintf(buf_argv, sizeof(buf_argv), "sys.argv = ['%s']\n", interpreter);
    PyRun_SimpleString(buf_exec);
    PyRun_SimpleString(buf_argv);

    PyRun_SimpleString(add_site_packages_dir);
    /* "sys.path.append(join(dirname(realpath(__file__)), 'site-packages'))") */
    PyRun_SimpleString("sys.path = ['.'] + sys.path");
    PyRun_SimpleString("os.environ['PYTHONPATH'] = ':'.join(sys.path)");
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
      "print('Android kivy bootstrap done. __name__ is', __name__)");

#if PY_MAJOR_VERSION < 3
  PyRun_SimpleString("import site; print site.getsitepackages()\n");
#endif

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

#if PY_MAJOR_VERSION < 3
  Py_Finalize();
  LOGP("Unexpectedly reached Py_FinalizeEx(), but was successful.");
#else
  if (Py_FinalizeEx() != 0) {  // properly check success on Python 3
    LOGP("Unexpectedly reached Py_FinalizeEx(), and got error!");
  }
#endif

  exit(ret);
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

  /* This interface could expand with ABI negotiation, callbacks, etc. */
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
