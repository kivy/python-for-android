/*
 * jidctvenum.c
 *
 * Copyright (c) 2010, Code Aurora Forum. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above
 *       copyright notice, this list of conditions and the following
 *       disclaimer in the documentation and/or other materials provided
 *       with the distribution.
 *     * Neither the name of Code Aurora Forum, Inc. nor the names of its
 *       contributors may be used to endorse or promote products derived
 *       from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
 * BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 * BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 * OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
 * IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#define JPEG_INTERNALS
#include "jinclude.h"
#include "jpeglib.h"
#include "jdct.h"    /* Private declarations for DCT subsystem */

#ifdef ANDROID_JPEG_USE_VENUM
/*
 * This module is specialized to the case DCTSIZE = 8.
 */
#if DCTSIZE != 8
  Sorry, this code only copes with 8x8 DCTs. /* deliberate syntax err */
#endif

/* Dequantize a coefficient by multiplying it by the multiplier-table
 * entry; produce an int result.  In this module, both inputs and result
 * are 16 bits or less, so either int or short multiply will work.
 */

#define DEQUANTIZE(coef,quantval)  ((coef) * ((INT16)quantval))

GLOBAL(void)
jpeg_idct_islow (j_decompress_ptr cinfo, jpeg_component_info * compptr,
         JCOEFPTR coef_block,
         JSAMPARRAY output_buf, JDIMENSION output_col)
{
  ISLOW_MULT_TYPE * quantptr;
  JCOEFPTR coefptr;
  int ctr;

  /* idct_out temp buffer is needed because output_buf sample allocation is 8 bits,
   * while IDCT output expects 16 bits.
   */
  INT16 idct_out[DCTSIZE2];  /* buffers data between passes */
  JSAMPROW outptr;
  INT16*  idctptr;

  coefptr  = coef_block;
  quantptr = (ISLOW_MULT_TYPE *) compptr->dct_table;

  /* Dequantize the coeff buffer and write it back to the same location */
  for (ctr = DCTSIZE; ctr > 0; ctr--) {
    coefptr[0]         = DEQUANTIZE(coefptr[0]        , quantptr[0]        );
    coefptr[DCTSIZE*1] = DEQUANTIZE(coefptr[DCTSIZE*1], quantptr[DCTSIZE*1]);
    coefptr[DCTSIZE*2] = DEQUANTIZE(coefptr[DCTSIZE*2], quantptr[DCTSIZE*2]);
    coefptr[DCTSIZE*3] = DEQUANTIZE(coefptr[DCTSIZE*3], quantptr[DCTSIZE*3]);
    coefptr[DCTSIZE*4] = DEQUANTIZE(coefptr[DCTSIZE*4], quantptr[DCTSIZE*4]);
    coefptr[DCTSIZE*5] = DEQUANTIZE(coefptr[DCTSIZE*5], quantptr[DCTSIZE*5]);
    coefptr[DCTSIZE*6] = DEQUANTIZE(coefptr[DCTSIZE*6], quantptr[DCTSIZE*6]);
    coefptr[DCTSIZE*7] = DEQUANTIZE(coefptr[DCTSIZE*7], quantptr[DCTSIZE*7]);

    /* advance pointers to next column */
    quantptr++;
    coefptr++;
  }

  idct_8x8_venum((INT16*)coef_block,
                 (INT16*)idct_out,
                 DCTSIZE * sizeof(INT16));

  idctptr = idct_out;
  for (ctr = 0; ctr < DCTSIZE; ctr++) {
    outptr = output_buf[ctr] + output_col;
    // outptr sample size is 1 byte while idctptr sample size is 2 bytes
    outptr[0] = idctptr[0];
    outptr[1] = idctptr[1];
    outptr[2] = idctptr[2];
    outptr[3] = idctptr[3];
    outptr[4] = idctptr[4];
    outptr[5] = idctptr[5];
    outptr[6] = idctptr[6];
    outptr[7] = idctptr[7];
    idctptr  += DCTSIZE;      /* advance pointers to next row */
  }
}

GLOBAL(void)
jpeg_idct_4x4 (j_decompress_ptr cinfo, jpeg_component_info * compptr,
         JCOEFPTR coef_block,
         JSAMPARRAY output_buf, JDIMENSION output_col)
{
  ISLOW_MULT_TYPE * quantptr;
  JSAMPROW outptr;

  /* Note: Must allocate 8x4 even though only 4x4 is used because
   * IDCT function expects stride of 8. Stride input to function is ignored.
   */
  INT16    idct_out[DCTSIZE * (DCTSIZE>>1)];  /* buffers data between passes */
  INT16*   idctptr;
  JCOEFPTR coefptr;
  int ctr;

  coefptr  = coef_block;
  quantptr = (ISLOW_MULT_TYPE *) compptr->dct_table;

  /* Dequantize the coeff buffer and write it back to the same location */
  for (ctr = (DCTSIZE>>1); ctr > 0; ctr--) {
    coefptr[0]         = DEQUANTIZE(coefptr[0]        , quantptr[0]        );
    coefptr[DCTSIZE*1] = DEQUANTIZE(coefptr[DCTSIZE*1], quantptr[DCTSIZE*1]);
    coefptr[DCTSIZE*2] = DEQUANTIZE(coefptr[DCTSIZE*2], quantptr[DCTSIZE*2]);
    coefptr[DCTSIZE*3] = DEQUANTIZE(coefptr[DCTSIZE*3], quantptr[DCTSIZE*3]);

    /* advance pointers to next column */
    quantptr++;
    coefptr++;
  }

  idct_4x4_venum((INT16*)coef_block,
                 (INT16*)idct_out,
                  DCTSIZE * sizeof(INT16));

  idctptr = idct_out;
  for (ctr = 0; ctr < (DCTSIZE>>1); ctr++) {
    outptr = output_buf[ctr] + output_col;

    /* outptr sample size is 1 byte while idctptr sample size is 2 bytes */
    outptr[0] = idctptr[0];
    outptr[1] = idctptr[1];
    outptr[2] = idctptr[2];
    outptr[3] = idctptr[3];
    /* IDCT function assumes stride of 8 units */
    idctptr += (DCTSIZE);    /* advance pointers to next row */
  }
}

GLOBAL(void)
jpeg_idct_2x2 (j_decompress_ptr cinfo, jpeg_component_info * compptr,
         JCOEFPTR coef_block,
         JSAMPARRAY output_buf, JDIMENSION output_col)
{
  ISLOW_MULT_TYPE * quantptr;
  JSAMPROW outptr;

  /* Note: Must allocate 8x2 even though only 2x2 is used because
   * IDCT function expects stride of 8. Stride input to function is ignored.
   * There is also a hw limitation requiring input size to be 8x2.
   */
  INT16    idct_out[DCTSIZE * (DCTSIZE>>2)];  /* buffers data between passes */
  INT16*   idctptr;
  JCOEFPTR coefptr;
  int ctr;

  coefptr  = coef_block;
  quantptr = (ISLOW_MULT_TYPE *) compptr->dct_table;

  /* Dequantize the coeff buffer and write it back to the same location */
  for (ctr = (DCTSIZE>>2); ctr > 0; ctr--) {
    coefptr[0]         = DEQUANTIZE(coefptr[0]        , quantptr[0]        );
    coefptr[DCTSIZE*1] = DEQUANTIZE(coefptr[DCTSIZE*1], quantptr[DCTSIZE*1]);

    /* advance pointers to next column */
    quantptr++;
    coefptr++;
  }

  idct_2x2_venum((INT16*)coef_block,
                 (INT16*)idct_out,
                  DCTSIZE * sizeof(INT16));

  idctptr = idct_out;
  for (ctr = 0; ctr < (DCTSIZE>>2); ctr++) {
    outptr = output_buf[ctr] + output_col;

    /* outptr sample size is 1 bytes, idctptr sample size is 2 bytes */
    outptr[0] = idctptr[0];
    outptr[1] = idctptr[1];

    /* IDCT function assumes stride of 8 units */
    idctptr += (DCTSIZE);    /* advance pointers to next row */
  }
}


GLOBAL(void)
jpeg_idct_1x1 (j_decompress_ptr cinfo, jpeg_component_info * compptr,
         JCOEFPTR coef_block,
         JSAMPARRAY output_buf, JDIMENSION output_col)
{
  ISLOW_MULT_TYPE * quantptr;
  JSAMPROW outptr; // 8-bit type
  INT16    idct_out[DCTSIZE]; /* Required to allocate 8 samples, even though we only use one. */
  JCOEFPTR coefptr;
  int ctr;

  coefptr  = coef_block;
  quantptr = (ISLOW_MULT_TYPE *) compptr->dct_table;
  outptr   = output_buf[0] + output_col;

  /* Dequantize the coeff buffer and write it back to the same location */
  coefptr[0] = DEQUANTIZE(coefptr[0], quantptr[0]);

  idct_1x1_venum((INT16*)coef_block,
                 (INT16*)idct_out,
                 DCTSIZE * sizeof(INT16));
  outptr[0] = idct_out[0];
}


#endif /* ANDROID_JPEG_USE_VENUM */
