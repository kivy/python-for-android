LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := tremor

LOCAL_CFLAGS := -I$(LOCAL_PATH) -DHAVE_ALLOCA_H

LOCAL_CPP_EXTENSION := .cpp

LOCAL_SRC_FILES := $(notdir $(wildcard $(LOCAL_PATH)/*.c))

include $(BUILD_STATIC_LIBRARY)

