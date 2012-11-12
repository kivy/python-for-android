#!/bin/bash

VERSION_lxml=2.3.6
URL_lxml=http://pypi.python.org/packages/source/l/lxml/lxml-$VERSION_lxml.tar.gz
DEPS_lxml=(libxml2 libxslt python)
MD5_lxml=d5d886088e78b1bdbfd66d328fc2d0bc
BUILD_lxml=$BUILD_PATH/lxml/$(get_directory $URL_lxml)
RECIPE_lxml=$RECIPES_PATH/lxml

function prebuild_lxml() {
	true
}

function build_lxml() {
	cd $BUILD_lxml

	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/lxml" ]; then
		return
	fi

	push_arm

	export CC="$CC -I$BUILD_libxml2/include -I$BUILD_libxslt"
	export LDFLAGS="-L$BUILD_libxslt/libxslt/.libs -L$BUILD_libxslt/libexslt/.libs -L$BUILD_libxml2/.libs -L$BUILD_libxslt/libxslt -L$BUILD_libxslt/libexslt -L$BUILD_libxml2/  $LDFLAGS"
	export LDSHARED="$LIBLINK"

	chmod +x $BUILD_libxslt/xslt-config
	export PATH=$PATH:$BUILD_libxslt

	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -I$BUILD_libxml2/include -I$BUILD_libxslt
	try find . -iname '*.pyx' -exec cython {} \;
	try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
	#try find build/lib.* -name "*.o" -exec $STRIP {} \;

	export PYTHONPATH=$BUILD_hostpython/Lib/site-packages
	try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

	unset LDSHARED
	pop_arm
}

function postbuild_lxml() {
	true
}
