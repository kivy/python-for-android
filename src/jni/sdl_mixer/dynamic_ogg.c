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

#ifdef OGG_MUSIC

#include "SDL_loadso.h"

#include "dynamic_ogg.h"

vorbis_loader vorbis = {
	0, NULL
};

#ifdef OGG_DYNAMIC
int Mix_InitOgg()
{
	if ( vorbis.loaded == 0 ) {
		vorbis.handle = SDL_LoadObject(OGG_DYNAMIC);
		if ( vorbis.handle == NULL ) {
			return -1;
		}
		vorbis.ov_clear =
			(int (*)(OggVorbis_File *))
			SDL_LoadFunction(vorbis.handle, "ov_clear");
		if ( vorbis.ov_clear == NULL ) {
			SDL_UnloadObject(vorbis.handle);
			return -1;
		}
		vorbis.ov_info =
			(vorbis_info *(*)(OggVorbis_File *,int))
			SDL_LoadFunction(vorbis.handle, "ov_info");
		if ( vorbis.ov_info == NULL ) {
			SDL_UnloadObject(vorbis.handle);
			return -1;
		}
		vorbis.ov_open_callbacks =
			(int (*)(void *, OggVorbis_File *, char *, long, ov_callbacks))
			SDL_LoadFunction(vorbis.handle, "ov_open_callbacks");
		if ( vorbis.ov_open_callbacks == NULL ) {
			SDL_UnloadObject(vorbis.handle);
			return -1;
		}
		vorbis.ov_pcm_total =
			(ogg_int64_t (*)(OggVorbis_File *,int))
			SDL_LoadFunction(vorbis.handle, "ov_pcm_total");
		if ( vorbis.ov_pcm_total == NULL ) {
			SDL_UnloadObject(vorbis.handle);
			return -1;
		}
		vorbis.ov_read =
#ifdef OGG_USE_TREMOR
			(long (*)(OggVorbis_File *,char *,int,int *))
#else
			(long (*)(OggVorbis_File *,char *,int,int,int,int,int *))
#endif
			SDL_LoadFunction(vorbis.handle, "ov_read");
		if ( vorbis.ov_read == NULL ) {
			SDL_UnloadObject(vorbis.handle);
			return -1;
		}
		vorbis.ov_time_seek =
			(int (*)(OggVorbis_File *,double))
			SDL_LoadFunction(vorbis.handle, "ov_time_seek");
		if ( vorbis.ov_time_seek == NULL ) {
			SDL_UnloadObject(vorbis.handle);
			return -1;
		}
	}
	++vorbis.loaded;

	return 0;
}
void Mix_QuitOgg()
{
	if ( vorbis.loaded == 0 ) {
		return;
	}
	if ( vorbis.loaded == 1 ) {
		SDL_UnloadObject(vorbis.handle);
	}
	--vorbis.loaded;
}
#else
int Mix_InitOgg()
{
	if ( vorbis.loaded == 0 ) {
		vorbis.ov_clear = ov_clear;
		vorbis.ov_info = ov_info;
		vorbis.ov_open_callbacks = ov_open_callbacks;
		vorbis.ov_pcm_total = ov_pcm_total;
		vorbis.ov_read = ov_read;
		vorbis.ov_time_seek = ov_time_seek;
	}
	++vorbis.loaded;

	return 0;
}
void Mix_QuitOgg()
{
	if ( vorbis.loaded == 0 ) {
		return;
	}
	if ( vorbis.loaded == 1 ) {
	}
	--vorbis.loaded;
}
#endif /* OGG_DYNAMIC */

#endif /* OGG_MUSIC */
