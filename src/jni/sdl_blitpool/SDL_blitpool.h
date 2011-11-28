/*
//
//	Blit operation pool for the SDL.
//	Copyright (C) 2005 Strangebug (S.Miura) [strangebug art hotmail.co.jp]
//
//
//	This library is free software; you can redistribute it and/or
//	modify it under the terms of the GNU Lesser General Public
//	License as published by the Free Software Foundation; either
//	version 2.1 of the License, or (at your option) any later version.
//	
//	This library is distributed in the hope that it will be useful,
//	but WITHOUT ANY WARRANTY; without even the implied warranty of
//	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
//	Lesser General Public License for more details.
//	
//	You should have received a copy of the GNU Lesser General Public
//	License along with this library; if not, write to the Free Software
//	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//
//	SDL_BlitPool.c	: 25/Feb/2005	: created
//
*/


#ifndef INCLUDED_SDL_BLITPOOL_H
#define INCLUDED_SDL_BLITPOOL_H



#include "SDL.h"
#include "begin_code.h"


#ifdef __cplusplus
extern "C" {
#endif




#ifndef Optional
# define Optional
#endif




typedef enum {
	
	/*	BlitType	*/
	BLIT_TYPE_SURFACE	= 1 << 0,
	BLIT_TYPE_COLORFILL	= 1 << 1,
	BLIT_TYPE_EMPTY		= 1 << 2,
	
	#define BLIT_TYPE_MASK	(BLIT_TYPE_SURFACE | BLIT_TYPE_COLORFILL | BLIT_TYPE_EMPTY)
	
	
	/*	BlitTransparency	*/
	BLIT_ALPHA_TRANSPARENT	= 1 << 3,			/*	Surface have transparency pixel	*/
	BLIT_ALPHA_OPAQUE		= 1 << 4,			/*	Surface not have transparency pixel	*/
	
	#define BLIT_ALPHA_MASK	(BLIT_ALPHA_TRANSPARENT | BLIT_ALPHA_OPAQUE)
	
	
	/*	BlitExecOption	*/
	BLIT_EXEC_OPTIMIZE		= 1 << 7,			/*	do optimize	*/
	BLIT_EXEC_NO_OPTIMIZE	= 1 << 8,			/*	do not optimize	*/
	
	#define BLIT_EXEC_MASK	(BLIT_EXEC_OPTIMIZE | BLIT_EXEC_NO_OPTIMIZE)
	
	
	BLIT_FLAG_TERM	= 1 << 9		/*	terminater	*/
	
} BlitEntryFlag;




typedef enum {
	BLIT_OPT_REMOVEOVERLAP	= 1 << 0,		/*	remove overlap area	*/
	BLIT_OPT_REMOVEOUTSIDE	= 1 << 1,		/*	remove outside of destination surface	*/
	
	BLIT_OPT_ALL = BLIT_OPT_REMOVEOVERLAP | BLIT_OPT_REMOVEOUTSIDE
	
} BlitOptimizeFlag;



typedef struct BlitPool_tag BlitPool;			/*	Pool object	*/


typedef void *(*allocator_func)(unsigned long nbyte);
typedef void (*releaser_func)(void *p);



typedef struct {
	/*
	// Box: (x0, y0) - (x1, y1)
	*/
	
	Sint16 x0, y0, x1, y1;
	
} BlitPool_BoundingBox;





/*
//	Create/Delete a BlitPool object.
*/
extern BlitPool *BlitPool_CreatePool(Optional SDL_Surface *destsurf);

extern void BlitPool_DeletePool(BlitPool *pool);

extern void BlitPool_SetAllocator(BlitPool *pool, allocator_func allocator, releaser_func releaser);




/*
//	Release all of entries.
*/
extern void BlitPool_ReleaseEntry(BlitPool *pool);




/*
//	Blit/Fill operation post.
*/
extern int BlitPool_Post(
	BlitPool *pool,
	BlitEntryFlag flag,
	SDL_Surface *src,
	Optional SDL_Rect *srcrect,
	Optional SDL_Rect *destrect,
	Uint32 color
);

#define BlitPool_PostSurface(pool, src, srcrect, destrect, flag)	\
	BlitPool_Post(pool, BLIT_TYPE_SURFACE | (flag), src, srcrect, destrect, 0)

#define BlitPool_PostFill(pool, destrect, color, flag)	\
	BlitPool_Post(pool, BLIT_TYPE_COLORFILL | (flag), NULL, NULL, destrect, color)




/*
//	Commit pool.
//	src_pool don't release.
//	offset use only (x, y).
*/
extern void BlitPool_PostPool(
	BlitPool *dest_pool,
	BlitPool *src_pool,
	Optional SDL_Rect *offset
);




/*
//	Post separated surface/fill by area_description_str.
//
//	area_description_str like: "pos=(45, 12):O:(0,0)-(12,12):(45,23)-(62, 24):pos=(0,0):col=(255,255,255,255):(12,98)-(1,65)"
//	pos=(x,y) : destination position. default=(0,0).
//	(x0,y0)-(x1,y1) : source surface rectangle.
//	O/T : T=Transparens(default), O=Opaque.
//	col=(r, g, b, a) : colorfill mode. it's format be surf->format.
//
//	* Don't forget delimiter ':'.
*/
extern int BlitPool_PostByDescription(
	BlitPool *pool,
	Optional SDL_Surface *surf,
	unsigned char *area_description_str
);




/*
//	Optimize the operations and execute blit.
*/
extern void BlitPool_Optimize(BlitPool *pool, BlitOptimizeFlag flag);

extern void BlitPool_Execute(BlitPool *pool);




/*
//	For update.
//	example: {
//		int numrect;
//		SDL_Rect rectbuf[10];
//		
//		while ((numrect = BlitPool_GetUpdateRects(pool, rectbuf, sizeof(rectbuf)/sizeof(rectbuf[0]))) > 0) {
//			SDL_UpdateRects(screen, numrect, rectbuf);
//		}
//	}
*/
extern int BlitPool_GetRectCount(BlitPool *pool);

extern void *BlitPool_GetUpdateRectsObj(BlitPool *pool);

extern int BlitPool_GetUpdateRects(BlitPool *pool, SDL_Rect *rectbuf, int size, void **update_rects_obj);





/*
//	Get update area.
*/
extern Uint32 BlitPool_GetArea(BlitPool *pool);




/*
//	Utilities.
*/

extern int BlitPoolUtil_GetOverlapCode(
	Uint8 *out_code,					/*	Must not NULL	*/
	BlitPool_BoundingBox *f,
	BlitPool_BoundingBox *b
);

extern void BlitPoolUtil_CalcOverlapArea(
	BlitPool_BoundingBox *out_overlap_box,		/*	Must not NULL	*/
	Uint8 code,
	BlitPool_BoundingBox *f,
	BlitPool_BoundingBox *b
);

extern void BlitPoolUtil_RectToBBox(SDL_Rect *src, BlitPool_BoundingBox *dest);

extern void BlitPoolUtil_BBoxToRect(BlitPool_BoundingBox *src, SDL_Rect *dest);




#ifdef __cplusplus
}		/*	for extern "c" {	*/
#endif


#include "close_code.h"


#endif	/*	INCLUDED_SDL_BLITPOOL_H	*/
