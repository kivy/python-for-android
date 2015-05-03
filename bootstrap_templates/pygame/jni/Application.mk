APP_PROJECT_PATH := $(call my-dir)/..

# Available libraries: mad sdl_mixer sdl_image sdl_ttf sdl_net sdl_blitpool sdl_gfx intl
# sdl_mixer depends on tremor and optionally mad
# sdl_image depends on png and jpeg
# sdl_ttf depends on freetype

APP_MODULES := application sdl sdl_main tremor png jpeg freetype sdl_ttf sdl_image sqlite3

APP_ABI := $(ARCH)
APP_STL := gnustl_static
APP_CFLAGS += $(OFLAG)
