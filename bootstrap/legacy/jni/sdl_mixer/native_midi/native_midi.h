/*
    native_midi:  Hardware Midi support for the SDL_mixer library
    Copyright (C) 2000  Florian 'Proff' Schulze

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

    Florian 'Proff' Schulze
    florian.proff.schulze@gmx.net
*/

#ifndef _NATIVE_MIDI_H_
#define _NATIVE_MIDI_H_

#include <SDL_rwops.h>

typedef struct _NativeMidiSong NativeMidiSong;

int native_midi_detect();
NativeMidiSong *native_midi_loadsong(const char *midifile);
NativeMidiSong *native_midi_loadsong_RW(SDL_RWops *rw);
void native_midi_freesong(NativeMidiSong *song);
void native_midi_start(NativeMidiSong *song);
void native_midi_stop();
int native_midi_active();
void native_midi_setvolume(int volume);
const char *native_midi_error(void);

#endif /* _NATIVE_MIDI_H_ */
