# Copyright (C) 2010 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE    := native-activity
LOCAL_SRC_FILES := main.c
LOCAL_LDLIBS    := -lpython2.7 -ldl -llog -lz -landroid
LOCAL_STATIC_LIBRARIES := android_native_app_glue
LOCAL_CFLAGS := \
    -I$(LOCAL_PATH)/../../../build/python-install/include/python2.7
LOCAL_LDFLAGS := \
    -L$(LOCAL_PATH)/../../../build/python-install/lib

include $(BUILD_SHARED_LIBRARY)

$(call import-module,android/native_app_glue)
