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
#include <jni.h>
#include <android/log.h>
#include <sys/time.h>
#include <time.h>
#include <stdint.h>
#include <math.h>
#include <string.h> // for memset()
#include <GLES/gl.h>
#include <GLES/glext.h>
#include <netinet/in.h>

#include "SDL_config.h"

#include "SDL_version.h"

//#include "SDL_opengles.h"
#include "../SDL_sysvideo.h"
#include "SDL_androidvideo.h"
#include "SDL_androidinput.h"
#include "jniwrapperstuff.h"

#include "touchscreenfont.h"

#define MIN(X, Y) ((X) < (Y) ? (X) : (Y))
#define MAX(X, Y) ((X) > (Y) ? (X) : (Y))

static int isTouchscreenKeyboardUsed = 0;
static int touchscreenKeyboardTheme = 0;
static int AutoFireButtonsNum = 0;

enum {
FONT_LEFT = 0, FONT_RIGHT = 1, FONT_UP = 2, FONT_DOWN = 3,
FONT_BTN1 = 4, FONT_BTN2 = 5, FONT_BTN3 = 6, FONT_BTN4 = 7
};

enum { MAX_BUTTONS = 7, MAX_BUTTONS_AUTOFIRE = 2 } ; // Max amount of custom buttons

static GLshort fontGL[sizeof(font)/sizeof(font[0])][FONT_MAX_LINES_PER_CHAR * 4 + 1];
enum { FONT_CHAR_LINES_COUNT = FONT_MAX_LINES_PER_CHAR * 4 };

static SDL_Rect arrows, buttons[MAX_BUTTONS];
static int nbuttons;
static SDLKey buttonKeysyms[MAX_BUTTONS] = { 
SDL_KEY(SDL_KEY_VAL(SDL_ANDROID_KEYCODE_0)),
SDL_KEY(SDL_KEY_VAL(SDL_ANDROID_KEYCODE_1)),
SDL_KEY(SDL_KEY_VAL(SDL_ANDROID_KEYCODE_2)),
SDL_KEY(SDL_KEY_VAL(SDL_ANDROID_KEYCODE_3)),
// 4 and 5 are MENU and BACK, always available as HW keys
SDL_KEY(SDL_KEY_VAL(SDL_ANDROID_KEYCODE_6)),
SDL_KEY(SDL_KEY_VAL(SDL_ANDROID_KEYCODE_7)),
SDL_KEY(SDL_KEY_VAL(SDL_ANDROID_KEYCODE_8))
};

enum { ARROW_LEFT = 1, ARROW_RIGHT = 2, ARROW_UP = 4, ARROW_DOWN = 8 };
static int oldArrows = 0;
static int ButtonAutoFire[MAX_BUTTONS_AUTOFIRE] = {0, 0};
static int ButtonAutoFireX[MAX_BUTTONS_AUTOFIRE] = {0, 0};
static int ButtonAutoFireRot[MAX_BUTTONS_AUTOFIRE] = {0, 0};

static SDL_Rect * OldCoords[MAX_MULTITOUCH_POINTERS] = { NULL };

typedef struct
{
    GLuint id;
    GLfloat w;
    GLfloat h;
} GLTexture_t;

static GLTexture_t arrowImages[5] = { {0, 0, 0}, };
static GLTexture_t buttonAutoFireImages[MAX_BUTTONS_AUTOFIRE] = { {0, 0, 0}, };
static GLTexture_t buttonImages[MAX_BUTTONS*2] = { {0, 0, 0}, };


static inline int InsideRect(const SDL_Rect * r, int x, int y)
{
	return ( x >= r->x && x <= r->x + r->w ) && ( y >= r->y && y <= r->y + r->h );
}


// Should be called on each char of font before drawing
static void prepareFontCharWireframe(int idx, int w, int h)
{
    int i, count = 0;
    float fw = (float) w / 255.0f;
    float fh = (float) h / 255.0f;

	//for( idx = 0; idx < sizeof(font)/sizeof(font[0]); idx++ )
	{
		for( i = 0; i < FONT_MAX_LINES_PER_CHAR; i++ )
			if( font[idx][i].x1 == 0 && font[idx][i].y1 == 0 && 
				font[idx][i].x2 == 0 && font[idx][i].y2 == 0 )
				break;
		count = i;
		for (i = 0; i < count; ++i) 
		{
			fontGL[idx][4*i+0] = (GLshort)(((int)font[idx][i].x1 - 128) * fw);
			fontGL[idx][4*i+1] = (GLshort)(((int)font[idx][i].y1 - 128) * fh);
			fontGL[idx][4*i+2] = (GLshort)(((int)font[idx][i].x2 - 128) * fw);
			fontGL[idx][4*i+3] = (GLshort)(((int)font[idx][i].y2 - 128) * fh);
		}
		fontGL[idx][FONT_CHAR_LINES_COUNT] = count*2;
	}
};


static inline void beginDrawingWireframe()
{
    glPushMatrix();
    glLoadIdentity();
    glOrthox( 0, SDL_ANDROID_sWindowWidth * 0x10000, SDL_ANDROID_sWindowHeight * 0x10000, 0, 0, 1 * 0x10000 );
    glPushMatrix();
    glEnableClientState(GL_VERTEX_ARRAY);
}
static inline void endDrawingWireframe()
{
    glDisableClientState(GL_VERTEX_ARRAY);
    glPopMatrix();
    glPopMatrix();
}

// Draws a char on screen using embedded line font, (x, y) are center of char, not upper-left corner
// TODO: use SDL 1.3 renderer routines? It will not be pixel-aligned then, if the screen is resized
static inline void drawCharWireframe(int idx, Uint16 x, Uint16 y, int rotation, Uint8 r, Uint8 g, Uint8 b, Uint8 a)
{
    glColor4x(r * 0x100, g * 0x100, b * 0x100, a * 0x100);

    glVertexPointer(2, GL_SHORT, 0, fontGL[idx]);
    glPopMatrix();
    glPushMatrix();
    glTranslatex( x * 0x10000, y * 0x10000, 0 );
    if(rotation != 0)
        glRotatex( rotation, 0, 0, 0x10000 );
    glDrawArrays(GL_LINES, 0, fontGL[idx][FONT_CHAR_LINES_COUNT]);
}

static inline void beginDrawingTex()
{
	glEnable(GL_TEXTURE_2D);
}

static inline void endDrawingTex()
{
	/*
	GLfloat texColor[4] = {0.0f, 0.0f, 0.0f, 0.0f};
	glTexEnvfv(GL_TEXTURE_ENV, GL_TEXTURE_ENV_COLOR, texColor);
	glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
	glDisable(GL_BLEND);
	*/

	glDisable(GL_TEXTURE_2D);
}


static inline void drawCharTex(GLTexture_t * tex, SDL_Rect * pos, Uint8 r, Uint8 g, Uint8 b, Uint8 a)
{
	GLint cropRect[4];
	/*
	GLfloat texColor[4];
	static const float onediv255 = 1.0f / 255.0f;
	*/

	glBindTexture(GL_TEXTURE_2D, tex->id);

	glColor4x(r * 0x100, g * 0x100, b * 0x100,  a * 0x100 );

	//glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_BLEND);
	
	glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);

	/*
	texColor[0] = r * onediv255;
	texColor[1] = g * onediv255;
	texColor[2] = b * onediv255;
	texColor[3] = a * onediv255;
	glTexEnvfv(GL_TEXTURE_ENV, GL_TEXTURE_ENV_COLOR, texColor);
	*/

	cropRect[0] = 0;
	cropRect[1] = tex->h;
	cropRect[2] = tex->w;
	cropRect[3] = -tex->h;
	glTexParameteriv(GL_TEXTURE_2D, GL_TEXTURE_CROP_RECT_OES, cropRect);
	glDrawTexiOES(pos->x, SDL_ANDROID_sWindowHeight - pos->y - pos->h, 0, pos->w, pos->h);
}

int SDL_ANDROID_drawTouchscreenKeyboard()
{
	int i;
	if( !isTouchscreenKeyboardUsed )
		return 0;
	if( touchscreenKeyboardTheme == 0 )
	{
		beginDrawingWireframe();
		// Draw arrow keys
		drawCharWireframe( FONT_LEFT, arrows.x + arrows.w / 4, arrows.y + arrows.h / 2, 0, 
					255, 255, SDL_GetKeyboardState(NULL)[SDL_KEY(LEFT)] ? 255 : 0, 128 );
		drawCharWireframe( FONT_RIGHT, arrows.x + arrows.w / 4 * 3, arrows.y + arrows.h / 2, 0,
					255, 255, SDL_GetKeyboardState(NULL)[SDL_KEY(RIGHT)] ? 255 : 0, 128 );
		drawCharWireframe( FONT_UP, arrows.x + arrows.w / 2, arrows.y + arrows.h / 4, 0, 
					255, 255, SDL_GetKeyboardState(NULL)[SDL_KEY(UP)] ? 255 : 0, 128 );
		drawCharWireframe( FONT_DOWN, arrows.x + arrows.w / 2, arrows.y + arrows.h / 4 * 3, 0, 
					255, 255, SDL_GetKeyboardState(NULL)[SDL_KEY(DOWN)] ? 255 : 0, 128 );

		// Draw buttons
		for( i = 0; i < nbuttons; i++ )
		{
			drawCharWireframe( FONT_BTN1 + i, buttons[i].x + buttons[i].w / 2, buttons[i].y + buttons[i].h / 2, ( i < AutoFireButtonsNum ? ButtonAutoFireRot[i] * 0x10000 : 0 ),
						( i < AutoFireButtonsNum && ButtonAutoFire[i] ) ? 0 : 255, 255, SDL_GetKeyboardState(NULL)[buttonKeysyms[i]] ? 255 : 0, 128 );
		}
		endDrawingWireframe();
	}
	else
	{
		int blendFactor =	( SDL_GetKeyboardState(NULL)[SDL_KEY(LEFT)] ? 1 : 0 ) + 
							( SDL_GetKeyboardState(NULL)[SDL_KEY(RIGHT)] ? 1 : 0 ) +
							( SDL_GetKeyboardState(NULL)[SDL_KEY(UP)] ? 1 : 0 ) +
							( SDL_GetKeyboardState(NULL)[SDL_KEY(DOWN)] ? 1 : 0 );
		beginDrawingTex();
		if( blendFactor == 0 )
			drawCharTex( &arrowImages[0], &arrows, 255, 255, 255, 128 );
		else
		{
			if( SDL_GetKeyboardState(NULL)[SDL_KEY(LEFT)] )
				drawCharTex( &arrowImages[1], &arrows, 255, 255, 255, 128 / blendFactor );
			if( SDL_GetKeyboardState(NULL)[SDL_KEY(RIGHT)] )
				drawCharTex( &arrowImages[2], &arrows, 255, 255, 255, 128 / blendFactor );
			if( SDL_GetKeyboardState(NULL)[SDL_KEY(UP)] )
				drawCharTex( &arrowImages[3], &arrows, 255, 255, 255, 128 / blendFactor );
			if( SDL_GetKeyboardState(NULL)[SDL_KEY(DOWN)] )
				drawCharTex( &arrowImages[4], &arrows, 255, 255, 255, 128 / blendFactor );
		}

		for( i = 0; i < nbuttons; i++ )
		{
			drawCharTex( ( i < AutoFireButtonsNum && ButtonAutoFire[i] ) ? &buttonAutoFireImages[i] : 
							&buttonImages[ SDL_GetKeyboardState(NULL)[buttonKeysyms[i]] ? (i * 2 + 1) : (i * 2) ],
							&buttons[i], 255, 255, 255, 128 );
		}
		endDrawingTex();
	}
	return 1;
};

static inline int ArrowKeysPressed(int x, int y)
{
	int ret = 0, dx, dy;
	dx = x - arrows.x - arrows.w / 2;
	dy = y - arrows.y - arrows.h / 2;
	// Single arrow key pressed
	if( abs(dy / 2) >= abs(dx) )
	{
		if( dy < 0 )
			ret |= ARROW_UP;
		else
			ret |= ARROW_DOWN;
	}
	else
	if( abs(dx / 2) >= abs(dy) )
	{
		if( dx > 0 )
			ret |= ARROW_RIGHT;
		else
			ret |= ARROW_LEFT;
	}
	else // Two arrow keys pressed
	{
		if( dx > 0 )
			ret |= ARROW_RIGHT;
		else
			ret |= ARROW_LEFT;

		if( dy < 0 )
			ret |= ARROW_UP;
		else
			ret |= ARROW_DOWN;
	}
	return ret;
}

int SDL_android_processTouchscreenKeyboard(int x, int y, int action, int pointerId)
{
	int i;
	SDL_keysym keysym;

	if( !isTouchscreenKeyboardUsed )
		return 0;

	if( action == MOUSE_DOWN )
	{
		if( InsideRect( &arrows, x, y ) )
		{
			OldCoords[pointerId] = &arrows;
			i = ArrowKeysPressed(x, y);
			if( i & ARROW_UP )
				SDL_SendKeyboardKey( SDL_PRESSED, GetKeysym( SDL_KEY(UP), &keysym) );
			if( i & ARROW_DOWN )
				SDL_SendKeyboardKey( SDL_PRESSED, GetKeysym( SDL_KEY(DOWN), &keysym) );
			if( i & ARROW_LEFT )
				SDL_SendKeyboardKey( SDL_PRESSED, GetKeysym( SDL_KEY(LEFT), &keysym) );
			if( i & ARROW_RIGHT )
				SDL_SendKeyboardKey( SDL_PRESSED, GetKeysym( SDL_KEY(RIGHT), &keysym) );
			oldArrows = i;
			return 1;
		}

		for( i = 0; i < nbuttons; i++ )
		{
			if( InsideRect( &buttons[i], x, y) )
			{
				OldCoords[pointerId] = &buttons[i];
				SDL_SendKeyboardKey( SDL_PRESSED, GetKeysym(buttonKeysyms[i], &keysym) );
				if( i < AutoFireButtonsNum )
				{
					ButtonAutoFireX[i] = x;
					ButtonAutoFire[i] = 0;
					ButtonAutoFireRot[i] = 0;
				}
				return 1;
			}
		}
	}
	else
	if( action == MOUSE_UP )
	{
		if( OldCoords[pointerId] == &arrows )
		{
			OldCoords[pointerId] = NULL;
			SDL_SendKeyboardKey( SDL_RELEASED, GetKeysym( SDL_KEY(UP), &keysym) );
			SDL_SendKeyboardKey( SDL_RELEASED, GetKeysym( SDL_KEY(DOWN), &keysym) );
			SDL_SendKeyboardKey( SDL_RELEASED, GetKeysym( SDL_KEY(LEFT), &keysym) );
			SDL_SendKeyboardKey( SDL_RELEASED, GetKeysym( SDL_KEY(RIGHT), &keysym) );
			oldArrows = 0;
			return 1;
		}
		for( i = 0; i < nbuttons; i++ )
		{
			if( OldCoords[pointerId] == &buttons[i] )
			{
				if( ! ( i < AutoFireButtonsNum && ButtonAutoFire[i] ) )
					SDL_SendKeyboardKey( SDL_RELEASED, GetKeysym(buttonKeysyms[i] ,&keysym) );
				OldCoords[pointerId] = NULL;
				return 1;
			}
		}
	}
	else
	if( action == MOUSE_MOVE )
	{
		if( OldCoords[pointerId] && !InsideRect(OldCoords[pointerId], x, y) )
		{
			SDL_android_processTouchscreenKeyboard(x, y, MOUSE_UP, pointerId);
			return SDL_android_processTouchscreenKeyboard(x, y, MOUSE_DOWN, pointerId);
		}
		else
		if( OldCoords[pointerId] == &arrows )
		{
			i = ArrowKeysPressed(x, y);
			if( i == oldArrows )
				return 1;
			if( oldArrows & ARROW_UP && ! (i & ARROW_UP) )
				SDL_SendKeyboardKey( SDL_RELEASED, GetKeysym( SDL_KEY(UP), &keysym) );
			if( oldArrows & ARROW_DOWN && ! (i & ARROW_DOWN) )
				SDL_SendKeyboardKey( SDL_RELEASED, GetKeysym( SDL_KEY(DOWN), &keysym) );
			if( oldArrows & ARROW_LEFT && ! (i & ARROW_LEFT) )
				SDL_SendKeyboardKey( SDL_RELEASED, GetKeysym( SDL_KEY(LEFT), &keysym) );
			if( oldArrows & ARROW_RIGHT && ! (i & ARROW_RIGHT) )
				SDL_SendKeyboardKey( SDL_RELEASED, GetKeysym( SDL_KEY(RIGHT), &keysym) );
			if( i & ARROW_UP )
				SDL_SendKeyboardKey( SDL_PRESSED, GetKeysym( SDL_KEY(UP), &keysym) );
			if( i & ARROW_DOWN )
				SDL_SendKeyboardKey( SDL_PRESSED, GetKeysym( SDL_KEY(DOWN), &keysym) );
			if( i & ARROW_LEFT )
				SDL_SendKeyboardKey( SDL_PRESSED, GetKeysym( SDL_KEY(LEFT), &keysym) );
			if( i & ARROW_RIGHT )
				SDL_SendKeyboardKey( SDL_PRESSED, GetKeysym( SDL_KEY(RIGHT), &keysym) );
			oldArrows = i;
		}
		else
		{
			for(i = 0; i < AutoFireButtonsNum; i++)
			if( OldCoords[pointerId] == &buttons[i] )
			{
				ButtonAutoFire[i] = abs(ButtonAutoFireX[i] - x) > buttons[i].w / 2;
				if( !ButtonAutoFire[i] )
					ButtonAutoFireRot[i] = ButtonAutoFireX[i] - x;
			}
		}

		if( OldCoords[pointerId] )
			return 1;

		return SDL_android_processTouchscreenKeyboard(x, y, MOUSE_DOWN, pointerId);
	}
	return 0;
};

JNIEXPORT void JNICALL 
JAVA_EXPORT_NAME(SDLSurfaceView_nativeSetupScreenKeyboard) ( JNIEnv*  env, jobject thiz, jint size, jint theme, jint _nbuttons, jint nbuttonsAutoFire )
{
	int i, ii;
	int nbuttons1row, nbuttons2row;
	nbuttons = _nbuttons;
	touchscreenKeyboardTheme = theme;
	if( nbuttons > MAX_BUTTONS )
		nbuttons = MAX_BUTTONS;
	AutoFireButtonsNum = nbuttonsAutoFire;
	if( AutoFireButtonsNum > MAX_BUTTONS_AUTOFIRE )
		AutoFireButtonsNum = MAX_BUTTONS_AUTOFIRE;
	// TODO: works for horizontal screen orientation only!
	
	if(touchscreenKeyboardTheme == 0)
	{
		// Arrows to the lower-left part of screen
		arrows.w = SDL_ANDROID_sWindowWidth / (size + 2);
		arrows.h = arrows.w;
		arrows.x = 0;
		arrows.y = SDL_ANDROID_sWindowHeight - arrows.h;
		
		// Main button to the lower-right
		buttons[0].w = SDL_ANDROID_sWindowWidth / (size + 2);
		buttons[0].h = SDL_ANDROID_sWindowHeight / (size + 2);
		buttons[0].x = SDL_ANDROID_sWindowWidth - buttons[0].w;
		buttons[0].y = SDL_ANDROID_sWindowHeight - buttons[0].h;

		// Row of secondary buttons to the upper-right
		nbuttons1row = MIN(nbuttons, 4);
		for( i = 1; i < nbuttons1row; i++ )
		{
			buttons[i].w = SDL_ANDROID_sWindowWidth / (nbuttons1row - 1) / (size + 2);
			buttons[i].h = SDL_ANDROID_sWindowHeight / (size + 2);
			buttons[i].x = SDL_ANDROID_sWindowWidth - buttons[i].w * (nbuttons1row - i);
			buttons[i].y = 0;
		}

		// Row of secondary buttons to the upper-left above arrows
		nbuttons2row = MIN(nbuttons, 7);
		for( i = 4; i < nbuttons2row; i++ )
		{
			buttons[i].w = SDL_ANDROID_sWindowWidth / (nbuttons2row - 4) / (size + 2);
			buttons[i].h = (SDL_ANDROID_sWindowHeight - SDL_ANDROID_sWindowWidth / 2) * 2 / (size + 2);
			buttons[i].x = buttons[i].w * (nbuttons2row - i - 1);
			buttons[i].y = 0;
		}
		
		// Resize char images
		prepareFontCharWireframe(FONT_LEFT, arrows.w / 2, arrows.h / 2);
		prepareFontCharWireframe(FONT_RIGHT, arrows.w / 2, arrows.h / 2);
		prepareFontCharWireframe(FONT_UP, arrows.w / 2, arrows.h / 2);
		prepareFontCharWireframe(FONT_DOWN, arrows.w / 2, arrows.h / 2);
	
		for( i = 0; i < nbuttons; i++ )
		{
			prepareFontCharWireframe(FONT_BTN1 + i, MIN(buttons[i].h, buttons[i].w), MIN(buttons[i].h, buttons[i].w));
		}
	}
	else
	{
		if(touchscreenKeyboardTheme == 1)
			AutoFireButtonsNum = 0; // Theme does not support auto-fire
		// Arrows to the lower-left part of screen
		arrows.x = SDL_ANDROID_sWindowWidth / 4;
		arrows.y = SDL_ANDROID_sWindowHeight - SDL_ANDROID_sWindowWidth / 4;
		arrows.w = SDL_ANDROID_sWindowWidth / (size + 2);
		arrows.h = arrows.w;
		arrows.x -= arrows.w/2;
		arrows.y -= arrows.h/2;
		// Move arrows from the center of the screen
		arrows.x -= size * SDL_ANDROID_sWindowWidth / 32;
		arrows.y += size * SDL_ANDROID_sWindowWidth / 32;
		
		// Buttons to the lower-right in 2 rows
		for(i = 0; i < 2; i++)
		for(ii = 0; ii < 3; ii++)
		{
			// Custom button ordering
			int iii = ii + i*2;
			if( ii == 2 )
				iii = 5 + i;
			buttons[iii].x = SDL_ANDROID_sWindowWidth - SDL_ANDROID_sWindowWidth / 12 - (SDL_ANDROID_sWindowWidth * ii / 6);
			buttons[iii].y = SDL_ANDROID_sWindowHeight - SDL_ANDROID_sWindowHeight / 8 - (SDL_ANDROID_sWindowHeight * i / 4);
			buttons[iii].w = SDL_ANDROID_sWindowWidth / (size + 2) / 3;
			buttons[iii].h = buttons[iii].w;
			buttons[iii].x -= buttons[iii].w/2;
			buttons[iii].y -= buttons[iii].h/2;
		}
		buttons[6].x = 0;
		buttons[6].y = 0;
		buttons[6].w = 30;
		buttons[6].h = 30;
	}
};


JNIEXPORT void JNICALL 
JAVA_EXPORT_NAME(SDLSurfaceView_nativeSetTouchscreenKeyboardUsed) ( JNIEnv*  env, jobject thiz)
{
	isTouchscreenKeyboardUsed = 1;
}

static int
power_of_2(int input)
{
    int value = 1;

    while (value < input) {
        value <<= 1;
    }
    return value;
}

JNIEXPORT void JNICALL 
JAVA_EXPORT_NAME(SDLSurfaceView_nativeSetupScreenKeyboardButton) ( JNIEnv*  env, jobject thiz, jint buttonID, jbyteArray charBufJava )
{
	// TODO: softstretch with antialiasing
	jboolean isCopy = JNI_TRUE;
	Uint8 * charBuf = NULL;
	int w, h, len, format;
	GLTexture_t * data = NULL;
	int texture_w, texture_h;
	len = (*env)->GetArrayLength(env, charBufJava);
	charBuf = (Uint8 *) (*env)->GetByteArrayElements(env, charBufJava, &isCopy);
	
	w = ntohl(((Uint32 *) charBuf)[0]);
	h = ntohl(((Uint32 *) charBuf)[1]);
	format = ntohl(((Uint32 *) charBuf)[2]);
	if( buttonID < 5 )
		data = &(arrowImages[buttonID]);
	else
	if( buttonID < 7 )
		data = &(buttonAutoFireImages[buttonID-5]);
	else
		data = &(buttonImages[buttonID-7]);
	
	texture_w = power_of_2(w);
	texture_h = power_of_2(h);
	data->w = w;
	data->h = h;

	glEnable(GL_TEXTURE_2D);

	glGenTextures(1, &data->id);
	glBindTexture(GL_TEXTURE_2D, data->id);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture_w, texture_h, 0, GL_RGBA,
					format ? GL_UNSIGNED_SHORT_4_4_4_4 : GL_UNSIGNED_SHORT_5_5_5_1, NULL);
	glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
	
	glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, w, h, GL_RGBA,
						format ? GL_UNSIGNED_SHORT_4_4_4_4 : GL_UNSIGNED_SHORT_5_5_5_1,
						charBuf + 12 );

	glDisable(GL_TEXTURE_2D);

	(*env)->ReleaseByteArrayElements(env, charBufJava, (jbyte *)charBuf, 0);
}
