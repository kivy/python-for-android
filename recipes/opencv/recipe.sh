#!/bin/bash

VERSION_opencv=${VERSION_opencv:-2.4.11}
URL_opencv=https://github.com/Itseez/opencv/archive/$VERSION_opencv.zip

DEPS_opencv=(numpy python)
MD5_opencv=32f498451bff1817a60e1aabc2939575
BUILD_opencv=$BUILD_PATH/opencv/$(get_directory $URL_opencv)
RECIPE_opencv=$RECIPES_PATH/opencv

_cvsrc=$BUILD_opencv
_cvbuild=$BUILD_opencv/build_p4a
_pyroot=$(dirname `dirname $HOSTPYTHON`)

function prebuild_opencv() {
	cd $BUILD_opencv

	if [ -f .patched ]; then
		return
	fi

	try patch -p1 < $RECIPE_opencv/patches/p4a_build-2.4.11.patch
	touch .patched
}

function shouldbuild_opencv() {
	if [ -f "$SITEPACKAGES_PATH/cv2.so" ]; then
		DO_BUILD=0
	fi
}

function build_opencv() {

	try mkdir -p $_cvbuild
	cd $_cvbuild

	push_arm
	#try set > opencv_p4y_env.log # check env vars for debugging

	export ANDROID_NDK=$ANDROIDNDK
	try cmake -DP4A=ON -DANDROID_ABI=$ARCH -DCMAKE_TOOLCHAIN_FILE=$_cvsrc/platforms/android/android.toolchain.cmake \
	  -DPYTHON_INCLUDE_PATH=$_pyroot/include/python2.7 -DPYTHON_LIBRARY=$_pyroot/lib/libpython2.7.so \
	  -DPYTHON_NUMPY_INCLUDE_DIR=$SITEPACKAGES_PATH/numpy/core/include \
	  -DANDROID_EXECUTABLE=$ANDROIDSDK/tools/android \
	  -DBUILD_TESTS=OFF -DBUILD_PERF_TESTS=OFF -DBUILD_EXAMPLES=OFF -DBUILD_ANDROID_EXAMPLES=OFF \
	  -DPYTHON_PACKAGES_PATH=$SITEPACKAGES_PATH \
	  $_cvsrc
	try make -j8 opencv_python
	try cmake -DCOMPONENT=python -P ./cmake_install.cmake
	try cp -a $_cvbuild/lib/$ARCH/lib*.so $LIBS_PATH

	pop_arm
}

function postbuild_opencv() {
	true
}
