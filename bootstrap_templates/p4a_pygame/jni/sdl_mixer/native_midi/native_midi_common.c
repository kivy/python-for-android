/*
    native_midi:  Hardware Midi support for the SDL_mixer library
    Copyright (C) 2000,2001  Florian 'Proff' Schulze

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


#include "native_midi_common.h"

#include "../SDL_mixer.h"

#include <stdlib.h>
#include <string.h>
#include <limits.h>


/* The maximum number of midi tracks that we can handle 
#define MIDI_TRACKS 32 */


/* A single midi track as read from the midi file */
typedef struct
{
	Uint8 *data;					/* MIDI message stream */
	int len;						/* length of the track data */
} MIDITrack;

/* A midi file, stripped down to the absolute minimum - divison & track data */
typedef struct
{
	int division;					/* number of pulses per quarter note (ppqn) */
    int nTracks;                    /* number of tracks */
	MIDITrack *track;               /* tracks */
} MIDIFile;


/* Some macros that help us stay endianess-independant */
#if SDL_BYTEORDER == SDL_BIG_ENDIAN
#define BE_SHORT(x) (x)
#define BE_LONG(x) (x)
#else
#define BE_SHORT(x)	((((x)&0xFF)<<8) | (((x)>>8)&0xFF))
#define BE_LONG(x)	((((x)&0x0000FF)<<24) | \
			 (((x)&0x00FF00)<<8) | \
			 (((x)&0xFF0000)>>8) | \
			 (((x)>>24)&0xFF))
#endif



/* Get Variable Length Quantity */
static int GetVLQ(MIDITrack *track, int *currentPos)
{
	int l = 0;
	Uint8 c;
	while(1)
	{
		c = track->data[*currentPos];
		(*currentPos)++;
		l += (c & 0x7f);
		if (!(c & 0x80)) 
			return l;
		l <<= 7;
	}
}

/* Create a single MIDIEvent */
static MIDIEvent *CreateEvent(Uint32 time, Uint8 event, Uint8 a, Uint8 b)
{
	MIDIEvent *newEvent;
	
	newEvent = calloc(1, sizeof(MIDIEvent));

	if (newEvent)
	{
		newEvent->time = time;
		newEvent->status = event;
		newEvent->data[0] = a;
		newEvent->data[1] = b;
	}
	else
		Mix_SetError("Out of memory");
	
	return newEvent;
}

/* Convert a single midi track to a list of MIDIEvents */
static MIDIEvent *MIDITracktoStream(MIDITrack *track)
{
	Uint32 atime = 0;
	Uint32 len = 0;
	Uint8 event,type,a,b;
	Uint8 laststatus = 0;
	Uint8 lastchan = 0;
	int currentPos = 0;
	int end = 0;
	MIDIEvent *head = CreateEvent(0,0,0,0);	/* dummy event to make handling the list easier */
	MIDIEvent *currentEvent = head;

	while (!end)
	{
		if (currentPos >= track->len)
			break; /* End of data stream reached */

		atime += GetVLQ(track, &currentPos);
		event = track->data[currentPos++];
		
		/* Handle SysEx seperatly */
		if (((event>>4) & 0x0F) == MIDI_STATUS_SYSEX)
		{
			if (event == 0xFF)
			{
				type = track->data[currentPos];
				currentPos++;
				switch(type)
				{
					case 0x2f: /* End of data marker */
						end = 1;
					case 0x51: /* Tempo change */
						/*
						a=track->data[currentPos];
						b=track->data[currentPos+1];
						c=track->data[currentPos+2];
						AddEvent(song, atime, MEVT_TEMPO, c, b, a);
						*/
						break;
				}
			}
			else
				type = 0;

			len = GetVLQ(track, &currentPos);
			
			/* Create an event and attach the extra data, if any */
			currentEvent->next = CreateEvent(atime, event, type, 0);
			currentEvent = currentEvent->next;
			if (NULL == currentEvent)
			{
				FreeMIDIEventList(head);
				return NULL;
			}
			if (len)
			{
				currentEvent->extraLen = len;
				currentEvent->extraData = malloc(len);
				memcpy(currentEvent->extraData, &(track->data[currentPos]), len);
				currentPos += len;
			}
		}
		else
		{
			a = event;
			if (a & 0x80) /* It's a status byte */
			{
				/* Extract channel and status information */
				lastchan = a & 0x0F;
				laststatus = (a>>4) & 0x0F;
				
				/* Read the next byte which should always be a data byte */
				a = track->data[currentPos++] & 0x7F;
			}
			switch(laststatus)
			{
				case MIDI_STATUS_NOTE_OFF:
				case MIDI_STATUS_NOTE_ON: /* Note on */
				case MIDI_STATUS_AFTERTOUCH: /* Key Pressure */
				case MIDI_STATUS_CONTROLLER: /* Control change */
				case MIDI_STATUS_PITCH_WHEEL: /* Pitch wheel */
					b = track->data[currentPos++] & 0x7F;
					currentEvent->next = CreateEvent(atime, (Uint8)((laststatus<<4)+lastchan), a, b);
					currentEvent = currentEvent->next;
					if (NULL == currentEvent)
					{
						FreeMIDIEventList(head);
						return NULL;
					}
					break;

				case MIDI_STATUS_PROG_CHANGE: /* Program change */
				case MIDI_STATUS_PRESSURE: /* Channel pressure */
					a &= 0x7f;
					currentEvent->next = CreateEvent(atime, (Uint8)((laststatus<<4)+lastchan), a, 0);
					currentEvent = currentEvent->next;
					if (NULL == currentEvent)
					{
						FreeMIDIEventList(head);
						return NULL;
					}
					break;

				default: /* Sysex already handled above */
					break;
			}
		}
	}
	
	currentEvent = head->next;
	free(head);	/* release the dummy head event */
	return currentEvent;
}

/*
 *  Convert a midi song, consisting of up to 32 tracks, to a list of MIDIEvents.
 *  To do so, first convert the tracks seperatly, then interweave the resulting
 *  MIDIEvent-Lists to one big list.
 */
static MIDIEvent *MIDItoStream(MIDIFile *mididata)
{
	MIDIEvent **track;
	MIDIEvent *head = CreateEvent(0,0,0,0);	/* dummy event to make handling the list easier */
	MIDIEvent *currentEvent = head;
	int trackID;

    if (NULL == head)
		return NULL;
        
    track = (MIDIEvent**) calloc(1, sizeof(MIDIEvent*) * mididata->nTracks);
	if (NULL == head)
        return NULL;
	
	/* First, convert all tracks to MIDIEvent lists */
	for (trackID = 0; trackID < mididata->nTracks; trackID++)
		track[trackID] = MIDITracktoStream(&mididata->track[trackID]);

	/* Now, merge the lists. */
	/* TODO */
	while(1)
	{
		Uint32 lowestTime = INT_MAX;
		int currentTrackID = -1;
		
		/* Find the next event */
		for (trackID = 0; trackID < mididata->nTracks; trackID++)
		{
			if (track[trackID] && (track[trackID]->time < lowestTime))
			{
				currentTrackID = trackID;
				lowestTime = track[currentTrackID]->time;
			}
		}
		
		/* Check if we processes all events */
		if (currentTrackID == -1)
			break;
		
		currentEvent->next = track[currentTrackID];
		track[currentTrackID] = track[currentTrackID]->next;

		currentEvent = currentEvent->next;
		
		
		lowestTime = 0;
	}

	/* Make sure the list is properly terminated */
	currentEvent->next = 0;

	currentEvent = head->next;
    free(track);
	free(head);	/* release the dummy head event */
	return currentEvent;
}

static int ReadMIDIFile(MIDIFile *mididata, SDL_RWops *rw)
{
	int i = 0;
	Uint32	ID;
	Uint32	size;
	Uint16	format;
	Uint16	tracks;
	Uint16	division;

	if (!mididata)
		return 0;
	if (!rw)
		return 0;

	/* Make sure this is really a MIDI file */
	SDL_RWread(rw, &ID, 1, 4);
	if (BE_LONG(ID) != 'MThd')
		return 0;
	
	/* Header size must be 6 */
	SDL_RWread(rw, &size, 1, 4);
	size = BE_LONG(size);
	if (size != 6)
		return 0;
	
	/* We only support format 0 and 1, but not 2 */
	SDL_RWread(rw, &format, 1, 2);
	format = BE_SHORT(format);
	if (format != 0 && format != 1)
		return 0;
	
	SDL_RWread(rw, &tracks, 1, 2);
	tracks = BE_SHORT(tracks);
	mididata->nTracks = tracks;
    
    /* Allocate tracks */
    mididata->track = (MIDITrack*) calloc(1, sizeof(MIDITrack) * mididata->nTracks);
    if (NULL == mididata->track)
    {
        Mix_SetError("Out of memory");
        goto bail;
    }
    
	/* Retrieve the PPQN value, needed for playback */
	SDL_RWread(rw, &division, 1, 2);
	mididata->division = BE_SHORT(division);
	
	
	for (i=0; i<tracks; i++)
	{
		SDL_RWread(rw, &ID, 1, 4);	/* We might want to verify this is MTrk... */
		SDL_RWread(rw, &size, 1, 4);
		size = BE_LONG(size);
		mididata->track[i].len = size;
		mididata->track[i].data = malloc(size);
		if (NULL == mididata->track[i].data)
		{
			Mix_SetError("Out of memory");
			goto bail;
		}
		SDL_RWread(rw, mididata->track[i].data, 1, size);
	}
	return 1;

bail:
	for(;i >= 0; i--)
	{
		if (mididata->track[i].data)
			free(mididata->track[i].data);
	}

	return 0;
}

MIDIEvent *CreateMIDIEventList(SDL_RWops *rw, Uint16 *division)
{
	MIDIFile *mididata = NULL;
	MIDIEvent *eventList;
	int trackID;
	
	mididata = calloc(1, sizeof(MIDIFile));
	if (!mididata)
		return NULL;

	/* Open the file */
	if ( rw != NULL )
	{
		/* Read in the data */
		if ( ! ReadMIDIFile(mididata, rw))
		{
			free(mididata);
			return NULL;
		}
	}
	else
	{
		free(mididata);
		return NULL;
	}
	
	if (division)
		*division = mididata->division;
	
	eventList = MIDItoStream(mididata);
	
	for(trackID = 0; trackID < mididata->nTracks; trackID++)
	{
		if (mididata->track[trackID].data)
			free(mididata->track[trackID].data);
	}
	free(mididata->track);
    free(mididata);
	
	return eventList;
}

void FreeMIDIEventList(MIDIEvent *head)
{
	MIDIEvent *cur, *next;
	
	cur = head;

	while (cur)
	{
		next = cur->next;
		if (cur->extraData) 
			free (cur->extraData);
		free (cur);
		cur = next;
	}
}
