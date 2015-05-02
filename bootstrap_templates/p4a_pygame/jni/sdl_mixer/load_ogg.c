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

    This is the source needed to decode an Ogg Vorbis into a waveform.
    This file by Vaclav Slavik (vaclav.slavik@matfyz.cz).
*/

/* $Id: load_ogg.c 5214 2009-11-08 17:11:09Z slouken $ */

#ifdef OGG_MUSIC

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "SDL_mutex.h"
#include "SDL_endian.h"
#include "SDL_timer.h"

#include "SDL_mixer.h"
#include "dynamic_ogg.h"
#include "load_ogg.h"

static size_t sdl_read_func(void *ptr, size_t size, size_t nmemb, void *datasource)
{
    return SDL_RWread((SDL_RWops*)datasource, ptr, size, nmemb);
}

static int sdl_seek_func(void *datasource, ogg_int64_t offset, int whence)
{
    return SDL_RWseek((SDL_RWops*)datasource, (int)offset, whence);
}

static int sdl_close_func_freesrc(void *datasource)
{
    return SDL_RWclose((SDL_RWops*)datasource);
}

static int sdl_close_func_nofreesrc(void *datasource)
{
    return SDL_RWseek((SDL_RWops*)datasource, 0, RW_SEEK_SET);
}

static long sdl_tell_func(void *datasource)
{
    return SDL_RWtell((SDL_RWops*)datasource);
}


/* don't call this directly; use Mix_LoadWAV_RW() for now. */
SDL_AudioSpec *Mix_LoadOGG_RW (SDL_RWops *src, int freesrc,
        SDL_AudioSpec *spec, Uint8 **audio_buf, Uint32 *audio_len)
{
    OggVorbis_File vf;
    ov_callbacks callbacks;
    vorbis_info *info;
    Uint8 *buf;
    int bitstream = -1;
    long samplesize;
    long samples;
    int read, to_read;
    int must_close = 1;
    int was_error = 1;
    
    if ( (!src) || (!audio_buf) || (!audio_len) )   /* sanity checks. */
        goto done;

    if ( !Mix_Init(MIX_INIT_OGG) )
        goto done;

    callbacks.read_func = sdl_read_func;
    callbacks.seek_func = sdl_seek_func;
    callbacks.tell_func = sdl_tell_func;
    callbacks.close_func = freesrc ? 
                           sdl_close_func_freesrc : sdl_close_func_nofreesrc;

    if (vorbis.ov_open_callbacks(src, &vf, NULL, 0, callbacks) != 0)
    {
        SDL_SetError("OGG bitstream is not valid Vorbis stream!");
        goto done;
    }

    must_close = 0;
    
    info = vorbis.ov_info(&vf, -1);
    
    *audio_buf = NULL;
    *audio_len = 0;
    memset(spec, '\0', sizeof (SDL_AudioSpec));

    spec->format = AUDIO_S16;
    spec->channels = info->channels;
    spec->freq = info->rate;
    spec->samples = 4096; /* buffer size */
    
    samples = (long)vorbis.ov_pcm_total(&vf, -1);

    *audio_len = spec->size = samples * spec->channels * 2;
    *audio_buf = malloc(*audio_len);
    if (*audio_buf == NULL)
        goto done;

    buf = *audio_buf;
    to_read = *audio_len;
#ifdef OGG_USE_TREMOR
    for (read = vorbis.ov_read(&vf, (char *)buf, to_read, &bitstream);
	 read > 0;
	 read = vorbis.ov_read(&vf, (char *)buf, to_read, &bitstream))
#else
    for (read = vorbis.ov_read(&vf, (char *)buf, to_read, 0/*LE*/, 2/*16bit*/, 1/*signed*/, &bitstream);
         read > 0;
         read = vorbis.ov_read(&vf, (char *)buf, to_read, 0, 2, 1, &bitstream))
#endif	 
    {
        if (read == OV_HOLE || read == OV_EBADLINK)
            break; /* error */
        
        to_read -= read;
        buf += read;
    }

    vorbis.ov_clear(&vf);
    was_error = 0;

    /* Don't return a buffer that isn't a multiple of samplesize */
    samplesize = ((spec->format & 0xFF)/8)*spec->channels;
    *audio_len &= ~(samplesize-1);

done:
    if (src && must_close)
    {
        if (freesrc)
            SDL_RWclose(src);
        else
            SDL_RWseek(src, 0, RW_SEEK_SET);
    }

    if ( was_error )
        spec = NULL;

    return(spec);
} /* Mix_LoadOGG_RW */

/* end of load_ogg.c ... */

#endif
