#!/bin/bash
#------------------------------------------------------------------------------
#
# Python for android
# https://github.com/tito/python-for-android
#
#------------------------------------------------------------------------------

# Modules
MODULES=

# Resolve Python path
PYTHON="$(which python2.7)"
if [ "X$PYTHON" == "X" ]; then
	PYTHON="$(which python2)"
fi
if [ "X$PYTHON" == "X" ]; then
	PYTHON="$(which python)"
fi

# Resolve pip path
PIP_NAME="$(which pip-2.7)"
if [ "X$PIP_NAME" == "X" ]; then
	PIP_NAME="$(which pip2.7)"
fi
if [ "X$PIP_NAME" == "X" ]; then
	PIP_NAME="$(which pip2)"
fi
if [ "X$PIP_NAME" == "X" ]; then
	PIP_NAME="$(which pip)"
fi

# Resolve virtualenv path
VIRTUALENV_NAME="$(which virtualenv-2.7)"
if [ "X$VIRTUALENV_NAME" == "X" ]; then
	VIRTUALENV_NAME="$(which virtualenv2.7)"
fi
if [ "X$VIRTUALENV_NAME" == "X" ]; then
	VIRTUALENV_NAME="$(which virtualenv2)"
fi
if [ "X$VIRTUALENV_NAME" == "X" ]; then
	VIRTUALENV_NAME="$(which virtualenv)"
fi

# Resolve Cython path
CYTHON="$(which cython2)"
if [ "X$CYTHON" == "X" ]; then
        CYTHON="$(which cython)"
fi

# Paths
ROOT_PATH="$(dirname $($PYTHON -c 'from __future__ import print_function; import os,sys;print(os.path.realpath(sys.argv[1]))' $0))"
RECIPES_PATH="$ROOT_PATH/recipes"
BUILD_PATH="$ROOT_PATH/build"
LIBS_PATH="$ROOT_PATH/build/libs"
JAVACLASS_PATH="$ROOT_PATH/build/java"
PACKAGES_PATH="${PACKAGES_PATH:-$ROOT_PATH/.packages}"
SRC_PATH="$ROOT_PATH/src"
JNI_PATH="$SRC_PATH/jni"
DIST_PATH="$ROOT_PATH/dist/default"
SITEPACKAGES_PATH="$BUILD_PATH/python-install/lib/python2.7/site-packages/"
HOSTPYTHON="$BUILD_PATH/python-install/bin/python.host"
CYTHON+=" -t"

# Tools
export LIBLINK_PATH="$BUILD_PATH/objects"
export LIBLINK="$ROOT_PATH/src/tools/liblink"
export BIGLINK="$ROOT_PATH/src/tools/biglink"
export PIP=$PIP_NAME
export VIRTUALENV=$VIRTUALENV_NAME

export COPYLIBS=0

MD5SUM=$(which md5sum)
if [ "X$MD5SUM" == "X" ]; then
	MD5SUM=$(which md5)
	if [ "X$MD5SUM" == "X" ]; then
		echo "Error: you need at least md5sum or md5 installed."
		exit 1
	else
		MD5SUM="$MD5SUM -r"
	fi
fi

WGET=$(which wget)
if [ "X$WGET" == "X" ]; then
	WGET=$(which curl)
	if [ "X$WGET" == "X" ]; then
		echo "Error: you need at least wget or curl installed."
		exit 1
	else
		WGET="$WGET -L -O -o"
	fi
	WHEAD="curl -L -I"
else
	WGET="$WGET -O"
	WHEAD="wget --spider -q -S"
fi

case $OSTYPE in
	darwin*)
		SED="sed -i ''"
		;;
	*)
		SED="sed -i"
		;;
esac


# Internals
CRED="\x1b[31;01m"
CBLUE="\x1b[34;01m"
CGRAY="\x1b[30;01m"
CRESET="\x1b[39;49;00m"
DO_CLEAN_BUILD=0
DO_SET_X=0

# Use ccache ?
which ccache &>/dev/null
if [ $? -eq 0 ]; then
	export CC="ccache gcc"
	export CXX="ccache g++"
	export NDK_CCACHE="ccache"
fi

function try () {
    "$@" || exit -1
}

function info() {
	echo -e "$CBLUE"$@"$CRESET";
}

function error() {
	echo -e "$CRED"$@"$CRESET";
}

function debug() {
	echo -e "$CGRAY"$@"$CRESET";
}

function get_directory() {
	case $1 in
		*.tar.gz)	directory=$(basename $1 .tar.gz) ;;
		*.tgz)		directory=$(basename $1 .tgz) ;;
		*.tar.bz2)	directory=$(basename $1 .tar.bz2) ;;
		*.tbz2)		directory=$(basename $1 .tbz2) ;;
		*.zip)		directory=$(basename $1 .zip) ;;
		*)
			error "Unknown file extension $1"
			exit -1
			;;
	esac
	echo $directory
}

function push_arm() {
	info "Entering in ARM environment"

	# save for pop
	export OLD_PATH=$PATH
	export OLD_CFLAGS=$CFLAGS
	export OLD_CXXFLAGS=$CXXFLAGS
	export OLD_LDFLAGS=$LDFLAGS
	export OLD_CC=$CC
	export OLD_CXX=$CXX
	export OLD_AR=$AR
	export OLD_RANLIB=$RANLIB
	export OLD_STRIP=$STRIP
	export OLD_MAKE=$MAKE
	export OLD_LD=$LD

	# to override the default optimization, set OFLAG
	#export OFLAG="-Os"
	#export OFLAG="-O2"

	export CFLAGS="-DANDROID -mandroid $OFLAG -fomit-frame-pointer --sysroot $NDKPLATFORM"
	if [ "X$ARCH" == "Xarmeabi-v7a" ]; then
		CFLAGS+=" -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -mthumb"
	fi
	export CXXFLAGS="$CFLAGS"

	# that could be done only for darwin platform, but it doesn't hurt.
	export LDFLAGS="-lm"

	# this must be something depending of the API level of Android
	PYPLATFORM=$($PYTHON -c 'from __future__ import print_function; import sys; print(sys.platform)')
	if [ "$PYPLATFORM" == "linux2" ]; then
		PYPLATFORM="linux"
	elif [ "$PYPLATFORM" == "linux3" ]; then
		PYPLATFORM="linux"
	fi

    if [ "X$ANDROIDNDKVER" == "Xr5b" ]; then
        export TOOLCHAIN_PREFIX=arm-eabi
        export TOOLCHAIN_VERSION=4.4.0
    elif [ "X${ANDROIDNDKVER:0:2}" == "Xr7" ] || [ "X${ANDROIDNDKVER:0:2}" == "Xr8" ]; then
        export TOOLCHAIN_PREFIX=arm-linux-androideabi
        export TOOLCHAIN_VERSION=4.4.3
    elif  [ "X${ANDROIDNDKVER:0:2}" == "Xr9" ]; then
        export TOOLCHAIN_PREFIX=arm-linux-androideabi
        export TOOLCHAIN_VERSION=4.8
    elif [ "X${ANDROIDNDKVER:0:3}" == "Xr10" ]; then
        export TOOLCHAIN_PREFIX=arm-linux-androideabi
        export TOOLCHAIN_VERSION=4.9
    else
        echo "Error: Please report issue to enable support for newer ndk."
        exit 1
    fi

	export PATH="$ANDROIDNDK/toolchains/$TOOLCHAIN_PREFIX-$TOOLCHAIN_VERSION/prebuilt/$PYPLATFORM-x86/bin/:$ANDROIDNDK/toolchains/$TOOLCHAIN_PREFIX-$TOOLCHAIN_VERSION/prebuilt/$PYPLATFORM-x86_64/bin/:$ANDROIDNDK:$ANDROIDSDK/tools:$PATH"

	# search compiler in the path, to fail now instead of later.
	CC=$(which $TOOLCHAIN_PREFIX-gcc)
	if [ "X$CC" == "X" ]; then
		error "Unable to find compiler ($TOOLCHAIN_PREFIX-gcc) !!"
		error "1. Ensure that SDK/NDK paths are correct"
		error "2. Ensure that you've the Android API $ANDROIDAPI SDK Platform (via android tool)"
		exit 1
	else
		debug "Compiler found at $CC"
	fi

	export CC="$TOOLCHAIN_PREFIX-gcc $CFLAGS"
	export CXX="$TOOLCHAIN_PREFIX-g++ $CXXFLAGS"
	export AR="$TOOLCHAIN_PREFIX-ar" 
	export RANLIB="$TOOLCHAIN_PREFIX-ranlib"
	export LD="$TOOLCHAIN_PREFIX-ld"
	export STRIP="$TOOLCHAIN_PREFIX-strip --strip-unneeded"
	export MAKE="make -j5"
	export READELF="$TOOLCHAIN_PREFIX-readelf"

	# This will need to be updated to support Python versions other than 2.7
	export BUILDLIB_PATH="$BUILD_hostpython/build/lib.linux-`uname -m`-2.7/"

	# Use ccache ?
	which ccache &>/dev/null
	if [ $? -eq 0 ]; then
		export CC="ccache $CC"
		export CXX="ccache $CXX"
	fi
}

function pop_arm() {
	info "Leaving ARM enviromnent"
	export PATH=$OLD_PATH
	export CFLAGS=$OLD_CFLAGS
	export CXXFLAGS=$OLD_CXXFLAGS
	export LDFLAGS=$OLD_LDFLAGS
	export CC=$OLD_CC
	export CXX=$OLD_CXX
	export AR=$OLD_AR
	export LD=$OLD_LD
	export RANLIB=$OLD_RANLIB
	export STRIP=$OLD_STRIP
	export MAKE=$OLD_MAKE
}

function usage() {
	echo "Python for android - distribute.sh"
	echo 
	echo "Usage:   ./distribute.sh [options]"
	echo
	echo "  -d directory           Name of the distribution directory"
	echo "  -h                     Show this help"
	echo "  -l                     Show a list of available modules"
	echo "  -m 'mod1 mod2'         Modules to include"
	echo "  -f                     Restart from scratch (remove the current build)"
	echo "  -x                     display expanded values (execute 'set -x')"
	echo
	echo "Advanced:"
	echo "  -C                     Copy libraries instead of using biglink"
	echo "                         (may not work before Android 4.3)"
	echo
	echo "For developers:"
	echo "  -u 'mod1 mod2'         Modules to update (if already compiled)"
	echo
	exit 0
}

# Check installation state of a debian package list.
# Return all missing packages.
function check_pkg_deb_installed() {
    PKGS=$1
    MISSING_PKGS=""
    for PKG in $PKGS; do
        CHECK=$(dpkg -s $PKG 2>&1)
        if [ $? -eq 1 ]; then
           MISSING_PKGS="$PKG $MISSING_PKGS"
        fi
    done
	if [ "X$MISSING_PKGS" != "X" ]; then
		error "Packages missing: $MISSING_PKGS"
		error "It might break the compilation, except if you installed thoses packages manually."
	fi
}

function check_build_deps() {
    DIST=$(lsb_release -is)
	info "Check build dependencies for $DIST"
    case $DIST in
		Debian|Ubuntu|LinuxMint)
			check_pkg_deb_installed "build-essential zlib1g-dev cython"
			;;
		*)
			debug "Avoid check build dependencies, unknow platform $DIST"
			;;
	esac
}

function run_prepare() {
	info "Check enviromnent"
	if [ "X$ANDROIDSDK" == "X" ]; then
		error "No ANDROIDSDK environment set, abort"
		exit -1
	fi
	if [ ! -d "$ANDROIDSDK" ]; then
		echo "ANDROIDSDK=$ANDROIDSDK"
		error "ANDROIDSDK path is invalid, it must be a directory. abort."
		exit 1
	fi

	if [ "X$ANDROIDNDK" == "X" ]; then
		error "No ANDROIDNDK environment set, abort"
		exit -1
	fi
	if [ ! -d "$ANDROIDNDK" ]; then
		echo "ANDROIDNDK=$ANDROIDNDK"
		error "ANDROIDNDK path is invalid, it must be a directory. abort."
		exit 1
	fi

	if [ "X$ANDROIDAPI" == "X" ]; then
		export ANDROIDAPI=14
	fi

	if [ "X$ANDROIDNDKVER" == "X" ]; then
		error "No ANDROIDNDKVER enviroment set, abort"
		error "(Must be something like 'r5b', 'r7'...)"
		exit -1
	fi

	if [ "X$MODULES" == "X" ]; then
		usage
		exit 0
	fi

	debug "SDK located at $ANDROIDSDK"
	debug "NDK located at $ANDROIDNDK"
	debug "NDK version is $ANDROIDNDKVER"
	debug "API level set to $ANDROIDAPI"

	export NDKPLATFORM="$ANDROIDNDK/platforms/android-$ANDROIDAPI/arch-arm"
	export ARCH="armeabi"
	#export ARCH="armeabi-v7a" # not tested yet.

	info "Check mandatory tools"
	# ensure that some tools are existing
	for tool in tar bzip2 unzip make gcc g++; do
		which $tool &>/dev/null
		if [ $? -ne 0 ]; then
			error "Tool $tool is missing"
			exit -1
		fi
	done

	if [ "$COPYLIBS" == "1" ]; then
		info "Library files will be copied to the distribution (no biglink)"
		error "NOTICE: This option is still beta!"
		error "\tIf you encounter an error 'Failed to locate needed libraries!' and"
		error "\tthe libraries listed are not supposed to be provided by your app or"
		error "\tits dependencies, please submit a bug report at"
		error "\thttps://github.com/kivy/python-for-android/issues"
	fi

	info "Distribution will be located at $DIST_PATH"
	if [ -e "$DIST_PATH" ]; then
		error "The distribution $DIST_PATH already exist"
		error "Press a key to remove it, or Control + C to abort."
		read
		try rm -rf "$DIST_PATH"
	fi
	try mkdir -p "$DIST_PATH"

	if [ $DO_CLEAN_BUILD -eq 1 ]; then
		info "Cleaning build"
		try rm -rf $BUILD_PATH
		try rm -rf $SRC_PATH/obj
		try rm -rf $SRC_PATH/libs
		pushd $JNI_PATH
		push_arm
		try ndk-build clean
		pop_arm
		popd
	fi

	# create build directory if not found
	test -d $PACKAGES_PATH || mkdir -p $PACKAGES_PATH
	test -d $BUILD_PATH || mkdir -p $BUILD_PATH
	test -d $LIBS_PATH || mkdir -p $LIBS_PATH
	test -d $JAVACLASS_PATH || mkdir -p $JAVACLASS_PATH
	test -d $LIBLINK_PATH || mkdir -p $LIBLINK_PATH

	# create initial files
	echo "target=android-$ANDROIDAPI" > $SRC_PATH/default.properties
	echo "sdk.dir=$ANDROIDSDK" > $SRC_PATH/local.properties

	# copy the initial blacklist in build
	try cp -a $SRC_PATH/blacklist.txt $BUILD_PATH
	try cp -a $SRC_PATH/whitelist.txt $BUILD_PATH

	# check arm env
	push_arm
	debug "PATH is $PATH"
	pop_arm
}

function in_array() {
	term="$1"
	shift
	i=0
	for key in $@; do
		if [ $term == $key ]; then
			return $i
		fi
		i=$(($i + 1))
	done
	return 255
}

function run_source_modules() {
	# preprocess version modules
	needed=($MODULES)
	while [ ${#needed[*]} -ne 0 ]; do

		# pop module from the needed list
		module=${needed[0]}
		unset needed[0]
		needed=( ${needed[@]} )

		# is a version is specified ?
		items=( ${module//==/ } )
		module=${items[0]}
		version=${items[1]}
		if [ ! -z "$version" ]; then
			info "Specific version detected for $module: $version"
			eval "VERSION_$module=$version"
		fi
	done


	needed=($MODULES)
	declare -a processed
	declare -a pymodules

	fn_deps='.deps'
	fn_optional_deps='.optional-deps'

	> $fn_deps
	> $fn_optional_deps

	while [ ${#needed[*]} -ne 0 ]; do

		# pop module from the needed list
		module=${needed[0]}
		original_module=${needed[0]}
		unset needed[0]
		needed=( ${needed[@]} )

		# split the version if exist
		items=( ${module//==/ } )
		module=${items[0]}
		version=${items[1]}

		# check if the module have already been declared
		in_array $module "${processed[@]}"
		if [ $? -ne 255 ]; then
			debug "Ignored $module, already processed"
			continue;
		fi

		# add this module as done
		processed=( ${processed[@]} $module )

		# read recipe
		debug "Read $module recipe"
		recipe=$RECIPES_PATH/$module/recipe.sh
		if [ ! -f $recipe ]; then
			error "Recipe $module does not exist, adding the module as pure-python package"
			pymodules+=($original_module)
			continue;
		fi
		source $RECIPES_PATH/$module/recipe.sh

		# if a version has been specified by the user, the md5 will not
		# correspond at all. so deactivate it.
		if [ ! -z "$version" ]; then
			debug "Deactivate MD5 test for $module, due to specific version"
			eval "MD5_$module="
		fi

		# append current module deps to the needed
		deps=$(echo \$"{DEPS_$module[@]}")
		eval deps=($deps)
		optional_deps=$(echo \$"{DEPS_OPTIONAL_$module[@]}")
		eval optional_deps=($optional_deps)
		if [ ${#deps[*]} -gt 0 ]; then
			debug "Module $module depend on" ${deps[@]}
			needed=( ${needed[@]} ${deps[@]} )
			echo $module ${deps[@]} >> $fn_deps
		else
			echo $module >> $fn_deps
		fi
		if [ ${#optional_deps[*]} -gt 0 ]; then
			echo $module ${optional_deps[@]} >> $fn_optional_deps
		fi
	done

	MODULES="$($PYTHON tools/depsort.py --optional $fn_optional_deps < $fn_deps)"

	info "Modules changed to $MODULES"

	PYMODULES="${pymodules[@]}"

	info "Pure-Python modules changed to $PYMODULES"
}

function run_get_packages() {
	info "Run get packages"

	for module in $MODULES; do
		# download dependencies for this module
		# check if there is not an overload from environment
		module_dir=$(eval "echo \$P4A_${module}_DIR")
		if [ "$module_dir" ]
		then
			debug "\$P4A_${module}_DIR is not empty, linking $module_dir dir instead of downloading"
			directory=$(eval "echo \$BUILD_${module}")
			if [ -e $directory ]; then
				try rm -rf "$directory"
			fi
			try mkdir -p "$directory"
			try rmdir "$directory"
			try ln -s "$module_dir" "$directory"
			continue
		fi
		debug "Download package for $module"

		url="URL_$module"
		url=${!url}
		md5="MD5_$module"
		md5=${!md5}

		if [ ! -d "$BUILD_PATH/$module" ]; then
			try mkdir -p $BUILD_PATH/$module
		fi

		if [ ! -d "$PACKAGES_PATH/$module" ]; then
			try mkdir -p "$PACKAGES_PATH/$module"
		fi

		if [ "X$url" == "X" ]; then
			debug "No package for $module"
			continue
		fi

		filename=$(basename $url)
		marker_filename=".mark-$filename"
		do_download=1

		cd "$PACKAGES_PATH/$module"

		# check if the file is already present
		if [ -f $filename ]; then
			# if the marker has not been set, it might be cause of a invalid download.
			if [ ! -f $marker_filename ]; then
				rm $filename
			elif [ -n "$md5" ]; then
				# check if the md5 is correct
				current_md5=$($MD5SUM $filename | cut -d\  -f1)
				if [ "X$current_md5" == "X$md5" ]; then
					# correct, no need to download
					do_download=0
				else
					# invalid download, remove the file
					error "Module $module have invalid md5, redownload."
					rm $filename
				fi
			else
				do_download=0
			fi
		fi

		# check if the file HEAD in case of, only if there is no MD5 to check.
		check_headers=0
		if [ -z "$md5" ]; then
			if [ "X$DO_CLEAN_BUILD" == "X1" ]; then
				check_headers=1
			elif [ ! -f $filename ]; then
				check_headers=1
			fi
		fi

		if [ "X$check_headers" == "X1" ]; then
			debug "Checking if $url changed"
			$WHEAD $url &> .headers-$filename
			$PYTHON "$ROOT_PATH/tools/check_headers.py" .headers-$filename .sig-$filename
			if [ $? -ne 0 ]; then
				do_download=1
			fi
		fi

		# download if needed
		if [ $do_download -eq 1 ]; then
			info "Downloading $url"
			try rm -f $marker_filename
			try $WGET $filename $url
			touch $marker_filename
		else
			debug "Module $module already downloaded"
		fi

		# check md5
		if [ -n "$md5" ]; then
			current_md5=$($MD5SUM $filename | cut -d\  -f1)
			if [ "X$current_md5" != "X$md5" ]; then
				error "File $filename md5 check failed (got $current_md5 instead of $md5)."
				error "Ensure the file is correctly downloaded, and update MD5S_$module"
				exit -1
			fi
		fi

		# if already decompress, forget it
		cd $BUILD_PATH/$module
		directory=$(get_directory $filename)
		if [ -d "$directory" ]; then
			continue
		fi

		# decompress
		pfilename=$PACKAGES_PATH/$module/$filename
		info "Extract $pfilename"
		case $pfilename in
			*.tar.gz|*.tgz )
				try tar xzf $pfilename
				root_directory=$(basename $(try tar tzf $pfilename|head -n1))
				if [ "X$root_directory" != "X$directory" ]; then
					mv $root_directory $directory
				fi
				;;
			*.tar.bz2|*.tbz2 )
				try tar xjf $pfilename
				root_directory=$(basename $(try tar tjf $pfilename|head -n1))
				if [ "X$root_directory" != "X$directory" ]; then
					mv $root_directory $directory
				fi
				;;
			*.zip )
				try unzip $pfilename
				root_directory=$(basename $(try unzip -l $pfilename|sed -n 5p|awk '{print $4}'))
				if [ "X$root_directory" != "X$directory" ]; then
					mv $root_directory $directory
				fi
				;;
		esac
	done
}

function run_prebuild() {
	info "Run prebuild"
	cd $BUILD_PATH
	for module in $MODULES; do
		fn=$(echo prebuild_$module)
		debug "Call $fn"
		$fn
	done
}

function run_build() {
	info "Run build"

	modules_update=($MODULES_UPDATE)

	cd $BUILD_PATH

	for module in $MODULES; do
		fn="build_$module"
		shouldbuildfn="shouldbuild_$module"
		MARKER_FN="$BUILD_PATH/.mark-$module"

		# if the module should be updated, then remove the marker.
		in_array $module "${modules_update[@]}"
		if [ $? -ne 255 ]; then
			debug "$module detected to be updated"
			rm -f "$MARKER_FN"
		fi

		# if shouldbuild_$module exist, call it to see if the module want to be
		# built again
		DO_BUILD=1
		if [ "$(type -t $shouldbuildfn)" == "function" ]; then
			$shouldbuildfn
		fi

		# if the module should be build, or if the marker is not present,
		# do the build
		if [ "X$DO_BUILD" == "X1" ] || [ ! -f "$MARKER_FN" ]; then
			debug "Call $fn"
			rm -f "$MARKER_FN"
			$fn
			touch "$MARKER_FN"
		else
			debug "Skipped $fn"
		fi
	done
}

function run_postbuild() {
	info "Run postbuild"
	cd $BUILD_PATH
	for module in $MODULES; do
		fn=$(echo postbuild_$module)
		debug "Call $fn"
		$fn
	done
}

function run_pymodules_install() {
	info "Run pymodules install"
	if [ "X$PYMODULES" == "X" ]; then
		debug "No pymodules to install"
		return
	fi

	cd "$BUILD_PATH"

	debug "We want to install: $PYMODULES"

	debug "Check if $VIRTUALENV and $PIP are present"
	for tool in $VIRTUALENV $PIP; do
		which $tool &>/dev/null
		if [ $? -ne 0 ]; then
			error "Tool $tool is missing"
			exit -1
		fi
	done
	
	debug "Check if virtualenv is existing"
	if [ ! -d venv ]; then
		debug "Installing virtualenv"
		try $VIRTUALENV --python=python2.7 venv
	fi

	debug "Create a requirement file for pure-python modules"
	try echo "" > requirements.txt
	for mod in $PYMODULES; do
		echo $mod >> requirements.txt
	done

	debug "Install pure-python modules via pip in venv"
	try bash -c "source venv/bin/activate && env CC=/bin/false CXX=/bin/false pip install --target '$SITEPACKAGES_PATH' --download-cache '$PACKAGES_PATH' -r requirements.txt"

}

function run_distribute() {
	info "Run distribute"

	cd "$DIST_PATH"

	debug "Create initial layout"
	try mkdir assets bin private res templates

	debug "Copy default files"
	try cp -a $SRC_PATH/default.properties .
	try cp -a $SRC_PATH/local.properties .
	try cp -a $SRC_PATH/build.py .
	try cp -a $SRC_PATH/buildlib .
	try cp -a $SRC_PATH/src .
	try cp -a $SRC_PATH/templates .
	try cp -a $SRC_PATH/res .
	try cp -a $BUILD_PATH/blacklist.txt .
	try cp -a $BUILD_PATH/whitelist.txt .

	debug "Copy python distribution"
	$HOSTPYTHON -OO -m compileall $BUILD_PATH/python-install
	try cp -a $BUILD_PATH/python-install .

	debug "Copy libs"
	try mkdir -p libs/$ARCH
	try cp -a $BUILD_PATH/libs/* libs/$ARCH/

	debug "Copy java files from various libs"
	cp -a $BUILD_PATH/java/* src

	debug "Fill private directory"
	try cp -a python-install/lib private/
	try mkdir -p private/include/python2.7
	
	if [ "$COPYLIBS" == "1" ]; then
		if [ -s "libs/$ARCH/copylibs" ]; then
			try sh -c "cat libs/$ARCH/copylibs | xargs -d'\n' cp -t private/"
		fi
	else
		try mv libs/$ARCH/libpymodules.so private/
	fi
	try cp python-install/include/python2.7/pyconfig.h private/include/python2.7/

	debug "Reduce private directory from unwanted files"
	try rm -f "$DIST_PATH"/private/lib/libpython2.7.so
	try rm -rf "$DIST_PATH"/private/lib/pkgconfig
	try cd "$DIST_PATH"/private/lib/python2.7
	try find . | grep -E '*\.(py|pyc|so\.o|so\.a|so\.libs)$' | xargs rm

	# we are sure that all of theses will be never used on android (well...)
	try rm -rf ctypes
	try rm -rf lib2to3
	try rm -rf idlelib
	try rm -rf config/libpython*.a
	try rm -rf config/python.o
	try rm -rf lib-dynload/_ctypes_test.so
	try rm -rf lib-dynload/_testcapi.so

	debug "Strip libraries"
	push_arm
	try find "$DIST_PATH"/private "$DIST_PATH"/libs -iname '*.so' -exec $STRIP {} \;
	pop_arm

}

function run_biglink() {
	push_arm
	if [ "$COPYLIBS" == "0" ]; then
		try $BIGLINK $LIBS_PATH/libpymodules.so $LIBLINK_PATH
	else
		try $BIGLINK $LIBS_PATH/copylibs $LIBLINK_PATH
	fi
	pop_arm
}

function run() {
	check_build_deps
	run_prepare
	run_source_modules
	run_get_packages
	run_prebuild
	run_build
	run_biglink
	run_postbuild
	run_pymodules_install
	run_distribute
	info "All done !"
}

function list_modules() {
	modules=$(find recipes -iname 'recipe.sh' | cut -d/ -f2 | sort -u | xargs echo)
	echo "Available modules: $modules"
	exit 0
}

# one method to deduplicate some symbol in libraries
function arm_deduplicate() {
	fn=$(basename $1)
	echo "== Trying to remove duplicate symbol in $1"
	push_arm
	try mkdir ddp
	try cd ddp
	try $AR x $1
	try $AR rc $fn *.o
	try $RANLIB $fn
	try mv -f $fn $1
	try cd ..
	try rm -rf ddp
	pop_arm
}


# Do the build
while getopts ":hCvlfxm:u:d:s" opt; do
	case $opt in
		h)
			usage
			;;
		C)
			COPYLIBS=1
			LIBLINK=${LIBLINK}-jb
			BIGLINK=${BIGLINK}-jb
			;;
		l)
			list_modules
			;;
		s)
			run_prepare
			run_source_modules
			push_arm
			bash
			pop_arm
			exit 0
			;;
		m)
			MODULES="$OPTARG"
			;;
		u)
			MODULES_UPDATE="$OPTARG"
			;;
		d)
			DIST_PATH="$ROOT_PATH/dist/$OPTARG"
			;;
		f)
			DO_CLEAN_BUILD=1
			;;
		x)
			DO_SET_X=1
			;;
		\?)
			echo "Invalid option: -$OPTARG" >&2
			exit 1
			;;
		:)
			echo "Option -$OPTARG requires an argument." >&2
			exit 1
			;;

		*)
			echo "=> $OPTARG"
			;;
	esac
done

if [ $DO_SET_X -eq 1 ]; then
	info "Set -x for displaying expanded values"
	set -x
fi

run
