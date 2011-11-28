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


    Implementation of the dynamic loading functionality for libFLAC.
    									~ Austen Dicken (admin@cvpcs.org)
*/

#ifdef FLAC_MUSIC

#include "SDL_loadso.h"

#include "dynamic_flac.h"

flac_loader flac = {
	0, NULL
};

#ifdef FLAC_DYNAMIC
int Mix_InitFLAC()
{
	if ( flac.loaded == 0 ) {
		flac.handle = SDL_LoadObject(FLAC_DYNAMIC);
		if ( flac.handle == NULL ) {
			return -1;
		}
		flac.FLAC__stream_decoder_new =
			(FLAC__StreamDecoder *(*)())
			SDL_LoadFunction(flac.handle, "FLAC__stream_decoder_new");
		if ( flac.FLAC__stream_decoder_new == NULL ) {
			SDL_UnloadObject(flac.handle);
			return -1;
		}
		flac.FLAC__stream_decoder_delete =
			(void (*)(FLAC__StreamDecoder *))
			SDL_LoadFunction(flac.handle, "FLAC__stream_decoder_delete");
		if ( flac.FLAC__stream_decoder_delete == NULL ) {
			SDL_UnloadObject(flac.handle);
			return -1;
		}
		flac.FLAC__stream_decoder_init_stream =
			(FLAC__StreamDecoderInitStatus (*)(
						FLAC__StreamDecoder *,
						FLAC__StreamDecoderReadCallback,
						FLAC__StreamDecoderSeekCallback,
						FLAC__StreamDecoderTellCallback,
						FLAC__StreamDecoderLengthCallback,
						FLAC__StreamDecoderEofCallback,
						FLAC__StreamDecoderWriteCallback,
						FLAC__StreamDecoderMetadataCallback,
						FLAC__StreamDecoderErrorCallback,
						void *))
			SDL_LoadFunction(flac.handle, "FLAC__stream_decoder_init_stream");
		if ( flac.FLAC__stream_decoder_init_stream == NULL ) {
			SDL_UnloadObject(flac.handle);
			return -1;
		}
		flac.FLAC__stream_decoder_finish =
			(FLAC__bool (*)(FLAC__StreamDecoder *))
			SDL_LoadFunction(flac.handle, "FLAC__stream_decoder_finish");
		if ( flac.FLAC__stream_decoder_finish == NULL ) {
			SDL_UnloadObject(flac.handle);
			return -1;
		}
		flac.FLAC__stream_decoder_flush =
			(FLAC__bool (*)(FLAC__StreamDecoder *))
			SDL_LoadFunction(flac.handle, "FLAC__stream_decoder_flush");
		if ( flac.FLAC__stream_decoder_flush == NULL ) {
			SDL_UnloadObject(flac.handle);
			return -1;
		}
		flac.FLAC__stream_decoder_process_single =
			(FLAC__bool (*)(FLAC__StreamDecoder *))
			SDL_LoadFunction(flac.handle,
						"FLAC__stream_decoder_process_single");
		if ( flac.FLAC__stream_decoder_process_single == NULL ) {
			SDL_UnloadObject(flac.handle);
			return -1;
		}
		flac.FLAC__stream_decoder_process_until_end_of_metadata =
			(FLAC__bool (*)(FLAC__StreamDecoder *))
			SDL_LoadFunction(flac.handle,
						"FLAC__stream_decoder_process_until_end_of_metadata");
		if ( flac.FLAC__stream_decoder_process_until_end_of_metadata == NULL ) {
			SDL_UnloadObject(flac.handle);
			return -1;
		}
		flac.FLAC__stream_decoder_process_until_end_of_stream =
			(FLAC__bool (*)(FLAC__StreamDecoder *))
			SDL_LoadFunction(flac.handle,
						"FLAC__stream_decoder_process_until_end_of_stream");
		if ( flac.FLAC__stream_decoder_process_until_end_of_stream == NULL ) {
			SDL_UnloadObject(flac.handle);
			return -1;
		}
		flac.FLAC__stream_decoder_seek_absolute =
			(FLAC__bool (*)(FLAC__StreamDecoder *, FLAC__uint64))
			SDL_LoadFunction(flac.handle, "FLAC__stream_decoder_seek_absolute");
		if ( flac.FLAC__stream_decoder_seek_absolute == NULL ) {
			SDL_UnloadObject(flac.handle);
			return -1;
		}
		flac.FLAC__stream_decoder_get_state =
			(FLAC__StreamDecoderState (*)(const FLAC__StreamDecoder *decoder))
			SDL_LoadFunction(flac.handle, "FLAC__stream_decoder_get_state");
		if ( flac.FLAC__stream_decoder_get_state == NULL ) {
			SDL_UnloadObject(flac.handle);
			return -1;
		}
	}
	++flac.loaded;

	return 0;
}
void Mix_QuitFLAC()
{
	if ( flac.loaded == 0 ) {
		return;
	}
	if ( flac.loaded == 1 ) {
		SDL_UnloadObject(flac.handle);
	}
	--flac.loaded;
}
#else
int Mix_InitFLAC()
{
	if ( flac.loaded == 0 ) {
		flac.FLAC__stream_decoder_new = FLAC__stream_decoder_new;
		flac.FLAC__stream_decoder_delete = FLAC__stream_decoder_delete;
		flac.FLAC__stream_decoder_init_stream =
							FLAC__stream_decoder_init_stream;
		flac.FLAC__stream_decoder_finish = FLAC__stream_decoder_finish;
		flac.FLAC__stream_decoder_flush = FLAC__stream_decoder_flush;
		flac.FLAC__stream_decoder_process_single =
							FLAC__stream_decoder_process_single;
		flac.FLAC__stream_decoder_process_until_end_of_metadata =
							FLAC__stream_decoder_process_until_end_of_metadata;
		flac.FLAC__stream_decoder_process_until_end_of_stream =
							FLAC__stream_decoder_process_until_end_of_stream;
		flac.FLAC__stream_decoder_seek_absolute =
							FLAC__stream_decoder_seek_absolute;
		flac.FLAC__stream_decoder_get_state =
							FLAC__stream_decoder_get_state;
	}
	++flac.loaded;

	return 0;
}
void Mix_QuitFLAC()
{
	if ( flac.loaded == 0 ) {
		return;
	}
	if ( flac.loaded == 1 ) {
	}
	--flac.loaded;
}
#endif /* FLAC_DYNAMIC */

#endif /* FLAC_MUSIC */
