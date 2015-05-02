/*
    SDL - Simple DirectMedia Layer
    Copyright (C) 1997-2009 Sam Lantinga

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

    Sam Lantinga
    slouken@libsdl.org

    This file written by Ryan C. Gordon (icculus@icculus.org)
*/
#include "SDL_config.h"
#include "SDL_version.h"

#include "SDL_rwops.h"
#include "SDL_timer.h"
#include "SDL_audio.h"
#include "../SDL_audiomem.h"
#include "../SDL_audio_c.h"
#include "../SDL_audiodev_c.h"
#include "SDL_androidaudio.h"
#include "SDL_mutex.h"
#include "SDL_thread.h"
#include <jni.h>
#include <android/log.h>
#include <string.h> // for memset()
#include <pthread.h>

#define _THIS	SDL_AudioDevice *this

/* Audio driver functions */

static void ANDROIDAUD_WaitAudio(_THIS);
static void ANDROIDAUD_PlayAudio(_THIS);
static Uint8 *ANDROIDAUD_GetAudioBuf(_THIS);
static void ANDROIDAUD_CloseAudio(_THIS);
static void ANDROIDAUD_ThreadInit(_THIS);
static void ANDROIDAUD_ThreadDeinit(_THIS);

#if SDL_VERSION_ATLEAST(1,3,0)

static int ANDROIDAUD_OpenAudio(_THIS, const char *devname, int iscapture);

static void ANDROIDAUD_DeleteDevice()
{
}

static int ANDROIDAUD_CreateDevice(SDL_AudioDriverImpl * impl)
{

	/* Set the function pointers */
	impl->OpenDevice = ANDROIDAUD_OpenAudio;
	impl->WaitDevice = ANDROIDAUD_WaitAudio;
	impl->PlayDevice = ANDROIDAUD_PlayAudio;
	impl->GetDeviceBuf = ANDROIDAUD_GetAudioBuf;
	impl->CloseDevice = ANDROIDAUD_CloseAudio;
	impl->ThreadInit = ANDROIDAUD_ThreadInit;
	impl->WaitDone = ANDROIDAUD_ThreadDeinit;
	impl->Deinitialize = ANDROIDAUD_DeleteDevice;
	impl->OnlyHasDefaultOutputDevice = 1;

	return 1;
}

AudioBootStrap ANDROIDAUD_bootstrap = {
	"android", "SDL Android audio driver",
	ANDROIDAUD_CreateDevice, 0
};

#else

static int ANDROIDAUD_OpenAudio(_THIS, SDL_AudioSpec *spec);

static int ANDROIDAUD_Available(void)
{
	return(1);
}

static void ANDROIDAUD_DeleteDevice(SDL_AudioDevice *device)
{
	SDL_free(device);
}

static SDL_AudioDevice *ANDROIDAUD_CreateDevice(int devindex)
{
	SDL_AudioDevice *this;

	/* Initialize all variables that we clean on shutdown */
	this = (SDL_AudioDevice *)SDL_malloc(sizeof(SDL_AudioDevice));
	if ( this ) {
		SDL_memset(this, 0, (sizeof *this));
		this->hidden = NULL;
	} else {
		SDL_OutOfMemory();
		return(0);
	}

	/* Set the function pointers */
	this->OpenAudio = ANDROIDAUD_OpenAudio;
	this->WaitAudio = ANDROIDAUD_WaitAudio;
	this->PlayAudio = ANDROIDAUD_PlayAudio;
	this->GetAudioBuf = ANDROIDAUD_GetAudioBuf;
	this->CloseAudio = ANDROIDAUD_CloseAudio;
	this->ThreadInit = ANDROIDAUD_ThreadInit;
	this->WaitDone = ANDROIDAUD_ThreadDeinit;
	this->free = ANDROIDAUD_DeleteDevice;

	return this;
}

AudioBootStrap ANDROIDAUD_bootstrap = {
	"android", "SDL Android audio driver",
	ANDROIDAUD_Available, ANDROIDAUD_CreateDevice
};

#endif


static unsigned char * audioBuffer = NULL;
static size_t audioBufferSize = 0;

// Extremely wicked JNI environment to call Java functions from C code
static jbyteArray audioBufferJNI = NULL;
static JavaVM *jniVM = NULL;
static jobject JavaAudioThread = NULL;
static jmethodID JavaInitAudio = NULL;
static jmethodID JavaDeinitAudio = NULL;


static Uint8 *ANDROIDAUD_GetAudioBuf(_THIS)
{
	return(audioBuffer);
}


#if SDL_VERSION_ATLEAST(1,3,0)
static int ANDROIDAUD_OpenAudio (_THIS, const char *devname, int iscapture)
{
	SDL_AudioSpec *audioFormat = &this->spec;

#else
static int ANDROIDAUD_OpenAudio (_THIS, SDL_AudioSpec *spec)
{
	SDL_AudioSpec *audioFormat = spec;
#endif

	int bytesPerSample;
	JNIEnv * jniEnv = NULL;

	this->hidden = NULL;

	if( ! (audioFormat->format == AUDIO_S8 || audioFormat->format == AUDIO_S16) )
	{
		__android_log_print(ANDROID_LOG_ERROR, "libSDL", "Application requested unsupported audio format - only S8 and S16 are supported");
		return (-1); // TODO: enable format conversion? Don't know how to do that in SDL
	}

	bytesPerSample = (audioFormat->format & 0xFF) / 8;
	audioFormat->format = ( bytesPerSample == 2 ) ? AUDIO_S16 : AUDIO_S8;
	
	(*jniVM)->AttachCurrentThread(jniVM, &jniEnv, NULL);

	if( !jniEnv )
	{
		__android_log_print(ANDROID_LOG_ERROR, "libSDL", "ANDROIDAUD_OpenAudio: Java VM AttachCurrentThread() failed");
		return (-1); // TODO: enable format conversion? Don't know how to do that in SDL
	}

	audioBufferSize = (*jniEnv)->CallIntMethod( jniEnv, JavaAudioThread, JavaInitAudio, 
					(jint)audioFormat->freq, (jint)audioFormat->channels, 
					(jint)(( bytesPerSample == 2 ) ? 1 : 0), (jint)audioFormat->size);

	if( audioBufferSize == 0 )
	{
		__android_log_print(ANDROID_LOG_INFO, "libSDL", "ANDROIDAUD_OpenAudio(): failed to get audio buffer from JNI");
		ANDROIDAUD_CloseAudio(this);
		return(-1);
	}

	/* We cannot call DetachCurrentThread() from main thread or we'll crash */
	/* (*jniVM)->DetachCurrentThread(jniVM); */

	audioFormat->samples = audioBufferSize / bytesPerSample / audioFormat->channels;
	audioFormat->size = audioBufferSize;
	__android_log_print(ANDROID_LOG_INFO, "libSDL", "ANDROIDAUD_OpenAudio(): app opened audio bytespersample %d freq %d channels %d bufsize %d", bytesPerSample, audioFormat->freq, (jint)audioFormat->channels, audioBufferSize);

	SDL_CalculateAudioSpec(audioFormat);
	
#if SDL_VERSION_ATLEAST(1,3,0)
	return(1);
#else
	return(0);
#endif
}

static void ANDROIDAUD_CloseAudio(_THIS)
{
	//__android_log_print(ANDROID_LOG_INFO, "libSDL", "ANDROIDAUD_CloseAudio()");
	JNIEnv * jniEnv = NULL;
	(*jniVM)->AttachCurrentThread(jniVM, &jniEnv, NULL);

	(*jniEnv)->DeleteGlobalRef(jniEnv, audioBufferJNI);
	audioBufferJNI = NULL;
	audioBuffer = NULL;
	audioBufferSize = 0;
	
	(*jniEnv)->CallIntMethod( jniEnv, JavaAudioThread, JavaDeinitAudio );

	/* We cannot call DetachCurrentThread() from main thread or we'll crash */
	/* (*jniVM)->DetachCurrentThread(jniVM); */
	
}

/* This function waits until it is possible to write a full sound buffer */
static void ANDROIDAUD_WaitAudio(_THIS)
{
	/* We will block in PlayAudio(), do nothing here */
}

static JNIEnv * jniEnvPlaying = NULL;
static jmethodID JavaFillBuffer = NULL;

static void ANDROIDAUD_ThreadInit(_THIS)
{
	jclass JavaAudioThreadClass = NULL;
	jmethodID JavaInitThread = NULL;
	jmethodID JavaGetBuffer = NULL;
	jboolean isCopy = JNI_TRUE;

	(*jniVM)->AttachCurrentThread(jniVM, &jniEnvPlaying, NULL);

	JavaAudioThreadClass = (*jniEnvPlaying)->GetObjectClass(jniEnvPlaying, JavaAudioThread);
	JavaFillBuffer = (*jniEnvPlaying)->GetMethodID(jniEnvPlaying, JavaAudioThreadClass, "fillBuffer", "()I");

	/* HACK: raise our own thread priority to max to get rid of "W/AudioFlinger: write blocked for 54 msecs" errors */
	JavaInitThread = (*jniEnvPlaying)->GetMethodID(jniEnvPlaying, JavaAudioThreadClass, "initAudioThread", "()I");
	(*jniEnvPlaying)->CallIntMethod( jniEnvPlaying, JavaAudioThread, JavaInitThread );

	JavaGetBuffer = (*jniEnvPlaying)->GetMethodID(jniEnvPlaying, JavaAudioThreadClass, "getBuffer", "()[B");
	audioBufferJNI = (*jniEnvPlaying)->CallObjectMethod( jniEnvPlaying, JavaAudioThread, JavaGetBuffer );
	audioBufferJNI = (*jniEnvPlaying)->NewGlobalRef(jniEnvPlaying, audioBufferJNI);
	audioBuffer = (unsigned char *) (*jniEnvPlaying)->GetByteArrayElements(jniEnvPlaying, audioBufferJNI, &isCopy);
	if( !audioBuffer )
	{
		__android_log_print(ANDROID_LOG_ERROR, "libSDL", "ANDROIDAUD_ThreadInit() JNI::GetByteArrayElements() failed! we will crash now");
		return;
	}
	if( isCopy == JNI_TRUE )
		__android_log_print(ANDROID_LOG_ERROR, "libSDL", "ANDROIDAUD_ThreadInit(): JNI returns a copy of byte array - no audio will be played");

	//__android_log_print(ANDROID_LOG_INFO, "libSDL", "ANDROIDAUD_ThreadInit()");
	SDL_memset(audioBuffer, this->spec.silence, this->spec.size);
};

static void ANDROIDAUD_ThreadDeinit(_THIS)
{
	(*jniVM)->DetachCurrentThread(jniVM);
};

static void ANDROIDAUD_PlayAudio(_THIS)
{
	//__android_log_print(ANDROID_LOG_INFO, "libSDL", "ANDROIDAUD_PlayAudio()");
	jboolean isCopy = JNI_TRUE;

	(*jniEnvPlaying)->ReleaseByteArrayElements(jniEnvPlaying, audioBufferJNI, (jbyte *)audioBuffer, 0);
	audioBuffer = NULL;

	(*jniEnvPlaying)->CallIntMethod( jniEnvPlaying, JavaAudioThread, JavaFillBuffer );

	audioBuffer = (unsigned char *) (*jniEnvPlaying)->GetByteArrayElements(jniEnvPlaying, audioBufferJNI, &isCopy);
	if( !audioBuffer )
		__android_log_print(ANDROID_LOG_ERROR, "libSDL", "ANDROIDAUD_PlayAudio() JNI::GetByteArrayElements() failed! we will crash now");

	if( isCopy == JNI_TRUE )
		__android_log_print(ANDROID_LOG_INFO, "libSDL", "ANDROIDAUD_PlayAudio() JNI returns a copy of byte array - that's slow");
}

#ifndef SDL_JAVA_PACKAGE_PATH
#error You have to define SDL_JAVA_PACKAGE_PATH to your package path with dots replaced with underscores, for example "com_example_SanAngeles"
#endif
#define JAVA_EXPORT_NAME2(name,package) Java_##package##_##name
#define JAVA_EXPORT_NAME1(name,package) JAVA_EXPORT_NAME2(name,package)
#define JAVA_EXPORT_NAME(name) JAVA_EXPORT_NAME1(name,SDL_JAVA_PACKAGE_PATH)

JNIEXPORT jint JNICALL JAVA_EXPORT_NAME(AudioThread_nativeAudioInitJavaCallbacks) (JNIEnv * jniEnv, jobject thiz)
{
	jclass JavaAudioThreadClass = NULL;
	JavaAudioThread = (*jniEnv)->NewGlobalRef(jniEnv, thiz);
	JavaAudioThreadClass = (*jniEnv)->GetObjectClass(jniEnv, JavaAudioThread);
	JavaInitAudio = (*jniEnv)->GetMethodID(jniEnv, JavaAudioThreadClass, "initAudio", "(IIII)I");
	JavaDeinitAudio = (*jniEnv)->GetMethodID(jniEnv, JavaAudioThreadClass, "deinitAudio", "()I");
	/*
	__android_log_print(ANDROID_LOG_INFO, "libSDL", "nativeAudioInitJavaCallbacks(): JavaAudioThread %p JavaFillBuffer %p JavaInitAudio %p JavaDeinitAudio %p",
							JavaAudioThread, JavaFillBuffer, JavaInitAudio, JavaDeinitAudio);
	*/
}

JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM *vm, void *reserved)
{
	jniVM = vm;
	return JNI_VERSION_1_2;
};

JNIEXPORT void JNICALL JNI_OnUnload(JavaVM *vm, void *reserved)
{
	/* TODO: free JavaAudioThread */
	jniVM = vm;
};

