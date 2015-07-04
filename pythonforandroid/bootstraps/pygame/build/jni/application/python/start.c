#define PY_SSIZE_T_CLEAN
#include "Python.h"
#ifndef Py_PYTHON_H
    #error Python headers needed to compile C extensions, please install development version of Python.
#else

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <jni.h>
#include "SDL.h"
#include "android/log.h"
#include "jniwrapperstuff.h"

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

PyMODINIT_FUNC initandroidembed(void) {
    (void) Py_InitModule("androidembed", AndroidEmbedMethods);
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

int main(int argc, char **argv) {

    char *env_argument = NULL;
    int ret = 0;
    FILE *fd;

    LOG("Initialize Python for Android");
    env_argument = getenv("ANDROID_ARGUMENT");
    setenv("ANDROID_APP_PATH", env_argument, 1);
	//setenv("PYTHONVERBOSE", "2", 1);
    Py_SetProgramName(argv[0]);
    Py_Initialize();
    PySys_SetArgv(argc, argv);

    /* ensure threads will work.
     */
    PyEval_InitThreads();

    /* our logging module for android
     */
    initandroidembed();

    /* inject our bootstrap code to redirect python stdin/stdout
     * replace sys.path with our path
     */
    PyRun_SimpleString(
        "import sys, posix\n" \
        "private = posix.environ['ANDROID_PRIVATE']\n" \
        "argument = posix.environ['ANDROID_ARGUMENT']\n" \
        "sys.path[:] = [ \n" \
		"    private + '/lib/python27.zip', \n" \
		"    private + '/lib/python2.7/', \n" \
		"    private + '/lib/python2.7/lib-dynload/', \n" \
		"    private + '/lib/python2.7/site-packages/', \n" \
		"    argument ]\n" \
        "import androidembed\n" \
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
		"import site; print site.getsitepackages()\n"\
		"print 'Android path', sys.path\n" \
        "print 'Android kivy bootstrap done. __name__ is', __name__");

    /* run it !
     */
    LOG("Run user program, change dir and execute main.py");
    chdir(env_argument);

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
        if (Py_FlushLine())
			PyErr_Clear();
    }

    /* close everything
     */
	Py_Finalize();
    fclose(fd);

    LOG("Python for android ended.");
    return ret;
}

JNIEXPORT void JNICALL JAVA_EXPORT_NAME(PythonService_nativeStart) ( JNIEnv*  env, jobject thiz,
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
