# installs java 1.8, android's SDK/NDK, cython and p4a

# The following variable/s can be override when running the file
ANDROID_HOME ?= $(HOME)/.android

all: upgrade_cython install_android_ndk_sdk

upgrade_cython:
	pip3 install --upgrade Cython

install_android_ndk_sdk:
	mkdir -p $(ANDROID_HOME)
	make -f ci/makefiles/android.mk JAVA_HOME=`/usr/libexec/java_home -v 13`
