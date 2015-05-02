/*
    SDL - Simple DirectMedia Layer
    Copyright (C) 1997-2009 Sam Lantinga

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

    Sam Lantinga
    slouken@libsdl.org
*/

#ifndef _SDL_config_android_h
#define _SDL_config_android_h

#include "SDL_platform.h"

/* This is the minimal configuration that can be used to build SDL */

#include <stdarg.h>
#include <stdint.h>
#include <sys/mman.h>

#define SDL_VIDEO_DRIVER_ANDROID 1
#define SDL_VIDEO_OPENGL_ES 1
#define SDL_VIDEO_RENDER_OGL_ES 1

#define SDL_AUDIO_DRIVER_ANDROID 1

#define SDL_CDROM_DISABLED 1

#define SDL_JOYSTICK_ANDROID 1

#define SDL_HAPTIC_DUMMY 1 // TODO: add vibrator and remove that
#define SDL_HAPTIC_ANDROID 1

#define SDL_POWER_DISABLED 1 // TODO: add battery meter and remove that
#define SDL_POWER_ANDROID 1
#undef SDL_POWER_LINUX

#define SDL_LOADSO_DLOPEN 1

#define SDL_THREAD_PTHREAD 1
#define SDL_THREAD_PTHREAD_RECURSIVE_MUTEX 1

#define SDL_TIMER_UNIX 1

#define HAVE_STDIO_H 1


#define SIZEOF_VOIDP 4
#define SDL_HAS_64BIT_TYPE 1

/* FireSlash found that SDL native memcpy crashes sometimes, these defines fix it (and they are faster) */
#define HAVE_LIBC 1

#define HAVE_ALLOCA_H 1
#define HAVE_SYS_TYPES_H 1
#define HAVE_STDIO_H 1
#define STDC_HEADERS 1
#define HAVE_STDLIB_H 1
#define HAVE_STDARG_H 1
#define HAVE_MALLOC_H 1
#define HAVE_MEMORY_H 1
#define HAVE_STRING_H 1
#define HAVE_STRINGS_H 1
#define HAVE_INTTYPES_H 1
#define HAVE_STDINT_H 1
#define HAVE_CTYPE_H 1
#define HAVE_MATH_H 1
#undef HAVE_ICONV_H
#define HAVE_SIGNAL_H 1
#undef HAVE_ALTIVEC_H

#define HAVE_MALLOC 1
#define HAVE_CALLOC 1
#define HAVE_REALLOC 1
#define HAVE_FREE 1
#define HAVE_ALLOCA 1
#define HAVE_GETENV 1
#define HAVE_PUTENV 1
#define HAVE_UNSETENV 1
#define HAVE_QSORT 1
#define HAVE_ABS 1
#define HAVE_BCOPY 1
#define HAVE_MEMSET 1
#define HAVE_MEMCPY 1
#define HAVE_MEMMOVE 1
#define HAVE_MEMCMP 1
#define HAVE_STRLEN 1
#define HAVE_STRLCPY 1
#define HAVE_STRLCAT 1
#define HAVE_STRDUP 1
#undef HAVE__STRREV
#undef HAVE__STRUPR
#undef HAVE__STRLWR
#define HAVE_INDEX 1
#define HAVE_RINDEX 1
#define HAVE_STRCHR 1
#define HAVE_STRRCHR 1
#define HAVE_STRSTR 1
#undef HAVE_ITOA
#undef HAVE__LTOA
#undef HAVE__UITOA
#undef HAVE__ULTOA
#define HAVE_STRTOL
#define HAVE_STRTOUL
#undef HAVE__I64TOA
#undef HAVE__UI64TOA
#define HAVE_STRTOLL 1
#define HAVE_STRTOULL 1
#define HAVE_STRTOD 1
#define HAVE_ATOI 1
#define HAVE_ATOF 1
#define HAVE_STRCMP 1
#define HAVE_STRNCMP 1
#undef HAVE__STRICMP
#define HAVE_STRCASECMP 1
#undef HAVE__STRNICMP
#define HAVE_STRNCASECMP 1
#define HAVE_SSCANF 1
#define HAVE_SNPRINTF 1
#define HAVE_VSNPRINTF 1
#undef HAVE_ICONV
#define HAVE_SIGACTION 1
#define HAVE_SETJMP 1
#define HAVE_NANOSLEEP 1
#define HAVE_CLOCK_GETTIME 1
#define HAVE_GETPAGESIZE 1
#define HAVE_MPROTECT 1

#define HAVE_CEIL 1
#define HAVE_COPYSIGN 1
#define HAVE_COS 1
#define HAVE_COSF 1
#define HAVE_FABS 1
#define HAVE_FLOOR 1
#define HAVE_LOG 1
#define HAVE_M_PI 1
#define HAVE_POW 1
#define HAVE_SCALBN 1
#define HAVE_SETENV 1
#define HAVE_SIN 1
#define HAVE_SINF 1
#define HAVE_SQRT 1
#define HAVE_SYSCONF 1
#undef HAVE_SYSCTLBYNAME
#undef SDL_ALTIVEC_BLITTERS
#define SDL_ASSEMBLY_ROUTINES 1 // There is no assembly code for Arm CPU yet

#endif /* _SDL_config_minimal_h */
