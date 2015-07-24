#!/bin/bash
VERSION_plyvel=${VERSION_plyvel:-0.9}
URL_plyvel=https://pypi.python.org/packages/source/p/plyvel/plyvel-${VERSION_plyvel}.tar.gz
DEPS_plyvel=(python setuptools leveldb)
MD5_plyvel=b0f768a07683dad01554b040c6320ed5
BUILD_plyvel=$BUILD_PATH/plyvel/$(get_directory $URL_plyvel)
RECIPE_plyvel=$RECIPES_PATH/plyvel

function prebuild_plyvel() {
	true
}

function shouldbuild_plyvel() {
	if [ -d "$SITEPACKAGES_PATH/plyvel" ]; then
		DO_BUILD=0
	fi
}

function build_plyvel() {
	cd $BUILD_plyvel

	# Add zip_safe=False, if not already there
	grep -q -e 'zip_safe=False' setup.py || sed -i "30i\ \ \ \ zip_safe=False," setup.py

	push_arm
	
	# gnu-libstdc++, leveldb and python
	export CFLAGS="$CFLAGS -I$BUILD_leveldb/include"
	export CFLAGS="$CFLAGS -I$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/$TOOLCHAIN_VERSION/include/ -I$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/$TOOLCHAIN_VERSION/libs/armeabi/include/"
	export CFLAGS="$CFLAGS -fpic -shared"
	export CXXFLAGS=$CFLAGS
	
	export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
	export LDFLAGS="$LDFLAGS -lgnustl_shared -lpython2.7"
	export LDSHARED=$LIBLINK
	
	export PPO=$PYTHONPATH
	export PYTHONPATH=$SITEPACKAGES_PATH:$BUILDLIB_PATH
	
	try $HOSTPYTHON setup.py install -O2
	
	export PYTHONPATH=$PPO
	unset LDSHARED
	unset PPO
	pop_arm
}

function postbuild_plyvel() {
	true
}
