#!/bin/bash

VERSION_task=${VERSION_task:-2.4.4}
URL_task=http://taskwarrior.org/download/task-${VERSION_task}.tar.gz

DEPS_task=(libuuid)  # gnutls
sha1_task=e7e1336ed099f672b3d5971d6a221b72ed804ac6
BUILD_task=$BUILD_PATH/task/$(get_directory $URL_task)
RECIPE_task=$RECIPES_PATH/task

_src=$BUILD_task
_build=$BUILD_task/build_p4a
_pyroot=$(dirname `dirname $HOSTPYTHON`)

function prebuild_task() {
	# take the patch from the recipe
	cd $_src
	patch -p1 < $ROOT_PATH/recipes/task/CMakeLists.txt.patch
	patch -p1 < $ROOT_PATH/recipes/task/Nibbler.h.patch

	cp $ROOT_PATH/recipes/task/glob.* $_src/src

	cd $_build
	if [ ! -d android-cmake ]
	then
		git clone https://github.com/taka-no-me/android-cmake.git
	fi

}


#function shouldbuild_task() {
#}

function build_task() {

	try mkdir -p $_build
	cd $_build

	push_arm

	export ANDROID_NDK=$ANDROIDNDK
	cmake -DCMAKE_TOOLCHAIN_FILE=android-cmake/android.toolchain.cmake \
	      -DUUID_INCLUDE_DIR=$BUILD_libuuid/build/include \
	      -DUUID_LIBRARY=$BUILD_libuuid/build/lib/libuuid.a \
	      -DCMAKE_CXX_FLAGS=-fPIC \
	      -DCMAKE_EXE_LINKER_FLAGS=-pie \
	      -DANDROID_NDK=$ANDROIDNDK \
	      -DCMAKE_BUILD_TYPE=Release \
	      -DANDROID_ABI="armeabi-v7a with NEON" \
	      $_src
	cmake --build .

	try make -j1 .
	try cp -a $_build/src/{task,calc,lex} $LIBS_PATH

	pop_arm
}

function postbuild_task() {
	true
}
