#include "de_mjpegsample_NativeJpegLib.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <fcntl.h>              /* low-level i/o */
#include <unistd.h>
#include <errno.h>
#include <malloc.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <sys/ioctl.h>

//#include <asm/types.h>          /* for videodev2.h */
#include <jpeglib.h>

/* default size, This just the size of sample yuv  */
#define OUTPUT_BUF_SIZE 4096

typedef struct {
  struct jpeg_destination_mgr pub; /* public fields */

  JOCTET * buffer;    /* start of buffer */

  unsigned char *outbuffer;
  int outbuffer_size;
  unsigned char *outbuffer_cursor;
  int *written;
}my_destmgr;

METHODDEF(void) init_destination(j_compress_ptr cinfo) {
  my_destmgr * dest = (my_destmgr*) cinfo->dest;

  /* Allocate the output buffer --- it will be released when done with
   * image */
  dest->buffer = (JOCTET *)(*cinfo->mem->alloc_small) ((j_common_ptr) cinfo, JPOOL_IMAGE, OUTPUT_BUF_SIZE * sizeof(JOCTET));

  *(dest->written) = 0;

  dest->pub.next_output_byte = dest->buffer;
  dest->pub.free_in_buffer = OUTPUT_BUF_SIZE;
}

/******************************************************************************
Description.: called whenever local jpeg buffer fills up
Input Value.:
Return Value:
******************************************************************************/
METHODDEF(boolean) empty_output_buffer(j_compress_ptr cinfo) 
{
  my_destmgr *dest = (my_destmgr *) cinfo->dest;

  memcpy(dest->outbuffer_cursor, dest->buffer, OUTPUT_BUF_SIZE);
  dest->outbuffer_cursor += OUTPUT_BUF_SIZE;
  *(dest->written) += OUTPUT_BUF_SIZE;

  dest->pub.next_output_byte = dest->buffer;
  dest->pub.free_in_buffer = OUTPUT_BUF_SIZE;

  return TRUE;
}


METHODDEF(void) term_destination(j_compress_ptr cinfo) 
{
  my_destmgr * dest = (my_destmgr *) cinfo->dest;
  size_t datacount = OUTPUT_BUF_SIZE - dest->pub.free_in_buffer;

  /* Write any data remaining in the buffer */
  memcpy(dest->outbuffer_cursor, dest->buffer, datacount);
  dest->outbuffer_cursor += datacount;
  *(dest->written) += datacount;
}

void dest_buffer(j_compress_ptr cinfo, unsigned char *buffer, int size, int *written) 
{
  my_destmgr * dest;

  if (cinfo->dest == NULL) {
    cinfo->dest = (struct jpeg_destination_mgr *)(*cinfo->mem->alloc_small) ((j_common_ptr) cinfo, JPOOL_PERMANENT, sizeof(my_destmgr));
  }

  dest = (my_destmgr*) cinfo->dest;
  dest->pub.init_destination = init_destination;
  dest->pub.empty_output_buffer = empty_output_buffer;
  dest->pub.term_destination = term_destination;
  dest->outbuffer = buffer;
  dest->outbuffer_size = size;
  dest->outbuffer_cursor = buffer;
  dest->written = written;
}


static int convert_to_jpg(void *src, int src_len, 
		void *dst, int pwidth, int pheight, int quality) {
	//Code for this function is taken from Motion
    //Credit to them !!!
    //Also Credit mjpg-streamer

    struct jpeg_compress_struct cinfo;
    struct jpeg_error_mgr jerr;
	my_destmgr dest;

	memset(&cinfo , 0, sizeof(cinfo));

    JSAMPROW y[16],cb[16],cr[16];
    JSAMPARRAY data[3];
    int i, line, width = pwidth, height = pheight;
    int written;                /* for count file size */

    printf("Encoding a %dx%d frame\n", width, height);

    data[0] = y;
    data[1] = cb;
    data[2] = cr;

    cinfo.err = jpeg_std_error(&jerr);
    jpeg_create_compress(&cinfo);
    
    //init JPEG dest mgr
    dest_buffer(&cinfo, dst, src_len, &written);

    jpeg_set_quality(&cinfo, quality, TRUE);

	cinfo.input_components = 3;
    cinfo.image_width = width;
    cinfo.image_height = height;

    cinfo.in_color_space = JCS_YCbCr;
    jpeg_set_defaults(&cinfo);
    jpeg_set_colorspace(&cinfo, JCS_YCbCr);
    cinfo.raw_data_in = TRUE; 

	cinfo.dct_method = JDCT_FLOAT;
    /* This method will faster in faster HW */
	
	jpeg_start_compress( &cinfo, TRUE );
    for (line=0; line<height; line+=16) {
        for (i=0; i<16; i++) {
            y[i] = src + width*(i+line);
            if (i%2 == 0) {
                cb[i/2] = src + width*height + width/2*((i+line)/2);
                cr[i/2] = src + width*height + width*height/4 + width/2*((i+line)/2);
            }
        }
        jpeg_write_raw_data(&cinfo, data, 16);
    }
    jpeg_finish_compress(&cinfo);
    return written;
}

/*
 * Class:     de_mjpegsample_NativeJpegLib
 * Method:    c_compress_jpeg
 * Signature: (III[B)Ljava/nio/ByteBuffer;
 */
JNIEXPORT jobject JNICALL Java_de_mjpegsample_NativeJpegLib_c_1compress_1jpeg
  (JNIEnv *env, jclass cls, jint width, jint height, jint quality, jbyteArray yuv_bytes) {
	//jboolean copy = (jboolean)false;
	jbyte *yuv_bytes_ptr = (*env)->GetByteArrayElements(env, yuv_bytes, 0);
	int yuv_length = (*env)->GetArrayLength(env, yuv_bytes);
	
	// allocate memory to hold converted JPEG bytes
	char *jpeg_buf = malloc(yuv_length);
	// convert YUV420 to JPEG
	int jpg_buf_size = convert_to_jpg(yuv_bytes_ptr, yuv_length, jpeg_buf, width, height, quality);

	// release all memory
	(*env)->ReleaseByteArrayElements(env, yuv_bytes, yuv_bytes_ptr, (jint)0);

	// create direct buffer
	jobject jbuff = (*env)->NewDirectByteBuffer(env, (void*)jpeg_buf, (jlong)jpg_buf_size);
	return jbuff;
}

/*
 * Class:     de_mjpegsample_NativeJpegLib
 * Method:    c_decompress_jpeg
 * Signature: (II[B)Ljava/nio/ByteBuffer;
 */
JNIEXPORT jobject JNICALL Java_de_mjpegsample_NativeJpegLib_c_1decompress_1jpeg
  (JNIEnv *env, jclass cls, jint width, jint height, jbyteArray jpeg_bytes) {
	// TODO: stub	
	return NULL;
}

/*
 * Class:     de_mjpegsample_NativeJpegLib
 * Method:    allocateNativeBuffer
 * Signature: (I)Ljava/nio/ByteBuffer;
 */
JNIEXPORT jobject JNICALL Java_de_mjpegsample_NativeJpegLib_allocateNativeBuffer
  (JNIEnv *env, jclass cls, jint size) {
	void* buffer = malloc(size);
    jobject directBuffer = (*env)->NewDirectByteBuffer(env, buffer, size);
	return directBuffer;
}

/*
 * Class:     de_mjpegsample_NativeJpegLib
 * Method:    freeNativeBuffer
 * Signature: (Ljava/nio/ByteBuffer;)V
 */
JNIEXPORT void JNICALL Java_de_mjpegsample_NativeJpegLib_freeNativeBuffer
  (JNIEnv *env, jclass cls, jobject jbyteBuf) {
	void *buf = (*env)->GetDirectBufferAddress(env, jbyteBuf);
	free(buf);	
}
