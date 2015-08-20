#!/bin/bash

VERSION_gnutls=3.3.16
DEPS_gnutls=(nettle)
URL_gnutls=ftp://ftp.gnutls.org/gcrypt/gnutls/v3.3/gnutls-${VERSION_gnutls}.tar.xz
BUILD_gnutls=$BUILD_PATH/gnutls/$(get_directory $URL_gnutls)
RECIPE_gnutls=$RECIPES_PATH/gnutls

function prebuild_gnutls() {
	true
}

function build_gnutls() {
	cd $BUILD_gnutls
	push_arm
	export PKG_CONFIG_PATH="$BUILD_nettle/build/lib/pkgconfig:$PKG_CONFIG_PATH"
	OLD_LDFLAGS=$LDFLAGS
	OLD_CPPFLAGS=$CPPFLAGS

	#echo $SHELL
	#PS1='\w: ' $SHELL

	export CPPFLAGS="-I$BUILD_libgmp/build/include $CPPFLAGS -fexceptions -I${ANDROIDNDK}/sources/cxx-stl/stlport/stlport"
	export LDFLAGS="-L$BUILD_libgmp/build/lib $LDFLAGS \
			$NDKPLATFORM/usr/lib/libz.so \
			$BUILD_libgmp/build/lib/libgmp.a \
			$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/$TOOLCHAIN_VERSION/libs/$ARCH/libsupc++.a \
			$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/$TOOLCHAIN_VERSION/libs/$ARCH/libgnustl_static.a"

	try ./configure --build=i686-pc-linux-gnu --host=arm-linux-eabi --prefix=$BUILD_gnutls/build/ --enable-local-libopts --disable-doc --disable-tests
	try make install
    	libtool --finish $BUILD_gnutls/build/

	export LDFLAGS=$OLD_LDFLAGS
	export CPPFLAGS=$OLD_CPPFLAGS
	pop_arm
}

function postbuild_gnutls() {
	true
}
