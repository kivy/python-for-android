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

#ifdef MP3_MAD_MUSIC

#include "mad.h"
#include "SDL_rwops.h"
#include "SDL_audio.h"
#include "SDL_mixer.h"

#define MAD_INPUT_BUFFER_SIZE	(5*8192)
#define MAD_OUTPUT_BUFFER_SIZE	8192

enum {
  MS_input_eof    = 0x0001,
  MS_input_error  = 0x0001,
  MS_decode_eof   = 0x0002,
  MS_decode_error = 0x0004,
  MS_error_flags  = 0x000f,

  MS_playing      = 0x0100,
  MS_cvt_decoded  = 0x0200,
};

typedef struct {
  SDL_RWops *rw;
  SDL_bool freerw;
  struct mad_stream stream;
  struct mad_frame frame;
  struct mad_synth synth;
  int frames_read;
  mad_timer_t next_frame_start;
  int volume;
  int status;
  int output_begin, output_end;
  SDL_AudioSpec mixer;
  SDL_AudioCVT cvt;

  unsigned char input_buffer[MAD_INPUT_BUFFER_SIZE + MAD_BUFFER_GUARD];
  unsigned char output_buffer[MAD_OUTPUT_BUFFER_SIZE];
} mad_data;

mad_data *mad_openFile(const char *filename, SDL_AudioSpec *mixer);
mad_data *mad_openFileRW(SDL_RWops *rw, SDL_AudioSpec *mixer);
void mad_closeFile(mad_data *mp3_mad);

void mad_start(mad_data *mp3_mad);
void mad_stop(mad_data *mp3_mad);
int mad_isPlaying(mad_data *mp3_mad);

int mad_getSamples(mad_data *mp3_mad, Uint8 *stream, int len);
void mad_seek(mad_data *mp3_mad, double position);
void mad_setVolume(mad_data *mp3_mad, int volume);

#endif
