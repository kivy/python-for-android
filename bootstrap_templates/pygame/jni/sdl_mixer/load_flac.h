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

    This is the source needed to decode a FLAC into a waveform.
    									~ Austen Dicken (admin@cvpcs.org).
*/

/* $Id: $ */

#ifdef FLAC_MUSIC
/* Don't call this directly; use Mix_LoadWAV_RW() for now. */
SDL_AudioSpec *Mix_LoadFLAC_RW (SDL_RWops *src, int freesrc,
		SDL_AudioSpec *spec, Uint8 **audio_buf, Uint32 *audio_len);
#endif
