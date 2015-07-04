LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := main

SDL_PATH := ../SDL

LOCAL_C_INCLUDES := $(LOCAL_PATH)/$(SDL_PATH)/include

# Add your application source files here...
LOCAL_SRC_FILES := $(SDL_PATH)/src/main/android/SDL_android_main.c \
	start.c

LOCAL_CFLAGS += -I$(LOCAL_PATH)/../../../../python-install/include/python2.7

LOCAL_SHARED_LIBRARIES := SDL2

LOCAL_LDLIBS := -lGLESv1_CM -lGLESv2 -llog -lpython2.7

LOCAL_LDFLAGS += -L$(LOCAL_PATH)/../../../../python-install/lib $(APPLICATION_ADDITIONAL_LDFLAGS)

include $(BUILD_SHARED_LIBRARY)
