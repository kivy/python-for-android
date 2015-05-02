LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := sdl_ttf

LOCAL_CFLAGS := -I$(LOCAL_PATH) -I$(LOCAL_PATH)/../sdl/include -I$(LOCAL_PATH)/../freetype/include

LOCAL_CPP_EXTENSION := .cpp

LOCAL_SRC_FILES := SDL_ttf.c

LOCAL_SHARED_LIBRARIES := sdl
LOCAL_STATIC_LIBRARIES := freetype
LOCAL_LDLIBS := -lz

include $(BUILD_SHARED_LIBRARY)

