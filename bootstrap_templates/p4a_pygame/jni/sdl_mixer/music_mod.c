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

/* $Id: music_mod.c 4211 2008-12-08 00:27:32Z slouken $ */

#ifdef MOD_MUSIC

/* This file supports MOD tracker music streams */

#include "SDL_mixer.h"
#include "dynamic_mod.h"
#include "music_mod.h"

#include "mikmod.h"

#define SDL_SURROUND
#ifdef SDL_SURROUND
#define MAX_OUTPUT_CHANNELS 6
#else
#define MAX_OUTPUT_CHANNELS 2
#endif

/* Reference for converting mikmod output to 4/6 channels */
static int current_output_channels;
static Uint16 current_output_format;

static int music_swap8;
static int music_swap16;

/* Initialize the MOD player, with the given mixer settings
   This function returns 0, or -1 if there was an error.
 */
int MOD_init(SDL_AudioSpec *mixerfmt)
{
	CHAR *list;

	if ( !Mix_Init(MIX_INIT_MOD) ) {
		return -1;
	}

	/* Set the MikMod music format */
	music_swap8 = 0;
	music_swap16 = 0;
	switch (mixerfmt->format) {

		case AUDIO_U8:
		case AUDIO_S8: {
			if ( mixerfmt->format == AUDIO_S8 ) {
				music_swap8 = 1;
			}
			*mikmod.md_mode = 0;
		}
		break;

		case AUDIO_S16LSB:
		case AUDIO_S16MSB: {
			/* See if we need to correct MikMod mixing */
#if SDL_BYTEORDER == SDL_LIL_ENDIAN
			if ( mixerfmt->format == AUDIO_S16MSB ) {
#else
			if ( mixerfmt->format == AUDIO_S16LSB ) {
#endif
				music_swap16 = 1;
			}
			*mikmod.md_mode = DMODE_16BITS;
		}
		break;

		default: {
			Mix_SetError("Unknown hardware audio format");
			return -1;
		}
	}
	current_output_channels = mixerfmt->channels;
	current_output_format = mixerfmt->format;
	if ( mixerfmt->channels > 1 ) {
		if ( mixerfmt->channels > MAX_OUTPUT_CHANNELS ) {
			Mix_SetError("Hardware uses more channels than mixerfmt");
			return -1;
		}
		*mikmod.md_mode |= DMODE_STEREO;
	}
	*mikmod.md_mixfreq = mixerfmt->freq;
	*mikmod.md_device  = 0;
	*mikmod.md_volume  = 96;
	*mikmod.md_musicvolume = 128;
	*mikmod.md_sndfxvolume = 128;
	*mikmod.md_pansep  = 128;
	*mikmod.md_reverb  = 0;
	*mikmod.md_mode    |= DMODE_HQMIXER|DMODE_SOFT_MUSIC|DMODE_SURROUND;

	list = mikmod.MikMod_InfoDriver();
	if ( list )
	  free(list);
	else
	  mikmod.MikMod_RegisterDriver(mikmod.drv_nos);

	list = mikmod.MikMod_InfoLoader();
	if ( list )
	  free(list);
	else
	  mikmod.MikMod_RegisterAllLoaders();

	if ( mikmod.MikMod_Init(NULL) ) {
		Mix_SetError("%s", mikmod.MikMod_strerror(*mikmod.MikMod_errno));
		return -1;
	}

	return 0;
}

/* Uninitialize the music players */
void MOD_exit(void)
{
	if (mikmod.MikMod_Exit) {
		mikmod.MikMod_Exit();
	}
}

/* Set the volume for a MOD stream */
void MOD_setvolume(MODULE *music, int volume)
{
	mikmod.Player_SetVolume((SWORD)volume);
}

/* Load a MOD stream from the given file */
MODULE *MOD_new(const char *file)
{
	SDL_RWops *rw;

	rw = SDL_RWFromFile(file, "rb");
	if ( rw == NULL ) {
		/* FIXME: Free rw, need to free on delete */
		SDL_SetError("Couldn't open %s", file);
		return NULL;
	}
	return MOD_new_RW(rw);
}


typedef struct
{
	MREADER mr;
	long offset;
	long eof;
	SDL_RWops *rw;
} LMM_MREADER;

BOOL LMM_Seek(struct MREADER *mr,long to,int dir)
{
	LMM_MREADER* lmmmr = (LMM_MREADER*)mr;
	if ( dir == SEEK_SET ) {
		to += lmmmr->offset;
	}
	return (SDL_RWseek(lmmmr->rw, to, dir) < lmmmr->offset);
}
long LMM_Tell(struct MREADER *mr)
{
	LMM_MREADER* lmmmr = (LMM_MREADER*)mr;
	return SDL_RWtell(lmmmr->rw) - lmmmr->offset;
}
BOOL LMM_Read(struct MREADER *mr,void *buf,size_t sz)
{
	LMM_MREADER* lmmmr = (LMM_MREADER*)mr;
	return SDL_RWread(lmmmr->rw, buf, sz, 1);
}
int LMM_Get(struct MREADER *mr)
{
	unsigned char c;
	LMM_MREADER* lmmmr = (LMM_MREADER*)mr;
	if ( SDL_RWread(lmmmr->rw, &c, 1, 1) ) {
		return c;
	}
	return EOF;
}
BOOL LMM_Eof(struct MREADER *mr)
{
	long offset;
	LMM_MREADER* lmmmr = (LMM_MREADER*)mr;
	offset = LMM_Tell(mr);
	return offset >= lmmmr->eof;
}
MODULE *MikMod_LoadSongRW(SDL_RWops *rw, int maxchan)
{
	LMM_MREADER lmmmr = {
		{ LMM_Seek, LMM_Tell, LMM_Read, LMM_Get, LMM_Eof },
		0,
		0,
		0
	};
	lmmmr.offset = SDL_RWtell(rw);
	SDL_RWseek(rw, 0, RW_SEEK_END);
	lmmmr.eof = SDL_RWtell(rw);
	SDL_RWseek(rw, lmmmr.offset, RW_SEEK_SET);
        lmmmr.rw = rw;
	return mikmod.Player_LoadGeneric((MREADER*)&lmmmr, maxchan, 0);
}

/* Load a MOD stream from an SDL_RWops object */
MODULE *MOD_new_RW(SDL_RWops *rw)
{
	MODULE *module;

	/* Make sure the mikmod library is loaded */
	if ( !Mix_Init(MIX_INIT_MOD) ) {
		return NULL;
	}

	module = MikMod_LoadSongRW(rw,64);
	if (!module) {
		Mix_SetError("%s", mikmod.MikMod_strerror(*mikmod.MikMod_errno));
		return NULL;
	}

	/* Stop implicit looping, fade out and other flags. */
	module->extspd  = 1;
	module->panflag = 1;
	module->wrap    = 0;
	module->loop    = 0;
#if 0 /* Don't set fade out by default - unfortunately there's no real way
to query the status of the song or set trigger actions.  Hum. */
	module->fadeout = 1;
#endif
	return module;
}

/* Start playback of a given MOD stream */
void MOD_play(MODULE *music)
{
	mikmod.Player_Start(music);
}

/* Return non-zero if a stream is currently playing */
int MOD_playing(MODULE *music)
{
	return mikmod.Player_Active();
}

/* Play some of a stream previously started with MOD_play() */
int MOD_playAudio(MODULE *music, Uint8 *stream, int len)
{
	if (current_output_channels > 2) {
		int small_len = 2 * len / current_output_channels;
		int i;
		Uint8 *src, *dst;

		mikmod.VC_WriteBytes((SBYTE *)stream, small_len);
		/* and extend to len by copying channels */
		src = stream + small_len;
		dst = stream + len;

		switch (current_output_format & 0xFF) {
			case 8:
				for ( i=small_len/2; i; --i ) {
					src -= 2;
					dst -= current_output_channels;
					dst[0] = src[0];
					dst[1] = src[1];
					dst[2] = src[0];
					dst[3] = src[1];
					if (current_output_channels == 6) {
						dst[4] = src[0];
						dst[5] = src[1];
					}
				}
				break;
			case 16:
				for ( i=small_len/4; i; --i ) {
					src -= 4;
					dst -= 2 * current_output_channels;
					dst[0] = src[0];
					dst[1] = src[1];
					dst[2] = src[2];
					dst[3] = src[3];
					dst[4] = src[0];
					dst[5] = src[1];
					dst[6] = src[2];
					dst[7] = src[3];
					if (current_output_channels == 6) {
						dst[8] = src[0];
						dst[9] = src[1];
						dst[10] = src[2];
						dst[11] = src[3];
					}
				}
				break;
		}
	} else {
		mikmod.VC_WriteBytes((SBYTE *)stream, len);
	}
	if ( music_swap8 ) {
		Uint8 *dst;
		int i;

		dst = stream;
		for ( i=len; i; --i ) {
			*dst++ ^= 0x80;
		}
	} else
	if ( music_swap16 ) {
		Uint8 *dst, tmp;
		int i;

		dst = stream;
		for ( i=(len/2); i; --i ) {
			tmp = dst[0];
			dst[0] = dst[1];
			dst[1] = tmp;
			dst += 2;
		}
	}
	return 0;
}

/* Stop playback of a stream previously started with MOD_play() */
void MOD_stop(MODULE *music)
{
	mikmod.Player_Stop();
}

/* Close the given MOD stream */
void MOD_delete(MODULE *music)
{
	mikmod.Player_Free(music);
}

/* Jump (seek) to a given position (time is in seconds) */
void MOD_jump_to_time(MODULE *music, double time)
{
	mikmod.Player_SetPosition((UWORD)time);
}

#endif /* MOD_MUSIC */
