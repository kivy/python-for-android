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

/* $Id: music_mod.h 4211 2008-12-08 00:27:32Z slouken $ */

#ifdef MOD_MUSIC

/* This file supports MOD tracker music streams */

struct MODULE;

/* Initialize the Ogg Vorbis player, with the given mixer settings
   This function returns 0, or -1 if there was an error.
 */
extern int MOD_init(SDL_AudioSpec *mixer);

/* Uninitialize the music players */
extern void MOD_exit(void);

/* Set the volume for a MOD stream */
extern void MOD_setvolume(struct MODULE *music, int volume);

/* Load a MOD stream from the given file */
extern struct MODULE *MOD_new(const char *file);

/* Load a MOD stream from an SDL_RWops object */
extern struct MODULE *MOD_new_RW(SDL_RWops *rw);

/* Start playback of a given MOD stream */
extern void MOD_play(struct MODULE *music);

/* Return non-zero if a stream is currently playing */
extern int MOD_playing(struct MODULE *music);

/* Play some of a stream previously started with MOD_play() */
extern int MOD_playAudio(struct MODULE *music, Uint8 *stream, int len);

/* Stop playback of a stream previously started with MOD_play() */
extern void MOD_stop(struct MODULE *music);

/* Close the given MOD stream */
extern void MOD_delete(struct MODULE *music);

/* Jump (seek) to a given position (time is in seconds) */
extern void MOD_jump_to_time(struct MODULE *music, double time);

#endif /* MOD_MUSIC */
