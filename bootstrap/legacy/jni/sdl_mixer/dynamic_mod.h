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

#ifdef MOD_MUSIC

#include "mikmod.h"

typedef struct {
	int loaded;
	void *handle;

	void (*MikMod_Exit)(void);
	CHAR* (*MikMod_InfoDriver)(void);
	CHAR* (*MikMod_InfoLoader)(void);
	BOOL (*MikMod_Init)(CHAR*);
	void (*MikMod_RegisterAllLoaders)(void);
	void (*MikMod_RegisterDriver)(struct MDRIVER*);
	int* MikMod_errno;
	char* (*MikMod_strerror)(int);
	BOOL (*Player_Active)(void);
	void (*Player_Free)(MODULE*);
	MODULE* (*Player_LoadGeneric)(MREADER*,int,BOOL);
	void (*Player_SetPosition)(UWORD);
	void (*Player_SetVolume)(SWORD);
	void (*Player_Start)(MODULE*);
	void (*Player_Stop)(void);
	ULONG (*VC_WriteBytes)(SBYTE*,ULONG);
	struct MDRIVER* drv_nos;
	UWORD* md_device;
	UWORD* md_mixfreq;
	UWORD* md_mode;
	UBYTE* md_musicvolume;
	UBYTE* md_pansep;
	UBYTE* md_reverb;
	UBYTE* md_sndfxvolume;
	UBYTE* md_volume;
} mikmod_loader;

extern mikmod_loader mikmod;

#endif /* MOD_MUSIC */

extern int Mix_InitMOD();
extern void Mix_QuitMOD();
