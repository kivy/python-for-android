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

/* $Id: music_ogg.h 4211 2008-12-08 00:27:32Z slouken $ */

#ifdef OGG_MUSIC

/* This file supports Ogg Vorbis music streams */

#ifdef OGG_USE_TREMOR
#include <tremor/ivorbisfile.h>
#else
#include <vorbis/vorbisfile.h>
#endif

typedef struct {
	int playing;
	int volume;
	OggVorbis_File vf;
	int section;
	SDL_AudioCVT cvt;
	int len_available;
	Uint8 *snd_available;
} OGG_music;

/* Initialize the Ogg Vorbis player, with the given mixer settings
   This function returns 0, or -1 if there was an error.
 */
extern int OGG_init(SDL_AudioSpec *mixer);

/* Set the volume for an OGG stream */
extern void OGG_setvolume(OGG_music *music, int volume);

/* Load an OGG stream from the given file */
extern OGG_music *OGG_new(const char *file);

/* Load an OGG stream from an SDL_RWops object */
extern OGG_music *OGG_new_RW(SDL_RWops *rw);

/* Start playback of a given OGG stream */
extern void OGG_play(OGG_music *music);

/* Return non-zero if a stream is currently playing */
extern int OGG_playing(OGG_music *music);

/* Play some of a stream previously started with OGG_play() */
extern int OGG_playAudio(OGG_music *music, Uint8 *stream, int len);

/* Stop playback of a stream previously started with OGG_play() */
extern void OGG_stop(OGG_music *music);

/* Close the given OGG stream */
extern void OGG_delete(OGG_music *music);

/* Jump (seek) to a given position (time is in seconds) */
extern void OGG_jump_to_time(OGG_music *music, double time);

#endif /* OGG_MUSIC */
