LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := libevent2

LOCAL_SRC_FILES := libevent2/lib/libevent.a
LOCAL_EXPORT_C_INCLUDES := libevent2/include
LOCAL_C_INCLUDES := libevent2/include

include $(PREBUILT_STATIC_LIBRARY)

LOCAL_MODULE    := swift
LOCAL_SRC_FILES := swift.cpp sha1.cpp compat.cpp sendrecv.cpp send_control.cpp hashtree.cpp bin.cpp binmap.cpp binheap.cpp channel.cpp transfer.cpp httpgw.cpp statsgw.cpp cmdgw.cpp avgspeed.cpp availability.cpp	

LOCAL_CFLAGS    += -D__NEW__ 

LOCAL_STATIC_LIBRARIES := libevent2

#include $(BUILD_SHARED_LIBRARY)
include $(BUILD_EXECUTABLE)
