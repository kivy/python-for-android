#include <jni.h>
#include <errno.h>
#include <android/log.h>
#include <android_native_app_glue.h>

#define LOGI(...) ((void)__android_log_print(ANDROID_LOG_INFO, "python", __VA_ARGS__))
#define LOGW(...) ((void)__android_log_print(ANDROID_LOG_WARN, "python", __VA_ARGS__))

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#ifndef Py_PYTHON_H
    #error Python headers needed to compile C extensions, please install development version of Python.
#endif

static PyObject *androidembed_log(PyObject *self, PyObject *args) {
    char *logstr = NULL;
    if (!PyArg_ParseTuple(args, "s", &logstr)) {
        return NULL;
    }
    __android_log_print(ANDROID_LOG_INFO, "python", "%s", logstr);
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

int asset_extract(AAssetManager *am, char *src_file, char *dst_file) {
    FILE *fhd = fopen(dst_file, "wb");
    if (fhd == NULL) {
        LOGW("Unable to open descriptor for %s (errno=%d:%s)",
            dst_file, errno, strerror(errno));
        return -1;
    }

    AAsset *asset = AAssetManager_open(am, src_file, AASSET_MODE_BUFFER);
    if (asset == NULL) {
        LOGW("Unable to open asset %s", src_file);
        return -1;
    }

    off_t l = AAsset_getLength(asset);
    fwrite(AAsset_getBuffer(asset),l, 1, fhd);
    fclose(fhd);
    AAsset_close(asset);

    return 0;
}

void android_main(struct android_app* state) {
    app_dummy();
    LOGI("Starting minimal bootstrap.");

    char *env_argument = NULL;
    int fd = -1;

    LOGI("Initialize Python for Android");
    //env_argument = getenv("ANDROID_ARGUMENT");
    //setenv("ANDROID_APP_PATH", env_argument, 1);
	//setenv("PYTHONVERBOSE", "2", 1);
    Py_SetProgramName("python-android");
    Py_Initialize();
    //PySys_SetArgv(argc, argv);

    // ensure threads will work.
    PyEval_InitThreads();

    // our logging module for android
    initandroidembed();

    // get the APK filename, and set it to ANDROID_APK_FN
    ANativeActivity* activity = state->activity;
    JNIEnv* env = NULL;
    (*activity->vm)->AttachCurrentThread(activity->vm, &env, 0);
    jclass clazz = (*env)->GetObjectClass(env, activity->clazz);
    jmethodID methodID = (*env)->GetMethodID(env, clazz, "getPackageCodePath", "()Ljava/lang/String;");
    jobject result = (*env)->CallObjectMethod(env, activity->clazz, methodID);
    const char* str;
    jboolean isCopy;
    str = (*env)->GetStringUTFChars(env, (jstring)result, &isCopy);
    LOGI("Looked up package code path: %s", str);
    (*activity->vm)->DetachCurrentThread(activity->vm);

    // set some envs
    setenv("ANDROID_APK_FN", str, 1);
    setenv("ANDROID_INTERNAL_DATA_PATH", state->activity->internalDataPath, 1);
    setenv("ANDROID_EXTERNAL_DATA_PATH", state->activity->externalDataPath, 1);
    LOGI("Internal data path is: %s", state->activity->internalDataPath);
    LOGI("External data path is: %s", state->activity->externalDataPath);

    // inject our bootstrap code to redirect python stdin/stdout
    PyRun_SimpleString(
        "import sys, androidembed\n" \
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
        "sys.stdout = sys.stderr = LogFile()\n");

    // let python knows where the python2.7 library is within the APK
    PyRun_SimpleString(
        "import sys, posix;" \
        "lib_path = '{}/assets/lib/python2.7/'.format(" \
        "           posix.environ['ANDROID_APK_FN'])\n" \
        "sys.path[:] = [lib_path, '{}/site-packages'.format(lib_path)]\n" \
        "import os; from os.path import exists, join\n" \
        "config_path = join(posix.environ['ANDROID_INTERNAL_DATA_PATH'], 'python2.7', 'config')\n" \
        "if not exists(config_path): os.makedirs(config_path)\n" \
        "import sysconfig\n" \
        "sysconfig._get_makefile_filename = lambda: '{}/Makefile'.format(config_path)\n" \
        "sysconfig.get_config_h_filename = lambda: '{}/pyconfig.h'.format(config_path)\n" \
        );

    // extract the Makefile, needed for sysconfig
    AAssetManager *am = state->activity->assetManager;
    char dest_fn[512];

    snprintf(dest_fn, 512, "%s/python2.7/config/Makefile", state->activity->internalDataPath);
    if (asset_extract(am, "lib/python2.7/config/Makefile", dest_fn) < 0)
        return;

    snprintf(dest_fn, 512, "%s/python2.7/config/pyconfig.h", state->activity->internalDataPath);
    if (asset_extract(am, "include/python2.7/pyconfig.h", dest_fn) < 0)
        return;

    // test import site
    PyRun_SimpleString(
		"import site; print site.getsitepackages()\n"\
		"print 'Android path', sys.path\n" \
        "print 'Android bootstrap done. __name__ is', __name__");

    /* run it !
     */
    LOGI("Extract main.py from assets");
    char main_fn[512];
    snprintf(main_fn, 512, "%s/main.pyo", state->activity->internalDataPath);
    if (asset_extract(am, "main.pyo", main_fn) < 0)
        return;

    /* run python !
     */
    LOGI("Run main.py >>>");
    FILE *fhd = fopen(main_fn, "rb");
    if (fhd == NULL) {
        LOGW("Cannot open main.pyo (errno=%d:%s)", errno, strerror(errno));
        return;
    }
    int ret = PyRun_SimpleFile(fhd, main_fn);
    fclose(fhd);
    LOGI("Run main.py (ret=%d) <<<", ret);

    if (PyErr_Occurred() != NULL) {
        LOGW("An error occured.");
        PyErr_Print(); /* This exits with the right code if SystemExit. */
        if (Py_FlushLine())
			PyErr_Clear();
    }

    /* close everything
     */
	Py_Finalize();

    LOGW("Python for android ended.");
}
