
LOCAL_PATH := $(call my-dir)
HARFBUZZ_PATH := $(LOCAL_PATH)/../../../../other_builds/harfbuzz/$(ARCH)/harfbuzz

# HARFBUZZ
include $(CLEAR_VARS)
LOCAL_MODULE := harfbuzz
LOCAL_SRC_FILES := $(LOCAL_PATH)/libharfbuzz.a
LOCAL_EXPORT_C_INCLUDES := $(HARFBUZZ_PATH) $(HARFBUZZ_PATH)/src
include $(PREBUILT_STATIC_LIBRARY)