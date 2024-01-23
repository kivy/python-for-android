LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := main_$(PREFERRED_ABI)

LOCAL_SRC_FILES := start.c

include $(BUILD_SHARED_LIBRARY)
