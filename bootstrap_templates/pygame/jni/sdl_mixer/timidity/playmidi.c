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

    playmidi.c -- random stuff in need of rearrangement

*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <SDL_rwops.h>

#include "config.h"
#include "common.h"
#include "instrum.h"
#include "playmidi.h"
#include "readmidi.h"
#include "output.h"
#include "mix.h"
#include "ctrlmode.h"
#include "timidity.h"

#include "tables.h"


static int opt_expression_curve = 2;
static int opt_volume_curve = 2;
static int opt_stereo_surround = 0;


Channel channel[MAXCHAN];
Voice voice[MAX_VOICES];
signed char drumvolume[MAXCHAN][MAXNOTE];
signed char drumpanpot[MAXCHAN][MAXNOTE];
signed char drumreverberation[MAXCHAN][MAXNOTE];
signed char drumchorusdepth[MAXCHAN][MAXNOTE];

int
    voices=DEFAULT_VOICES;

int32
    control_ratio=0,
    amplification=DEFAULT_AMPLIFICATION;

FLOAT_T
    master_volume;

int32 drumchannels=DEFAULT_DRUMCHANNELS;
int adjust_panning_immediately=0;

struct _MidiSong {
	int32 samples;
	MidiEvent *events;
};
static int midi_playing = 0;
static int32 lost_notes, cut_notes;
static int32 *buffer_pointer;
static int32 buffered_count;
extern int32 *common_buffer;
extern resample_t *resample_buffer; /* to free it on Timidity_Close */

static MidiEvent *event_list, *current_event;
static int32 sample_count, current_sample;

int GM_System_On=0;
int XG_System_On=0;
int GS_System_On=0;
int XG_System_reverb_type;
int XG_System_chorus_type;
int XG_System_variation_type;


static void adjust_amplification(void)
{ 
  master_volume = (FLOAT_T)(amplification) / (FLOAT_T)100.0;
  master_volume /= 2;
}


static void adjust_master_volume(int32 vol)
{ 
  master_volume = (double)(vol*amplification) / 1638400.0L;
  master_volume /= 2;
}


static void reset_voices(void)
{
  int i;
  for (i=0; i<MAX_VOICES; i++)
    voice[i].status=VOICE_FREE;
}

/* Process the Reset All Controllers event */
static void reset_controllers(int c)
{
  channel[c].volume=90; /* Some standard says, although the SCC docs say 0. */
  channel[c].expression=127; /* SCC-1 does this. */
  channel[c].sustain=0;
  channel[c].pitchbend=0x2000;
  channel[c].pitchfactor=0; /* to be computed */

  channel[c].reverberation = 0;
  channel[c].chorusdepth = 0;
}

static void redraw_controllers(int c)
{
  ctl->volume(c, channel[c].volume);
  ctl->expression(c, channel[c].expression);
  ctl->sustain(c, channel[c].sustain);
  ctl->pitch_bend(c, channel[c].pitchbend);
}

static void reset_midi(void)
{
  int i;
  for (i=0; i<MAXCHAN; i++)
    {
      reset_controllers(i);
      /* The rest of these are unaffected by the Reset All Controllers event */
      channel[i].program=default_program;
      channel[i].panning=NO_PANNING;
      channel[i].pitchsens=2;
      channel[i].bank=0; /* tone bank or drum set */
      channel[i].harmoniccontent=64,
      channel[i].releasetime=64,
      channel[i].attacktime=64,
      channel[i].brightness=64,
      channel[i].sfx=0;
    }
  reset_voices();
}

static void select_sample(int v, Instrument *ip)
{
  int32 f, cdiff, diff, midfreq;
  int s,i;
  Sample *sp, *closest;

  s=ip->samples;
  sp=ip->sample;

  if (s==1)
    {
      voice[v].sample=sp;
      return;
    }

  f=voice[v].orig_frequency;
  /* 
     No suitable sample found! We'll select the sample whose root
     frequency is closest to the one we want. (Actually we should
     probably convert the low, high, and root frequencies to MIDI note
     values and compare those.) */

  cdiff=0x7FFFFFFF;
  closest=sp=ip->sample;
  midfreq = (sp->low_freq + sp->high_freq) / 2;
  for(i=0; i<s; i++)
    {
      diff=sp->root_freq - f;
  /*  But the root freq. can perfectly well lie outside the keyrange
   *  frequencies, so let's try:
   */
      /* diff=midfreq - f; */
      if (diff<0) diff=-diff;
      if (diff<cdiff)
	{
	  cdiff=diff;
	  closest=sp;
	}
      sp++;
    }
  voice[v].sample=closest;
  return;
}



static void select_stereo_samples(int v, InstrumentLayer *lp)
{
  Instrument *ip;
  InstrumentLayer *nlp, *bestvel;
  int diffvel, midvel, mindiff;

/* select closest velocity */
  bestvel = lp;
  mindiff = 500;
  for (nlp = lp; nlp; nlp = nlp->next) {
	midvel = (nlp->hi + nlp->lo)/2;
	if (!midvel) diffvel = 127;
	else if (voice[v].velocity < nlp->lo || voice[v].velocity > nlp->hi)
		diffvel = 200;
	else diffvel = voice[v].velocity - midvel;
	if (diffvel < 0) diffvel = -diffvel;
	if (diffvel < mindiff) {
		mindiff = diffvel;
		bestvel = nlp;
	}
  }
  ip = bestvel->instrument;

  if (ip->right_sample) {
    ip->sample = ip->right_sample;
    ip->samples = ip->right_samples;
    select_sample(v, ip);
    voice[v].right_sample = voice[v].sample;
  }
  else voice[v].right_sample = 0;
  ip->sample = ip->left_sample;
  ip->samples = ip->left_samples;
  select_sample(v, ip);
}


static void recompute_freq(int v)
{
  int 
    sign=(voice[v].sample_increment < 0), /* for bidirectional loops */
    pb=channel[voice[v].channel].pitchbend;
  double a;
  
  if (!voice[v].sample->sample_rate)
    return;

  if (voice[v].vibrato_control_ratio)
    {
      /* This instrument has vibrato. Invalidate any precomputed
         sample_increments. */

      int i=VIBRATO_SAMPLE_INCREMENTS;
      while (i--)
	voice[v].vibrato_sample_increment[i]=0;
    }

  if (pb==0x2000 || pb<0 || pb>0x3FFF)
    voice[v].frequency=voice[v].orig_frequency;
  else
    {
      pb-=0x2000;
      if (!(channel[voice[v].channel].pitchfactor))
	{
	  /* Damn. Somebody bent the pitch. */
	  int32 i=pb*channel[voice[v].channel].pitchsens;
	  if (pb<0)
	    i=-i;
	  channel[voice[v].channel].pitchfactor=
	    (FLOAT_T)(bend_fine[(i>>5) & 0xFF] * bend_coarse[i>>13]);
	}
      if (pb>0)
	voice[v].frequency=
	  (int32)(channel[voice[v].channel].pitchfactor *
		  (double)(voice[v].orig_frequency));
      else
	voice[v].frequency=
	  (int32)((double)(voice[v].orig_frequency) /
		  channel[voice[v].channel].pitchfactor);
    }

  a = FSCALE(((double)(voice[v].sample->sample_rate) *
	      (double)(voice[v].frequency)) /
	     ((double)(voice[v].sample->root_freq) *
	      (double)(play_mode->rate)),
	     FRACTION_BITS);

  if (sign) 
    a = -a; /* need to preserve the loop direction */

  voice[v].sample_increment = (int32)(a);
}

static int expr_curve[128] = {
	7, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 10, 10, 10, 10, 11, 
	11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 14, 14, 14, 14, 15, 15, 
	15, 16, 16, 17, 17, 17, 18, 18, 19, 19, 19, 20, 20, 21, 21, 22, 
	22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 28, 28, 29, 30, 30, 31, 
	32, 32, 33, 34, 35, 35, 36, 37, 38, 39, 39, 40, 41, 42, 43, 44, 
	45, 46, 47, 48, 49, 50, 51, 53, 54, 55, 56, 57, 59, 60, 61, 63, 
	64, 65, 67, 68, 70, 71, 73, 75, 76, 78, 80, 82, 83, 85, 87, 89, 
	91, 93, 95, 97, 99, 102, 104, 106, 109, 111, 113, 116, 118, 121,
	124, 127 
};

static int panf(int pan, int speaker, int separation)
{
	int val;
	val = abs(pan - speaker);
	val = (val * 127) / separation;
	val = 127 - val;
	if (val < 0) val = 0;
	if (val > 127) val = 127;
	return expr_curve[val];
}


static int vcurve[128] = {
0,0,18,29,36,42,47,51,55,58,
60,63,65,67,69,71,73,74,76,77,
79,80,81,82,83,84,85,86,87,88,
89,90,91,92,92,93,94,95,95,96,
97,97,98,99,99,100,100,101,101,102,
103,103,104,104,105,105,106,106,106,107,
107,108,108,109,109,109,110,110,111,111,
111,112,112,112,113,113,114,114,114,115,
115,115,116,116,116,116,117,117,117,118,
118,118,119,119,119,119,120,120,120,120,
121,121,121,122,122,122,122,123,123,123,
123,123,124,124,124,124,125,125,125,125,
126,126,126,126,126,127,127,127
};

static void recompute_amp(int v)
{
  int32 tempamp;
  int chan = voice[v].channel;
  int panning = voice[v].panning;
  int vol = channel[chan].volume;
  int expr = channel[chan].expression;
  int vel = vcurve[voice[v].velocity];
  FLOAT_T curved_expression, curved_volume;

  if (channel[chan].kit)
   {
    int note = voice[v].sample->note_to_use;
    if (note>0 && drumvolume[chan][note]>=0) vol = drumvolume[chan][note];
    if (note>0 && drumpanpot[chan][note]>=0) panning = drumvolume[chan][note];
   }

  if (opt_expression_curve == 2) curved_expression = 127.0 * vol_table[expr];
  else if (opt_expression_curve == 1) curved_expression = 127.0 * expr_table[expr];
  else curved_expression = (FLOAT_T)expr;

  if (opt_volume_curve == 2) curved_volume = 127.0 * vol_table[vol];
  else if (opt_volume_curve == 1) curved_volume = 127.0 * expr_table[vol];
  else curved_volume = (FLOAT_T)vol;

  tempamp= (int32)((FLOAT_T)vel * curved_volume * curved_expression); /* 21 bits */

  /* TODO: use fscale */

  if (num_ochannels > 1)
    {
      if (panning > 60 && panning < 68)
	{
	  voice[v].panned=PANNED_CENTER;

	  if (num_ochannels == 6) voice[v].left_amp =
		FSCALENEG((double) (tempamp) * voice[v].sample->volume *
			    master_volume, 20);
	  else voice[v].left_amp=
	        FSCALENEG((double)(tempamp) * voice[v].sample->volume *
			    master_volume, 21);
	}
      else if (panning<5)
	{
	  voice[v].panned = PANNED_LEFT;

	  voice[v].left_amp=
	    FSCALENEG((double)(tempamp) * voice[v].sample->volume * master_volume,
		      20);
	}
      else if (panning>123)
	{
	  voice[v].panned = PANNED_RIGHT;

	  voice[v].left_amp= /* left_amp will be used */
	    FSCALENEG((double)(tempamp) * voice[v].sample->volume * master_volume,
		      20);
	}
      else
	{
	  FLOAT_T refv = (double)(tempamp) * voice[v].sample->volume * master_volume;
	  int wide_panning = 64;

	  if (num_ochannels == 4) wide_panning = 95;

	  voice[v].panned = PANNED_MYSTERY;
	  voice[v].lfe_amp = FSCALENEG(refv * 64, 27);

		switch (num_ochannels)
		{
		    case 2:
		      voice[v].lr_amp = 0;
		      voice[v].left_amp = FSCALENEG(refv * (128-panning), 27);
		      voice[v].ce_amp = 0;
		      voice[v].right_amp = FSCALENEG(refv * panning, 27);
		      voice[v].rr_amp = 0;
		      break;
		    case 4:
		      voice[v].lr_amp = FSCALENEG(refv * panf(panning, 0, wide_panning), 27);
		      voice[v].left_amp = FSCALENEG(refv * panf(panning, 32, wide_panning), 27);
		      voice[v].ce_amp = 0;
		      voice[v].right_amp = FSCALENEG(refv * panf(panning, 95, wide_panning), 27);
		      voice[v].rr_amp = FSCALENEG(refv * panf(panning, 128, wide_panning), 27);
		      break;
		    case 6:
		      voice[v].lr_amp = FSCALENEG(refv * panf(panning, 0, wide_panning), 27);
		      voice[v].left_amp = FSCALENEG(refv * panf(panning, 32, wide_panning), 27);
		      voice[v].ce_amp = FSCALENEG(refv * panf(panning, 64, wide_panning), 27);
		      voice[v].right_amp = FSCALENEG(refv * panf(panning, 95, wide_panning), 27);
		      voice[v].rr_amp = FSCALENEG(refv * panf(panning, 128, wide_panning), 27);
		      break;
		}

	}
    }
  else
    {
      voice[v].panned=PANNED_CENTER;

      voice[v].left_amp=
	FSCALENEG((double)(tempamp) * voice[v].sample->volume * master_volume,
		  21);
    }
}


#define NOT_CLONE 0
#define STEREO_CLONE 1
#define REVERB_CLONE 2
#define CHORUS_CLONE 3


/* just a variant of note_on() */
static int vc_alloc(int j)
{
  int i=voices; 

  while (i--)
    {
      if (i == j) continue;
      if (voice[i].status & VOICE_FREE) {
	return i;
      }
    }
  return -1;
}

static void kill_note(int i);

static void kill_others(int i)
{
  int j=voices; 

  if (!voice[i].sample->exclusiveClass) return;

  while (j--)
    {
      if (voice[j].status & (VOICE_FREE|VOICE_OFF|VOICE_DIE)) continue;
      if (i == j) continue;
      if (voice[i].channel != voice[j].channel) continue;
      if (voice[j].sample->note_to_use)
      {
    	if (voice[j].sample->exclusiveClass != voice[i].sample->exclusiveClass) continue;
        kill_note(j);
      }
    }
}


static void clone_voice(Instrument *ip, int v, MidiEvent *e, int clone_type, int variationbank)
{
  int w, played_note, chorus=0, reverb=0, milli;
  int chan = voice[v].channel;

  if (clone_type == STEREO_CLONE) {
	if (!voice[v].right_sample && variationbank != 3) return;
	if (variationbank == 6) return;
  }

  if (channel[chan].kit) {
	reverb = drumreverberation[chan][voice[v].note];
	chorus = drumchorusdepth[chan][voice[v].note];
  }
  else {
	reverb = channel[chan].reverberation;
	chorus = channel[chan].chorusdepth;
  }

  if (clone_type == REVERB_CLONE) chorus = 0;
  else if (clone_type == CHORUS_CLONE) reverb = 0;
  else if (clone_type == STEREO_CLONE) reverb = chorus = 0;

  if (reverb > 127) reverb = 127;
  if (chorus > 127) chorus = 127;

  if (clone_type == CHORUS_CLONE) {
	 if (variationbank == 32) chorus = 30;
	 else if (variationbank == 33) chorus = 60;
	 else if (variationbank == 34) chorus = 90;
  }

  chorus /= 2;  /* This is an ad hoc adjustment. */

  if (!reverb && !chorus && clone_type != STEREO_CLONE) return;

  if ( (w = vc_alloc(v)) < 0 ) return;

  voice[w] = voice[v];
  if (clone_type==STEREO_CLONE) voice[v].clone_voice = w;
  voice[w].clone_voice = v;
  voice[w].clone_type = clone_type;

  voice[w].sample = voice[v].right_sample;
  voice[w].velocity= e->b;

  milli = play_mode->rate/1000;

  if (clone_type == STEREO_CLONE) {
    int left, right, leftpan, rightpan;
    int panrequest = voice[v].panning;
    if (variationbank == 3) {
	voice[v].panning = 0;
	voice[w].panning = 127;
    }
    else {
	if (voice[v].sample->panning > voice[w].sample->panning) {
	  left = w;
	  right = v;
	}
	else {
	  left = v;
	  right = w;
	}
#define INSTRUMENT_SEPARATION 12
	leftpan = panrequest - INSTRUMENT_SEPARATION / 2;
	rightpan = leftpan + INSTRUMENT_SEPARATION;
	if (leftpan < 0) {
		leftpan = 0;
		rightpan = leftpan + INSTRUMENT_SEPARATION;
	}
	if (rightpan > 127) {
		rightpan = 127;
		leftpan = rightpan - INSTRUMENT_SEPARATION;
	}
	voice[left].panning = leftpan;
	voice[right].panning = rightpan;
	voice[right].echo_delay = 20 * milli;
    }
  }

  voice[w].volume = voice[w].sample->volume;

  if (reverb) {
	if (opt_stereo_surround) {
		if (voice[w].panning > 64) voice[w].panning = 127;
		else voice[w].panning = 0;
	}
	else {
		if (voice[v].panning < 64) voice[w].panning = 64 + reverb/2;
		else voice[w].panning = 64 - reverb/2;
	}

/* try 98->99 for melodic instruments ? (bit much for percussion) */
	voice[w].volume *= vol_table[(127-reverb)/8 + 98];

	voice[w].echo_delay += reverb * milli;
	voice[w].envelope_rate[DECAY] *= 2;
	voice[w].envelope_rate[RELEASE] /= 2;

	if (XG_System_reverb_type >= 0) {
	    int subtype = XG_System_reverb_type & 0x07;
	    int rtype = XG_System_reverb_type >>3;
	    switch (rtype) {
		case 0: /* no effect */
		  break;
		case 1: /* hall */
		  if (subtype) voice[w].echo_delay += 100 * milli;
		  break;
		case 2: /* room */
		  voice[w].echo_delay /= 2;
		  break;
		case 3: /* stage */
		  voice[w].velocity = voice[v].velocity;
		  break;
		case 4: /* plate */
		  voice[w].panning = voice[v].panning;
		  break;
		case 16: /* white room */
		  voice[w].echo_delay = 0;
		  break;
		case 17: /* tunnel */
		  voice[w].echo_delay *= 2;
		  voice[w].velocity /= 2;
		  break;
		case 18: /* canyon */
		  voice[w].echo_delay *= 2;
		  break;
		case 19: /* basement */
		  voice[w].velocity /= 2;
		  break;
	        default: break;
	    }
	}
  }
  played_note = voice[w].sample->note_to_use;
  if (!played_note) {
	played_note = e->a & 0x7f;
	if (variationbank == 35) played_note += 12;
	else if (variationbank == 36) played_note -= 12;
	else if (variationbank == 37) played_note += 7;
	else if (variationbank == 36) played_note -= 7;
  }
#if 0
  played_note = ( (played_note - voice[w].sample->freq_center) * voice[w].sample->freq_scale ) / 1024 +
		voice[w].sample->freq_center;
#endif
  voice[w].note = played_note;
  voice[w].orig_frequency = freq_table[played_note];

  if (chorus) {
	if (opt_stereo_surround) {
	  if (voice[v].panning < 64) voice[w].panning = voice[v].panning + 32;
	  else voice[w].panning = voice[v].panning - 32;
	}

	if (!voice[w].vibrato_control_ratio) {
		voice[w].vibrato_control_ratio = 100;
		voice[w].vibrato_depth = 6;
		voice[w].vibrato_sweep = 74;
	}
	voice[w].volume *= 0.40;
	voice[v].volume = voice[w].volume;
	recompute_amp(v);
        apply_envelope_to_amp(v);
	voice[w].vibrato_sweep = chorus/2;
	voice[w].vibrato_depth /= 2;
	if (!voice[w].vibrato_depth) voice[w].vibrato_depth = 2;
	voice[w].vibrato_control_ratio /= 2;
	voice[w].echo_delay += 30 * milli;

	if (XG_System_chorus_type >= 0) {
	    int subtype = XG_System_chorus_type & 0x07;
	    int chtype = 0x0f & (XG_System_chorus_type >> 3);
	    switch (chtype) {
		case 0: /* no effect */
		  break;
		case 1: /* chorus */
		  chorus /= 3;
		  if(channel[ voice[w].channel ].pitchbend + chorus < 0x2000)
            		voice[w].orig_frequency =
				(uint32)( (FLOAT_T)voice[w].orig_frequency * bend_fine[chorus] );
        	  else voice[w].orig_frequency =
			(uint32)( (FLOAT_T)voice[w].orig_frequency / bend_fine[chorus] );
		  if (subtype) voice[w].vibrato_depth *= 2;
		  break;
		case 2: /* celeste */
		  voice[w].orig_frequency += (voice[w].orig_frequency/128) * chorus;
		  break;
		case 3: /* flanger */
		  voice[w].vibrato_control_ratio = 10;
		  voice[w].vibrato_depth = 100;
		  voice[w].vibrato_sweep = 8;
		  voice[w].echo_delay += 200 * milli;
		  break;
		case 4: /* symphonic : cf Children of the Night /128 bad, /1024 ok */
		  voice[w].orig_frequency += (voice[w].orig_frequency/512) * chorus;
		  voice[v].orig_frequency -= (voice[v].orig_frequency/512) * chorus;
		  recompute_freq(v);
		  break;
		case 8: /* phaser */
		  break;
	      default:
		  break;
	    }
	}
	else {
	    chorus /= 3;
	    if(channel[ voice[w].channel ].pitchbend + chorus < 0x2000)
          	voice[w].orig_frequency =
			(uint32)( (FLOAT_T)voice[w].orig_frequency * bend_fine[chorus] );
            else voice[w].orig_frequency =
		(uint32)( (FLOAT_T)voice[w].orig_frequency / bend_fine[chorus] );
	}
  }
#if 0
  voice[w].loop_start = voice[w].sample->loop_start;
  voice[w].loop_end = voice[w].sample->loop_end;
#endif
  voice[w].echo_delay_count = voice[w].echo_delay;
  if (reverb) voice[w].echo_delay *= 2;

  recompute_freq(w);
  recompute_amp(w);
  if (voice[w].sample->modes & MODES_ENVELOPE)
    {
      /* Ramp up from 0 */
      voice[w].envelope_stage=ATTACK;
      voice[w].modulation_stage=ATTACK;
      voice[w].envelope_volume=0;
      voice[w].modulation_volume=0;
      voice[w].control_counter=0;
      voice[w].modulation_counter=0;
      recompute_envelope(w);
      /*recompute_modulation(w);*/
    }
  else
    {
      voice[w].envelope_increment=0;
      voice[w].modulation_increment=0;
    }
  apply_envelope_to_amp(w);
}


static void xremap(int *banknumpt, int *this_notept, int this_kit) {
	int i, newmap;
	int banknum = *banknumpt;
	int this_note = *this_notept;
	int newbank, newnote;

	if (!this_kit) {
		if (banknum == SFXBANK && tonebank[SFXBANK]) return;
		if (banknum == SFXBANK && tonebank[120]) *banknumpt = 120;
		return;
	}

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
		if (!drumset[newbank]->tone[newnote].layer) return;
		if (drumset[newbank]->tone[newnote].layer == MAGIC_LOAD_INSTRUMENT) return;
		*banknumpt = newbank;
		*this_notept = newnote;
		return;
	}
}


static void start_note(MidiEvent *e, int i)
{
  InstrumentLayer *lp;
  Instrument *ip;
  int j, banknum, ch=e->channel;
  int played_note, drumpan=NO_PANNING;
  int32 rt;
  int attacktime, releasetime, decaytime, variationbank;
  int brightness = channel[ch].brightness;
  int harmoniccontent = channel[ch].harmoniccontent;
  int this_note = e->a;
  int this_velocity = e->b;
  int drumsflag = channel[ch].kit;
  int this_prog = channel[ch].program;

  if (channel[ch].sfx) banknum=channel[ch].sfx;
  else banknum=channel[ch].bank;

  voice[i].velocity=this_velocity;

  if (XG_System_On) xremap(&banknum, &this_note, drumsflag);
  /*   if (current_config_pc42b) pcmap(&banknum, &this_note, &this_prog, &drumsflag); */

  if (drumsflag)
    {
      if (!(lp=drumset[banknum]->tone[this_note].layer))
	{
	  if (!(lp=drumset[0]->tone[this_note].layer))
	    return; /* No instrument? Then we can't play. */
	}
      ip = lp->instrument;
      if (ip->type == INST_GUS && ip->samples != 1)
	{
	  ctl->cmsg(CMSG_WARNING, VERB_VERBOSE, 
	       "Strange: percussion instrument with %d samples!", ip->samples);
	}

      if (ip->sample->note_to_use) /* Do we have a fixed pitch? */
	{
	  voice[i].orig_frequency=freq_table[(int)(ip->sample->note_to_use)];
	  drumpan=drumpanpot[ch][(int)ip->sample->note_to_use];
	}
      else
	voice[i].orig_frequency=freq_table[this_note & 0x7F];

    }
  else
    {
      if (channel[ch].program==SPECIAL_PROGRAM)
	lp=default_instrument;
      else if (!(lp=tonebank[channel[ch].bank]->
		 tone[channel[ch].program].layer))
	{
	  if (!(lp=tonebank[0]->tone[this_prog].layer))
	    return; /* No instrument? Then we can't play. */
	}
      ip = lp->instrument;
      if (ip->sample->note_to_use) /* Fixed-pitch instrument? */
	voice[i].orig_frequency=freq_table[(int)(ip->sample->note_to_use)];
      else
	voice[i].orig_frequency=freq_table[this_note & 0x7F];
    }

    select_stereo_samples(i, lp);

  voice[i].starttime = e->time;
  played_note = voice[i].sample->note_to_use;

  if (!played_note || !drumsflag) played_note = this_note & 0x7f;
#if 0
  played_note = ( (played_note - voice[i].sample->freq_center) * voice[i].sample->freq_scale ) / 1024 +
		voice[i].sample->freq_center;
#endif
  voice[i].status=VOICE_ON;
  voice[i].channel=ch;
  voice[i].note=played_note;
  voice[i].velocity=this_velocity;
  voice[i].sample_offset=0;
  voice[i].sample_increment=0; /* make sure it isn't negative */

  voice[i].tremolo_phase=0;
  voice[i].tremolo_phase_increment=voice[i].sample->tremolo_phase_increment;
  voice[i].tremolo_sweep=voice[i].sample->tremolo_sweep_increment;
  voice[i].tremolo_sweep_position=0;

  voice[i].vibrato_sweep=voice[i].sample->vibrato_sweep_increment;
  voice[i].vibrato_sweep_position=0;
  voice[i].vibrato_depth=voice[i].sample->vibrato_depth;
  voice[i].vibrato_control_ratio=voice[i].sample->vibrato_control_ratio;
  voice[i].vibrato_control_counter=voice[i].vibrato_phase=0;
  voice[i].vibrato_delay = voice[i].sample->vibrato_delay;

  kill_others(i);

  for (j=0; j<VIBRATO_SAMPLE_INCREMENTS; j++)
    voice[i].vibrato_sample_increment[j]=0;


  attacktime = channel[ch].attacktime;
  releasetime = channel[ch].releasetime;
  decaytime = 64;
  variationbank = channel[ch].variationbank;

  switch (variationbank) {
	case  8:
		attacktime = 64+32;
		break;
	case 12:
		decaytime = 64-32;
		break;
	case 16:
		brightness = 64+16;
		break;
	case 17:
		brightness = 64+32;
		break;
	case 18:
		brightness = 64-16;
		break;
	case 19:
		brightness = 64-32;
		break;
	case 20:
		harmoniccontent = 64+16;
		break;
#if 0
	case 24:
		voice[i].modEnvToFilterFc=2.0;
      		voice[i].sample->cutoff_freq = 800;
		break;
	case 25:
		voice[i].modEnvToFilterFc=-2.0;
      		voice[i].sample->cutoff_freq = 800;
		break;
	case 27:
		voice[i].modLfoToFilterFc=2.0;
		voice[i].lfo_phase_increment=109;
		voice[i].lfo_sweep=122;
      		voice[i].sample->cutoff_freq = 800;
		break;
	case 28:
		voice[i].modLfoToFilterFc=-2.0;
		voice[i].lfo_phase_increment=109;
		voice[i].lfo_sweep=122;
      		voice[i].sample->cutoff_freq = 800;
		break;
#endif
	default:
		break;
  }


  for (j=ATTACK; j<MAXPOINT; j++)
    {
	voice[i].envelope_rate[j]=voice[i].sample->envelope_rate[j];
	voice[i].envelope_offset[j]=voice[i].sample->envelope_offset[j];
    }

  voice[i].echo_delay=voice[i].envelope_rate[DELAY];
  voice[i].echo_delay_count = voice[i].echo_delay;

  if (attacktime!=64)
    {
	rt = voice[i].envelope_rate[ATTACK];
	rt = rt + ( (64-attacktime)*rt ) / 100;
	if (rt > 1000) voice[i].envelope_rate[ATTACK] = rt;
    }
  if (releasetime!=64)
    {
	rt = voice[i].envelope_rate[RELEASE];
	rt = rt + ( (64-releasetime)*rt ) / 100;
	if (rt > 1000) voice[i].envelope_rate[RELEASE] = rt;
    }
  if (decaytime!=64)
    {
	rt = voice[i].envelope_rate[DECAY];
	rt = rt + ( (64-decaytime)*rt ) / 100;
	if (rt > 1000) voice[i].envelope_rate[DECAY] = rt;
    }

  if (channel[ch].panning != NO_PANNING)
    voice[i].panning=channel[ch].panning;
  else
    voice[i].panning=voice[i].sample->panning;
  if (drumpan != NO_PANNING)
    voice[i].panning=drumpan;

  if (variationbank == 1) {
    int pan = voice[i].panning;
    int disturb = 0;
    /* If they're close up (no reverb) and you are behind the pianist,
     * high notes come from the right, so we'll spread piano etc. notes
     * out horizontally according to their pitches.
     */
    if (this_prog < 21) {
	    int n = voice[i].velocity - 32;
	    if (n < 0) n = 0;
	    if (n > 64) n = 64;
	    pan = pan/2 + n;
	}
    /* For other types of instruments, the music sounds more alive if
     * notes come from slightly different directions.  However, instruments
     * do drift around in a sometimes disconcerting way, so the following
     * might not be such a good idea.
     */
    else disturb = (voice[i].velocity/32 % 8) +
	(voice[i].note % 8); /* /16? */

    if (pan < 64) pan += disturb;
    else pan -= disturb;
    if (pan < 0) pan = 0;
    else if (pan > 127) pan = 127;
    voice[i].panning = pan;
  }

  recompute_freq(i);
  recompute_amp(i);
  if (voice[i].sample->modes & MODES_ENVELOPE)
    {
      /* Ramp up from 0 */
      voice[i].envelope_stage=ATTACK;
      voice[i].envelope_volume=0;
      voice[i].control_counter=0;
      recompute_envelope(i);
    }
  else
    {
      voice[i].envelope_increment=0;
    }
  apply_envelope_to_amp(i);

  voice[i].clone_voice = -1;
  voice[i].clone_type = NOT_CLONE;

  clone_voice(ip, i, e, STEREO_CLONE, variationbank);
  clone_voice(ip, i, e, CHORUS_CLONE, variationbank);
  clone_voice(ip, i, e, REVERB_CLONE, variationbank);

  ctl->note(i);
}

static void kill_note(int i)
{
  voice[i].status=VOICE_DIE;
  if (voice[i].clone_voice >= 0)
	voice[ voice[i].clone_voice ].status=VOICE_DIE;
  ctl->note(i);
}


/* Only one instance of a note can be playing on a single channel. */
static void note_on(MidiEvent *e)
{
  int i=voices, lowest=-1; 
  int32 lv=0x7FFFFFFF, v;

  while (i--)
    {
      if (voice[i].status == VOICE_FREE)
	lowest=i; /* Can't get a lower volume than silence */
      else if (voice[i].channel==e->channel && 
	       (voice[i].note==e->a || channel[voice[i].channel].mono))
	kill_note(i);
    }

  if (lowest != -1)
    {
      /* Found a free voice. */
      start_note(e,lowest);
      return;
    }
  
#if 0
  /* Look for the decaying note with the lowest volume */
  i=voices;
  while (i--)
    {
      if (voice[i].status & ~(VOICE_ON | VOICE_DIE | VOICE_FREE))
	{
	  v=voice[i].left_mix;
	  if ((voice[i].panned==PANNED_MYSTERY) && (voice[i].right_mix>v))
	    v=voice[i].right_mix;
	  if (v<lv)
	    {
	      lv=v;
	      lowest=i;
	    }
	}
    }
#endif

  /* Look for the decaying note with the lowest volume */
  if (lowest==-1)
   {
   i=voices;
   while (i--)
    {
      if ( (voice[i].status & ~(VOICE_ON | VOICE_DIE | VOICE_FREE)) &&
	  (!voice[i].clone_type))
	{
	  v=voice[i].left_mix;
	  if ((voice[i].panned==PANNED_MYSTERY) && (voice[i].right_mix>v))
	    v=voice[i].right_mix;
	  if (v<lv)
	    {
	      lv=v;
	      lowest=i;
	    }
	}
    }
   }

  if (lowest != -1)
    {
      int cl = voice[lowest].clone_voice;

      /* This can still cause a click, but if we had a free voice to
	 spare for ramping down this note, we wouldn't need to kill it
	 in the first place... Still, this needs to be fixed. Perhaps
	 we could use a reserve of voices to play dying notes only. */

      if (cl >= 0) {
	if (voice[cl].clone_type==STEREO_CLONE ||
		       	(!voice[cl].clone_type && voice[lowest].clone_type==STEREO_CLONE))
	   voice[cl].status=VOICE_FREE;
	else if (voice[cl].clone_voice==lowest) voice[cl].clone_voice=-1;
      }

      cut_notes++;
      voice[lowest].status=VOICE_FREE;
      ctl->note(lowest);
      start_note(e,lowest);
    }
  else
    lost_notes++;
}

static void finish_note(int i)
{
  if (voice[i].sample->modes & MODES_ENVELOPE)
    {
      /* We need to get the envelope out of Sustain stage */
      voice[i].envelope_stage=3;
      voice[i].status=VOICE_OFF;
      recompute_envelope(i);
      apply_envelope_to_amp(i);
      ctl->note(i);
    }
  else
    {
      /* Set status to OFF so resample_voice() will let this voice out
         of its loop, if any. In any case, this voice dies when it
         hits the end of its data (ofs>=data_length). */
      voice[i].status=VOICE_OFF;
    }

  { int v;
    if ( (v=voice[i].clone_voice) >= 0)
      {
	voice[i].clone_voice = -1;
        finish_note(v);
      }
  }
}

static void note_off(MidiEvent *e)
{
  int i=voices, v;
  while (i--)
    if (voice[i].status==VOICE_ON &&
	voice[i].channel==e->channel &&
	voice[i].note==e->a)
      {
	if (channel[e->channel].sustain)
	  {
	    voice[i].status=VOICE_SUSTAINED;

    	    if ( (v=voice[i].clone_voice) >= 0)
	      {
		if (voice[v].status == VOICE_ON)
		  voice[v].status=VOICE_SUSTAINED;
	      }

	    ctl->note(i);
	  }
	else
	  finish_note(i);
	return;
      }
}

/* Process the All Notes Off event */
static void all_notes_off(int c)
{
  int i=voices;
  ctl->cmsg(CMSG_INFO, VERB_DEBUG, "All notes off on channel %d", c);
  while (i--)
    if (voice[i].status==VOICE_ON &&
	voice[i].channel==c)
      {
	if (channel[c].sustain) 
	  {
	    voice[i].status=VOICE_SUSTAINED;
	    ctl->note(i);
	  }
	else
	  finish_note(i);
      }
}

/* Process the All Sounds Off event */
static void all_sounds_off(int c)
{
  int i=voices;
  while (i--)
    if (voice[i].channel==c && 
	voice[i].status != VOICE_FREE &&
	voice[i].status != VOICE_DIE)
      {
	kill_note(i);
      }
}

static void adjust_pressure(MidiEvent *e)
{
  int i=voices;
  while (i--)
    if (voice[i].status==VOICE_ON &&
	voice[i].channel==e->channel &&
	voice[i].note==e->a)
      {
	voice[i].velocity=e->b;
	recompute_amp(i);
	apply_envelope_to_amp(i);
	return;
      }
}

static void adjust_panning(int c)
{
  int i=voices;
  while (i--)
    if ((voice[i].channel==c) &&
	(voice[i].status==VOICE_ON || voice[i].status==VOICE_SUSTAINED))
      {
	if (voice[i].clone_type != NOT_CLONE) continue;
	voice[i].panning=channel[c].panning;
	recompute_amp(i);
	apply_envelope_to_amp(i);
      }
}

static void drop_sustain(int c)
{
  int i=voices;
  while (i--)
    if (voice[i].status==VOICE_SUSTAINED && voice[i].channel==c)
      finish_note(i);
}

static void adjust_pitchbend(int c)
{
  int i=voices;
  while (i--)
    if (voice[i].status!=VOICE_FREE && voice[i].channel==c)
      {
	recompute_freq(i);
      }
}

static void adjust_volume(int c)
{
  int i=voices;
  while (i--)
    if (voice[i].channel==c &&
	(voice[i].status==VOICE_ON || voice[i].status==VOICE_SUSTAINED))
      {
	recompute_amp(i);
	apply_envelope_to_amp(i);
      }
}

static void seek_forward(int32 until_time)
{
  reset_voices();
  while (current_event->time < until_time)
    {
      switch(current_event->type)
	{
	  /* All notes stay off. Just handle the parameter changes. */

	case ME_PITCH_SENS:
	  channel[current_event->channel].pitchsens=
	    current_event->a;
	  channel[current_event->channel].pitchfactor=0;
	  break;
	  
	case ME_PITCHWHEEL:
	  channel[current_event->channel].pitchbend=
	    current_event->a + current_event->b * 128;
	  channel[current_event->channel].pitchfactor=0;
	  break;
	  
	case ME_MAINVOLUME:
	  channel[current_event->channel].volume=current_event->a;
	  break;
	  
	case ME_MASTERVOLUME:
	  adjust_master_volume(current_event->a + (current_event->b <<7));
	  break;
	  
	case ME_PAN:
	  channel[current_event->channel].panning=current_event->a;
	  break;
	      
	case ME_EXPRESSION:
	  channel[current_event->channel].expression=current_event->a;
	  break;
	  
	case ME_PROGRAM:
	  /* if (ISDRUMCHANNEL(current_event->channel)) */
	  if (channel[current_event->channel].kit)
	    /* Change drum set */
	    channel[current_event->channel].bank=current_event->a;
	  else
	    channel[current_event->channel].program=current_event->a;
	  break;

	case ME_SUSTAIN:
	  channel[current_event->channel].sustain=current_event->a;
	  break;


	case ME_REVERBERATION:
	  channel[current_event->channel].reverberation=current_event->a;
	  break;

	case ME_CHORUSDEPTH:
	  channel[current_event->channel].chorusdepth=current_event->a;
	  break;

	case ME_HARMONICCONTENT:
	  channel[current_event->channel].harmoniccontent=current_event->a;
	  break;

	case ME_RELEASETIME:
	  channel[current_event->channel].releasetime=current_event->a;
	  break;

	case ME_ATTACKTIME:
	  channel[current_event->channel].attacktime=current_event->a;
	  break;

	case ME_BRIGHTNESS:
	  channel[current_event->channel].brightness=current_event->a;
	  break;

	case ME_TONE_KIT:
	  if (current_event->a==SFX_BANKTYPE)
		{
		    channel[current_event->channel].sfx=SFXBANK;
		    channel[current_event->channel].kit=0;
		}
	  else
		{
		    channel[current_event->channel].sfx=0;
		    channel[current_event->channel].kit=current_event->a;
		}
	  break;


	case ME_RESET_CONTROLLERS:
	  reset_controllers(current_event->channel);
	  break;
	      
	case ME_TONE_BANK:
	  channel[current_event->channel].bank=current_event->a;
	  break;
	  
	case ME_EOT:
	  current_sample=current_event->time;
	  return;
	}
      current_event++;
    }
  /*current_sample=current_event->time;*/
  if (current_event != event_list)
    current_event--;
  current_sample=until_time;
}

static void skip_to(int32 until_time)
{
  if (current_sample > until_time)
    current_sample=0;

  reset_midi();
  buffered_count=0;
  buffer_pointer=common_buffer;
  current_event=event_list;
  
  if (until_time)
    seek_forward(until_time);
  ctl->reset();
}

static int apply_controls(void)
{
  int rc, i, did_skip=0;
  int32 val;
  /* ASCII renditions of CD player pictograms indicate approximate effect */
  do
    switch(rc=ctl->read(&val))
      {
      case RC_QUIT: /* [] */
      case RC_LOAD_FILE:	  
      case RC_NEXT: /* >>| */
      case RC_REALLY_PREVIOUS: /* |<< */
	return rc;
	
      case RC_CHANGE_VOLUME:
	if (val>0 || amplification > -val)
	  amplification += val;
	else 
	  amplification=0;
	if (amplification > MAX_AMPLIFICATION)
	  amplification=MAX_AMPLIFICATION;
	adjust_amplification();
	for (i=0; i<voices; i++)
	  if (voice[i].status != VOICE_FREE)
	    {
	      recompute_amp(i);
	      apply_envelope_to_amp(i);
	    }
	ctl->master_volume(amplification);
	break;

      case RC_PREVIOUS: /* |<< */
	if (current_sample < 2*play_mode->rate)
	  return RC_REALLY_PREVIOUS;
	return RC_RESTART;

      case RC_RESTART: /* |<< */
	skip_to(0);
	did_skip=1;
	break;
	
      case RC_JUMP:
	if (val >= sample_count)
	  return RC_NEXT;
	skip_to(val);
	return rc;
	
      case RC_FORWARD: /* >> */
	if (val+current_sample >= sample_count)
	  return RC_NEXT;
	skip_to(val+current_sample);
	did_skip=1;
	break;
	
      case RC_BACK: /* << */
	if (current_sample > val)
	  skip_to(current_sample-val);
	else
	  skip_to(0); /* We can't seek to end of previous song. */
	did_skip=1;
	break;
      }
  while (rc!= RC_NONE);
 
  /* Advertise the skip so that we stop computing the audio buffer */
  if (did_skip)
    return RC_JUMP; 
  else
    return rc;
}

static void do_compute_data(uint32 count)
{
  int i;
  if (!count) return; /* (gl) */
  memset(buffer_pointer, 0, count * num_ochannels * 4);
  for (i=0; i<voices; i++)
    {
      if(voice[i].status != VOICE_FREE)
	{
	  if (!voice[i].sample_offset && voice[i].echo_delay_count)
	    {
		if ((uint32)voice[i].echo_delay_count >= count) voice[i].echo_delay_count -= count;
		else
		  {
	            mix_voice(buffer_pointer+voice[i].echo_delay_count, i, count-voice[i].echo_delay_count);
		    voice[i].echo_delay_count = 0;
		  }
	    }
	  else mix_voice(buffer_pointer, i, count);
	}
    }
  current_sample += count;
}


/* count=0 means flush remaining buffered data to output device, then
   flush the device itself */
static int compute_data(void *stream, int32 count)
{
  int rc, channels;

  if ( play_mode->encoding & PE_MONO )
    channels = 1;
  else
    channels = num_ochannels;

  if (!count)
    {
      if (buffered_count)
          s32tobuf(stream, common_buffer, channels*buffered_count);
      buffer_pointer=common_buffer;
      buffered_count=0;
      return RC_NONE;
    }

  while ((count+buffered_count) >= AUDIO_BUFFER_SIZE)
    {
      do_compute_data(AUDIO_BUFFER_SIZE-buffered_count);
      count -= AUDIO_BUFFER_SIZE-buffered_count;
      s32tobuf(stream, common_buffer, channels*AUDIO_BUFFER_SIZE);
      buffer_pointer=common_buffer;
      buffered_count=0;
      
      ctl->current_time(current_sample);
      if ((rc=apply_controls())!=RC_NONE)
	return rc;
    }
  if (count>0)
    {
      do_compute_data(count);
      buffered_count += count;
      buffer_pointer += count * channels;
    }
  return RC_NONE;
}

int Timidity_PlaySome(void *stream, int samples)
{
  int rc = RC_NONE;
  int32 end_sample;
  
  if ( ! midi_playing ) {
    return RC_NONE;
  }
  end_sample = current_sample+samples;
  while ( current_sample < end_sample ) {
    /* Handle all events that should happen at this time */
    while (current_event->time <= current_sample) {
      switch(current_event->type) {

        /* Effects affecting a single note */

        case ME_NOTEON:
	  current_event->a += channel[current_event->channel].transpose;
          if (!(current_event->b)) /* Velocity 0? */
            note_off(current_event);
          else
            note_on(current_event);
          break;
  
        case ME_NOTEOFF:
	  current_event->a += channel[current_event->channel].transpose;
          note_off(current_event);
          break;
  
        case ME_KEYPRESSURE:
          adjust_pressure(current_event);
          break;
  
          /* Effects affecting a single channel */
  
        case ME_PITCH_SENS:
          channel[current_event->channel].pitchsens=current_event->a;
          channel[current_event->channel].pitchfactor=0;
          break;
          
        case ME_PITCHWHEEL:
          channel[current_event->channel].pitchbend=
            current_event->a + current_event->b * 128;
          channel[current_event->channel].pitchfactor=0;
          /* Adjust pitch for notes already playing */
          adjust_pitchbend(current_event->channel);
          ctl->pitch_bend(current_event->channel, 
              channel[current_event->channel].pitchbend);
          break;
          
        case ME_MAINVOLUME:
          channel[current_event->channel].volume=current_event->a;
          adjust_volume(current_event->channel);
          ctl->volume(current_event->channel, current_event->a);
          break;

	case ME_MASTERVOLUME:
	  adjust_master_volume(current_event->a + (current_event->b <<7));
	  break;
	      
	case ME_REVERBERATION:
	  channel[current_event->channel].reverberation=current_event->a;
	  break;

	case ME_CHORUSDEPTH:
	  channel[current_event->channel].chorusdepth=current_event->a;
	  break;

        case ME_PAN:
          channel[current_event->channel].panning=current_event->a;
          if (adjust_panning_immediately)
            adjust_panning(current_event->channel);
          ctl->panning(current_event->channel, current_event->a);
          break;
          
        case ME_EXPRESSION:
          channel[current_event->channel].expression=current_event->a;
          adjust_volume(current_event->channel);
          ctl->expression(current_event->channel, current_event->a);
          break;
  
        case ME_PROGRAM:
          /* if (ISDRUMCHANNEL(current_event->channel)) { */
	  if (channel[current_event->channel].kit) {
            /* Change drum set */
            channel[current_event->channel].bank=current_event->a;
          }
          else
          {
            channel[current_event->channel].program=current_event->a;
          }
          ctl->program(current_event->channel, current_event->a);
          break;
  
        case ME_SUSTAIN:
          channel[current_event->channel].sustain=current_event->a;
          if (!current_event->a)
            drop_sustain(current_event->channel);
          ctl->sustain(current_event->channel, current_event->a);
          break;
          
        case ME_RESET_CONTROLLERS:
          reset_controllers(current_event->channel);
          redraw_controllers(current_event->channel);
          break;
  
        case ME_ALL_NOTES_OFF:
          all_notes_off(current_event->channel);
          break;
          
        case ME_ALL_SOUNDS_OFF:
          all_sounds_off(current_event->channel);
          break;

	case ME_HARMONICCONTENT:
	  channel[current_event->channel].harmoniccontent=current_event->a;
	  break;

	case ME_RELEASETIME:
	  channel[current_event->channel].releasetime=current_event->a;
	  break;

	case ME_ATTACKTIME:
	  channel[current_event->channel].attacktime=current_event->a;
	  break;

	case ME_BRIGHTNESS:
	  channel[current_event->channel].brightness=current_event->a;
	  break;

        case ME_TONE_BANK:
          channel[current_event->channel].bank=current_event->a;
          break;


	case ME_TONE_KIT:
	  if (current_event->a==SFX_BANKTYPE)
	  {
	    channel[current_event->channel].sfx=SFXBANK;
	    channel[current_event->channel].kit=0;
	  }
	  else
	  {
	    channel[current_event->channel].sfx=0;
	    channel[current_event->channel].kit=current_event->a;
	  }
	  break;

        case ME_EOT:
          /* Give the last notes a couple of seconds to decay  */
          ctl->cmsg(CMSG_INFO, VERB_VERBOSE,
            "Playing time: ~%d seconds", current_sample/play_mode->rate+2);
          ctl->cmsg(CMSG_INFO, VERB_VERBOSE,
            "Notes cut: %d", cut_notes);
          ctl->cmsg(CMSG_INFO, VERB_VERBOSE,
          "Notes lost totally: %d", lost_notes);
          midi_playing = 0;
          return RC_TUNE_END;
        }
      current_event++;
    }
    if (current_event->time > end_sample)
      rc=compute_data(stream, end_sample-current_sample);
    else
      rc=compute_data(stream, current_event->time-current_sample);
    ctl->refresh();
    if ( (rc!=RC_NONE) && (rc!=RC_JUMP))
      break;
  }
  return rc;
}


void Timidity_SetVolume(int volume)
{
  int i;
  if (volume > MAX_AMPLIFICATION)
    amplification=MAX_AMPLIFICATION;
  else
  if (volume < 0)
    amplification=0;
  else
    amplification=volume;
  adjust_amplification();
  for (i=0; i<voices; i++)
    if (voice[i].status != VOICE_FREE)
      {
        recompute_amp(i);
        apply_envelope_to_amp(i);
      }
  ctl->master_volume(amplification);
}

MidiSong *Timidity_LoadSong(const char *midifile)
{
  MidiSong *song;
  int32 events;
  SDL_RWops *rw;

  /* Allocate memory for the song */
  song = (MidiSong *)safe_malloc(sizeof(*song));
  memset(song, 0, sizeof(*song));

  /* Open the file */
  strcpy(midi_name, midifile);

  rw = SDL_RWFromFile(midifile, "rb");
  if ( rw != NULL ) {
    song->events=read_midi_file(rw, &events, &song->samples);
    SDL_RWclose(rw);
  }

  /* Make sure everything is okay */
  if (!song->events) {
    free(song);
    song = NULL;
  }
  return(song);
}

MidiSong *Timidity_LoadSong_RW(SDL_RWops *rw)
{
  MidiSong *song;
  int32 events;

  /* Allocate memory for the song */
  song = (MidiSong *)safe_malloc(sizeof(*song));
  memset(song, 0, sizeof(*song));

  strcpy(midi_name, "SDLrwops source");

  song->events=read_midi_file(rw, &events, &song->samples);

  /* Make sure everything is okay */
  if (!song->events) {
    free(song);
    song = NULL;
  }
  return(song);
}

void Timidity_Start(MidiSong *song)
{
  load_missing_instruments();
  adjust_amplification();
  sample_count = song->samples;
  event_list = song->events;
  lost_notes=cut_notes=0;

  skip_to(0);
  midi_playing = 1;
}

int Timidity_Active(void)
{
	return(midi_playing);
}

void Timidity_Stop(void)
{
  midi_playing = 0;
}

void Timidity_FreeSong(MidiSong *song)
{
  if (free_instruments_afterwards)
    free_instruments();
  
  free(song->events);
  free(song);
}

void Timidity_Close(void)
{
  if (resample_buffer) {
    free(resample_buffer);
    resample_buffer=NULL;
  }
  if (common_buffer) {
    free(common_buffer);
    common_buffer=NULL;
  }
  free_instruments();
  free_pathlist();
}

