/*

    TiMidity -- Experimental MIDI to WAVE converter
    Copyright (C) 1995 Tuukka Toivonen <toivonen@clinet.fi>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

*/

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

#include <SDL_rwops.h>

#include "config.h"
#include "common.h"
#include "instrum.h"
#include "playmidi.h"
#include "readmidi.h"
#include "output.h"
#include "ctrlmode.h"

int32 quietchannels=0;

static int midi_port_number;
char midi_name[FILENAME_MAX+1];

static int track_info, curr_track, curr_title_track;
static char title[128];

#if MAXCHAN <= 16
#define MERGE_CHANNEL_PORT(ch) ((int)(ch))
#else
#define MERGE_CHANNEL_PORT(ch) ((int)(ch) | (midi_port_number << 4))
#endif

/* to avoid some unnecessary parameter passing */
static MidiEventList *evlist;
static int32 event_count;
static SDL_RWops *rw;
static int32 at;

/* These would both fit into 32 bits, but they are often added in
   large multiples, so it's simpler to have two roomy ints */
static int32 sample_increment, sample_correction; /*samples per MIDI delta-t*/

/* Computes how many (fractional) samples one MIDI delta-time unit contains */
static void compute_sample_increment(int32 tempo, int32 divisions)
{
  double a;
  a = (double) (tempo) * (double) (play_mode->rate) * (65536.0/1000000.0) /
    (double)(divisions);

  sample_correction = (int32)(a) & 0xFFFF;
  sample_increment = (int32)(a) >> 16;

  ctl->cmsg(CMSG_INFO, VERB_DEBUG, "Samples per delta-t: %d (correction %d)",
       sample_increment, sample_correction);
}

/* Read variable-length number (7 bits per byte, MSB first) */
static int32 getvl(void)
{
  int32 l=0;
  uint8 c;
  for (;;)
    {
      SDL_RWread(rw,&c,1,1);
      l += (c & 0x7f);
      if (!(c & 0x80)) return l;
      l<<=7;
    }
}


static int sysex(uint32 len, uint8 *syschan, uint8 *sysa, uint8 *sysb, SDL_RWops *rw)
{
  unsigned char *s=(unsigned char *)safe_malloc(len);
  int id, model, ch, port, adhi, adlo, cd, dta, dtb, dtc;
  if (len != (uint32)SDL_RWread(rw, s, 1, len))
    {
      free(s);
      return 0;
    }
  if (len<5) { free(s); return 0; }
  if (curr_track == curr_title_track && track_info > 1) title[0] = '\0';
  id=s[0]; port=s[1]; model=s[2]; adhi=s[3]; adlo=s[4];
  if (id==0x7e && port==0x7f && model==0x09 && adhi==0x01)
    {
      ctl->cmsg(CMSG_TEXT, VERB_VERBOSE, "GM System On", len);
      GM_System_On=1;
      free(s);
      return 0;
    }
  ch = adlo & 0x0f;
  *syschan=(uint8)ch;
  if (id==0x7f && len==7 && port==0x7f && model==0x04 && adhi==0x01)
    {
      ctl->cmsg(CMSG_TEXT, VERB_DEBUG, "Master Volume %d", s[4]+(s[5]<<7));
      free(s);
      *sysa = s[4];
      *sysb = s[5];
      return ME_MASTERVOLUME;
      /** return s[4]+(s[5]<<7); **/
    }
  if (len<8) { free(s); return 0; }
  port &=0x0f;
  ch = (adlo & 0x0f) | ((port & 0x03) << 4);
  *syschan=(uint8)ch;
  cd=s[5]; dta=s[6];
  if (len >= 8) dtb=s[7];
  else dtb=-1;
  if (len >= 9) dtc=s[8];
  else dtc=-1;
  free(s);
  if (id==0x43 && model==0x4c)
    {
	if (!adhi && !adlo && cd==0x7e && !dta)
	  {
      	    ctl->cmsg(CMSG_TEXT, VERB_VERBOSE, "XG System On", len);
	    XG_System_On=1;
	    #ifdef tplus
	    vol_table = xg_vol_table;
	    #endif
	  }
	else if (adhi == 2 && adlo == 1)
	 {
	    if (dtb==8) dtb=3;
	    switch (cd)
	      {
		case 0x00:
		  XG_System_reverb_type=(dta<<3)+dtb;
		  break;
		case 0x20:
		  XG_System_chorus_type=((dta-64)<<3)+dtb;
		  break;
		case 0x40:
		  XG_System_variation_type=dta;
		  break;
		case 0x5a:
		  /* dta==0 Insertion; dta==1 System */
		  break;
		default: break;
	      }
	 }
	else if (adhi == 8 && cd <= 40)
	 {
	    *sysa = dta & 0x7f;
	    switch (cd)
	      {
		case 0x01: /* bank select MSB */
		  return ME_TONE_KIT;
		  break;
		case 0x02: /* bank select LSB */
		  return ME_TONE_BANK;
		  break;
		case 0x03: /* program number */
	      		/** MIDIEVENT(d->at, ME_PROGRAM, lastchan, a, 0); **/
		  return ME_PROGRAM;
		  break;
		case 0x08: /*  */
		  /* d->channel[adlo&0x0f].transpose = (char)(dta-64); */
		  channel[ch].transpose = (char)(dta-64);
      	    	  ctl->cmsg(CMSG_TEXT, VERB_DEBUG, "transpose channel %d by %d",
			(adlo&0x0f)+1, dta-64);
		  break;
		case 0x0b: /* volume */
		  return ME_MAINVOLUME;
		  break;
		case 0x0e: /* pan */
		  return ME_PAN;
		  break;
		case 0x12: /* chorus send */
		  return ME_CHORUSDEPTH;
		  break;
		case 0x13: /* reverb send */
		  return ME_REVERBERATION;
		  break;
		case 0x14: /* variation send */
		  break;
		case 0x18: /* filter cutoff */
		  return ME_BRIGHTNESS;
		  break;
		case 0x19: /* filter resonance */
		  return ME_HARMONICCONTENT;
		  break;
		default: break;
	      }
	  }
      return 0;
    }
  else if (id==0x41 && model==0x42 && adhi==0x12 && adlo==0x40)
    {
	if (dtc<0) return 0;
	if (!cd && dta==0x7f && !dtb && dtc==0x41)
	  {
      	    ctl->cmsg(CMSG_TEXT, VERB_VERBOSE, "GS System On", len);
	    GS_System_On=1;
	    #ifdef tplus
	    vol_table = gs_vol_table;
	    #endif
	  }
	else if (dta==0x15 && (cd&0xf0)==0x10)
	  {
	    int chan=cd&0x0f;
	    if (!chan) chan=9;
	    else if (chan<10) chan--;
	    chan = MERGE_CHANNEL_PORT(chan);
	    channel[chan].kit=dtb;
	  }
	else if (cd==0x01) switch(dta)
	  {
	    case 0x30:
		switch(dtb)
		  {
		    case 0: XG_System_reverb_type=16+0; break;
		    case 1: XG_System_reverb_type=16+1; break;
		    case 2: XG_System_reverb_type=16+2; break;
		    case 3: XG_System_reverb_type= 8+0; break;
		    case 4: XG_System_reverb_type= 8+1; break;
		    case 5: XG_System_reverb_type=32+0; break;
		    case 6: XG_System_reverb_type=8*17; break;
		    case 7: XG_System_reverb_type=8*18; break;
		  }
		break;
	    case 0x38:
		switch(dtb)
		  {
		    case 0: XG_System_chorus_type= 8+0; break;
		    case 1: XG_System_chorus_type= 8+1; break;
		    case 2: XG_System_chorus_type= 8+2; break;
		    case 3: XG_System_chorus_type= 8+4; break;
		    case 4: XG_System_chorus_type=  -1; break;
		    case 5: XG_System_chorus_type= 8*3; break;
		    case 6: XG_System_chorus_type=  -1; break;
		    case 7: XG_System_chorus_type=  -1; break;
		  }
		break;
	  }
      return 0;
    }
  return 0;
}

/* Print a string from the file, followed by a newline. Any non-ASCII
   or unprintable characters will be converted to periods. */
static int dumpstring(int32 len, const char *label)
{
  signed char *s=safe_malloc(len+1);
  if (len != (int32)SDL_RWread(rw, s, 1, len))
    {
      free(s);
      return -1;
    }
  s[len]='\0';
  while (len--)
    {
      if (s[len]<32)
	s[len]='.';
    }
  ctl->cmsg(CMSG_TEXT, VERB_VERBOSE, "%s%s", label, s);
  free(s);
  return 0;
}

#define MIDIEVENT(at,t,ch,pa,pb) \
  new=safe_malloc(sizeof(MidiEventList)); \
  new->event.time=at; new->event.type=t; new->event.channel=ch; \
  new->event.a=pa; new->event.b=pb; new->next=0;\
  return new;

#define MAGIC_EOT ((MidiEventList *)(-1))

/* Read a MIDI event, returning a freshly allocated element that can
   be linked to the event list */
static MidiEventList *read_midi_event(void)
{
  static uint8 laststatus, lastchan;
  static uint8 nrpn=0, rpn_msb[16], rpn_lsb[16]; /* one per channel */
  uint8 me, type, a,b,c;
  int32 len;
  MidiEventList *new;

  for (;;)
    {
      at+=getvl();
      if (SDL_RWread(rw,&me,1,1)!=1)
	{
	  ctl->cmsg(CMSG_ERROR, VERB_NORMAL, "%s: read_midi_event: %s", 
	       current_filename, strerror(errno));
	  return 0;
	}
      
      if(me==0xF0 || me == 0xF7) /* SysEx event */
	{
	  int32 sret;
	  uint8 sysa=0, sysb=0, syschan=0;

	  len=getvl();
	  sret=sysex(len, &syschan, &sysa, &sysb, rw);
	  if (sret)
	   {
	     MIDIEVENT(at, sret, syschan, sysa, sysb);
	   }
	}
      else if(me==0xFF) /* Meta event */
	{
	  SDL_RWread(rw,&type,1,1);
	  len=getvl();
	  if (type>0 && type<16)
	    {
	      static char *label[]={
		"Text event: ", "Text: ", "Copyright: ", "Track name: ",
		"Instrument: ", "Lyric: ", "Marker: ", "Cue point: "};
	      dumpstring(len, label[(type>7) ? 0 : type]);
	    }
	  else
	    switch(type)
	      {

	      case 0x21: /* MIDI port number */
		if(len == 1)
		{
	  	    SDL_RWread(rw,&midi_port_number,1,1);
		    if(midi_port_number == EOF)
		    {
			    ctl->cmsg(CMSG_ERROR, VERB_NORMAL,
				      "Warning: \"%s\": Short midi file.",
				      midi_name);
			    return 0;
		    }
		    midi_port_number &= 0x0f;
		    if (midi_port_number)
			ctl->cmsg(CMSG_INFO, VERB_VERBOSE,
			  "(MIDI port number %d)", midi_port_number);
		    midi_port_number &= 0x03;
		}
		else SDL_RWseek(rw, len, RW_SEEK_CUR);
		break;

	      case 0x2F: /* End of Track */
		return MAGIC_EOT;

	      case 0x51: /* Tempo */
		SDL_RWread(rw,&a,1,1); SDL_RWread(rw,&b,1,1); SDL_RWread(rw,&c,1,1);
		MIDIEVENT(at, ME_TEMPO, c, a, b);
		
	      default:
		ctl->cmsg(CMSG_INFO, VERB_DEBUG, 
		     "(Meta event type 0x%02x, length %ld)", type, len);
		SDL_RWseek(rw, len, RW_SEEK_CUR);
		break;
	      }
	}
      else
	{
	  a=me;
	  if (a & 0x80) /* status byte */
	    {
	      lastchan=a & 0x0F;
	      laststatus=(a>>4) & 0x07;
	      SDL_RWread(rw,&a, 1,1);
	      a &= 0x7F;
	    }
	  switch(laststatus)
	    {
	    case 0: /* Note off */
	      SDL_RWread(rw,&b, 1,1);
	      b &= 0x7F;
	      MIDIEVENT(at, ME_NOTEOFF, lastchan, a,b);

	    case 1: /* Note on */
	      SDL_RWread(rw,&b, 1,1);
	      b &= 0x7F;
	      if (curr_track == curr_title_track && track_info > 1) title[0] = '\0';
	      MIDIEVENT(at, ME_NOTEON, lastchan, a,b);


	    case 2: /* Key Pressure */
	      SDL_RWread(rw,&b, 1,1);
	      b &= 0x7F;
	      MIDIEVENT(at, ME_KEYPRESSURE, lastchan, a, b);

	    case 3: /* Control change */
	      SDL_RWread(rw,&b, 1,1);
	      b &= 0x7F;
	      {
		int control=255;
		switch(a)
		  {
		  case 7: control=ME_MAINVOLUME; break;
		  case 10: control=ME_PAN; break;
		  case 11: control=ME_EXPRESSION; break;
		  case 64: control=ME_SUSTAIN; break;

		  case 71: control=ME_HARMONICCONTENT; break;
		  case 72: control=ME_RELEASETIME; break;
		  case 73: control=ME_ATTACKTIME; break;
		  case 74: control=ME_BRIGHTNESS; break;
		  case 91: control=ME_REVERBERATION; break;
		  case 93: control=ME_CHORUSDEPTH; break;

		  case 120: control=ME_ALL_SOUNDS_OFF; break;
		  case 121: control=ME_RESET_CONTROLLERS; break;
		  case 123: control=ME_ALL_NOTES_OFF; break;

		    /* These should be the SCC-1 tone bank switch
		       commands. I don't know why there are two, or
		       why the latter only allows switching to bank 0.
		       Also, some MIDI files use 0 as some sort of
		       continuous controller. This will cause lots of
		       warnings about undefined tone banks. */
		  case 0: if (XG_System_On) control = ME_TONE_KIT; else control=ME_TONE_BANK; break;

		  case 32: if (XG_System_On) control = ME_TONE_BANK; break;

		  case 100: nrpn=0; rpn_msb[lastchan]=b; break;
		  case 101: nrpn=0; rpn_lsb[lastchan]=b; break;
		  case 99: nrpn=1; rpn_msb[lastchan]=b; break;
		  case 98: nrpn=1; rpn_lsb[lastchan]=b; break;
		    
		  case 6:
		    if (nrpn)
		      {
			if (rpn_msb[lastchan]==1) switch (rpn_lsb[lastchan])
			 {
#ifdef tplus
			   case 0x08: control=ME_VIBRATO_RATE; break;
			   case 0x09: control=ME_VIBRATO_DEPTH; break;
			   case 0x0a: control=ME_VIBRATO_DELAY; break;
#endif
			   case 0x20: control=ME_BRIGHTNESS; break;
			   case 0x21: control=ME_HARMONICCONTENT; break;
			/*
			   case 0x63: envelope attack rate
			   case 0x64: envelope decay rate
			   case 0x66: envelope release rate
			*/
			 }
			else switch (rpn_msb[lastchan])
			 {
			/*
			   case 0x14: filter cutoff frequency
			   case 0x15: filter resonance
			   case 0x16: envelope attack rate
			   case 0x17: envelope decay rate
			   case 0x18: pitch coarse
			   case 0x19: pitch fine
			*/
			   case 0x1a: drumvolume[lastchan][0x7f & rpn_lsb[lastchan]] = b; break;
			   case 0x1c:
			     if (!b) b=(int) (127.0*rand()/(RAND_MAX));
			     drumpanpot[lastchan][0x7f & rpn_lsb[lastchan]] = b;
			     break;
			   case 0x1d: drumreverberation[lastchan][0x7f & rpn_lsb[lastchan]] = b; break;
			   case 0x1e: drumchorusdepth[lastchan][0x7f & rpn_lsb[lastchan]] = b; break;
			/*
			   case 0x1f: variation send level
			*/
			 }

			ctl->cmsg(CMSG_INFO, VERB_DEBUG, 
				  "(Data entry (MSB) for NRPN %02x,%02x: %ld)",
				  rpn_msb[lastchan], rpn_lsb[lastchan],
				  b);
			break;
		      }
		    
		    switch((rpn_msb[lastchan]<<8) | rpn_lsb[lastchan])
		      {
		      case 0x0000: /* Pitch bend sensitivity */
			control=ME_PITCH_SENS;
			break;

		      case 0x7F7F: /* RPN reset */
			/* reset pitch bend sensitivity to 2 */
			MIDIEVENT(at, ME_PITCH_SENS, lastchan, 2, 0);

		      default:
			ctl->cmsg(CMSG_INFO, VERB_DEBUG, 
				  "(Data entry (MSB) for RPN %02x,%02x: %ld)",
				  rpn_msb[lastchan], rpn_lsb[lastchan],
				  b);
			break;
		      }
		    break;
		    
		  default:
		    ctl->cmsg(CMSG_INFO, VERB_DEBUG, 
			      "(Control %d: %d)", a, b);
		    break;
		  }
		if (control != 255)
		  { 
		    MIDIEVENT(at, control, lastchan, b, 0); 
		  }
	      }
	      break;

	    case 4: /* Program change */
	      a &= 0x7f;
	      MIDIEVENT(at, ME_PROGRAM, lastchan, a, 0);

	    case 5: /* Channel pressure - NOT IMPLEMENTED */
	      break;

	    case 6: /* Pitch wheel */
	      SDL_RWread(rw,&b, 1,1);
	      b &= 0x7F;
	      MIDIEVENT(at, ME_PITCHWHEEL, lastchan, a, b);

	    default: 
	      ctl->cmsg(CMSG_ERROR, VERB_NORMAL, 
		   "*** Can't happen: status 0x%02X, channel 0x%02X",
		   laststatus, lastchan);
	      break;
	    }
	}
    }
  
  return new;
}

#undef MIDIEVENT

/* Read a midi track into the linked list, either merging with any previous
   tracks or appending to them. */
static int read_track(int append)
{
  MidiEventList *meep;
  MidiEventList *next, *new;
  int32 len;
  char tmp[4];

  meep=evlist;
  if (append && meep)
    {
      /* find the last event in the list */
      for (; meep->next; meep=meep->next)
	;
      at=meep->event.time;
    }
  else
    at=0;

  /* Check the formalities */
  if ((SDL_RWread(rw,tmp,1,4) != 4) || (SDL_RWread(rw,&len,4,1) != 1))
    {
      ctl->cmsg(CMSG_ERROR, VERB_NORMAL,
	   "%s: Can't read track header.", current_filename);
      return -1;
    }
  len=BE_LONG(len);

  if (memcmp(tmp, "MTrk", 4))
    {
      ctl->cmsg(CMSG_ERROR, VERB_NORMAL,
	   "%s: Corrupt MIDI file.", current_filename);
      return -2;
    }

  for (;;)
    {
      if (!(new=read_midi_event())) /* Some kind of error  */
	return -2;

      if (new==MAGIC_EOT) /* End-of-track Hack. */
	{
	  return 0;
	}

      next=meep->next;
      while (next && (next->event.time < new->event.time))
	{
	  meep=next;
	  next=meep->next;
	}
	  
      new->next=next;
      meep->next=new;

      event_count++; /* Count the event. (About one?) */
      meep=new;
    }
}

/* Free the linked event list from memory. */
static void free_midi_list(void)
{
  MidiEventList *meep, *next;
  if (!(meep=evlist)) return;
  while (meep)
    {
      next=meep->next;
      free(meep);
      meep=next;
    }
  evlist=0;
}


static void xremap_percussion(int *banknumpt, int *this_notept, int this_kit) {
        int i, newmap;
        int banknum = *banknumpt;
        int this_note = *this_notept;
        int newbank, newnote;

        if (this_kit != 127 && this_kit != 126) return;

        for (i = 0; i < XMAPMAX; i++) {
                newmap = xmap[i][0];
                if (!newmap) return;
                if (this_kit == 127 && newmap != XGDRUM) continue;
                if (this_kit == 126 && newmap != SFXDRUM1) continue;
                if (xmap[i][1] != banknum) continue;
                if (xmap[i][3] != this_note) continue;
                newbank = xmap[i][2];
                newnote = xmap[i][4];
                if (newbank == banknum && newnote == this_note) return;
                if (!drumset[newbank]) return;
                *banknumpt = newbank;
                *this_notept = newnote;
                return;
        }
}

/* Allocate an array of MidiEvents and fill it from the linked list of
   events, marking used instruments for loading. Convert event times to
   samples: handle tempo changes. Strip unnecessary events from the list.
   Free the linked list. */
static MidiEvent *groom_list(int32 divisions,int32 *eventsp,int32 *samplesp)
{
  MidiEvent *groomed_list, *lp;
  MidiEventList *meep;
  int32 i, our_event_count, tempo, skip_this_event, new_value;
  int32 sample_cum, samples_to_do, at, st, dt, counting_time;

  int current_bank[MAXCHAN], current_banktype[MAXCHAN], current_set[MAXCHAN],
    current_kit[MAXCHAN], current_program[MAXCHAN];
  /* Or should each bank have its own current program? */
  int dset, dnote, drumsflag, mprog;

  for (i=0; i<MAXCHAN; i++)
    {
      current_bank[i]=0;
      current_banktype[i]=0;
      current_set[i]=0;
      current_kit[i]=channel[i].kit;
      current_program[i]=default_program;
    }

  tempo=500000;
  compute_sample_increment(tempo, divisions);

  /* This may allocate a bit more than we need */
  groomed_list=lp=safe_malloc(sizeof(MidiEvent) * (event_count+1));
  meep=evlist;

  our_event_count=0;
  st=at=sample_cum=0;
  counting_time=2; /* We strip any silence before the first NOTE ON. */

  for (i=0; i<event_count; i++)
    {
      skip_this_event=0;
      ctl->cmsg(CMSG_INFO, VERB_DEBUG_SILLY,
		"%6d: ch %2d: event %d (%d,%d)",
		meep->event.time, meep->event.channel + 1,
		meep->event.type, meep->event.a, meep->event.b);

      if (meep->event.type==ME_TEMPO)
	{
	  tempo=
	    meep->event.channel + meep->event.b * 256 + meep->event.a * 65536;
	  compute_sample_increment(tempo, divisions);
	  skip_this_event=1;
	}
      else if ((quietchannels & (1<<meep->event.channel)))
	skip_this_event=1;
      else switch (meep->event.type)
	{
	case ME_PROGRAM:

	  if (current_kit[meep->event.channel])
	    {
	      if (current_kit[meep->event.channel]==126)
		{
		  /* note request for 2nd sfx rhythm kit */
		  if (meep->event.a && drumset[SFXDRUM2])
		  {
			 current_kit[meep->event.channel]=125;
			 current_set[meep->event.channel]=SFXDRUM2;
		         new_value=SFXDRUM2;
		  }
		  else if (!meep->event.a && drumset[SFXDRUM1])
		  {
			 current_set[meep->event.channel]=SFXDRUM1;
		         new_value=SFXDRUM1;
		  }
		  else
		  {
		  	ctl->cmsg(CMSG_WARNING, VERB_VERBOSE,
		       		"XG SFX drum set is undefined");
			skip_this_event=1;
		  	break;
		  }
		}
	      if (drumset[meep->event.a]) /* Is this a defined drumset? */
		new_value=meep->event.a;
	      else
		{
		  ctl->cmsg(CMSG_WARNING, VERB_VERBOSE,
		       "Drum set %d is undefined", meep->event.a);
		  if (drumset[0])
		      new_value=meep->event.a=0;
		  else
		    {
			skip_this_event=1;
			break;
		    }
		}
	      if (current_set[meep->event.channel] != new_value)
		current_set[meep->event.channel]=new_value;
	      else 
		skip_this_event=1;
	    }
	  else
	    {
	      new_value=meep->event.a;
	      if ((current_program[meep->event.channel] != SPECIAL_PROGRAM)
		  && (current_program[meep->event.channel] != new_value))
		current_program[meep->event.channel] = new_value;
	      else
		skip_this_event=1;
	    }
	  break;

	case ME_NOTEON:
	  if (counting_time)
	    counting_time=1;

	  drumsflag = current_kit[meep->event.channel];

	  if (drumsflag) /* percussion channel? */
	    {
	      dset = current_set[meep->event.channel];
	      dnote=meep->event.a;
	      if (XG_System_On) xremap_percussion(&dset, &dnote, drumsflag);

	      /*if (current_config_pc42b) pcmap(&dset, &dnote, &mprog, &drumsflag);*/

	     if (drumsflag)
	     {
	      /* Mark this instrument to be loaded */
	      if (!(drumset[dset]->tone[dnote].layer))
	       {
		drumset[dset]->tone[dnote].layer=
		    MAGIC_LOAD_INSTRUMENT;
	       }
	      else drumset[dset]->tone[dnote].last_used
		 = current_tune_number;
	      if (!channel[meep->event.channel].name) channel[meep->event.channel].name=
		    drumset[dset]->name;
	     }
	    }

	  if (!drumsflag) /* not percussion */
	    {
	      int chan=meep->event.channel;
	      int banknum;

	      if (current_banktype[chan]) banknum=SFXBANK;
	      else banknum=current_bank[chan];

	      mprog = current_program[chan];

	      if (mprog==SPECIAL_PROGRAM)
		break;

	      if (XG_System_On && banknum==SFXBANK && !tonebank[SFXBANK] && tonebank[120]) 
		      banknum = 120;

	      /*if (current_config_pc42b) pcmap(&banknum, &dnote, &mprog, &drumsflag);*/

	     if (drumsflag)
	     {
	      /* Mark this instrument to be loaded */
	      if (!(drumset[dset]->tone[dnote].layer))
	       {
		drumset[dset]->tone[dnote].layer=MAGIC_LOAD_INSTRUMENT;
	       }
	      else drumset[dset]->tone[dnote].last_used = current_tune_number;
	      if (!channel[meep->event.channel].name) channel[meep->event.channel].name=
		    drumset[dset]->name;
	     }
	     if (!drumsflag)
	     {
	      /* Mark this instrument to be loaded */
	      if (!(tonebank[banknum]->tone[mprog].layer))
		{
		  tonebank[banknum]->tone[mprog].layer=MAGIC_LOAD_INSTRUMENT;
		}
	      else tonebank[banknum]->tone[mprog].last_used = current_tune_number;
	      if (!channel[meep->event.channel].name) channel[meep->event.channel].name=
		    tonebank[banknum]->tone[mprog].name;
	     }
	    }
	  break;

	case ME_TONE_KIT:
	  if (!meep->event.a || meep->event.a == 127)
	    {
	      new_value=meep->event.a;
	      if (current_kit[meep->event.channel] != new_value)
		current_kit[meep->event.channel]=new_value;
	      else 
		skip_this_event=1;
	      break;
	    }
	  else if (meep->event.a == 126)
	    {
	      if (drumset[SFXDRUM1]) /* Is this a defined tone bank? */
	        new_value=meep->event.a;
	      else
		{
	          ctl->cmsg(CMSG_WARNING, VERB_VERBOSE,
		   "XG rhythm kit %d is undefined", meep->event.a);
	          skip_this_event=1;
	          break;
		}
	      current_set[meep->event.channel]=SFXDRUM1;
	      current_kit[meep->event.channel]=new_value;
	      break;
	    }
	  else if (meep->event.a != SFX_BANKTYPE)
	    {
	      ctl->cmsg(CMSG_WARNING, VERB_VERBOSE,
		   "XG kit %d is impossible", meep->event.a);
	      skip_this_event=1;
	      break;
	    }

	  if (current_kit[meep->event.channel])
	    {
	      skip_this_event=1;
	      break;
	    }
	  if (tonebank[SFXBANK] || tonebank[120]) /* Is this a defined tone bank? */
	    new_value=SFX_BANKTYPE;
	  else 
	    {
	      ctl->cmsg(CMSG_WARNING, VERB_VERBOSE,
		   "XG Sfx bank is undefined");
	      skip_this_event=1;
	      break;
	    }
	  if (current_banktype[meep->event.channel]!=new_value)
	    current_banktype[meep->event.channel]=new_value;
	  else
	    skip_this_event=1;
	  break;

	case ME_TONE_BANK:
	  if (current_kit[meep->event.channel])
	    {
	      skip_this_event=1;
	      break;
	    }
	  if (XG_System_On && meep->event.a > 0 && meep->event.a < 48) {
	      channel[meep->event.channel].variationbank=meep->event.a;
	      ctl->cmsg(CMSG_WARNING, VERB_VERBOSE,
		   "XG variation bank %d", meep->event.a);
	      new_value=meep->event.a=0;
	  }
	  else if (tonebank[meep->event.a]) /* Is this a defined tone bank? */
	    new_value=meep->event.a;
	  else 
	    {
	      ctl->cmsg(CMSG_WARNING, VERB_VERBOSE,
		   "Tone bank %d is undefined", meep->event.a);
	      new_value=meep->event.a=0;
	    }

	  if (current_bank[meep->event.channel]!=new_value)
	    current_bank[meep->event.channel]=new_value;
	  else
	    skip_this_event=1;
	  break;

	case ME_HARMONICCONTENT:
	  channel[meep->event.channel].harmoniccontent=meep->event.a;
	  break;
	case ME_BRIGHTNESS:
	  channel[meep->event.channel].brightness=meep->event.a;
	  break;

	}

      /* Recompute time in samples*/
      if ((dt=meep->event.time - at) && !counting_time)
	{
	  samples_to_do=sample_increment * dt;
	  sample_cum += sample_correction * dt;
	  if (sample_cum & 0xFFFF0000)
	    {
	      samples_to_do += ((sample_cum >> 16) & 0xFFFF);
	      sample_cum &= 0x0000FFFF;
	    }
	  st += samples_to_do;
	}
      else if (counting_time==1) counting_time=0;
      if (!skip_this_event)
	{
	  /* Add the event to the list */
	  *lp=meep->event;
	  lp->time=st;
	  lp++;
	  our_event_count++;
	}
      at=meep->event.time;
      meep=meep->next;
    }
  /* Add an End-of-Track event */
  lp->time=st;
  lp->type=ME_EOT;
  our_event_count++;
  free_midi_list();
  
  *eventsp=our_event_count;
  *samplesp=st;
  return groomed_list;
}

MidiEvent *read_midi_file(SDL_RWops *mrw, int32 *count, int32 *sp)
{
  int32 len, divisions;
  int16 format, tracks, divisions_tmp;
  int i;
  char tmp[4];

  rw = mrw;
  event_count=0;
  at=0;
  evlist=0;

  GM_System_On=GS_System_On=XG_System_On=0;
  /* vol_table = def_vol_table; */
  XG_System_reverb_type=XG_System_chorus_type=XG_System_variation_type=0;
  memset(&drumvolume,-1,sizeof(drumvolume));
  memset(&drumchorusdepth,-1,sizeof(drumchorusdepth));
  memset(&drumreverberation,-1,sizeof(drumreverberation));
  memset(&drumpanpot,NO_PANNING,sizeof(drumpanpot));

  for (i=0; i<MAXCHAN; i++)
     {
	if (ISDRUMCHANNEL(i)) channel[i].kit = 127;
	else channel[i].kit = 0;
	channel[i].brightness = 64;
	channel[i].harmoniccontent = 64;
	channel[i].variationbank = 0;
	channel[i].chorusdepth = 0;
	channel[i].reverberation = 0;
	channel[i].transpose = 0;
     }

past_riff:

  if ((SDL_RWread(rw,tmp,1,4) != 4) || (SDL_RWread(rw,&len,4,1) != 1))
    {
     /* if (ferror(fp))
	{
	  ctl->cmsg(CMSG_ERROR, VERB_NORMAL, "%s: %s", current_filename, 
	       strerror(errno));
	}
      else*/
	ctl->cmsg(CMSG_ERROR, VERB_NORMAL, 
	     "%s: Not a MIDI file!", current_filename);
      return 0;
    }
  len=BE_LONG(len);

  if (!memcmp(tmp, "RIFF", 4))
    {
      SDL_RWread(rw,tmp,1,12);
      goto past_riff;
    }
  if (memcmp(tmp, "MThd", 4) || len < 6)
    {
      ctl->cmsg(CMSG_ERROR, VERB_NORMAL,
	   "%s: Not a MIDI file!", current_filename);
      return 0;
    }

  SDL_RWread(rw,&format, 2, 1);
  SDL_RWread(rw,&tracks, 2, 1);
  SDL_RWread(rw,&divisions_tmp, 2, 1);
  format=BE_SHORT(format);
  tracks=BE_SHORT(tracks);
  track_info = tracks;
  curr_track = 0;
  curr_title_track = -1;
  divisions_tmp=BE_SHORT(divisions_tmp);

  if (divisions_tmp<0)
    {
      /* SMPTE time -- totally untested. Got a MIDI file that uses this? */
      divisions=
	(int32)(-(divisions_tmp/256)) * (int32)(divisions_tmp & 0xFF);
    }
  else divisions=(int32)(divisions_tmp);

  if (len > 6)
    {
      ctl->cmsg(CMSG_WARNING, VERB_NORMAL, 
	   "%s: MIDI file header size %ld bytes", 
	   current_filename, len);
      SDL_RWseek(rw, len-6, RW_SEEK_CUR); /* skip the excess */
    }
  if (format<0 || format >2)
    {
      ctl->cmsg(CMSG_ERROR, VERB_NORMAL, 
	   "%s: Unknown MIDI file format %d", current_filename, format);
      return 0;
    }
  ctl->cmsg(CMSG_INFO, VERB_VERBOSE, 
       "Format: %d  Tracks: %d  Divisions: %d", format, tracks, divisions);

  /* Put a do-nothing event first in the list for easier processing */
  evlist=safe_malloc(sizeof(MidiEventList));
  evlist->event.time=0;
  evlist->event.type=ME_NONE;
  evlist->next=0;
  event_count++;

  switch(format)
    {
    case 0:
      if (read_track(0))
	{
	  free_midi_list();
	  return 0;
	}
      else curr_track++;
      break;

    case 1:
      for (i=0; i<tracks; i++)
	if (read_track(0))
	  {
	    free_midi_list();
	    return 0;
	  }
      break;

    case 2: /* We simply play the tracks sequentially */
      for (i=0; i<tracks; i++)
	if (read_track(1))
	  {
	    free_midi_list();
	    return 0;
	  }
         else curr_track++;
      break;
    }
  return groom_list(divisions, count, sp);
}
