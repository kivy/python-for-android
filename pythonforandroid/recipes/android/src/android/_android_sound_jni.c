#include <jni.h>
#include <stdio.h>
#include <android/log.h>
#include <string.h>

JNIEnv *SDL_ANDROID_GetJNIEnv();

#define aassert(x) { if (!x) { __android_log_print(ANDROID_LOG_ERROR, "android_sound_jni", "Assertion failed. %s:%d", __FILE__, __LINE__); abort(); }}
#define PUSH_FRAME { (*env)->PushLocalFrame(env, 16); }
#define POP_FRAME  { (*env)->PopLocalFrame(env, NULL); }


void android_sound_queue(int channel, char *filename, char *real_fn, long long base, long long length) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "queue", "(ILjava/lang/String;Ljava/lang/String;JJ)V");
        aassert(mid);
    }

    PUSH_FRAME;

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        channel,
        (*env)->NewStringUTF(env, filename),
        (*env)->NewStringUTF(env, real_fn),
        (jlong) base,
        (jlong) length);

    POP_FRAME;
}

void android_sound_play(int channel, char *filename, char *real_fn, long long base, long long length) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "play", "(ILjava/lang/String;Ljava/lang/String;JJ)V");
        aassert(mid);
    }

    PUSH_FRAME;

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        channel,
        (*env)->NewStringUTF(env, filename),
        (*env)->NewStringUTF(env, real_fn),
        (jlong) base,
        (jlong) length);

    POP_FRAME;
}

void android_sound_seek(int channel, float position){
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "seek", "(IF)V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        channel,
        (jfloat) position);
}

void android_sound_stop(int channel) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "stop", "(I)V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        channel);
}

void android_sound_dequeue(int channel) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "dequeue", "(I)V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        channel);
}

int android_sound_queue_depth(int channel) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "queue_depth", "(I)I");
        aassert(mid);
    }

    (*env)->CallStaticIntMethod(
        env, cls, mid,
        channel);
}

void android_sound_playing_name(int channel, char *buf, int buflen) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    jobject s = NULL;
    char *jbuf;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "playing_name", "(I)Ljava/lang/String;");
        aassert(mid);
    }

    PUSH_FRAME;

    s = (*env)->CallStaticObjectMethod(
        env, cls, mid,
        channel);

    jbuf = (*env)->GetStringUTFChars(env, s, NULL);
    strncpy(buf, jbuf, buflen);
    (*env)->ReleaseStringUTFChars(env, s, jbuf);

    POP_FRAME;
}

void android_sound_set_volume(int channel, float value) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "set_volume", "(IF)V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        channel,
        (jfloat) value);
}

void android_sound_set_secondary_volume(int channel, float value) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "set_secondary_volume", "(IF)V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        channel,
        (jfloat) value);
}

void android_sound_set_pan(int channel, float value) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "set_pan", "(IF)V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        channel,
        (jfloat) value);
}

void android_sound_pause(int channel) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "pause", "(I)V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        channel);
}

void android_sound_unpause(int channel) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "unpause", "(I)V");
        aassert(mid);
    }

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        channel);
}

int android_sound_get_pos(int channel) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "get_pos", "(I)I");
        aassert(mid);
    }

    return (*env)->CallStaticIntMethod(
        env, cls, mid,
        channel);
}

int android_sound_get_length(int channel) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, "org/renpy/android/RenPySound");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "get_length", "(I)I");
        aassert(mid);
    }

    return (*env)->CallStaticIntMethod(
        env, cls, mid,
        channel);
}
