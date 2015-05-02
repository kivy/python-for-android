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

    This is the source needed to decode an AIFF file into a waveform.
    It's pretty straightforward once you get going. The only
    externally-callable function is Mix_LoadAIFF_RW(), which is meant to
    act as identically to SDL_LoadWAV_RW() as possible.

    This file by Torbjörn Andersson (torbjorn.andersson@eurotime.se)
    8SVX file support added by Marc Le Douarain (mavati@club-internet.fr)
    in december 2002.
*/

/* $Id: load_aiff.c 5214 2009-11-08 17:11:09Z slouken $ */

#include <stdlib.h>
#include <string.h>

#include "SDL_endian.h"
#include "SDL_mixer.h"
#include "load_aiff.h"

/*********************************************/
/* Define values for AIFF (IFF audio) format */
/*********************************************/
#define FORM		0x4d524f46		/* "FORM" */

#define AIFF		0x46464941		/* "AIFF" */
#define SSND		0x444e5353		/* "SSND" */
#define COMM		0x4d4d4f43		/* "COMM" */

#define _8SVX		0x58565338		/* "8SVX" */
#define VHDR		0x52444856		/* "VHDR" */
#define BODY		0x59444F42		/* "BODY" */

/* This function was taken from libsndfile. I don't pretend to fully
 * understand it.
 */

static Uint32 SANE_to_Uint32 (Uint8 *sanebuf)
{
	/* Is the frequency outside of what we can represent with Uint32? */
	if ( (sanebuf[0] & 0x80) || (sanebuf[0] <= 0x3F) || (sanebuf[0] > 0x40)
		|| (sanebuf[0] == 0x40 && sanebuf[1] > 0x1C) )
		return 0;

	return ((sanebuf[2] << 23) | (sanebuf[3] << 15) | (sanebuf[4] << 7)
		| (sanebuf[5] >> 1)) >> (29 - sanebuf[1]);
}

/* This function is based on SDL_LoadWAV_RW(). */

SDL_AudioSpec *Mix_LoadAIFF_RW (SDL_RWops *src, int freesrc,
	SDL_AudioSpec *spec, Uint8 **audio_buf, Uint32 *audio_len)
{
	int was_error;
	int found_SSND;
	int found_COMM;
	int found_VHDR;
	int found_BODY;
	long start = 0;

	Uint32 chunk_type;
	Uint32 chunk_length;
	long next_chunk;

	/* AIFF magic header */
	Uint32 FORMchunk;
	Uint32 AIFFmagic;

	/* SSND chunk */
	Uint32 offset;
	Uint32 blocksize;

	/* COMM format chunk */
	Uint16 channels = 0;
	Uint32 numsamples = 0;
	Uint16 samplesize = 0;
	Uint8 sane_freq[10];
	Uint32 frequency = 0;

	/* Make sure we are passed a valid data source */
	was_error = 0;
	if ( src == NULL ) {
		was_error = 1;
		goto done;
	}

	FORMchunk	= SDL_ReadLE32(src);
	chunk_length	= SDL_ReadBE32(src);
	if ( chunk_length == AIFF ) { /* The FORMchunk has already been read */
		AIFFmagic    = chunk_length;
		chunk_length = FORMchunk;
		FORMchunk    = FORM;
	} else {
		AIFFmagic    = SDL_ReadLE32(src);
	}
	if ( (FORMchunk != FORM) || ( (AIFFmagic != AIFF) && (AIFFmagic != _8SVX) ) ) {
		SDL_SetError("Unrecognized file type (not AIFF nor 8SVX)");
		was_error = 1;
		goto done;
	}

	/* TODO: Better santity-checking. */

	found_SSND = 0;
	found_COMM = 0;
	found_VHDR = 0;
	found_BODY = 0;

	do {
		chunk_type	= SDL_ReadLE32(src);
		chunk_length	= SDL_ReadBE32(src);
		next_chunk	= SDL_RWtell(src) + chunk_length;
		/* Paranoia to avoid infinite loops */
		if (chunk_length == 0)
			break;

		switch (chunk_type) {
			case SSND:
				found_SSND	= 1;
				offset		= SDL_ReadBE32(src);
				blocksize	= SDL_ReadBE32(src);
				start		= SDL_RWtell(src) + offset;
				break;

			case COMM:
				found_COMM	= 1;
				channels	= SDL_ReadBE16(src);
				numsamples	= SDL_ReadBE32(src);
				samplesize	= SDL_ReadBE16(src);
				SDL_RWread(src, sane_freq, sizeof(sane_freq), 1);
				frequency	= SANE_to_Uint32(sane_freq);
				if (frequency == 0) {
					SDL_SetError("Bad AIFF sample frequency");
					was_error = 1;
					goto done;
				}
				break;

			case VHDR:
				found_VHDR	= 1;
				SDL_ReadBE32(src);
				SDL_ReadBE32(src);
				SDL_ReadBE32(src);
				frequency = SDL_ReadBE16(src);
				channels = 1;
				samplesize = 8;
				break;

			case BODY:
				found_BODY	= 1;
				numsamples	= chunk_length;
				start		= SDL_RWtell(src);
				break;

			default:
				break;
		}
		/* a 0 pad byte can be stored for any odd-length chunk */
		if (chunk_length&1)
			next_chunk++;
	} while ( ( ( (AIFFmagic == AIFF) && ( !found_SSND || !found_COMM ) )
		  || ( (AIFFmagic == _8SVX ) && ( !found_VHDR || !found_BODY ) ) )
		  && SDL_RWseek(src, next_chunk, RW_SEEK_SET) != 1 );

	if ( (AIFFmagic == AIFF) && !found_SSND ) {
		SDL_SetError("Bad AIFF (no SSND chunk)");
		was_error = 1;
		goto done;
	}

	if ( (AIFFmagic == AIFF) && !found_COMM ) {
		SDL_SetError("Bad AIFF (no COMM chunk)");
		was_error = 1;
		goto done;
	}

	if ( (AIFFmagic == _8SVX) && !found_VHDR ) {
		SDL_SetError("Bad 8SVX (no VHDR chunk)");
		was_error = 1;
		goto done;
	}

	if ( (AIFFmagic == _8SVX) && !found_BODY ) {
		SDL_SetError("Bad 8SVX (no BODY chunk)");
		was_error = 1;
		goto done;
	}

	/* Decode the audio data format */
	memset(spec, 0, sizeof(*spec));
	spec->freq = frequency;
	switch (samplesize) {
		case 8:
			spec->format = AUDIO_S8;
			break;
		case 16:
			spec->format = AUDIO_S16MSB;
			break;
		default:
			SDL_SetError("Unsupported AIFF samplesize");
			was_error = 1;
			goto done;
	}
	spec->channels = (Uint8) channels;
	spec->samples = 4096;		/* Good default buffer size */

	*audio_len = channels * numsamples * (samplesize / 8);
	*audio_buf = (Uint8 *)malloc(*audio_len);
	if ( *audio_buf == NULL ) {
		SDL_SetError("Out of memory");
		return(NULL);
	}
	SDL_RWseek(src, start, RW_SEEK_SET);
	if ( SDL_RWread(src, *audio_buf, *audio_len, 1) != 1 ) {
		SDL_SetError("Unable to read audio data");
		return(NULL);
	}

	/* Don't return a buffer that isn't a multiple of samplesize */
	*audio_len &= ~((samplesize / 8) - 1);

done:
	if ( freesrc && src ) {
		SDL_RWclose(src);
	}
	if ( was_error ) {
		spec = NULL;
	}
	return(spec);
}

