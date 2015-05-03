/*
 *  IMG_ImageIO.c
 *  SDL_image
 *
 *  Created by Eric Wing on 1/1/09.
 *  Copyright 2009 __MyCompanyName__. All rights reserved.
 *
 */

#if defined(__APPLE__) && !defined(SDL_IMAGE_USE_COMMON_BACKEND)

#include "SDL_image.h"

// For ImageIO framework and also LaunchServices framework (for UTIs)
#include <ApplicationServices/ApplicationServices.h>
// Used because CGDataProviderCreate became deprecated in 10.5
#include <AvailabilityMacros.h>

/**************************************************************
 ***** Begin Callback functions for block reading *************
 **************************************************************/

// This callback reads some bytes from an SDL_rwops and copies it
// to a Quartz buffer (supplied by Apple framework).
static size_t MyProviderGetBytesCallback(void* rwops_userdata, void* quartz_buffer, size_t the_count)
{
	return (size_t)SDL_RWread((struct SDL_RWops *)rwops_userdata, quartz_buffer, 1, the_count);
}

// This callback is triggered when the data provider is released
// so you can clean up any resources.
static void MyProviderReleaseInfoCallback(void* rwops_userdata)
{
	// What should I put here? 
	// I think the user and SDL_RWops controls closing, so I don't do anything.
}

static void MyProviderRewindCallback(void* rwops_userdata)
{
	SDL_RWseek((struct SDL_RWops *)rwops_userdata, 0, RW_SEEK_SET);
}

#if MAC_OS_X_VERSION_MAX_ALLOWED >= 1050 // CGDataProviderCreateSequential was introduced in 10.5; CGDataProviderCreate is deprecated
off_t MyProviderSkipForwardBytesCallback(void* rwops_userdata, off_t the_count)
{
	off_t start_position = SDL_RWtell((struct SDL_RWops *)rwops_userdata);
	SDL_RWseek((struct SDL_RWops *)rwops_userdata, the_count, RW_SEEK_CUR);
    off_t end_position = SDL_RWtell((struct SDL_RWops *)rwops_userdata);
    return (end_position - start_position);	
}
#else // CGDataProviderCreate was deprecated in 10.5
static void MyProviderSkipBytesCallback(void* rwops_userdata, size_t the_count)
{
	SDL_RWseek((struct SDL_RWops *)rwops_userdata, the_count, RW_SEEK_CUR);
}
#endif


/**************************************************************
 ***** End Callback functions for block reading ***************
 **************************************************************/

// This creates a CGImageSourceRef which is a handle to an image that can be used to examine information
// about the image or load the actual image data.
static CGImageSourceRef CreateCGImageSourceFromRWops(SDL_RWops* rw_ops, CFDictionaryRef hints_and_options)
{
	CGImageSourceRef source_ref;

	// Similar to SDL_RWops, Apple has their own callbacks for dealing with data streams.
	
#if MAC_OS_X_VERSION_MAX_ALLOWED >= 1050 // CGDataProviderCreateSequential was introduced in 10.5; CGDataProviderCreate is deprecated
	CGDataProviderSequentialCallbacks provider_callbacks =
	{
        0,
		MyProviderGetBytesCallback,
		MyProviderSkipForwardBytesCallback,
		MyProviderRewindCallback,
		MyProviderReleaseInfoCallback
	};
	
	CGDataProviderRef data_provider = CGDataProviderCreateSequential(rw_ops, &provider_callbacks);
	
	
#else // CGDataProviderCreate was deprecated in 10.5
	
	CGDataProviderCallbacks provider_callbacks =
	{
		MyProviderGetBytesCallback,
		MyProviderSkipBytesCallback,
		MyProviderRewindCallback,
		MyProviderReleaseInfoCallback
	};
	
	CGDataProviderRef data_provider = CGDataProviderCreate(rw_ops, &provider_callbacks);
#endif
	// Get the CGImageSourceRef.
	// The dictionary can be NULL or contain hints to help ImageIO figure out the image type.
	source_ref = CGImageSourceCreateWithDataProvider(data_provider, hints_and_options);
	return source_ref;
}


/* Create a CGImageSourceRef from a file. */
/* Remember to CFRelease the created source when done. */
static CGImageSourceRef CreateCGImageSourceFromFile(const char* the_path)
{
    CFURLRef the_url = NULL;
    CGImageSourceRef source_ref = NULL;
	CFStringRef cf_string = NULL;
	
	/* Create a CFString from a C string */
	cf_string = CFStringCreateWithCString(
										  NULL,
										  the_path,
										  kCFStringEncodingUTF8
										  );
	if(!cf_string)
	{
		return NULL;
	}
	
	/* Create a CFURL from a CFString */
    the_url = CFURLCreateWithFileSystemPath(
											NULL, 
											cf_string,
											kCFURLPOSIXPathStyle,
											false
											);
	
	/* Don't need the CFString any more (error or not) */
	CFRelease(cf_string);
	
	if(!the_url)
	{
		return NULL;
	}
	
	
    source_ref = CGImageSourceCreateWithURL(the_url, NULL);
	/* Don't need the URL any more (error or not) */
	CFRelease(the_url);
	
	return source_ref;
}



static CGImageRef CreateCGImageFromCGImageSource(CGImageSourceRef image_source)
{
	CGImageRef image_ref = NULL;
	
    if(NULL == image_source)
	{
		return NULL;
	}
	
	// Get the first item in the image source (some image formats may
	// contain multiple items).
	image_ref = CGImageSourceCreateImageAtIndex(image_source, 0, NULL);
	return image_ref;
}

static CFDictionaryRef CreateHintDictionary(CFStringRef uti_string_hint)
{
	CFDictionaryRef hint_dictionary = NULL;

	if(uti_string_hint != NULL)
	{
		// Do a bunch of work to setup a CFDictionary containing the jpeg compression properties.
		CFStringRef the_keys[1];
		CFStringRef the_values[1];
		
		the_keys[0] = kCGImageSourceTypeIdentifierHint;
		the_values[0] = uti_string_hint;
		
		// kCFTypeDictionaryKeyCallBacks or kCFCopyStringDictionaryKeyCallBacks?
		hint_dictionary = CFDictionaryCreate(NULL, (const void**)&the_keys, (const void**)&the_values, 1, &kCFTypeDictionaryKeyCallBacks, &kCFTypeDictionaryValueCallBacks);
	}
	return hint_dictionary;
}




static int Internal_isType(SDL_RWops* rw_ops, CFStringRef uti_string_to_test)
{
	CGImageSourceRef image_source;
	CFStringRef uti_type;
	Boolean is_type;
	
	CFDictionaryRef hint_dictionary = NULL;
	
	hint_dictionary = CreateHintDictionary(uti_string_to_test);	
	image_source = CreateCGImageSourceFromRWops(rw_ops, hint_dictionary);
	
	if(hint_dictionary != NULL)
	{
		CFRelease(hint_dictionary);		
	}
	
	if(NULL == image_source)
	{
		return 0;
	}
	
	// This will get the UTI of the container, not the image itself.
	// Under most cases, this won't be a problem.
	// But if a person passes an icon file which contains a bmp,
	// the format will be of the icon file.
	// But I think the main SDL_image codebase has this same problem so I'm not going to worry about it.	
	uti_type = CGImageSourceGetType(image_source);
	//	CFShow(uti_type);
	
	// Unsure if we really want conformance or equality
	is_type = UTTypeConformsTo(uti_string_to_test, uti_type);
	
	CFRelease(image_source);
	
	return (int)is_type;
}

// Once we have our image, we need to get it into an SDL_Surface
static SDL_Surface* Create_SDL_Surface_From_CGImage(CGImageRef image_ref)
{
	/* This code is adapted from Apple's Documentation found here:
	 * http://developer.apple.com/documentation/GraphicsImaging/Conceptual/OpenGL-MacProgGuide/index.html
	 * Listing 9-4††Using a Quartz image as a texture source.
	 * Unfortunately, this guide doesn't show what to do about
	 * non-RGBA image formats so I'm making the rest up.
	 * All this code should be scrutinized.
	 */

	size_t w = CGImageGetWidth(image_ref);
	size_t h = CGImageGetHeight(image_ref);
	CGRect rect = {{0, 0}, {w, h}};

	CGImageAlphaInfo alpha = CGImageGetAlphaInfo(image_ref);
	//size_t bits_per_pixel = CGImageGetBitsPerPixel(image_ref);
	size_t bits_per_component = 8;

	SDL_Surface* surface;
	Uint32 Amask;
	Uint32 Rmask;
	Uint32 Gmask;
	Uint32 Bmask;

	CGContextRef bitmap_context;
	CGBitmapInfo bitmap_info;
	CGColorSpaceRef color_space = CGColorSpaceCreateDeviceRGB();

	if (alpha == kCGImageAlphaNone ||
	    alpha == kCGImageAlphaNoneSkipFirst ||
	    alpha == kCGImageAlphaNoneSkipLast) {
		bitmap_info = kCGImageAlphaNoneSkipFirst | kCGBitmapByteOrder32Host; /* XRGB */
		Amask = 0x00000000;
	} else {
		/* kCGImageAlphaFirst isn't supported */
		//bitmap_info = kCGImageAlphaFirst | kCGBitmapByteOrder32Host; /* ARGB */
		bitmap_info = kCGImageAlphaPremultipliedFirst | kCGBitmapByteOrder32Host; /* ARGB */
		Amask = 0xFF000000;
	}

	Rmask = 0x00FF0000;
	Gmask = 0x0000FF00;
	Bmask = 0x000000FF;

	surface = SDL_CreateRGBSurface(SDL_SWSURFACE, w, h, 32, Rmask, Gmask, Bmask, Amask);
	if (surface)
	{
		// Sets up a context to be drawn to with surface->pixels as the area to be drawn to
		bitmap_context = CGBitmapContextCreate(
															surface->pixels,
															surface->w,
															surface->h,
															bits_per_component,
															surface->pitch,
															color_space,
															bitmap_info
															);

		// Draws the image into the context's image_data
		CGContextDrawImage(bitmap_context, rect, image_ref);

		CGContextRelease(bitmap_context);

		// FIXME: Reverse the premultiplied alpha
		if ((bitmap_info & kCGBitmapAlphaInfoMask) == kCGImageAlphaPremultipliedFirst) {
			int i, j;
			Uint8 *p = (Uint8 *)surface->pixels;
			for (i = surface->h * surface->pitch/4; i--; ) {
#if __LITTLE_ENDIAN__
				Uint8 A = p[3];
				if (A) {
					for (j = 0; j < 3; ++j) {
						p[j] = (p[j] * 255) / A;
					}
				}
#else
				Uint8 A = p[0];
				if (A) {
					for (j = 1; j < 4; ++j) {
						p[j] = (p[j] * 255) / A;
					}
				}
#endif /* ENDIAN */
				p += 4;
			}
		}
	}

	if (color_space)
	{
		CGColorSpaceRelease(color_space);			
	}

	return surface;
}


static SDL_Surface* LoadImageFromRWops(SDL_RWops* rw_ops, CFStringRef uti_string_hint)
{
	SDL_Surface* sdl_surface;
	CGImageSourceRef image_source;
	CGImageRef image_ref = NULL;
	CFDictionaryRef hint_dictionary = NULL;

	hint_dictionary = CreateHintDictionary(uti_string_hint);
	image_source = CreateCGImageSourceFromRWops(rw_ops, hint_dictionary);

	if(hint_dictionary != NULL)
	{
		CFRelease(hint_dictionary);		
	}
	
	if(NULL == image_source)
	{
		return NULL;
	}
	
	image_ref = CreateCGImageFromCGImageSource(image_source);
	CFRelease(image_source);

	if(NULL == image_ref)
	{
		return NULL;
	}
	
	sdl_surface = Create_SDL_Surface_From_CGImage(image_ref);
	CFRelease(image_ref);
	return sdl_surface;
	
}



static SDL_Surface* LoadImageFromFile(const char* file)
{
	SDL_Surface* sdl_surface = NULL;
	CGImageSourceRef image_source = NULL;
	CGImageRef image_ref = NULL;
	
	// First ImageIO
	image_source = CreateCGImageSourceFromFile(file);
	
	if(NULL == image_source)
	{
		return NULL;
	}
	
	image_ref = CreateCGImageFromCGImageSource(image_source);
	CFRelease(image_source);
	
	if(NULL == image_ref)
	{
		return NULL;
	}
	
	sdl_surface = Create_SDL_Surface_From_CGImage(image_ref);
	CFRelease(image_ref);
	return sdl_surface;	
}

int IMG_InitJPG()
{
	return 0;
}

void IMG_QuitJPG()
{
}

int IMG_InitPNG()
{
	return 0;
}

void IMG_QuitPNG()
{
}

int IMG_InitTIF()
{
	return 0;
}

void IMG_QuitTIF()
{
}

int IMG_isCUR(SDL_RWops *src)
{
	/* FIXME: Is this a supported type? */
	return Internal_isType(src, CFSTR("com.microsoft.cur"));
}

int IMG_isICO(SDL_RWops *src)
{
	return Internal_isType(src, kUTTypeICO);
}

int IMG_isBMP(SDL_RWops *src)
{
	return Internal_isType(src, kUTTypeBMP);
}

int IMG_isGIF(SDL_RWops *src)
{
	return Internal_isType(src, kUTTypeGIF);
}

// Note: JPEG 2000 is kUTTypeJPEG2000
int IMG_isJPG(SDL_RWops *src)
{
	return Internal_isType(src, kUTTypeJPEG);
}

int IMG_isPNG(SDL_RWops *src)
{
	return Internal_isType(src, kUTTypePNG);
}

// This isn't a public API function. Apple seems to be able to identify tga's.
int IMG_isTGA(SDL_RWops *src)
{
	return Internal_isType(src, CFSTR("com.truevision.tga-image"));
}

int IMG_isTIF(SDL_RWops *src)
{
	return Internal_isType(src, kUTTypeTIFF);
}

SDL_Surface* IMG_LoadCUR_RW(SDL_RWops *src)
{
	/* FIXME: Is this a supported type? */
	return LoadImageFromRWops(src, CFSTR("com.microsoft.cur"));
}
SDL_Surface* IMG_LoadICO_RW(SDL_RWops *src)
{
	return LoadImageFromRWops(src, kUTTypeICO);
}
SDL_Surface* IMG_LoadBMP_RW(SDL_RWops *src)
{
	return LoadImageFromRWops(src, kUTTypeBMP);
}
SDL_Surface* IMG_LoadGIF_RW(SDL_RWops *src)
{
	return LoadImageFromRWops(src, kUTTypeGIF);
}
SDL_Surface* IMG_LoadJPG_RW(SDL_RWops *src)
{
	return LoadImageFromRWops(src, kUTTypeJPEG);
}
SDL_Surface* IMG_LoadPNG_RW(SDL_RWops *src)
{
	return LoadImageFromRWops(src, kUTTypePNG);
}
SDL_Surface* IMG_LoadTGA_RW(SDL_RWops *src)
{
	return LoadImageFromRWops(src, CFSTR("com.truevision.tga-image"));
}
SDL_Surface* IMG_LoadTIF_RW(SDL_RWops *src)
{
	return LoadImageFromRWops(src, kUTTypeTIFF);
}

// Apple provides both stream and file loading functions in ImageIO.
// Potentially, Apple can optimize for either case.
SDL_Surface* IMG_Load(const char *file)
{
	SDL_Surface* sdl_surface = NULL;

	sdl_surface = LoadImageFromFile(file);
	if(NULL == sdl_surface)
	{
		// Either the file doesn't exist or ImageIO doesn't understand the format.
		// For the latter case, fallback to the native SDL_image handlers.
		SDL_RWops *src = SDL_RWFromFile(file, "rb");
		char *ext = strrchr(file, '.');
		if(ext) {
			ext++;
		}
		if(!src) {
			/* The error message has been set in SDL_RWFromFile */
			return NULL;
		}
		sdl_surface = IMG_LoadTyped_RW(src, 1, ext);
	}
	return sdl_surface;
}

#endif /* defined(__APPLE__) && !defined(SDL_IMAGE_USE_COMMON_BACKEND) */
