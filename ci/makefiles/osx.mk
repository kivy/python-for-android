# installs Android's SDK/NDK, cython

# The following variable/s can be override when running the file
ANDROID_HOME ?= $(HOME)/.android

all: upgrade_cython install_android_ndk_sdk

upgrade_cython:
	pip3 install --upgrade Cython

install_android_ndk_sdk:
	mkdir -p $(ANDROID_HOME)
	make -f ci/makefiles/android.mk
