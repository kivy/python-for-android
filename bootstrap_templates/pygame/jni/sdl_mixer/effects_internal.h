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

    Sam Lantinga
    slouken@libsdl.org
*/

/* $Id: effects_internal.h 5045 2009-10-11 02:59:12Z icculus $ */

#ifndef _INCLUDE_EFFECTS_INTERNAL_H_
#define _INCLUDE_EFFECTS_INTERNAL_H_

#ifndef __MIX_INTERNAL_EFFECT__
#error You should not include this file or use these functions.
#endif

#include "SDL_mixer.h"

/* Set up for C function definitions, even when using C++ */
#ifdef __cplusplus
extern "C" {
#endif

extern int _Mix_effects_max_speed;
extern void *_Eff_volume_table;
void *_Eff_build_volume_table_u8(void);
void *_Eff_build_volume_table_s8(void);

void _Mix_InitEffects(void);
void _Mix_DeinitEffects(void);
void _Eff_PositionDeinit(void);

int _Mix_RegisterEffect_locked(int channel, Mix_EffectFunc_t f,
                               Mix_EffectDone_t d, void *arg);
int _Mix_UnregisterEffect_locked(int channel, Mix_EffectFunc_t f);
int _Mix_UnregisterAllEffects_locked(int channel);


/* Set up for C function definitions, even when using C++ */
#ifdef __cplusplus
}
#endif


#endif

