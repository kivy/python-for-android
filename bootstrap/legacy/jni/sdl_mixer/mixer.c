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

/* $Id: mixer.c 5243 2009-11-14 19:31:39Z slouken $ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "SDL_mutex.h"
#include "SDL_endian.h"
#include "SDL_timer.h"

#include "SDL_mixer.h"
#include "load_aiff.h"
#include "load_voc.h"
#include "load_ogg.h"
#include "load_flac.h"
#include "dynamic_flac.h"
#include "dynamic_mod.h"
#include "dynamic_mp3.h"
#include "dynamic_ogg.h"

#define __MIX_INTERNAL_EFFECT__
#include "effects_internal.h"

/* Magic numbers for various audio file formats */
#define RIFF		0x46464952		/* "RIFF" */
#define WAVE		0x45564157		/* "WAVE" */
#define FORM		0x4d524f46		/* "FORM" */
#define OGGS		0x5367674f		/* "OggS" */
#define CREA		0x61657243		/* "Crea" */
#define FLAC		0x43614C66		/* "fLaC" */

static int audio_opened = 0;
static SDL_AudioSpec mixer;

typedef struct _Mix_effectinfo
{
	Mix_EffectFunc_t callback;
	Mix_EffectDone_t done_callback;
	void *udata;
	struct _Mix_effectinfo *next;
} effect_info;

static struct _Mix_Channel {
	Mix_Chunk *chunk;
	int playing;
	int paused;
	Uint8 *samples;
	int volume;
	int looping;
	int tag;
	Uint32 expire;
	Uint32 start_time;
	Mix_Fading fading;
	int fade_volume;
	int fade_volume_reset;
	Uint32 fade_length;
	Uint32 ticks_fade;
	effect_info *effects;
} *mix_channel = NULL;

static effect_info *posteffects = NULL;

static int num_channels;
static int reserved_channels = 0;


/* Support for hooking into the mixer callback system */
static void (*mix_postmix)(void *udata, Uint8 *stream, int len) = NULL;
static void *mix_postmix_data = NULL;

/* rcg07062001 callback to alert when channels are done playing. */
static void (*channel_done_callback)(int channel) = NULL;

/* Music function declarations */
extern int open_music(SDL_AudioSpec *mixer);
extern void close_music(void);

/* Support for user defined music functions, plus the default one */
extern int volatile music_active;
extern void music_mixer(void *udata, Uint8 *stream, int len);
static void (*mix_music)(void *udata, Uint8 *stream, int len) = music_mixer;
static void *music_data = NULL;

/* rcg06042009 report available decoders at runtime. */
static const char **chunk_decoders = NULL;
static int num_decoders = 0;

int Mix_GetNumChunkDecoders(void)
{
	return(num_decoders);
}

const char *Mix_GetChunkDecoder(int index)
{
	if ((index < 0) || (index >= num_decoders)) {
		return NULL;
	}
	return(chunk_decoders[index]);
}

static void add_chunk_decoder(const char *decoder)
{
	void *ptr = realloc(chunk_decoders, (num_decoders + 1) * sizeof (const char **));
	if (ptr == NULL) {
		return;  /* oh well, go on without it. */
	}
	chunk_decoders = (const char **) ptr;
	chunk_decoders[num_decoders++] = decoder;
}

/* rcg06192001 get linked library's version. */
const SDL_version *Mix_Linked_Version(void)
{
	static SDL_version linked_version;
	SDL_MIXER_VERSION(&linked_version);
	return(&linked_version);
}

static int initialized = 0;

int Mix_Init(int flags)
{
	int result = 0;

	if (flags & MIX_INIT_FLAC) {
#ifdef FLAC_MUSIC
		if ((initialized & MIX_INIT_FLAC) || Mix_InitFLAC() == 0) {
			result |= MIX_INIT_FLAC;
		}
#else
		Mix_SetError("Mixer not built with FLAC support");
#endif
	}
	if (flags & MIX_INIT_MOD) {
#ifdef MOD_MUSIC
		if ((initialized & MIX_INIT_MOD) || Mix_InitMOD() == 0) {
			result |= MIX_INIT_MOD;
		}
#else
		Mix_SetError("Mixer not built with MOD support");
#endif
	}
	if (flags & MIX_INIT_MP3) {
#ifdef MP3_MUSIC
		if ((initialized & MIX_INIT_MP3) || Mix_InitMP3() == 0) {
			result |= MIX_INIT_MP3;
		}
#else
		Mix_SetError("Mixer not built with MP3 support");
#endif
	}
	if (flags & MIX_INIT_OGG) {
#ifdef OGG_MUSIC
		if ((initialized & MIX_INIT_OGG) || Mix_InitOgg() == 0) {
			result |= MIX_INIT_OGG;
		}
#else
		Mix_SetError("Mixer not built with Ogg Vorbis support");
#endif
	}
	initialized |= result;

	return (result);
}

void Mix_Quit()
{
#ifdef FLAC_MUSIC
	if (initialized & MIX_INIT_FLAC) {
		Mix_QuitFLAC();
	}
#endif
#ifdef MOD_MUSIC
	if (initialized & MIX_INIT_MOD) {
		Mix_QuitMOD();
	}
#endif
#ifdef MP3_MUSIC
	if (initialized & MIX_INIT_MP3) {
		Mix_QuitMP3();
	}
#endif
#ifdef OGG_MUSIC
	if (initialized & MIX_INIT_OGG) {
		Mix_QuitOgg();
	}
#endif
	initialized = 0;
}

static int _Mix_remove_all_effects(int channel, effect_info **e);

/*
 * rcg06122001 Cleanup effect callbacks.
 *  MAKE SURE SDL_LockAudio() is called before this (or you're in the
 *   audio callback).
 */
static void _Mix_channel_done_playing(int channel)
{
	if (channel_done_callback) {
	    channel_done_callback(channel);
	}

	/*
	 * Call internal function directly, to avoid locking audio from
	 *   inside audio callback.
	 */
	_Mix_remove_all_effects(channel, &mix_channel[channel].effects);
}


static void *Mix_DoEffects(int chan, void *snd, int len)
{
	int posteffect = (chan == MIX_CHANNEL_POST);
	effect_info *e = ((posteffect) ? posteffects : mix_channel[chan].effects);
	void *buf = snd;

	if (e != NULL) {    /* are there any registered effects? */
		/* if this is the postmix, we can just overwrite the original. */
		if (!posteffect) {
			buf = malloc(len);
			if (buf == NULL) {
				return(snd);
			}
		    memcpy(buf, snd, len);
		}

		for (; e != NULL; e = e->next) {
			if (e->callback != NULL) {
				e->callback(chan, buf, len, e->udata);
			}
		}
	}

	/* be sure to free() the return value if != snd ... */
	return(buf);
}


/* Mixing function */
static void mix_channels(void *udata, Uint8 *stream, int len)
{
	Uint8 *mix_input;
	int i, mixable, volume = SDL_MIX_MAXVOLUME;
	Uint32 sdl_ticks;

#if SDL_VERSION_ATLEAST(1, 3, 0)
	/* Need to initialize the stream in SDL 1.3+ */
	memset(stream, mixer.silence, len);
#endif

	/* Mix the music (must be done before the channels are added) */
	if ( music_active || (mix_music != music_mixer) ) {
		mix_music(music_data, stream, len);
	}

	/* Mix any playing channels... */
	sdl_ticks = SDL_GetTicks();
	for ( i=0; i<num_channels; ++i ) {
		if( ! mix_channel[i].paused ) {
			if ( mix_channel[i].expire > 0 && mix_channel[i].expire < sdl_ticks ) {
				/* Expiration delay for that channel is reached */
				mix_channel[i].playing = 0;
				mix_channel[i].fading = MIX_NO_FADING;
				mix_channel[i].expire = 0;
				_Mix_channel_done_playing(i);
			} else if ( mix_channel[i].fading != MIX_NO_FADING ) {
				Uint32 ticks = sdl_ticks - mix_channel[i].ticks_fade;
				if( ticks > mix_channel[i].fade_length ) {
				    Mix_Volume(i, mix_channel[i].fade_volume_reset); /* Restore the volume */
					if( mix_channel[i].fading == MIX_FADING_OUT ) {
						mix_channel[i].playing = 0;
						mix_channel[i].expire = 0;
						_Mix_channel_done_playing(i);
					}
					mix_channel[i].fading = MIX_NO_FADING;
				} else {
					if( mix_channel[i].fading == MIX_FADING_OUT ) {
						Mix_Volume(i, (mix_channel[i].fade_volume * (mix_channel[i].fade_length-ticks))
								   / mix_channel[i].fade_length );
					} else {
						Mix_Volume(i, (mix_channel[i].fade_volume * ticks) / mix_channel[i].fade_length );
					}
				}
			}
			if ( mix_channel[i].playing > 0 ) {
				int index = 0;
				int remaining = len;
				while (mix_channel[i].playing > 0 && index < len) {
					remaining = len - index;
					volume = (mix_channel[i].volume*mix_channel[i].chunk->volume) / MIX_MAX_VOLUME;
					mixable = mix_channel[i].playing;
					if ( mixable > remaining ) {
						mixable = remaining;
					}

					mix_input = Mix_DoEffects(i, mix_channel[i].samples, mixable);
					SDL_MixAudio(stream+index,mix_input,mixable,volume);
					if (mix_input != mix_channel[i].samples)
						free(mix_input);

					mix_channel[i].samples += mixable;
					mix_channel[i].playing -= mixable;
					index += mixable;

					/* rcg06072001 Alert app if channel is done playing. */
					if (!mix_channel[i].playing && !mix_channel[i].looping) {
						_Mix_channel_done_playing(i);
					}
				}

				/* If looping the sample and we are at its end, make sure
				   we will still return a full buffer */
				while ( mix_channel[i].looping && index < len ) {
					int alen = mix_channel[i].chunk->alen;
					remaining = len - index;
					if (remaining > alen) {
						remaining = alen;
					}

					mix_input = Mix_DoEffects(i, mix_channel[i].chunk->abuf, remaining);
					SDL_MixAudio(stream+index, mix_input, remaining, volume);
					if (mix_input != mix_channel[i].chunk->abuf)
						free(mix_input);

					--mix_channel[i].looping;
					mix_channel[i].samples = mix_channel[i].chunk->abuf + remaining;
					mix_channel[i].playing = mix_channel[i].chunk->alen - remaining;
					index += remaining;
				}
				if ( ! mix_channel[i].playing && mix_channel[i].looping ) {
					--mix_channel[i].looping;
					mix_channel[i].samples = mix_channel[i].chunk->abuf;
					mix_channel[i].playing = mix_channel[i].chunk->alen;
				}
			}
		}
	}

	/* rcg06122001 run posteffects... */
	Mix_DoEffects(MIX_CHANNEL_POST, stream, len);

	if ( mix_postmix ) {
		mix_postmix(mix_postmix_data, stream, len);
	}
}

#if 0
static void PrintFormat(char *title, SDL_AudioSpec *fmt)
{
	printf("%s: %d bit %s audio (%s) at %u Hz\n", title, (fmt->format&0xFF),
			(fmt->format&0x8000) ? "signed" : "unsigned",
			(fmt->channels > 2) ? "surround" :
			(fmt->channels > 1) ? "stereo" : "mono", fmt->freq);
}
#endif


/* Open the mixer with a certain desired audio format */
int Mix_OpenAudio(int frequency, Uint16 format, int nchannels, int chunksize)
{
	int i;
	SDL_AudioSpec desired;

	/* If the mixer is already opened, increment open count */
	if ( audio_opened ) {
		if ( format == mixer.format && nchannels == mixer.channels ) {
	    	++audio_opened;
	    	return(0);
		}
		while ( audio_opened ) {
			Mix_CloseAudio();
		}
	}

	/* Set the desired format and frequency */
	desired.freq = frequency;
	desired.format = format;
	desired.channels = nchannels;
	desired.samples = chunksize;
	desired.callback = mix_channels;
	desired.userdata = NULL;

	/* Accept nearly any audio format */
	if ( SDL_OpenAudio(&desired, &mixer) < 0 ) {
		return(-1);
	}
#if 0
	PrintFormat("Audio device", &mixer);
#endif

	/* Initialize the music players */
	if ( open_music(&mixer) < 0 ) {
		SDL_CloseAudio();
		return(-1);
	}

	num_channels = MIX_CHANNELS;
	mix_channel = (struct _Mix_Channel *) malloc(num_channels * sizeof(struct _Mix_Channel));

	/* Clear out the audio channels */
	for ( i=0; i<num_channels; ++i ) {
		mix_channel[i].chunk = NULL;
		mix_channel[i].playing = 0;
		mix_channel[i].looping = 0;
		mix_channel[i].volume = SDL_MIX_MAXVOLUME;
		mix_channel[i].fade_volume = SDL_MIX_MAXVOLUME;
		mix_channel[i].fade_volume_reset = SDL_MIX_MAXVOLUME;
		mix_channel[i].fading = MIX_NO_FADING;
		mix_channel[i].tag = -1;
		mix_channel[i].expire = 0;
		mix_channel[i].effects = NULL;
		mix_channel[i].paused = 0;
	}
	Mix_VolumeMusic(SDL_MIX_MAXVOLUME);

	_Mix_InitEffects();

	/* This list is (currently) decided at build time. */
	add_chunk_decoder("WAVE");
	add_chunk_decoder("AIFF");
	add_chunk_decoder("VOC");
#ifdef OGG_MUSIC
	add_chunk_decoder("OGG");
#endif
#ifdef FLAC_MUSIC
	add_chunk_decoder("FLAC");
#endif

	audio_opened = 1;
	SDL_PauseAudio(0);
	return(0);
}

/* Dynamically change the number of channels managed by the mixer.
   If decreasing the number of channels, the upper channels are
   stopped.
 */
int Mix_AllocateChannels(int numchans)
{
	if ( numchans<0 || numchans==num_channels )
		return(num_channels);

	if ( numchans < num_channels ) {
		/* Stop the affected channels */
		int i;
		for(i=numchans; i < num_channels; i++) {
			Mix_UnregisterAllEffects(i);
			Mix_HaltChannel(i);
		}
	}
	SDL_LockAudio();
	mix_channel = (struct _Mix_Channel *) realloc(mix_channel, numchans * sizeof(struct _Mix_Channel));
	if ( numchans > num_channels ) {
		/* Initialize the new channels */
		int i;
		for(i=num_channels; i < numchans; i++) {
			mix_channel[i].chunk = NULL;
			mix_channel[i].playing = 0;
			mix_channel[i].looping = 0;
			mix_channel[i].volume = SDL_MIX_MAXVOLUME;
			mix_channel[i].fade_volume = SDL_MIX_MAXVOLUME;
			mix_channel[i].fade_volume_reset = SDL_MIX_MAXVOLUME;
			mix_channel[i].fading = MIX_NO_FADING;
			mix_channel[i].tag = -1;
			mix_channel[i].expire = 0;
			mix_channel[i].effects = NULL;
			mix_channel[i].paused = 0;
		}
	}
	num_channels = numchans;
	SDL_UnlockAudio();
	return(num_channels);
}

/* Return the actual mixer parameters */
int Mix_QuerySpec(int *frequency, Uint16 *format, int *channels)
{
	if ( audio_opened ) {
		if ( frequency ) {
			*frequency = mixer.freq;
		}
		if ( format ) {
			*format = mixer.format;
		}
		if ( channels ) {
			*channels = mixer.channels;
		}
	}
	return(audio_opened);
}


/*
 * !!! FIXME: Ideally, we want a Mix_LoadSample_RW(), which will handle the
 *             generic setup, then call the correct file format loader.
 */

/* Load a wave file */
Mix_Chunk *Mix_LoadWAV_RW(SDL_RWops *src, int freesrc)
{
	Uint32 magic;
	Mix_Chunk *chunk;
	SDL_AudioSpec wavespec, *loaded;
	SDL_AudioCVT wavecvt;
	int samplesize;

	/* rcg06012001 Make sure src is valid */
	if ( ! src ) {
		SDL_SetError("Mix_LoadWAV_RW with NULL src");
		return(NULL);
	}

	/* Make sure audio has been opened */
	if ( ! audio_opened ) {
		SDL_SetError("Audio device hasn't been opened");
		if ( freesrc && src ) {
			SDL_RWclose(src);
		}
		return(NULL);
	}

	/* Allocate the chunk memory */
	chunk = (Mix_Chunk *)malloc(sizeof(Mix_Chunk));
	if ( chunk == NULL ) {
		SDL_SetError("Out of memory");
		if ( freesrc ) {
			SDL_RWclose(src);
		}
		return(NULL);
	}

	/* Find out what kind of audio file this is */
	magic = SDL_ReadLE32(src);
	/* Seek backwards for compatibility with older loaders */
	SDL_RWseek(src, -(int)sizeof(Uint32), RW_SEEK_CUR);

	switch (magic) {
		case WAVE:
		case RIFF:
			loaded = SDL_LoadWAV_RW(src, freesrc, &wavespec,
					(Uint8 **)&chunk->abuf, &chunk->alen);
			break;
		case FORM:
			loaded = Mix_LoadAIFF_RW(src, freesrc, &wavespec,
					(Uint8 **)&chunk->abuf, &chunk->alen);
			break;
#ifdef OGG_MUSIC
		case OGGS:
			loaded = Mix_LoadOGG_RW(src, freesrc, &wavespec,
					(Uint8 **)&chunk->abuf, &chunk->alen);
			break;
#endif
#ifdef FLAC_MUSIC
		case FLAC:
			loaded = Mix_LoadFLAC_RW(src, freesrc, &wavespec,
					(Uint8 **)&chunk->abuf, &chunk->alen);
			break;
#endif
		case CREA:
			loaded = Mix_LoadVOC_RW(src, freesrc, &wavespec,
					(Uint8 **)&chunk->abuf, &chunk->alen);
			break;
		default:
			SDL_SetError("Unrecognized sound file type");
			return(0);			
	}
	if ( !loaded ) {
		free(chunk);
		return(NULL);
	}

#if 0
	PrintFormat("Audio device", &mixer);
	PrintFormat("-- Wave file", &wavespec);
#endif

	/* Build the audio converter and create conversion buffers */
	if ( SDL_BuildAudioCVT(&wavecvt,
			wavespec.format, wavespec.channels, wavespec.freq,
			mixer.format, mixer.channels, mixer.freq) < 0 ) {
		SDL_FreeWAV(chunk->abuf);
		free(chunk);
		return(NULL);
	}
	samplesize = ((wavespec.format & 0xFF)/8)*wavespec.channels;
	wavecvt.len = chunk->alen & ~(samplesize-1);
	wavecvt.buf = (Uint8 *)malloc(wavecvt.len*wavecvt.len_mult);
	if ( wavecvt.buf == NULL ) {
		SDL_SetError("Out of memory");
		SDL_FreeWAV(chunk->abuf);
		free(chunk);
		return(NULL);
	}
	memcpy(wavecvt.buf, chunk->abuf, chunk->alen);
	SDL_FreeWAV(chunk->abuf);

	/* Run the audio converter */
	if ( SDL_ConvertAudio(&wavecvt) < 0 ) {
		free(wavecvt.buf);
		free(chunk);
		return(NULL);
	}
	chunk->allocated = 1;
	chunk->abuf = wavecvt.buf;
	chunk->alen = wavecvt.len_cvt;
	chunk->volume = MIX_MAX_VOLUME;
	return(chunk);
}

/* Load a wave file of the mixer format from a memory buffer */
Mix_Chunk *Mix_QuickLoad_WAV(Uint8 *mem)
{
	Mix_Chunk *chunk;
	Uint8 magic[4];

	/* Make sure audio has been opened */
	if ( ! audio_opened ) {
		SDL_SetError("Audio device hasn't been opened");
		return(NULL);
	}

	/* Allocate the chunk memory */
	chunk = (Mix_Chunk *)calloc(1,sizeof(Mix_Chunk));
	if ( chunk == NULL ) {
		SDL_SetError("Out of memory");
		return(NULL);
	}

	/* Essentially just skip to the audio data (no error checking - fast) */
	chunk->allocated = 0;
	mem += 12; /* WAV header */
	do {
		memcpy(magic, mem, 4);
		mem += 4;
		chunk->alen = ((mem[3]<<24)|(mem[2]<<16)|(mem[1]<<8)|(mem[0]));
		mem += 4;
		chunk->abuf = mem;
		mem += chunk->alen;
	} while ( memcmp(magic, "data", 4) != 0 );
	chunk->volume = MIX_MAX_VOLUME;

	return(chunk);
}

/* Load raw audio data of the mixer format from a memory buffer */
Mix_Chunk *Mix_QuickLoad_RAW(Uint8 *mem, Uint32 len)
{
	Mix_Chunk *chunk;

	/* Make sure audio has been opened */
	if ( ! audio_opened ) {
		SDL_SetError("Audio device hasn't been opened");
		return(NULL);
	}

	/* Allocate the chunk memory */
	chunk = (Mix_Chunk *)malloc(sizeof(Mix_Chunk));
	if ( chunk == NULL ) {
		SDL_SetError("Out of memory");
		return(NULL);
	}

	/* Essentially just point at the audio data (no error checking - fast) */
	chunk->allocated = 0;
	chunk->alen = len;
	chunk->abuf = mem;
	chunk->volume = MIX_MAX_VOLUME;

	return(chunk);
}

/* Free an audio chunk previously loaded */
void Mix_FreeChunk(Mix_Chunk *chunk)
{
	int i;

	/* Caution -- if the chunk is playing, the mixer will crash */
	if ( chunk ) {
		/* Guarantee that this chunk isn't playing */
		SDL_LockAudio();
		if ( mix_channel ) {
			for ( i=0; i<num_channels; ++i ) {
				if ( chunk == mix_channel[i].chunk ) {
					mix_channel[i].playing = 0;
				}
			}
		}
		SDL_UnlockAudio();
		/* Actually free the chunk */
		if ( chunk->allocated ) {
			free(chunk->abuf);
		}
		free(chunk);
	}
}

/* Set a function that is called after all mixing is performed.
   This can be used to provide real-time visual display of the audio stream
   or add a custom mixer filter for the stream data.
*/
void Mix_SetPostMix(void (*mix_func)
                    (void *udata, Uint8 *stream, int len), void *arg)
{
	SDL_LockAudio();
	mix_postmix_data = arg;
	mix_postmix = mix_func;
	SDL_UnlockAudio();
}

/* Add your own music player or mixer function.
   If 'mix_func' is NULL, the default music player is re-enabled.
 */
void Mix_HookMusic(void (*mix_func)(void *udata, Uint8 *stream, int len),
                                                                void *arg)
{
	SDL_LockAudio();
	if ( mix_func != NULL ) {
		music_data = arg;
		mix_music = mix_func;
	} else {
		music_data = NULL;
		mix_music = music_mixer;
	}
	SDL_UnlockAudio();
}

void *Mix_GetMusicHookData(void)
{
	return(music_data);
}

void Mix_ChannelFinished(void (*channel_finished)(int channel))
{
	SDL_LockAudio();
	channel_done_callback = channel_finished;
	SDL_UnlockAudio();
}


/* Reserve the first channels (0 -> n-1) for the application, i.e. don't allocate
   them dynamically to the next sample if requested with a -1 value below.
   Returns the number of reserved channels.
 */
int Mix_ReserveChannels(int num)
{
	if (num > num_channels)
		num = num_channels;
	reserved_channels = num;
	return num;
}

static int checkchunkintegral(Mix_Chunk *chunk)
{
	int frame_width = 1;

	if ((mixer.format & 0xFF) == 16) frame_width = 2;
	frame_width *= mixer.channels;
	while (chunk->alen % frame_width) chunk->alen--;
	return chunk->alen;
}

/* Play an audio chunk on a specific channel.
   If the specified channel is -1, play on the first free channel.
   'ticks' is the number of milliseconds at most to play the sample, or -1
   if there is no limit.
   Returns which channel was used to play the sound.
*/
int Mix_PlayChannelTimed(int which, Mix_Chunk *chunk, int loops, int ticks)
{
	int i;

	/* Don't play null pointers :-) */
	if ( chunk == NULL ) {
		Mix_SetError("Tried to play a NULL chunk");
		return(-1);
	}
	if ( !checkchunkintegral(chunk)) {
		Mix_SetError("Tried to play a chunk with a bad frame");
		return(-1);
	}

	/* Lock the mixer while modifying the playing channels */
	SDL_LockAudio();
	{
		/* If which is -1, play on the first free channel */
		if ( which == -1 ) {
			for ( i=reserved_channels; i<num_channels; ++i ) {
				if ( mix_channel[i].playing <= 0 )
					break;
			}
			if ( i == num_channels ) {
				Mix_SetError("No free channels available");
				which = -1;
			} else {
				which = i;
			}
		}

		/* Queue up the audio data for this channel */
		if ( which >= 0 ) {
			Uint32 sdl_ticks = SDL_GetTicks();
			if (Mix_Playing(which))
				_Mix_channel_done_playing(which);
			mix_channel[which].samples = chunk->abuf;
			mix_channel[which].playing = chunk->alen;
			mix_channel[which].looping = loops;
			mix_channel[which].chunk = chunk;
			mix_channel[which].paused = 0;
			mix_channel[which].fading = MIX_NO_FADING;
			mix_channel[which].start_time = sdl_ticks;
			mix_channel[which].expire = (ticks>0) ? (sdl_ticks + ticks) : 0;
		}
	}
	SDL_UnlockAudio();

	/* Return the channel on which the sound is being played */
	return(which);
}

/* Change the expiration delay for a channel */
int Mix_ExpireChannel(int which, int ticks)
{
	int status = 0;

	if ( which == -1 ) {
		int i;
		for ( i=0; i < num_channels; ++ i ) {
			status += Mix_ExpireChannel(i, ticks);
		}
	} else if ( which < num_channels ) {
		SDL_LockAudio();
		mix_channel[which].expire = (ticks>0) ? (SDL_GetTicks() + ticks) : 0;
		SDL_UnlockAudio();
		++ status;
	}
	return(status);
}

/* Fade in a sound on a channel, over ms milliseconds */
int Mix_FadeInChannelTimed(int which, Mix_Chunk *chunk, int loops, int ms, int ticks)
{
	int i;

	/* Don't play null pointers :-) */
	if ( chunk == NULL ) {
		return(-1);
	}
	if ( !checkchunkintegral(chunk)) {
		Mix_SetError("Tried to play a chunk with a bad frame");
		return(-1);
	}

	/* Lock the mixer while modifying the playing channels */
	SDL_LockAudio();
	{
		/* If which is -1, play on the first free channel */
		if ( which == -1 ) {
			for ( i=reserved_channels; i<num_channels; ++i ) {
				if ( mix_channel[i].playing <= 0 )
					break;
			}
			if ( i == num_channels ) {
				which = -1;
			} else {
				which = i;
			}
		}

		/* Queue up the audio data for this channel */
		if ( which >= 0 ) {
			Uint32 sdl_ticks = SDL_GetTicks();
			if (Mix_Playing(which))
				_Mix_channel_done_playing(which);
			mix_channel[which].samples = chunk->abuf;
			mix_channel[which].playing = chunk->alen;
			mix_channel[which].looping = loops;
			mix_channel[which].chunk = chunk;
			mix_channel[which].paused = 0;
			mix_channel[which].fading = MIX_FADING_IN;
			mix_channel[which].fade_volume = mix_channel[which].volume;
			mix_channel[which].fade_volume_reset = mix_channel[which].volume;
			mix_channel[which].volume = 0;
			mix_channel[which].fade_length = (Uint32)ms;
			mix_channel[which].start_time = mix_channel[which].ticks_fade = sdl_ticks;
			mix_channel[which].expire = (ticks > 0) ? (sdl_ticks+ticks) : 0;
		}
	}
	SDL_UnlockAudio();

	/* Return the channel on which the sound is being played */
	return(which);
}

/* Set volume of a particular channel */
int Mix_Volume(int which, int volume)
{
	int i;
	int prev_volume;

	if ( which == -1 ) {
		prev_volume = 0;
		for ( i=0; i<num_channels; ++i ) {
			prev_volume += Mix_Volume(i, volume);
		}
		prev_volume /= num_channels;
	} else {
		prev_volume = mix_channel[which].volume;
		if ( volume >= 0 ) {
			if ( volume > SDL_MIX_MAXVOLUME ) {
				volume = SDL_MIX_MAXVOLUME;
			}
			mix_channel[which].volume = volume;
		}
	}
	return(prev_volume);
}
/* Set volume of a particular chunk */
int Mix_VolumeChunk(Mix_Chunk *chunk, int volume)
{
	int prev_volume;

	prev_volume = chunk->volume;
	if ( volume >= 0 ) {
		if ( volume > MIX_MAX_VOLUME ) {
			volume = MIX_MAX_VOLUME;
		}
		chunk->volume = volume;
	}
	return(prev_volume);
}

/* Halt playing of a particular channel */
int Mix_HaltChannel(int which)
{
	int i;

	if ( which == -1 ) {
		for ( i=0; i<num_channels; ++i ) {
			Mix_HaltChannel(i);
		}
	} else {
		SDL_LockAudio();
		if (mix_channel[which].playing) {
			_Mix_channel_done_playing(which);
		mix_channel[which].playing = 0;
		}
		mix_channel[which].expire = 0;
		if(mix_channel[which].fading != MIX_NO_FADING) /* Restore volume */
			mix_channel[which].volume = mix_channel[which].fade_volume_reset;
		mix_channel[which].fading = MIX_NO_FADING;
		SDL_UnlockAudio();
	}
	return(0);
}

/* Halt playing of a particular group of channels */
int Mix_HaltGroup(int tag)
{
	int i;

	for ( i=0; i<num_channels; ++i ) {
		if( mix_channel[i].tag == tag ) {
			Mix_HaltChannel(i);
		}
	}
	return(0);
}

/* Fade out a channel and then stop it automatically */
int Mix_FadeOutChannel(int which, int ms)
{
	int status;

	status = 0;
	if ( audio_opened ) {
		if ( which == -1 ) {
			int i;

			for ( i=0; i<num_channels; ++i ) {
				status += Mix_FadeOutChannel(i, ms);
			}
		} else {
			SDL_LockAudio();
			if ( mix_channel[which].playing && 
			    (mix_channel[which].volume > 0) &&
			    (mix_channel[which].fading != MIX_FADING_OUT) ) {
				mix_channel[which].fade_volume = mix_channel[which].volume;
				mix_channel[which].fading = MIX_FADING_OUT;
				mix_channel[which].fade_length = ms;
				mix_channel[which].ticks_fade = SDL_GetTicks();

				/* only change fade_volume_reset if we're not fading. */
				if (mix_channel[which].fading == MIX_NO_FADING) {
				    mix_channel[which].fade_volume_reset = mix_channel[which].volume;
				}
				++status;
			}
			SDL_UnlockAudio();
		}
	}
	return(status);
}

/* Halt playing of a particular group of channels */
int Mix_FadeOutGroup(int tag, int ms)
{
	int i;
	int status = 0;
	for ( i=0; i<num_channels; ++i ) {
		if( mix_channel[i].tag == tag ) {
			status += Mix_FadeOutChannel(i,ms);
		}
	}
	return(status);
}

Mix_Fading Mix_FadingChannel(int which)
{
	return mix_channel[which].fading;
}

/* Check the status of a specific channel.
   If the specified mix_channel is -1, check all mix channels.
*/
int Mix_Playing(int which)
{
	int status;

	status = 0;
	if ( which == -1 ) {
		int i;

		for ( i=0; i<num_channels; ++i ) {
			if ((mix_channel[i].playing > 0) ||
				(mix_channel[i].looping > 0))
			{
				++status;
			}
		}
	} else {
		if ((mix_channel[which].playing > 0) ||
			(mix_channel[which].looping > 0))
		{
			++status;
		}
	}
	return(status);
}

/* rcg06072001 Get the chunk associated with a channel. */
Mix_Chunk *Mix_GetChunk(int channel)
{
	Mix_Chunk *retval = NULL;

	if ((channel >= 0) && (channel < num_channels)) {
		retval = mix_channel[channel].chunk;
	}

	return(retval);
}

/* Close the mixer, halting all playing audio */
void Mix_CloseAudio(void)
{
	int i;

	if ( audio_opened ) {
		if ( audio_opened == 1 ) {
			for (i = 0; i < num_channels; i++) {
				Mix_UnregisterAllEffects(i);
			}
			Mix_UnregisterAllEffects(MIX_CHANNEL_POST);
			close_music();
			Mix_HaltChannel(-1);
			_Mix_DeinitEffects();
			SDL_CloseAudio();
			free(mix_channel);
			mix_channel = NULL;

			/* rcg06042009 report available decoders at runtime. */
			free(chunk_decoders);
			chunk_decoders = NULL;
			num_decoders = 0;
		}
		--audio_opened;
	}
}

/* Pause a particular channel (or all) */
void Mix_Pause(int which)
{
	Uint32 sdl_ticks = SDL_GetTicks();
	if ( which == -1 ) {
		int i;

		for ( i=0; i<num_channels; ++i ) {
			if ( mix_channel[i].playing > 0 ) {
				mix_channel[i].paused = sdl_ticks;
			}
		}
	} else {
		if ( mix_channel[which].playing > 0 ) {
			mix_channel[which].paused = sdl_ticks;
		}
	}
}

/* Resume a paused channel */
void Mix_Resume(int which)
{
	Uint32 sdl_ticks = SDL_GetTicks();

	SDL_LockAudio();
	if ( which == -1 ) {
		int i;

		for ( i=0; i<num_channels; ++i ) {
			if ( mix_channel[i].playing > 0 ) {
				if(mix_channel[i].expire > 0)
					mix_channel[i].expire += sdl_ticks - mix_channel[i].paused;
				mix_channel[i].paused = 0;
			}
		}
	} else {
		if ( mix_channel[which].playing > 0 ) {
			if(mix_channel[which].expire > 0)
				mix_channel[which].expire += sdl_ticks - mix_channel[which].paused;
			mix_channel[which].paused = 0;
		}
	}
	SDL_UnlockAudio();
}

int Mix_Paused(int which)
{
	if ( which > num_channels )
		return(0);
	if ( which < 0 ) {
		int status = 0;
		int i;
		for( i=0; i < num_channels; ++i ) {
			if ( mix_channel[i].paused ) {
				++ status;
			}
		}
		return(status);
	} else {
		return(mix_channel[which].paused != 0);
	}
}

/* Change the group of a channel */
int Mix_GroupChannel(int which, int tag)
{
	if ( which < 0 || which > num_channels )
		return(0);

	SDL_LockAudio();
	mix_channel[which].tag = tag;
	SDL_UnlockAudio();
	return(1);
}

/* Assign several consecutive channels to a group */
int Mix_GroupChannels(int from, int to, int tag)
{
	int status = 0;
	for( ; from <= to; ++ from ) {
		status += Mix_GroupChannel(from, tag);
	}
	return(status);
}

/* Finds the first available channel in a group of channels */
int Mix_GroupAvailable(int tag)
{
	int i;
	for( i=0; i < num_channels; i ++ ) {
		if ( ((tag == -1) || (tag == mix_channel[i].tag)) &&
		                    (mix_channel[i].playing <= 0) )
			return i;
	}
	return(-1);
}

int Mix_GroupCount(int tag)
{
	int count = 0;
	int i;
	for( i=0; i < num_channels; i ++ ) {
		if ( mix_channel[i].tag==tag || tag==-1 )
			++ count;
	}
	return(count);
}

/* Finds the "oldest" sample playing in a group of channels */
int Mix_GroupOldest(int tag)
{
	int chan = -1;
	Uint32 mintime = SDL_GetTicks();
	int i;
	for( i=0; i < num_channels; i ++ ) {
		if ( (mix_channel[i].tag==tag || tag==-1) && mix_channel[i].playing > 0
			 && mix_channel[i].start_time <= mintime ) {
			mintime = mix_channel[i].start_time;
			chan = i;
		}
	}
	return(chan);
}

/* Finds the "most recent" (i.e. last) sample playing in a group of channels */
int Mix_GroupNewer(int tag)
{
	int chan = -1;
	Uint32 maxtime = 0;
	int i;
	for( i=0; i < num_channels; i ++ ) {
		if ( (mix_channel[i].tag==tag || tag==-1) && mix_channel[i].playing > 0
			 && mix_channel[i].start_time >= maxtime ) {
			maxtime = mix_channel[i].start_time;
			chan = i;
		}
	}
	return(chan);
}



/*
 * rcg06122001 The special effects exportable API.
 *  Please see effect_*.c for internally-implemented effects, such
 *  as Mix_SetPanning().
 */

/* MAKE SURE you hold the audio lock (SDL_LockAudio()) before calling this! */
static int _Mix_register_effect(effect_info **e, Mix_EffectFunc_t f,
				Mix_EffectDone_t d, void *arg)
{
	effect_info *new_e = malloc(sizeof (effect_info));

	if (!e) {
		Mix_SetError("Internal error");
		return(0);
	}

	if (f == NULL) {
		Mix_SetError("NULL effect callback");
		return(0);
	}

	if (new_e == NULL) {
		Mix_SetError("Out of memory");
		return(0);
	}

	new_e->callback = f;
	new_e->done_callback = d;
	new_e->udata = arg;
	new_e->next = NULL;

	/* add new effect to end of linked list... */
	if (*e == NULL) {
		*e = new_e;
	} else {
		effect_info *cur = *e;
		while (1) {
			if (cur->next == NULL) {
				cur->next = new_e;
				break;
			}
			cur = cur->next;
		}
	}

	return(1);
}


/* MAKE SURE you hold the audio lock (SDL_LockAudio()) before calling this! */
static int _Mix_remove_effect(int channel, effect_info **e, Mix_EffectFunc_t f)
{
	effect_info *cur;
	effect_info *prev = NULL;
	effect_info *next = NULL;

	if (!e) {
		Mix_SetError("Internal error");
		return(0);
	}

	for (cur = *e; cur != NULL; cur = cur->next) {
		if (cur->callback == f) {
			next = cur->next;
			if (cur->done_callback != NULL) {
				cur->done_callback(channel, cur->udata);
			}
			free(cur);

			if (prev == NULL) {   /* removing first item of list? */
				*e = next;
			} else {
				prev->next = next;
			}
			return(1);
		}
		prev = cur;
	}

	Mix_SetError("No such effect registered");
	return(0);
}


/* MAKE SURE you hold the audio lock (SDL_LockAudio()) before calling this! */
static int _Mix_remove_all_effects(int channel, effect_info **e)
{
	effect_info *cur;
	effect_info *next;

	if (!e) {
		Mix_SetError("Internal error");
		return(0);
	}

	for (cur = *e; cur != NULL; cur = next) {
		next = cur->next;
		if (cur->done_callback != NULL) {
			cur->done_callback(channel, cur->udata);
		}
		free(cur);
	}
	*e = NULL;

	return(1);
}


/* MAKE SURE you hold the audio lock (SDL_LockAudio()) before calling this! */
int _Mix_RegisterEffect_locked(int channel, Mix_EffectFunc_t f,
			Mix_EffectDone_t d, void *arg)
{
	effect_info **e = NULL;

	if (channel == MIX_CHANNEL_POST) {
		e = &posteffects;
	} else {
		if ((channel < 0) || (channel >= num_channels)) {
			Mix_SetError("Invalid channel number");
			return(0);
		}
		e = &mix_channel[channel].effects;
	}

	return _Mix_register_effect(e, f, d, arg);
}

int Mix_RegisterEffect(int channel, Mix_EffectFunc_t f,
			Mix_EffectDone_t d, void *arg)
{
    int retval;
	SDL_LockAudio();
	retval = _Mix_RegisterEffect_locked(channel, f, d, arg);
	SDL_UnlockAudio();
    return retval;
}


/* MAKE SURE you hold the audio lock (SDL_LockAudio()) before calling this! */
int _Mix_UnregisterEffect_locked(int channel, Mix_EffectFunc_t f)
{
	effect_info **e = NULL;

	if (channel == MIX_CHANNEL_POST) {
		e = &posteffects;
	} else {
		if ((channel < 0) || (channel >= num_channels)) {
			Mix_SetError("Invalid channel number");
			return(0);
		}
		e = &mix_channel[channel].effects;
	}

	return _Mix_remove_effect(channel, e, f);
}

int Mix_UnregisterEffect(int channel, Mix_EffectFunc_t f)
{
	int retval;
	SDL_LockAudio();
	retval = _Mix_UnregisterEffect_locked(channel, f);
	SDL_UnlockAudio();
	return(retval);
}

/* MAKE SURE you hold the audio lock (SDL_LockAudio()) before calling this! */
int _Mix_UnregisterAllEffects_locked(int channel)
{
	effect_info **e = NULL;

	if (channel == MIX_CHANNEL_POST) {
		e = &posteffects;
	} else {
		if ((channel < 0) || (channel >= num_channels)) {
			Mix_SetError("Invalid channel number");
			return(0);
		}
		e = &mix_channel[channel].effects;
	}

	return _Mix_remove_all_effects(channel, e);
}

int Mix_UnregisterAllEffects(int channel)
{
	int retval;
	SDL_LockAudio();
	retval = _Mix_UnregisterAllEffects_locked(channel);
	SDL_UnlockAudio();
	return(retval);
}

/* end of mixer.c ... */

