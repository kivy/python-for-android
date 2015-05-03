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


    The following file defines all of the functions/objects used to dynamically
    link to the libFLAC library.
    										~ Austen Dicken (admin@cvpcs.org)
*/

#ifdef FLAC_MUSIC

#include <FLAC/stream_decoder.h>

typedef struct {
	int loaded;
	void *handle;
	FLAC__StreamDecoder *(*FLAC__stream_decoder_new)();
	void (*FLAC__stream_decoder_delete)(FLAC__StreamDecoder *decoder);
	FLAC__StreamDecoderInitStatus (*FLAC__stream_decoder_init_stream)(
						FLAC__StreamDecoder *decoder,
						FLAC__StreamDecoderReadCallback read_callback,
						FLAC__StreamDecoderSeekCallback seek_callback,
						FLAC__StreamDecoderTellCallback tell_callback,
						FLAC__StreamDecoderLengthCallback length_callback,
						FLAC__StreamDecoderEofCallback eof_callback,
						FLAC__StreamDecoderWriteCallback write_callback,
						FLAC__StreamDecoderMetadataCallback metadata_callback,
						FLAC__StreamDecoderErrorCallback error_callback,
						void *client_data);
	FLAC__bool (*FLAC__stream_decoder_finish)(FLAC__StreamDecoder *decoder);
	FLAC__bool (*FLAC__stream_decoder_flush)(FLAC__StreamDecoder *decoder);
	FLAC__bool (*FLAC__stream_decoder_process_single)(
						FLAC__StreamDecoder *decoder);
	FLAC__bool (*FLAC__stream_decoder_process_until_end_of_metadata)(
						FLAC__StreamDecoder *decoder);
	FLAC__bool (*FLAC__stream_decoder_process_until_end_of_stream)(
						FLAC__StreamDecoder *decoder);
	FLAC__bool (*FLAC__stream_decoder_seek_absolute)(
						FLAC__StreamDecoder *decoder,
						FLAC__uint64 sample);
	FLAC__StreamDecoderState (*FLAC__stream_decoder_get_state)(
						const FLAC__StreamDecoder *decoder);
} flac_loader;

extern flac_loader flac;

#endif /* FLAC_MUSIC */

extern int Mix_InitFLAC();
extern void Mix_QuitFLAC();
