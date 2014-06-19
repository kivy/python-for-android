#!/bin/bash

# version of your package
VERSION_apsw=${VERSION_apsw:-3.8.4.1-r1}

# dependencies of this recipe
DEPS_apsw=(python)

# url of the package
URL_apsw=https://github.com/rogerbinns/apsw/releases/download/3.8.4.1-r1/apsw-3.8.4.1-r1.zip

# md5 of the package
MD5_apsw=5ad3098489576929b90f4215eb5b2621

# default build path
BUILD_apsw=$BUILD_PATH/apsw/$(get_directory $URL_apsw)

# default recipe path
RECIPE_apsw=$RECIPES_PATH/apsw

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_apsw() {

    # fetch sqlite if necessary
    cd ${BUILD_apsw}
    if [ ! -d ${BUILD_apsw}/sqlite3 ]; then
        echo "fetching sqlite..."
        # using /usr/bin/python for this
	python setup.py fetch --sqlite --version=3.8.4.1 --missing-checksum-ok
    fi

    # apsw insists on configuring sqlite, but it's for the host, not the target.
    # So, put in the correct values.

    cat >sqlite3/sqlite3config.h <<EOF
#define HAVE_SYS_TYPES_H 1
#define HAVE_SYS_STAT_H 1
#define HAVE_STDLIB_H 1
#define HAVE_STRING_H 1
#define HAVE_MEMORY_H 1
#define HAVE_STRINGS_H 1
#define HAVE_INTTYPES_H 1
#define HAVE_STDINT_H 1
#define HAVE_UNISTD_H 1
#define HAVE_DLFCN_H 1
#define HAVE_FDATASYNC 0
#define HAVE_USLEEP 1
#define HAVE_LOCALTIME_R 1
#define HAVE_GMTIME_R 1
#define HAVE_DECL_STRERROR_R 1
#define HAVE_STRERROR_R 1
#define HAVE_POSIX_FALLOCATE 0
EOF

}

function shouldbuild_apsw() {
    if [ -d "$SITEPACKAGES_PATH/apsw" ]; then
	DO_BUILD=0
    fi
}

# function called to build the source code
function build_apsw() {

    cd ${BUILD_apsw}

    export NDK=$ANDROIDNDK
    push_arm

    # HOSTPYTHON can't do zipfile or tarfile modules because of
    # buildozer bug (missing LD_LIBRARY_PATH is what it looks like),
    # but we don't need them at this stage
    cp setup.py setup.py.backup
    sed -e 's/import zipfile, tarfile/# import zipfile, tarfile/g' <setup.py.backup >setup.py

    # build python extension
    export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
    export LDSHARED="$LIBLINK"

    echo "building apsw in `pwd`..."
    # now we can build; enable the FTS4 sqlite extension for full-text search
    try ${HOSTPYTHON} setup.py build --enable=fts4
    echo "installing apsw..."
    try ${HOSTPYTHON} setup.py install
    echo "done with apsw."

    pop_arm
}

# function called after all the compile have been done
function postbuild_apsw() {
    echo "apsw built"
}
