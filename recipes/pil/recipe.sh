#!/bin/bash

VERSION_pil=1.1.7
URL_pil=http://effbot.org/downloads/Imaging-$VERSION_pil.tar.gz
DEPS_pil=(png jpeg python)
MD5_pil=fc14a54e1ce02a0225be8854bfba478e
BUILD_pil=$BUILD_PATH/pil/$(get_directory $URL_pil)
RECIPE_pil=$RECIPES_PATH/pil

function prebuild_pil() {
	cd $BUILD_pil

	# check marker in our source build
	if [ -f .patched ]; then
		# no patch needed
		return
	fi

	try cp setup.py setup.py.tmpl
	try patch -p1 < $RECIPE_pil/patches/fix-path.patch

	LIBS="$SRC_PATH/obj/local/$ARCH"
	try cp setup.py.tmpl setup.py
	try $SED s:_LIBS_:$LIBS: setup.py
	try $SED s:_JNI_:$JNI_PATH: setup.py
	try $SED s:_NDKPLATFORM_:$NDKPLATFORM: setup.py

	try patch -p1 < $RECIPE_pil/patches/disable-tk.patch

	# everything done, touch the marker !
	touch .patched
}

function build_pil() {
	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/PIL" ]; then
		return
	fi

	cd $BUILD_pil

	push_arm

	LIBS="$SRC_PATH/obj/local/$ARCH"
	export CFLAGS="$CFLAGS -I$JNI_PATH/png -I$JNI_PATH/jpeg"
	export LDFLAGS="$LDFLAGS -L$LIBS -lm -lz"
	export LDSHARED="$LIBLINK"
	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

	unset LDSHARED
	pop_arm
}

function postbuild_pil() {
	true
}
