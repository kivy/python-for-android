#ifdef ANDROID

#include <unistd.h>
#include <stdlib.h>
#include <jni.h>
#include <android/log.h>
#include "SDL_thread.h"
#include "SDL_main.h"

/* JNI-C wrapper stuff */

#ifdef __cplusplus
#define C_LINKAGE "C"
#else
#define C_LINKAGE
#endif


#ifndef SDL_JAVA_PACKAGE_PATH
#error You have to define SDL_JAVA_PACKAGE_PATH to your package path with dots replaced with underscores, for example "com_example_SanAngeles"
#endif
#define JAVA_EXPORT_NAME2(name,package) Java_##package##_##name
#define JAVA_EXPORT_NAME1(name,package) JAVA_EXPORT_NAME2(name,package)
#define JAVA_EXPORT_NAME(name) JAVA_EXPORT_NAME1(name,SDL_JAVA_PACKAGE_PATH)


static int isSdcardUsed = 0;

extern C_LINKAGE void
JAVA_EXPORT_NAME(SDLSurfaceView_nativeInit) ( JNIEnv*  env, jobject thiz )
{
	int argc = 1;
	char * argv[] = { "sdl" };
	main( argc, argv );
};

extern C_LINKAGE void
JAVA_EXPORT_NAME(SDLSurfaceView_nativeIsSdcardUsed) ( JNIEnv*  env, jobject thiz, jint flag )
{
	isSdcardUsed = flag;
}

extern C_LINKAGE void
JAVA_EXPORT_NAME(SDLSurfaceView_nativeSetEnv) ( JNIEnv*  env, jobject thiz, jstring j_name, jstring j_value )
{
    jboolean iscopy;
    const char *name = (*env)->GetStringUTFChars(env, j_name, &iscopy);
    const char *value = (*env)->GetStringUTFChars(env, j_value, &iscopy);
    setenv(name, value, 1);
    (*env)->ReleaseStringUTFChars(env, j_name, name);
    (*env)->ReleaseStringUTFChars(env, j_value, value);
}

#undef JAVA_EXPORT_NAME
#undef JAVA_EXPORT_NAME1
#undef JAVA_EXPORT_NAME2
#undef C_LINKAGE

#endif
