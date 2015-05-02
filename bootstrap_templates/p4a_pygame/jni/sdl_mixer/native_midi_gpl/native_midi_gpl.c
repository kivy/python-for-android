/***************************************************************************
                           native_midi_lnx.c
			   -----------------
			   
    copyright            : (C) 2002 by Peter Ku»ák
    email                : kutak@stonline.sk
 ***************************************************************************/

/* in this file is used code from PlayMidi    Copyright (C) 1994-1996 Nathan I. Laredo */

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#if defined(linux) || defined(__FreeBSD__)

#ifndef __FreeBSD__
#include <getopt.h>
#endif
#include <fcntl.h>
#include <ctype.h>
#include <unistd.h>
#include <sys/stat.h>
#include <string.h>
#include "SDL_thread.h"
#include "native_midi.h"
#include "playmidi.h"

SEQ_DEFINEBUF(SEQUENCERBLOCKSIZE);

int play_fm = 0, play_gus = 0, play_ext = 0, play_awe = 0;
int opl3_patch_aviable = 0, fm_patch_aviable = 0;

struct miditrack seq[MAXTRKS];
struct synth_info card_info[MAX_CARDS];

int FORCE_EXT_DEV = -1;
int chanmask = 0xffff, perc = PERCUSSION;
int dochan = 1, force8bit = 0, wantopl3 = FM_DEFAULT_MODE;
int patchloaded[256], fmloaded[256], useprog[16], usevol[16]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
int reverb = 0, chorus = 0, nrsynths, nrmidis;
int sb_dev = -1, gus_dev = -1, ext_dev = -1, awe_dev = -1, p_remap = 0;
int seqfd,  MT32 = 0;
FILE *mfd;
unsigned long int default_tempo;
float skew = 1.0;
char ImPlaying = 0;
SDL_Thread *playevents_thread=NULL;

extern int ntrks;
extern char *gmvoice[256];
extern int mt32pgm[128];
extern int note_vel[16][128];
extern int playevents();
extern int gus_load(int);
extern int readmidi(unsigned char *, off_t);
extern void loadfm();

void seqbuf_dump();
int synth_setup();

struct _NativeMidiSong
{
    char *filebuf;
    unsigned long int file_size;
};

int native_midi_detect()
{

    int sbfd;
    int ret=0;    

    /* Open sequencer device */
    if ((seqfd = open(SEQUENCER_DEV, O_WRONLY, 0)) < 0) 
    {
	perror("open " SEQUENCER_DEV);
	return 0;
    }

    gus_dev = -1;
    sb_dev = -1;
    ext_dev = -1;
    awe_dev = -1;
    play_fm = 0;
    play_gus = 0;
    play_ext = 0;
    play_awe = 0;
    
    opl3_patch_aviable = 0;
    fm_patch_aviable = 0;

    sbfd = open(SBMELODIC, O_RDONLY, 0);
    if (sbfd != -1)
    {
	close(sbfd);
	sbfd = open(SBDRUMS, O_RDONLY, 0);
	if (sbfd != -1)
	{
            close(sbfd);
	    fm_patch_aviable = 1;
	}
    }

    sbfd = open(O3MELODIC, O_RDONLY, 0);
    if (sbfd != -1)
    {
        close(sbfd);
        sbfd = open(O3DRUMS, O_RDONLY, 0);
	if (sbfd != -1)
	{
            close(sbfd);
	    opl3_patch_aviable = 1;
	}
    }

    ret=synth_setup();

    /* Close sequencer device */
    close(seqfd);

    return ret;
}

NativeMidiSong *native_midi_loadsong(const char *midifile)
{
    NativeMidiSong	*song = NULL;
    char 		*extra;
    int 		piped = 0;
    struct stat 	info;

    song = malloc(sizeof(NativeMidiSong));
    if (!song)
    {
	return NULL;
    };
    if (stat(midifile, &info) == -1) 
    {
        if ((extra = malloc(strlen(midifile) + 4)) == NULL)
        {
	    goto end;
	}
	sprintf(extra, "%s.mid", midifile);
	if (stat(extra, &info) == -1)
	{
	    free(extra);
	    goto end;
	}
	if ((mfd = fopen(extra, "r")) == NULL)
	{
	    free(extra);
	    goto end;
	}
	free(extra);
    } else
    {
        char *ext = strrchr(midifile, '.');
        if (ext && strcmp(ext, ".gz") == 0) 
	{
	    char temp[1024];
	    piped = 1;
	    sprintf(temp, "gzip -l %s", midifile);
	    if ((mfd = popen(temp, "r")) == NULL)
	    {
	        goto end;
	    }
	    fgets(temp, sizeof(temp), mfd); /* skip 1st line */
	    fgets(temp, sizeof(temp), mfd);
	    strtok(temp, " "); /* compressed size */
	    info.st_size = atoi(strtok(NULL, " ")); /* original size */
	    pclose(mfd);
	    sprintf(temp, "gzip -d -c %s",midifile);
	    if ((mfd = popen(temp, "r")) == NULL)
	    {
	        goto end;
	    }
	}else if ((mfd = fopen(midifile, "r")) == NULL)
	{
	    goto end;
	}
    }
    if ((song->filebuf = malloc(info.st_size)) == NULL)
    {
        if (piped)
        {
	    pclose(mfd);
	}else
	{
	    fclose(mfd);
	}
	goto end;
    }
    song->file_size=info.st_size;
    fread(song->filebuf, 1, info.st_size, mfd);
    if (piped)
    {
        pclose(mfd);
    } else
    {
        fclose(mfd);
    }
    
  return song;

end:
    free(song);
    return NULL;
}

NativeMidiSong *native_midi_loadsong_RW(SDL_RWops *rw)
{
	NativeMidiSong	*song = NULL;
	char 		*extra;

	song = malloc(sizeof(NativeMidiSong));
	if (!song) {
		return NULL;
	};

	SDL_RWseek(rw, 0, RW_SEEK_END);
	song->file_size = SDL_RWtell(rw);
	SDL_RWseek(rw, 0, RW_SEEK_SET);

	song->filebuf = malloc(song->file_size);
	if (!song->filebuf) {
		free(song);
		return NULL;
	}

	SDL_RWread(rw, song->filebuf, song->file_size, 1);
	return song;
}

void native_midi_freesong(NativeMidiSong *song)
{
    free(song->filebuf);
    free(song);
}

void native_midi_start(NativeMidiSong *song)
{

    int i, error = 0, j;

    for (i = 0; i < 16; i++)
    {
	useprog[i] = 0;	/* reset options */
    }
    
    /* Open sequencer device */
    if ((seqfd = open(SEQUENCER_DEV, O_WRONLY, 0)) < 0) 
    {
	perror("open " SEQUENCER_DEV);
	goto eend;
    }
    if(!synth_setup()) { goto end;};


	    if (play_gus)
	    {
		gus_load(-1);
	    }
	    default_tempo = 500000;
	    /* error holds number of tracks read */
	    error = readmidi(song->filebuf, song->file_size);
	    if (play_gus && error > 0) 
	    {
		int i;		/* need to keep other i safe */
#define CMD (seq[i].data[j] & 0xf0)
#define CHN (seq[i].data[j] & 0x0f)
#define PGM (seq[i].data[j + 1])
		/* REALLY STUPID way to preload GUS, but it works */
		for (i = 0; i < ntrks; i++)
		    for (j = 0; j < seq[i].length - 5; j++)
			if (ISGUS(CHN) && !(PGM & 0x80) &&
			    ((CMD == MIDI_PGM_CHANGE && !ISPERC(CHN))
			     || (CMD == MIDI_NOTEON && ISPERC(CHN))))
			    gus_load(ISPERC(CHN) ? PGM + 128 :
				     useprog[CHN] ? useprog[CHN] - 1 :
				     MT32 ? mt32pgm[PGM] : PGM);
		/* make sure that some program was loaded to use */
		for (j = 0; patchloaded[j] != 1 && j < 128; j++);
		if (j > 127)
		    gus_load(0);
	    }
				/* if there's an error skip to next file */
	    if (error > 0)	/* error holds number of tracks read */
	    {
		ImPlaying=1;
	    	playevents_thread=SDL_CreateThread(playevents,NULL);
	    }

end:
eend:
	    return;
}

void native_midi_stop()
{
    /* Close sequencer device */
    close(seqfd);
}

int native_midi_active()
{
    return ImPlaying;
}

void native_midi_setvolume(int volume)
{
}

const char *native_midi_error(void)
{
  return "stala sa chyba";
}

void seqbuf_dump()
{
    if (_seqbufptr)
	if (write(seqfd, _seqbuf, _seqbufptr) == -1) {
	    perror("write " SEQUENCER_DEV);
	    return;
	}
    _seqbufptr = 0;
}

int synth_setup()
{
    int i;
    char *nativemusicenv = getenv("SDL_NATIVE_MUSIC");
    char *extmidi=getenv("SDL_NATIVE_MUSIC_EXT");

    if(extmidi)
    {
	
    	FORCE_EXT_DEV = atoi(extmidi);
	printf("EXT midi %s , %d \n",extmidi,FORCE_EXT_DEV);
    }
    
    if (ioctl(seqfd, SNDCTL_SEQ_NRSYNTHS, &nrsynths) == -1) 
    {
	fprintf(stderr, "there is no soundcard\n");
	return 0;
    }
    for (i = 0; i < nrsynths; i++) 
    {
	card_info[i].device = i;
	if (ioctl(seqfd, SNDCTL_SYNTH_INFO, &card_info[i]) == -1) 
	{
	    fprintf(stderr, "cannot get info on soundcard\n");
	    perror(SEQUENCER_DEV);
	    return 0;
	}
	card_info[i].device = i;
	if (card_info[i].synth_type == SYNTH_TYPE_SAMPLE
	    && card_info[i].synth_subtype == SAMPLE_TYPE_GUS)
	{
	    gus_dev = i;
	}else if (card_info[i].synth_type == SYNTH_TYPE_SAMPLE
	    && card_info[i].synth_subtype == SAMPLE_TYPE_AWE32)
	{
	    awe_dev = i;
	}else if (card_info[i].synth_type == SYNTH_TYPE_FM) 
	{
	    sb_dev = i;
	    if (play_fm)
		loadfm();
	    if (wantopl3) 
	    {
		card_info[i].nr_voices = 12;	/* we have 12 with 4-op */
	    }
	}
    }

    if (gus_dev >= 0) {
	if (ioctl(seqfd, SNDCTL_SEQ_RESETSAMPLES, &gus_dev) == -1) 
	{
	    perror("Sample reset");
	    return 0;
	}
    }
    if (ioctl(seqfd, SNDCTL_SEQ_NRMIDIS, &nrmidis) == -1) 
    {
	fprintf(stderr, "can't get info about midi ports\n");
	return 0;
    }
    if (nrmidis > 0) {
	if (FORCE_EXT_DEV >= 0)
	    ext_dev = FORCE_EXT_DEV;
	else
	    ext_dev = nrmidis - 1;
    }

    if( nativemusicenv ) /* select device by SDL_NATIVE_MUSIC */
    {
	if(strcasecmp(nativemusicenv,"GUS") == 0)
	{
    	    if( gus_dev >= 0 )
	    {
    		play_gus = -1;
	        awe_dev = -1;
		sb_dev  = -1;
	        ext_dev = -1;
	        return 1;
            }else
	    {
    		play_gus = 0;
		return 0;
	    }
	}else if(strcasecmp(nativemusicenv,"AWE") == 0)
	{
    	    if( awe_dev >= 0 )
	    {
    		play_awe = -1;
	        gus_dev = -1;
		sb_dev  = -1;
	        ext_dev = -1;
	        return 1;
            }else
	    {
    		play_awe = 0;
		return 0;
	    }
	}else if(strcasecmp(nativemusicenv,"FM") == 0)
	{
    	    if( sb_dev >= 0 && fm_patch_aviable )
	    {
    		play_fm = -1;
		gus_dev = -1;
	        awe_dev = -1;
	        ext_dev = -1;
	        wantopl3 = 0;
	        return 1;
            }else
	    {
    		play_fm = 0;
		return 0;
	    }
	}else if(strcasecmp(nativemusicenv,"OPL3") == 0)
	{
    	    if( sb_dev >= 0 && opl3_patch_aviable )
	    {
    		play_fm = -1;
		gus_dev = -1;
	        awe_dev = -1;
	        ext_dev = -1;
	        wantopl3 = 1;
	        return 1;
            }else
	    {
    		play_fm = 0;
		return 0;
	    }
	}else if(strcasecmp(nativemusicenv,"EXT") == 0)
	{
    	    if( ext_dev >= 0 )
	    {
    		play_ext = -1;
	        gus_dev = -1;
	        awe_dev = -1;
		sb_dev  = -1;
	        return 1;
            }else
	    {
    		play_ext = 0;
		return 0;
	    }
	}
    }
    /* autoselect best device */
    if( gus_dev >= 0 )
    {
        play_gus = -1;
        awe_dev = -1;
        sb_dev  = -1;
        ext_dev = -1;
        return 1;
        }
    if( awe_dev >= 0 )
    {
        play_awe = -1;
	gus_dev = -1;
        sb_dev  = -1;
        ext_dev = -1;
        return 1;
    }
    if( sb_dev >= 0 && fm_patch_aviable )
    {
        play_fm = -1;
	gus_dev = -1;
        awe_dev = -1;
        ext_dev = -1;
        return 2;	/* return 1 if use FM befor Timidity */
    }
    if( ext_dev >= 0 )
    {
        play_ext = -1;
	gus_dev = -1;
        awe_dev = -1;
        sb_dev  = -1;
        return 3;
    }
    return 0;
}

#endif /* linux || FreeBSD */
