#!/bin/bash

# version of your package
VERSION_requests=${VERSION_requests:-2.2.0}

# dependencies of this recipe
DEPS_requests=()

# url of the package
URL_requests=https://pypi.python.org/packages/source/r/requests/requests-$VERSION_requests.tar.gz

# md5 of the package
MD5_requests=

# default build path
BUILD_requests=$BUILD_PATH/requests/$(get_directory $URL_requests)

# default recipe path
RECIPE_requests=$RECIPES_PATH/requests

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_requests() {
    cd $BUILD_requests/requests/packages/urllib3

    FILES=$(find . -name \*.py -print)

    for f in $FILES
    do
        echo "Processing $f file..."
        line=$(head -n 1 $f)
        if [[ $line != *UTF-8* ]]
        then
            #echo -e "\n\n$(cat $f)" > $f
            sed -i '1s/^/# -*- coding: utf-8 -*-\n\n/' $f
        fi
    done

    true
}

# function called to build the source code
function build_requests() {
    if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/requests" ]; then
        return
    fi

    cd $BUILD_requests

    push_arm
    export PYTHONPATH=$BUILD_PATH/hostpython/Python-2.7.2/Lib/site-packages
    try $BUILD_PATH/hostpython/Python-2.7.2/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages
    pop_arm
}

# function called after all the compile have been done
function postbuild_requests() {
    true
}
