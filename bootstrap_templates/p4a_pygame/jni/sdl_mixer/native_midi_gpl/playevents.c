/************************************************************************
   playevents.c  -- actually sends sorted list of events to device

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
/*    edited by Peter Kutak           */
/*    email : kutak@stonline.sk       */

#if defined(linux) || defined(__FreeBSD__)

#include "playmidi.h"
#include <sys/time.h>

extern int seq_set_patch(int, int);
extern void seq_key_pressure(int, int, int, int);
extern void seq_start_note(int, int, int, int);
extern void seq_stop_note(int, int, int, int);
extern void seq_control(int, int, int, int);
extern void seq_chn_pressure(int, int, int);
extern void seq_bender(int, int, int, int);
extern void seq_reset();

SEQ_USE_EXTBUF();
extern int division, ntrks, format;
extern int gus_dev, ext_dev, sb_dev, awe_dev, perc, seqfd, p_remap;
extern int play_gus, play_fm, play_ext, play_awe, reverb, chorus, chanmask;
extern int usevol[16];
extern struct miditrack seq[MAXTRKS];
extern float skew;
extern unsigned long int default_tempo;
extern char ImPlaying,StopPlease;
extern void load_sysex(int, unsigned char *, int);

unsigned long int ticks, tempo;
struct timeval start_time;

unsigned long int rvl(s)
struct miditrack *s;
{
    register unsigned long int value = 0;
    register unsigned char c;

    if (s->index < s->length && ((value = s->data[(s->index)++]) & 0x80)) {
	value &= 0x7f;
	do {
	    if (s->index >= s->length)
		c = 0;
	    else
		value = (value << 7) +
		    ((c = s->data[(s->index)++]) & 0x7f);
	} while (c & 0x80);
    }
    return (value);
}

/* indexed by high nibble of command */
int cmdlen[16] =
{0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 1, 1, 2, 0};

#define CMD		seq[track].running_st
#define TIME		seq[track].ticks
#define CHN		(CMD & 0xf)
#define NOTE		data[0]
#define VEL		data[1]

int playevents()
{
    unsigned long int tempo = default_tempo, lasttime = 0;
    unsigned int lowtime, track, best, length, loaded;
    unsigned char *data;
    double current = 0.0, dtime = 0.0;
    int use_dev, play_status, playing = 1;

    seq_reset();
    gettimeofday(&start_time, NULL);	/* for synchronization */
    for (track = 0; track < ntrks; track++) {
	seq[track].index = seq[track].running_st = 0;
	seq[track].ticks = rvl(&seq[track]);
    }
    for (best = 0; best < 16; best++) {
	if (ISAWE(best))
	    use_dev = awe_dev;
	else if (ISGUS(best))
	    use_dev = gus_dev;
	else if (ISFM(best))
	    use_dev = sb_dev;
	else
	    use_dev = ext_dev;
	seq_control(use_dev, best, CTL_BANK_SELECT, 0);
	seq_control(use_dev, best, CTL_EXT_EFF_DEPTH, reverb);
	seq_control(use_dev, best, CTL_CHORUS_DEPTH, chorus);
	seq_control(use_dev, best, CTL_MAIN_VOLUME, 127);
	seq_chn_pressure(use_dev, best, 127);
	seq_control(use_dev, best, 0x4a, 127);
    }
    SEQ_START_TIMER();
    SEQ_DUMPBUF();
    while (playing) {
	lowtime = ~0;
	for (best = track = 0; track < ntrks; track++)
	    if (seq[track].ticks < lowtime) {
		best = track;
		lowtime = TIME;
	    }
	if (lowtime == ~0)
	    break;		/* no more data to read */
	track = best;
	if (ISMIDI(CHN))
	    use_dev = ext_dev;
	else if (ISAWE(CHN))
	    use_dev = awe_dev;
	else if (ISGUS(CHN))
	    use_dev = gus_dev;
	else
	    use_dev = sb_dev;

	/* this section parses data in midi file buffer */
	if ((seq[track].data[seq[track].index] & 0x80) &&
	    (seq[track].index < seq[track].length))
	    CMD = seq[track].data[seq[track].index++];
	if (CMD == 0xff && seq[track].index < seq[track].length)
	    CMD = seq[track].data[seq[track].index++];
	if (CMD > 0xf7)	/* midi real-time message (ignored) */
	    length = 0;
	else if (!(length = cmdlen[(CMD & 0xf0) >> 4]))
	    length = rvl(&seq[track]);

	if (seq[track].index + length < seq[track].length) {
	    /* use the parsed midi data */
	    data = &(seq[track].data[seq[track].index]);
	    if (CMD == set_tempo)
		tempo = ((*(data) << 16) | (data[1] << 8) | data[2]);
	    if (TIME > lasttime) {
		if (division > 0) {
		    dtime = ((double) ((TIME - lasttime) * (tempo / 10000)) /
			     (double) (division)) * skew;
		    current += dtime;
		    lasttime = TIME;
		} else if (division < 0)
		    current = ((double) TIME /
			       ((double) ((division & 0xff00 >> 8) *
				   (division & 0xff)) * 10000.0)) * skew;
		/* stop if there's more than 40 seconds of nothing */
		if (dtime > 4096.0)
		    playing = 0;
		else if ((int) current > ticks) {
		    SEQ_WAIT_TIME((ticks = (int) current));
		    SEQ_DUMPBUF();
		}
	    }
	    if (CMD > 0x7f && CMD < 0xf0 && ISPERC(CHN) && p_remap) {
		CMD &= 0xf0;
		CMD |= (p_remap - 1);
	    }
	    loaded = 0;		/* for patch setting failures */
	    if (playing && CMD > 0x7f && ISPLAYING(CHN))
		switch (CMD & 0xf0) {
		case MIDI_KEY_PRESSURE:
		    if (ISPERC(CHN) && VEL && (!ISMIDI(CHN)&&!ISAWE(CHN)))
			loaded = seq_set_patch(CHN, NOTE + 128);
		    if (loaded != -1)
			seq_key_pressure(use_dev, CHN, NOTE, VEL);
		    break;
		case MIDI_NOTEON:
		    if (ISPERC(CHN) && VEL && (!ISMIDI(CHN)&&!ISAWE(CHN)))
			loaded = seq_set_patch(CHN, NOTE + 128);
		    if (VEL && usevol[CHN])
			VEL = usevol[CHN];
		    if (loaded != -1)
			seq_start_note(use_dev, CHN, NOTE, VEL);
		    break;
		case MIDI_NOTEOFF:
		    seq_stop_note(use_dev, CHN, NOTE, VEL);
		    break;
		case MIDI_CTL_CHANGE:
		    seq_control(use_dev, CHN, NOTE, VEL);
		    break;
		case MIDI_CHN_PRESSURE:
		    seq_chn_pressure(use_dev, CHN, NOTE);
		    break;
		case MIDI_PITCH_BEND:
		    seq_bender(use_dev, CHN, NOTE, VEL);
		    break;
		case MIDI_PGM_CHANGE:
		    if (ISMIDI(CHN) || ISAWE(CHN) || !ISPERC(CHN))
			NOTE = seq_set_patch(CHN, NOTE);
		    break;
		case MIDI_SYSTEM_PREFIX:
		    if (length > 1)
			load_sysex(length, data, CMD);
		    break;
		default:
		    break;
		}
	}
	/* this last little part queues up the next event time */
	seq[track].index += length;
	if (seq[track].index >= seq[track].length)
	    seq[track].ticks = ~0;	/* mark track complete */
	else
	    seq[track].ticks += rvl(&seq[track]);
    }
    SEQ_DUMPBUF();
    ImPlaying = 0;
    return 1;
}
#endif /* linux || FreeBSD */
