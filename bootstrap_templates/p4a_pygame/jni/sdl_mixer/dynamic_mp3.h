/*
    SDL_mixer:  An audio mixer library based on the SDL library
    Copyright (C) 1997-2009 Sam Lantinga

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Library General Public
    License as published by the Free Software Foundation; either
    version 2 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Library General Public License for more details.

    You should have received a copy of the GNU Library General Public
    License along with this library; if not, write to the Free
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

    Sam Lantinga
    slouken@libsdl.org
*/

#ifdef MP3_MUSIC
#include "smpeg.h"

typedef struct {
	int loaded;
	void *handle;
	void (*SMPEG_actualSpec)( SMPEG *mpeg, SDL_AudioSpec *spec );
	void (*SMPEG_delete)( SMPEG* mpeg );
	void (*SMPEG_enableaudio)( SMPEG* mpeg, int enable );
	void (*SMPEG_enablevideo)( SMPEG* mpeg, int enable );
	SMPEG* (*SMPEG_new)(const char *file, SMPEG_Info* info, int sdl_audio);
	SMPEG* (*SMPEG_new_rwops)(SDL_RWops *src, SMPEG_Info* info, int sdl_audio);
	void (*SMPEG_play)( SMPEG* mpeg );
	int (*SMPEG_playAudio)( SMPEG *mpeg, Uint8 *stream, int len );
	void (*SMPEG_rewind)( SMPEG* mpeg );
	void (*SMPEG_setvolume)( SMPEG* mpeg, int volume );
	void (*SMPEG_skip)( SMPEG* mpeg, float seconds );
	SMPEGstatus (*SMPEG_status)( SMPEG* mpeg );
	void (*SMPEG_stop)( SMPEG* mpeg );
} smpeg_loader;

extern smpeg_loader smpeg;

#endif /* MUSIC_MP3 */

extern int Mix_InitMP3();
extern void Mix_QuitMP3();
