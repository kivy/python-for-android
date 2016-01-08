#include <jni.h>
#include <stdio.h>
#include <android/log.h>
#include <string.h>
#include <stdlib.h>

#include "config.h"

#define aassert(x) { if (!x) { __android_log_print(ANDROID_LOG_ERROR, "android_jni", "Assertion failed. %s:%d", __FILE__, __LINE__); abort(); }}
#define PUSH_FRAME { (*env)->PushLocalFrame(env, 16); }
#define POP_FRAME  { (*env)->PopLocalFrame(env, NULL); }

void android_billing_service_start() {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, JNI_NAMESPACE "/PythonActivity");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "billingServiceStart", "()V");
        aassert(mid);
    }

    PUSH_FRAME;
    (*env)->CallStaticVoidMethod(env, cls, mid);
    POP_FRAME;
}

void android_billing_service_stop() {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, JNI_NAMESPACE "/PythonActivity");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "billingServiceStop", "()V");
        aassert(mid);
    }

    PUSH_FRAME;
    (*env)->CallStaticVoidMethod(env, cls, mid);
    POP_FRAME;
}

void android_billing_buy(char *sku) {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, JNI_NAMESPACE "/PythonActivity");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "billingBuy", "(Ljava/lang/String;)V");
        aassert(mid);
    }

    PUSH_FRAME;

    (*env)->CallStaticVoidMethod(
        env, cls, mid,
        (*env)->NewStringUTF(env, sku)
        );

    POP_FRAME;
}

char *android_billing_get_purchased_items() {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;
    jobject jreading;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, JNI_NAMESPACE "/PythonActivity");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "billingGetPurchasedItems", "()Ljava/lang/String;");
        aassert(mid);
    }

    PUSH_FRAME;
    jreading = (*env)->CallStaticObjectMethod(env, cls, mid);
    const char * reading = (*env)->GetStringUTFChars(env, jreading, 0);
    POP_FRAME;

    return reading;
}

char *android_billing_get_pending_message() {
    static JNIEnv *env = NULL;
    static jclass *cls = NULL;
    static jmethodID mid = NULL;
    jobject jreading;

    if (env == NULL) {
        env = SDL_ANDROID_GetJNIEnv();
        aassert(env);
        cls = (*env)->FindClass(env, JNI_NAMESPACE "/PythonActivity");
        aassert(cls);
        mid = (*env)->GetStaticMethodID(env, cls, "billingGetPendingMessage", "()Ljava/lang/String;");
        aassert(mid);
    }

    PUSH_FRAME;
    jreading = (*env)->CallStaticObjectMethod(env, cls, mid);
    const char * reading = (*env)->GetStringUTFChars(env, jreading, 0);
    POP_FRAME;

    return reading;
}

