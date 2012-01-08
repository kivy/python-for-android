#!/bin/bash

VERSION_pil=1.1.7
URL_pil=http://effbot.org/downloads/Imaging-$VERSION_pil.tar.gz
DEPS_pil=(png jpeg)
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
	try sed -i s:_LIBS_:$LIBS: setup.py
	try sed -i s:_JNI_:$JNI_PATH: setup.py
	try sed -i s:_NDKPLATFORM_:$NDKPLATFORM: setup.py

	# everything done, touch the marker !
	touch .patched
}

function build_pil() {
	cd $BUILD_pil

	push_arm

	LIBS="$SRC_PATH/obj/local/$ARCH"
	export CFLAGS="$CFLAGS -I$JNI_PATH/png -I$JNI_PATH/jpeg"
	export LDFLAGS="$LDFLAGS -L$LIBS -lm -lz"
	try $BUILD_PATH/python-install/bin/python.host setup.py install
	try find build/lib.* -name "*.o" -exec $STRIP {} \;

	pop_arm
}

function postbuild_pil() {
	true
}
