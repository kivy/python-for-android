
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

/* #include <SDL_main.h> */

#include "android/log.h"

/* #include "jniwrapperstuff.h" */


/* AND: I don't know why this include is needed! */
#include "SDL_opengles2.h"

#define LOG(x) __android_log_write(ANDROID_LOG_INFO, "python", (x))

static PyObject *androidembed_log(PyObject *self, PyObject *args) {
    char *logstr = NULL;
    if (!PyArg_ParseTuple(args, "s", &logstr)) {
        return NULL;
    }
    LOG(logstr);
    Py_RETURN_NONE;
}

static PyMethodDef AndroidEmbedMethods[] = {
    {"log", androidembed_log, METH_VARARGS,
     "Log on android platform"},
    {NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3
    static struct PyModuleDef androidembed =
      {
        PyModuleDef_HEAD_INIT,
        "androidembed",
        "",
        -1,
        AndroidEmbedMethods
      };

    PyMODINIT_FUNC initandroidembed(void) {
      return PyModule_Create(&androidembed);
        /* (void) Py_InitModule("androidembed", AndroidEmbedMethods); */
    }
#else
    PyMODINIT_FUNC initandroidembed(void) {
      (void) Py_InitModule("androidembed", AndroidEmbedMethods);
    }
#endif

/* int dir_exists(char* filename) */
/*   /\* Function from http://stackoverflow.com/questions/12510874/how-can-i-check-if-a-directory-exists-on-linux-in-c# *\/ */
/* { */
/*   if (0 != access(filename, F_OK)) { */
/*     if (ENOENT == errno) { */
/*       return 0; */
/*     } */
/*     if (ENOTDIR == errno) { */
/*       return 0; */
/*     } */
/*     return 1; */
/*   } */
/* } */

/* int dir_exists(char* filename) { */
/*   DIR *dip; */
/*   if (dip = opendir(filename)) { */
/*     closedir(filename); */
/*     return 1; */
/*   } */
/*   return 0; */
/* } */

 
int dir_exists(char *filename) {
  struct stat st;
  if (stat(filename, &st) == 0) {
    if (S_ISDIR(st.st_mode))
      return 1;
  }
  return 0;
}


int file_exists(const char * filename)
{
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
    int ret = 0;
    FILE *fd;

 /* AND: Several filepaths are hardcoded here, these must be made
    configurable */
 /* AND: P4A uses env vars...not sure what's best */
    LOG("Initialize Python for Android");
    /* env_argument = "/data/data/org.kivy.android/files"; */
    env_argument = getenv("ANDROID_ARGUMENT");
    setenv("ANDROID_APP_PATH", env_argument, 1);
    
    /* setenv("ANDROID_ARGUMENT", env_argument, 1); */
    /* setenv("ANDROID_PRIVATE", env_argument, 1); */
    /* setenv("ANDROID_APP_PATH", env_argument, 1); */
    /* setenv("PYTHONHOME", env_argument, 1); */
    /* setenv("PYTHONPATH", "/data/data/org.kivy.android/files:/data/data/org.kivy.android/files/lib", 1); */

    /* LOG("AND: Set env vars"); */
    /* LOG(argv[0]); */
    /* LOG("AND: That was argv 0"); */
	//setenv("PYTHONVERBOSE", "2", 1);
    
    LOG("Changing directory to the one provided by ANDROID_ARGUMENT");
    LOG(env_argument);
    chdir(env_argument);

    Py_SetProgramName(L"android_python");

#if PY_MAJOR_VERSION >= 3
    /* our logging module for android
     */
    PyImport_AppendInittab("androidembed", initandroidembed);
#endif
    
    LOG("Preparing to initialize python");
    
    if (dir_exists("crystax_python/")) {
      LOG("crystax_python exists");
        char paths[256];
        snprintf(paths, 256, "%s/crystax_python/stdlib.zip:%s/crystax_python/modules", env_argument, env_argument);
        /* snprintf(paths, 256, "%s/stdlib.zip:%s/modules", env_argument, env_argument); */
        LOG("calculated paths to be...");
        LOG(paths);
        
#if PY_MAJOR_VERSION >= 3
        wchar_t* wchar_paths = Py_DecodeLocale(paths, NULL);
        Py_SetPath(wchar_paths);
#else
        char* wchar_paths = paths;
        LOG("Can't Py_SetPath in python2, so crystax python2 doesn't work yet");
        exit(1);
#endif
     
        LOG("set wchar paths...");
    } else { LOG("crystax_python does not exist");}

    Py_Initialize();
    
#if PY_MAJOR_VERSION < 3
    PySys_SetArgv(argc, argv);
#endif
    
    LOG("Initialized python");

    /* ensure threads will work.
     */
    LOG("AND: Init threads");
    PyEval_InitThreads();
    

#if PY_MAJOR_VERSION < 3
    initandroidembed();
#endif

    PyRun_SimpleString("import androidembed\nandroidembed.log('testing python print redirection')");
    
    /* inject our bootstrap code to redirect python stdin/stdout
     * replace sys.path with our path
     */
    PyRun_SimpleString("import sys, posix\n");
    if (dir_exists("lib")) {
        /* If we built our own python, set up the paths correctly */
      LOG("Setting up python from ANDROID_PRIVATE");
        PyRun_SimpleString(
            "private = posix.environ['ANDROID_PRIVATE']\n" \
            "argument = posix.environ['ANDROID_ARGUMENT']\n" \
            "sys.path[:] = [ \n" \
            "    private + '/lib/python27.zip', \n" \
            "    private + '/lib/python2.7/', \n" \
            "    private + '/lib/python2.7/lib-dynload/', \n" \
            "    private + '/lib/python2.7/site-packages/', \n" \
            "    argument ]\n");
    } 

    if (dir_exists("crystax_python")) {
      char add_site_packages_dir[256];
      snprintf(add_site_packages_dir, 256, "sys.path.append('%s/crystax_python/site-packages')", 
               env_argument);
      
      PyRun_SimpleString(
          "import sys\n"             \
          "sys.argv = ['notaninterpreterreally']\n"  \
          "from os.path import realpath, join, dirname");
      PyRun_SimpleString(add_site_packages_dir);
      /* "sys.path.append(join(dirname(realpath(__file__)), 'site-packages'))") */
      PyRun_SimpleString("sys.path = ['.'] + sys.path");
    }
    
    PyRun_SimpleString(
        "class LogFile(object):\n" \
        "    def __init__(self):\n" \
        "        self.buffer = ''\n" \
        "    def write(self, s):\n" \
        "        s = self.buffer + s\n" \
        "        lines = s.split(\"\\n\")\n" \
        "        for l in lines[:-1]:\n" \
        "            androidembed.log(l)\n" \
        "        self.buffer = lines[-1]\n" \
        "    def flush(self):\n" \
        "        return\n" \
        "sys.stdout = sys.stderr = LogFile()\n" \
		"print('Android path', sys.path)\n" \
        "import os\n" \
        "print('os.environ is', os.environ)\n" \
        "print('Android kivy bootstrap done. __name__ is', __name__)");

    /* PyRun_SimpleString( */
    /*     "import sys, posix\n" \ */
    /*     "private = posix.environ['ANDROID_PRIVATE']\n" \ */
    /*     "argument = posix.environ['ANDROID_ARGUMENT']\n" \ */
    /*     "sys.path[:] = [ \n" \ */
	/* 	"    private + '/lib/python27.zip', \n" \ */
	/* 	"    private + '/lib/python2.7/', \n" \ */
	/* 	"    private + '/lib/python2.7/lib-dynload/', \n" \ */
	/* 	"    private + '/lib/python2.7/site-packages/', \n" \ */
	/* 	"    argument ]\n" \ */
    /*     "import androidembed\n" \ */
    /*     "class LogFile(object):\n" \ */
    /*     "    def __init__(self):\n" \ */
    /*     "        self.buffer = ''\n" \ */
    /*     "    def write(self, s):\n" \ */
    /*     "        s = self.buffer + s\n" \ */
    /*     "        lines = s.split(\"\\n\")\n" \ */
    /*     "        for l in lines[:-1]:\n" \ */
    /*     "            androidembed.log(l)\n" \ */
    /*     "        self.buffer = lines[-1]\n" \ */
    /*     "    def flush(self):\n" \ */
    /*     "        return\n" \ */
    /*     "sys.stdout = sys.stderr = LogFile()\n" \ */
	/* 	"import site; print site.getsitepackages()\n"\ */
	/* 	"print 'Android path', sys.path\n" \ */
    /*     "print 'Android kivy bootstrap done. __name__ is', __name__"); */

    LOG("AND: Ran string");

    /* run it !
     */
    LOG("Run user program, change dir and execute main.py");

	/* search the initial main.py
	 */
	char *main_py = "main.pyo";
	if ( file_exists(main_py) == 0 ) {
		if ( file_exists("main.py") )
			main_py = "main.py";
		else
			main_py = NULL;
	}

	if ( main_py == NULL ) {
		LOG("No main.pyo / main.py found.");
		return -1;
	}

    fd = fopen(main_py, "r");
    if ( fd == NULL ) {
        LOG("Open the main.py(o) failed");
        return -1;
    }

    /* run python !
     */
    ret = PyRun_SimpleFile(fd, main_py);

    if (PyErr_Occurred() != NULL) {
        ret = 1;
        PyErr_Print(); /* This exits with the right code if SystemExit. */
        PyObject *f = PySys_GetObject("stdout");
        if (PyFile_WriteString("\n", f))  /* python2 used Py_FlushLine, but this no longer exists */
          PyErr_Clear();
    }

    /* close everything
     */
	Py_Finalize();
    fclose(fd);

    LOG("Python for android ended.");
    return ret;
}

JNIEXPORT void JNICALL Java_org_kivy_android_PythonService_nativeStart ( JNIEnv*  env, jobject thiz, 
                                                                         jstring j_android_private, 
                                                                         jstring j_android_argument, 
                                                                         jstring j_python_home, 
                                                                         jstring j_python_path, 
                                                                         jstring j_arg ) 
{
    jboolean iscopy; 
    const char *android_private = (*env)->GetStringUTFChars(env, j_android_private, &iscopy); 
    const char *android_argument = (*env)->GetStringUTFChars(env, j_android_argument, &iscopy); 
    const char *python_home = (*env)->GetStringUTFChars(env, j_python_home, &iscopy); 
    const char *python_path = (*env)->GetStringUTFChars(env, j_python_path, &iscopy); 
    const char *arg = (*env)->GetStringUTFChars(env, j_arg, &iscopy); 

    setenv("ANDROID_PRIVATE", android_private, 1); 
    setenv("ANDROID_ARGUMENT", android_argument, 1); 
    setenv("PYTHONOPTIMIZE", "2", 1); 
    setenv("PYTHONHOME", python_home, 1); 
    setenv("PYTHONPATH", python_path, 1); 
    setenv("PYTHON_SERVICE_ARGUMENT", arg, 1); 

    char *argv[] = { "service" }; 
    /* ANDROID_ARGUMENT points to service subdir, 
     * so main() will run main.py from this dir 
     */
    main(1, argv); 
}

#endif
