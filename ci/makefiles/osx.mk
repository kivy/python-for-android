# installs java 1.8, android's SDK/NDK, cython and p4a

# The following variable/s can be override when running the file
ANDROID_HOME ?= $(HOME)/.android

all: install_java upgrade_cython install_android_ndk_sdk install_p4a

install_java:
	brew tap adoptopenjdk/openjdk
	brew cask install adoptopenjdk8
	/usr/libexec/java_home -V

upgrade_cython:
	pip3 install --upgrade Cython==0.28.6

install_android_ndk_sdk:
	mkdir -p $(ANDROID_HOME)
	make -f ci/makefiles/android.mk target_os=darwin JAVA_HOME=`/usr/libexec/java_home -v 1.8`

install_p4a:
	# check python version and install p4a
	python3 --version
	pip3 install -e .
