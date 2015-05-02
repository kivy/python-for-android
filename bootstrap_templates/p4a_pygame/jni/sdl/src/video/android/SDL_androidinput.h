/*
    SDL - Simple DirectMedia Layer
    Copyright (C) 1997-2009 Sam Lantinga

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

    Sam Lantinga
    slouken@libsdl.org
*/
#ifndef _SDL_ANDROIDINPUT_H_
#define _SDL_ANDROIDINPUT_H_

#include "SDL_config.h"

#include "SDL_version.h"
#include "SDL_video.h"
#include "SDL_mouse.h"
#include "SDL_mutex.h"
#include "SDL_thread.h"
#include "../SDL_sysvideo.h"
#include "../SDL_pixels_c.h"
#include "SDL_events.h"
#if (SDL_VERSION_ATLEAST(1,3,0))
#include "../../events/SDL_events_c.h"
#include "../../events/SDL_keyboard_c.h"
#include "../../events/SDL_mouse_c.h"
#include "SDL_scancode.h"
#include "SDL_compat.h"
#else
#include "SDL_keysym.h"
#include "../../events/SDL_events_c.h"
#endif
#include "SDL_joystick.h"
#include "../../joystick/SDL_sysjoystick.h"
#include "../../joystick/SDL_joystick_c.h"

#include "../SDL_sysvideo.h"
#include "SDL_androidvideo.h"
#include "javakeycodes.h"
#include <android/log.h>

extern SDLKey SDL_android_keymap[KEYCODE_LAST+1];

/* JNI-C++ wrapper stuff */

#if SDL_VERSION_ATLEAST(1,3,0)

#define SDL_KEY2(X) SDL_SCANCODE_ ## X
#define SDL_KEY(X) SDL_KEY2(X)

static inline SDL_scancode TranslateKey(int scancode, SDL_keysym *keysym)
{
	if ( scancode >= SDL_arraysize(SDL_android_keymap) )
		scancode = KEYCODE_UNKNOWN;

        return SDL_android_keymap[scancode];
}

static inline SDL_scancode GetKeysym(SDL_scancode scancode, SDL_keysym *keysym)
{
	return scancode;
}

#define SDL_SendKeyboardKey(X, Y) SDL_SendKeyboardKey(X, Y, SDL_FALSE)

#else

#define SDL_KEY2(X) SDLK_ ## X
#define SDL_KEY(X) SDL_KEY2(X)

#define SDL_SendKeyboardKey SDL_PrivateKeyboard

// Randomly redefining SDL 1.3 scancodes to SDL 1.2 keycodes
#define KP_0 KP0
#define KP_1 KP1
#define KP_2 KP2
#define KP_3 KP3
#define KP_4 KP4
#define KP_5 KP5
#define KP_6 KP6
#define KP_7 KP7
#define KP_8 KP8
#define KP_9 KP9
#define NUMLOCKCLEAR NUMLOCK
#define GRAVE DOLLAR
#define APOSTROPHE QUOTE
#define LGUI LMETA
// Overkill haha
#define A a
#define B b
#define C c
#define D d
#define E e
#define F f
#define G g
#define H h
#define I i
#define J j
#define K k
#define L l
#define M m
#define N n
#define O o
#define P p
#define Q q
#define R r
#define S s
#define T t
#define U u
#define V v
#define W w
#define X x
#define Y y
#define Z z

#define SDL_scancode SDLKey
#define SDL_GetKeyboardState SDL_GetKeyState

static inline SDL_keysym *TranslateKey(int scancode, SDL_keysym *keysym)
{
	/* Sanity check */
	if ( scancode >= SDL_arraysize(SDL_android_keymap) )
		scancode = KEYCODE_UNKNOWN;

	/* Set the keysym information */
	keysym->scancode = scancode;
	keysym->sym = SDL_android_keymap[scancode];
	keysym->mod = KMOD_NONE;

	/* If UNICODE is on, get the UNICODE value for the key */
	keysym->unicode = 0;
	/* XXX This is wrong. Cause android keysym != unicode. Instead, use the unicode
	 * from android toolkit.
	 */
#if 0
	if ( SDL_TranslateUNICODE && keysym->sym >= 0x20) {
            /* Populate the unicode field with the ASCII value */
            keysym->unicode = scancode;
	}
#endif

	return(keysym);
}

static inline SDL_keysym *GetKeysym(SDLKey scancode, SDL_keysym *keysym)
{
	/* Sanity check */

	/* Set the keysym information */
	keysym->scancode = scancode;
	keysym->sym = scancode;
	keysym->mod = KMOD_NONE;

	/* If UNICODE is on, get the UNICODE value for the key */
	keysym->unicode = 0;
	/* XXX This is wrong, check TranslateKey.
	 */
#if 0
	if ( SDL_TranslateUNICODE ) {
		/* Populate the unicode field with the ASCII value */
		keysym->unicode = scancode;
	}
#endif
	return(keysym);
}

#endif

#define SDL_KEY_VAL(X) X

enum MOUSE_ACTION { MOUSE_DOWN = 0, MOUSE_UP=1, MOUSE_MOVE=2 };

enum { MAX_MULTITOUCH_POINTERS = 16 };

extern int SDL_android_processTouchscreenKeyboard(int x, int y, int action, int pointerId);

#ifndef SDL_ANDROID_KEYCODE_0
#define SDL_ANDROID_KEYCODE_0 RETURN
#endif
#ifndef SDL_ANDROID_KEYCODE_1
#define SDL_ANDROID_KEYCODE_1 END
#endif
#ifndef SDL_ANDROID_KEYCODE_2
#define SDL_ANDROID_KEYCODE_2 PAGEUP
#endif
#ifndef SDL_ANDROID_KEYCODE_3
#define SDL_ANDROID_KEYCODE_3 PAGEDOWN
#endif
#ifndef SDL_ANDROID_KEYCODE_4
#define SDL_ANDROID_KEYCODE_4 LCTRL
#endif
#ifndef SDL_ANDROID_KEYCODE_5
#define SDL_ANDROID_KEYCODE_5 ESCAPE
#endif
#ifndef SDL_ANDROID_KEYCODE_6
#define SDL_ANDROID_KEYCODE_6 RSHIFT
#endif
#ifndef SDL_ANDROID_KEYCODE_7
#define SDL_ANDROID_KEYCODE_7 RETURN
#endif
#ifndef SDL_ANDROID_KEYCODE_8
#define SDL_ANDROID_KEYCODE_8 DELETE
#endif

#endif
