LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := main

SDL_PATH := ../SDL

LOCAL_C_INCLUDES := $(LOCAL_PATH)/$(SDL_PATH)/include

# Add your application source files here...
LOCAL_SRC_FILES := $(SDL_PATH)/src/main/android/SDL_android_main.c \
	start.c

LOCAL_CFLAGS += -I$(PYTHON_INCLUDE_ROOT) $(EXTRA_CFLAGS)

LOCAL_SHARED_LIBRARIES := SDL2 python_shared

LOCAL_LDLIBS := -lGLESv1_CM -lGLESv2 -llog $(EXTRA_LDLIBS)

LOCAL_LDFLAGS += -L$(PYTHON_LINK_ROOT) $(APPLICATION_ADDITIONAL_LDFLAGS)

include $(BUILD_SHARED_LIBRARY)

ifdef CRYSTAX_PYTHON_VERSION
    $(call import-module,python/$(CRYSTAX_PYTHON_VERSION))
endif
