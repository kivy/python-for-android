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

/* $Id: music.c 5247 2009-11-14 20:44:30Z slouken $ */

#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <assert.h>
#include "SDL_endian.h"
#include "SDL_audio.h"
#include "SDL_timer.h"

#include "SDL_mixer.h"

#ifdef CMD_MUSIC
#include "music_cmd.h"
#endif
#ifdef WAV_MUSIC
#include "wavestream.h"
#endif
#ifdef MOD_MUSIC
#include "music_mod.h"
#endif
#ifdef MID_MUSIC
#  ifdef USE_TIMIDITY_MIDI
#    include "timidity.h"
#  endif
#  ifdef USE_NATIVE_MIDI
#    include "native_midi.h"
#  endif
#  if defined(USE_TIMIDITY_MIDI) && defined(USE_NATIVE_MIDI)
#    define MIDI_ELSE	else
#  else
#    define MIDI_ELSE
#  endif
#endif
#ifdef OGG_MUSIC
#include "music_ogg.h"
#endif
#ifdef MP3_MUSIC
#include "dynamic_mp3.h"
#endif
#ifdef MP3_MAD_MUSIC
#include "music_mad.h"
#endif
#ifdef FLAC_MUSIC
#include "music_flac.h"
#endif

#if defined(MP3_MUSIC) || defined(MP3_MAD_MUSIC)
static SDL_AudioSpec used_mixer;
#endif


int volatile music_active = 1;
static int volatile music_stopped = 0;
static int music_loops = 0;
static char *music_cmd = NULL;
static Mix_Music * volatile music_playing = NULL;
static int music_volume = MIX_MAX_VOLUME;

struct _Mix_Music {
	Mix_MusicType type;
	union {
#ifdef CMD_MUSIC
		MusicCMD *cmd;
#endif
#ifdef WAV_MUSIC
		WAVStream *wave;
#endif
#ifdef MOD_MUSIC
		struct MODULE *module;
#endif
#ifdef MID_MUSIC
#ifdef USE_TIMIDITY_MIDI
		MidiSong *midi;
#endif
#ifdef USE_NATIVE_MIDI
		NativeMidiSong *nativemidi;
#endif
#endif
#ifdef OGG_MUSIC
		OGG_music *ogg;
#endif
#ifdef MP3_MUSIC
		SMPEG *mp3;
#endif
#ifdef MP3_MAD_MUSIC
		mad_data *mp3_mad;
#endif
#ifdef FLAC_MUSIC
		FLAC_music *flac;
#endif
	} data;
	Mix_Fading fading;
	int fade_step;
	int fade_steps;
	int error;
};
#ifdef MID_MUSIC
#ifdef USE_TIMIDITY_MIDI
static int timidity_ok;
static int samplesize;
#endif
#ifdef USE_NATIVE_MIDI
static int native_midi_ok;
#endif
#endif

/* Used to calculate fading steps */
static int ms_per_step;

/* rcg06042009 report available decoders at runtime. */
static const char **music_decoders = NULL;
static int num_decoders = 0;

int Mix_GetNumMusicDecoders(void)
{
	return(num_decoders);
}

const char *Mix_GetMusicDecoder(int index)
{
	if ((index < 0) || (index >= num_decoders)) {
		return NULL;
	}
	return(music_decoders[index]);
}

static void add_music_decoder(const char *decoder)
{
	void *ptr = realloc(music_decoders, (num_decoders + 1) * sizeof (const char **));
	if (ptr == NULL) {
		return;  /* oh well, go on without it. */
	}
	music_decoders = (const char **) ptr;
	music_decoders[num_decoders++] = decoder;
}

/* Local low-level functions prototypes */
static void music_internal_initialize_volume(void);
static void music_internal_volume(int volume);
static int  music_internal_play(Mix_Music *music, double position);
static int  music_internal_position(double position);
static int  music_internal_playing();
static void music_internal_halt(void);


/* Support for hooking when the music has finished */
static void (*music_finished_hook)(void) = NULL;

void Mix_HookMusicFinished(void (*music_finished)(void))
{
	SDL_LockAudio();
	music_finished_hook = music_finished;
	SDL_UnlockAudio();
}


/* If music isn't playing, halt it if no looping is required, restart it */
/* otherwhise. NOP if the music is playing */
static int music_halt_or_loop (void)
{
	/* Restart music if it has to loop */
	
	if (!music_internal_playing()) 
	{
		/* Restart music if it has to loop at a high level */
		if (music_loops && --music_loops)
		{
			Mix_Fading current_fade = music_playing->fading;
			music_internal_play(music_playing, 0.0);
			music_playing->fading = current_fade;
		} 
		else 
		{
			music_internal_halt();
			if (music_finished_hook)
				music_finished_hook();
			
			return 0;
		}
	}
	
	return 1;
}



/* Mixing function */
void music_mixer(void *udata, Uint8 *stream, int len)
{
	int left = 0;

	if ( music_playing && music_active ) {
		/* Handle fading */
		if ( music_playing->fading != MIX_NO_FADING ) {
			if ( music_playing->fade_step++ < music_playing->fade_steps ) {
				int volume;
				int fade_step = music_playing->fade_step;
				int fade_steps = music_playing->fade_steps;

				if ( music_playing->fading == MIX_FADING_OUT ) {
					volume = (music_volume * (fade_steps-fade_step)) / fade_steps;
				} else { /* Fading in */
					volume = (music_volume * fade_step) / fade_steps;
				}
				music_internal_volume(volume);
			} else {
				if ( music_playing->fading == MIX_FADING_OUT ) {
					music_internal_halt();
					if ( music_finished_hook ) {
						music_finished_hook();
					}
					return;
				}
				music_playing->fading = MIX_NO_FADING;
			}
		}
		
		if (music_halt_or_loop() == 0)
			return;
		
		
		switch (music_playing->type) {
#ifdef CMD_MUSIC
			case MUS_CMD:
				/* The playing is done externally */
				break;
#endif
#ifdef WAV_MUSIC
			case MUS_WAV:
				left = WAVStream_PlaySome(stream, len);
				break;
#endif
#ifdef MOD_MUSIC
			case MUS_MOD:
				left = MOD_playAudio(music_playing->data.module, stream, len);
				break;
#endif
#ifdef MID_MUSIC
#ifdef USE_TIMIDITY_MIDI
			case MUS_MID:
				if ( timidity_ok ) {
					int samples = len / samplesize;
  					Timidity_PlaySome(stream, samples);
				}
				break;
#endif
#endif
#ifdef OGG_MUSIC
			case MUS_OGG:
				
				left = OGG_playAudio(music_playing->data.ogg, stream, len);
				break;
#endif
#ifdef FLAC_MUSIC
			case MUS_FLAC:
				left = FLAC_playAudio(music_playing->data.flac, stream, len);
				break;
#endif
#ifdef MP3_MUSIC
			case MUS_MP3:
				left = (len - smpeg.SMPEG_playAudio(music_playing->data.mp3, stream, len));
				break;
#endif
#ifdef MP3_MAD_MUSIC
			case MUS_MP3_MAD:
				left = mad_getSamples(music_playing->data.mp3_mad, stream, len);
				break;
#endif
			default:
				/* Unknown music type?? */
				break;
		}
	}

	/* Handle seamless music looping */
	if (left > 0 && left < len && music_halt_or_loop()) {
		music_mixer(udata, stream+(len-left), left);
	}
}

/* Initialize the music players with a certain desired audio format */
int open_music(SDL_AudioSpec *mixer)
{
#ifdef WAV_MUSIC
	if ( WAVStream_Init(mixer) == 0 ) {
		add_music_decoder("WAVE");
	}
#endif
#ifdef MOD_MUSIC
	if ( MOD_init(mixer) == 0 ) {
		add_music_decoder("MIKMOD");
	}
#endif
#ifdef MID_MUSIC
#ifdef USE_TIMIDITY_MIDI
	samplesize = mixer->size / mixer->samples;
	if ( Timidity_Init(mixer->freq, mixer->format,
	                    mixer->channels, mixer->samples) == 0 ) {
		timidity_ok = 1;
		add_music_decoder("TIMIDITY");
	} else {
		timidity_ok = 0;
	}
#endif
#ifdef USE_NATIVE_MIDI
#ifdef USE_TIMIDITY_MIDI
	native_midi_ok = !timidity_ok;
	if ( !native_midi_ok ) {
		native_midi_ok = (getenv("SDL_NATIVE_MUSIC") != NULL);
	}
	if ( native_midi_ok )
#endif
		native_midi_ok = native_midi_detect();
	if ( native_midi_ok )
		add_music_decoder("NATIVEMIDI");
#endif
#endif
#ifdef OGG_MUSIC
	if ( OGG_init(mixer) == 0 ) {
		add_music_decoder("OGG");
	}
#endif
#ifdef FLAC_MUSIC
	if ( FLAC_init(mixer) == 0 ) {
		add_music_decoder("FLAC");
	}
#endif
#if defined(MP3_MUSIC) || defined(MP3_MAD_MUSIC)
	/* Keep a copy of the mixer */
	used_mixer = *mixer;
	add_music_decoder("MP3");
#endif

	music_playing = NULL;
	music_stopped = 0;
	Mix_VolumeMusic(SDL_MIX_MAXVOLUME);

	/* Calculate the number of ms for each callback */
	ms_per_step = (int) (((float)mixer->samples * 1000.0) / mixer->freq);

	return(0);
}

/* Portable case-insensitive string compare function */
int MIX_string_equals(const char *str1, const char *str2)
{
	while ( *str1 && *str2 ) {
		if ( toupper((unsigned char)*str1) !=
		     toupper((unsigned char)*str2) )
			break;
		++str1;
		++str2;
	}
	return (!*str1 && !*str2);
}

/* Load a music file */
Mix_Music *Mix_LoadMUS(const char *file)
{
	FILE *fp;
	char *ext;
	Uint8 magic[5], moremagic[9];
	Mix_Music *music;

	/* Figure out what kind of file this is */
	fp = fopen(file, "rb");
	if ( (fp == NULL) || !fread(magic, 4, 1, fp) ) {
		if ( fp != NULL ) {
			fclose(fp);
		}
		Mix_SetError("Couldn't read from '%s'", file);
		return(NULL);
	}
	if (!fread(moremagic, 8, 1, fp)) {
		Mix_SetError("Couldn't read from '%s'", file);
		return(NULL);
	}
	magic[4] = '\0';
	moremagic[8] = '\0';
	fclose(fp);

	/* Figure out the file extension, so we can determine the type */
	ext = strrchr(file, '.');
	if ( ext ) ++ext; /* skip the dot in the extension */

	/* Allocate memory for the music structure */
	music = (Mix_Music *)malloc(sizeof(Mix_Music));
	if ( music == NULL ) {
		Mix_SetError("Out of memory");
		return(NULL);
	}
	music->error = 0;

#ifdef CMD_MUSIC
	if ( music_cmd ) {
		music->type = MUS_CMD;
		music->data.cmd = MusicCMD_LoadSong(music_cmd, file);
		if ( music->data.cmd == NULL ) {
			music->error = 1;
		}
	} else
#endif
#ifdef WAV_MUSIC
	/* WAVE files have the magic four bytes "RIFF"
	   AIFF files have the magic 12 bytes "FORM" XXXX "AIFF"
	 */
	if ( (ext && MIX_string_equals(ext, "WAV")) ||
	     ((strcmp((char *)magic, "RIFF") == 0) && (strcmp((char *)(moremagic+4), "WAVE") == 0)) ||
	     (strcmp((char *)magic, "FORM") == 0) ) {
		music->type = MUS_WAV;
		music->data.wave = WAVStream_LoadSong(file, (char *)magic);
		if ( music->data.wave == NULL ) {
		  	Mix_SetError("Unable to load WAV file");
			music->error = 1;
		}
	} else
#endif
#ifdef MID_MUSIC
	/* MIDI files have the magic four bytes "MThd" */
	if ( (ext && MIX_string_equals(ext, "MID")) ||
	     (ext && MIX_string_equals(ext, "MIDI")) ||
	     strcmp((char *)magic, "MThd") == 0  ||
	     ( strcmp((char *)magic, "RIFF") == 0  &&
	  	strcmp((char *)(moremagic+4), "RMID") == 0 ) ) {
		music->type = MUS_MID;
#ifdef USE_NATIVE_MIDI
  		if ( native_midi_ok ) {
  			music->data.nativemidi = native_midi_loadsong(file);
	  		if ( music->data.nativemidi == NULL ) {
		  		Mix_SetError("%s", native_midi_error());
			  	music->error = 1;
			}
	  	} MIDI_ELSE
#endif
#ifdef USE_TIMIDITY_MIDI
		if ( timidity_ok ) {
			music->data.midi = Timidity_LoadSong(file);
			if ( music->data.midi == NULL ) {
				Mix_SetError("%s", Timidity_Error());
				music->error = 1;
			}
		} else {
			Mix_SetError("%s", Timidity_Error());
			music->error = 1;
		}
#endif
	} else
#endif
#ifdef OGG_MUSIC
	/* Ogg Vorbis files have the magic four bytes "OggS" */
	if ( (ext && MIX_string_equals(ext, "OGG")) ||
	     strcmp((char *)magic, "OggS") == 0 ) {
		music->type = MUS_OGG;
		music->data.ogg = OGG_new(file);
		if ( music->data.ogg == NULL ) {
			music->error = 1;
		}
	} else
#endif
#ifdef FLAC_MUSIC
	/* FLAC files have the magic four bytes "fLaC" */
	if ( (ext && MIX_string_equals(ext, "FLAC")) ||
		 strcmp((char *)magic, "fLaC") == 0 ) {
		music->type = MUS_FLAC;
		music->data.flac = FLAC_new(file);
		if ( music->data.flac == NULL ) {
			music->error = 1;
		}
	} else
#endif
#ifdef MP3_MUSIC
	if ( (ext && MIX_string_equals(ext, "MPG")) ||
	     (ext && MIX_string_equals(ext, "MP3")) ||
	     (ext && MIX_string_equals(ext, "MPEG")) ||
	     (magic[0] == 0xFF && (magic[1] & 0xF0) == 0xF0) ||
	     (strncmp((char *)magic, "ID3", 3) == 0) ) {
		if ( Mix_Init(MIX_INIT_MP3) ) {
			SMPEG_Info info;
			music->type = MUS_MP3;
			music->data.mp3 = smpeg.SMPEG_new(file, &info, 0);
			if ( !info.has_audio ) {
				Mix_SetError("MPEG file does not have any audio stream.");
				music->error = 1;
			} else {
				smpeg.SMPEG_actualSpec(music->data.mp3, &used_mixer);
			}
		} else {
			music->error = 1;
		}
	} else
#endif
#ifdef MP3_MAD_MUSIC
	if ( (ext && MIX_string_equals(ext, "MPG")) ||
	     (ext && MIX_string_equals(ext, "MP3")) ||
	     (ext && MIX_string_equals(ext, "MPEG")) ||
	     (ext && MIX_string_equals(ext, "MAD")) ||
	     (magic[0] == 0xFF && (magic[1] & 0xF0) == 0xF0) ||
	     (strncmp((char *)magic, "ID3", 3) == 0) ) {
		music->type = MUS_MP3_MAD;
		music->data.mp3_mad = mad_openFile(file, &used_mixer);
		if (music->data.mp3_mad == 0) {
		    Mix_SetError("Could not initialize MPEG stream.");
			music->error = 1;
		}
	} else
#endif
#ifdef MOD_MUSIC
	if ( 1 ) {
		music->type = MUS_MOD;
		music->data.module = MOD_new(file);
		if ( music->data.module == NULL ) {
			music->error = 1;
		}
	} else
#endif
	{
		Mix_SetError("Unrecognized music format");
		music->error = 1;
	}
	if ( music->error ) {
		free(music);
		music = NULL;
	}
	return(music);
}

/* Free a music chunk previously loaded */
void Mix_FreeMusic(Mix_Music *music)
{
	if ( music ) {
		/* Stop the music if it's currently playing */
		SDL_LockAudio();
		if ( music == music_playing ) {
			/* Wait for any fade out to finish */
			while ( music->fading == MIX_FADING_OUT ) {
				SDL_UnlockAudio();
				SDL_Delay(100);
				SDL_LockAudio();
			}
			if ( music == music_playing ) {
				music_internal_halt();
			}
		}
		SDL_UnlockAudio();
		switch (music->type) {
#ifdef CMD_MUSIC
			case MUS_CMD:
				MusicCMD_FreeSong(music->data.cmd);
				break;
#endif
#ifdef WAV_MUSIC
			case MUS_WAV:
				WAVStream_FreeSong(music->data.wave);
				break;
#endif
#ifdef MOD_MUSIC
			case MUS_MOD:
				MOD_delete(music->data.module);
				break;
#endif
#ifdef MID_MUSIC
			case MUS_MID:
#ifdef USE_NATIVE_MIDI
  				if ( native_midi_ok ) {
					native_midi_freesong(music->data.nativemidi);
				} MIDI_ELSE
#endif
#ifdef USE_TIMIDITY_MIDI
				if ( timidity_ok ) {
					Timidity_FreeSong(music->data.midi);
				}
#endif
				break;
#endif
#ifdef OGG_MUSIC
			case MUS_OGG:
				OGG_delete(music->data.ogg);
				break;
#endif
#ifdef FLAC_MUSIC
			case MUS_FLAC:
				FLAC_delete(music->data.flac);
				break;
#endif
#ifdef MP3_MUSIC
			case MUS_MP3:
				smpeg.SMPEG_delete(music->data.mp3);
				break;
#endif
#ifdef MP3_MAD_MUSIC
			case MUS_MP3_MAD:
				mad_closeFile(music->data.mp3_mad);
				break;
#endif
			default:
				/* Unknown music type?? */
				break;
		}
		free(music);
	}
}

/* Find out the music format of a mixer music, or the currently playing
   music, if 'music' is NULL.
*/
Mix_MusicType Mix_GetMusicType(const Mix_Music *music)
{
	Mix_MusicType type = MUS_NONE;

	if ( music ) {
		type = music->type;
	} else {
		SDL_LockAudio();
		if ( music_playing ) {
			type = music_playing->type;
		}
		SDL_UnlockAudio();
	}
	return(type);
}

/* Play a music chunk.  Returns 0, or -1 if there was an error.
 */
static int music_internal_play(Mix_Music *music, double position)
{
	int retval = 0;

	/* Note the music we're playing */
	if ( music_playing ) {
		music_internal_halt();
	}
	music_playing = music;

	/* Set the initial volume */
	if ( music->type != MUS_MOD ) {
		music_internal_initialize_volume();
	}

	/* Set up for playback */
	switch (music->type) {
#ifdef CMD_MUSIC
	    case MUS_CMD:
		MusicCMD_Start(music->data.cmd);
		break;
#endif
#ifdef WAV_MUSIC
	    case MUS_WAV:
		WAVStream_Start(music->data.wave);
		break;
#endif
#ifdef MOD_MUSIC
	    case MUS_MOD:
		MOD_play(music->data.module);
		/* Player_SetVolume() does nothing before Player_Start() */
		music_internal_initialize_volume();
		break;
#endif
#ifdef MID_MUSIC
	    case MUS_MID:
#ifdef USE_NATIVE_MIDI
		if ( native_midi_ok ) {
			native_midi_start(music->data.nativemidi);
		} MIDI_ELSE
#endif
#ifdef USE_TIMIDITY_MIDI
		if ( timidity_ok ) {
			Timidity_Start(music->data.midi);
		}
#endif
		break;
#endif
#ifdef OGG_MUSIC
	    case MUS_OGG:
		OGG_play(music->data.ogg);
		break;
#endif
#ifdef FLAC_MUSIC
	    case MUS_FLAC:
		FLAC_play(music->data.flac);
		break;
#endif
#ifdef MP3_MUSIC
	    case MUS_MP3:
		smpeg.SMPEG_enableaudio(music->data.mp3,1);
		smpeg.SMPEG_enablevideo(music->data.mp3,0);
		smpeg.SMPEG_play(music_playing->data.mp3);
		break;
#endif
#ifdef MP3_MAD_MUSIC
	    case MUS_MP3_MAD:
		mad_start(music->data.mp3_mad);
		break;
#endif
	    default:
		Mix_SetError("Can't play unknown music type");
		retval = -1;
		break;
	}

	/* Set the playback position, note any errors if an offset is used */
	if ( retval == 0 ) {
		if ( position > 0.0 ) {
			if ( music_internal_position(position) < 0 ) {
				Mix_SetError("Position not implemented for music type");
				retval = -1;
			}
		} else {
			music_internal_position(0.0);
		}
	}

	/* If the setup failed, we're not playing any music anymore */
	if ( retval < 0 ) {
		music_playing = NULL;
	}
	return(retval);
}
int Mix_FadeInMusicPos(Mix_Music *music, int loops, int ms, double position)
{
	int retval;

	/* Don't play null pointers :-) */
	if ( music == NULL ) {
		Mix_SetError("music parameter was NULL");
		return(-1);
	}

	/* Setup the data */
	if ( ms ) {
		music->fading = MIX_FADING_IN;
	} else {
		music->fading = MIX_NO_FADING;
	}
	music->fade_step = 0;
	music->fade_steps = ms/ms_per_step;

	/* Play the puppy */
	SDL_LockAudio();
	/* If the current music is fading out, wait for the fade to complete */
	while ( music_playing && (music_playing->fading == MIX_FADING_OUT) ) {
		SDL_UnlockAudio();
		SDL_Delay(100);
		SDL_LockAudio();
	}
	music_active = 1;
	music_loops = loops;
	retval = music_internal_play(music, position);
	SDL_UnlockAudio();

	return(retval);
}
int Mix_FadeInMusic(Mix_Music *music, int loops, int ms)
{
	return Mix_FadeInMusicPos(music, loops, ms, 0.0);
}
int Mix_PlayMusic(Mix_Music *music, int loops)
{
	return Mix_FadeInMusicPos(music, loops, 0, 0.0);
}

/* Set the playing music position */
int music_internal_position(double position)
{
	int retval = 0;

	switch (music_playing->type) {
#ifdef MOD_MUSIC
	    case MUS_MOD:
		MOD_jump_to_time(music_playing->data.module, position);
		break;
#endif
#ifdef OGG_MUSIC
	    case MUS_OGG:
		OGG_jump_to_time(music_playing->data.ogg, position);
		break;
#endif
#ifdef FLAC_MUSIC
	    case MUS_FLAC:
		FLAC_jump_to_time(music_playing->data.flac, position);
		break;
#endif
#ifdef MP3_MUSIC
	    case MUS_MP3:
		if ( position > 0.0 ) {
			smpeg.SMPEG_skip(music_playing->data.mp3, (float)position);
		} else {
			smpeg.SMPEG_rewind(music_playing->data.mp3);
			smpeg.SMPEG_play(music_playing->data.mp3);
		}
		break;
#endif
#ifdef MP3_MAD_MUSIC
	    case MUS_MP3_MAD:
		mad_seek(music_playing->data.mp3_mad, position);
		break;
#endif
	    default:
		/* TODO: Implement this for other music backends */
		retval = -1;
		break;
	}
	return(retval);
}
int Mix_SetMusicPosition(double position)
{
	int retval;

	SDL_LockAudio();
	if ( music_playing ) {
		retval = music_internal_position(position);
		if ( retval < 0 ) {
			Mix_SetError("Position not implemented for music type");
		}
	} else {
		Mix_SetError("Music isn't playing");
		retval = -1;
	}
	SDL_UnlockAudio();

	return(retval);
}

/* Set the music's initial volume */
static void music_internal_initialize_volume(void)
{
	if ( music_playing->fading == MIX_FADING_IN ) {
		music_internal_volume(0);
	} else {
		music_internal_volume(music_volume);
	}
}

/* Set the music volume */
static void music_internal_volume(int volume)
{
	switch (music_playing->type) {
#ifdef CMD_MUSIC
	    case MUS_CMD:
		MusicCMD_SetVolume(volume);
		break;
#endif
#ifdef WAV_MUSIC
	    case MUS_WAV:
		WAVStream_SetVolume(volume);
		break;
#endif
#ifdef MOD_MUSIC
	    case MUS_MOD:
		MOD_setvolume(music_playing->data.module, volume);
		break;
#endif
#ifdef MID_MUSIC
	    case MUS_MID:
#ifdef USE_NATIVE_MIDI
		if ( native_midi_ok ) {
			native_midi_setvolume(volume);
		} MIDI_ELSE
#endif
#ifdef USE_TIMIDITY_MIDI
		if ( timidity_ok ) {
			Timidity_SetVolume(volume);
		}
#endif
		break;
#endif
#ifdef OGG_MUSIC
	    case MUS_OGG:
		OGG_setvolume(music_playing->data.ogg, volume);
		break;
#endif
#ifdef FLAC_MUSIC
	    case MUS_FLAC:
		FLAC_setvolume(music_playing->data.flac, volume);
		break;
#endif
#ifdef MP3_MUSIC
	    case MUS_MP3:
		smpeg.SMPEG_setvolume(music_playing->data.mp3,(int)(((float)volume/(float)MIX_MAX_VOLUME)*100.0));
		break;
#endif
#ifdef MP3_MAD_MUSIC
	    case MUS_MP3_MAD:
		mad_setVolume(music_playing->data.mp3_mad, volume);
		break;
#endif
	    default:
		/* Unknown music type?? */
		break;
	}
}
int Mix_VolumeMusic(int volume)
{
	int prev_volume;

	prev_volume = music_volume;
	if ( volume < 0 ) {
		return prev_volume;
	}
	if ( volume > SDL_MIX_MAXVOLUME ) {
		volume = SDL_MIX_MAXVOLUME;
	}
	music_volume = volume;
	SDL_LockAudio();
	if ( music_playing ) {
		music_internal_volume(music_volume);
	}
	SDL_UnlockAudio();
	return(prev_volume);
}

/* Halt playing of music */
static void music_internal_halt(void)
{
	switch (music_playing->type) {
#ifdef CMD_MUSIC
	    case MUS_CMD:
		MusicCMD_Stop(music_playing->data.cmd);
		break;
#endif
#ifdef WAV_MUSIC
	    case MUS_WAV:
		WAVStream_Stop();
		break;
#endif
#ifdef MOD_MUSIC
	    case MUS_MOD:
		MOD_stop(music_playing->data.module);
		break;
#endif
#ifdef MID_MUSIC
	    case MUS_MID:
#ifdef USE_NATIVE_MIDI
		if ( native_midi_ok ) {
			native_midi_stop();
		} MIDI_ELSE
#endif
#ifdef USE_TIMIDITY_MIDI
		if ( timidity_ok ) {
			Timidity_Stop();
		}
#endif
		break;
#endif
#ifdef OGG_MUSIC
	    case MUS_OGG:
		OGG_stop(music_playing->data.ogg);
		break;
#endif
#ifdef FLAC_MUSIC
	    case MUS_FLAC:
		FLAC_stop(music_playing->data.flac);
		break;
#endif
#ifdef MP3_MUSIC
	    case MUS_MP3:
		smpeg.SMPEG_stop(music_playing->data.mp3);
		break;
#endif
#ifdef MP3_MAD_MUSIC
	    case MUS_MP3_MAD:
		mad_stop(music_playing->data.mp3_mad);
		break;
#endif
	    default:
		/* Unknown music type?? */
		return;
	}
	music_playing->fading = MIX_NO_FADING;
	music_playing = NULL;
}
int Mix_HaltMusic(void)
{
	SDL_LockAudio();
	if ( music_playing ) {
		music_internal_halt();
	}
	SDL_UnlockAudio();

	return(0);
}

/* Progressively stop the music */
int Mix_FadeOutMusic(int ms)
{
	int retval = 0;

	if (ms <= 0) {  /* just halt immediately. */
		Mix_HaltMusic();
		return 1;
	}

	SDL_LockAudio();
	if ( music_playing) {
                int fade_steps = (ms + ms_per_step - 1)/ms_per_step;
                if ( music_playing->fading == MIX_NO_FADING ) {
	        	music_playing->fade_step = 0;
                } else {
                        int step;
                        int old_fade_steps = music_playing->fade_steps;
                        if ( music_playing->fading == MIX_FADING_OUT ) {
                                step = music_playing->fade_step;
                        } else {
                                step = old_fade_steps
                                        - music_playing->fade_step + 1;
                        }
                        music_playing->fade_step = (step * fade_steps)
                                / old_fade_steps;
                }
		music_playing->fading = MIX_FADING_OUT;
		music_playing->fade_steps = fade_steps;
		retval = 1;
	}
	SDL_UnlockAudio();

	return(retval);
}

Mix_Fading Mix_FadingMusic(void)
{
	Mix_Fading fading = MIX_NO_FADING;

	SDL_LockAudio();
	if ( music_playing ) {
		fading = music_playing->fading;
	}
	SDL_UnlockAudio();

	return(fading);
}

/* Pause/Resume the music stream */
void Mix_PauseMusic(void)
{
	music_active = 0;
}

void Mix_ResumeMusic(void)
{
	music_active = 1;
}

void Mix_RewindMusic(void)
{
	Mix_SetMusicPosition(0.0);
}

int Mix_PausedMusic(void)
{
	return (music_active == 0);
}

/* Check the status of the music */
static int music_internal_playing()
{
	int playing = 1;
	switch (music_playing->type) {
#ifdef CMD_MUSIC
	    case MUS_CMD:
		if (!MusicCMD_Active(music_playing->data.cmd)) {
			playing = 0;
		}
		break;
#endif
#ifdef WAV_MUSIC
	    case MUS_WAV:
		if ( ! WAVStream_Active() ) {
			playing = 0;
		}
		break;
#endif
#ifdef MOD_MUSIC
	    case MUS_MOD:
		if ( ! MOD_playing(music_playing->data.module) ) {
			playing = 0;
		}
		break;
#endif
#ifdef MID_MUSIC
	    case MUS_MID:
#ifdef USE_NATIVE_MIDI
		if ( native_midi_ok ) {
			if ( ! native_midi_active() )
				playing = 0;
		} MIDI_ELSE
#endif
#ifdef USE_TIMIDITY_MIDI
		if ( timidity_ok ) {
			if ( ! Timidity_Active() )
				playing = 0;
		}
#endif
		break;
#endif
#ifdef OGG_MUSIC
	    case MUS_OGG:
		if ( ! OGG_playing(music_playing->data.ogg) ) {
			playing = 0;
		}
		break;
#endif
#ifdef FLAC_MUSIC
	    case MUS_FLAC:
		if ( ! FLAC_playing(music_playing->data.flac) ) {
			playing = 0;
		}
		break;
#endif
#ifdef MP3_MUSIC
	    case MUS_MP3:
		if ( smpeg.SMPEG_status(music_playing->data.mp3) != SMPEG_PLAYING )
			playing = 0;
		break;
#endif
#ifdef MP3_MAD_MUSIC
	    case MUS_MP3_MAD:
		if (!mad_isPlaying(music_playing->data.mp3_mad)) {
			playing = 0;
		}
		break;
#endif
	    default:
		playing = 0;
		break;
	}
	return(playing);
}
int Mix_PlayingMusic(void)
{
	int playing = 0;

	SDL_LockAudio();
	if ( music_playing ) {
		playing = music_internal_playing();
	}
	SDL_UnlockAudio();

	return(playing);
}

/* Set the external music playback command */
int Mix_SetMusicCMD(const char *command)
{
	Mix_HaltMusic();
	if ( music_cmd ) {
		free(music_cmd);
		music_cmd = NULL;
	}
	if ( command ) {
		music_cmd = (char *)malloc(strlen(command)+1);
		if ( music_cmd == NULL ) {
			return(-1);
		}
		strcpy(music_cmd, command);
	}
	return(0);
}

int Mix_SetSynchroValue(int i)
{
	/* Not supported by any players at this time */
	return(-1);
}

int Mix_GetSynchroValue(void)
{
	/* Not supported by any players at this time */
	return(-1);
}


/* Uninitialize the music players */
void close_music(void)
{
	Mix_HaltMusic();
#ifdef CMD_MUSIC
	Mix_SetMusicCMD(NULL);
#endif
#ifdef MOD_MUSIC
	MOD_exit();
#endif
#ifdef MID_MUSIC
# ifdef USE_TIMIDITY_MIDI
	Timidity_Close();
# endif
#endif

	/* rcg06042009 report available decoders at runtime. */
	free(music_decoders);
	music_decoders = NULL;
	num_decoders = 0;
}

Mix_Music *Mix_LoadMUS_RW(SDL_RWops *rw)
{
	Uint8 magic[5];	  /*Apparently there is no way to check if the file is really a MOD,*/
	/*		    or there are too many formats supported by MikMod or MikMod does */
	/*		    this check by itself. If someone implements other formats (e.g. MP3) */
	/*		    the check can be uncommented */
	Uint8 moremagic[9];
	Mix_Music *music;
	int start;

	if (!rw) {
		Mix_SetError("RWops pointer is NULL");
		return NULL;
	}

	/* Figure out what kind of file this is */
	start = SDL_RWtell(rw);
	if ( SDL_RWread(rw,magic,1,4) != 4 ||
	     SDL_RWread(rw,moremagic,1,8) != 8 ) {
		Mix_SetError("Couldn't read from RWops");
		return NULL;
	}
	SDL_RWseek(rw, start, RW_SEEK_SET);
	magic[4]='\0';
	moremagic[8] = '\0';

	/* Allocate memory for the music structure */
	music=(Mix_Music *)malloc(sizeof(Mix_Music));
	if (music==NULL ) {
		Mix_SetError("Out of memory");
		return(NULL);
	}
	music->error = 0;

#ifdef WAV_MUSIC
	/* WAVE files have the magic four bytes "RIFF"
	   AIFF files have the magic 12 bytes "FORM" XXXX "AIFF"
	 */
	if ( ((strcmp((char *)magic, "RIFF") == 0) && (strcmp((char *)(moremagic+4), "WAVE") == 0)) ||
	     (strcmp((char *)magic, "FORM") == 0) ) {
		music->type = MUS_WAV;
		music->data.wave = WAVStream_LoadSong_RW(rw, (char *)magic);
		if ( music->data.wave == NULL ) {
			music->error = 1;
		}

	} else
#endif
#ifdef OGG_MUSIC
	/* Ogg Vorbis files have the magic four bytes "OggS" */
	if ( strcmp((char *)magic, "OggS") == 0 ) {
		music->type = MUS_OGG;
		music->data.ogg = OGG_new_RW(rw);
		if ( music->data.ogg == NULL ) {
			music->error = 1;
		}
	} else
#endif
#ifdef FLAC_MUSIC
	/* FLAC files have the magic four bytes "fLaC" */
	if ( strcmp((char *)magic, "fLaC") == 0 ) {
		music->type = MUS_FLAC;
		music->data.flac = FLAC_new_RW(rw);
		if ( music->data.flac == NULL ) {
			music->error = 1;
		}
	} else
#endif
#ifdef MP3_MUSIC
	if ( ( magic[0] == 0xFF && (magic[1] & 0xF0) == 0xF0) || ( strncmp((char *)magic, "ID3", 3) == 0 ) ) {
		if ( Mix_Init(MIX_INIT_MP3) ) {
			SMPEG_Info info;
			music->type = MUS_MP3;
			music->data.mp3 = smpeg.SMPEG_new_rwops(rw, &info, 0);
			if ( !info.has_audio ) {
				Mix_SetError("MPEG file does not have any audio stream.");
				music->error = 1;
			} else {
				smpeg.SMPEG_actualSpec(music->data.mp3, &used_mixer);
			}
		} else {
			music->error = 1;
		}
	} else
#endif
#ifdef MP3_MAD_MUSIC
	if ( ( magic[0] == 0xFF && (magic[1] & 0xF0) == 0xF0) || ( strncmp((char *)magic, "ID3", 3) == 0 ) ) {
		music->type = MUS_MP3_MAD;
		music->data.mp3_mad = mad_openFileRW(rw, &used_mixer);
		if (music->data.mp3_mad == 0) {
			Mix_SetError("Could not initialize MPEG stream.");
			music->error = 1;
		}
	} else
#endif
#ifdef MID_MUSIC
	/* MIDI files have the magic four bytes "MThd" */
	if ( strcmp((char *)magic, "MThd") == 0 ) {
		music->type = MUS_MID;
#ifdef USE_NATIVE_MIDI
		if ( native_midi_ok ) {
			music->data.nativemidi = native_midi_loadsong_RW(rw);
	  		if ( music->data.nativemidi == NULL ) {
		  		Mix_SetError("%s", native_midi_error());
			  	music->error = 1;
			}
		} MIDI_ELSE
#endif
#ifdef USE_TIMIDITY_MIDI
		if ( timidity_ok ) {
			music->data.midi = Timidity_LoadSong_RW(rw);
			if ( music->data.midi == NULL ) {
				Mix_SetError("%s", Timidity_Error());
				music->error = 1;
			}
		} else {
			Mix_SetError("%s", Timidity_Error());
			music->error = 1;
		}
#endif
	} else
#endif
#ifdef MOD_MUSIC
	if (1) {
		music->type=MUS_MOD;
		music->data.module = MOD_new_RW(rw);
		if ( music->data.module == NULL ) {
			music->error = 1;
		}
	} else
#endif
	{
		Mix_SetError("Unrecognized music format");
		music->error=1;
	}
	if (music->error) {
		free(music);
		music=NULL;
	}
	return(music);
}
