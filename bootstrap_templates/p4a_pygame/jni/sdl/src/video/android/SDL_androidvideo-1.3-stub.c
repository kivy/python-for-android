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
#include "SDL_config.h"

#include "SDL_pixels.h"
#include "SDL_video-1.3.h"
#include "SDL_sysvideo-1.3.h"
#include "SDL_androidvideo.h"

#include <stdint.h>
#include <string.h> // for memset()

static int ANDROID_VideoInit(_THIS);
static int ANDROID_GetDisplayBounds(_THIS, SDL_VideoDisplay * display, SDL_Rect * rect);
static void ANDROID_GetDisplayModes(_THIS, SDL_VideoDisplay * display);
static int ANDROID_SetDisplayMode(_THIS, SDL_VideoDisplay * display, SDL_DisplayMode * mode);
static void ANDROID_VideoQuit(_THIS);

static void ANDROID_GL_SwapBuffers(_THIS, SDL_Window * window);
// Stubs
static SDL_GLContext ANDROID_GL_CreateContext(_THIS, SDL_Window * window);
static int ANDROID_GL_MakeCurrent (_THIS, SDL_Window * window, SDL_GLContext context);
static void ANDROID_GL_DeleteContext (_THIS, SDL_GLContext context);
static void ANDROID_PumpEvents(_THIS);

static void ANDROID_DeleteDevice(SDL_VideoDevice *device)
{
	SDL_free(device);
}

SDL_VideoDevice *ANDROID_CreateDevice_1_3(int devindex)
{
	SDL_VideoDevice *device;

	/* Initialize all variables that we clean on shutdown */
	device = (SDL_VideoDevice *)SDL_malloc(sizeof(SDL_VideoDevice));
	if ( device ) {
		SDL_memset(device, 0, sizeof (*device));
	}
	if ( (device == NULL) ) {
		SDL_OutOfMemory();
		if ( device ) {
			SDL_free(device);
		}
		return(0);
	}

	/* Set the function pointers */
	device->VideoInit = ANDROID_VideoInit;
	device->GetDisplayBounds = ANDROID_GetDisplayBounds;
	device->GetDisplayModes = ANDROID_GetDisplayModes;
	device->PumpEvents = ANDROID_PumpEvents;
	device->VideoQuit = ANDROID_VideoQuit;
	device->free = ANDROID_DeleteDevice;
	
	device->GL_SwapWindow = ANDROID_GL_SwapBuffers;
	device->GL_CreateContext = ANDROID_GL_CreateContext;
	device->GL_MakeCurrent = ANDROID_GL_MakeCurrent;
	device->GL_DeleteContext = ANDROID_GL_DeleteContext;

	return device;
}

int ANDROID_VideoInit(_THIS)
{
	SDL_VideoDisplay display;
	SDL_DisplayMode mode;

	mode.w = SDL_ANDROID_sWindowWidth;
	mode.h = SDL_ANDROID_sWindowHeight;
	mode.refresh_rate = 0;
	mode.format = SDL_PIXELFORMAT_RGB565;
	mode.driverdata = NULL;

	SDL_zero(display);
	display.desktop_mode = mode;
	display.current_mode = mode;
	display.driverdata = NULL;
	SDL_AddVideoDisplay(&display);

	return 0;
}

void ANDROID_GetDisplayModes(_THIS, SDL_VideoDisplay * display)
{
	SDL_DisplayMode mode;
	mode.w = SDL_ANDROID_sWindowWidth;
	mode.h = SDL_ANDROID_sWindowHeight;
	mode.refresh_rate = 0;
	mode.format = SDL_PIXELFORMAT_RGB565;
	mode.driverdata = NULL;
	SDL_AddDisplayMode(display, &mode);
}

int ANDROID_GetDisplayBounds(_THIS, SDL_VideoDisplay * display, SDL_Rect * rect)
{
	rect->w = SDL_ANDROID_sWindowWidth;
	rect->h = SDL_ANDROID_sWindowHeight;
	return 1;
};

int ANDROID_SetDisplayMode(_THIS, SDL_VideoDisplay * display, SDL_DisplayMode * mode)
{
	return 1;
};

void ANDROID_VideoQuit(_THIS)
{
}

void ANDROID_PumpEvents(_THIS)
{
}

void ANDROID_GL_SwapBuffers(_THIS, SDL_Window * window)
{
	SDL_ANDROID_CallJavaSwapBuffers();
};

SDL_GLContext ANDROID_GL_CreateContext(_THIS, SDL_Window * window)
{
	return (SDL_GLContext)1;
};
int ANDROID_GL_MakeCurrent (_THIS, SDL_Window * window, SDL_GLContext context)
{
	return 1;
};
void ANDROID_GL_DeleteContext (_THIS, SDL_GLContext context)
{
};

