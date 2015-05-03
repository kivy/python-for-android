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




#include <stdlib.h>		/*	malloc/free	*/
#include <assert.h>

#include "SDL.h"
#include "SDL_BlitPool.h"




/*	<configure>	*/



#ifndef NO_ALLOC_FAIL	/*	allocator will not fail	*/
# define IF_ALLOC_FAIL(statement)	/*	empty	*/
#else
# define IF_ALLOC_FAIL(statement)	statement
#endif


/*	view divided surface (for debug).	*/
#ifdef PAINT_DIVIDED
# define IF_PAINT_DIVIDED(statement)	statement
#else
# define IF_PAINT_DIVIDED(statement)	/*	empty	*/
#endif

/*	view separated surface (for debug).	*/
#ifdef PAINT_SEPARATED
# define IF_PAINT_SEPARATED(statement)	statement
#else
# define IF_PAINT_SEPARATED(statement)	/*	empty	*/
#endif


#ifndef IF_DEBUG
# ifdef NDEBUG
#  define IF_DEBUG(statement)	/*	empty	*/
# else
#  define IF_DEBUG(statement)	statement
# endif
#endif


/*	</configure>	*/




#if IF_DEBUG(1) + 0
# include <stdio.h>
#endif




typedef struct BlitEntry_tag {
	
	SDL_Surface *srcsurf;				/*	BlitSurface	*/
	Uint32 color;						/*	FillColor	*/
	BlitEntryFlag type;					/*	Surface/Fill: BlitEntryFlag	*/
	BlitEntryFlag trans;				/*	Transparency: BlitEntryFlag	*/
	
	SDL_Rect srcrect;
	BlitPool_BoundingBox destbox;		/*	Destination position bouding box (not rect)	*/
	
	SDL_Rect destrect;
	struct BlitEntry_tag *next, *prev;		/*	Double link list	*/
	
	struct {
		int optimize;
	} flag;
	
} BlitEntry;



struct BlitPool_tag {		/*	typedefed BlitPool in SDL_BlitPool.h	*/
	
	SDL_Surface *destsurf;
	BlitEntry *head, *tail;			/*	Double link list	*/
	
	int num_entry;
	
	allocator_func allocator;
	releaser_func releaser;
	
	struct {
		int converted_to_destrect;
	} flag;
};





static void *DefaultAllocator(unsigned long nbyte);
static void DefaultReleaser(void *p);
static BlitEntry *AllocateBlitEntry(BlitPool *pool);
static void ReleaseBlitEntry(BlitPool *pool, BlitEntry *entry);
static BlitEntry *DuplicateBlitEntry(BlitPool *pool, BlitEntry *base);


static void ConvertBBoxToRect(BlitPool *pool);
static int RemoveOverlapArea(BlitPool *pool);
static int RemoveOutsideEntry(BlitPool *pool);



static void AddEntryToTail(BlitPool *pool, BlitEntry *entry);

static void RemoveEntry(BlitPool *pool, BlitEntry *entry);
static void DeleteEntry(BlitPool *pool, BlitEntry *entry);

static int StrEq(unsigned char *str0, unsigned char *str1, int n);
static void AddEntryToNext(BlitPool *pool, BlitEntry *entry, BlitEntry *new_entry);

/*	unuse
static void AddEntryToPrev(BlitPool *pool, BlitEntry *entry, BlitEntry *new_entry);
static void AddEntryToHead(BlitPool *pool, BlitEntry *entry);
*/



BlitPool *BlitPool_CreatePool(Optional SDL_Surface *destsurf)
/*
//	This allocate a new pool.
*/
{
	BlitPool *p;
	
	
	p = (BlitPool *)malloc(sizeof(*p));
	if (p == NULL) {
		return NULL;
	}
	
	p->head = NULL;
	p->tail = NULL;
	p->num_entry = 0;
	p->destsurf = destsurf;
	p->flag.converted_to_destrect = 0;
	p->allocator = DefaultAllocator;
	p->releaser = DefaultReleaser;
	
	return p;
}




static void *DefaultAllocator(unsigned long nbyte)
{
	return malloc(nbyte);
}




static void DefaultReleaser(void *p)
{
	free(p);
}




void BlitPool_DeletePool(BlitPool *pool)
{
	assert(pool != NULL);
	
	BlitPool_ReleaseEntry(pool);
	
	free(pool);
}




void BlitPool_SetAllocator(BlitPool *pool, allocator_func allocator, releaser_func releaser)
{
	assert(pool != NULL);
	assert(allocator != NULL);
	assert(releaser != NULL);
	
	assert(pool->head == NULL);
	assert(pool->num_entry == 0);
	
	pool->allocator = allocator;
	pool->releaser = releaser;
}




void BlitPool_ReleaseEntry(BlitPool *pool)
{
	BlitEntry *p, *next;
	
	
	assert(pool != NULL);
	
	
	for (p = pool->head; p != NULL; p = next) {
		
		next = p->next;
		
		ReleaseBlitEntry(pool, p);
	}
	
	pool->head = NULL;
	pool->tail = NULL;
	pool->num_entry = 0;
	pool->flag.converted_to_destrect = 0;
}




int BlitPool_Post(
	BlitPool *pool,
	BlitEntryFlag flag,
	SDL_Surface *src,
	Optional SDL_Rect *srcrect,
	Optional SDL_Rect *destrect,
	Uint32 color
)
/*
//	This post the new operation to a pool.
*/
{
	BlitEntry *p;
	
	
	assert(pool != NULL);
	
	p = AllocateBlitEntry(pool);
	if (p == NULL) {
		return 1;
	}
	
	assert(flag < BLIT_FLAG_TERM);
	
	p->type = flag & BLIT_TYPE_MASK;
	p->srcsurf = src;
	p->color = color;
	p->trans = flag & BLIT_ALPHA_MASK;
	p->flag.optimize = flag & BLIT_EXEC_MASK;
	if (p->flag.optimize == 0) {
		p->flag.optimize = BLIT_EXEC_OPTIMIZE;
	}
	
	
	assert(p->type == BLIT_TYPE_SURFACE || p->type == BLIT_TYPE_COLORFILL || p->type == BLIT_TYPE_EMPTY);
	assert(p->trans == BLIT_ALPHA_TRANSPARENT || p->trans == BLIT_ALPHA_OPAQUE);
	assert(p->flag.optimize == BLIT_EXEC_OPTIMIZE || p->flag.optimize == BLIT_EXEC_NO_OPTIMIZE);
	
	
	if (p->type == BLIT_TYPE_SURFACE) {
		if (srcrect == NULL) {
			p->srcrect.w = src->w;
			p->srcrect.h = src->h;
			p->srcrect.x = p->srcrect.y = 0;
			
		} else {
			p->srcrect = *srcrect;
		}
	} else {
		assert(src == NULL);
		assert(srcrect == NULL);
		
		if (destrect == NULL) {
			p->srcrect.w = pool->destsurf->w;
			p->srcrect.h = pool->destsurf->h;
		} else {
			p->srcrect.w = destrect->w;
			p->srcrect.h = destrect->h;
		}
	}
	
	if (p->srcrect.w == 0 || p->srcrect.h == 0) {
		ReleaseBlitEntry(pool, p);
		return 1;
	}
	
	
	/*
	//	Not use destrect in BlitPool.
	//	It will be update rect after.
	*/
	if (destrect == NULL) {
		p->destbox.x0 = p->destbox.y0 = 0;
		
	} else {
		p->destbox.x0 = destrect->x;
		p->destbox.y0 = destrect->y;
		
		destrect->w = p->srcrect.w;
		destrect->h = p->srcrect.h;
	}
	
	p->destbox.x1 = p->destbox.x0 + p->srcrect.w;
	p->destbox.y1 = p->destbox.y0 + p->srcrect.h;
	
	AddEntryToTail(pool, p);
	pool->flag.converted_to_destrect = 0;
	
	return 0;
}





int BlitPool_PostByDescription(
	BlitPool *pool,
	Optional SDL_Surface *surf,
	unsigned char *area_description_str
)
/*
//	area_description_str like: "pos=(45, 12):O:(0,0)-(12,12):(45,23)-(62, 24):pos=(0,0):T:(12,98)-(1,65)"
//	pos=(x,y) : destination position.
//	(x0,y0)-(x1,y1) : source surface rectangle.
//	O/T : T=Transparens(default), O=Opaque.
//	col=(r, g, b, a) : colorfill mode. it's format be surf->format.
//
//	* Don't forget delimiter ':'.
*/
{
	unsigned char *p;
	SDL_Rect dest_rect, src_rect, blit_dest_rect;
	BlitEntryFlag blit_type;
	int flag_fillmode;
	int post_result;
	Uint32 color;
	
	
	#define SkipSpace(p)	while (*p == ' ' | *p == '\t' | *p == '\n') { p += 1; }
	#define SkipDigit(p)	while (*p == '0' | *p == '1' | *p == '2' | *p == '3' | *p == '4' | \
							*p == '5' | *p == '6' | *p == '7' | *p == '8' | *p == '9') { p += 1; }
	#define CheckAndSkip_OrDead(ch)	if (*p != ch) { return 1; } else { p += 1; SkipSpace(p); }
	
	
	assert(pool != NULL);
	assert(surf != NULL);
	assert(area_description_str != NULL);
	
	p = area_description_str;
	dest_rect.x = dest_rect.y = 0;
	blit_type = BLIT_ALPHA_TRANSPARENT;
	flag_fillmode = 0;
	color = 0;
	
	while (*p != '\0') {
		
		if (*p == ':') {
			p += 1;
		}
		
		SkipSpace(p);
		if (StrEq(p, "pos", 3) == 0) {
			p += 3;
			assert(*(p-1) == 's');
			SkipSpace(p);
			
			CheckAndSkip_OrDead('=');
			CheckAndSkip_OrDead('(');
			dest_rect.x = atoi(p);
			SkipDigit(p);
			SkipSpace(p);
			CheckAndSkip_OrDead(',');
			
			dest_rect.y = atoi(p);
			SkipDigit(p);
			SkipSpace(p);
			CheckAndSkip_OrDead(')');
			continue;
		}
		
		if (StrEq(p, "col", 3) == 0) {
			Uint8 r, g, b, a;
			
			p += 3;
			assert(*(p-1) == 'l');
			SkipSpace(p);
			
			#define GetCol(elem)	\
				elem = atoi(p);\
				SkipDigit(p);\
				SkipSpace(p);
			
			CheckAndSkip_OrDead('=');
			CheckAndSkip_OrDead('(');
			GetCol(r);
			CheckAndSkip_OrDead(',');
			GetCol(g);
			CheckAndSkip_OrDead(',');
			GetCol(b);
			CheckAndSkip_OrDead(',');
			GetCol(a);
			CheckAndSkip_OrDead(')');
			
			color = SDL_MapRGBA(surf->format, r, g, b, a);
			
			#undef GetCol
			
			flag_fillmode = 1;
			blit_type = BLIT_ALPHA_OPAQUE;
			
			continue;
		}
		
		if (flag_fillmode == 0 && (*p == 'T' || *p == 'O')) {
			if (*p == 'T') {
				blit_type = BLIT_ALPHA_TRANSPARENT;
			} else if (*p == 'O') {
				blit_type = BLIT_ALPHA_OPAQUE;
			} else {
				assert(0);
			}
			p += 1;
			SkipSpace(p);
			continue;
		}
		
		CheckAndSkip_OrDead('(');
		src_rect.x = atoi(p);
		SkipDigit(p);
		SkipSpace(p);
		
		CheckAndSkip_OrDead(',');
		src_rect.y = atoi(p);
		SkipDigit(p);
		SkipSpace(p);
		
		CheckAndSkip_OrDead(')');
		CheckAndSkip_OrDead('-');
		CheckAndSkip_OrDead('(');
		src_rect.w = atoi(p);
		SkipDigit(p);
		SkipSpace(p);
		
		CheckAndSkip_OrDead(',');
		src_rect.h = atoi(p);
		SkipDigit(p);
		SkipSpace(p);
		CheckAndSkip_OrDead(')');
		
		assert((Sint32)src_rect.x < (Sint32)src_rect.w);
		assert((Sint32)src_rect.y < (Sint32)src_rect.h);
		
		
		src_rect.w -= src_rect.x;
		src_rect.h -= src_rect.y;
		blit_dest_rect.x = src_rect.x + dest_rect.x;
		blit_dest_rect.y = src_rect.y + dest_rect.y;
		
		if (flag_fillmode) {
			blit_dest_rect.w = src_rect.w;
			blit_dest_rect.h = src_rect.h;
			post_result = BlitPool_PostFill(pool, &blit_dest_rect, color, blit_type);
		} else {
			post_result = BlitPool_PostSurface(pool, surf, &src_rect, &blit_dest_rect, blit_type);
		}
		
		if (post_result) {
			return 1;
		}
	}
	
	
	#undef SkipSpace
	#undef SkipDigit
	#undef CheckAndSkip_OrDead
	
	return 0;
}




void BlitPool_PostPool(
	BlitPool *dest_pool,
	BlitPool *src_pool,
	Optional SDL_Rect *offset
)
/*
//	Commit(add) the entries.
*/
{
	BlitEntry *new_entry, *src_entry;
	SDL_Rect zerorect;
	
	assert(dest_pool != NULL);
	assert(src_pool != NULL);
	
	if (offset == NULL) {
		zerorect.x = zerorect.y = 0;
		offset = &zerorect;
	}
	
	for (src_entry = src_pool->head; src_entry != NULL; src_entry = src_entry->next) {
		
		new_entry = DuplicateBlitEntry(dest_pool, src_entry);
		
		IF_ALLOC_FAIL( if (new_entry == NULL) return );
		
		new_entry->destbox.x0 += offset->x;
		new_entry->destbox.y0 += offset->y;
		new_entry->destbox.x1 += offset->x;
		new_entry->destbox.y1 += offset->y;
		
		AddEntryToTail(dest_pool, new_entry);
		dest_pool->flag.converted_to_destrect = 0;
	}
}




void BlitPool_Execute(BlitPool *pool)
/*
//	This execute the blit_surface and the color_fill.
*/
{
	BlitEntry *p;
	
	
	assert(pool != NULL);
	assert(pool->destsurf != NULL);
	
	if (pool->num_entry == 0) {
		return;
	}
	
	
	ConvertBBoxToRect(pool);
	
	
	for (p = pool->head; p != NULL; p = p->next) {
		
		/*
		//	if (type == BLIT_TYPE_SURFACE) {
		//		p->destrect:	destination position.
		//		p->srcrect: 	source position and rectangle size.
		//	} else {
		//		p->destrect:	destination position and rectangle size.
		//	}
		*/
		
		switch (p->type) {
		
		case BLIT_TYPE_SURFACE:
			SDL_BlitSurface(
				p->srcsurf, &p->srcrect,
				pool->destsurf, &p->destrect
			);
			break;
		
		 case BLIT_TYPE_COLORFILL:
			SDL_FillRect(pool->destsurf, &p->destrect, p->color);
			break;
		
		case BLIT_TYPE_EMPTY:
			/*
			//	Empty operation.
			*/
			break;
			
			IF_DEBUG(default: assert(0));
		}
	}
}




void BlitPool_Optimize(BlitPool *pool, BlitOptimizeFlag flag)
/*
//	Apply optimizations.
*/
{
	
	if (flag & BLIT_OPT_REMOVEOUTSIDE) {
		pool->flag.converted_to_destrect = 0;
		RemoveOutsideEntry(pool);
	}
	
	if (flag & BLIT_OPT_REMOVEOVERLAP) {
		pool->flag.converted_to_destrect = 0;
		if (RemoveOverlapArea(pool)) {
			/*	allocation failed	*/;
		}
	}
}




static void ConvertBBoxToRect(BlitPool *pool)
{
	BlitEntry *p;
	
	
	assert(pool != NULL);
	
	if (pool->flag.converted_to_destrect) {
		return;
	}
	
	for (p = pool->head; p != NULL; p = p->next) {
		
		BlitPoolUtil_BBoxToRect(&p->destbox, &p->destrect);
		
		if (p->type == BLIT_TYPE_SURFACE) {
			p->srcrect.w = p->destbox.x1 - p->destrect.x;
			p->srcrect.h = p->destbox.y1 - p->destrect.y;
		}
	}
	
	pool->flag.converted_to_destrect = 1;
}




int BlitPool_GetRectCount(BlitPool *pool)
{
	return pool->num_entry;
}




int BlitPool_GetUpdateRects(BlitPool *pool, SDL_Rect *rectbuf, int size, void **update_rects_obj)
/*
//	This gets the rects of update, to the rectbuf.
//	for SDL_UpdateRects.
//	return number is count of the updated rects, < size
//	example:
//
//	BlitPool_Execute(pool);
//	{
//		int numrect;
//		SDL_Rect rectbuf[10];
//		void *p;
//
//		p = BlitPool_GetUpdateRectsObj(pool);
//		while ((numrect = BlitPool_GetUpdateRects(pool, rectbuf, sizeof(rectbuf)/sizeof(rectbuf[0]), &p)) > 0) {
//			SDL_UpdateRects(screen, numrect, rectbuf);
//		}
//	}
*/
{
	int n;
	BlitEntry *p;
	
	
	assert(pool != NULL);
	assert(rectbuf != NULL);
	assert(size > 0);
	
	if (*update_rects_obj == NULL) {
		return 0;
	}
	
	if (pool->flag.converted_to_destrect) {
		;
	} else {
		ConvertBBoxToRect(pool);
	}
	
	n = 0;
	p = (BlitEntry *) *update_rects_obj;
	
	while (p != NULL && n < size) {
		rectbuf[n++] = p->destrect;
		p = p->next;
	}
	
	*update_rects_obj = (p == NULL) ? NULL : p->prev;
	
	return n;
}




void *BlitPool_GetUpdateRectsObj(BlitPool *pool)
{
	assert(pool != NULL);
	
	return (void *)pool->head;
}




Uint32 BlitPool_GetArea(BlitPool *pool)
{
	BlitEntry *p;
	Uint32 area;
	
	
	assert(pool != NULL);
	
	ConvertBBoxToRect(pool);
	
	area = 0;
	for (p = pool->head; p != NULL; p = p->next) {
		
		if (p->type == BLIT_TYPE_SURFACE) {
			area += p->srcrect.w * p->srcrect.h;
			
		} else if (p->type == BLIT_TYPE_COLORFILL) {
			area += p->destrect.w * p->destrect.h;
			
		} else {
			assert(0);
		}
	}
	
	return area;
}




static int RemoveOverlapArea(BlitPool *pool)
/*
//	This apply remove the overlapped rect and divide the back surface.
//	If return not 0 then fail operation.
*/
{
	Uint8 code;
	SDL_Rect srcrect;
	BlitPool_BoundingBox destbox;
	BlitEntry *new_entry;
	BlitEntry *front, *back, *back_next;
	int is_overlapped;
	int divided;
	
	
	assert(pool != NULL);
	
	
	for (back = pool->head; back != NULL; back = back_next) {
		
		back_next = back->next;
		
		/*	skip no optimization entry	*/
		if (back->flag.optimize == BLIT_EXEC_NO_OPTIMIZE) {
			continue;
		}
		
		for (front = back->next; front != NULL; front = front->next) {
			
			assert(back != front);
			
			if (front->flag.optimize == BLIT_EXEC_NO_OPTIMIZE |		/*	skip no optimization entry	*/
				front->trans == BLIT_ALPHA_TRANSPARENT				/*	skip transparent surface	*/
			) {
				continue;
			}
			
			assert((back->destbox.x1 - back->destbox.x0) > 0);
			assert((back->destbox.y1 - back->destbox.y0) > 0);
			assert((front->destbox.x1 - front->destbox.x0) > 0);
			assert((front->destbox.y1 - front->destbox.y0) > 0);
			
			is_overlapped = BlitPoolUtil_GetOverlapCode(
				&code,
				&front->destbox,
				&back->destbox
			);
			
			if (is_overlapped == 0) {
				continue;
			}
			
			assert(code <= 0x0f);
			
			
			/*
			//	Divide the back rects.
			*/
			
			divided = 0;
			
			
			#define AddNewEntryBegin()			\
				srcrect.x = back->srcrect.x;	\
				srcrect.y = back->srcrect.y;	\
				destbox = back->destbox;
			
			#define AddNewEntryEnd()							\
				assert(destbox.x1 >= destbox.x0);				\
				assert(destbox.y1 >= destbox.y0);				\
				if ((destbox.x1 - destbox.x0) <= 0 |			\
					(destbox.y1 - destbox.y0) <= 0				\
				) {												\
					;											\
				} else {										\
					new_entry = DuplicateBlitEntry(pool, back);	\
					IF_ALLOC_FAIL(if (new_entry == NULL) return 1);\
					AddEntryToNext(pool, back, new_entry);		\
					new_entry->srcrect.x = srcrect.x;			\
					new_entry->srcrect.y = srcrect.y;			\
					new_entry->destbox = destbox;				\
					IF_PAINT_DIVIDED(new_entry->type = BLIT_TYPE_COLORFILL);\
					IF_PAINT_DIVIDED(new_entry->color = (Uint32)new_entry*80);\
					assert(back->next == new_entry);			\
					back_next = new_entry;						\
					divided += 1;								\
				}
			
			switch (code) {
			case 0:
				/*
				//	00 00
				//
				//	*----*
				//	|  o----o
				//	*--|ffff|
				//	   o----o
				*/
				
				
				/*
				//	Perfect overlapped?
				//		(back->destbox.x1 - back->destbox.x0) - (back->destbox.x1 - front->destbox.x0) == 0
				//		           back width                 -           overlapped rect width        == 0
				//
				//		= back->destbox.x1 - back->destbox.x0 - back->destbox.x1 + front->destbox.x0
				//		= front->destbox.x0 - back->destbox.x0
				*/
				if ((front->destbox.x0 - back->destbox.x0) |		/*	== ||	*/
					(front->destbox.y0 - back->destbox.y0)
				) {
					;
				} else {
					break;
				}
				
				/*	Top - Left	*/
				AddNewEntryBegin();
				destbox.y1 = front->destbox.y0;
				AddNewEntryEnd();
				
				/*	Left	*/
				AddNewEntryBegin();
				srcrect.y += front->destbox.y0 - back->destbox.y0;
				destbox.y0 = front->destbox.y0;
				destbox.x1 = front->destbox.x0;
				AddNewEntryEnd();
				break;
				
			case 1:
				/*
				//	00 01
				//
				//	*----------*
				//	|  o----o  |
				//	*--|ffff|--*
				//	   o----o
				*/
				
				/*	WholeTop */
				AddNewEntryBegin();
				destbox.y1 = front->destbox.y0;
				AddNewEntryEnd();
				
				/*	Left	*/
				AddNewEntryBegin();
				srcrect.y += front->destbox.y0 - back->destbox.y0;
				destbox.y0 = front->destbox.y0;
				destbox.x1 = front->destbox.x0;
				AddNewEntryEnd();
				
				/*	Right	*/
				AddNewEntryBegin();
				srcrect.x += front->destbox.x1 - back->destbox.x0;
				srcrect.y += front->destbox.y0 - back->destbox.y0;
				destbox.x0 = front->destbox.x1;
				destbox.y0 = front->destbox.y0;
				AddNewEntryEnd();
				break;
				
			case 2:
				/*
				//	00 10
				//
				//	   *----*
				//	   |    |
				//	o----------o
				//	|   ffff   |
				//	o----------o
				*/
				
				/*	Top */
				AddNewEntryBegin();
				destbox.y1 = front->destbox.y0;
				AddNewEntryEnd();
				break;
				
			case 3:
				/*
				//	00 11
				//
				//	   *-----*
				//	   |     |
				//	o----o   |
				//	|ffff|---*
				//	o----o
				*/
				
				/*	Top - Right	*/
				AddNewEntryBegin();
				destbox.y1 = front->destbox.y0;
				AddNewEntryEnd();
				
				/*	Right	*/
				AddNewEntryBegin();
				srcrect.x += front->destbox.x1 - back->destbox.x0;
				srcrect.y += front->destbox.y0 - back->destbox.y0;
				destbox.x0 = front->destbox.x1;
				destbox.y0 = front->destbox.y0;
				AddNewEntryEnd();
				break;
				
			case 4:
				/*
				//	00 11
				//
				//	*----*
				//	|  o---o
				//	|  |fff|
				//	|  o---o
				//	*----*
				*/
				
				
				/*	Top - Left	*/
				AddNewEntryBegin();
				destbox.y1 = front->destbox.y0;
				AddNewEntryEnd();
				
				/*	Bottom - Left	*/
				AddNewEntryBegin();
				srcrect.y += front->destbox.y1 - back->destbox.y0;
				destbox.y0 = front->destbox.y1;
				AddNewEntryEnd();
				
				
				/*	Left	*/
				AddNewEntryBegin();
				srcrect.y += front->destbox.y0 - back->destbox.y0;
				destbox.y0 = front->destbox.y0;
				destbox.x1 = front->destbox.x0;
				destbox.y1 = front->destbox.y1;
				AddNewEntryEnd();
				break;
				
			case 5:
				/*
				//	01 01
				//
				//	*-------*
				//	|  o--o |
				//	|  |ff| |
				//	|  o--o |
				//	*-------*
				*/
				
				/*	WholeTop */
				AddNewEntryBegin();
				destbox.y1 = front->destbox.y0;
				AddNewEntryEnd();
				
				/*	WholeBottom */
				AddNewEntryBegin();
				srcrect.y += front->destbox.y1 - back->destbox.y0;
				destbox.y0 = front->destbox.y1;
				AddNewEntryEnd();
				
				/*	Left */
				AddNewEntryBegin();
				srcrect.y += front->destbox.y0 - back->destbox.y0;
				destbox.y0 = front->destbox.y0;
				destbox.x1 = front->destbox.x0;
				destbox.y1 = front->destbox.y1;
				AddNewEntryEnd();
				
				/*	Right */
				AddNewEntryBegin();
				srcrect.x += front->destbox.x1 - back->destbox.x0;
				srcrect.y += front->destbox.y0 - back->destbox.y0;
				destbox.x0 = front->destbox.x1;
				destbox.y0 = front->destbox.y0;
				destbox.y1 = front->destbox.y1;
				AddNewEntryEnd();
				break;
				
			case 6:
				/*
				//	01 10
				//
				//	  *-*
				//	o-----o
				//	o-----o
				//	  *-*
				*/
				
				/*	Top	*/
				AddNewEntryBegin();
				destbox.y1 = front->destbox.y0;
				AddNewEntryEnd();
				
				/*	Bottom	*/
				AddNewEntryBegin();
				srcrect.y += front->destbox.y1 - back->destbox.y0;
				destbox.y0 = front->destbox.y1;
				AddNewEntryEnd();
				break;
				
			case 7:
				/*
				//	01 11
				//
				//	   *---*
				//	 o---o |
				//	 |fff| |
				//	 o---o |
				//	   *---*
				*/
				
				/*	Top - Right	*/
				AddNewEntryBegin();
				destbox.y1 = front->destbox.y0;
				AddNewEntryEnd();
				
				/*	Bottom - Right	*/
				AddNewEntryBegin();
				srcrect.y += front->destbox.y1 - back->destbox.y0;
				destbox.y0 = front->destbox.y1;
				AddNewEntryEnd();
				
				/*	Right	*/
				AddNewEntryBegin();
				srcrect.x += front->destbox.x1 - back->destbox.x0;
				srcrect.y += front->destbox.y0 - back->destbox.y0;
				destbox.x0 = front->destbox.x1;
				destbox.y0 = front->destbox.y0;
				destbox.y1 = front->destbox.y1;
				AddNewEntryEnd();
				break;
				
			case 8:
				/*
				//	10 00
				//
				//	   o---o
				//	 *-|   |
				//	 | |fff|
				//	 *-|   |
				//	   o---o
				*/
				
				/*	Left */
				AddNewEntryBegin();
				destbox.x1 = front->destbox.x0;
				AddNewEntryEnd();
				break;
				
			case 9:								/*	10 01	*/
				/*
				//	10 01
				//
				//	   o---o
				//	 *-|   |-*
				//	 | |fff| |
				//	 *-|   |-*
				//	   o---o
				*/
				
				/*	Left */
				AddNewEntryBegin();
				destbox.x1 = front->destbox.x0;
				AddNewEntryEnd();
				
				/*	Right	*/
				AddNewEntryBegin();
				srcrect.x += front->destbox.x1 - back->destbox.x0;
				destbox.x0 = front->destbox.x1;
				AddNewEntryEnd();
				break;
				
			case 10:							/*	10 10	*/
				/*
				//	10 10
				//	Perfect Overlap.
				*/
				break;
				
			case 11:							/*	10 11	*/
				/*
				//	10 11
				//
				//	o---o
				//	|   |-*
				//	|fff| |
				//	|   |-*
				//	o---o
				*/
				
				/*	Right	*/
				AddNewEntryBegin();
				srcrect.x += front->destbox.x1 - back->destbox.x0;
				destbox.x0 = front->destbox.x1;
				AddNewEntryEnd();
				break;
				
			case 12:
				/*
				//	11 00
				//
				//	   o-----o
				//	   |ffff |
				//	*--| ffff|
				//	|  o-----o
				//	*----*
				*/
				
				/*	Bottom - Left	*/
				AddNewEntryBegin();
				srcrect.y += front->destbox.y1 - back->destbox.y0;
				destbox.y0 = front->destbox.y1;
				AddNewEntryEnd();
				
				/*	Left	*/
				AddNewEntryBegin();
				destbox.x1 = front->destbox.x0;
				destbox.y1 = front->destbox.y1;
				AddNewEntryEnd();
				break;
				
			case 13:
				/*
				//	11 01
				//
				//	   o-----o
				//	   |ffff |
				//	*--| ffff|--*
				//	|  o-----o  |
				//	*-----------*
				*/
				
				/*	WholeBottom */
				AddNewEntryBegin();
				srcrect.y += front->destbox.y1 - back->destbox.y0;
				destbox.y0 = front->destbox.y1;
				AddNewEntryEnd();
				
				/*	Left */
				AddNewEntryBegin();
				destbox.x1 = front->destbox.x0;
				destbox.y1 = front->destbox.y1;
				AddNewEntryEnd();
				
				/*	Right */
				AddNewEntryBegin();
				srcrect.x += front->destbox.x1 - back->destbox.x0;
				destbox.x0 = front->destbox.x1;
				destbox.y1 = front->destbox.y1;
				AddNewEntryEnd();
				break;
				
			case 14:
				/*
				//	11 10
				//
				//	o----------o
				//	|   ffff   |
				//	o----------o
				//	   *----*
				*/
				
				/*	Bottom */
				AddNewEntryBegin();
				srcrect.y += front->destbox.y1 - back->destbox.y0;
				destbox.y0 = front->destbox.y1;
				AddNewEntryEnd();
				break;
				
			case 15:
				/*
				//	11 11
				//
				//	o----o
				//	|ffff|--*
				//	o----o  |
				//	   *----*
				*/
				
				/*	Bottom - Right */
				AddNewEntryBegin();
				srcrect.y += front->destbox.y1 - back->destbox.y0;
				destbox.y0 = front->destbox.y1;
				AddNewEntryEnd();
				
				/*	Right	*/
				AddNewEntryBegin();
				srcrect.x += front->destbox.x1 - back->destbox.x0;
				destbox.x0 = front->destbox.x1;
				destbox.y1 = front->destbox.y1;
				AddNewEntryEnd();
				break;
				
				IF_DEBUG(default: assert(0 && "FATAL: in RemoveOverlapArea"));
			}
			
			assert(back != front);
			
			DeleteEntry(pool, back);
			
			if (divided) {
				back = back_next;
				back_next = back->next;
				
			} else {
				break;		/*	only deleted	*/
			}
		}
	}
	
	return 0;
	
	#undef AddNewEntryBegin
	#undef AddNewEntryEnd
}




static int RemoveOutsideEntry(BlitPool *pool)
/*
//	Remove outside of the destination surface.
//	return removed entry count.
*/
{
	BlitEntry *p, *next;
	Uint8 code;
	BlitPool_BoundingBox destsurfbox;
	int is_overlapped;
	int removed_count;
	
	
	assert(pool != NULL);
	
	if (pool->destsurf == NULL) {
		/*	impossible!	*/
		return 0;
	}
	
	if (pool->head == NULL || pool->num_entry == 0) {
		return 0;
	}
	
	destsurfbox.x0 = 0;
	destsurfbox.y0 = 0;
	destsurfbox.x1 = pool->destsurf->w;
	destsurfbox.y1 = pool->destsurf->h;
	
	removed_count = 0;
	
	for (p = pool->head; p != NULL; p = next) {
		
		next = p->next;
		
		is_overlapped = BlitPoolUtil_GetOverlapCode(
			&code,
			&p->destbox,		/*	destination	bouding box	*/
			&destsurfbox		/*	destination surface box	*/
		);
		
		if (is_overlapped == 0) {
			/*
			//	Outside of the destination surface.
			*/
			
			/*
			//	future: clipping p->destbox.
			*/
			
			removed_count += 1;
			DeleteEntry(pool, p);
		}
	}
	
	return removed_count;
}




int BlitPoolUtil_GetOverlapCode(
	Uint8 *out_code,				/*	Must not NULL	*/
	BlitPool_BoundingBox *f,					/*	front	*/
	BlitPool_BoundingBox *b					/*	back	*/
)
/*
//	This check the overlapped rect.
//
//	if (overlapped(front_rect, back_rect)) {
//		*out_code = code;
//		return 1;
//	} else {
//		return 0;
//	}
*/
{
	Uint8 code;					/*	use low nibble	*/
	
	enum {
		Overlapped = 1,
		NotOverlapped = 0
	};
	
	
	assert(out_code != NULL);
	assert(f != NULL);
	assert(b != NULL);
	
	
	assert((f->x1 - f->x0) > 0);
	assert((f->y1 - f->y0) > 0);
	assert((b->x1 - b->x0) > 0);
	assert((b->y1 - b->y0) > 0);
	
	
	/*
	//	It's overlapped?
	//	If overlapped then make the overlap rect,
	//	by just switch jump.
	*/
	
	
	/*
	//	Get MSB of 32bit signed integer.
	*/
	#define	GetMSB(val)	((Uint32)(val) & 0x80000000)
	
	
	/*
	//				   Y      X
	//	code:	...	b3	b2	b1	b0			bn == bit n
	//	b1,b0 = subtract back from front	of X axis
	//	b3,b2 = 							of Y axis
	*/
	code =	(GetMSB(f->x0 - b->x0) >> (2 + 28)) |		/*	b1	*/
			(GetMSB(f->x1 - b->x1) >> (3 + 28)) |		/*	b0	*/
			(GetMSB(f->y0 - b->y0) >> (0 + 28)) |		/*	b3	*/
			(GetMSB(f->y1 - b->y1) >> (1 + 28));		/*	b2	*/
	
	
	assert(code <= 0x0f);
	
	
	/*
	//	pattern: 00
	//	f:	   *----*		       *----*
	//	b:	*----*		or	*----*
	*/
	#define OutsideCheck00(axis)	((b->axis##1 - f->axis##0) <= 0)
	
	/*
	//	pattern: 01
	//	f:	  *--*
	//	b:	*-------*
	*/
	#define OutsideCheck01(axis)	( IF_DEBUG((f->axis##1 - f->axis##0) <= 0) + 0 )
	
	/*
	//	pattern: 11
	//	f:	*----*				*----*
	//	b:	   *----*		or	       *----*
	*/
	#define OutsideCheck11(axis)	((f->axis##1 - b->axis##0) <= 0)
	
	/*
	//	pattern: 10
	//	f:	*-------*
	//	b:	 *---*
	*/
	#define OutsideCheck10(axis)	( IF_DEBUG((b->axis##1 - b->axis##0) <= 0) + 0 )
	
	
	
	#define CaseOfCode_Overlap(codeval, codesymY, codesymX)	\
		case codeval:						\
			if (OutsideCheck##codesymX(x) | OutsideCheck##codesymY(y)) {		/*	== ||	*/		\
				return NotOverlapped;		\
			}								\
			*out_code = code;				\
			return Overlapped;
	
	
	switch (code) {
		CaseOfCode_Overlap(0, 00, 00);
		CaseOfCode_Overlap(1, 00, 01);
		CaseOfCode_Overlap(2, 00, 10);
		CaseOfCode_Overlap(3, 00, 11);
		
		CaseOfCode_Overlap(4, 01, 00);
		CaseOfCode_Overlap(5, 01, 01);
		CaseOfCode_Overlap(6, 01, 10);
		CaseOfCode_Overlap(7, 01, 11);
		
		CaseOfCode_Overlap(8, 10, 00);
		CaseOfCode_Overlap(9, 10, 01);
		CaseOfCode_Overlap(10, 10, 10);
		CaseOfCode_Overlap(11, 10, 11);
		
		CaseOfCode_Overlap(12, 11, 00);
		CaseOfCode_Overlap(13, 11, 01);
		CaseOfCode_Overlap(14, 11, 10);
		CaseOfCode_Overlap(15, 11, 11);
	}
	
	
	#undef CaseOfCode_Overlap
	#undef OutsideCheck00
	#undef OutsideCheck01
	#undef OutsideCheck11
	#undef OutsideCheck10
	
	/*	Not comming	*/
	assert(0 && "BlitPoolUtil_GetOverlapCode: Illigal area!");
	
	return Overlapped;
}




void BlitPoolUtil_CalcOverlapArea(
	BlitPool_BoundingBox *out_overlap_box,
	Uint8 code,
	BlitPool_BoundingBox *f,
	BlitPool_BoundingBox *b
)
/*
//	This calculate the overlapped rect.
//	bouding box f and b must be overlapped.
*/
{
	assert(out_overlap_box != NULL);
	assert(f != NULL);
	assert(b != NULL);
	assert(code <= 0x0f);
	
	
	#define CalcOverlapBox00(axis)				\
		out_overlap_box->axis##0 = f->axis##0;	\
		out_overlap_box->axis##1 = b->axis##1
	
	#define CalcOverlapBox01(axis)				\
		out_overlap_box->axis##0 = f->axis##0;	\
		out_overlap_box->axis##1 = f->axis##1
	
	#define CalcOverlapBox11(axis)				\
		out_overlap_box->axis##0 = b->axis##0;	\
		out_overlap_box->axis##1 = f->axis##1
	
	#define CalcOverlapBox10(axis)				\
		out_overlap_box->axis##0 = b->axis##0;	\
		out_overlap_box->axis##1 = b->axis##1
	
	
	
	#define CaseOfCode_CalcOverlap(codeval, codesymY, codesymX)	\
		case codeval:					\
			CalcOverlapBox##codesymX(x);\
			CalcOverlapBox##codesymY(y);\
			break;
	
	
	switch (code) {
		CaseOfCode_CalcOverlap(0, 00, 00);
		CaseOfCode_CalcOverlap(1, 00, 01);
		CaseOfCode_CalcOverlap(2, 00, 10);
		CaseOfCode_CalcOverlap(3, 00, 11);
		
		CaseOfCode_CalcOverlap(4, 01, 00);
		CaseOfCode_CalcOverlap(5, 01, 01);
		CaseOfCode_CalcOverlap(6, 01, 10);
		CaseOfCode_CalcOverlap(7, 01, 11);
		
		CaseOfCode_CalcOverlap(8, 10, 00);
		CaseOfCode_CalcOverlap(9, 10, 01);
		CaseOfCode_CalcOverlap(10, 10, 10);
		CaseOfCode_CalcOverlap(11, 10, 11);
		
		CaseOfCode_CalcOverlap(12, 11, 00);
		CaseOfCode_CalcOverlap(13, 11, 01);
		CaseOfCode_CalcOverlap(14, 11, 10);
		CaseOfCode_CalcOverlap(15, 11, 11);
	}
	
	
	#undef CaseOfCode_CalcOverlap
	#undef CalcOverlapBox00
	#undef CalcOverlapBox01
	#undef CalcOverlapBox11
	#undef CalcOverlapBox10
}





static void AddEntryToNext(BlitPool *pool, BlitEntry *entry, BlitEntry *new_entry)
/*
//	This add a new entry to a next node of a [entry].
//
//	[entry]  <->  [next]
//			|
//			V
//	[entry]  <->  [new_entry]  <->  [next]
*/
{
	assert(pool != NULL);
	assert(entry != NULL);
	assert(new_entry != NULL);
	
	
	if (pool->head == NULL) {
		AddEntryToTail(pool, entry);
		return;
		
	} else {
		BlitEntry *next;		/*	next node of [entry]	*/
		
		next = entry->next;
		
		/*	link: entry <-> new_entry	*/
		entry->next = new_entry;
		new_entry->prev = entry;
		
		/*	link: new_entry <-> next	*/
		new_entry->next = next;
		if (next != NULL) {
			next->prev = new_entry;
		}
		
		pool->num_entry += 1;
	}
}



#if 0
/*	unuse	*/
static void AddEntryToPrev(BlitPool *pool, BlitEntry *entry, BlitEntry *new_entry)
/*
//	This add a new entry to a prev node of a [entry].
//
//	[prev]  <->  [entry]
//			|
//			V
//	[prev]  <->  [new_entry]  <->  [entry]
*/
{
	assert(pool != NULL);
	assert(entry != NULL);
	assert(new_entry != NULL);
	
	
	if (pool->head == NULL) {
		AddEntryToHead(pool, entry);
		return;
		
	} else {
		BlitEntry *prev;		/*	next node of [entry]	*/
		
		prev = entry->prev;
		
		/*	link: entry <-> new_entry	*/
		entry->prev = new_entry;
		new_entry->next = entry;
		
		/*	link: new_entry <-> prev	*/
		new_entry->prev = prev;
		if (prev != NULL) {
			prev->next = new_entry;
		}
		
		pool->num_entry += 1;
	}
}

static void AddEntryToHead(BlitPool *pool, BlitEntry *entry)
/*
//	This add a new entry to head of list.
*/
{
	assert(pool != NULL);
	assert(entry != NULL);
	
	entry->next = NULL;
	entry->prev = NULL;
	
	if (pool->head == NULL) {
		pool->head = entry;
		pool->tail = entry;
		
	} else {
		pool->head->next = entry;
		entry->next = pool->head;
		
		pool->head = entry;
	}
	
	pool->num_entry += 1;
}
#endif




static void AddEntryToTail(BlitPool *pool, BlitEntry *entry)
/*
//	This add a new entry to tail of list.
*/
{
	assert(pool != NULL);
	assert(entry != NULL);
	
	entry->next = NULL;
	entry->prev = NULL;
	
	if (pool->head == NULL) {
		pool->head = entry;
		pool->tail = entry;
		
	} else {
		pool->tail->next = entry;
		entry->prev = pool->tail;
		
		pool->tail = entry;
	}
	
	pool->num_entry += 1;
}




static void RemoveEntry(BlitPool *pool, BlitEntry *entry)
/*
//	This unlink a entry from a pool(list).
*/
{
	BlitEntry *next ,*prev;
	
	
	assert(pool != NULL);
	assert(entry != NULL);
	
	next = entry->next;
	prev = entry->prev;
	
	if (prev == NULL) {
		assert(entry == pool->head);
		pool->head = next;
		if (next != NULL) {
			next->prev = NULL;
		}
		
	} else {
		prev->next = next;
	}
	
	if (next == NULL) {
		assert(entry == pool->tail);
		pool->tail = prev;
		if (prev != NULL) {
			prev->next = NULL;
		}
		
	} else {
		next->prev = prev;
	}
	
	pool->num_entry -= 1;
}




static void DeleteEntry(BlitPool *pool, BlitEntry *entry)
/*
//	This delete a entry from a pool(list).
*/
{
	assert(pool != NULL);
	assert(entry != NULL);
	
	
	RemoveEntry(pool, entry);
	
	ReleaseBlitEntry(pool, entry);
}




void BlitPoolUtil_RectToBBox(SDL_Rect *srcrect, BlitPool_BoundingBox *destbox)
{
	assert(destbox != NULL);
	assert(srcrect != NULL);
	
	destbox->x0 = srcrect->x;
	destbox->y0 = srcrect->y;
	destbox->x1 = destbox->x0 + srcrect->w;
	destbox->y1 = destbox->y0 + srcrect->h;
}




void BlitPoolUtil_BBoxToRect(BlitPool_BoundingBox *srcbox, SDL_Rect *destrect)
{
	assert(destrect != NULL);
	assert(srcbox != NULL);
	
	destrect->x = srcbox->x0;
	destrect->y = srcbox->y0;
	destrect->w = srcbox->x1 - destrect->x;
	destrect->h = srcbox->y1 - destrect->y;
}




static BlitEntry *AllocateBlitEntry(BlitPool *pool)
{
	assert(pool != NULL);
	
	return (BlitEntry *)pool->allocator(sizeof(BlitEntry));
}




static void ReleaseBlitEntry(BlitPool *pool, BlitEntry *entry)
{
	assert(pool != NULL);
	assert(entry != NULL);
	
	pool->releaser(entry);
}




static BlitEntry *DuplicateBlitEntry(BlitPool *pool, BlitEntry *base)
{
	BlitEntry *p;
	
	
	assert(pool != NULL);
	assert(base != NULL);
	
	p = AllocateBlitEntry(pool);
	
	
	#if IF_ALLOC_FAIL(1) + 0
	
	if (p == NULL)  {
		return NULL;
	}
	
	#endif
	
	
	*p = *base;					/*	or memcpy	*/
	
	p->next = NULL;
	p->prev = NULL;
	
	return p;
}





static int StrEq(unsigned char *str0, unsigned char *str1, int n)
{
	int i;
	
	
	assert(str0 != NULL);
	assert(str1 != NULL);
	
	for (i = 0; i < n; i++) {
		if (str0[i] != str1[i]) {
			return 1;
		}
	}
	
	return 0;
}




static const unsigned char * const stg_BlitPool_Sign = "SDL_BlitPool by Strangebug";



