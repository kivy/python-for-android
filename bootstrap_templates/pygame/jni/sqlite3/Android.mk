LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_SRC_FILES := sqlite3.c

LOCAL_MODULE := sqlite3

include $(BUILD_SHARED_LIBRARY)
