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

/* $Id: music_ogg.c 5211 2009-11-08 16:35:36Z slouken $ */

#ifdef OGG_MUSIC

/* This file supports Ogg Vorbis music streams */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "SDL_mixer.h"
#include "dynamic_ogg.h"
#include "music_ogg.h"

/* This is the format of the audio mixer data */
static SDL_AudioSpec mixer;

/* Initialize the Ogg Vorbis player, with the given mixer settings
   This function returns 0, or -1 if there was an error.
 */
int OGG_init(SDL_AudioSpec *mixerfmt)
{
	mixer = *mixerfmt;
	return(0);
}

/* Set the volume for an OGG stream */
void OGG_setvolume(OGG_music *music, int volume)
{
	music->volume = volume;
}

/* Load an OGG stream from the given file */
OGG_music *OGG_new(const char *file)
{
	SDL_RWops *rw;

	rw = SDL_RWFromFile(file, "rb");
	if ( rw == NULL ) {
		SDL_SetError("Couldn't open %s", file);
		return NULL;
	}
	return OGG_new_RW(rw);
}


static size_t sdl_read_func(void *ptr, size_t size, size_t nmemb, void *datasource)
{
    return SDL_RWread((SDL_RWops*)datasource, ptr, size, nmemb);
}

static int sdl_seek_func(void *datasource, ogg_int64_t offset, int whence)
{
    return SDL_RWseek((SDL_RWops*)datasource, (int)offset, whence);
}

static int sdl_close_func(void *datasource)
{
    return SDL_RWclose((SDL_RWops*)datasource);
}

static long sdl_tell_func(void *datasource)
{
    return SDL_RWtell((SDL_RWops*)datasource);
}

/* Load an OGG stream from an SDL_RWops object */
OGG_music *OGG_new_RW(SDL_RWops *rw)
{
	OGG_music *music;
	ov_callbacks callbacks;

	callbacks.read_func = sdl_read_func;
	callbacks.seek_func = sdl_seek_func;
	callbacks.close_func = sdl_close_func;
	callbacks.tell_func = sdl_tell_func;

	music = (OGG_music *)malloc(sizeof *music);
	if ( music ) {
		/* Initialize the music structure */
		memset(music, 0, (sizeof *music));
		OGG_stop(music);
		OGG_setvolume(music, MIX_MAX_VOLUME);
		music->section = -1;

		if ( !Mix_Init(MIX_INIT_OGG) ) {
			return(NULL);
		}
		if ( vorbis.ov_open_callbacks(rw, &music->vf, NULL, 0, callbacks) < 0 ) {
			free(music);
			SDL_RWclose(rw);
			SDL_SetError("Not an Ogg Vorbis audio stream");
			return(NULL);
		}
	} else {
		SDL_OutOfMemory();
	}
	return(music);
}

/* Start playback of a given OGG stream */
void OGG_play(OGG_music *music)
{
	music->playing = 1;
}

/* Return non-zero if a stream is currently playing */
int OGG_playing(OGG_music *music)
{
	return(music->playing);
}

/* Read some Ogg stream data and convert it for output */
static void OGG_getsome(OGG_music *music)
{
	int section;
	int len;
	char data[4096];
	SDL_AudioCVT *cvt;

#ifdef OGG_USE_TREMOR
	len = vorbis.ov_read(&music->vf, data, sizeof(data), &section);
#else
	len = vorbis.ov_read(&music->vf, data, sizeof(data), 0, 2, 1, &section);
#endif
	if ( len <= 0 ) {
		if ( len == 0 ) {
			music->playing = 0;
		}
		return;
	}
	cvt = &music->cvt;
	if ( section != music->section ) {
		vorbis_info *vi;

		vi = vorbis.ov_info(&music->vf, -1);
		SDL_BuildAudioCVT(cvt, AUDIO_S16, vi->channels, vi->rate,
		                       mixer.format,mixer.channels,mixer.freq);
		if ( cvt->buf ) {
			free(cvt->buf);
		}
		cvt->buf = (Uint8 *)malloc(sizeof(data)*cvt->len_mult);
		music->section = section;
	}
	if ( cvt->buf ) {
		memcpy(cvt->buf, data, len);
		if ( cvt->needed ) {
			cvt->len = len;
			SDL_ConvertAudio(cvt);
		} else {
			cvt->len_cvt = len;
		}
		music->len_available = music->cvt.len_cvt;
		music->snd_available = music->cvt.buf;
	} else {
		SDL_SetError("Out of memory");
		music->playing = 0;
	}
}

/* Play some of a stream previously started with OGG_play() */
int OGG_playAudio(OGG_music *music, Uint8 *snd, int len)
{
	int mixable;

	while ( (len > 0) && music->playing ) {
		if ( ! music->len_available ) {
			OGG_getsome(music);
		}
		mixable = len;
		if ( mixable > music->len_available ) {
			mixable = music->len_available;
		}
		if ( music->volume == MIX_MAX_VOLUME ) {
			memcpy(snd, music->snd_available, mixable);
		} else {
			SDL_MixAudio(snd, music->snd_available, mixable,
			                              music->volume);
		}
		music->len_available -= mixable;
		music->snd_available += mixable;
		len -= mixable;
		snd += mixable;
	}
	
	return len;
}

/* Stop playback of a stream previously started with OGG_play() */
void OGG_stop(OGG_music *music)
{
	music->playing = 0;
}

/* Close the given OGG stream */
void OGG_delete(OGG_music *music)
{
	if ( music ) {
		if ( music->cvt.buf ) {
			free(music->cvt.buf);
		}
		vorbis.ov_clear(&music->vf);
		free(music);
	}
}

/* Jump (seek) to a given position (time is in seconds) */
void OGG_jump_to_time(OGG_music *music, double time)
{
       vorbis.ov_time_seek( &music->vf, time );
}

#endif /* OGG_MUSIC */
