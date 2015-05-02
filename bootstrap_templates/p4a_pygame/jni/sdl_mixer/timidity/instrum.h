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

   instrum.h

   */


typedef struct {
  int32
    loop_start, loop_end, data_length,
    sample_rate, low_freq, high_freq, root_freq;
  uint8
    root_tune, fine_tune;
  int32
    envelope_rate[7], envelope_offset[7],
    modulation_rate[7], modulation_offset[7];
  FLOAT_T
    volume, resonance,
    modEnvToFilterFc, modEnvToPitch, modLfoToFilterFc;
  sample_t *data;
  int32 
    tremolo_sweep_increment, tremolo_phase_increment, 
    lfo_sweep_increment, lfo_phase_increment,
    vibrato_sweep_increment, vibrato_control_ratio,
    cutoff_freq;
  uint8
    reverberation, chorusdepth,
    tremolo_depth, vibrato_depth,
    modes;
  uint8
    attenuation, freq_center;
  int8
    panning, note_to_use, exclusiveClass;
  int16
    scale_tuning, keyToModEnvHold, keyToModEnvDecay,
    keyToVolEnvHold, keyToVolEnvDecay;
  int32
    freq_scale, vibrato_delay;
} Sample;

/* Bits in modes: */
#define MODES_16BIT	(1<<0)
#define MODES_UNSIGNED	(1<<1)
#define MODES_LOOPING	(1<<2)
#define MODES_PINGPONG	(1<<3)
#define MODES_REVERSE	(1<<4)
#define MODES_SUSTAIN	(1<<5)
#define MODES_ENVELOPE	(1<<6)
#define MODES_FAST_RELEASE	(1<<7)

#if 0
typedef struct {
  int samples;
  Sample *sample;
} Instrument;
#endif

#define INST_GUS	0
#define INST_SF2	1

typedef struct {
  int type;
  int samples;
  Sample *sample;
  int left_samples;
  Sample *left_sample;
  int right_samples;
  Sample *right_sample;
  unsigned char *contents;
} Instrument;


typedef struct _InstrumentLayer {
  uint8 lo, hi;
  int size;
  Instrument *instrument;
  struct _InstrumentLayer *next;
} InstrumentLayer;

struct cfg_type {
	int font_code;
	int num;
	const char *name;
};

#define FONT_NORMAL 0
#define FONT_FFF    1
#define FONT_SBK    2
#define FONT_TONESET 3
#define FONT_DRUMSET 4
#define FONT_PRESET 5


typedef struct {
  char *name;
  InstrumentLayer *layer;
  int font_type, sf_ix, last_used, tuning;
  int note, amp, pan, strip_loop, strip_envelope, strip_tail;
} ToneBankElement;

#if 0
typedef struct {
  char *name;
  Instrument *instrument;
  int note, amp, pan, strip_loop, strip_envelope, strip_tail;
} ToneBankElement;
#endif
/* A hack to delay instrument loading until after reading the
   entire MIDI file. */
#define MAGIC_LOAD_INSTRUMENT ((InstrumentLayer *)(-1))

#define MAXPROG 128
#define MAXBANK 130
#define SFXBANK (MAXBANK-1)
#define SFXDRUM1 (MAXBANK-2)
#define SFXDRUM2 (MAXBANK-1)
#define XGDRUM 1

#if 0
typedef struct {
  ToneBankElement tone[128];
} ToneBank;
#endif

typedef struct {
  char *name;
  ToneBankElement tone[MAXPROG];
} ToneBank;


extern char *sf_file;

extern ToneBank *tonebank[], *drumset[];

#if 0
extern Instrument *default_instrument;
#endif
extern InstrumentLayer *default_instrument;
extern int default_program;
extern int antialiasing_allowed;
extern int fast_decay;
extern int free_instruments_afterwards;

#define SPECIAL_PROGRAM -1

extern int load_missing_instruments(void);
extern void free_instruments(void);
extern void end_soundfont(void);
extern int set_default_instrument(const char *name);


extern int32 convert_tremolo_sweep(uint8 sweep);
extern int32 convert_vibrato_sweep(uint8 sweep, int32 vib_control_ratio);
extern int32 convert_tremolo_rate(uint8 rate);
extern int32 convert_vibrato_rate(uint8 rate);

extern int init_soundfont(char *fname, int oldbank, int newbank, int level);
extern InstrumentLayer *load_sbk_patch(const char *name, int gm_num, int bank, int percussion,
 int panning, int amp, int note_to_use, int sf_ix);
extern int current_tune_number;
extern int max_patch_memory;
extern int current_patch_memory;
#define XMAPMAX 800
extern int xmap[XMAPMAX][5];
extern void pcmap(int *b, int *v, int *p, int *drums);

