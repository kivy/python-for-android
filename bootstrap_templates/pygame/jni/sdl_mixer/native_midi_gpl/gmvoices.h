/********************************************************************
   gmvoices.h -- List of GM voice filenames for GUS.

   Copyright (C) 1994-1996 Nathan I. Laredo

   This program is modifiable/redistributable under the terms
   of the GNU General Public Licence.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
   Send your comments and all your spare pocket change to
   laredo@gnu.ai.mit.edu (Nathan Laredo) or to PSC 1, BOX 709, 2401
   Kelly Drive, Lackland AFB, TX 78236-5128, USA.

 ********************************************************************/
char *gmvoice[256] = {
/* [Melodic Patches] */
 /* 000 */ "acpiano",	/* 001 */ "britepno",	/* 002 */ "synpiano",
 /* 003 */ "honky",	/* 004 */ "epiano1",	/* 005 */ "epiano2",
 /* 006 */ "hrpschrd",	/* 007 */ "clavinet",	/* 008 */ "celeste",
 /* 009 */ "glocken",	/* 010 */ "musicbox",	/* 011 */ "vibes",
 /* 012 */ "marimba",	/* 013 */ "xylophon",	/* 014 */ "tubebell",
 /* 015 */ "santur",	/* 016 */ "homeorg",	/* 017 */ "percorg",
 /* 018 */ "rockorg",	/* 019 */ "church",	/* 020 */ "reedorg",
 /* 021 */ "accordn",	/* 022 */ "harmonca",	/* 023 */ "concrtna",
 /* 024 */ "nyguitar",	/* 025 */ "acguitar",	/* 026 */ "jazzgtr",
 /* 027 */ "cleangtr",	/* 028 */ "mutegtr",	/* 029 */ "odguitar",
 /* 030 */ "distgtr",	/* 031 */ "gtrharm",	/* 032 */ "acbass",
 /* 033 */ "fngrbass",	/* 034 */ "pickbass",	/* 035 */ "fretless",
 /* 036 */ "slapbas1",	/* 037 */ "slapbas2",	/* 038 */ "synbass1",
 /* 039 */ "synbass2",	/* 040 */ "violin",	/* 041 */ "viola",
 /* 042 */ "cello",	/* 043 */ "contraba",	/* 044 */ "marcato",
 /* 045 */ "pizzcato",	/* 046 */ "harp",	/* 047 */ "timpani",
 /* 048 */ "marcato",	/* 049 */ "slowstr",	/* 050 */ "synstr1",
 /* 051 */ "synstr2",	/* 052 */ "choir",	/* 053 */ "doo",
 /* 054 */ "voices",	/* 055 */ "orchhit",	/* 056 */ "trumpet",
 /* 057 */ "trombone",	/* 058 */ "tuba",	/* 059 */ "mutetrum",
 /* 060 */ "frenchrn",	/* 061 */ "hitbrass",	/* 062 */ "synbras1",
 /* 063 */ "synbras2",	/* 064 */ "sprnosax",	/* 065 */ "altosax",
 /* 066 */ "tenorsax",	/* 067 */ "barisax",	/* 068 */ "oboe",
 /* 069 */ "englhorn",	/* 070 */ "bassoon",	/* 071 */ "clarinet",
 /* 072 */ "piccolo",	/* 073 */ "flute",	/* 074 */ "recorder",
 /* 075 */ "woodflut",	/* 076 */ "bottle",	/* 077 */ "shakazul",
 /* 078 */ "whistle",	/* 079 */ "ocarina",	/* 080 */ "sqrwave",
 /* 081 */ "sawwave",	/* 082 */ "calliope",	/* 083 */ "chiflead",
 /* 084 */ "charang",	/* 085 */ "voxlead",	/* 086 */ "lead5th",
 /* 087 */ "basslead",	/* 088 */ "fantasia",	/* 089 */ "warmpad",
 /* 090 */ "polysyn",	/* 091 */ "ghostie",	/* 092 */ "bowglass",
 /* 093 */ "metalpad",	/* 094 */ "halopad",	/* 095 */ "sweeper",
 /* 096 */ "aurora",	/* 097 */ "soundtrk",	/* 098 */ "crystal",
 /* 099 */ "atmosphr",	/* 100 */ "freshair",	/* 101 */ "unicorn",
 /* 102 */ "sweeper",	/* 103 */ "startrak",	/* 104 */ "sitar",
 /* 105 */ "banjo",	/* 106 */ "shamisen",	/* 107 */ "koto",
 /* 108 */ "kalimba",	/* 109 */ "bagpipes",	/* 110 */ "fiddle",
 /* 111 */ "shannai",	/* 112 */ "carillon",	/* 113 */ "agogo",
 /* 114 */ "steeldrm",	/* 115 */ "woodblk",	/* 116 */ "taiko",
 /* 117 */ "toms",	/* 118 */ "syntom",	/* 119 */ "revcym",
 /* 120 */ "fx-fret",	/* 121 */ "fx-blow",	/* 122 */ "seashore",
 /* 123 */ "jungle",	/* 124 */ "telephon",	/* 125 */ "helicptr",
 /* 126 */ "applause",	/* 127 */ "ringwhsl",
/* [Drum Patches] */
 /* C 0 */ NULL,	/* C#0 */ NULL,		/* D 0 */ NULL,
 /* D#0 */ NULL,	/* E 0 */ NULL,		/* F 0 */ NULL,
 /* F#0 */ NULL,	/* G 0 */ NULL,		/* G#0 */ NULL,
 /* A 0 */ NULL,	/* A#0 */ NULL,		/* B 0 */ NULL,
 /* C 1 */ NULL,	/* C#1 */ NULL,		/* D 1 */ NULL,
 /* D#1 */ NULL,	/* E 1 */ NULL,		/* F 1 */ NULL,
 /* F#1 */ NULL,	/* G 1 */ NULL,		/* G#1 */ NULL,
 /* A 1 */ NULL,	/* A#1 */ NULL,		/* B 1 */ NULL,
 /* C 2 */ NULL,	/* C#2 */ NULL,		/* D 2 */ NULL,
 /* D#2 */ "highq",	/* E 2 */ "slap",	/* F 2 */ "scratch1",
 /* F#2 */ "scratch2",	/* G 2 */ "sticks",	/* G#2 */ "sqrclick",
 /* A 2 */ "metclick",	/* A#2 */ "metbell",	/* B 2 */ "kick1",
 /* C 3 */ "kick2",	/* C#3 */ "stickrim",	/* D 3 */ "snare1",
 /* D#3 */ "claps",	/* E 3 */ "snare2",	/* F 3 */ "tomlo2",
 /* F#3 */ "hihatcl",	/* G 3 */ "tomlo1",	/* G#3 */ "hihatpd",
 /* A 3 */ "tommid2",	/* A#3 */ "hihatop",	/* B 3 */ "tommid1",
 /* C 4 */ "tomhi2",	/* C#4 */ "cymcrsh1",	/* D 4 */ "tomhi1",
 /* D#4 */ "cymride1",	/* E 4 */ "cymchina",	/* F 4 */ "cymbell",
 /* F#4 */ "tamborin",	/* G 4 */ "cymsplsh",	/* G#4 */ "cowbell",
 /* A 4 */ "cymcrsh2",	/* A#4 */ "vibslap",	/* B 4 */ "cymride2",
 /* C 5 */ "bongohi",	/* C#5 */ "bongolo",	/* D 5 */ "congahi1",
 /* D#5 */ "congahi2",	/* E 5 */ "congalo",	/* F 5 */ "timbaleh",
 /* F#5 */ "timbalel",	/* G 5 */ "agogohi",	/* G#5 */ "agogolo",
 /* A 5 */ "cabasa",	/* A#5 */ "maracas",	/* B 5 */ "whistle1",
 /* C 6 */ "whistle2",	/* C#6 */ "guiro1",	/* D 6 */ "guiro2",
 /* D#6 */ "clave",	/* E 6 */ "woodblk1",	/* F 6 */ "woodblk2",
 /* F#6 */ "cuica1",	/* G 6 */ "cuica2",	/* G#6 */ "triangl1",
 /* A 6 */ "triangl2",	/* A#6 */ "shaker",	/* B 6 */ "jingles",
 /* C 7 */ "belltree",	/* C#7 */ "castinet",	/* D 7 */ "surdo1",
 /* D#7 */ "surdo2",	/* E 7 */ NULL,		/* F 7 */ NULL,
 /* F#7 */ NULL,	/* G 7 */ NULL,		/* G#7 */ NULL,
 /* A 7 */ NULL,	/* A#7 */ NULL,		/* B 7 */ NULL,
 /* C 8 */ NULL,	/* C#8 */ NULL,		/* D 8 */ NULL,
 /* D#8 */ NULL,	/* E 8 */ NULL,		/* F 8 */ NULL,
 /* F#8 */ NULL,	/* G 8 */ NULL,		/* G#8 */ NULL,
 /* A 8 */ NULL,	/* A#8 */ NULL,		/* B 8 */ NULL,
 /* C 9 */ NULL,	/* C#9 */ NULL,		/* D 9 */ NULL,
 /* D#9 */ NULL,	/* E 9 */ NULL,		/* F 9 */ NULL,
 /* F#9 */ NULL,	/* G 9 */ NULL,		/* G#9 */ NULL,
 /* A 9 */ NULL,	/* A#9 */ NULL,		/* B 9 */ NULL,
 /* C 10*/ NULL,	/* C#10*/ NULL,		/* D 10*/ NULL,
 /* D#10*/ NULL,	/* E 10*/ NULL,		/* F 10*/ NULL,
 /* F#10*/ NULL,	/* G 10*/ NULL
};
