/************************************************************************
   emumidi.h  -- tables and includes required by emumidi.c

   Copyright (C) 1994-1996 Nathan I. Laredo

   This program is modifiable/redistributable under the terms
   of the GNU General Public Licence.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 675 Mass Ave, Cambridge, MA  2139, USA.
   Send your comments and all your spare pocket change to
   laredo@gnu.ai.mit.edu (Nathan Laredo) or to PSC 1, BOX 709, 2401
   Kelly Drive, Lackland AFB, TX 78236-5128, USA.
 *************************************************************************/
#include "playmidi.h"
#ifdef linux
#include <linux/ultrasound.h>
#else
#include <machine/ultrasound.h>
#endif

/*
 * TABLE OF NEARLY EXACT FREQUENCIES FOR ALL MIDI NOTES (A=440Hz)
 * the whole table is really not necessary, but it prevents some
 * rounding errors by having it complete, and the cost of 128
 * integers is cheaper than the cpu cost of multiple right shifts
 * of a table of twelve frequencies, and definately cheaper than
 * calculating freq = 13.75 * 2^((n + 4)/12) for each note value,
 * which is how this table was created.
 */

unsigned int n_freq[128] =
{
/* C     C#    D     D#    E     F     F#    G     G#    A     A#    B */
   16,   17,   18,   19,   21,   22,   23,   24,   26,   28,   29,   31,
   33,   34,   37,   39,   41,   44,   46,   49,   52,   55,   58,   62,
   65,   69,   73,   78,   82,   87,   92,   98,  103,  110,  117,  123,
  131,  139,  147,  156,  165,  175,  185,  195,  207,  220,  233,  247,
  262,  277,  294,  311,  330,  349,  370,  392,  415,  440,  466,  494,
  523,  554,  587,  622,  659,  698,  740,  784,  831,  880,  932,  988,
 1047, 1109, 1175, 1245, 1319, 1397, 1480, 1568, 1661, 1760, 1865, 1976,
 2093, 2217, 2349, 2489, 2637, 2794, 2960, 3136, 3322, 3520, 3729, 3951,
 4186, 4435, 4699, 4978, 5274, 5588, 5920, 6272, 6645, 7040, 7459, 7902,
 8372, 8870, 9397, 9956,10548,11175,11840,12544,13290,14080,14917,15804,
16744,17740,18795,19912,21096,22351,23680,25088
};

/* MT-32 emulation translate table */
int mt32pgm[128] =
{
   0,   1,   2,   4,   4,   5,   5,   3,  16,  16,  16,  16,  19,
  19,  19,  21,   6,   6,   6,   7,   7,   7,   8,   8,  62,  57,
  63,  58,  38,  38,  39,  39,  88,  33,  52,  35,  97, 100,  38,
  39,  14, 102,  68, 103,  44,  92,  46,  80,  48,  49,  51,  45,
  40,  40,  42,  42,  43,  46,  46,  24,  25,  28,  27, 104,  32,
  32,  34,  33,  36,  37,  39,  35,  79,  73,  76,  72,  74,  75,
  64,  65,  66,  67,  71,  71,  69,  70,  60,  22,  56,  59,  57,
  63,  60,  60,  58,  61,  61,  11,  11,  99, 100,   9,  14,  13,
  12, 107, 106,  77,  78,  78,  76, 111,  47, 117, 127, 115, 118,
 116, 118, 126, 121, 121,  55, 124, 120, 125, 126, 127
};

