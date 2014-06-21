
SDL_mixer 1.2

The latest version of this library is available from:
http://www.libsdl.org/projects/SDL_mixer/

Due to popular demand, here is a simple multi-channel audio mixer.
It supports 8 channels of 16 bit stereo audio, plus a single channel
of music, mixed by the popular MikMod MOD, Timidity MIDI and SMPEG MP3
libraries.

See the header file SDL_mixer.h and the examples playwave.c and playmus.c
for documentation on this mixer library.

The mixer can currently load Microsoft WAVE files and Creative Labs VOC
files as audio samples, and can load MIDI files via Timidity and the
following music formats via MikMod:  .MOD .S3M .IT .XM. It can load
Ogg Vorbis streams as music if built with Ogg Vorbis or Tremor libraries,
and finally it can load MP3 music using the SMPEG or libmad libraries.

Tremor decoding is disabled by default; you can enable it by passing
	--enable-music-ogg-tremor
to configure, or by defining OGG_MUSIC and OGG_USE_TREMOR.

libmad decoding is disabled by default; you can enable it by passing
	--enable-music-mp3-mad
to configure, or by defining MP3_MAD_MUSIC
vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
WARNING: The license for libmad is GPL, which means that in order to
         use it your application must also be GPL!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The process of mixing MIDI files to wave output is very CPU intensive,
so if playing regular WAVE files sound great, but playing MIDI files
sound choppy, try using 8-bit audio, mono audio, or lower frequencies.

To play MIDI files, you'll need to get a complete set of GUS patches
from:
http://www.libsdl.org/projects/mixer/timidity/timidity.tar.gz
and unpack them in /usr/local/lib under UNIX, and C:\ under Win32.

This library is available under the GNU Library General Public License,
see the file "COPYING" for details.

