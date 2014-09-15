#include <errno.h>
#include <android/log.h>

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
