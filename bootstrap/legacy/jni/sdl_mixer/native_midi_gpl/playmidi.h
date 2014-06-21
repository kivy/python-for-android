#define RELEASE "Playmidi 2.4"
/************************************************************************
   playmidi.h  --  defines and structures for use by playmidi package

   Copyright (C) 1994-1996 Nathan I. Laredo

   This program is modifiable/redistributable under the terms
   of the GNU General Public Licence.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
   Send your comments and all your spare pocket change to
   laredo@gnu.ai.mit.edu (Nathan Laredo) or to PSC 1, BOX 709, 2401
   Kelly Drive, Lackland AFB, TX 78236-5128, USA.
 *************************************************************************
/*    edited by Peter Kutak          */
/*    email : kutak@stonline.sk      */


/* Default mask for percussion instruments.  Channels 16 and 10 = 0x8200 */
#define PERCUSSION	0x0200
/* change the following if you have lots of synth devices */
#define MAX_CARDS	5
/* the following definition is set by Configure */
#define FM_DEFAULT_MODE	0
/* the following definition is set by Configure */
#define PATCH_PATH1	"/dos/ultrasnd/midi"
/* the following definition is set by Configure */
#define PATCH_PATH2	"/usr/local/lib/Plib"
/* change this if you notice performance problems,  128 bytes by default */
#define SEQUENCERBLOCKSIZE 128
/* change this if you have really outrageous midi files > 128 tracks */
/* 128 tracks is approximately a 4K structure */
#define MAXTRKS		128
/* where to find fm patch libraries */
#define SEQUENCER_DEV	"/dev/sequencer"
#define O3MELODIC	"/etc/std.o3"
#define O3DRUMS		"/etc/drums.o3"
#define SBMELODIC	"/etc/std.sb"
#define SBDRUMS		"/etc/drums.sb"
#define ISPERC(x)	(perc & (1 << x))
#define ISGUS(x)	(play_gus & (1 << x))
#define ISFM(x)		(play_fm & (1 << x))
#define ISMIDI(x)	(play_ext & (1 << x))
#define ISAWE(x)	(play_awe & (1 << x))
#define ISPLAYING(x)	(chanmask & (1 << x))
#define NO_EXIT		100

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/soundcard.h>
#include <sys/ioctl.h>
#ifdef linux
#include <linux/awe_voice.h>
#else
#include <awe_voice.h>
#endif

struct chanstate {
    int program;
    int bender;
    int oldbend;	/* used for graphics */
    int bender_range;
    int oldrange;	/* used for graphics */
    int controller[255];
    int pressure;
};

struct voicestate {
    int note;
    int channel;
    int timestamp;
    int dead;
};
/* Non-standard MIDI file formats */
#define RIFF			0x52494646
#define CTMF			0x43544d46
/* Standard MIDI file format definitions */
#define MThd			0x4d546864
#define MTrk			0x4d54726b
#define	meta_event		0xff
#define	sequence_number 	0x00
#define	text_event		0x01
#define copyright_notice 	0x02
#define sequence_name    	0x03
#define instrument_name 	0x04
#define lyric	        	0x05
#define marker			0x06
#define	cue_point		0x07
#define channel_prefix		0x20
#define	end_of_track		0x2f
#define	set_tempo		0x51
#define	smpte_offset		0x54
#define	time_signature		0x58
#define	key_signature		0x59
#define	sequencer_specific	0x74

struct miditrack {
   unsigned char *data;		/* data of midi track */
   unsigned long int length;	/* length of track data */
   unsigned long int index;	/* current byte in track */
   unsigned long int ticks;	/* current midi tick count */
   unsigned char running_st;	/* running status byte */
};

