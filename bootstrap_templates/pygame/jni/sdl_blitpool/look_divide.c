/*
//	Look divide.
//	please set compiler option, macro define [PAINT_DIVIDED]
*/


#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <assert.h>

#include "SDL.h"
#include "SDL_BlitPool.h"



void MouseEvent(SDL_MouseButtonEvent *event);
void Render(void);

SDL_Surface *g_ScreenSurface;
SDL_Rect g_Rect1, g_Rect2;

SDL_Rect g_ClearRect[256];
int g_NumClearRects;

int main(int argc, char *argv[])
{
	SDL_Event event;
	int running;
	
	if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER) < 0) {
        fprintf(stderr, "Unable to init SDL: %s\n", SDL_GetError());
        return 1;
    }
	
	g_ScreenSurface = SDL_SetVideoMode(
		640, 480, 32,
		SDL_SWSURFACE | SDL_DOUBLEBUF | SDL_RESIZABLE	/* | SDL_FULLSCREEN	*/
	);
	
	running = 1;
	while (running) {
		while (SDL_PollEvent(&event)) {
			switch(event.type){
			case SDL_QUIT:
				running = 0;
				break;
			case SDL_MOUSEBUTTONDOWN:
			case SDL_MOUSEBUTTONUP:
				MouseEvent(&event.button);
				break;
			case SDL_VIDEORESIZE:
				g_ScreenSurface = SDL_SetVideoMode(
					event.resize.w,
					event.resize.h,
					g_ScreenSurface->format->BitsPerPixel,
					g_ScreenSurface->flags
				);
			}
		}
		
		Render();
	}
	
	SDL_FreeSurface(g_ScreenSurface);
	SDL_Quit();
	return 0;
}

void MouseEvent(SDL_MouseButtonEvent *event)
{
}



void Render(void)
{
	int x, y;
	BlitPool *pool;
	SDL_Rect rect;
	
	
	pool = BlitPool_CreatePool(g_ScreenSurface);
	
	BlitPool_PostFill(
		pool,
		NULL,
		SDL_MapRGBA(g_ScreenSurface->format, 0, 0, 0, 10),
		BLIT_ALPHA_OPAQUE
	);
	
	rect.x = 40;
	rect.y = 40;
	rect.w = 100;
	rect.h = 100;
	BlitPool_PostFill(
		pool,
		&rect,
		0xff116699,
		BLIT_ALPHA_OPAQUE
	);
	
	rect.x = 220;
	rect.y = 40;
	rect.w = 200;
	rect.h = 200;
	BlitPool_PostFill(
		pool,
		&rect,
		0xff0011ff,
		BLIT_ALPHA_OPAQUE
	);
	
	rect.x = 40;
	rect.y = 160;
	rect.w = 50;
	rect.h = 50;
	BlitPool_PostFill(
		pool,
		&rect,
		0xffff1101,
		BLIT_ALPHA_OPAQUE
	);
	
	rect.x = 40;
	rect.y = 260;
	rect.w = 200;
	rect.h = 50;
	BlitPool_PostFill(
		pool,
		&rect,
		0xff113694,
		BLIT_ALPHA_OPAQUE
	);
	
	rect.x = 300;
	rect.y = 260;
	rect.w = 50;
	rect.h = 200;
	BlitPool_PostFill(
		pool,
		&rect,
		0xff001100,
		BLIT_ALPHA_OPAQUE
	);
	
	
	SDL_GetMouseState(&x, &y);
	rect.w = 100;
	rect.h = 100;
	rect.x = x - rect.w / 2;
	rect.y = y - rect.h / 2;
	BlitPool_PostFill(
		pool,
		&rect,
		0x00ffffff,
		BLIT_ALPHA_OPAQUE
	);
	
	
	BlitPool_Optimize(pool, BLIT_OPT_ALL);
	BlitPool_Execute(pool);
	
	
	#if 0
	{
		int numrect;
		SDL_Rect rectbuf[50];
		void *p;
		
		p = BlitPool_GetUpdateRectsObj(pool);
		while ((numrect = BlitPool_GetUpdateRects(pool, rectbuf, sizeof(rectbuf)/sizeof(rectbuf[0]), &p)) > 0) {
			SDL_UpdateRects(g_ScreenSurface, numrect, rectbuf);
		}
	}
	#else
	SDL_Flip(g_ScreenSurface);
	#endif
	
	BlitPool_DeletePool(pool);
}



