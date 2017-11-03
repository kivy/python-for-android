LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS) 

LOCAL_MODULE := iconv 
LOCAL_CFLAGS := -Wno-multichar \
	-D_ANDROID \
	-DLIBDIR="c" \
	-DBUILDING_LIBICONV \
	-DIN_LIBRARY

LOCAL_C_INCLUDES := $(LOCAL_PATH)/include \
	$(LOCAL_PATH)/lib \
	$(LOCAL_PATH) \
	$(LOCAL_PATH)/libcharset/lib
    	
LOCAL_SRC_FILES := lib/iconv.c \
     libcharset/lib/localcharset.c \
     lib/relocatable.c

LOCAL_EXPORT_C_INCLUDES := $(LOCAL_PATH)/include
LOCAL_EXPORT_LDLIBS := -lz 

include $(BUILD_STATIC_LIBRARY)
