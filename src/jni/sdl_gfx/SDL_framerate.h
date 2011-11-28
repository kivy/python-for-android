
/*

SDL_framerate: framerate manager

LGPL (c) A. Schiffler

*/

#ifndef _SDL_framerate_h
#define _SDL_framerate_h

/* Set up for C function definitions, even when using C++ */
#ifdef __cplusplus
extern "C" {
#endif

	/* --- */

#include "SDL.h"

	/* --------- Definitions */

/*!
\brief Highest possible rate supported by framerate controller in Hz (1/s).
*/
#define FPS_UPPER_LIMIT		200

/*!
\brief Lowest possible rate supported by framerate controller in Hz (1/s).
*/
#define FPS_LOWER_LIMIT		1

/*!
\brief Default rate of framerate controller in Hz (1/s).
*/
#define FPS_DEFAULT		30

/*! 
\brief Structure holding the state and timing information of the framerate controller. 
*/
	typedef struct {
		Uint32 framecount;
		float rateticks;
		Uint32 lastticks;
		Uint32 rate;
	} FPSmanager;

	/* --------- Function prototypes */

#ifdef WIN32
#  ifdef DLL_EXPORT
#    define SDL_FRAMERATE_SCOPE __declspec(dllexport)
#  else
#    ifdef LIBSDL_GFX_DLL_IMPORT
#      define SDL_FRAMERATE_SCOPE __declspec(dllimport)
#    endif
#  endif
#endif
#ifndef SDL_FRAMERATE_SCOPE
#  define SDL_FRAMERATE_SCOPE extern
#endif

	/* Functions return 0 or value for sucess and -1 for error */

	SDL_FRAMERATE_SCOPE void SDL_initFramerate(FPSmanager * manager);
	SDL_FRAMERATE_SCOPE int SDL_setFramerate(FPSmanager * manager, int rate);
	SDL_FRAMERATE_SCOPE int SDL_getFramerate(FPSmanager * manager);
	SDL_FRAMERATE_SCOPE int SDL_getFramecount(FPSmanager * manager);
	SDL_FRAMERATE_SCOPE void SDL_framerateDelay(FPSmanager * manager);

	/* --- */

	/* Ends C function definitions when using C++ */
#ifdef __cplusplus
}
#endif

#endif				/* _SDL_framerate_h */
