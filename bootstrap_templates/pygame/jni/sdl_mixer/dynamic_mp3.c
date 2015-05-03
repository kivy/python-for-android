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

#include "SDL_loadso.h"

#include "dynamic_mp3.h"

smpeg_loader smpeg = {
	0, NULL
};

#ifdef MP3_DYNAMIC
int Mix_InitMP3()
{
	if ( smpeg.loaded == 0 ) {
		smpeg.handle = SDL_LoadObject(MP3_DYNAMIC);
		if ( smpeg.handle == NULL ) {
			return -1;
		}
		smpeg.SMPEG_actualSpec =
			(void (*)( SMPEG *, SDL_AudioSpec * ))
			SDL_LoadFunction(smpeg.handle, "SMPEG_actualSpec");
		if ( smpeg.SMPEG_actualSpec == NULL ) {
			SDL_UnloadObject(smpeg.handle);
			return -1;
		}
		smpeg.SMPEG_delete =
			(void (*)( SMPEG* ))
			SDL_LoadFunction(smpeg.handle, "SMPEG_delete");
		if ( smpeg.SMPEG_delete == NULL ) {
			SDL_UnloadObject(smpeg.handle);
			return -1;
		}
		smpeg.SMPEG_enableaudio =
			(void (*)( SMPEG*, int ))
			SDL_LoadFunction(smpeg.handle, "SMPEG_enableaudio");
		if ( smpeg.SMPEG_enableaudio == NULL ) {
			SDL_UnloadObject(smpeg.handle);
			return -1;
		}
		smpeg.SMPEG_enablevideo =
			(void (*)( SMPEG*, int ))
			SDL_LoadFunction(smpeg.handle, "SMPEG_enablevideo");
		if ( smpeg.SMPEG_enablevideo == NULL ) {
			SDL_UnloadObject(smpeg.handle);
			return -1;
		}
		smpeg.SMPEG_new =
			(SMPEG* (*)(const char *, SMPEG_Info*, int))
			SDL_LoadFunction(smpeg.handle, "SMPEG_new");
		if ( smpeg.SMPEG_new == NULL ) {
			SDL_UnloadObject(smpeg.handle);
			return -1;
		}
		smpeg.SMPEG_new_rwops =
			(SMPEG* (*)(SDL_RWops *, SMPEG_Info*, int))
			SDL_LoadFunction(smpeg.handle, "SMPEG_new_rwops");
		if ( smpeg.SMPEG_new_rwops == NULL ) {
			SDL_UnloadObject(smpeg.handle);
			return -1;
		}
		smpeg.SMPEG_play =
			(void (*)( SMPEG* ))
			SDL_LoadFunction(smpeg.handle, "SMPEG_play");
		if ( smpeg.SMPEG_play == NULL ) {
			SDL_UnloadObject(smpeg.handle);
			return -1;
		}
		smpeg.SMPEG_playAudio =
			(int (*)( SMPEG *, Uint8 *, int ))
			SDL_LoadFunction(smpeg.handle, "SMPEG_playAudio");
		if ( smpeg.SMPEG_playAudio == NULL ) {
			SDL_UnloadObject(smpeg.handle);
			return -1;
		}
		smpeg.SMPEG_rewind =
			(void (*)( SMPEG* ))
			SDL_LoadFunction(smpeg.handle, "SMPEG_rewind");
		if ( smpeg.SMPEG_rewind == NULL ) {
			SDL_UnloadObject(smpeg.handle);
			return -1;
		}
		smpeg.SMPEG_setvolume =
			(void (*)( SMPEG*, int ))
			SDL_LoadFunction(smpeg.handle, "SMPEG_setvolume");
		if ( smpeg.SMPEG_setvolume == NULL ) {
			SDL_UnloadObject(smpeg.handle);
			return -1;
		}
		smpeg.SMPEG_skip =
			(void (*)( SMPEG*, float ))
			SDL_LoadFunction(smpeg.handle, "SMPEG_skip");
		if ( smpeg.SMPEG_skip == NULL ) {
			SDL_UnloadObject(smpeg.handle);
			return -1;
		}
		smpeg.SMPEG_status =
			(SMPEGstatus (*)( SMPEG* ))
			SDL_LoadFunction(smpeg.handle, "SMPEG_status");
		if ( smpeg.SMPEG_status == NULL ) {
			SDL_UnloadObject(smpeg.handle);
			return -1;
		}
		smpeg.SMPEG_stop =
			(void (*)( SMPEG* ))
			SDL_LoadFunction(smpeg.handle, "SMPEG_stop");
		if ( smpeg.SMPEG_stop == NULL ) {
			SDL_UnloadObject(smpeg.handle);
			return -1;
		}
	}
	++smpeg.loaded;

	return 0;
}
void Mix_QuitMP3()
{
	if ( smpeg.loaded == 0 ) {
		return;
	}
	if ( smpeg.loaded == 1 ) {
		SDL_UnloadObject(smpeg.handle);
	}
	--smpeg.loaded;
}
#else
int Mix_InitMP3()
{
	if ( smpeg.loaded == 0 ) {
		smpeg.SMPEG_actualSpec = SMPEG_actualSpec;
		smpeg.SMPEG_delete = SMPEG_delete;
		smpeg.SMPEG_enableaudio = SMPEG_enableaudio;
		smpeg.SMPEG_enablevideo = SMPEG_enablevideo;
		smpeg.SMPEG_new = SMPEG_new;
		smpeg.SMPEG_new_rwops = SMPEG_new_rwops;
		smpeg.SMPEG_play = SMPEG_play;
		smpeg.SMPEG_playAudio = SMPEG_playAudio;
		smpeg.SMPEG_rewind = SMPEG_rewind;
		smpeg.SMPEG_setvolume = SMPEG_setvolume;
		smpeg.SMPEG_skip = SMPEG_skip;
		smpeg.SMPEG_status = SMPEG_status;
		smpeg.SMPEG_stop = SMPEG_stop;
	}
	++smpeg.loaded;

	return 0;
}
void Mix_QuitMP3()
{
	if ( smpeg.loaded == 0 ) {
		return;
	}
	if ( smpeg.loaded == 1 ) {
	}
	--smpeg.loaded;
}
#endif /* MP3_DYNAMIC */

#endif /* MP3_MUSIC */
