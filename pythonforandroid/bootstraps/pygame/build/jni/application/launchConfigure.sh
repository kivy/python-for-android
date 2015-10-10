#!/bin/sh

# Set here your own NDK path if needed
# export PATH=$PATH:~/src/endless_space/android-ndk-r4

IFS='
'

NDK=`which ndk-build`
NDK=`dirname $NDK`
GCCVER=4.4.0
PLATFORMVER=android-8
LOCAL_PATH=`dirname $0`
LOCAL_PATH=`cd $LOCAL_PATH && pwd`

# Hacks for broken configure scripts
ln -sf libsdl_mixer.so $LOCAL_PATH/../../bin/ndk/local/armeabi/libSDL_mixer.so
ln -sf libsdl_mixer.so $LOCAL_PATH/../../bin/ndk/local/armeabi/libSDL_Mixer.so
ln -sf libsdl_net.so $LOCAL_PATH/../../bin/ndk/local/armeabi/libSDL_net.so

CFLAGS="-I$NDK/build/platforms/$PLATFORMVER/arch-arm/usr/include \
-fpic -mthumb-interwork -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums \
-D__ARM_ARCH_5__ -D__ARM_ARCH_5T__ -D__ARM_ARCH_5E__ -D__ARM_ARCH_5TE__ -DANDROID \
-Wno-psabi -march=armv5te -mtune=xscale -msoft-float -fno-exceptions -fno-rtti -mthumb -Os \
-fomit-frame-pointer -fno-strict-aliasing -finline-limit=64 \
-Wa,--noexecstack -O2 -DNDEBUG -g \
`grep '[-]I[$][(]LOCAL_PATH[)]/[.][.]/' $LOCAL_PATH/Android.mk | tr '\n' ' ' | sed 's/[\\]//g' | sed \"s@[\$][(]LOCAL_PATH[)]/@$LOCAL_PATH/@g\" | sed 's/[	 ][	 ]*/ /g'`"

LDFLAGS="-nostdlib -Wl,-soname,libapplication.so -Wl,-shared,-Bsymbolic \
-Wl,--whole-archive  -Wl,--no-whole-archive \
$NDK/build/prebuilt/linux-x86/arm-eabi-$GCCVER/lib/gcc/arm-eabi/4.4.0/libgcc.a \
`echo $LOCAL_PATH/../../bin/ndk/local/armeabi/*.so | sed "s@$LOCAL_PATH/../../bin/ndk/local/armeabi/libsdl_main.so@@" | sed "s@$LOCAL_PATH/../../bin/ndk/local/armeabi/libapplication.so@@"` \
$NDK/build/platforms/$PLATFORMVER/arch-arm/usr/lib/libc.so \
$NDK/build/platforms/$PLATFORMVER/arch-arm/usr/lib/libstdc++.so \
$NDK/build/platforms/$PLATFORMVER/arch-arm/usr/lib/libm.so \
-Wl,--no-undefined -Wl,-z,noexecstack \
-L$NDK/build/platforms/$PLATFORMVER/arch-arm/usr/lib \
-lGLESv1_CM -ldl -llog -lz \
-Wl,-rpath-link=$NDK/build/platforms/$PLATFORMVER/arch-arm/usr/lib \
-L$LOCAL_PATH/../../bin/ndk/local/armeabi"

env PATH=$NDK/build/prebuilt/linux-x86/arm-eabi-$GCCVER/bin:$LOCAL_PATH:$PATH \
CFLAGS="$CFLAGS" \
CXXFLAGS="$CFLAGS" \
LDFLAGS="$LDFLAGS" \
CC="$NDK/build/prebuilt/linux-x86/arm-eabi-$GCCVER/bin/arm-eabi-gcc" \
CXX="$NDK/build/prebuilt/linux-x86/arm-eabi-$GCCVER/bin/arm-eabi-g++" \
RANLIB="$NDK/build/prebuilt/linux-x86/arm-eabi-$GCCVER/bin/arm-eabi-ranlib" \
LD="$NDK/build/prebuilt/linux-x86/arm-eabi-$GCCVER/bin/arm-eabi-gcc" \
AR="$NDK/build/prebuilt/linux-x86/arm-eabi-$GCCVER/bin/arm-eabi-ar" \
CPP="$NDK/build/prebuilt/linux-x86/arm-eabi-$GCCVER/bin/arm-eabi-cpp $CFLAGS" \
NM="$NDK/build/prebuilt/linux-x86/arm-eabi-$GCCVER/bin/arm-eabi-nm" \
AS="$NDK/build/prebuilt/linux-x86/arm-eabi-$GCCVER/bin/arm-eabi-as" \
STRIP="$NDK/build/prebuilt/linux-x86/arm-eabi-$GCCVER/bin/arm-eabi-strip" \
./configure --host=arm-eabi "$@"
