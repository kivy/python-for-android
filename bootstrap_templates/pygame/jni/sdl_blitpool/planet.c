/*
//	Blit pool test: big planet.
//	press b key to switch UseBlitPool/Unuse.
*/


#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <assert.h>

#include "SDL.h"
#include "SDL_BlitPool.h"



#define MAX_BUFFER	256
#define MAX_PLANET	(MAX_BUFFER * 2)


#define PATH_IMG_PLANET			"bigplanet.bmp"
#define EPSILON		1.0e-3


struct Vector2 {
	float x, y;
};

struct Planet {
	struct Vector2 Position;
	struct Vector2 Acceleration;
	
	SDL_Rect ClearRect;
	float Weight;
};


struct {
	
	struct Planet PlanetArray[MAX_PLANET];
	Uint32 PlanetCount;
	Uint32 PlanetSize;
	
	BlitPool *PlanetPool;
	
	struct Video {
		SDL_Surface *ScreenSurface;
		SDL_Surface *PlanetSurface;
		
		Uint32 FramePerSecond;
		Uint32 FrameCounter;
		
		struct Vector2 ViewportOffset;
	} Video;
	
	struct MouseState {
		struct Vector2 Position;
		struct Vector2 Acceleration;
		int FlagViewportDragging;
	} MouseState;
	
	struct {
		int CleanFill;
		int Wall;
		int UseBlitPool;
	} Option;
} g;


void MainLoop(void);
int Initialize(void);
int InitializeVideo(void);
void DeInitialize(void);

int EventProcess(void);
void Step(Uint32 dt);
void Render(void);
void RenderUseBlitPool(void);

void MouseEvent(SDL_MouseButtonEvent *event);
void Clear(void);
void UpdateMouseState(void);
void UpdateTitleBar(void);

int CreatePlanet(float weight);
void DeleteAllPlanet(void);


void ApplyGravidy(Uint32 dt);
void ApplyMove(Uint32 dt);
void ApplyFrameCollide(void);
void ApplyGeneralResistance(void);

void Vec2_Plus(struct Vector2 *dest, struct Vector2 *src);
void Vec2_Minus(struct Vector2 *dest, struct Vector2 *src);
void Vec2_Multi(struct Vector2 *dest, float t);
float Vec2_Norm(struct Vector2 *vec);
void Vec2_Normalize(struct Vector2 *vec);




int main(int argc, char *argv[])
{
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER) < 0) {
        fprintf(stderr, "Unable to init SDL: %s\n", SDL_GetError());
        return 1;
    }
	
	if (Initialize()) {
		goto end;
	}
	
	printf("press b key to switch UseBlitPool/Unuse.\n");
	
	MainLoop();
	
end:
	DeInitialize();
	SDL_Quit();
	return 0;
}



int Initialize(void)
{
	if (InitializeVideo()) {
		return 1;
	}
	
	g.PlanetCount = 0;
	g.PlanetSize = g.Video.PlanetSurface->w;
	
	g.Option.CleanFill = 1;
	g.Option.Wall = 1;
	g.Option.UseBlitPool = 1;		/*	switch by b key	*/
	
	g.MouseState.FlagViewportDragging = 0;
	
	return 0;
}

int InitializeVideo(void)
{
	struct Video *p;
	
	
	p = &g.Video;
	
	p->ScreenSurface = SDL_SetVideoMode(
		640, 480, 32,
		SDL_SWSURFACE | SDL_RESIZABLE /*	| SDL_FULLSCREEN	*/
	);
	
	{							/*	青を透明カラーに	*/
		SDL_Surface *s;
		
		s = SDL_LoadBMP(PATH_IMG_PLANET);
		if (s == NULL) {
			return 1;
		}
		if (SDL_SetColorKey(s, SDL_SRCCOLORKEY | SDL_RLEACCEL, SDL_MapRGB(s->format, 0, 0, 0xff))) {
			return 1;
		}
		p->PlanetSurface = SDL_DisplayFormatAlpha(s);
		SDL_FreeSurface(s);
	}
	
	if (p->ScreenSurface == NULL || p->PlanetSurface == NULL) {
		return 1;
	}
	
	assert((p->PlanetSurface->w == p->PlanetSurface->h) && "planet Image must be square (width == height)");
	
	p->FramePerSecond = 0;
	p->FrameCounter = 0;
	
	p->ViewportOffset.x = 
	p->ViewportOffset.y = 0;
	
	
	/*	Make the planet surfaces pool	*/
	g.PlanetPool = BlitPool_CreatePool(NULL);
	
	BlitPool_PostByDescription(
		g.PlanetPool,
		p->PlanetSurface,
		"pos=(0,0):"
		"T:(29,0)-(170,200):"
		"T:(0,29)-(200,170):"
		"O:(29,29)-(170,170):"
	);
	
	BlitPool_Optimize(g.PlanetPool, BLIT_OPT_REMOVEOVERLAP);
	
	SDL_FillRect(p->ScreenSurface, NULL, SDL_MapRGBA(p->ScreenSurface->format, 0, 0, 0, 255));
	
	return 0;
}


void DeInitialize(void)
{
	BlitPool_DeletePool(g.PlanetPool);
	SDL_FreeSurface(g.Video.PlanetSurface);
	SDL_FreeSurface(g.Video.ScreenSurface);
}


void MainLoop(void)
{
	Uint32 tick, pretick, fpstick, dt;
	void (*per_second_operator[])(void) = { ApplyGeneralResistance, UpdateTitleBar, NULL };
	int i;
	
	
	Clear();
	
	UpdateTitleBar();
	
	pretick = fpstick = SDL_GetTicks();
	
	for (;;) {
		
		tick = SDL_GetTicks();
		dt = tick - pretick;
		
		#if 0
		if (dt <= 0) {
			continue;
		}
		#endif
		
		if (EventProcess()) {
			break;
		}
		
		if ((tick - fpstick) >= 1000) {
			
			fpstick = tick;
			
			g.Video.FramePerSecond = g.Video.FrameCounter;
			g.Video.FrameCounter = 0;
			
			for (i = 0; per_second_operator[i] != NULL; i++) {
				per_second_operator[i]();
			}
		}
		
		Step(dt);
		
		if (g.Option.UseBlitPool) {
			RenderUseBlitPool();
		} else {
			Render();
		}
		
		g.Video.FrameCounter += 1;
		
		pretick = tick;
	}
}



void ApplyGeneralResistance(void)
{
	Uint32 i;
	
	for (i = 0; i < g.PlanetCount; i++) {
		Vec2_Multi(&g.PlanetArray[i].Acceleration, 0.90);	/*	すべてのオブジェクトの速度を減衰	*/
	}
}


int EventProcess(void)
{
	SDL_Event event;
	SDL_Surface *surf;
	Uint32 i;
	
	
	surf = g.Video.ScreenSurface;
	
	UpdateMouseState();
	
	if (g.MouseState.FlagViewportDragging) {
		g.Video.ViewportOffset.x -= g.MouseState.Acceleration.x;
		g.Video.ViewportOffset.y -= g.MouseState.Acceleration.y;
	}
	
	while (SDL_PollEvent(&event)) {
		switch(event.type){
		case SDL_QUIT:
			return 1;
			
		case SDL_KEYDOWN:
			switch (event.key.keysym.sym) {
			case SDLK_ESCAPE:								return 1;		/*	終了	*/
			case SDLK_w:		g.Option.Wall ^= 1;			break;			/*	壁への衝突判定フラグ	*/
			case SDLK_b:		g.Option.UseBlitPool ^= 1;	break;			/*	Blitをプールするか	*/
			case SDLK_SPACE:	Clear();					break;			/*	惑星＆画面クリア	*/
			case SDLK_a:		CreatePlanet(1.0);			break;			/*	惑星生成	*/
			
			case SDLK_f:
				SDL_FillRect(surf, NULL, SDL_MapRGBA(surf->format, 0, 0, 0, 0));
				SDL_Flip(surf);	
				break;														/*	画面クリア	*/
			case SDLK_s:				/*	ストップ（全速度0）	*/
				for (i = 0; i < g.PlanetCount; i++) {
					g.PlanetArray[i].Acceleration.x = 0;
					g.PlanetArray[i].Acceleration.y = 0;
				}
				break;
			}
			break;
			
		case SDL_MOUSEBUTTONDOWN:
		case SDL_MOUSEBUTTONUP:
			MouseEvent(&event.button);
			break;
			
		case SDL_VIDEORESIZE:
			g.Video.ScreenSurface = SDL_SetVideoMode(
				event.resize.w,
				event.resize.h,
				surf->format->BitsPerPixel,
				surf->flags
			);
			SDL_FreeSurface(surf);
			break;
		}
	}
	
	return 0;
}


void MouseEvent(SDL_MouseButtonEvent *event)
{
	if (event->button == SDL_BUTTON_LEFT && event->type == SDL_MOUSEBUTTONDOWN) {
		CreatePlanet(1.0);
	}
}

void Clear(void)
{
	DeleteAllPlanet();
	
	SDL_FillRect(g.Video.ScreenSurface, NULL, SDL_MapRGBA(g.Video.ScreenSurface->format, 0, 0, 0, 255));
	SDL_Flip(g.Video.ScreenSurface);
	
	g.MouseState.Position.x = g.Video.ScreenSurface->w / 2;
	g.MouseState.Position.y = g.Video.ScreenSurface->h / 2;
	
	g.MouseState.Acceleration.x =
	g.MouseState.Acceleration.y = 0;
	
	g.Video.ViewportOffset.x =
	g.Video.ViewportOffset.y = 0;
}

void UpdateMouseState(void)
{
	int x, y;
	
	
	SDL_GetMouseState(&x, &y);
	g.MouseState.Position.x = x;
	g.MouseState.Position.y = y;
	
	SDL_GetRelativeMouseState(&x, &y);
	g.MouseState.Acceleration.x = x;
	g.MouseState.Acceleration.y = y;
}



void UpdateTitleBar(void)
{
	SDL_Surface *surf;
	unsigned char str[MAX_BUFFER];
	static const unsigned char *title = "PlanetSDL";
	
	
	surf = g.Video.ScreenSurface;
	
	sprintf(str,
		"%s | %2lu fps | [%lu x %lu x %lu bit] | %lu planet | [space] reset | [s] stop | [b]UsePool=%d",
		title, g.Video.FramePerSecond, surf->clip_rect.w, surf->h, surf->format->BitsPerPixel, g.PlanetCount, g.Option.UseBlitPool
	);
		
	SDL_WM_SetCaption(str, title);
}



void Step(Uint32 dt)
{
	if (dt == 0) {
		return;
	}
	
	ApplyGravidy(dt);			/*	惑星間重力	*/
	
	if (g.Option.Wall) {
		ApplyFrameCollide();	/*	画面フレームとの衝突判定	*/
	}
	
	ApplyMove(dt);				/*	加速度適応	*/
}


void ApplyGravidy(Uint32 dt)
{
	Uint32 i, j;
	float weight, distance, force, limit, delta;
	struct Vector2 vec1, vec2;
	register struct Planet *planet1, *planet2;
	
	const float G = 30.0;
	
	
	limit = g.PlanetSize / 3.0f;
	delta = dt;
	
	assert(limit >= 0.5 && "limit must be >= 0.5");
	
	for (i = 0; i < g.PlanetCount; i++) {
		
		planet1 = &g.PlanetArray[i];
		
		for (j = i + 1; j < g.PlanetCount; j++) {
			
			planet2 = &g.PlanetArray[j];
			
			vec1 = planet1->Position;
			Vec2_Minus(&vec1, &planet2->Position);
			
			distance = Vec2_Norm(&vec1);
			
			weight = planet1->Weight * planet2->Weight;
			
			if (distance <= limit) {
				distance = limit;
			}
			
			force = -G * weight / (distance * distance) * delta;
			
			Vec2_Normalize(&vec1);	/*	惑星間の単位方向ベクトル	*/
			vec2 = vec1;
			
			Vec2_Multi(&vec1, force / planet1->Weight);
			Vec2_Plus(&planet1->Acceleration, &vec1);
			
			Vec2_Multi(&vec2, force / -planet2->Weight);
			Vec2_Plus(&planet2->Acceleration, &vec2);
		}
	}
}


void ApplyMove(Uint32 dt)
{
	register Uint32 i;
	register float delta;
	struct Vector2 acc;
	
	
	delta = dt / 10.0f;
	
	for (i = 0; i < g.PlanetCount; i++) {
		acc = g.PlanetArray[i].Acceleration;
		Vec2_Multi(&acc, delta);
		Vec2_Plus(&g.PlanetArray[i].Position, &acc);
	}
}


void ApplyFrameCollide(void)
{
	float frame_width, frame_height;
	Uint32 i;
	struct Planet *planet;
	register float planet_radius;
	
	
	frame_width = g.Video.ScreenSurface->w;
	frame_height = g.Video.ScreenSurface->h;
	planet_radius = g.PlanetSize / 2;
	
	for (i = 0; i < g.PlanetCount; i++) {
		
		planet = &g.PlanetArray[i];
		
		if (planet->Position.x < planet_radius){
			planet->Position.x = planet_radius;
			planet->Acceleration.x *= -1;
			
		} else if (planet->Position.x > (frame_width - planet_radius)){
			planet->Position.x = frame_width - planet_radius;
			planet->Acceleration.x *= -1;
		}
		
		if (planet->Position.y < planet_radius){
			planet->Position.y = planet_radius;
			planet->Acceleration.y *= -1;
			
		} else if (planet->Position.y > (frame_height - planet_radius)){
			planet->Position.y = frame_height - planet_radius;
			planet->Acceleration.y *= -1;
		}
	}
}



void Render(void)
{
	SDL_Surface *surf;
	Uint32 i;
	SDL_Rect rect;
	Sint32 offset;
	Uint32 numrect;
	SDL_Rect rectbuf[MAX_PLANET * 2];
	
	
	surf = g.Video.ScreenSurface;
	rect.x = rect.y = 0;
	rect.w = rect.h = 0;
	offset = g.PlanetSize / 2;
	numrect = 0;
	
	for (i = 0; i < g.PlanetCount; i++) {
		SDL_FillRect(surf, &g.PlanetArray[i].ClearRect, SDL_MapRGBA(surf->format, 0, 0, 0, 255));
		rectbuf[numrect++] = g.PlanetArray[i].ClearRect;
	}
	
	
	/*	描画	*/
		
	for (i = 0; i < g.PlanetCount; i++) {
		rect.x = g.PlanetArray[i].Position.x - offset - g.Video.ViewportOffset.x;
		rect.y = g.PlanetArray[i].Position.y - offset - g.Video.ViewportOffset.y;
		
		SDL_BlitSurface(g.Video.PlanetSurface, NULL, surf, &rect);
		
		g.PlanetArray[i].ClearRect = rect;
		rectbuf[numrect++] = rect;
	}
	
	SDL_UpdateRects(surf, numrect, rectbuf);
	SDL_Flip(surf);
}



static unsigned char g_buf[1024 * 512];
static unsigned char *g_p;
#define InitAllocator()	g_p = g_buf

static void *Allocator(unsigned long nbyte)
{
	return (void *)((g_p += nbyte) - nbyte);
}
static void Releaser(void *p)
{
	assert(p != NULL);
}



void RenderUseBlitPool(void)
{
	Uint32 i;
	SDL_Rect rect;
	Sint32 offset;
	BlitPool *pool;
	SDL_Surface *screen, *planet;
	
	
	rect.x = rect.y = 0;
	offset = g.PlanetSize / 2;
	screen = g.Video.ScreenSurface;
	planet = g.Video.PlanetSurface;
	rect.w = rect.h = g.PlanetSize;
	pool = BlitPool_CreatePool(screen);
	
	BlitPool_SetAllocator(pool, Allocator, Releaser);
	InitAllocator();
	
	for (i = 0; i < g.PlanetCount; i++) {
		BlitPool_PostFill(
			pool,
			&g.PlanetArray[i].ClearRect,
			SDL_MapRGBA(screen->format, 0, 0, 0, 255),
			BLIT_ALPHA_OPAQUE
		);
	}
	
	for (i = 0; i < g.PlanetCount; i++) {
		
		rect.x = g.PlanetArray[i].Position.x - offset - g.Video.ViewportOffset.x;
		rect.y = g.PlanetArray[i].Position.y - offset - g.Video.ViewportOffset.y;
		
		BlitPool_PostPool(pool, g.PlanetPool, &rect);
		
		g.PlanetArray[i].ClearRect = rect;
	}
	
	BlitPool_Optimize(pool, BLIT_OPT_ALL);
	BlitPool_Execute(pool);
	
	
	if ((BlitPool_GetArea(pool) / (float)(screen->w * screen->h)) >= 0.8) {		/*	update area ratio	*/
		
		SDL_Flip(screen);
		
	} else {
		int numrect;
		SDL_Rect rectbuf[1024];
		void *p;
		
		p = BlitPool_GetUpdateRectsObj(pool);	/*	work object	*/
		while ((numrect = BlitPool_GetUpdateRects(pool, rectbuf, sizeof(rectbuf)/sizeof(rectbuf[0]), &p)) > 0) {
			SDL_UpdateRects(screen, numrect, rectbuf);
		}
	}
	
	
	BlitPool_DeletePool(pool);
}

int CreatePlanet(float weight)
{
	struct Planet *new_planet;
	
	
	if (g.PlanetCount >= MAX_PLANET) {
		return 1;
	}
	
	new_planet = &g.PlanetArray[g.PlanetCount];
	g.PlanetCount += 1;
	
	new_planet->Position = g.MouseState.Position;
	new_planet->Acceleration = g.MouseState.Acceleration;
	new_planet->Weight = weight;
	
	/*	調整	*/
	new_planet->Position.x += g.Video.ViewportOffset.x;
	new_planet->Position.y += g.Video.ViewportOffset.y;
	
	return 0;
}


void DeleteAllPlanet(void)
{
	g.PlanetCount = 0;
}


void Vec2_Plus(struct Vector2 *dest, struct Vector2 *src)
{
	dest->x += src->x;
	dest->y += src->y;
}

void Vec2_Minus(struct Vector2 *dest, struct Vector2 *src)
{
	dest->x -= src->x;
	dest->y -= src->y;
}

void Vec2_Multi(struct Vector2 *dest, float t)
{
	dest->x *= t;
	dest->y *= t;
}

float Vec2_Norm(struct Vector2 *vec)
{
	return sqrt(vec->x * vec->x + vec->y * vec->y);
}

void Vec2_Normalize(struct Vector2 *vec)
{
	float norm;
	
	norm = Vec2_Norm(vec);
	
	if (norm <= EPSILON && norm >= -EPSILON) {
		
		vec->x = 1;
		vec->y = 0;
		
	} else {
		vec->x /= norm;
		vec->y /= norm;
	}
}


