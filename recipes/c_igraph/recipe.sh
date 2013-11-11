#!/bin/bash

# Recipe for igraph, a high performance graph library in C: http://igraph.org
#
# Written by Zachary Spector: https://github.com/LogicalDash/
#
# 

VERSION_c_igraph=${VERSION_c_igraph:0.6.5}

DEPS_c_igraph=()

URL_c_igraph=http://downloads.sourceforge.net/project/igraph/C%20library/0.6.5/igraph-0.6.5.tar.gz

MD5_c_igraph=5f9562263ba78b31c564d6897ff5a110

BUILD_c_igraph=$BUILD_PATH/c_igraph/$(get_directory $URL_c_igraph)

RECIPE_c_igraph=$RECIPES_PATH/c_igraph

function prebuild_c_igraph() {
    true
}

function shouldbuild_c_igraph() {
    false
}

function build_c_igraph() {
    # I'm not even going to make anything here!
    # I'll let the main igraph recipe do that.
    true
}

function postbuild_c_igraph() {
    true
}
