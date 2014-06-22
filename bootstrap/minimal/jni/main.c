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

struct android_app *g_state = NULL;


static PyObject *androidembed_poll(PyObject *self, PyObject *args) {
    int indent;
    int events;
    struct android_poll_source *source;
    int timeout;

    if (!PyArg_ParseTuple(args, "i", &timeout)) {
        return NULL;
    }

    while ((indent = ALooper_pollAll(
        timeout, NULL, &events, (void **)&source)) >= 0) {

        // Process this event
        if (source != NULL) {
            source->process(g_state, source);
        }

        // Check if we are exiting.
        if (g_state->destroyRequested != 0) {
            Py_RETURN_FALSE;
        }
    }

    Py_RETURN_TRUE;
}

static PyObject *androidembed_log(PyObject *self, PyObject *args) {
    char *logstr = NULL;
    if (!PyArg_ParseTuple(args, "s", &logstr)) {
        return NULL;
    }
    __android_log_print(ANDROID_LOG_INFO, "python", "%s", logstr);
    Py_RETURN_NONE;
}

static PyMethodDef AndroidEmbedMethods[] = {
    {"log", androidembed_log, METH_VARARGS, "Log on android platform"},
    {"poll", androidembed_poll, METH_VARARGS, "Poll the android events"},
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
    g_state = state;

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

    // extract the Makefile, needed for sysconfig
    AAssetManager *am = state->activity->assetManager;
    char bootstrap_fn[512];
    snprintf(bootstrap_fn, 512, "%s/_bootstrap.py", state->activity->internalDataPath);
    if (asset_extract(am, "_bootstrap.py", bootstrap_fn) < 0) {
        LOGW("Unable to extract _bootstrap.py");
        return;
    }

    // run the python bootstrap
    LOGI("Run _bootstrap.py >>>");
    FILE *fhd = fopen(bootstrap_fn, "rb");
    if (fhd == NULL) {
        LOGW("Cannot open _bootstrap.py (errno=%d:%s)", errno, strerror(errno));
        return;
    }
    int ret = PyRun_SimpleFile(fhd, bootstrap_fn);
    fclose(fhd);
    LOGI("Run _bootstrap.py (ret=%d) <<<", ret);

    if (PyErr_Occurred() != NULL) {
        PyErr_Print();
        if (Py_FlushLine())
            PyErr_Clear();
    }

    Py_Finalize();
    LOGI("Python for android ended.");
}
