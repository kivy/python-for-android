/*
    SDL_mixer:  An audio mixer library based on the SDL library
    Copyright (C) 1997-2009 Sam Lantinga

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Library General Public
    License as published by the Free Software Foundation; either
    version 2 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Library General Public License for more details.

    You should have received a copy of the GNU Library General Public
    License along with this library; if not, write to the Free
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

    This file by Ryan C. Gordon (icculus@icculus.org)

    These are some helper functions for the internal mixer special effects.
*/

/* $Id: effects_internal.c 4211 2008-12-08 00:27:32Z slouken $ */


     /* ------ These are used internally only. Don't touch. ------ */



#include <stdio.h>
#include <stdlib.h>
#include "SDL_mixer.h"

#define __MIX_INTERNAL_EFFECT__
#include "effects_internal.h"

/* Should we favor speed over memory usage and/or quality of output? */
int _Mix_effects_max_speed = 0;


void _Mix_InitEffects(void)
{
    _Mix_effects_max_speed = (getenv(MIX_EFFECTSMAXSPEED) != NULL);
}

void _Mix_DeinitEffects(void)
{
    _Eff_PositionDeinit();
}


void *_Eff_volume_table = NULL;


/* Build the volume table for Uint8-format samples.
 *
 * Each column of the table is a possible sample, while each row of the
 *  table is a volume. Volume is a Uint8, where 0 is silence and 255 is full
 *  volume. So _Eff_volume_table[128][mysample] would be the value of
 *  mysample, at half volume.
 */
void *_Eff_build_volume_table_u8(void)
{
    int volume;
    int sample;
    Uint8 *rc;

    if (!_Mix_effects_max_speed) {
        return(NULL);
    }

    if (!_Eff_volume_table) {
        rc = malloc(256 * 256);
        if (rc) {
            _Eff_volume_table = (void *) rc;
            for (volume = 0; volume < 256; volume++) {
                for (sample = -128; sample < 128; sample ++) {
                    *rc = (Uint8)(((float) sample) * ((float) volume / 255.0)) 
                        + 128;
                    rc++;
                }
            }
        }
    }

    return(_Eff_volume_table);
}


/* Build the volume table for Sint8-format samples.
 *
 * Each column of the table is a possible sample, while each row of the
 *  table is a volume. Volume is a Uint8, where 0 is silence and 255 is full
 *  volume. So _Eff_volume_table[128][mysample+128] would be the value of
 *  mysample, at half volume.
 */
void *_Eff_build_volume_table_s8(void)
{
    int volume;
    int sample;
    Sint8 *rc;

    if (!_Eff_volume_table) {
        rc = malloc(256 * 256);
        if (rc) {
            _Eff_volume_table = (void *) rc;
            for (volume = 0; volume < 256; volume++) {
                for (sample = -128; sample < 128; sample ++) {
                    *rc = (Sint8)(((float) sample) * ((float) volume / 255.0));
                    rc++;
                }
            }
        }
    }

    return(_Eff_volume_table);
}


/* end of effects.c ... */

