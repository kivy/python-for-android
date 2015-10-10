
# The namespace in Java file, with dots replaced with underscores
SDL_JAVA_PACKAGE_PATH := org_renpy_android

# Path to shared libraries - Android 1.6 cannot load them properly, thus we have to specify absolute path here
# SDL_SHARED_LIBRARIES_PATH := /data/data/de.schwardtnet.alienblaster/lib

# Path to files with application data - they should be downloaded from Internet on first app run inside
# Java sources, or unpacked from resources (TODO)
# Typically /sdcard/alienblaster 
# Or /data/data/de.schwardtnet.alienblaster/files if you're planning to unpack data in application private folder
# Your application will just set current directory there
SDL_CURDIR_PATH := org.renpy.android

# Android Dev Phone G1 has trackball instead of cursor keys, and 
# sends trackball movement events as rapid KeyDown/KeyUp events,
# this will make Up/Down/Left/Right key up events with X frames delay,
# so if application expects you to press and hold button it will process the event correctly.
# TODO: create a libsdl config file for that option and for key mapping/on-screen keyboard
SDL_TRACKBALL_KEYUP_DELAY := 1

# If the application designed for higher screen resolution enable this to get the screen
# resized in HW-accelerated way, however it eats a tiny bit of CPU
SDL_VIDEO_RENDER_RESIZE := 0

COMPILED_LIBRARIES := sdl_ttf sdl_image sdl_mixer

APPLICATION_ADDITIONAL_CFLAGS := -finline-functions -O2 -DSDL_JAVA_PACKAGE_PATH=$(SDL_JAVA_PACKAGE_PATH)

APPLICATION_ADDITIONAL_LDFLAGS := -Xlinker -export-dynamic -Wl,-O1 -Wl,-Bsymbolic-functions

SDL_ADDITIONAL_CFLAGS := -DSDL_ANDROID_KEYCODE_MOUSE=UNKNOWN -DSDL_ANDROID_KEYCODE_0=SPACE -DSDL_ANDROID_KEYCODE_1=RETURN -DSDL_ANDROID_KEYCODE_2=LCTRL -DSDL_ANDROID_KEYCODE_3=LALT -DSDL_ANDROID_KEYCODE_4=RETURN

# If SDL_Mixer should link to libMAD
SDL_MIXER_USE_LIBMAD :=
ifneq ($(strip $(filter mad, $(COMPILED_LIBRARIES))),)
SDL_MIXER_USE_LIBMAD := 1
endif

include $(call all-subdir-makefiles)
