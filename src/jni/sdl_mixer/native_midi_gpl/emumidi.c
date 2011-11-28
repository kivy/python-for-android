/************************************************************************
   emumidi.c  -- emulation of midi device for FM/OPL3/GUS

   Copyright (C) 1994-1996 Nathan I. Laredo

   This program is modifiable/redistributable under the terms
   of the GNU General Public Licence.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
   Send your comments and all your spare pocket change to
   laredo@gnu.ai.mit.edu (Nathan Laredo) or to PSC 1, BOX 709, 2401
   Kelly Drive, Lackland AFB, TX 78236-5128, USA.
 *************************************************************************/
/*    edited by Peter Kutak         */
/*    email : kutak@stonline.sk     */

#if defined(linux) || defined(__FreeBSD__)

#include "emumidi.h"

SEQ_USE_EXTBUF();

extern int seqfd, play_ext, play_gus, play_fm, play_awe;
extern int gus_dev, sb_dev, ext_dev, awe_dev;
extern struct synth_info card_info[MAX_CARDS];
extern int chanmask, perc, ticks, dochan, wantopl3, MT32;
extern int patchloaded[256], fmloaded[256], useprog[16];
int note_vel[16][128];
struct voicestate voice[2][36];
struct chanstate channel[16];
#define C_GUS 0
#define C_FM 1
#define CN (ISGUS(chn) ? C_GUS : C_FM)
#define CHANNEL (dochan ? chn : 0)

void load_sysex(length, data, type)
int length;
unsigned char *data;
int type;
{
    unsigned long int i, j;

    /*
     * If the system exclusive is for roland, evaluate it.  More than
     * roland could be evaluated here if i had documentation.  Please
     * submit patches for any other hardware to laredo@gnu.ai.mit.edu
     * Complete emulation of all GS sysex messages in the works....
     */
    if (length > 7 && data[0] == 0x41 && data[2] == 0x42 && data[3] == 0x12) {
	/* GS DATA SET MESSAGES */
	if (data[4] == 0x40 && (data[5] & 0xf0) == 0x10 && data[6] == 0x15) {
		/* USE RHYTHM PART */
		if (!(i = (data[5] & 0xf)))
		    i = 0x09;
		else if (i < 10)
		    i--;
		i = 1<<i;
		if (data[7])
		    perc |= i;
		else
		    perc &= ~i;
	}
	if ((data[4] == 0x40 || data[4] == 0) &&
	    data[5] == 0x00 && data[6] == 0x7f) { /* GS RESET */
		perc = 0x0200;	/* percussion in channel 10 only */
		for (i = 0; i < 16; i++) {	/* set state info */
		    for (j = 0; j < 128; j++)
			note_vel[i][j] = 0;
		    channel[i].bender = channel[i].oldbend = 8192;
		    channel[i].bender_range = channel[i].oldrange = 2;
		    channel[i].controller[CTL_PAN] = 64;
		    channel[i].controller[CTL_SUSTAIN] = 0;
    		}
	}
    }
    if (!play_ext)
	return;
    if (type == MIDI_SYSTEM_PREFIX)
	SEQ_MIDIOUT(ext_dev, MIDI_SYSTEM_PREFIX);
    for (i = 0; i < length; i++)
	SEQ_MIDIOUT(ext_dev, data[i]);
}

int seq_set_patch(chn, pgm)
int chn, pgm;
{
    if (MT32 && pgm < 128)
	pgm = mt32pgm[pgm];
    if (useprog[chn])
	pgm = useprog[chn] - 1;
    if (ISMIDI(chn)) {
	SEQ_MIDIOUT(ext_dev, MIDI_PGM_CHANGE + CHANNEL);
	SEQ_MIDIOUT(ext_dev, pgm);
    } else if (ISAWE(chn)) {
	SEQ_SET_PATCH(awe_dev, chn, pgm);
    } else if (ISPERC(chn)) {
	if (ISGUS(chn) && patchloaded[pgm] != 1)
	    return -1;
	else if (ISFM(chn) && !fmloaded[pgm])
	    return -1;
    } else if (ISGUS(chn) && patchloaded[pgm] != 1)
	/* find first loaded gus program to replace missing one */
	for (pgm = 0; patchloaded[pgm] != 1; pgm++);
    return (channel[chn].program = pgm);
}

/* finetune returns exact frequency with bender applied.  Not used */
/*
int finetune(chn, note)
int chn, note;
{
    long int r, b, d;

    r = channel[chn].bender_range;
    b = channel[chn].bender - 8192;
    if (!b || r + note > 127 || r - note < 0)
	return n_freq[note];
    r = n_freq[note + r] - n_freq[note - r];
    d = b * r;
    d /= 8192;
    return n_freq[note] + d;

}
*/
extern int _seqbufptr;

void seq_stop_note(dev, chn, note, vel)
int dev, chn, note, vel;
{
    int i, card = CN;

    note_vel[chn][note] = 0;
    if (ISMIDI(chn)) {
	SEQ_MIDIOUT(dev, MIDI_NOTEOFF + CHANNEL);
	SEQ_MIDIOUT(dev, note);
	SEQ_MIDIOUT(dev, vel);
    } else if (ISAWE(chn)) {
	SEQ_STOP_NOTE(dev, chn, note, vel);
    } else
	for (i = 0; i < card_info[dev].nr_voices; i++)
	    if (voice[card][i].channel == chn &&
		voice[card][i].note == note) {
		voice[card][i].dead = 1;
		voice[card][i].timestamp /= 2;
		if (!channel[chn].controller[CTL_SUSTAIN] && !ISPERC(chn))
		    SEQ_STOP_NOTE(dev, i, note, vel);
	    }
}

void seq_key_pressure(dev, chn, note, vel)
int dev, chn, note, vel;
{
    int i, card = CN;

    if (ISMIDI(chn)) {
	SEQ_MIDIOUT(dev, MIDI_KEY_PRESSURE + CHANNEL);
	SEQ_MIDIOUT(dev, note);
	SEQ_MIDIOUT(dev, vel);
    } else if (ISAWE(chn)) {
	AWE_KEY_PRESSURE(dev, chn, note, vel);
    } else
	for (i = 0; i < card_info[dev].nr_voices; i++)
	    if (voice[card][i].channel == chn &&
		voice[card][i].note == note)
		SEQ_KEY_PRESSURE(dev, i, note, vel);
}

int new_voice(dev, chn)
int dev, chn;
{
    int i, oldest, last, card = CN;

    if (ISFM(chn) && fmloaded[channel[chn].program] == OPL3_PATCH)
	last = 6;		/* 4-op voice can only use first six voices */
    else
	last = card_info[dev].nr_voices;

    for (i = oldest = 0; i < last; i++)
	if (voice[card][i].timestamp < voice[card][oldest].timestamp)
	    oldest = i;
    return oldest;
}

void seq_start_note(dev, chn, note, vel)
int dev, chn, note, vel;
{
    int v, c, card = CN;

    note_vel[chn][note] = vel;
    if (ISMIDI(chn)) {
	SEQ_MIDIOUT(dev, MIDI_NOTEON + CHANNEL);
	SEQ_MIDIOUT(dev, note);
	SEQ_MIDIOUT(dev, vel);
    } else if (vel == 0)
	seq_stop_note(dev, chn, note, 64);
    else if (ISAWE(chn)) {
	SEQ_START_NOTE(dev, chn, note, vel);
    } else {
	v = new_voice(dev, chn);
	SEQ_SET_PATCH(dev, v, channel[chn].program);
	SEQ_BENDER_RANGE(dev, v, (channel[chn].bender_range * 100));
	SEQ_BENDER(dev, v, channel[chn].bender);
	SEQ_CONTROL(dev, v, CTL_PAN,
		    channel[chn].controller[CTL_PAN]);
	SEQ_START_NOTE(dev, v, note, vel);
	voice[card][v].note = note;
	voice[card][v].channel = chn;
	voice[card][v].timestamp = ticks;
	voice[card][v].dead = 0;
	if ((c = channel[chn].controller[CTL_CHORUS_DEPTH] * 8)) {
	    if (channel[chn].bender_range)
		c /= channel[chn].bender_range;
	    v = new_voice(dev, chn);
	    SEQ_SET_PATCH(dev, v, channel[chn].program);
	    SEQ_BENDER_RANGE(dev, v, (channel[chn].bender_range * 100));
	    if (channel[chn].bender + c < 0x4000) {
		SEQ_BENDER(dev, v, channel[chn].bender + c);
	    } else {
		SEQ_BENDER(dev, v, channel[chn].bender - c);
	    }
	    /* put chorus note on the "extreme" side */
	    c = channel[chn].controller[CTL_PAN];
	    if (c < 64)
		c = 0;
	    else if (c > 64)
		c = 127;
	    SEQ_CONTROL(dev, v, CTL_PAN, c);
	    SEQ_START_NOTE(dev, v, note, vel);
	    voice[card][v].note = note;
	    voice[card][v].channel = chn;
	    /* allow chorus note to be stolen very quickly */
	    voice[card][v].timestamp = ticks / 2;
	    voice[card][v].dead = 0;
	}
    }
}

static int rpn1[16] =
{127, 127, 127, 127, 127, 127, 127, 127,
 127, 127, 127, 127, 127, 127, 127, 127};
static int rpn2[16] =
{127, 127, 127, 127, 127, 127, 127, 127,
 127, 127, 127, 127, 127, 127, 127, 127};

void seq_control(dev, chn, p1, p2)
int dev, chn, p1, p2;
{
    int i, card = CN;

    channel[chn].controller[p1] = p2;

    if (ISMIDI(chn)) {
	SEQ_MIDIOUT(dev, MIDI_CTL_CHANGE + CHANNEL);
	SEQ_MIDIOUT(dev, p1);
	SEQ_MIDIOUT(dev, p2);
    }
    if (p1 == 7 || p1 == 39)
	return;
    switch (p1) {
    case CTL_SUSTAIN:
	if (ISAWE(chn)) {
	    SEQ_CONTROL(dev, chn, p1, p2);
	} else if (!ISMIDI(chn))
	    if (p1 == CTL_SUSTAIN && !p2) {
		for (i = 0; i < card_info[card].nr_voices; i++)
		    if (voice[card][i].channel == chn
			&& voice[card][i].dead) {
			SEQ_STOP_NOTE(dev, i, voice[card][i].note, 64);
			voice[card][i].dead = 0;
		    }
	    }
	break;
    case CTL_REGIST_PARM_NUM_MSB:
	rpn1[chn] = p2;
	break;
    case CTL_REGIST_PARM_NUM_LSB:
	rpn2[chn] = p2;
	break;
    case CTL_DATA_ENTRY:
	if (rpn1[chn] == 0 && rpn2[chn] == 0) {
	    channel[chn].oldrange = channel[chn].bender_range;
	    channel[chn].bender_range = p2;
	    rpn1[chn] = rpn2[chn] = 127;
	    if (ISAWE(chn)) {
		SEQ_BENDER_RANGE(dev, chn, p2 * 100);
	    } else if (!ISMIDI(chn))
		for (i = 0; i < card_info[card].nr_voices; i++)
		    SEQ_BENDER_RANGE(dev, i, p2 * 100);
	}
	break;
    default:
	/* sent on the off chance the sound driver is enhanced */
	if (ISAWE(chn)) {
	    SEQ_CONTROL(dev, chn, p1, p2);
	} else if (!ISMIDI(chn) && (p1 < 0x10 || (p1 & 0xf0) == 0x50))
	    for (i = 0; i < card_info[card].nr_voices; i++)
		if (voice[card][i].channel == chn)
		    SEQ_CONTROL(dev, i, p1, p2);
	break;
    }
}

void seq_chn_pressure(dev, chn, vel)
int dev, chn, vel;
{
    int card = CN, i;

    channel[chn].pressure = vel;
    if (ISMIDI(chn)) {
	SEQ_MIDIOUT(dev, MIDI_CHN_PRESSURE + CHANNEL);
	SEQ_MIDIOUT(dev, vel);
    } else if (ISAWE(chn)) {
	AWE_CHN_PRESSURE(dev, chn, vel);
    } else
	for (i = 0; i < card_info[dev].nr_voices; i++)
	    if (voice[card][i].channel == chn)
		SEQ_KEY_PRESSURE(dev, i, voice[card][i].note, vel);
}

void seq_bender(dev, chn, p1, p2)
int dev, chn, p1, p2;
{
    int card = CN, i, val;

    val = (p2 << 7) + p1;
    channel[chn].oldbend = channel[chn].bender;
    channel[chn].bender = val;

    if (ISMIDI(chn)) {
	SEQ_MIDIOUT(dev, MIDI_PITCH_BEND + CHANNEL);
	SEQ_MIDIOUT(dev, p1);
	SEQ_MIDIOUT(dev, p2);
    } else if (ISAWE(chn)) {
	SEQ_BENDER(dev, chn, val);
    } else
	for (i = 0; i < card_info[dev].nr_voices; i++)
	    if (voice[card][i].channel == chn)
		SEQ_BENDER(dev, i, val);
}

void seq_reset()
{
    int i, j;

    _seqbufptr = ticks = 0;
    ioctl(seqfd, SNDCTL_SEQ_RESET);
    for (i = 0; i < 16; i++) {
	if (ISMIDI(i)) {
	    seq_control(ext_dev,i,0,0);
	    seq_control(ext_dev,i,32,0);
	}
	seq_set_patch(i, 0);
	for (j = 0; j < 128; j++)
	    note_vel[i][j] = 0;
	channel[i].bender = channel[i].oldbend = 8192;
	channel[i].bender_range = channel[i].oldrange = 2;
	channel[i].controller[CTL_PAN] = 64;
	channel[i].controller[CTL_SUSTAIN] = 0;
    }
    if (play_gus)
	for (i = 0; i < card_info[gus_dev].nr_voices; i++) {
	    SEQ_CONTROL(gus_dev, i, SEQ_VOLMODE, VOL_METHOD_LINEAR);
	    if (voice[0][i].note)
		SEQ_STOP_NOTE(gus_dev, i, voice[0][i].note, 64);
	    voice[0][i].dead = voice[0][i].timestamp = -1;
	}
    if (play_fm) {
	if (wantopl3)
	    ioctl(seqfd, SNDCTL_FM_4OP_ENABLE, &sb_dev);
	for (i = 0; i < card_info[sb_dev].nr_voices; i++) {
	    SEQ_CONTROL(sb_dev, i, SEQ_VOLMODE, VOL_METHOD_LINEAR);
	    if (voice[1][i].note)
		SEQ_STOP_NOTE(sb_dev, i, voice[1][i].note, 64);
	    voice[1][i].dead = voice[1][i].timestamp = -1;
	}
    }
    if (play_awe) {
	AWE_SET_CHANNEL_MODE(awe_dev, 1);
	AWE_DRUM_CHANNELS(awe_dev, perc);
	AWE_TERMINATE_ALL(awe_dev);
	for (i = 0; i < card_info[awe_dev].nr_voices; i++) {
	    voice[0][i].dead = voice[0][i].timestamp = -1;
	}
    }
    SEQ_DUMPBUF();
}

#endif /* linux || FreeBSD */
