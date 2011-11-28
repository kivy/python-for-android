/************************************************************************
   patchload.c  --  loads patches for playmidi package
   Some of this code was adapted from code written by Hannu Solovainen

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
/*    edited by Peter Kutak            */
/*    email : kutak@stonline.sk        */

#if defined(linux) || defined(__FreeBSD__)

#include "playmidi.h"
#ifdef linux
#include <linux/ultrasound.h>
#else
#include <machine/ultrasound.h>
#endif
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include "gmvoices.h"

SEQ_USE_EXTBUF();
extern int play_gus, play_sb, play_ext, playing, verbose, force8bit;
extern int reverb, fmloaded[256], patchloaded[256];
extern int gus_dev, sb_dev, ext_dev, seqfd, wantopl3;
extern struct synth_info card_info[MAX_CARDS];

static int use8bit = 0;

struct pat_header {
    char magic[12];
    char version[10];
    char description[60];
    unsigned char instruments;
    char voices;
    char channels;
    unsigned short nr_waveforms;
    unsigned short master_volume;
    unsigned int data_size;
};

struct sample_header {
    char name[7];
    unsigned char fractions;
    int len;
    int loop_start;
    int loop_end;
    unsigned short base_freq;
    int low_note;
    int high_note;
    int base_note;
    short detune;
    unsigned char panning;

    unsigned char envelope_rate[6];
    unsigned char envelope_offset[6];

    unsigned char tremolo_sweep;
    unsigned char tremolo_rate;
    unsigned char tremolo_depth;

    unsigned char vibrato_sweep;
    unsigned char vibrato_rate;
    unsigned char vibrato_depth;

    char modes;

    short scale_frequency;
    unsigned short scale_factor;
};

struct patch_info *patch;
int spaceleft, totalspace;

void gus_reload_8_bit();

void gus_load(pgm)
int pgm;
{
    int i, j, patfd, offset;
    struct pat_header header;
    struct sample_header sample;
    char buf[256], name[256];
    struct stat info;

    if (pgm < 0) {
	use8bit = force8bit;
	GUS_NUMVOICES(gus_dev, (card_info[gus_dev].nr_voices = 32));
	SEQ_DUMPBUF();
	for (i = 0; i < 256; i++)
	    patchloaded[i] = 0;
	if (ioctl(seqfd, SNDCTL_SEQ_RESETSAMPLES, &gus_dev) == -1)
	{
	    /* error: should quit */
	}
	spaceleft = gus_dev;
	ioctl(seqfd, SNDCTL_SYNTH_MEMAVL, &spaceleft);
	totalspace = spaceleft;
    }

    if (patchloaded[pgm] < 0)
	return;

    if (patchloaded[pgm] == 1)
	return;

    if (gmvoice[pgm] == NULL) {
	patchloaded[pgm] = -1;
	return;
    }
    sprintf(name, PATCH_PATH1 "/%s.pat", gmvoice[pgm]);

    if (stat(name, &info) == -1) {
	sprintf(name, PATCH_PATH2 "/%s.pat", gmvoice[pgm]);
	if (stat(name, &info) == -1)
	    return;
    }
    if ((patfd = open(name, O_RDONLY, 0)) == -1)
	return;
    if (spaceleft < info.st_size) {
	if (!use8bit)
	    gus_reload_8_bit();
	if (use8bit)
	    if (spaceleft < info.st_size / 2) {
		close(patfd);
		patchloaded[pgm] = -1;	/* no space for patch */
		return;
	    }
    }
    if (read(patfd, buf, 0xef) != 0xef) {
	close(patfd);
	return;
    }
    memcpy((char *) &header, buf, sizeof(header));

    if (strncmp(header.magic, "GF1PATCH110", 12)) {
	close(patfd);
	return;
    }
    if (strncmp(header.version, "ID#000002", 10)) {
	close(patfd);
	return;
    }
    header.nr_waveforms = *(unsigned short *) &buf[85];
    header.master_volume = *(unsigned short *) &buf[87];

    offset = 0xef;

    for (i = 0; i < header.nr_waveforms; i++) {

	if (lseek(patfd, offset, 0) == -1) {
	    close(patfd);
	    return;
	}
	if (read(patfd, &buf, sizeof(sample)) != sizeof(sample)) {
	    close(patfd);
	    return;
	}
	memcpy((char *) &sample, buf, sizeof(sample));

	/*
	 * Since some fields of the patch record are not 32bit aligned, we must
	 * handle them specially.
	 */
	sample.low_note = *(int *) &buf[22];
	sample.high_note = *(int *) &buf[26];
	sample.base_note = *(int *) &buf[30];
	sample.detune = *(short *) &buf[34];
	sample.panning = (unsigned char) buf[36];

	memcpy(sample.envelope_rate, &buf[37], 6);
	memcpy(sample.envelope_offset, &buf[43], 6);

	sample.tremolo_sweep = (unsigned char) buf[49];
	sample.tremolo_rate = (unsigned char) buf[50];
	sample.tremolo_depth = (unsigned char) buf[51];

	sample.vibrato_sweep = (unsigned char) buf[52];
	sample.vibrato_rate = (unsigned char) buf[53];
	sample.vibrato_depth = (unsigned char) buf[54];
	sample.modes = (unsigned char) buf[55];
	sample.scale_frequency = *(short *) &buf[56];
	sample.scale_factor = *(unsigned short *) &buf[58];

	offset = offset + 96;
	patch = (struct patch_info *) malloc(sizeof(*patch) + sample.len);

	if (patch == NULL) {
	    close(patfd);
	    return;
	}
	patch->key = GUS_PATCH;
	patch->device_no = gus_dev;
	patch->instr_no = pgm;
	patch->mode = sample.modes | WAVE_TREMOLO |
	    WAVE_VIBRATO | WAVE_SCALE;
	patch->len = (use8bit ? sample.len / 2 : sample.len);
	patch->loop_start =
	    (use8bit ? sample.loop_start / 2 : sample.loop_start);
	patch->loop_end = (use8bit ? sample.loop_end / 2 : sample.loop_end);
	patch->base_note = sample.base_note;
	patch->high_note = sample.high_note;
	patch->low_note = sample.low_note;
	patch->base_freq = sample.base_freq;
	patch->detuning = sample.detune;
	patch->panning = (sample.panning - 7) * 16;

	memcpy(patch->env_rate, sample.envelope_rate, 6);
	for (j = 0; j < 6; j++)	/* tone things down slightly */
	    patch->env_offset[j] =
		(736 * sample.envelope_offset[j] + 384) / 768;

	if (reverb)
	    if (pgm < 120)
		patch->env_rate[3] = (2 << 6) | (12 - (reverb >> 4));
	    else if (pgm > 127)
		patch->env_rate[1] = (3 << 6) | (63 - (reverb >> 1));

	patch->tremolo_sweep = sample.tremolo_sweep;
	patch->tremolo_rate = sample.tremolo_rate;
	patch->tremolo_depth = sample.tremolo_depth;

	patch->vibrato_sweep = sample.vibrato_sweep;
	patch->vibrato_rate = sample.vibrato_rate;
	patch->vibrato_depth = sample.vibrato_depth;

	patch->scale_frequency = sample.scale_frequency;
	patch->scale_factor = sample.scale_factor;

	patch->volume = header.master_volume;

	if (lseek(patfd, offset, 0) == -1) {
	    close(patfd);
	    return;
	}
	if (read(patfd, patch->data, sample.len) != sample.len) {
	    close(patfd);
	    return;
	}
	if (patch->mode & WAVE_16_BITS && use8bit) {
	    patch->mode &= ~WAVE_16_BITS;
	    /* cut out every other byte to make 8-bit data from 16-bit */
	    for (j = 0; j < patch->len; j++)
		patch->data[j] = patch->data[1 + j * 2];
	}
	SEQ_WRPATCH(patch, sizeof(*patch) + patch->len);
	free(patch);
	offset = offset + sample.len;
    }
    close(patfd);
    spaceleft = gus_dev;
    ioctl(seqfd, SNDCTL_SYNTH_MEMAVL, &spaceleft);
    patchloaded[pgm] = 1;
    return;
}

void gus_reload_8_bit()
{
    int i;

    if (ioctl(seqfd, SNDCTL_SEQ_RESETSAMPLES, &gus_dev) == -1) 
    {
	/* error: should quit */
    }
    spaceleft = gus_dev;
    ioctl(seqfd, SNDCTL_SYNTH_MEMAVL, &spaceleft);
    totalspace = spaceleft;
    use8bit = 1;
    for (i = 0; i < 256; i++)
	if (patchloaded[i] > 0) {
	    patchloaded[i] = 0;
	    gus_load(i);
	}
}

void adjustfm(buf, key)
char *buf;
int key;
{
    unsigned char pan = ((rand() % 3) + 1) << 4;

    if (key == FM_PATCH) {
	buf[39] &= 0xc0;
	if (buf[46] & 1)
	    buf[38] &= 0xc0;
	buf[46] = (buf[46] & 0xcf) | pan;
	if (reverb) {
	    unsigned val;
	    val = buf[43] & 0x0f;
	    if (val > 0)
		val--;
	    buf[43] = (buf[43] & 0xf0) | val;
	}
    } else {
	int mode;
	if (buf[46] & 1)
	    mode = 2;
	else
	    mode = 0;
	if (buf[57] & 1)
	    mode++;
	buf[50] &= 0xc0;
	if (mode == 3)
	    buf[49] &= 0xc0;
	if (mode == 1)
	    buf[39] &= 0xc0;
	if (mode == 2 || mode == 3)
	    buf[38] &= 0xc0;
	buf[46] = (buf[46] & 0xcf) | pan;
	buf[57] = (buf[57] & 0xcf) | pan;
	if (mode == 1 && reverb) {
	    unsigned val;
	    val = buf[43] & 0x0f;
	    if (val > 0)
		val--;
	    buf[43] = (buf[43] & 0xf0) | val;
	    val = buf[54] & 0x0f;
	    if (val > 0)
		val--;
	    buf[54] = (buf[54] & 0xf0) | val;
	}
    }
}

void loadfm()
{
    int sbfd, i, n, voice_size, data_size;
    char buf[60];
    struct sbi_instrument instr;

    for (i = 0; i < 256; i++)
	fmloaded[i] = 0;
    srand(getpid());
    if (wantopl3) {
	voice_size = 60;
	sbfd = open(O3MELODIC, O_RDONLY, 0);
    } else {
	voice_size = 52;
	sbfd = open(SBMELODIC, O_RDONLY, 0);
    }
    if (sbfd == -1)
    {
        /* error: should quit */
    }
    instr.device = sb_dev;

    for (i = 0; i < 128; i++) {
	if (read(sbfd, buf, voice_size) != voice_size)
	{
	    /* error: should quit */
	}
	instr.channel = i;

	if (strncmp(buf, "4OP", 3) == 0) {
	    instr.key = OPL3_PATCH;
	    data_size = 22;
	} else {
	    instr.key = FM_PATCH;
	    data_size = 11;
	}

	fmloaded[i] = instr.key;

	adjustfm(buf, instr.key);
	for (n = 0; n < 32; n++)
	    instr.operators[n] = (n < data_size) ? buf[36 + n] : 0;

	SEQ_WRPATCH(&instr, sizeof(instr));
    }
    close(sbfd);

    if (wantopl3)
	sbfd = open(O3DRUMS, O_RDONLY, 0);
    else
	sbfd = open(SBDRUMS, O_RDONLY, 0);

    for (i = 128; i < 175; i++) {
	if (read(sbfd, buf, voice_size) != voice_size)
	{
	    /* error: should quit */
	}
	instr.channel = i;

	if (strncmp(buf, "4OP", 3) == 0) {
	    instr.key = OPL3_PATCH;
	    data_size = 22;
	} else {
	    instr.key = FM_PATCH;
	    data_size = 11;
	}
	fmloaded[i] = instr.key;

	adjustfm(buf, instr.key);
	for (n = 0; n < 32; n++)
	    instr.operators[n] = (n < data_size) ? buf[n + 36] : 0;

	SEQ_WRPATCH(&instr, sizeof(instr));
    }
    close(sbfd);
}
#endif /* linux || FreeBSD */
