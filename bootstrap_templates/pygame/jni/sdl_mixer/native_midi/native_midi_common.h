/*
    native_midi:  Hardware Midi support for the SDL_mixer library
    Copyright (C) 2000,2001  Florian 'Proff' Schulze & Max Horn

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

    Max Horn
    max@quendi.de
*/

#ifndef _NATIVE_MIDI_COMMON_H_
#define _NATIVE_MIDI_COMMON_H_

#include "SDL.h"

/* Midi Status Bytes */
#define MIDI_STATUS_NOTE_OFF	0x8
#define MIDI_STATUS_NOTE_ON	0x9
#define MIDI_STATUS_AFTERTOUCH	0xA
#define MIDI_STATUS_CONTROLLER	0xB
#define MIDI_STATUS_PROG_CHANGE	0xC
#define MIDI_STATUS_PRESSURE	0xD
#define MIDI_STATUS_PITCH_WHEEL	0xE
#define MIDI_STATUS_SYSEX	0xF

/* We store the midi events in a linked list; this way it is
   easy to shuffle the tracks together later on; and we are
   flexible in the size of each elemnt.
 */
typedef struct MIDIEvent
{
	Uint32	time;		/* Time at which this midi events occurs */
	Uint8	status;		/* Status byte */
	Uint8	data[2];	/* 1 or 2 bytes additional data for most events */

	Uint32	extraLen;	/* For some SysEx events, we need additional storage */
	Uint8	*extraData;
	
	struct MIDIEvent *next;
} MIDIEvent;


/* Load a midifile to memory, converting it to a list of MIDIEvents.
   This function returns a linked lists of MIDIEvents, 0 if an error occured.
 */ 
MIDIEvent *CreateMIDIEventList(SDL_RWops *rw, Uint16 *division);

/* Release a MIDIEvent list after usage. */
void FreeMIDIEventList(MIDIEvent *head);


#endif /* _NATIVE_MIDI_COMMON_H_ */
