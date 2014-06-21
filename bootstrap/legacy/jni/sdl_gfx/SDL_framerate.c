/*

SDL_framerate: framerate manager

LGPL (c) A. Schiffler

*/

#include "SDL_framerate.h"

/*!
\brief Initialize the framerate manager.

Initialize the framerate manager, set default framerate of 30Hz and
reset delay interpolation.

\param manager Pointer to the framerate manager.
*/
void SDL_initFramerate(FPSmanager * manager)
{
	/*
	* Store some sane values 
	*/
	manager->framecount = 0;
	manager->rate = FPS_DEFAULT;
	manager->rateticks = (1000.0f / (float) FPS_DEFAULT);
	manager->lastticks = SDL_GetTicks();
}

/*!
\brief Set the framerate in Hz 

Sets a new framerate for the manager and reset delay interpolation.
Rate values must be between FPS_LOWER_LIMIT and FPS_UPPER_LIMIT inclusive to be accepted.

\param manager Pointer to the framerate manager.
\param rate The new framerate in Hz (frames per second).

\return 0 for sucess and -1 for error.
*/
int SDL_setFramerate(FPSmanager * manager, int rate)
{
	if ((rate >= FPS_LOWER_LIMIT) && (rate <= FPS_UPPER_LIMIT)) {
		manager->framecount = 0;
		manager->rate = rate;
		manager->rateticks = (1000.0f / (float) rate);
		return (0);
	} else {
		return (-1);
	}
}

/*!
\brief Return the current target framerate in Hz 

Get the currently set framerate of the manager.

\param manager Pointer to the framerate manager.

\return Current framerate in Hz or -1 for error.
*/
int SDL_getFramerate(FPSmanager * manager)
{
	if (manager == NULL) {
		return (-1);
	} else {
		return (manager->rate);
	}
}

/*!
\brief Return the current framecount.

Get the current framecount from the framerate manager. 
A frame is counted each time SDL_framerateDelay is called.

\param manager Pointer to the framerate manager.

\return Current frame count or -1 for error.
*/
int SDL_getFramecount(FPSmanager * manager)
{
	if (manager == NULL) {
		return (-1);
	} else {
		return ((Uint32)manager->framecount);
	}
}

/*!
\brief Delay execution to maintain a constant framerate and calculate fps.

Generate a delay to accomodate currently set framerate. Call once in the
graphics/rendering loop. If the computer cannot keep up with the rate (i.e.
drawing too slow), the delay is zero and the delay interpolation is reset.

\param manager Pointer to the framerate manager.
*/
void SDL_framerateDelay(FPSmanager * manager)
{
	Uint32 current_ticks;
	Uint32 target_ticks;
	Uint32 the_delay;

	/*
	* No manager, no delay
	*/
	if (manager == NULL)
		return;

	/*
	* Initialize uninitialized manager 
	*/
	if (manager->lastticks == 0)
		SDL_initFramerate(manager);

	/*
	* Next frame 
	*/
	manager->framecount++;

	/*
	* Get/calc ticks 
	*/
	current_ticks = SDL_GetTicks();
	target_ticks = manager->lastticks + (Uint32) ((float) manager->framecount * manager->rateticks);

	if (current_ticks <= target_ticks) {
		the_delay = target_ticks - current_ticks;
		SDL_Delay(the_delay);
	} else {
		manager->framecount = 0;
		manager->lastticks = SDL_GetTicks();
	}
}
