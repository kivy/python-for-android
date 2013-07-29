#!/bin/bash

VERSION_python=2.7.2
DEPS_python=(hostpython)
DEPS_OPTIONAL_python=(openssl sqlite3)
URL_python=http://python.org/ftp/python/$VERSION_python/Python-$VERSION_python.tar.bz2
MD5_python=ba7b2f11ffdbf195ee0d111b9455a5bd

# must be generated ?
BUILD_python=$BUILD_PATH/python/$(get_directory $URL_python)
RECIPE_python=$RECIPES_PATH/python

function prebuild_python() {
	cd $BUILD_python

	# check marker in our source build
	if [ -f .patched ]; then
		# no patch needed
		return
	fi

	try patch -p1 < $RECIPE_python/patches/Python-$VERSION_python-xcompile.patch
	try patch -p1 < $RECIPE_python/patches/disable-modules.patch
	try patch -p1 < $RECIPE_python/patches/fix-locale.patch
	try patch -p1 < $RECIPE_python/patches/fix-gethostbyaddr.patch
	try patch -p1 < $RECIPE_python/patches/fix-setup-flags.patch
	try patch -p1 < $RECIPE_python/patches/fix-filesystemdefaultencoding.patch
	try patch -p1 < $RECIPE_python/patches/fix-termios.patch
	try patch -p1 < $RECIPE_python/patches/custom-loader.patch
	try patch -p1 < $RECIPE_python/patches/verbose-compilation.patch
	try patch -p1 < $RECIPE_python/patches/fix-remove-corefoundation.patch
	try patch -p1 < $RECIPE_python/patches/fix-dynamic-lookup.patch
	try patch -p1 < $RECIPE_python/patches/fix-dlfcn.patch

	system=$(uname -s)
	if [ "X$system" == "XDarwin" ]; then
		try patch -p1 < $RECIPE_python/patches/fix-configure-darwin.patch
		try patch -p1 < $RECIPE_python/patches/fix-distutils-darwin.patch
	fi

	# everything done, touch the marker !
	touch .patched
}

function build_python() {
	# placeholder for building
	cd $BUILD_python

	# if the last step have been done, avoid all
	if [ -f libpython2.7.so ]; then
		return
	fi
	
	# copy same module from host python
	try cp $RECIPE_hostpython/Setup Modules
	try cp $BUILD_hostpython/hostpython .
	try cp $BUILD_hostpython/hostpgen .

	push_arm

	# openssl activated ?
	if [ "X$BUILD_openssl" != "X" ]; then
		debug "Activate flags for openssl / python"
		export CFLAGS="$CFLAGS -I$BUILD_openssl/include/"
		export LDFLAGS="$LDFLAGS -L$BUILD_openssl/"
	fi

	# sqlite3 activated ?
	if [ "X$BUILD_sqlite3" != "X" ]; then
		debug "Activate flags for sqlite3"
		export CFLAGS="$CFLAGS -I$BUILD_sqlite3"
		export LDFLAGS="$LDFLAGS -L$SRC_PATH/obj/local/$ARCH/"
	fi

	try ./configure --host=arm-eabi --prefix="$BUILD_PATH/python-install" --enable-shared --disable-toolbox-glue --disable-framework
	echo ./configure --host=arm-eabi --prefix="$BUILD_PATH/python-install" --enable-shared --disable-toolbox-glue --disable-framework
	echo $MAKE HOSTPYTHON=$BUILD_python/hostpython HOSTPGEN=$BUILD_python/hostpgen CROSS_COMPILE_TARGET=yes INSTSONAME=libpython2.7.so
	cp HOSTPYTHON=$BUILD_python/hostpython python

	# FIXME, the first time, we got a error at:
	# python$EXE ../../Tools/scripts/h2py.py -i '(u_long)' /usr/include/netinet/in.h
    # /home/tito/code/python-for-android/build/python/Python-2.7.2/python: 1: Syntax error: word unexpected (expecting ")")
	# because at this time, python is arm, not x86. even that, why /usr/include/netinet/in.h is used ?
	# check if we can avoid this part.

	debug 'First install (failing..)'
	$MAKE install HOSTPYTHON=$BUILD_python/hostpython HOSTPGEN=$BUILD_python/hostpgen CROSS_COMPILE_TARGET=yes INSTSONAME=libpython2.7.so
	debug 'Second install.'
	touch python.exe python
	$MAKE install HOSTPYTHON=$BUILD_python/hostpython HOSTPGEN=$BUILD_python/hostpgen CROSS_COMPILE_TARGET=yes INSTSONAME=libpython2.7.so
	pop_arm

	system=$(uname -s)
	if [ "X$system" == "XDarwin" ]; then
		try cp $RECIPE_python/patches/_scproxy.py $BUILD_python/Lib/
	fi
	try cp $BUILD_hostpython/hostpython $BUILD_PATH/python-install/bin/python.host
	try cp libpython2.7.so $LIBS_PATH/
}


function postbuild_python() {
	# placeholder for post build
	true
}
