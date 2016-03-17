LOCAL_PATH := $(call my-dir)/..

include $(CLEAR_VARS)
LOCAL_MODULE            := sqlite3
LOCAL_SRC_FILES         := sqlite3.c
LOCAL_CFLAGS            := -DSQLITE_THREADSAFE=1
include $(BUILD_SHARED_LIBRARY)
