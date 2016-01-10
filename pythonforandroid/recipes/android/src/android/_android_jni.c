#include <jni.h>
#include <stdio.h>
#include <android/log.h>
#include <string.h>
#include <stdlib.h>

#include "config.h"

#define aassert(x) { if (!x) { __android_log_print(ANDROID_LOG_ERROR, "android_jni", "Assertion failed. %s:%d", __FILE__, __LINE__); abort(); }}
#define PUSH_FRAME { (*env)->PushLocalFrame(env, 16); }
#define POP_FRAME  { (*env)->PopLocalFrame(env, NULL); }

void android_vibrate(double seconds) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/Hardware");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "vibrate", "(D)V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        (jdouble) seconds);
}

void android_accelerometer_enable(int enable) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/Hardware");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "accelerometerEnable", "(Z)V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        (jboolean) enable);
}

void android_wifi_scanner_enable(void){
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/Hardware");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "enableWifiScanner", "()V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(env, cls, mid);
}


char * android_wifi_scan() {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;
    jobject jreading;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/Hardware");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "scanWifi", "()Ljava/lang/String;");
        aassert(mid);
    }

    PUSH_FRAME;
    jreading = (*env)->CallStaticObjectMethod(env, cls, mid);
    const char * reading = (*env)->GetStringUTFChars(env, jreading, 0);
    POP_FRAME;

    return reading;
}

void android_accelerometer_reading(float *values) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;
    jobject jvalues;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/Hardware");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "accelerometerReading", "()[F");
        aassert(mid);
    }

    PUSH_FRAME;

    jvalues = (*env)->CallStaticObjectMethod(env, cls, mid);
    (*env)->GetFloatArrayRegion(env, jvalues, 0, 3, values);

    POP_FRAME;
}

int android_get_dpi(void) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/Hardware");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "getDPI", "()I");
        aassert(mid);
    }

    return (*env)->CallStaticIntMethod(env, cls, mid);
}

void android_show_keyboard(int input_type) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/Hardware");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "showKeyboard", "(I)V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(env, cls, mid, (jint) input_type);
}

void android_hide_keyboard(void) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/Hardware");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "hideKeyboard", "()V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(env, cls, mid);
}

char* BUILD_MANUFACTURER = NULL;
char* BUILD_MODEL = NULL;
char* BUILD_PRODUCT = NULL;
char* BUILD_VERSION_RELEASE = NULL;

void android_get_buildinfo() {
    static JNIEnv *env = NULL;

    if (env == NULL) {
        jclass *cls = NULL;
        jfieldID fid;
        jstring sval;

        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);

        cls = (*env)->FindClass(env, "android/os/Build");

        fid = (*env)->GetStaticFieldID(env, cls, "MANUFACTURER", "Ljava/lang/String;");
        sval = (jstring) (*env)->GetStaticObjectField(env, cls, fid);
        BUILD_MANUFACTURER = (*env)->GetStringUTFChars(env, sval, 0);

        fid = (*env)->GetStaticFieldID(env, cls, "MODEL", "Ljava/lang/String;");
        sval = (jstring) (*env)->GetStaticObjectField(env, cls, fid);
        BUILD_MODEL = (*env)->GetStringUTFChars(env, sval, 0);

        fid = (*env)->GetStaticFieldID(env, cls, "PRODUCT", "Ljava/lang/String;");
        sval = (jstring) (*env)->GetStaticObjectField(env, cls, fid);
        BUILD_PRODUCT = (*env)->GetStringUTFChars(env, sval, 0);

        cls = (*env)->FindClass(env, "android/os/Build$VERSION");

        fid = (*env)->GetStaticFieldID(env, cls, "RELEASE", "Ljava/lang/String;");
        sval = (jstring) (*env)->GetStaticObjectField(env, cls, fid);
        BUILD_VERSION_RELEASE = (*env)->GetStringUTFChars(env, sval, 0);
    }
}

#if IS_PYGAME
void android_activate_input(void) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/SDLSurfaceView");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "activateInput", "()V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(env, cls, mid);
}

int android_checkstop(void) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/SDLSurfaceView");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "checkStop", "()I");
        aassert(mid);
    }

    return (*env)->CallStaticIntMethod(env, cls, mid);
}

void android_ackstop(void) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/SDLSurfaceView");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "ackStop", "()I");
        aassert(mid);
    }

    (*env)->CallStaticIntMethod(env, cls, mid);
}

void android_action_send(char *mimeType, char *filename, char *subject, char *text, char *chooser_title) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/Action");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "send",
			"(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V");
        aassert(mid);
    }

	jstring j_mimeType = (*env)->NewStringUTF(env, mimeType);
	jstring j_filename = NULL;
	jstring j_subject = NULL;
	jstring j_text = NULL;
	jstring j_chooser_title = NULL;
	if ( filename != NULL )
		j_filename = (*env)->NewStringUTF(env, filename);
	if ( subject != NULL )
		j_subject = (*env)->NewStringUTF(env, subject);
	if ( text != NULL )
		j_text = (*env)->NewStringUTF(env, text);
	if ( chooser_title != NULL )
		j_chooser_title = (*env)->NewStringUTF(env, text);

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
		j_mimeType, j_filename, j_subject, j_text,
		j_chooser_title);
}

void android_open_url(char *url) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/SDLSurfaceView");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "openUrl", "(Ljava/lang/String;)V");
        aassert(mid);
    }

    PUSH_FRAME;

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        (*env)->NewStringUTF(env, url)
        );

    POP_FRAME;
}
#endif // IS_PYGAME

void android_start_service(char *title, char *description, char *arg) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, JNI_NAMESPACE "/PythonActivity");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "start_service",
                                       "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V");
        aassert(mid);
    }

    jstring j_title = NULL;
    jstring j_description = NULL;
    jstring j_arg = NULL;
    if ( title != 0 )
            j_title = (*env)->NewStringUTF(env, title);
    if ( description != 0 )
            j_description = (*env)->NewStringUTF(env, description);
    if ( arg != 0 )
            j_arg = (*env)->NewStringUTF(env, arg);

    (*env)->CallStaticVoidMethod(env, cls, mid, j_title, j_description, j_arg);
}

void android_stop_service() {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        cls = (*env)->FindClass(env, JNI_NAMESPACE "/PythonActivity");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "stop_service", "()V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(env, cls, mid);
}
