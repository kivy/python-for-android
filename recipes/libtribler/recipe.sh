#!/bin/bash
VERSION_libtribler=${VERSION_libtribler:-devel}
DEPS_libtribler=(kivy python openssl m2crypto twisted sqlite3 pyasn1 apsw cherrypy netifaces libtorrent libnacl libsodium pil plyvel requests)
BUILD_libtribler=$BUILD_PATH/libtribler
RECIPE_libtribler=$RECIPES_PATH/libtribler

function prebuild_libtribler() {

	cd $PACKAGES_PATH/libtribler
	LIBTRIBLER_CHANGED=1
	if [ ! -d ./tribler-git ]; then
		# Clone repo so all submodules are included:
		try git clone --recursive https://github.com/tribler/tribler.git tribler-git
	else
		# Pull latest changes and check whether anything changed at all:
		pushd ./tribler-git
		OLD_LATEST_COMMIT_HASH="$(git log -n 1 --pretty=format:'%H')"
		try git pull origin $VERSION_libtribler
		NEW_LATEST_COMMIT_HASH="$(git log -n 1 --pretty=format:'%H')"
		if [ "$OLD_LATEST_COMMIT_HASH" == "$NEW_LATEST_COMMIT_HASH" ]; then
			LIBTRIBLER_CHANGED=0
		fi
		popd
	fi

	# Copy repo to build folder when build folder is empty or libtribler has changed:
	if [ ! -d ${BUILD_libtribler}/tribler-git ] || [ $LIBTRIBLER_CHANGED ]; then
		try rsync -a ./tribler-git ${BUILD_libtribler}
	fi

}

function build_libtribler() {
	cd ${BUILD_libtribler}/tribler-git
	push_arm
	try $HOSTPYTHON setup.py install
	pop_arm
}

function postbuild_libtribler() {
	true
}
