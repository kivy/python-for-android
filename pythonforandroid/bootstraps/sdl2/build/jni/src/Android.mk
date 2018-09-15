LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := main

SDL_PATH := ../SDL

LOCAL_C_INCLUDES := $(LOCAL_PATH)/$(SDL_PATH)/include

# Add your application source files here...
LOCAL_SRC_FILES := $(SDL_PATH)/src/main/android/SDL_android_main.c \
	start.c

# LOCAL_CFLAGS += -I$(LOCAL_PATH)/../../../../other_builds/$(PYTHON2_NAME)/$(ARCH)/python2/python-install/include/python2.7 $(EXTRA_CFLAGS)

LOCAL_CFLAGS += -I$(LOCAL_PATH)/../../../../other_builds/python3/$(ARCH)/python3/Include -I$(LOCAL_PATH)/../../../../other_builds/python3/$(ARCH)/python3/Android/build/python3.7-android-$(TARGET_ANDROID_API)-armv7 -L$(LOCAL_PATH)/../../../../other_builds/python3/$(ARCH)/python3/Android/build/python3.7-android-$(TARGET_ANDROID_API)-armv7


# LOCAL_CFLAGS += -I/home/sandy/.local/share/python-for-android/build/bootstrap_builds/sdl2_gradle-python3/jni/src/../../../../other_builds/python3/armeabi-v7a/python3/Android/build/python3.7-android-24-armv7

LOCAL_SHARED_LIBRARIES := SDL2 python_shared

LOCAL_LDLIBS := -lGLESv1_CM -lGLESv2 -llog $(EXTRA_LDLIBS) -lpython3.7m

LOCAL_LDFLAGS += $(APPLICATION_ADDITIONAL_LDFLAGS) -L$(LOCAL_PATH)/../../../../other_builds/python3/$(ARCH)/python3/Android/build/python3.7-android-$(TARGET_ANDROID_API)-armv7

include $(BUILD_SHARED_LIBRARY)

ifdef CRYSTAX_PYTHON_VERSION
    $(call import-module,python/$(CRYSTAX_PYTHON_VERSION))
endif
