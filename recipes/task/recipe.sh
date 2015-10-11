#!/bin/bash

VERSION_task=${VERSION_task:-2.4.4}
URL_task=http://taskwarrior.org/download/task-${VERSION_task}.tar.gz

DEPS_task=(libuuid gnutls)
sha1_task=e7e1336ed099f672b3d5971d6a221b72ed804ac6
BUILD_task=$BUILD_PATH/task/$(get_directory $URL_task)
RECIPE_task=$RECIPES_PATH/task

_build=$BUILD_task/build_p4a
_pyroot=$(dirname `dirname $HOSTPYTHON`)

function prebuild_task() {
	# take the patch from the recipe
	cd $BUILD_task
	patch -p1 < $RECIPE_task/CMakeLists.txt.patch
	patch -p1 < $RECIPE_task/Nibbler.h.patch

	cp $RECIPE_task/glob.* $BUILD_task/src

	cd $BUILD_task/build_p4a
	if [ ! -d android-cmake ]
	then
		git clone https://github.com/taka-no-me/android-cmake.git
	fi

}


#function shouldbuild_task() {
#}

function build_task() {
	try mkdir -p $BUILD_task/build_p4a
	cd $BUILD_task/build_p4a

	push_arm

	export ANDROID_NDK=$ANDROIDNDK
	export GNUTLS_LIBRARY=$BUILD_gnutls/build/lib/libgnutls.a
	export GNUTLS_INCLUDE_DIR=$BUILD_gnutls/build/include
	cmake -DCMAKE_TOOLCHAIN_FILE=android-cmake/android.toolchain.cmake \
	      -DUUID_INCLUDE_DIR=$BUILD_libuuid/build/include \
	      -DUUID_LIBRARY=$BUILD_libgmp/build/lib/libgmp.a \
	      -DTASK_LIBRARIES=$BUILD_libuuid/build/lib/libuuid.a \
	      -DCMAKE_CXX_FLAGS=-fPIC \
	      -DGNUTLS_LIBRARY="$GNUTLS_LIBRARY" \
	      -DGNUTLS_INCLUDE_DIR=$GNUTLS_INCLUDE_DIR \
	      -DCMAKE_EXE_LINKER_FLAGS="-pie $(pkg-config --libs nettle hogweed) -lz" \
	      -DANDROID_NDK=$ANDROIDNDK \
	      -DCMAKE_BUILD_TYPE=Release \
	      -DCMAKE_VERBOSE_MAKEFILE=ON \
	      -DANDROID_ABI="armeabi-v7a with NEON" \
	      $BUILD_task
	cmake --build .

	make -j1 .
	try cp -a $BUILD_task/build_p4a/src/{task,calc,lex} $LIBS_PATH

	pop_arm
}

function postbuild_task() {
	true
}
