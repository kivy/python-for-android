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
#include "SDL_config.h"

/* everything below is currently one very big bad hack ;) Proff */

#if __WIN32__
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <windowsx.h>
#include <mmsystem.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include "native_midi.h"
#include "native_midi_common.h"

struct _NativeMidiSong {
  int MusicLoaded;
  int MusicPlaying;
  MIDIHDR MidiStreamHdr;
  MIDIEVENT *NewEvents;
	Uint16 ppqn;
  int Size;
  int NewPos;
};

static UINT MidiDevice=MIDI_MAPPER;
static HMIDISTRM hMidiStream;
static NativeMidiSong *currentsong;

static int BlockOut(NativeMidiSong *song)
{
  MMRESULT err;
  int BlockSize;

  if ((song->MusicLoaded) && (song->NewEvents))
  {
    // proff 12/8/98: Added for savety
    midiOutUnprepareHeader((HMIDIOUT)hMidiStream,&song->MidiStreamHdr,sizeof(MIDIHDR));
    if (song->NewPos>=song->Size)
      return 0;
    BlockSize=(song->Size-song->NewPos);
    if (BlockSize<=0)
      return 0;
    if (BlockSize>36000)
      BlockSize=36000;
    song->MidiStreamHdr.lpData=(void *)((unsigned char *)song->NewEvents+song->NewPos);
    song->NewPos+=BlockSize;
    song->MidiStreamHdr.dwBufferLength=BlockSize;
    song->MidiStreamHdr.dwBytesRecorded=BlockSize;
    song->MidiStreamHdr.dwFlags=0;
    err=midiOutPrepareHeader((HMIDIOUT)hMidiStream,&song->MidiStreamHdr,sizeof(MIDIHDR));
    if (err!=MMSYSERR_NOERROR)
      return 0;
    err=midiStreamOut(hMidiStream,&song->MidiStreamHdr,sizeof(MIDIHDR));
      return 0;
  }
  return 1;
}

static void MIDItoStream(NativeMidiSong *song, MIDIEvent *evntlist)
{
  int eventcount;
  MIDIEvent *event;
  MIDIEVENT *newevent;

  eventcount=0;
  event=evntlist;
  while (event)
  {
    eventcount++;
    event=event->next;
  }
  song->NewEvents=malloc(eventcount*3*sizeof(DWORD));
  if (!song->NewEvents)
    return;
  memset(song->NewEvents,0,(eventcount*3*sizeof(DWORD)));

  eventcount=0;
  event=evntlist;
  newevent=song->NewEvents;
  while (event)
  {
		int status = (event->status&0xF0)>>4;
		switch (status)
		{
		case MIDI_STATUS_NOTE_OFF:
		case MIDI_STATUS_NOTE_ON:
		case MIDI_STATUS_AFTERTOUCH:
		case MIDI_STATUS_CONTROLLER:
		case MIDI_STATUS_PROG_CHANGE:
		case MIDI_STATUS_PRESSURE:
		case MIDI_STATUS_PITCH_WHEEL:
      newevent->dwDeltaTime=event->time;
		  newevent->dwEvent=(event->status|0x80)|(event->data[0]<<8)|(event->data[1]<<16)|(MEVT_SHORTMSG<<24);
      newevent=(MIDIEVENT*)((char*)newevent+(3*sizeof(DWORD)));
      eventcount++;
			break;

		case MIDI_STATUS_SYSEX:
			if (event->status == 0xFF && event->data[0] == 0x51) /* Tempo change */
			{
				int tempo = (event->extraData[0] << 16) |
					          (event->extraData[1] << 8) |
					           event->extraData[2];
        newevent->dwDeltaTime=event->time;
				newevent->dwEvent=(MEVT_TEMPO<<24) | tempo;
        newevent=(MIDIEVENT*)((char*)newevent+(3*sizeof(DWORD)));
        eventcount++;
			}
			break;
    }

    event=event->next;
  }

  song->Size=eventcount*3*sizeof(DWORD);

  {
    int time;
    int temptime;

    song->NewPos=0;
    time=0;
    newevent=song->NewEvents;
    while (song->NewPos<song->Size)
    {
      temptime=newevent->dwDeltaTime;
      newevent->dwDeltaTime-=time;
      time=temptime;
      if ((song->NewPos+12)>=song->Size)
        newevent->dwEvent |= MEVT_F_CALLBACK;
      newevent=(MIDIEVENT*)((char*)newevent+(3*sizeof(DWORD)));
      song->NewPos+=12;
    }
  }
  song->NewPos=0;
  song->MusicLoaded=1;
}

void CALLBACK MidiProc( HMIDIIN hMidi, UINT uMsg, DWORD_PTR dwInstance,
                        DWORD_PTR dwParam1, DWORD_PTR dwParam2 )
{
    switch( uMsg )
    {
    case MOM_DONE:
      if ((currentsong->MusicLoaded) && (dwParam1 == (DWORD_PTR)&currentsong->MidiStreamHdr))
        BlockOut(currentsong);
      break;
    case MOM_POSITIONCB:
      if ((currentsong->MusicLoaded) && (dwParam1 == (DWORD_PTR)&currentsong->MidiStreamHdr))
        currentsong->MusicPlaying=0;
      break;
    default:
      break;
    }
}

int native_midi_detect()
{
  MMRESULT merr;
  HMIDISTRM MidiStream;

  merr=midiStreamOpen(&MidiStream,&MidiDevice,(DWORD)1,(DWORD_PTR)MidiProc,(DWORD_PTR)0,CALLBACK_FUNCTION);
  if (merr!=MMSYSERR_NOERROR)
    return 0;
  midiStreamClose(MidiStream);
  return 1;
}

NativeMidiSong *native_midi_loadsong(const char *midifile)
{
	NativeMidiSong *newsong;
	MIDIEvent		*evntlist = NULL;
	SDL_RWops	*rw;

	newsong=malloc(sizeof(NativeMidiSong));
	if (!newsong)
		return NULL;
	memset(newsong,0,sizeof(NativeMidiSong));

	/* Attempt to load the midi file */
	rw = SDL_RWFromFile(midifile, "rb");
	if (rw) {
		evntlist = CreateMIDIEventList(rw, &newsong->ppqn);
		SDL_RWclose(rw);
		if (!evntlist)
		{
			free(newsong);
			return NULL;
		}
	}

	MIDItoStream(newsong, evntlist);

	FreeMIDIEventList(evntlist);

	return newsong;
}

NativeMidiSong *native_midi_loadsong_RW(SDL_RWops *rw)
{
	NativeMidiSong *newsong;
	MIDIEvent		*evntlist = NULL;

	newsong=malloc(sizeof(NativeMidiSong));
	if (!newsong)
		return NULL;
	memset(newsong,0,sizeof(NativeMidiSong));

	/* Attempt to load the midi file */
	evntlist = CreateMIDIEventList(rw, &newsong->ppqn);
	if (!evntlist)
	{
		free(newsong);
		return NULL;
	}

	MIDItoStream(newsong, evntlist);

	FreeMIDIEventList(evntlist);

	return newsong;
}

void native_midi_freesong(NativeMidiSong *song)
{
  if (hMidiStream)
  {
    midiStreamStop(hMidiStream);
    midiStreamClose(hMidiStream);
  }
  if (song)
  {
    if (song->NewEvents)
      free(song->NewEvents);
    free(song);
  }
}

void native_midi_start(NativeMidiSong *song)
{
  MMRESULT merr;
  MIDIPROPTIMEDIV mptd;

  native_midi_stop();
  if (!hMidiStream)
  {
    merr=midiStreamOpen(&hMidiStream,&MidiDevice,1,(DWORD)&MidiProc,0,CALLBACK_FUNCTION);
    if (merr!=MMSYSERR_NOERROR)
    {
      hMidiStream=0;
      return;
    }
    //midiStreamStop(hMidiStream);
    currentsong=song;
    currentsong->NewPos=0;
    currentsong->MusicPlaying=1;
    mptd.cbStruct=sizeof(MIDIPROPTIMEDIV);
    mptd.dwTimeDiv=currentsong->ppqn;
    merr=midiStreamProperty(hMidiStream,(LPBYTE)&mptd,MIDIPROP_SET | MIDIPROP_TIMEDIV);
    BlockOut(song);
    merr=midiStreamRestart(hMidiStream);
  }
}

void native_midi_stop()
{
  if (!hMidiStream)
    return;
  midiStreamStop(hMidiStream);
  midiStreamClose(hMidiStream);
  currentsong=NULL;
  hMidiStream = 0;
}

int native_midi_active()
{
  return currentsong->MusicPlaying;
}

void native_midi_setvolume(int volume)
{
  int calcVolume;
  if (volume > 128)
    volume = 128;
  if (volume < 0)
    volume = 0;
  calcVolume = (65535 * volume / 128);

  midiOutSetVolume((HMIDIOUT)hMidiStream, MAKELONG(calcVolume , calcVolume));
}

const char *native_midi_error(void)
{
  return "";
}

#endif /* Windows native MIDI support */
