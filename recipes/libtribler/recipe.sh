#!/bin/bash
DEPS_libtribler=(kivy python openssl m2crypto twisted sqlite3 pyasn1 apsw cherrypy netifaces libtorrent libnacl libsodium pil plyvel requests)
BUILD_libtribler=$BUILD_PATH/libtribler/tribler-git
RECIPE_libtribler=$RECIPES_PATH/libtribler

function prebuild_libtribler() {

	# Clone repo so all submodules are included:
	cd $BUILD_PATH/libtribler
	git clone --recursive https://github.com/tribler/tribler.git tribler-git

}

function build_libtribler() {
	cd $BUILD_libtribler
	push_arm
	try $HOSTPYTHON setup.py install
	pop_arm
}

function postbuild_libtribler() {
	true
}
