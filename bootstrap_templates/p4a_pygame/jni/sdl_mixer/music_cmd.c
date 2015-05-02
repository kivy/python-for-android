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
#include "SDL_config.h"

/* This file supports an external command for playing music */

#ifdef CMD_MUSIC

#include <sys/types.h>
#include <sys/wait.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <ctype.h>

#include "SDL_mixer.h"
#include "music_cmd.h"

/* Unimplemented */
void MusicCMD_SetVolume(int volume)
{
	Mix_SetError("No way to modify external player volume");
}

/* Load a music stream from the given file */
MusicCMD *MusicCMD_LoadSong(const char *cmd, const char *file)
{
	MusicCMD *music;

	/* Allocate and fill the music structure */
	music = (MusicCMD *)malloc(sizeof *music);
	if ( music == NULL ) {
		Mix_SetError("Out of memory");
		return(NULL);
	}
	strncpy(music->file, file, (sizeof music->file)-1);
	music->file[(sizeof music->file)-1] = '\0';
	strncpy(music->cmd, cmd, (sizeof music->cmd)-1);
	music->cmd[(sizeof music->cmd)-1] = '\0';
	music->pid = 0;

	/* We're done */
	return(music);
}

/* Parse a command line buffer into arguments */
static int ParseCommandLine(char *cmdline, char **argv)
{
	char *bufp;
	int argc;

	argc = 0;
	for ( bufp = cmdline; *bufp; ) {
		/* Skip leading whitespace */
		while ( isspace(*bufp) ) {
			++bufp;
		}
		/* Skip over argument */
		if ( *bufp == '"' ) {
			++bufp;
			if ( *bufp ) {
				if ( argv ) {
					argv[argc] = bufp;
				}
				++argc;
			}
			/* Skip over word */
			while ( *bufp && (*bufp != '"') ) {
				++bufp;
			}
		} else {
			if ( *bufp ) {
				if ( argv ) {
					argv[argc] = bufp;
				}
				++argc;
			}
			/* Skip over word */
			while ( *bufp && ! isspace(*bufp) ) {
				++bufp;
			}
		}
		if ( *bufp ) {
			if ( argv ) {
				*bufp = '\0';
			}
			++bufp;
		}
	}
	if ( argv ) {
		argv[argc] = NULL;
	}
	return(argc);
}

static char **parse_args(char *command, char *last_arg)
{
	int argc;
	char **argv;

	/* Parse the command line */
	argc = ParseCommandLine(command, NULL);
	if ( last_arg ) {
		++argc;
	}
	argv = (char **)malloc((argc+1)*(sizeof *argv));
	if ( argv == NULL ) {
		return(NULL);
	}
	argc = ParseCommandLine(command, argv);

	/* Add last command line argument */
	if ( last_arg ) {
		argv[argc++] = last_arg;
	}
	argv[argc] = NULL;

	/* We're ready! */
	return(argv);
}

/* Start playback of a given music stream */
void MusicCMD_Start(MusicCMD *music)
{
#ifdef HAVE_FORK
	music->pid = fork();
#else
	music->pid = vfork();
#endif
	switch(music->pid) {
	    /* Failed fork() system call */
	    case -1:
		Mix_SetError("fork() failed");
		return;

	    /* Child process - executes here */
	    case 0: {
		    char command[PATH_MAX];
		    char **argv;

		    /* Unblock signals in case we're called from a thread */
		    {
			sigset_t mask;
			sigemptyset(&mask);
			sigprocmask(SIG_SETMASK, &mask, NULL);
		    }

		    /* Execute the command */
		    strcpy(command, music->cmd);
		    argv = parse_args(command, music->file);
		    if ( argv != NULL ) {
			execvp(argv[0], argv);
		    }

		    /* exec() failed */
		    perror(argv[0]);
		    _exit(-1);
		}
		break;

	    /* Parent process - executes here */
	    default:
		break;
	}
	return;
}

/* Stop playback of a stream previously started with MusicCMD_Start() */
void MusicCMD_Stop(MusicCMD *music)
{
	int status;

	if ( music->pid > 0 ) {
		while ( kill(music->pid, 0) == 0 ) {
			kill(music->pid, SIGTERM);
			sleep(1);
			waitpid(music->pid, &status, WNOHANG);
		}
		music->pid = 0;
	}
}

/* Pause playback of a given music stream */
void MusicCMD_Pause(MusicCMD *music)
{
	if ( music->pid > 0 ) {
		kill(music->pid, SIGSTOP);
	}
}

/* Resume playback of a given music stream */
void MusicCMD_Resume(MusicCMD *music)
{
	if ( music->pid > 0 ) {
		kill(music->pid, SIGCONT);
	}
}

/* Close the given music stream */
void MusicCMD_FreeSong(MusicCMD *music)
{
	free(music);
}

/* Return non-zero if a stream is currently playing */
int MusicCMD_Active(MusicCMD *music)
{
	int status;
	int active;

	active = 0;
	if ( music->pid > 0 ) {
		waitpid(music->pid, &status, WNOHANG);
		if ( kill(music->pid, 0) == 0 ) {
			active = 1;
		}
	}
	return(active);
}

#endif /* CMD_MUSIC */
