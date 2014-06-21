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

    Header to handle loading FLAC music files in SDL.
	    									~ Austen Dicken (admin@cvpcs.org)
*/

/* $Id:  $ */

#ifdef FLAC_MUSIC

#include <FLAC/stream_decoder.h>

typedef struct {
	FLAC__uint64 sample_size;
	unsigned sample_rate;
	unsigned channels;
	unsigned bits_per_sample;
	FLAC__uint64 total_samples;

	// the following are used to handle the callback nature of the writer
	int max_to_read;
	char *data;				// pointer to beginning of data array
	int data_len;			// size of data array
	int data_read;			// amount of data array used
	char *overflow;			// pointer to beginning of overflow array
	int overflow_len;		// size of overflow array
	int overflow_read;		// amount of overflow array used
} FLAC_Data;

typedef struct {
	int playing;
	int volume;
	int section;
	FLAC__StreamDecoder *flac_decoder;
	FLAC_Data flac_data;
	SDL_RWops *rwops;
	SDL_AudioCVT cvt;
	int len_available;
	Uint8 *snd_available;
} FLAC_music;

/* Initialize the FLAC player, with the given mixer settings
   This function returns 0, or -1 if there was an error.
 */
extern int FLAC_init(SDL_AudioSpec *mixer);

/* Set the volume for a FLAC stream */
extern void FLAC_setvolume(FLAC_music *music, int volume);

/* Load a FLAC stream from the given file */
extern FLAC_music *FLAC_new(const char *file);

/* Load an FLAC stream from an SDL_RWops object */
extern FLAC_music *FLAC_new_RW(SDL_RWops *rw);

/* Start playback of a given FLAC stream */
extern void FLAC_play(FLAC_music *music);

/* Return non-zero if a stream is currently playing */
extern int FLAC_playing(FLAC_music *music);

/* Play some of a stream previously started with FLAC_play() */
extern int FLAC_playAudio(FLAC_music *music, Uint8 *stream, int len);

/* Stop playback of a stream previously started with FLAC_play() */
extern void FLAC_stop(FLAC_music *music);

/* Close the given FLAC stream */
extern void FLAC_delete(FLAC_music *music);

/* Jump (seek) to a given position (time is in seconds) */
extern void FLAC_jump_to_time(FLAC_music *music, double time);

#endif /* FLAC_MUSIC */
