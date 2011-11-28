/*

    TiMidity -- Experimental MIDI to WAVE converter
    Copyright (C) 1995 Tuukka Toivonen <toivonen@clinet.fi>

    Suddenly, you realize that this program is free software; you get
    an overwhelming urge to redistribute it and/or modify it under the
    terms of the GNU General Public License as published by the Free
    Software Foundation; either version 2 of the License, or (at your
    option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received another copy of the GNU General Public
    License along with this program; if not, write to the Free
    Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
    I bet they'll be amazed.

    mix.c */

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "config.h"
#include "common.h"
#include "instrum.h"
#include "playmidi.h"
#include "output.h"
#include "ctrlmode.h"
#include "tables.h"
#include "resample.h"
#include "mix.h"

/* Returns 1 if envelope runs out */
int recompute_envelope(int v)
{
  int stage;

  stage = voice[v].envelope_stage;

  if (stage>5)
    {
      /* Envelope ran out. */
      int tmp=(voice[v].status == VOICE_DIE); /* Already displayed as dead */
      voice[v].status = VOICE_FREE;
      if(!tmp)
	ctl->note(v);
      return 1;
    }

  if (voice[v].sample->modes & MODES_ENVELOPE)
    {
      if (voice[v].status==VOICE_ON || voice[v].status==VOICE_SUSTAINED)
	{
	  if (stage>2)
	    {
	      /* Freeze envelope until note turns off. Trumpets want this. */
	      voice[v].envelope_increment=0;
	      return 0;
	    }
	}
    }
  voice[v].envelope_stage=stage+1;

  if (voice[v].envelope_volume==voice[v].sample->envelope_offset[stage])
    return recompute_envelope(v);
  voice[v].envelope_target=voice[v].sample->envelope_offset[stage];
  voice[v].envelope_increment = voice[v].sample->envelope_rate[stage];
  if (voice[v].envelope_target<voice[v].envelope_volume)
    voice[v].envelope_increment = -voice[v].envelope_increment;
  return 0;
}

void apply_envelope_to_amp(int v)
{
  FLOAT_T lamp=voice[v].left_amp, ramp, lramp, rramp, ceamp, lfeamp;
  int32 la,ra, lra, rra, cea, lfea;
  if (voice[v].panned == PANNED_MYSTERY)
    {
      lramp=voice[v].lr_amp;
      ramp=voice[v].right_amp;
      ceamp=voice[v].ce_amp;
      rramp=voice[v].rr_amp;
      lfeamp=voice[v].lfe_amp;

      if (voice[v].tremolo_phase_increment)
	{
	  FLOAT_T tv = voice[v].tremolo_volume;
	  lramp *= tv;
	  lamp *= tv;
	  ceamp *= tv;
	  ramp *= tv;
	  rramp *= tv;
	  lfeamp *= tv;
	}
      if (voice[v].sample->modes & MODES_ENVELOPE)
	{
	  FLOAT_T ev = (FLOAT_T)vol_table[voice[v].envelope_volume>>23];
	  lramp *= ev;
	  lamp *= ev;
	  ceamp *= ev;
	  ramp *= ev;
	  rramp *= ev;
	  lfeamp *= ev;
	}

      la = (int32)FSCALE(lamp,AMP_BITS);
      ra = (int32)FSCALE(ramp,AMP_BITS);
      lra = (int32)FSCALE(lramp,AMP_BITS);
      rra = (int32)FSCALE(rramp,AMP_BITS);
      cea = (int32)FSCALE(ceamp,AMP_BITS);
      lfea = (int32)FSCALE(lfeamp,AMP_BITS);
      
      if (la>MAX_AMP_VALUE) la=MAX_AMP_VALUE;
      if (ra>MAX_AMP_VALUE) ra=MAX_AMP_VALUE;
      if (lra>MAX_AMP_VALUE) lra=MAX_AMP_VALUE;
      if (rra>MAX_AMP_VALUE) rra=MAX_AMP_VALUE;
      if (cea>MAX_AMP_VALUE) cea=MAX_AMP_VALUE;
      if (lfea>MAX_AMP_VALUE) lfea=MAX_AMP_VALUE;

      voice[v].lr_mix=FINAL_VOLUME(lra);
      voice[v].left_mix=FINAL_VOLUME(la);
      voice[v].ce_mix=FINAL_VOLUME(cea);
      voice[v].right_mix=FINAL_VOLUME(ra);
      voice[v].rr_mix=FINAL_VOLUME(rra);
      voice[v].lfe_mix=FINAL_VOLUME(lfea);
    }
  else
    {
      if (voice[v].tremolo_phase_increment)
	lamp *= voice[v].tremolo_volume;
      if (voice[v].sample->modes & MODES_ENVELOPE)
	lamp *= (FLOAT_T)vol_table[voice[v].envelope_volume>>23];

      la = (int32)FSCALE(lamp,AMP_BITS);

      if (la>MAX_AMP_VALUE)
	la=MAX_AMP_VALUE;

      voice[v].left_mix=FINAL_VOLUME(la);
    }
}

static int update_envelope(int v)
{
  voice[v].envelope_volume += voice[v].envelope_increment;
  /* Why is there no ^^ operator?? */
  if (((voice[v].envelope_increment < 0) &&
       (voice[v].envelope_volume <= voice[v].envelope_target)) ||
      ((voice[v].envelope_increment > 0) &&
	   (voice[v].envelope_volume >= voice[v].envelope_target)))
    {
      voice[v].envelope_volume = voice[v].envelope_target;
      if (recompute_envelope(v))
	return 1;
    }
  return 0;
}

static void update_tremolo(int v)
{
  int32 depth=voice[v].sample->tremolo_depth<<7;

  if (voice[v].tremolo_sweep)
    {
      /* Update sweep position */

      voice[v].tremolo_sweep_position += voice[v].tremolo_sweep;
      if (voice[v].tremolo_sweep_position>=(1<<SWEEP_SHIFT))
	voice[v].tremolo_sweep=0; /* Swept to max amplitude */
      else
	{
	  /* Need to adjust depth */
	  depth *= voice[v].tremolo_sweep_position;
	  depth >>= SWEEP_SHIFT;
	}
    }

  voice[v].tremolo_phase += voice[v].tremolo_phase_increment;

  /* if (voice[v].tremolo_phase >= (SINE_CYCLE_LENGTH<<RATE_SHIFT))
     voice[v].tremolo_phase -= SINE_CYCLE_LENGTH<<RATE_SHIFT;  */

  voice[v].tremolo_volume = (FLOAT_T) 
    (1.0 - FSCALENEG((sine(voice[v].tremolo_phase >> RATE_SHIFT) + 1.0)
		    * depth * TREMOLO_AMPLITUDE_TUNING,
		    17));

  /* I'm not sure about the +1.0 there -- it makes tremoloed voices'
     volumes on average the lower the higher the tremolo amplitude. */
}

/* Returns 1 if the note died */
static int update_signal(int v)
{
  if (voice[v].envelope_increment && update_envelope(v))
    return 1;

  if (voice[v].tremolo_phase_increment)
    update_tremolo(v);

  apply_envelope_to_amp(v);
  return 0;
}

#ifdef LOOKUP_HACK
#  define MIXATION(a)	*lp++ += mixup[(a<<8) | (uint8)s];
#else
#  define MIXATION(a)	*lp++ += (a)*s;
#endif

#define MIXSKIP lp++
#define MIXMAX(a,b) *lp++ += ((a>b)?a:b) * s
#define MIXCENT(a,b) *lp++ += (a/2+b/2) * s
#define MIXHALF(a)	*lp++ += (a>>1)*s;

static void mix_mystery_signal(resample_t *sp, int32 *lp, int v, int count)
{
  Voice *vp = voice + v;
  final_volume_t 
    left_rear=vp->lr_mix, 
    left=vp->left_mix, 
    center=vp->ce_mix, 
    right=vp->right_mix, 
    right_rear=vp->rr_mix, 
    lfe=vp->lfe_mix;
  int cc;
  resample_t s;

  if (!(cc = vp->control_counter))
    {
      cc = control_ratio;
      if (update_signal(v))
	return;	/* Envelope ran out */

	left_rear = vp->lr_mix;
	left = vp->left_mix;
	center = vp->ce_mix;
	right = vp->right_mix;
	right_rear = vp->rr_mix;
	lfe = vp->lfe_mix;
    }
  
  while (count)
    if (cc < count)
      {
	count -= cc;
	while (cc--)
	  {
	    s = *sp++;
	      	MIXATION(left);
	      	MIXATION(right);
		if (num_ochannels >= 4) {
			MIXATION(left_rear);
			MIXATION(right_rear);
		}
		if (num_ochannels == 6) {
			MIXATION(center);
			MIXATION(lfe);
		}
	  }
	cc = control_ratio;
	if (update_signal(v))
	  return;	/* Envelope ran out */
	left_rear = vp->lr_mix;
	left = vp->left_mix;
	center = vp->ce_mix;
	right = vp->right_mix;
	right_rear = vp->rr_mix;
	lfe = vp->lfe_mix;
      }
    else
      {
	vp->control_counter = cc - count;
	while (count--)
	  {
	    s = *sp++;
	      	MIXATION(left);
	      	MIXATION(right);
		if (num_ochannels >= 4) {
			MIXATION(left_rear);
			MIXATION(right_rear);
		}
		if (num_ochannels == 6) {
			MIXATION(center);
			MIXATION(lfe);
		}
	  }
	return;
      }
}

static void mix_center_signal(resample_t *sp, int32 *lp, int v, int count)
{
  Voice *vp = voice + v;
  final_volume_t 
    left=vp->left_mix;
  int cc;
  resample_t s;

  if (!(cc = vp->control_counter))
    {
      cc = control_ratio;
      if (update_signal(v))
	return;	/* Envelope ran out */
      left = vp->left_mix;
    }
  
  while (count)
    if (cc < count)
      {
	count -= cc;
	while (cc--)
	  {
	    s = *sp++;
		if (num_ochannels == 2) {
	    		MIXATION(left);
	    		MIXATION(left);
		}
		else if (num_ochannels == 4) {
			MIXATION(left);
			MIXSKIP;
			MIXATION(left);
			MIXSKIP;
		}
		else if (num_ochannels == 6) {
			MIXSKIP;
			MIXSKIP;
			MIXSKIP;
			MIXSKIP;
			MIXATION(left);
			MIXATION(left);
		}
	  }
	cc = control_ratio;
	if (update_signal(v))
	  return;	/* Envelope ran out */
	left = vp->left_mix;
      }
    else
      {
	vp->control_counter = cc - count;
	while (count--)
	  {
	    s = *sp++;
		if (num_ochannels == 2) {
	    		MIXATION(left);
	    		MIXATION(left);
		}
		else if (num_ochannels == 4) {
			MIXATION(left);
			MIXSKIP;
			MIXATION(left);
			MIXSKIP;
		}
		else if (num_ochannels == 6) {
			MIXSKIP;
			MIXSKIP;
			MIXSKIP;
			MIXSKIP;
			MIXATION(left);
			MIXATION(left);
		}
	  }
	return;
      }
}

static void mix_single_left_signal(resample_t *sp, int32 *lp, int v, int count)
{
  Voice *vp = voice + v;
  final_volume_t 
    left=vp->left_mix;
  int cc;
  resample_t s;
  
  if (!(cc = vp->control_counter))
    {
      cc = control_ratio;
      if (update_signal(v))
	return;	/* Envelope ran out */
      left = vp->left_mix;
    }
  
  while (count)
    if (cc < count)
      {
	count -= cc;
	while (cc--)
	  {
	    s = *sp++;
		if (num_ochannels == 2) {
			MIXATION(left);
	    		MIXSKIP;
		}
		if (num_ochannels >= 4) {
			MIXHALF(left);
	    		MIXSKIP;
			MIXATION(left);
	    		MIXSKIP;
		}
		if (num_ochannels == 6) {
	    		MIXSKIP;
			MIXATION(left);
		}
	  }
	cc = control_ratio;
	if (update_signal(v))
	  return;	/* Envelope ran out */
	left = vp->left_mix;
      }
    else
      {
	vp->control_counter = cc - count;
	while (count--)
	  {
	    s = *sp++;
		if (num_ochannels == 2) {
			MIXATION(left);
	    		MIXSKIP;
		}
		if (num_ochannels >= 4) {
			MIXHALF(left);
	    		MIXSKIP;
			MIXATION(left);
	    		MIXSKIP;
		}
		if (num_ochannels == 6) {
	    		MIXSKIP;
			MIXATION(left);
		}
	  }
	return;
      }
}

static void mix_single_right_signal(resample_t *sp, int32 *lp, int v, int count)
{
  Voice *vp = voice + v;
  final_volume_t 
    left=vp->left_mix;
  int cc;
  resample_t s;
  
  if (!(cc = vp->control_counter))
    {
      cc = control_ratio;
      if (update_signal(v))
	return;	/* Envelope ran out */
      left = vp->left_mix;
    }
  
  while (count)
    if (cc < count)
      {
	count -= cc;
	while (cc--)
	  {
	    s = *sp++;
		if (num_ochannels == 2) {
	    		MIXSKIP;
			MIXATION(left);
		}
		if (num_ochannels >= 4) {
	    		MIXSKIP;
			MIXHALF(left);
	    		MIXSKIP;
			MIXATION(left);
		} if (num_ochannels == 6) {
	    		MIXSKIP;
			MIXATION(left);
		}
	  }
	cc = control_ratio;
	if (update_signal(v))
	  return;	/* Envelope ran out */
	left = vp->left_mix;
      }
    else
      {
	vp->control_counter = cc - count;
	while (count--)
	  {
	    s = *sp++;
		if (num_ochannels == 2) {
	    		MIXSKIP;
			MIXATION(left);
		}
		if (num_ochannels >= 4) {
	    		MIXSKIP;
			MIXHALF(left);
	    		MIXSKIP;
			MIXATION(left);
		} if (num_ochannels == 6) {
	    		MIXSKIP;
			MIXATION(left);
		}
	  }
	return;
      }
}

static void mix_mono_signal(resample_t *sp, int32 *lp, int v, int count)
{
  Voice *vp = voice + v;
  final_volume_t 
    left=vp->left_mix;
  int cc;
  resample_t s;
  
  if (!(cc = vp->control_counter))
    {
      cc = control_ratio;
      if (update_signal(v))
	return;	/* Envelope ran out */
      left = vp->left_mix;
    }
  
  while (count)
    if (cc < count)
      {
	count -= cc;
	while (cc--)
	  {
	    s = *sp++;
	    MIXATION(left);
	  }
	cc = control_ratio;
	if (update_signal(v))
	  return;	/* Envelope ran out */
	left = vp->left_mix;
      }
    else
      {
	vp->control_counter = cc - count;
	while (count--)
	  {
	    s = *sp++;
	    MIXATION(left);
	  }
	return;
      }
}

static void mix_mystery(resample_t *sp, int32 *lp, int v, int count)
{
  final_volume_t 
    left_rear=voice[v].lr_mix, 
    left=voice[v].left_mix, 
    center=voice[v].ce_mix, 
    right=voice[v].right_mix, 
    right_rear=voice[v].rr_mix, 
    lfe=voice[v].lfe_mix;
  resample_t s;
  
  while (count--)
    {
      s = *sp++;
	      	MIXATION(left);
	      	MIXATION(right);
		if (num_ochannels >= 4) {
			MIXATION(left_rear);
			MIXATION(right_rear);
		}
		if (num_ochannels == 6) {
			MIXATION(center);
			MIXATION(lfe);
		}
    }
}

static void mix_center(resample_t *sp, int32 *lp, int v, int count)
{
  final_volume_t 
    left=voice[v].left_mix;
  resample_t s;
  
  while (count--)
    {
      s = *sp++;
		if (num_ochannels == 2) {
      			MIXATION(left);
      			MIXATION(left);
		}
		else if (num_ochannels == 4) {
      			MIXATION(left);
      			MIXATION(left);
			MIXSKIP;
			MIXSKIP;
		}
		else if (num_ochannels == 6) {
			MIXSKIP;
			MIXSKIP;
			MIXSKIP;
			MIXSKIP;
			MIXATION(left);
			MIXATION(left);
		}
    }
}

static void mix_single_left(resample_t *sp, int32 *lp, int v, int count)
{
  final_volume_t 
    left=voice[v].left_mix;
  resample_t s;
  
  while (count--)
    {
      s = *sp++;
		if (num_ochannels == 2) {
			MIXATION(left);
      			MIXSKIP;
		}
		if (num_ochannels >= 4) {
			MIXHALF(left);
      			MIXSKIP;
			MIXATION(left);
      			MIXSKIP;
		}
	       	if (num_ochannels == 6) {
      			MIXSKIP;
			MIXATION(left);
		}
    }
}
static void mix_single_right(resample_t *sp, int32 *lp, int v, int count)
{
  final_volume_t 
    left=voice[v].left_mix;
  resample_t s;
  
  while (count--)
    {
      s = *sp++;
		if (num_ochannels == 2) {
      			MIXSKIP;
			MIXATION(left);
		}
		if (num_ochannels >= 4) {
      			MIXSKIP;
			MIXHALF(left);
      			MIXSKIP;
			MIXATION(left);
		}
	       	if (num_ochannels == 6) {
      			MIXSKIP;
			MIXATION(left);
		}
    }
}

static void mix_mono(resample_t *sp, int32 *lp, int v, int count)
{
  final_volume_t 
    left=voice[v].left_mix;
  resample_t s;
  
  while (count--)
    {
      s = *sp++;
      MIXATION(left);
    }
}

/* Ramp a note out in c samples */
static void ramp_out(resample_t *sp, int32 *lp, int v, int32 c)
{

  /* should be final_volume_t, but uint8 gives trouble. */
  int32 left_rear, left, center, right, right_rear, lfe, li, ri;

  resample_t s = 0; /* silly warning about uninitialized s */

  /* Fix by James Caldwell */
  if ( c == 0 ) c = 1;

  left = voice[v].left_mix;
  li = -(left/c);
  if (!li) li = -1;

  /* printf("Ramping out: left=%d, c=%d, li=%d\n", left, c, li); */

  if (!(play_mode->encoding & PE_MONO))
    {
      if (voice[v].panned==PANNED_MYSTERY)
	{
	  left_rear = voice[v].lr_mix;
	  center=voice[v].ce_mix;
	  right=voice[v].right_mix;
	  right_rear = voice[v].rr_mix;
	  lfe = voice[v].lfe_mix;

	  ri=-(right/c);
	  while (c--)
	    {
	      left_rear += li; if (left_rear<0) left_rear=0;
	      left += li; if (left<0) left=0;
	      center += li; if (center<0) center=0;
	      right += ri; if (right<0) right=0;
	      right_rear += ri; if (right_rear<0) right_rear=0;
	      lfe += li; if (lfe<0) lfe=0;
	      s=*sp++;
	      	MIXATION(left);
	      	MIXATION(right);
		if (num_ochannels >= 4) {
			MIXATION(left_rear);
			MIXATION(right_rear);
		}
		if (num_ochannels == 6) {
			MIXATION(center);
			MIXATION(lfe);
		}
	    }
	}
      else if (voice[v].panned==PANNED_CENTER)
	{
	  while (c--)
	    {
	      left += li;
	      if (left<0)
		return;
	      s=*sp++;	
		if (num_ochannels == 2) {
	      		MIXATION(left);
	      		MIXATION(left);
		}
		else if (num_ochannels == 4) {
			MIXATION(left);
	      		MIXATION(left);
			MIXSKIP;
			MIXSKIP;
		}
		else if (num_ochannels == 6) {
			MIXSKIP;
			MIXSKIP;
			MIXSKIP;
			MIXSKIP;
	      		MIXATION(left);
	      		MIXATION(left);
		}
	    }
	}
      else if (voice[v].panned==PANNED_LEFT)
	{
	  while (c--)
	    {
	      left += li;
	      if (left<0)
		return;
	      s=*sp++;
	      MIXATION(left);
	      MIXSKIP;
		if (num_ochannels >= 4) {
			MIXATION(left);
	      		MIXSKIP;
		} if (num_ochannels == 6) {
			MIXATION(left);
			MIXATION(left);
		}
	    }
	}
      else if (voice[v].panned==PANNED_RIGHT)
	{
	  while (c--)
	    {
	      left += li;
	      if (left<0)
		return;
	      s=*sp++;
	      MIXSKIP;
	      MIXATION(left);
		if (num_ochannels >= 4) {
	      		MIXSKIP;
			MIXATION(left);
		} if (num_ochannels == 6) {
			MIXATION(left);
			MIXATION(left);
		}
	    }
	}
    }
  else
    {
      /* Mono output.  */
      while (c--)
	{
	  left += li;
	  if (left<0)
	    return;
	  s=*sp++;
	  MIXATION(left);
	}
    }
}


/**************** interface function ******************/

void mix_voice(int32 *buf, int v, int32 c)
{
  Voice *vp=voice+v;
  int32 count=c;
  resample_t *sp;
  if (c<0) return;
  if (vp->status==VOICE_DIE)
    {
      if (count>=MAX_DIE_TIME)
	count=MAX_DIE_TIME;
      sp=resample_voice(v, &count);
      ramp_out(sp, buf, v, count);
      vp->status=VOICE_FREE;
    }
  else
    {
      sp=resample_voice(v, &count);
      if (count<0) return;
      if (play_mode->encoding & PE_MONO)
	{
	  /* Mono output. */
	  if (vp->envelope_increment || vp->tremolo_phase_increment)
	    mix_mono_signal(sp, buf, v, count);
	  else
	    mix_mono(sp, buf, v, count);
	}
      else
	{
	  if (vp->panned == PANNED_MYSTERY)
	    {
	      if (vp->envelope_increment || vp->tremolo_phase_increment)
		mix_mystery_signal(sp, buf, v, count);
	      else
		mix_mystery(sp, buf, v, count);
	    }
	  else if (vp->panned == PANNED_CENTER)
	    {
	      if (vp->envelope_increment || vp->tremolo_phase_increment)
		mix_center_signal(sp, buf, v, count);
	      else
		mix_center(sp, buf, v, count);
	    }
	  else
	    { 
	      /* It's either full left or full right. In either case,
		 every other sample is 0. Just get the offset right: */
	      
	      if (vp->envelope_increment || vp->tremolo_phase_increment)
	      {
	        if (vp->panned == PANNED_RIGHT)
			mix_single_right_signal(sp, buf, v, count);
		else mix_single_left_signal(sp, buf, v, count);
	      }
	      else 
	      {
	        if (vp->panned == PANNED_RIGHT)
			mix_single_right(sp, buf, v, count);
		else mix_single_left(sp, buf, v, count);
	      }
	    }
	}
    }
}
