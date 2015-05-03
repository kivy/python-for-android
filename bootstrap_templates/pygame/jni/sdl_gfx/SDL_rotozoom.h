
/*

SDL_rotozoom - rotozoomer

LGPL (c) A. Schiffler

*/

#ifndef _SDL_rotozoom_h
#define _SDL_rotozoom_h

#include <math.h>

/* Set up for C function definitions, even when using C++ */
#ifdef __cplusplus
extern "C" {
#endif

#ifndef M_PI
#define M_PI	3.141592654
#endif

#include "SDL.h"

	/* ---- Defines */

	/*!
	\brief Disable anti-aliasing (no smoothing).
	*/
#define SMOOTHING_OFF		0

	/*!
	\brief Enable anti-aliasing (smoothing).
	*/
#define SMOOTHING_ON		1

	/* ---- Prototypes */

#ifdef WIN32
#  ifdef DLL_EXPORT
#    define SDL_ROTOZOOM_SCOPE __declspec(dllexport)
#  else
#    ifdef LIBSDL_GFX_DLL_IMPORT
#      define SDL_ROTOZOOM_SCOPE __declspec(dllimport)
#    endif
#  endif
#endif
#ifndef SDL_ROTOZOOM_SCOPE
#  define SDL_ROTOZOOM_SCOPE extern
#endif

	/* 

	Rotozoom functions

	*/

	SDL_ROTOZOOM_SCOPE SDL_Surface *rotozoomSurface(SDL_Surface * src, double angle, double zoom, int smooth);

	SDL_ROTOZOOM_SCOPE SDL_Surface *rotozoomSurfaceXY
		(SDL_Surface * src, double angle, double zoomx, double zoomy, int smooth);


	SDL_ROTOZOOM_SCOPE void rotozoomSurfaceSize(int width, int height, double angle, double zoom, int *dstwidth,
		int *dstheight);

	SDL_ROTOZOOM_SCOPE void rotozoomSurfaceSizeXY
		(int width, int height, double angle, double zoomx, double zoomy, 
		int *dstwidth, int *dstheight);

	/* 

	Zooming functions

	*/

	SDL_ROTOZOOM_SCOPE SDL_Surface *zoomSurface(SDL_Surface * src, double zoomx, double zoomy, int smooth);

	SDL_ROTOZOOM_SCOPE void zoomSurfaceSize(int width, int height, double zoomx, double zoomy, int *dstwidth, int *dstheight);

	/* 

	Shrinking functions

	*/     

	SDL_ROTOZOOM_SCOPE SDL_Surface *shrinkSurface(SDL_Surface * src, int factorx, int factory);

	/* 

	Specialized rotation functions

	*/

	SDL_ROTOZOOM_SCOPE SDL_Surface* rotateSurface90Degrees(SDL_Surface* src, int numClockwiseTurns);

	/* Ends C function definitions when using C++ */
#ifdef __cplusplus
}
#endif

#endif				/* _SDL_rotozoom_h */
