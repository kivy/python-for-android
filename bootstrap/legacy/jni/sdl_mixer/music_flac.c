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


    This file is used to support SDL_LoadMUS playback of FLAC files.
   											~ Austen Dicken (admin@cvpcs.org)
*/

#ifdef FLAC_MUSIC

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "SDL_mixer.h"
#include "dynamic_flac.h"
#include "music_flac.h"

/* This is the format of the audio mixer data */
static SDL_AudioSpec mixer;

/* Initialize the FLAC player, with the given mixer settings
   This function returns 0, or -1 if there was an error.
 */
int FLAC_init(SDL_AudioSpec *mixerfmt)
{
	mixer = *mixerfmt;
	return(0);
}

/* Set the volume for an FLAC stream */
void FLAC_setvolume(FLAC_music *music, int volume)
{
	music->volume = volume;
}

/* Load an FLAC stream from the given file */
FLAC_music *FLAC_new(const char *file)
{
	SDL_RWops *rw;

	rw = SDL_RWFromFile (file, "rb");
	if (rw == NULL) {
		SDL_SetError ("Couldn't open %s", file);
		return NULL;
	}
	return FLAC_new_RW (rw);
}

static FLAC__StreamDecoderReadStatus flac_read_music_cb(
									const FLAC__StreamDecoder *decoder,
									FLAC__byte buffer[],
									size_t *bytes,
									void *client_data)
{
	FLAC_music *data = (FLAC_music*)client_data;

	// make sure there is something to be reading
	if (*bytes > 0) {
		*bytes = SDL_RWread (data->rwops, buffer, sizeof (FLAC__byte), *bytes);

		if (*bytes < 0) { // error in read
			return FLAC__STREAM_DECODER_READ_STATUS_ABORT;
		}
		else if (*bytes == 0 ) { // no data was read (EOF)
			return FLAC__STREAM_DECODER_READ_STATUS_END_OF_STREAM;
		}
		else { // data was read, continue
			return FLAC__STREAM_DECODER_READ_STATUS_CONTINUE;
		}
	}
	else {
		return FLAC__STREAM_DECODER_READ_STATUS_ABORT;
	}
}

static FLAC__StreamDecoderSeekStatus flac_seek_music_cb(
									const FLAC__StreamDecoder *decoder,
									FLAC__uint64 absolute_byte_offset,
									void *client_data)
{
	FLAC_music *data = (FLAC_music*)client_data;

	if (SDL_RWseek (data->rwops, absolute_byte_offset, RW_SEEK_SET) < 0) {
		return FLAC__STREAM_DECODER_SEEK_STATUS_ERROR;
	}
	else {
		return FLAC__STREAM_DECODER_SEEK_STATUS_OK;
	}
}

static FLAC__StreamDecoderTellStatus flac_tell_music_cb(
									const FLAC__StreamDecoder *decoder,
									FLAC__uint64 *absolute_byte_offset,
									void *client_data )
{
	FLAC_music *data = (FLAC_music*)client_data;

	int pos = SDL_RWtell (data->rwops);

	if (pos < 0) {
		return FLAC__STREAM_DECODER_TELL_STATUS_ERROR;
	}
	else {
		*absolute_byte_offset = (FLAC__uint64)pos;
		return FLAC__STREAM_DECODER_TELL_STATUS_OK;
	}
}

static FLAC__StreamDecoderLengthStatus flac_length_music_cb (
									const FLAC__StreamDecoder *decoder,
									FLAC__uint64 *stream_length,
									void *client_data)
{
	FLAC_music *data = (FLAC_music*)client_data;

	int pos = SDL_RWtell (data->rwops);
	int length = SDL_RWseek (data->rwops, 0, RW_SEEK_END);

	if (SDL_RWseek (data->rwops, pos, RW_SEEK_SET) != pos || length < 0) {
		/* there was an error attempting to return the stream to the original
		 * position, or the length was invalid. */
		return FLAC__STREAM_DECODER_LENGTH_STATUS_ERROR;
	}
	else {
		*stream_length = (FLAC__uint64)length;
		return FLAC__STREAM_DECODER_LENGTH_STATUS_OK;
	}
}

static FLAC__bool flac_eof_music_cb(
								const FLAC__StreamDecoder *decoder,
								void *client_data )
{
	FLAC_music *data = (FLAC_music*)client_data;

	int pos = SDL_RWtell (data->rwops);
	int end = SDL_RWseek (data->rwops, 0, RW_SEEK_END);

	// was the original position equal to the end (a.k.a. the seek didn't move)?
	if (pos == end) {
		// must be EOF
		return true;
	}
	else {
		// not EOF, return to the original position
		SDL_RWseek (data->rwops, pos, RW_SEEK_SET);

		return false;
	}
}

static FLAC__StreamDecoderWriteStatus flac_write_music_cb(
									const FLAC__StreamDecoder *decoder,
									const FLAC__Frame *frame,
									const FLAC__int32 *const buffer[],
									void *client_data)
{
	FLAC_music *data = (FLAC_music *)client_data;
	size_t i;

	if (data->flac_data.total_samples == 0) {
		SDL_SetError ("Given FLAC file does not specify its sample count.");
		return FLAC__STREAM_DECODER_WRITE_STATUS_ABORT;
	}

	if (data->flac_data.channels != 2 ||
		data->flac_data.bits_per_sample != 16) {
		SDL_SetError("Current FLAC support is only for 16 bit Stereo files.");
		return FLAC__STREAM_DECODER_WRITE_STATUS_ABORT;
	}

	for (i = 0; i < frame->header.blocksize; i++) {
		FLAC__int16 i16;
		FLAC__uint16 ui16;

		// make sure we still have at least two bytes that can be read (one for
		// each channel)
		if (data->flac_data.max_to_read >= 4) {
			// does the data block exist?
			if (!data->flac_data.data) {
				data->flac_data.data_len = data->flac_data.max_to_read;
				data->flac_data.data_read = 0;

				// create it
				data->flac_data.data =
									(char *)malloc (data->flac_data.data_len);

				if (!data->flac_data.data) {
					return FLAC__STREAM_DECODER_WRITE_STATUS_ABORT;
				}
			}

			i16 = (FLAC__int16)buffer[0][i];
			ui16 = (FLAC__uint16)i16;

			*((data->flac_data.data) + (data->flac_data.data_read++)) =
															(char)(ui16);
			*((data->flac_data.data) + (data->flac_data.data_read++)) =
															(char)(ui16 >> 8);

			i16 = (FLAC__int16)buffer[1][i];
			ui16 = (FLAC__uint16)i16;

			*((data->flac_data.data) + (data->flac_data.data_read++)) =
															(char)(ui16);
			*((data->flac_data.data) + (data->flac_data.data_read++)) =
															(char)(ui16 >> 8);

			data->flac_data.max_to_read -= 4;

			if (data->flac_data.max_to_read < 4) {
				// we need to set this so that the read halts from the
				// FLAC_getsome function.
				data->flac_data.max_to_read = 0;
			}
		}
		else {
			// we need to write to the overflow
			if (!data->flac_data.overflow) {
				data->flac_data.overflow_len =
											4 * (frame->header.blocksize - i);
				data->flac_data.overflow_read = 0;

				// make it big enough for the rest of the block
				data->flac_data.overflow =
								(char *)malloc (data->flac_data.overflow_len);

				if (!data->flac_data.overflow) {
					return FLAC__STREAM_DECODER_WRITE_STATUS_ABORT;
				}
			}

			i16 = (FLAC__int16)buffer[0][i];
			ui16 = (FLAC__uint16)i16;

			*((data->flac_data.overflow) + (data->flac_data.overflow_read++)) =
															(char)(ui16);
			*((data->flac_data.overflow) + (data->flac_data.overflow_read++)) =
															(char)(ui16 >> 8);

			i16 = (FLAC__int16)buffer[1][i];
			ui16 = (FLAC__uint16)i16;

			*((data->flac_data.overflow) + (data->flac_data.overflow_read++)) =
															(char)(ui16);
			*((data->flac_data.overflow) + (data->flac_data.overflow_read++)) =
															(char)(ui16 >> 8);
		}
	}

	return FLAC__STREAM_DECODER_WRITE_STATUS_CONTINUE;
}

static void flac_metadata_music_cb(
					const FLAC__StreamDecoder *decoder,
					const FLAC__StreamMetadata *metadata,
					void *client_data)
{
	FLAC_music *data = (FLAC_music *)client_data;

	if (metadata->type == FLAC__METADATA_TYPE_STREAMINFO) {
		data->flac_data.sample_rate = metadata->data.stream_info.sample_rate;
		data->flac_data.channels = metadata->data.stream_info.channels;
		data->flac_data.total_samples =
							metadata->data.stream_info.total_samples;
		data->flac_data.bits_per_sample =
							metadata->data.stream_info.bits_per_sample;
		data->flac_data.sample_size = data->flac_data.channels *
										((data->flac_data.bits_per_sample) / 8);
	}
}

static void flac_error_music_cb(
				const FLAC__StreamDecoder *decoder,
				FLAC__StreamDecoderErrorStatus status,
				void *client_data)
{
	// print an SDL error based on the error status
	switch (status) {
		case FLAC__STREAM_DECODER_ERROR_STATUS_LOST_SYNC:
			SDL_SetError ("Error processing the FLAC file [LOST_SYNC].");
		break;
		case FLAC__STREAM_DECODER_ERROR_STATUS_BAD_HEADER:
			SDL_SetError ("Error processing the FLAC file [BAD_HEADER].");
		break;
		case FLAC__STREAM_DECODER_ERROR_STATUS_FRAME_CRC_MISMATCH:
			SDL_SetError ("Error processing the FLAC file [CRC_MISMATCH].");
		break;
		case FLAC__STREAM_DECODER_ERROR_STATUS_UNPARSEABLE_STREAM:
			SDL_SetError ("Error processing the FLAC file [UNPARSEABLE].");
		break;
		default:
			SDL_SetError ("Error processing the FLAC file [UNKNOWN].");
		break;
	}
}

/* Load an FLAC stream from an SDL_RWops object */
FLAC_music *FLAC_new_RW(SDL_RWops *rw)
{
	FLAC_music *music;
	int init_stage = 0;
	int was_error = 1;

	music = (FLAC_music *)malloc ( sizeof (*music));
	if (music) {
		/* Initialize the music structure */
		memset (music, 0, (sizeof (*music)));
		FLAC_stop (music);
		FLAC_setvolume (music, MIX_MAX_VOLUME);
		music->section = -1;
		music->rwops = rw;
		music->flac_data.max_to_read = 0;
		music->flac_data.overflow = NULL;
		music->flac_data.overflow_len = 0;
		music->flac_data.overflow_read = 0;
		music->flac_data.data = NULL;
		music->flac_data.data_len = 0;
		music->flac_data.data_read = 0;

		if (Mix_Init(MIX_INIT_FLAC)) {
			init_stage++; // stage 1!

			music->flac_decoder = flac.FLAC__stream_decoder_new ();

			if (music->flac_decoder != NULL) {
				init_stage++; // stage 2!

				if (flac.FLAC__stream_decoder_init_stream(
							music->flac_decoder,
							flac_read_music_cb, flac_seek_music_cb,
							flac_tell_music_cb, flac_length_music_cb,
							flac_eof_music_cb, flac_write_music_cb,
							flac_metadata_music_cb, flac_error_music_cb,
							music) == FLAC__STREAM_DECODER_INIT_STATUS_OK ) {
					init_stage++; // stage 3!

					if (flac.FLAC__stream_decoder_process_until_end_of_metadata
											(music->flac_decoder)) {
						was_error = 0;
					} else {
						SDL_SetError("FLAC__stream_decoder_process_until_end_of_metadata() failed");
					}
				} else {
					SDL_SetError("FLAC__stream_decoder_init_stream() failed");
				}
			} else {
				SDL_SetError("FLAC__stream_decoder_new() failed");
			}
		}

		if (was_error) {
			switch (init_stage) {
				case 3:
					flac.FLAC__stream_decoder_finish( music->flac_decoder );
				case 2:
					flac.FLAC__stream_decoder_delete( music->flac_decoder );
				case 1:
				case 0:
					free(music);
					SDL_RWclose(rw);
					break;
			}
			return NULL;
		}
	}
	else {
		SDL_OutOfMemory();
	}

	return music;
}

/* Start playback of a given FLAC stream */
void FLAC_play(FLAC_music *music)
{
	music->playing = 1;
}

/* Return non-zero if a stream is currently playing */
int FLAC_playing(FLAC_music *music)
{
	return(music->playing);
}

/* Read some FLAC stream data and convert it for output */
static void FLAC_getsome(FLAC_music *music)
{
	int section;
	SDL_AudioCVT *cvt;

	/* GET AUDIO wAVE DATA */
	// set the max number of characters to read
	music->flac_data.max_to_read = 8192;

	// clear out the data buffer if it exists
	if (music->flac_data.data) {
		free (music->flac_data.data);
	}

	music->flac_data.data_len = music->flac_data.max_to_read;
	music->flac_data.data_read = 0;
	music->flac_data.data = (char *)malloc (music->flac_data.data_len);

	// we have data to read
	while(music->flac_data.max_to_read > 0) {
		// first check if there is data in the overflow from before
		if (music->flac_data.overflow) {
			size_t overflow_len = music->flac_data.overflow_read;

			if (overflow_len > music->flac_data.max_to_read) {
				size_t overflow_extra_len = overflow_len -
												music->flac_data.max_to_read;

				char* new_overflow = (char *)malloc (overflow_extra_len);
				memcpy (music->flac_data.data+music->flac_data.data_read,
					music->flac_data.overflow, music->flac_data.max_to_read);
				music->flac_data.data_read += music->flac_data.max_to_read;
				memcpy (new_overflow,
					music->flac_data.overflow + music->flac_data.max_to_read,
					overflow_extra_len);
				free (music->flac_data.overflow);
				music->flac_data.overflow = new_overflow;
				music->flac_data.overflow_len = overflow_extra_len;
				music->flac_data.overflow_read = 0;
				music->flac_data.max_to_read = 0;
			}
			else {
				memcpy (music->flac_data.data+music->flac_data.data_read,
					music->flac_data.overflow, overflow_len);
				music->flac_data.data_read += overflow_len;
				free (music->flac_data.overflow);
				music->flac_data.overflow = NULL;
				music->flac_data.overflow_len = 0;
				music->flac_data.overflow_read = 0;
				music->flac_data.max_to_read -= overflow_len;
			}
		}
		else {
			if (!flac.FLAC__stream_decoder_process_single (
														music->flac_decoder)) {
				music->flac_data.max_to_read = 0;
			}

			if (flac.FLAC__stream_decoder_get_state (music->flac_decoder)
									== FLAC__STREAM_DECODER_END_OF_STREAM) {
				music->flac_data.max_to_read = 0;
			}
		}
	}

	if (music->flac_data.data_read <= 0) {
		if (music->flac_data.data_read == 0) {
			music->playing = 0;
		}
		return;
	}
	cvt = &music->cvt;
	if (section != music->section) {

		SDL_BuildAudioCVT (cvt, AUDIO_S16, (Uint8)music->flac_data.channels,
						(int)music->flac_data.sample_rate, mixer.format,
		                mixer.channels, mixer.freq);
		if (cvt->buf) {
			free (cvt->buf);
		}
		cvt->buf = (Uint8 *)malloc (music->flac_data.data_len * cvt->len_mult);
		music->section = section;
	}
	if (cvt->buf) {
		memcpy (cvt->buf, music->flac_data.data, music->flac_data.data_read);
		if (cvt->needed) {
			cvt->len = music->flac_data.data_read;
			SDL_ConvertAudio (cvt);
		}
		else {
			cvt->len_cvt = music->flac_data.data_read;
		}
		music->len_available = music->cvt.len_cvt;
		music->snd_available = music->cvt.buf;
	}
	else {
		SDL_SetError ("Out of memory");
		music->playing = 0;
	}
}

/* Play some of a stream previously started with FLAC_play() */
int FLAC_playAudio(FLAC_music *music, Uint8 *snd, int len)
{
	int mixable;

	while ((len > 0) && music->playing) {
		if (!music->len_available) {
			FLAC_getsome (music);
		}
		mixable = len;
		if (mixable > music->len_available) {
			mixable = music->len_available;
		}
		if (music->volume == MIX_MAX_VOLUME) {
			memcpy (snd, music->snd_available, mixable);
		}
		else {
			SDL_MixAudio (snd, music->snd_available, mixable, music->volume);
		}
		music->len_available -= mixable;
		music->snd_available += mixable;
		len -= mixable;
		snd += mixable;
	}

	return len;
}

/* Stop playback of a stream previously started with FLAC_play() */
void FLAC_stop(FLAC_music *music)
{
	music->playing = 0;
}

/* Close the given FLAC_music object */
void FLAC_delete(FLAC_music *music)
{
	if (music) {
		if (music->flac_decoder) {
			flac.FLAC__stream_decoder_finish (music->flac_decoder);
			flac.FLAC__stream_decoder_delete (music->flac_decoder);
		}

		if (music->flac_data.data) {
			free (music->flac_data.data);
		}

		if (music->flac_data.overflow) {
			free (music->flac_data.overflow);
		}

		if (music->cvt.buf) {
			free (music->cvt.buf);
		}

		free (music);
	}
}

/* Jump (seek) to a given position (time is in seconds) */
void FLAC_jump_to_time(FLAC_music *music, double time)
{
	if (music) {
		if (music->flac_decoder) {
			double seek_sample = music->flac_data.sample_rate * time;

			// clear data if it has data
			if (music->flac_data.data) {
				free (music->flac_data.data);
				music->flac_data.data = NULL;
			}

			// clear overflow if it has data
			if (music->flac_data.overflow) {
				free (music->flac_data.overflow);
				music->flac_data.overflow = NULL;
			}

			if (!flac.FLAC__stream_decoder_seek_absolute (music->flac_decoder,
												(FLAC__uint64)seek_sample)) {
				if (flac.FLAC__stream_decoder_get_state (music->flac_decoder)
										== FLAC__STREAM_DECODER_SEEK_ERROR) {
					flac.FLAC__stream_decoder_flush (music->flac_decoder);
				}

				SDL_SetError
					("Seeking of FLAC stream failed: libFLAC seek failed.");
			}
		}
		else {
			SDL_SetError
				("Seeking of FLAC stream failed: FLAC decoder was NULL.");
		}
	}
	else {
		SDL_SetError ("Seeking of FLAC stream failed: music was NULL.");
	}
}

#endif /* FLAC_MUSIC */
