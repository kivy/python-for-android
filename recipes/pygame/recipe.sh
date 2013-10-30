#!/bin/bash

VERSION_pygame=${VERSION_pygame:-1.9.1}
URL_pygame=http://pygame.org/ftp/pygame-$(echo $VERSION_pygame)release.tar.gz
DEPS_pygame=(python sdl)
MD5_pygame=1c4cdc708d17c8250a2d78ef997222fc
BUILD_pygame=$BUILD_PATH/pygame/$(get_directory $URL_pygame)
RECIPE_pygame=$RECIPES_PATH/pygame

function prebuild_pygame() {
	cd $BUILD_pygame

	# check marker in our source build
	if [ -f .patched ]; then
		# no patch needed
		return
	fi

	try cp $RECIPE_pygame/Setup .
	try patch -p1 < $RECIPE_pygame/patches/fix-surface-access.patch
	try patch -p1 < $RECIPE_pygame/patches/fix-array-surface.patch

	# everything done, touch the marker !
	touch .patched
}

function shouldbuild_pygame() {
	if [ -d $BUILD_PATH/python-install/lib/python*/site-packages/pygame ]; then
		DO_BUILD=0
	fi
}

function build_pygame() {
	cd $BUILD_pygame

	push_arm

	CFLAGS="$CFLAGS -I$JNI_PATH/png -I$JNI_PATH/jpeg"
	CFLAGS="$CFLAGS -I$JNI_PATH/sdl/include -I$JNI_PATH/sdl_mixer"
	CFLAGS="$CFLAGS -I$JNI_PATH/sdl_ttf -I$JNI_PATH/sdl_image"
	export CFLAGS="$CFLAGS"
	export LDFLAGS="$LDFLAGS -L$LIBS_PATH -L$SRC_PATH/obj/local/$ARCH/ -lm -lz"
	export LDSHARED="$LIBLINK"
	try $HOSTPYTHON setup.py install -O2
	try find build/lib.* -name "*.o" -exec $STRIP {} \;

	try rm -rf $BUILD_PATH/python-install/lib/python*/site-packages/pygame/docs
	try rm -rf $BUILD_PATH/python-install/lib/python*/site-packages/pygame/examples
	try rm -rf $BUILD_PATH/python-install/lib/python*/site-packages/pygame/tests
	try rm -rf $BUILD_PATH/python-install/lib/python*/site-packages/pygame/gp2x

	unset LDSHARED
	pop_arm
}

function postbuild_pygame() {
	true
}
