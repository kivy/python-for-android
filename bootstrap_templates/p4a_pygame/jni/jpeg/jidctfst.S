/*
 * Copyright (C) 2008 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <machine/cpu-features.h>

    .text
    .align

    .global jpeg_idct_ifast
    .func   jpeg_idct_ifast

// NOTE: sb=r9, fp=r11 ip=r12, sp=r13, lr=r14, pc=r15

// jpeg_idct_ifast (j_decompress_ptr       cinfo,
//                 jpeg_component_info *   compptr,
//                 short*                  coef_block,
//                 unsigned char*          output_buf,
//                 int                     output_col)

#define  local_TMP0123       sp
#define  local_TMP0          [sp, #0]
#define  local_TMP1          [sp, #4]
#define  local_TMP2          [sp, #8]
#define  local_TMP3          [sp, #12]
#define  local_RANGE_TABLE   [sp, #16]
#define  local_OUTPUT_COL    [sp, #20]
#define  local_OUTPUT_BUF    [sp, #24]
#define  local_UNUSED        [sp, #28]
#define  off_WORKSPACE       32
#define  local_WORKSPACE     [sp, #offWORKSPACE]
#define  local_SIZE          (off_WORKSPACE + 8*8*4)

#define  off_DECOMPRESS_range_limit_base  324
#define  off_COMPINFO_quanttable          80

#define  DCTSIZE   8
#define  VY(x)   ((x)*DCTSIZE*2)
#define  QY(x)   ((x)*DCTSIZE*4)

#define  VX(x)   ((x)*2)
#define  QX(x)   ((x)*4)

#define  FIX_1_414213562    #362
#define  FIX_1_082392200    #277
#define  FIX_1_847759065    #473
#define  FIX_2_613125930    #669

#define  RANGE_MASK   1023



jpeg_idct_ifast:
    PLD     [r2, #0]
    stmdb   sp!, {r4,r5, r6,r7, r8,r9, r10,r11, r12,lr}
    ldr     r4, [sp, #4*10]
    sub     sp, #local_SIZE

    ldr     r10,[r1, #off_COMPINFO_quanttable]         // r10 = quanttable
    str     r4, local_OUTPUT_COL
    str     r3, local_OUTPUT_BUF
    ldr     r5, [r0, #off_DECOMPRESS_range_limit_base]
    add     r5, r5, #128
    str     r5, local_RANGE_TABLE
    mov     fp, r2                                      // fp = coef_block
    add     ip, sp, #off_WORKSPACE

VLoopTail:
    ldrsh    r0, [fp, #VY(0)]
    ldrsh    r1, [fp, #VY(1)]
    ldrsh    r2, [fp, #VY(2)]
    ldrsh    r3, [fp, #VY(3)]
    ldrsh    r4, [fp, #VY(4)]
    ldrsh    r5, [fp, #VY(5)]
    ldrsh    r6, [fp, #VY(6)]
    ldrsh    r7, [fp, #VY(7)]

    cmp      r1, #0
    orreqs   r8, r2, r3
    orreqs   r8, r4, r5
    orreqs   r8, r6, r7
    beq      VLoopHeadZero

VLoopHead:
    // tmp0 = DEQUANTIZE(in[DCTSIZE*0], quant[DCTSIZE*0]   (r0)
    // tmp2 = DEQUANTIZE(in[DCTSIZE*4], quant[DCTSIZE*4]   (r4)
    // tmp1 = DEQUANTIZE(in[DCTSIZE*2], quant[DCTSIZE*2]   (r2)
    // tmp3 = DEQUANTIZE(in[DCTSIZE*6], quant[DCTSIZE*6]   (r6)
    // tmp10 = tmp0 + tmp2   (r0)
    // tmp11 = tmp0 - tmp2   (r4)

    ldr      r9, [r10, #QY(4)]
    ldr      r8, [r10, #QY(0)]
#if __ARM_HAVE_HALFWORD_MULTIPLY
    smulbb   r4, r9, r4
    smlabb   r0, r8, r0, r4
#else
    mul      r4, r9, r4
    mul      r0, r8, r0
    add      r0, r4
#endif
    ldr      r9, [r10, #QY(6)]
    ldr      r8, [r10, #QY(2)]
    sub      r4, r0, r4, lsl #1
#if __ARM_HAVE_HALFWORD_MULTIPLY
    smulbb   r6, r9, r6
    smlabb   r2, r8, r2, r6
#else
    mul      r6, r9, r6
    mul      r2, r8, r2
    add      r2, r6
#endif

    // tmp13 = tmp1 + tmp3                                       (r2)
    // tmp12 = MULTIPLY(tmp1 - tmp3, FIX_1_414213562) - tmp13    (r6)
    // FIX_1_4142... = 362 = 45*8 + 2
    sub      r6, r2, r6, lsl #1
    mov      r8, #360
    add      r8, r8, #2
    mul      r9, r6, r8

    // tmp0 = tmp10 + tmp13;   (r0)
    // tmp3 = tmp10 - tmp13;   (r8)
    // tmp1 = tmp11 + tmp12;   (r4)
    // tmp2 = tmp11 - tmp12;   (r6)
    add     r0, r0, r2
    rsb     r6, r2, r9, asr #8
    sub     r8, r0, r2, lsl #1
    add     r4, r4, r6
    sub     r6, r4, r6, lsl #1

    stmia   local_TMP0123, {r0, r4, r6, r8}

    // NOTE: be sure to not user r0,r4,r6,r8 soon after stm above

    // odd part
    // tmp4 = DEQUANTIZE( in[DCTSIZE*1], quant[DCTSIZE*1] )   (r1)
    // tmp6 = DEQUANTIZE( in[DCTSIZE*5], quant[DCTSIZE*5] )   (r5)
    // tmp5 = DEQUANTIZE( in[DCTSIZE*3], quant[DCTSIZE*3] )   (r3)
    // tmp7 = DEQUANTIZE( in[DCTSIZE*7], quant[DCTSIZE*7] )   (r7)
    // z13 = tmp6 + tmp5;  (r0)
    // z10 = tmp6 - tmp5;  (r2)
    // z11 = tmp4 + tmp7;  (r4)
    // z12 = tmp4 - tmp7;  (r6)

    ldr     r2, [r10, #QY(1)]
    ldr     r9, [r10, #QY(5)]
#if __ARM_HAVE_HALFWORD_MULTIPLY
    smulbb  r1, r2, r1
#else
    mul     r1, r2, r1
#endif
    ldr     r2, [r10, #QY(3)]
#if __ARM_HAVE_HALFWORD_MULTIPLY
    smulbb  r5, r9, r5
#else
    mul     r5, r9, r5
#endif
    ldr     r9, [r10, #QY(7)]
#if __ARM_HAVE_HALFWORD_MULTIPLY
    smlabb  r0, r2, r3, r5
    smlabb  r4, r9, r7, r1
#else
    mul     r0, r2, r3
    add     r0, r5
    mul     r4, r9, r7
    add     r4, r1
#endif
    rsb  r2, r0, r5, lsl #1
    rsb  r6, r4, r1, lsl #1

    // tmp7 = z11 + z13;                             (r7)
    // tmp11 = MULTIPLY(z11 - z13, FIX_1_414213562); (r1)
    // FIX_... = 360 + 2
    add   r7, r4, r0
    sub   r1, r4, r0
    mov   r8, #360
    add   r8, r8, #2
    mul   r1, r8, r1

    // z5 = MULTIPLY(z10 + z12, FIX_1_847759065);        (r8)
    // tmp10 = MULTIPLY(z12, FIX_1_082392200) - z5;      (r0)
    // tmp12 = MULTIPLY(z10, - FIX_2_613125930) + z5;    (r2)
    // FIX_1_8477... = 473 = 472 + 1
    // FIX_1_082...  = 277 = 276 + 1
    // FIX_2_...     = 669 = 668 + 1
    add     r8, r2, r6
    mov     r9, #472
    mla     r8, r9, r8, r8
    mov     r9, #276
    mla     r0, r6, r9, r6
    mov     r9, #668
    mla     r2, r9, r2, r2
    sub     r0, r0, r8
    rsb     r2, r2, r8

    // tmp6 = tmp12 - tmp7;  (r6)
    // tmp5 = tmp11 - tmp6;  (r5)
    // tmp4 = tmp10 + tmp5;  (r4)
    rsb  r6, r7, r2, asr #8
    rsb  r5, r6, r1, asr #8
    add  r4, r5, r0, asr #8

    ldmia local_TMP0123, {r0, r1, r2, r3}

    // wsptr[DCTSIZE*0] = (int) (tmp0 + tmp7);
    // wsptr[DCTSIZE*7] = (int) (tmp0 - tmp7);
    // wsptr[DCTSIZE*1] = (int) (tmp1 + tmp6);
    // wsptr[DCTSIZE*6] = (int) (tmp1 - tmp6);
    // wsptr[DCTSIZE*2] = (int) (tmp2 + tmp5);
    // wsptr[DCTSIZE*5] = (int) (tmp2 - tmp5);
    // wsptr[DCTSIZE*4] = (int) (tmp3 + tmp4);
    // wsptr[DCTSIZE*3] = (int) (tmp3 - tmp4);

    add   r0, r0, r7
    sub   r7, r0, r7, lsl #1
    add   r1, r1, r6
    sub   r6, r1, r6, lsl #1
    add   r2, r2, r5
    sub   r5, r2, r5, lsl #1
    sub   r3, r3, r4
    add   r4, r3, r4, lsl #1

    str   r0, [ip, #QY(0)]
    str   r1, [ip, #QY(1)]
    str   r2, [ip, #QY(2)]
    str   r3, [ip, #QY(3)]
    str   r4, [ip, #QY(4)]
    str   r5, [ip, #QY(5)]
    str   r6, [ip, #QY(6)]
    str   r7, [ip, #QY(7)]

    // inptr++;                    /* advance pointers to next column */
    // quantptr++;
    // wsptr++;
    add  fp, fp, #2
    add  r10, r10, #4
    add  ip, ip, #4
    add  r0, sp, #(off_WORKSPACE + 4*8)
    cmp  ip, r0
    bne  VLoopTail



HLoopStart:
    // reset pointers
    PLD     [sp, #off_WORKSPACE]
    add     ip, sp, #off_WORKSPACE
    ldr     r10, local_RANGE_TABLE

HLoopTail:
    // output = *output_buf++ + output_col
    ldr      r0, local_OUTPUT_BUF
    ldr      r1, local_OUTPUT_COL
    ldr      r2, [r0], #4
    str      r0, local_OUTPUT_BUF
    add      fp, r2, r1

    PLD      [ip, #32]
    ldmia    ip!, {r0-r7}

    cmp      r1, #0
    orreqs   r8, r2, r3
    orreqs   r8, r4, r5
    orreqs   r8, r6, r7
    beq      HLoopTailZero

HLoopHead:
    // tmp10 = ((DCTELEM) wsptr[0] + (DCTELEM) wsptr[4]);    (r0)
    // tmp11 = ((DCTELEM) wsptr[0] - (DCTELEM) wsptr[4]);    (r4)
    add     r0, r0, r4
    sub     r4, r0, r4, lsl #1

    // tmp13 = ((DCTELEM) wsptr[2] + (DCTELEM) wsptr[6]);                                   (r2)
    // tmp12 = MULTIPLY((DCTELEM) wsptr[2] - (DCTELEM) wsptr[6], FIX_1_414213562) - tmp13;  (r6)
    // FIX_... = 360 + 2
    add     r2, r2, r6
    sub     r6, r2, r6, lsl #1
    mov     r8, #360
    add     r8, r8, #2
    mul     r6, r8, r6

    // tmp0 = tmp10 + tmp13;   (r0)
    // tmp3 = tmp10 - tmp13;   (r8)
    // tmp1 = tmp11 + tmp12;   (r4)
    // tmp2 = tmp11 - tmp12;   (r6)
    add     r0, r0, r2
    rsb     r6, r2, r6, asr #8
    sub     r8, r0, r2, lsl #1
    add     r4, r4, r6
    sub     r6, r4, r6, lsl #1

    stmia   local_TMP0123, {r0, r4, r6, r8}

    // Odd part

    // z13 = (DCTELEM) wsptr[5] + (DCTELEM) wsptr[3];  (r0)
    // z10 = (DCTELEM) wsptr[5] - (DCTELEM) wsptr[3];  (r2)
    // z11 = (DCTELEM) wsptr[1] + (DCTELEM) wsptr[7];  (r4)
    // z12 = (DCTELEM) wsptr[1] - (DCTELEM) wsptr[7];  (r6)
    add  r0, r5, r3
    sub  r2, r5, r3
    add  r4, r1, r7
    sub  r6, r1, r7

    // tmp7 = z11 + z13;                             (r7)
    // tmp11 = MULTIPLY(z11 - z13, FIX_1_414213562); (r1)
    // FIX_... = 360 + 2
    add   r7, r4, r0
    sub   r1, r4, r0
    mov   r8, #360
    add   r8, r8, #2
    mul   r1, r8, r1

    // z5 = MULTIPLY(z10 + z12, FIX_1_847759065);        (r8)
    // tmp10 = MULTIPLY(z12, FIX_1_082392200) - z5;      (r0)
    // tmp12 = MULTIPLY(z10, - FIX_2_613125930) + z5;    (r2)
    // FIX_1_8477... = 473 = 472 + 1
    // FIX_1_082...  = 277 = 276 + 1
    // FIX_2_...     = 669 = 668 + 1
    add  r8, r2, r6
    mov  r9, #472
    mla  r8, r9, r8, r8
    mov  r9, #276
    mla  r0, r6, r9, r6
    mov  r9, #668
    mla  r2, r9, r2, r2
    sub  r0, r0, r8
    sub  r2, r8, r2

    // tmp6 = tmp12 - tmp7;  (r6)
    // tmp5 = tmp11 - tmp6;  (r5)
    // tmp4 = tmp10 + tmp5;  (r4)
    rsb  r6, r7, r2, asr #8
    rsb  r5, r6, r1, asr #8
    add  r4, r5, r0, asr #8

    ldmia local_TMP0123, {r0, r1, r2, r3}

    // outptr[0] = range_limit[IDESCALE(tmp0 + tmp7, PASS1_BITS+3) & RANGE_MASK];
    // outptr[7] = range_limit[IDESCALE(tmp0 - tmp7, PASS1_BITS+3) & RANGE_MASK];
    // outptr[1] = range_limit[IDESCALE(tmp1 + tmp6, PASS1_BITS+3) & RANGE_MASK];
    // outptr[6] = range_limit[IDESCALE(tmp1 - tmp6, PASS1_BITS+3) & RANGE_MASK];
    // outptr[2] = range_limit[IDESCALE(tmp2 + tmp5, PASS1_BITS+3) & RANGE_MASK];
    // outptr[5] = range_limit[IDESCALE(tmp2 - tmp5, PASS1_BITS+3) & RANGE_MASK];
    // outptr[4] = range_limit[IDESCALE(tmp3 + tmp4, PASS1_BITS+3) & RANGE_MASK];
    // outptr[3] = range_limit[IDESCALE(tmp3 - tmp4, PASS1_BITS+3) & RANGE_MASK];

    mov    r8, #128
    add    r0, r0, r7
    sub    r7, r0, r7, lsl #1
    add    r0, r8, r0, asr #5
    add    r7, r8, r7, asr #5
    add    r1, r1, r6
    sub    r6, r1, r6, lsl #1
    add    r1, r8, r1, asr #5
    add    r6, r8, r6, asr #5
    add    r2, r2, r5
    sub    r5, r2, r5, lsl #1
    add    r2, r8, r2, asr #5
    add    r5, r8, r5, asr #5
    sub    r3, r3, r4
    add    r4, r3, r4, lsl #1
    add    r3, r8, r3, asr #5
    add    r4, r8, r4, asr #5

#if __ARM_ARCH__ >= 6
    usat   r0, #8, r0
    usat   r1, #8, r1
    usat   r2, #8, r2
    usat   r3, #8, r3
    usat   r4, #8, r4
    usat   r5, #8, r5
    usat   r6, #8, r6
    usat   r7, #8, r7
#else
    cmp    r0, #255
    mvnhi  r0, r0, asr #31
    andhi  r0, #255
    cmp    r7, #255
    mvnhi  r7, r7, asr #31
    cmp    r1, #255
    mvnhi  r1, r1, asr #31
    andhi  r1, #255
    cmp    r6, #255
    mvnhi  r6, r6, asr #31
    andhi  r6, #255
    cmp    r2, #255
    mvnhi  r2, r2, asr #31
    andhi  r2, #255
    cmp    r5, #255
    mvnhi  r5, r5, asr #31
    andhi  r5, #255
    cmp    r3, #255
    mvnhi  r3, r3, asr #31
    cmp    r4, #255
    mvnhi  r4, r4, asr #31
    andhi  r4, #255
#endif

    // r3 r2 r1 r0
    orr    r0, r0, r1, lsl #8
    orr    r0, r0, r2, lsl #16
    orr    r0, r0, r3, lsl #24

    // r7 r6 r5 r4
    orr    r1, r4, r5, lsl #8
    orr    r1, r1, r6, lsl #16
    orr    r1, r1, r7, lsl #24
    stmia  fp, {r0, r1}

    add    r0, sp, #(off_WORKSPACE + 8*8*4)
    cmp    ip, r0
    bne    HLoopTail

Exit:
    add    sp, sp, #local_SIZE
    ldmia  sp!, {r4,r5, r6,r7, r8,r9, r10,r11, r12,lr}
    bx     lr


VLoopHeadZero:
// ok, all AC coefficients are 0
    ldr      r1, [r10, #QY(0)]
    add      fp, fp, #2
    add      r10, r10, #4
    mul      r0, r1, r0
    str      r0, [ip, #QY(0)]
    str      r0, [ip, #QY(1)]
    str      r0, [ip, #QY(2)]
    str      r0, [ip, #QY(3)]
    str      r0, [ip, #QY(4)]
    str      r0, [ip, #QY(5)]
    str      r0, [ip, #QY(6)]
    str      r0, [ip, #QY(7)]
    add      ip, ip, #4
    add      r0, sp, #(off_WORKSPACE + 4*8)
    cmp      ip, r0
    beq      HLoopStart
    b        VLoopTail

HLoopTailZero:
    mov      r0, r0, asr #5
    add      r0, #128

#if __ARM_ARCH__ >= 6
    usat     r0, #8, r0
#else
    cmp      r0, #255
    mvnhi    r0, r0, asr #31
    andhi    r0, r0, #255
#endif

    orr      r0, r0, lsl #8
    orr      r0, r0, lsl #16
    mov      r1, r0
    stmia    fp, {r0, r1}

    add      r0, sp, #(off_WORKSPACE + 64*4)
    cmp      ip, r0
    beq      Exit
    b        HLoopTail

    .endfunc
