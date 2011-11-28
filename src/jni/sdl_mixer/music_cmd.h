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

/* This file supports an external command for playing music */

#ifdef CMD_MUSIC

#include <sys/types.h>
#include <limits.h>
#include <stdio.h>
#if defined(__linux__) && defined(__arm__)
# include <linux/limits.h>
#endif
typedef struct {
	char file[PATH_MAX];
	char cmd[PATH_MAX];
	pid_t pid;
} MusicCMD;

/* Unimplemented */
extern void MusicCMD_SetVolume(int volume);

/* Load a music stream from the given file */
extern MusicCMD *MusicCMD_LoadSong(const char *cmd, const char *file);

/* Start playback of a given music stream */
extern void MusicCMD_Start(MusicCMD *music);

/* Stop playback of a stream previously started with MusicCMD_Start() */
extern void MusicCMD_Stop(MusicCMD *music);

/* Pause playback of a given music stream */
extern void MusicCMD_Pause(MusicCMD *music);

/* Resume playback of a given music stream */
extern void MusicCMD_Resume(MusicCMD *music);

/* Close the given music stream */
extern void MusicCMD_FreeSong(MusicCMD *music);

/* Return non-zero if a stream is currently playing */
extern int MusicCMD_Active(MusicCMD *music);

#endif /* CMD_MUSIC */
