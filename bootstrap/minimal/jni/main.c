#include <jni.h>
#include <android_native_app_glue.h>

#include "utils.c"


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
    setenv("ANDROID_APK_FN", str, 1);

    methodID = (*env)->GetMethodID(env, clazz, "getApplicationInfo", "()Landroid/content/pm/ApplicationInfo;");
    jobject appInfo = (*env)->CallObjectMethod(env, activity->clazz, methodID);
    jfieldID fieldID = (*env)->GetFieldID(env,
        (*env)->GetObjectClass(env, appInfo), "nativeLibraryDir", "Ljava/lang/String;");
    result = (*env)->GetObjectField(env, appInfo, fieldID);
    str = (*env)->GetStringUTFChars(env, (jstring)result, &isCopy);
    LOGI("Looked up library code path: %s", str);
    setenv("ANDROID_LIB_PATH", str, 1);

    (*activity->vm)->DetachCurrentThread(activity->vm);

    // set some envs
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

    // pass a module name as argument: _bootstrap.py use it as the main module
    int argc;
    char * argv[2];
    argc = 2;
    argv[0] = "_bootstrap.py";
    argv[1] = "main";

    PySys_SetArgv(argc, argv);

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
