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

#ifdef OGG_MUSIC
#ifdef OGG_USE_TREMOR
#include <tremor/ivorbisfile.h>
#else
#include <vorbis/vorbisfile.h>
#endif

typedef struct {
	int loaded;
	void *handle;
	int (*ov_clear)(OggVorbis_File *vf);
	vorbis_info *(*ov_info)(OggVorbis_File *vf,int link);
	int (*ov_open_callbacks)(void *datasource, OggVorbis_File *vf, char *initial, long ibytes, ov_callbacks callbacks);
	ogg_int64_t (*ov_pcm_total)(OggVorbis_File *vf,int i);
#ifdef OGG_USE_TREMOR
	long (*ov_read)(OggVorbis_File *vf,char *buffer,int length, int *bitstream);
#else
	long (*ov_read)(OggVorbis_File *vf,char *buffer,int length, int bigendianp,int word,int sgned,int *bitstream);
#endif
	int (*ov_time_seek)(OggVorbis_File *vf,double pos);
} vorbis_loader;

extern vorbis_loader vorbis;

#endif /* OGG_MUSIC */

extern int Mix_InitOgg();
extern void Mix_QuitOgg();
