/*------------------------------------------------------------------------
* jdcolor-android-armv7.S
*
*  Copyright (c) 2010, Code Aurora Forum. All rights reserved.
*
*  Redistribution and use in source and binary forms, with or without
*  modification, are permitted provided that the following conditions are
*  met:
*      * Redistributions of source code must retain the above copyright
*        notice, this list of conditions and the following disclaimer.
*      * Redistributions in binary form must reproduce the above
*        copyright notice, this list of conditions and the following
*        disclaimer in the documentation and/or other materials provided
*        with the distribution.
*      * Neither the name of Code Aurora Forum, Inc. nor the names of its
*        contributors may be used to endorse or promote products derived
*        from this software without specific prior written permission.
*
*  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED
*  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
*  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT
*  ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
*  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
*  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
*  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
*  BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
*  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
*  OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
*  IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*--------------------------------------------------------------------------

*--------------------------------------------------------------------------
*                         FUNCTION LIST
*--------------------------------------------------------------------------
*
* - yvup2rgb565_venum
* - yyvup2rgb565_venum
* - yvup2abgr8888_venum
* - yyvup2abgr8888_venum
*
*--------------------------------------------------------------------------
*/

    .section yvu_plain_to_rgb_android, "x"  @ AREA
    .text                              @ |.text|, CODE, READONLY
    .align 2
    .code  32                          @ CODE32

/*-----------------------------------------------------------------------------
 *   ARM Registers
 * ---------------------------------------------------------------------------- */
p_y       .req r0
p_cr      .req r1
p_cb      .req r2
p_rgb     .req r3
p_bgr     .req r3
length    .req r12

    .global yvup2rgb565_venum
    .global yyvup2rgb565_venum
    .global yvup2abgr8888_venum
    .global yyvup2abgr8888_venum

@ coefficients in color conversion matrix multiplication
.equ COEFF_Y,          256             @ contribution of Y
.equ COEFF_V_RED,      359             @ contribution of V for red
.equ COEFF_U_GREEN,    -88             @ contribution of U for green
.equ COEFF_V_GREEN,   -183             @ contribution of V for green
.equ COEFF_U_BLUE,     454             @ contribution of U for blue

@ Clamping constants 0x0 and 0xFF
.equ COEFF_0,          0
.equ COEFF_255,        255

@ Bias coefficients for red, green and blue
.equ COEFF_BIAS_R,   -45824            @ Red   bias =     -359*128 + 128
.equ COEFF_BIAS_G,    34816            @ Green bias = (88+183)*128 + 128
.equ COEFF_BIAS_B,   -57984            @ Blue  bias =     -454*128 + 128


/*--------------------------------------------------------------------------
* FUNCTION     : yvup2rgb565_venum
*--------------------------------------------------------------------------
* DESCRIPTION  : Perform YVU planar to RGB565 conversion.
*--------------------------------------------------------------------------
* C PROTOTYPE  : void yvup2rgb565_venum(uint8_t  *p_y,
*                                       uint8_t  *p_cr,
*                                       uint8_t  *p_cb,
*                                       uint8_t  *p_rgb565,
*                                       uint32_t  length)
*--------------------------------------------------------------------------
* REG INPUT    : R0: uint8_t  *p_y
*                      pointer to the input Y Line
*                R1: uint8_t  *p_cr
*                      pointer to the input Cr Line
*                R2: uint8_t  *p_cb
*                      pointer to the input Cb Line
*                R3: uint8_t  *p_rgb565
*                      pointer to the output RGB Line
*                R12: uint32_t  length
*                      width of Line
*--------------------------------------------------------------------------
* STACK ARG    : None
*--------------------------------------------------------------------------
* REG OUTPUT   : None
*--------------------------------------------------------------------------
* MEM INPUT    : p_y      - a line of Y pixels
*                p_cr     - a line of Cr pixels
*                p_cb     - a line of Cb pixels
*                length   - the width of the input line
*--------------------------------------------------------------------------
* MEM OUTPUT   : p_rgb565 - the converted rgb pixels
*--------------------------------------------------------------------------
* REG AFFECTED : ARM:  R0-R4, R12
*                NEON: Q0-Q15
*--------------------------------------------------------------------------
* STACK USAGE  : none
*--------------------------------------------------------------------------
* CYCLES       : none
*
*--------------------------------------------------------------------------
* NOTES        :
*--------------------------------------------------------------------------
*/
.type yvup2rgb565_venum, %function
yvup2rgb565_venum:
    /*-------------------------------------------------------------------------
     *  Store stack registers
     * ------------------------------------------------------------------------ */
    STMFD SP!, {LR}

    VPUSH {D8-D15}

    PLD [R0, R3]                       @ preload luma line

    ADR   R12, constants

    VLD1.S16  {D6, D7}, [R12]!         @ D6, D7: 359 |  -88 | -183 | 454 | 256 | 0 | 255 | 0
    VLD1.S32  {D30, D31}, [R12]        @ Q15   :  -45824    |    34816   |  -57984 |     X

    /*-------------------------------------------------------------------------
     *  Load the 5th parameter via stack
     *  R0 ~ R3 are used to pass the first 4 parameters, the 5th and above
     *  parameters are passed via stack
     * ------------------------------------------------------------------------ */
    LDR R12, [SP, #68]                 @ LR is pushed into the stack so SP is
                                       @ decreased by 4,
                                       @ D8-D15 are also pushed into the stack
                                       @ so SP is decreased by
                                       @ 8-byte/D-Register * 8 D-Registers = 64,
                                       @ so SP needs to be increased by 64+4=68
                                       @ to get the value that was first pushed
                                       @ into stack (the 5th parameter passed in
                                       @ throught stack)

    /*-------------------------------------------------------------------------
     *  Load clamping parameters to duplicate vector elements
     * ------------------------------------------------------------------------ */
    VDUP.S16  Q4,  D7[1]               @ Q4:  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0
    VDUP.S16  Q5,  D7[2]               @ Q5: 255 | 255 | 255 | 255 | 255 | 255 | 255 | 255

    /*-------------------------------------------------------------------------
     *  Read bias
     * ------------------------------------------------------------------------ */
    VDUP.S32  Q0,   D30[0]             @ Q0:  -45824 | -45824 | -45824 | -45824
    VDUP.S32  Q1,   D30[1]             @ Q1:   34816 |  34816 |  34816 |  34816
    VDUP.S32  Q2,   D31[0]             @ Q2:  -70688 | -70688 | -70688 | -70688


    /*-------------------------------------------------------------------------
     *  The main loop
     * ------------------------------------------------------------------------ */
loop_yvup2rgb565:

    /*-------------------------------------------------------------------------
     *  Load input from Y, V and U
     *  D12  : Y0  Y1  Y2  Y3  Y4  Y5  Y6  Y7
     *  D14  : V0  V1  V2  V3  V4  V5  V6  V7
     *  D15  : U0  U1  U2  U3  U4  U5  U6  U7
     * ------------------------------------------------------------------------ */
    VLD1.U8  {D12},  [p_y]!            @ Load 8 Y  elements (uint8) to D12
    VLD1.U8  {D14},  [p_cr]!           @ Load 8 Cr elements (uint8) to D14
    VLD1.U8  {D15},  [p_cb]!           @ Load 8 Cb elements (uint8) to D15

    /*-------------------------------------------------------------------------
     *  Expand uint8 value to uint16
     *  D18, D19: Y0 Y1 Y2 Y3 Y4 Y5 Y6 Y7
     *  D20, D21: V0 V1 V2 V3 V4 V5 V6 V7
     *  D22, D23: U0 U1 U2 U3 U4 U5 U6 U7
     * ------------------------------------------------------------------------ */
    VMOVL.U8 Q9,  D12
    VMOVL.U8 Q10, D14
    VMOVL.U8 Q11, D15

    /*-------------------------------------------------------------------------
     *  Multiply contribution from chrominance, results are in 32-bit
     * ------------------------------------------------------------------------ */
    VMULL.S16  Q12, D20, D6[0]         @ Q12:  359*(V0,V1,V2,V3)     Red
    VMULL.S16  Q13, D22, D6[1]         @ Q13:  -88*(U0,U1,U2,U3)     Green
    VMLAL.S16  Q13, D20, D6[2]         @ Q13:  -88*(U0,U1,U2,U3) - 183*(V0,V1,V2,V3)
    VMULL.S16  Q14, D22, D6[3]         @ Q14:  454*(U0,U1,U2,U3)     Blue

    /*-------------------------------------------------------------------------
     *  Add bias
     * ------------------------------------------------------------------------ */
    VADD.S32  Q12, Q0                  @ Q12 add Red   bias -45824
    VADD.S32  Q13, Q1                  @ Q13 add Green bias  34816
    VADD.S32  Q14, Q2                  @ Q14 add Blue  bias -57984

    /*-------------------------------------------------------------------------
     *  Calculate Red, Green, Blue
     * ------------------------------------------------------------------------ */
    VMLAL.S16  Q12, D18, D7[0]         @ Q12: R0, R1, R2, R3 in 32-bit Q8 format
    VMLAL.S16  Q13, D18, D7[0]         @ Q13: G0, G1, G2, G3 in 32-bit Q8 format
    VMLAL.S16  Q14, D18, D7[0]         @ Q14: B0, B1, B2, B3 in 32-bit Q8 format

    /*-------------------------------------------------------------------------
     *  Right shift eight bits with rounding
     * ------------------------------------------------------------------------ */
    VSHRN.S32   D18 , Q12, #8          @ D18: R0, R1, R2, R3 in 16-bit Q0 format
    VSHRN.S32   D20 , Q13, #8          @ D20: G0, G1, G2, G3 in 16-bit Q0 format
    VSHRN.S32   D22,  Q14, #8          @ D22: B0, B1, B2, B3 in 16-bit Q0 format

    /*-------------------------------------------------------------------------
     *  Done with the first 4 elements, continue on the next 4 elements
     * ------------------------------------------------------------------------ */

    /*-------------------------------------------------------------------------
     *  Multiply contribution from chrominance, results are in 32-bit
     * ------------------------------------------------------------------------ */
    VMULL.S16  Q12, D21, D6[0]         @ Q12:  359*(V0,V1,V2,V3)     Red
    VMULL.S16  Q13, D23, D6[1]         @ Q13:  -88*(U0,U1,U2,U3)     Green
    VMLAL.S16  Q13, D21, D6[2]         @ Q13:  -88*(U0,U1,U2,U3) - 183*(V0,V1,V2,V3)
    VMULL.S16  Q14, D23, D6[3]         @ Q14:  454*(U0,U1,U2,U3)     Blue

    /*-------------------------------------------------------------------------
     *  Add bias
     * ------------------------------------------------------------------------ */
    VADD.S32  Q12, Q0                  @ Q12 add Red   bias -45824
    VADD.S32  Q13, Q1                  @ Q13 add Green bias  34816
    VADD.S32  Q14, Q2                  @ Q14 add Blue  bias -57984

    /*-------------------------------------------------------------------------
     *  Calculate Red, Green, Blue
     * ------------------------------------------------------------------------ */
    VMLAL.S16  Q12, D19, D7[0]         @ Q12: R0, R1, R2, R3 in 32-bit Q8 format
    VMLAL.S16  Q13, D19, D7[0]         @ Q13: G0, G1, G2, G3 in 32-bit Q8 format
    VMLAL.S16  Q14, D19, D7[0]         @ Q14: B0, B1, B2, B3 in 32-bit Q8 format

    /*-------------------------------------------------------------------------
     *  Right shift eight bits with rounding
     * ------------------------------------------------------------------------ */
    VSHRN.S32   D19 , Q12, #8          @ D18: R0, R1, R2, R3 in 16-bit Q0 format
    VSHRN.S32   D21 , Q13, #8          @ D20: G0, G1, G2, G3 in 16-bit Q0 format
    VSHRN.S32   D23,  Q14, #8          @ D22: B0, B1, B2, B3 in 16-bit Q0 format

    /*-------------------------------------------------------------------------
     *  Clamp the value to be within [0~255]
     * ------------------------------------------------------------------------ */
    VMAX.S16  Q9, Q9, Q4               @ if Q9 <   0, Q9 =   0
    VMIN.S16  Q9, Q9, Q5               @ if Q9 > 255, Q9 = 255
    VQMOVUN.S16  D28, Q9               @ store Red to D28, narrow the value from int16 to int8

    VMAX.S16  Q10, Q10, Q4             @ if Q10 <   0, Q10 =   0
    VMIN.S16  Q10, Q10, Q5             @ if Q10 > 255, Q10 = 255
    VQMOVUN.S16   D27, Q10             @ store Green to D27, narrow the value from int16 to int8

    VMAX.S16  Q11, Q11, Q4             @ if Q11 <   0, Q11 =   0
    VMIN.S16  Q11, Q11, Q5             @ if Q11 > 255, Q11 = 255
    VQMOVUN.S16   D26, Q11             @ store Blue to D26, narrow the value from int16 to int8.

    /*-------------------------------------------------------------------------
     *  D27:  3 bits of Green + 5 bits of Blue
     *  D28:  5 bits of Red   + 3 bits of Green
     * ------------------------------------------------------------------------ */
    VSRI.8   D28, D27, #5              @ right shift G by 5 and insert to R
    VSHL.U8  D27, D27, #3              @ left  shift G by 3
    VSRI.8   D27, D26, #3              @ right shift B by 3 and insert to G

    SUBS length, length, #8            @ check if the length is less than 8

    BMI  trailing_yvup2rgb565          @ jump to trailing processing if remaining length is less than 8

    VST2.U8  {D27, D28}, [p_rgb]!      @ vector store Red, Green, Blue to destination
                                       @ Blue at LSB

    BHI loop_yvup2rgb565               @ loop if more than 8 pixels left

    BEQ  end_yvup2rgb565               @ done if exactly 8 pixel processed in the loop


trailing_yvup2rgb565:
    /*-------------------------------------------------------------------------
     *  There are from 1 ~ 7 pixels left in the trailing part.
     *  First adding 7 to the length so the length would be from 0 ~ 6.
     *  eg: 1 pixel left in the trailing part, so 1-8+7 = 0.
     *  Then save 1 pixel unconditionally since at least 1 pixels left in the
     *  trailing part.
     * ------------------------------------------------------------------------ */
    ADDS length, length, #7            @ there are 7 or less in the trailing part

    VST2.U8 {D27[0], D28[0]}, [p_rgb]! @ at least 1 pixel left in the trailing part
    BEQ  end_yvup2rgb565               @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST2.U8 {D27[1], D28[1]}, [p_rgb]! @ store one more pixel
    BEQ  end_yvup2rgb565               @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST2.U8 {D27[2], D28[2]}, [p_rgb]! @ store one more pixel
    BEQ  end_yvup2rgb565               @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST2.U8 {D27[3], D28[3]}, [p_rgb]! @ store one more pixel
    BEQ  end_yvup2rgb565               @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST2.U8 {D27[4], D28[4]}, [p_rgb]! @ store one more pixel
    BEQ  end_yvup2rgb565               @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST2.U8 {D27[5], D28[5]}, [p_rgb]! @ store one more pixel
    BEQ  end_yvup2rgb565               @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST2.U8 {D27[6], D28[6]}, [p_rgb]! @ store one more pixel

end_yvup2rgb565:
    VPOP  {D8-D15}
    LDMFD SP!, {PC}

                                       @ end of yvup2rgb565


/*--------------------------------------------------------------------------
* FUNCTION     : yyvup2rgb565_venum
*--------------------------------------------------------------------------
* DESCRIPTION  : Perform YYVU planar to RGB565 conversion.
*--------------------------------------------------------------------------
* C PROTOTYPE  : void yyvup2rgb565_venum(uint8_t  *p_y,
*                                        uint8_t  *p_cr,
*                                        uint8_t  *p_cb,
*                                        uint8_t  *p_rgb565,
*                                        uint32_t  length)
*--------------------------------------------------------------------------
* REG INPUT    : R0: uint8_t  *p_y
*                      pointer to the input Y Line
*                R1: uint8_t  *p_cr
*                      pointer to the input Cr Line
*                R2: uint8_t  *p_cb
*                      pointer to the input Cb Line
*                R3: uint8_t  *p_rgb565
*                      pointer to the output RGB Line
*                R12: uint32_t  length
*                      width of Line
*--------------------------------------------------------------------------
* STACK ARG    : None
*--------------------------------------------------------------------------
* REG OUTPUT   : None
*--------------------------------------------------------------------------
* MEM INPUT    : p_y      - a line of Y pixels
*                p_cr     - a line of Cr pixels
*                p_cb     - a line of Cb pixels
*                length   - the width of the input line
*--------------------------------------------------------------------------
* MEM OUTPUT   : p_rgb565 - the converted rgb pixels
*--------------------------------------------------------------------------
* REG AFFECTED : ARM:  R0-R4, R12
*                NEON: Q0-Q15
*--------------------------------------------------------------------------
* STACK USAGE  : none
*--------------------------------------------------------------------------
* CYCLES       : none
*
*--------------------------------------------------------------------------
* NOTES        :
*--------------------------------------------------------------------------
*/
.type yyvup2rgb565_venum, %function
yyvup2rgb565_venum:
    /*-------------------------------------------------------------------------
     *  Store stack registers
     * ------------------------------------------------------------------------ */
    STMFD SP!, {LR}

    VPUSH {D8-D15}

    PLD [R0, R3]                       @ preload luma line

    ADR   R12, constants

    VLD1.S16  {D6, D7}, [R12]!         @ D6, D7: 359 |  -88 | -183 | 454 | 256 | 0 | 255 | 0
    VLD1.S32  {D30, D31}, [R12]        @ Q15   :  -45824    |    34816   |  -57984 |     X

    /*-------------------------------------------------------------------------
     *  Load the 5th parameter via stack
     *  R0 ~ R3 are used to pass the first 4 parameters, the 5th and above
     *  parameters are passed via stack
     * ------------------------------------------------------------------------ */
    LDR R12, [SP, #68]                 @ LR is pushed into the stack so SP is
                                       @ decreased by 4,
                                       @ D8-D15 are also pushed into the stack
                                       @ so SP is decreased by
                                       @ 8-byte/D-Register * 8 D-Registers = 64,
                                       @ so SP needs to be increased by 64+4=68
                                       @ to get the value that was first pushed
                                       @ into stack (the 5th parameter passed in
                                       @ throught stack)

    /*-------------------------------------------------------------------------
     *  Load clamping parameters to duplicate vector elements
     * ------------------------------------------------------------------------ */
    VDUP.S16  Q4,  D7[1]               @ Q4:  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0
    VDUP.S16  Q5,  D7[2]               @ Q5: 255 | 255 | 255 | 255 | 255 | 255 | 255 | 255

    /*-------------------------------------------------------------------------
     *  Read bias
     * ------------------------------------------------------------------------ */
    VDUP.S32  Q0,   D30[0]             @ Q0:  -45824 | -45824 | -45824 | -45824
    VDUP.S32  Q1,   D30[1]             @ Q1:   34816 |  34816 |  34816 |  34816
    VDUP.S32  Q2,   D31[0]             @ Q2:  -70688 | -70688 | -70688 | -70688


    /*-------------------------------------------------------------------------
     *  The main loop
     * ------------------------------------------------------------------------ */
loop_yyvup2rgb565:

    /*-------------------------------------------------------------------------
     *  Load input from Y, V and U
     *  D12, D13: Y0 Y2 Y4 Y6 Y8 Y10 Y12 Y14, Y1 Y3 Y5 Y7 Y9 Y11 Y13 Y15
     *  D14     : V0 V1 V2 V3 V4 V5  V6  V7
     *  D15     : U0 U1 U2 U3 U4 U5  U6  U7
     * ------------------------------------------------------------------------ */
    VLD2.U8  {D12,D13}, [p_y]!         @ Load 16 Luma elements (uint8) to D12, D13
    VLD1.U8  {D14},     [p_cr]!        @ Load 8 Cr elements (uint8) to D14
    VLD1.U8  {D15},     [p_cb]!        @ Load 8 Cb elements (uint8) to D15

    /*-------------------------------------------------------------------------
     *  Expand uint8 value to uint16
     *  D24, D25: Y0 Y2 Y4 Y6 Y8 Y10 Y12 Y14
     *  D26, D27: Y1 Y3 Y5 Y7 Y9 Y11 Y13 Y15
     *  D28, D29: V0 V1 V2 V3 V4 V5  V6  V7
     *  D30, D31: U0 U1 U2 U3 U4 U5  U6  U7
     * ------------------------------------------------------------------------ */
    VMOVL.U8 Q12, D12
    VMOVL.U8 Q13, D13
    VMOVL.U8 Q14, D14
    VMOVL.U8 Q15, D15

    /*-------------------------------------------------------------------------
     *  Multiply contribution from chrominance, results are in 32-bit
     * ------------------------------------------------------------------------ */
    VMULL.S16  Q6, D28, D6[0]          @ Q6:  359*(V0,V1,V2,V3)     Red
    VMULL.S16  Q7, D30, D6[1]          @ Q7:  -88*(U0,U1,U2,U3)     Green
    VMLAL.S16  Q7, D28, D6[2]          @ q7:  -88*(U0,U1,U2,U3) - 183*(V0,V1,V2,V3)
    VMULL.S16  Q8, D30, D6[3]          @ q8:  454*(U0,U1,U2,U3)     Blue

    /*-------------------------------------------------------------------------
     *  Add bias
     * ------------------------------------------------------------------------ */
    VADD.S32  Q6, Q0                   @ Q6 add Red   bias -45824
    VADD.S32  Q7, Q1                   @ Q7 add Green bias  34816
    VADD.S32  Q8, Q2                   @ Q8 add Blue  bias -57984

    /*-------------------------------------------------------------------------
     *  Calculate Red, Green, Blue
     * ------------------------------------------------------------------------ */
    VMOV.S32   Q9, Q6
    VMLAL.S16  Q6, D24, D7[0]          @ Q6: R0, R2, R4, R6 in 32-bit Q8 format
    VMLAL.S16  Q9, D26, D7[0]          @ Q9: R1, R3, R5, R7 in 32-bit Q8 format

    VMOV.S32   Q10, Q7
    VMLAL.S16  Q7,  D24, D7[0]         @ Q7:  G0, G2, G4, G6 in 32-bit Q8 format
    VMLAL.S16  Q10, D26, D7[0]         @ Q10: G1, G3, G5, G7 in 32-bit Q8 format

    VMOV.S32   Q11, Q8
    VMLAL.S16  Q8,  D24, D7[0]         @ Q8:  B0, B2, B4, B6 in 32-bit Q8 format
    VMLAL.S16  Q11, D26, D7[0]         @ Q11: B1, B3, B5, B7 in 32-bit Q8 format

    /*-------------------------------------------------------------------------
     *  Right shift eight bits with rounding
     * ------------------------------------------------------------------------ */
    VSHRN.S32   D12, Q6,  #8           @ D12: R0 R2 R4 R6 in 16-bit Q0 format
    VSHRN.S32   D13, Q9,  #8           @ D13: R1 R3 R5 R7 in 16-bit Q0 format
    VZIP.16     D12, D13               @ Q6 : R0 R1 R2 R3 R4 R5 R6 R7

    VSHRN.S32   D18, Q7,  #8           @ D18: G0 G2 G4 G6 in 16-bit Q0 format
    VSHRN.S32   D19, Q10, #8           @ D19: G1 G3 G5 G7 in 16-bit Q0 format
    VZIP.16     D18, D19               @ Q9 : G0 G1 G2 G3 G4 G5 G6 G7

    VSHRN.S32   D20, Q8,  #8           @ D20: B0 B2 B4 B6 in 16-bit Q0 format
    VSHRN.S32   D21, Q11, #8           @ D21: B1 B3 B5 B7 in 16-bit Q0 format
    VZIP.16     D20, D21               @ Q10: B0 B1 B2 B3 B4 B5 B6 B7

    /*-------------------------------------------------------------------------
     *  Clamp the value to be within [0~255]
     * ------------------------------------------------------------------------ */
    VMAX.S16  Q6, Q6, Q4               @ if Q6 <   0, Q6 =   0
    VMIN.S16  Q6, Q6, Q5               @ if Q6 > 255, Q6 = 255
    VQMOVUN.S16  D23, Q6               @ store Red to D23, narrow the value from int16 to int8

    VMAX.S16  Q9, Q9, Q4               @ if Q9 <   0, Q9 =   0
    VMIN.S16  Q9, Q9, Q5               @ if Q9 > 255, Q9 = 255
    VQMOVUN.S16  D22, Q9               @ store Green to D22, narrow the value from int16 to int8

    VMAX.S16  Q10, Q10, Q4             @ if Q10 <   0, Q10 =   0
    VMIN.S16  Q10, Q10, Q5             @ if Q10 > 255, Q10 = 255
    VQMOVUN.S16   D21, Q10             @ store Blue to D21, narrow the value from int16 to int8

    /*-------------------------------------------------------------------------
     *  D22:  3 bits of Green + 5 bits of Blue
     *  D23:  5 bits of Red   + 3 bits of Green
     * ------------------------------------------------------------------------ */
    VSRI.8   D23, D22, #5              @ right shift G by 5 and insert to R
    VSHL.U8  D22, D22, #3              @ left shift G by 3
    VSRI.8   D22, D21, #3              @ right shift B by 3 and insert to G

    SUBS length, length, #8            @ check if the length is less than 8

    BMI  trailing_yyvup2rgb565         @ jump to trailing processing if remaining length is less than 8

    VST2.U8  {D22,D23}, [p_rgb]!       @ vector store Red, Green, Blue to destination
                                       @ Blue at LSB

    BEQ  end_yyvup2rgb565              @ done if exactly 8 pixel processed in the loop


    /*-------------------------------------------------------------------------
     *  Done with the first 8 elements, continue on the next 8 elements
     * ------------------------------------------------------------------------ */

    /*-------------------------------------------------------------------------
     *  Multiply contribution from chrominance, results are in 32-bit
     * ------------------------------------------------------------------------ */
    VMULL.S16  Q6, D29, D6[0]          @ Q6: 359*(V4,V5,V6,V7)       Red
    VMULL.S16  Q7, D31, D6[1]          @ Q7: -88*(U4,U5,U6,U7)      Green
    VMLAL.S16  Q7, D29, D6[2]          @ Q7: -88*(U4,U5,U6,U7) - 183*(V4,V5,V6,V7)
    VMULL.S16  Q8, D31, D6[3]          @ Q8: 454*(U4,U5,U6,U7)       Blue

    /*-------------------------------------------------------------------------
     *  Add bias
     * ------------------------------------------------------------------------ */
    VADD.S32  Q6, Q0                   @ Q6 add Red   bias -45824
    VADD.S32  Q7, Q1                   @ Q7 add Green bias  34816
    VADD.S32  Q8, Q2                   @ Q8 add Blue  bias -57984

    /*-------------------------------------------------------------------------
     *  Calculate Red, Green, Blue
     * ------------------------------------------------------------------------ */
    VMOV.S32   Q9, Q6
    VMLAL.S16  Q6, D25, D7[0]          @ Q6: R8 R10 R12 R14 in 32-bit Q8 format
    VMLAL.S16  Q9, D27, D7[0]          @ Q9: R9 R11 R13 R15 in 32-bit Q8 format

    VMOV.S32   Q10, Q7
    VMLAL.S16  Q7,  D25, D7[0]         @ Q7: G0, G2, G4, G6 in 32-bit Q8 format
    VMLAL.S16  Q10, D27, D7[0]         @ Q10 : G1, G3, G5, G7 in 32-bit Q8 format

    VMOV.S32   Q11, Q8
    VMLAL.S16  Q8,  D25, D7[0]         @ Q8: B0, B2, B4, B6 in 32-bit Q8 format
    VMLAL.S16  Q11, D27, D7[0]         @ Q11 : B1, B3, B5, B7 in 32-bit Q8 format

    /*-------------------------------------------------------------------------
     *  Right shift eight bits with rounding
     * ------------------------------------------------------------------------ */
    VSHRN.S32   D12, Q6,  #8           @ D12: R8 R10 R12 R14 in 16-bit Q0 format
    VSHRN.S32   D13, Q9,  #8           @ D13: R9 R11 R13 R15 in 16-bit Q0 format
    VZIP.16     D12, D13               @ Q6: R8 R9 R10 R11 R12 R13 R14 R15

    VSHRN.S32   D18, Q7,  #8           @ D18: G8 G10 G12 G14 in 16-bit Q0 format
    VSHRN.S32   D19, Q10, #8           @ D19: G9 G11 G13 G15 in 16-bit Q0 format
    VZIP.16     D18, D19               @ Q9:  G8 G9 G10 G11 G12 G13 G14 G15

    VSHRN.S32   D20, Q8,  #8           @ D20: B8 B10 B12 B14 in 16-bit Q0 format
    VSHRN.S32   D21, Q11, #8           @ D21: B9 B11 B13 B15 in 16-bit Q0 format
    VZIP.16     D20, D21               @ Q10: B8 B9 B10 B11 B12 B13 B14 B15

    /*-------------------------------------------------------------------------
     *  Clamp the value to be within [0~255]
     * ------------------------------------------------------------------------ */
    VMAX.S16  Q6, Q6, Q4               @ if Q6 <   0, Q6 =   0
    VMIN.S16  Q6, Q6, Q5               @ if Q6 > 255, Q6 = 255
    VQMOVUN.S16  D23, Q6               @ store Red to D23, narrow the value from int16 to int8

    VMAX.S16  Q9, Q9, Q4               @ if Q9 <   0, Q9 =   0
    VMIN.S16  Q9, Q9, Q5               @ if Q9 > 255, Q9 = 255
    VQMOVUN.S16  D22, Q9               @ store Green to D22, narrow the value from int16 to int8

    VMAX.S16  Q10, Q10, Q4             @ if Q10 <   0, Q10 =   0
    VMIN.S16  Q10, Q10, Q5             @ if Q10 > 255, Q10 = 255
    VQMOVUN.S16   D21, Q10             @ store Blue to D21, narrow the value from int16 to int8

    /*-------------------------------------------------------------------------
     *  D22:  3 bits of Green + 5 bits of Blue
     *  D23:  5 bits of Red   + 3 bits of Green
     * ------------------------------------------------------------------------ */
    VSRI.8   D23, D22, #5              @ right shift G by 5 and insert to R
    VSHL.U8  D22, D22, #3              @ left shift G by 3
    VSRI.8   D22, D21, #3              @ right shift B by 3 and insert to G

    SUBS length, length, #8            @ check if the length is less than 8

    BMI  trailing_yyvup2rgb565         @ jump to trailing processing if remaining length is less than 8

    VST2.U8  {D22,D23}, [p_rgb]!       @ vector store Red, Green, Blue to destination
                                       @ Blue at LSB

    BHI loop_yyvup2rgb565              @ loop if more than 8 pixels left

    BEQ  end_yyvup2rgb565              @ done if exactly 8 pixel processed in the loop


trailing_yyvup2rgb565:
    /*-------------------------------------------------------------------------
     *  There are from 1 ~ 7 pixels left in the trailing part.
     *  First adding 7 to the length so the length would be from 0 ~ 6.
     *  eg: 1 pixel left in the trailing part, so 1-8+7 = 0.
     *  Then save 1 pixel unconditionally since at least 1 pixels left in the
     *  trailing part.
     * ------------------------------------------------------------------------ */
    ADDS length, length, #7            @ there are 7 or less in the trailing part

    VST2.U8 {D22[0],D23[0]}, [p_rgb]!  @ at least 1 pixel left in the trailing part
    BEQ end_yyvup2rgb565               @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST2.U8 {D22[1],D23[1]}, [p_rgb]!  @ store one more pixel
    BEQ end_yyvup2rgb565               @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST2.U8 {D22[2],D23[2]}, [p_rgb]!  @ store one more pixel
    BEQ end_yyvup2rgb565               @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST2.U8 {D22[3],D23[3]}, [p_rgb]!  @ store one more pixel
    BEQ end_yyvup2rgb565               @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST2.U8 {D22[4],D23[4]}, [p_rgb]!  @ store one more pixel
    BEQ end_yyvup2rgb565               @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST2.U8 {D22[5],D23[5]}, [p_rgb]!  @ store one more pixel
    BEQ end_yyvup2rgb565               @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST2.U8 {D22[6],D23[6]}, [p_rgb]!  @ store one more pixel

end_yyvup2rgb565:
    VPOP  {D8-D15}
    LDMFD SP!, {PC}

                                       @ end of yyvup2rgb565

constants:
    .hword (COEFF_V_RED),  (COEFF_U_GREEN), (COEFF_V_GREEN), (COEFF_U_BLUE) @   359  | -88   |  -183  | 454
    .hword (COEFF_Y),      (COEFF_0),       (COEFF_255)    , (COEFF_0)      @   256  |   0   |   255  |  0
    .word  (COEFF_BIAS_R), (COEFF_BIAS_G),  (COEFF_BIAS_B)                  @ -45824 | 34816 | -57984 |  X

/*--------------------------------------------------------------------------
* FUNCTION     : yvup2abgr8888_venum
*--------------------------------------------------------------------------
* DESCRIPTION  : Perform YVU planar to ABGR8888 conversion.
*--------------------------------------------------------------------------
* C PROTOTYPE  : void yvup2abgr8888_venum(uint8_t  *p_y,
*                                         uint8_t  *p_cr,
*                                         uint8_t  *p_cb,
*                                         uint8_t  *p_abgr8888,
*                                         uint32_t  length)
*--------------------------------------------------------------------------
* REG INPUT    : R0: uint8_t  *p_y
*                      pointer to the input Y Line
*                R1: uint8_t  *p_cr
*                      pointer to the input Cr Line
*                R2: uint8_t  *p_cb
*                      pointer to the input Cb Line
*                R3: uint8_t  *p_abgr8888
*                      pointer to the output ABGR Line
*                R12: uint32_t  length
*                      width of Line
*--------------------------------------------------------------------------
* STACK ARG    : None
*--------------------------------------------------------------------------
* REG OUTPUT   : None
*--------------------------------------------------------------------------
* MEM INPUT    : p_y      - a line of Y pixels
*                p_cr     - a line of Cr pixels
*                p_cb     - a line of Cb pixels
*                length   - the width of the input line
*--------------------------------------------------------------------------
* MEM OUTPUT   : p_abgr8888 - the converted ABGR pixels
*--------------------------------------------------------------------------
* REG AFFECTED : ARM:  R0-R4, R12
*                NEON: Q0-Q15
*--------------------------------------------------------------------------
* STACK USAGE  : none
*--------------------------------------------------------------------------
* CYCLES       : none
*
*--------------------------------------------------------------------------
* NOTES        :
*--------------------------------------------------------------------------
*/
.type yvup2abgr8888_venum, %function
yvup2abgr8888_venum:
    /*-------------------------------------------------------------------------
     *  Store stack registers
     * ------------------------------------------------------------------------ */
    STMFD SP!, {LR}

    VPUSH {D8-D15}

    PLD [R0, R3]                       @ preload luma line

    ADR   R12, constants

    VLD1.S16  {D6, D7}, [R12]!         @ D6, D7: 359 |  -88 | -183 | 454 | 256 | 0 | 255 | 0
    VLD1.S32  {D30, D31}, [R12]        @ Q15   :  -45824    |    34816   |  -57984 |     X

    /*-------------------------------------------------------------------------
     *  Load the 5th parameter via stack
     *  R0 ~ R3 are used to pass the first 4 parameters, the 5th and above
     *  parameters are passed via stack
     * ------------------------------------------------------------------------ */
    LDR R12, [SP, #68]                 @ LR is pushed into the stack so SP is
                                       @ decreased by 4,
                                       @ D8-D15 are also pushed into the stack
                                       @ so SP is decreased by
                                       @ 8-byte/D-Register * 8 D-Registers = 64,
                                       @ so SP needs to be increased by 64+4=68
                                       @ to get the value that was first pushed
                                       @ into stack (the 5th parameter passed in
                                       @ throught stack)

    /*-------------------------------------------------------------------------
     *  Load clamping parameters to duplicate vector elements
     * ------------------------------------------------------------------------ */
    VDUP.S16  Q4,  D7[1]               @ Q4:  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0
    VDUP.S16  Q5,  D7[2]               @ Q5: 255 | 255 | 255 | 255 | 255 | 255 | 255 | 255

    /*-------------------------------------------------------------------------
     *  Read bias
     * ------------------------------------------------------------------------ */
    VDUP.S32  Q0,   D30[0]             @ Q0:  -45824 | -45824 | -45824 | -45824
    VDUP.S32  Q1,   D30[1]             @ Q1:   34816 |  34816 |  34816 |  34816
    VDUP.S32  Q2,   D31[0]             @ Q2:  -70688 | -70688 | -70688 | -70688


    /*-------------------------------------------------------------------------
     *  The main loop
     * ------------------------------------------------------------------------ */
loop_yvup2abgr:

    /*-------------------------------------------------------------------------
     *  Load input from Y, V and U
     *  D12  : Y0  Y1  Y2  Y3  Y4  Y5  Y6  Y7
     *  D14  : V0  V1  V2  V3  V4  V5  V6  V7
     *  D15  : U0  U1  U2  U3  U4  U5  U6  U7
     * ------------------------------------------------------------------------ */
    VLD1.U8  {D12},  [p_y]!            @ Load 8 Luma elements (uint8) to D12
    VLD1.U8  {D14},  [p_cr]!           @ Load 8 Cr elements (uint8) to D14
    VLD1.U8  {D15},  [p_cb]!           @ Load 8 Cb elements (uint8) to D15

    /*-------------------------------------------------------------------------
     *  Expand uint8 value to uint16
     *  D18, D19: Y0 Y1 Y2 Y3 Y4 Y5 Y6 Y7
     *  D20, D21: V0 V1 V2 V3 V4 V5 V6 V7
     *  D22, D23: U0 U1 U2 U3 U4 U5 U6 U7
     * ------------------------------------------------------------------------ */
    VMOVL.U8 Q9,  D12
    VMOVL.U8 Q10, D14
    VMOVL.U8 Q11, D15

    /*-------------------------------------------------------------------------
     *  Multiply contribution from chrominance, results are in 32-bit
     * ------------------------------------------------------------------------ */
    VMULL.S16  Q12, D20, D6[0]         @ Q12:  359*(V0,V1,V2,V3)     Red
    VMULL.S16  Q13, D22, D6[1]         @ Q13:  -88*(U0,U1,U2,U3)     Green
    VMLAL.S16  Q13, D20, D6[2]         @ Q13:  -88*(U0,U1,U2,U3) - 183*(V0,V1,V2,V3)
    VMULL.S16  Q14, D22, D6[3]         @ Q14:  454*(U0,U1,U2,U3)     Blue

    /*-------------------------------------------------------------------------
     *  Add bias
     * ------------------------------------------------------------------------ */
    VADD.S32  Q12, Q0                  @ Q12 add Red   bias -45824
    VADD.S32  Q13, Q1                  @ Q13 add Green bias  34816
    VADD.S32  Q14, Q2                  @ Q14 add Blue  bias -57984

    /*-------------------------------------------------------------------------
     *  Calculate Red, Green, Blue
     * ------------------------------------------------------------------------ */
    VMLAL.S16  Q12, D18, D7[0]         @ Q12: R0, R1, R2, R3 in 32-bit Q8 format
    VMLAL.S16  Q13, D18, D7[0]         @ Q13: G0, G1, G2, G3 in 32-bit Q8 format
    VMLAL.S16  Q14, D18, D7[0]         @ Q14: B0, B1, B2, B3 in 32-bit Q8 format

    /*-------------------------------------------------------------------------
     *  Right shift eight bits with rounding
     * ------------------------------------------------------------------------ */
    VSHRN.S32   D18 , Q12, #8          @ D18: R0, R1, R2, R3 in 16-bit Q0 format
    VSHRN.S32   D20 , Q13, #8          @ D20: G0, G1, G2, G3 in 16-bit Q0 format
    VSHRN.S32   D22,  Q14, #8          @ D22: B0, B1, B2, B3 in 16-bit Q0 format

    /*-------------------------------------------------------------------------
     *  Done with the first 4 elements, continue on the next 4 elements
     * ------------------------------------------------------------------------ */

    /*-------------------------------------------------------------------------
     *  Multiply contribution from chrominance, results are in 32-bit
     * ------------------------------------------------------------------------ */
    VMULL.S16  Q12, D21, D6[0]         @ Q12:  359*(V0,V1,V2,V3)     Red
    VMULL.S16  Q13, D23, D6[1]         @ Q13: -88*(U0,U1,U2,U3)     Green
    VMLAL.S16  Q13, D21, D6[2]         @ Q13: -88*(U0,U1,U2,U3) - 183*(V0,V1,V2,V3)
    VMULL.S16  Q14, D23, D6[3]         @ Q14:  454*(U0,U1,U2,U3)     Blue

    /*-------------------------------------------------------------------------
     *  Add bias
     * ------------------------------------------------------------------------ */
    VADD.S32  Q12, Q0                  @ Q12 add Red   bias -45824
    VADD.S32  Q13, Q1                  @ Q13 add Green bias  34816
    VADD.S32  Q14, Q2                  @ Q14 add Blue  bias -57984

    /*-------------------------------------------------------------------------
     *  Calculate Red, Green, Blue
     * ------------------------------------------------------------------------ */
    VMLAL.S16  Q12, D19, D7[0]         @ Q12: R0, R1, R2, R3 in 32-bit Q8 format
    VMLAL.S16  Q13, D19, D7[0]         @ Q13: G0, G1, G2, G3 in 32-bit Q8 format
    VMLAL.S16  Q14, D19, D7[0]         @ Q14: B0, B1, B2, B3 in 32-bit Q8 format

    /*-------------------------------------------------------------------------
     *  Right shift eight bits with rounding
     * ------------------------------------------------------------------------ */
    VSHRN.S32   D19 , Q12, #8          @ D18: R0, R1, R2, R3 in 16-bit Q0 format
    VSHRN.S32   D21 , Q13, #8          @ D20: G0, G1, G2, G3 in 16-bit Q0 format
    VSHRN.S32   D23,  Q14, #8          @ D22: B0, B1, B2, B3 in 16-bit Q0 format

    /*-------------------------------------------------------------------------
     *  Clamp the value to be within [0~255]
     * ------------------------------------------------------------------------ */
    VMAX.S16  Q11, Q11, Q4             @ if Q11 <   0, Q11 =   0
    VMIN.S16  Q11, Q11, Q5             @ if Q11 > 255, Q11 = 255
    VQMOVUN.S16   D28, Q11             @ store Blue to D28, narrow the value from int16 to int8

    VMAX.S16  Q10, Q10, Q4             @ if Q10 <   0, Q10 =   0
    VMIN.S16  Q10, Q10, Q5             @ if Q10 > 255, Q10 = 255
    VQMOVUN.S16   D27, Q10             @ store Green to D27, narrow the value from int16 to int8

    VMAX.S16    Q9, Q9, Q4             @ if Q9 <   0, Q9 =   0
    VMIN.S16    Q9, Q9, Q5             @ if Q9 > 255, Q9 = 255
    VQMOVUN.S16    D26, Q9             @ store Red to D26, narrow the value from int16 to int8

    /*-------------------------------------------------------------------------
     *  abgr format with leading 0xFF byte
     * ------------------------------------------------------------------------ */
    VMOVN.I16  D29, Q5                 @ D29:  255 | 255 | 255 | 255 | 255 | 255 | 255 | 255

    SUBS length, length, #8            @ check if the length is less than 8

    BMI  trailing_yvup2abgr            @ jump to trailing processing if remaining length is less than 8

    VST4.U8  {D26,D27,D28,D29}, [p_bgr]!   @ vector store Red, Green, Blue to destination
                                       @ Blue at LSB

    BHI loop_yvup2abgr                 @ loop if more than 8 pixels left

    BEQ  end_yvup2abgr                 @ done if exactly 8 pixel processed in the loop


trailing_yvup2abgr:
    /*-------------------------------------------------------------------------
     *  There are from 1 ~ 7 pixels left in the trailing part.
     *  First adding 7 to the length so the length would be from 0 ~ 6.
     *  eg: 1 pixel left in the trailing part, so 1-8+7 = 0.
     *  Then save 1 pixel unconditionally since at least 1 pixels left in the
     *  trailing part.
     * ------------------------------------------------------------------------ */
    ADDS length, length, #7            @ there are 7 or less in the trailing part

    VST4.U8 {D26[0], D27[0], D28[0], D29[0]}, [p_bgr]! @ at least 1 pixel left in the trailing part
    BEQ  end_yvup2abgr                 @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST4.U8 {D26[1], D27[1], D28[1], D29[1]}, [p_bgr]!  @ store one more pixel
    BEQ  end_yvup2abgr                 @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST4.U8 {D26[2], D27[2], D28[2], D29[2]}, [p_bgr]!  @ store one more pixel
    BEQ  end_yvup2abgr                 @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST4.U8 {D26[3], D27[3], D28[3], D29[3]}, [p_bgr]!  @ store one more pixel
    BEQ  end_yvup2abgr                 @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST4.U8 {D26[4], D27[4], D28[4], D29[4]}, [p_bgr]!  @ store one more pixel
    BEQ  end_yvup2abgr                 @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST4.U8 {D26[5], D27[5], D28[5], D29[5]}, [p_bgr]!  @ store one more pixel
    BEQ  end_yvup2abgr                 @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST4.U8 {D26[6], D27[6], D28[6], D29[6]}, [p_bgr]! @ store one more pixel

end_yvup2abgr:
    VPOP  {D8-D15}
    LDMFD SP!, {PC}
                                       @ end of yvup2abgr

/*--------------------------------------------------------------------------
* FUNCTION     : yyvup2abgr8888_venum
*--------------------------------------------------------------------------
* DESCRIPTION  : Perform YYVU planar to ABGR8888 conversion.
*--------------------------------------------------------------------------
* C PROTOTYPE  : void yyvup2abgr8888_venum(uint8_t  *p_y,
*                                          uint8_t  *p_cr,
*                                          uint8_t  *p_cb,
*                                          uint8_t  *p_abgr8888,
*                                          uint32_t  length)
*--------------------------------------------------------------------------
* REG INPUT    : R0: uint8_t  *p_y
*                      pointer to the input Y Line
*                R1: uint8_t  *p_cr
*                      pointer to the input Cr Line
*                R2: uint8_t  *p_cb
*                      pointer to the input Cb Line
*                R3: uint8_t  *p_abgr8888
*                      pointer to the output ABGR Line
*                R12: uint32_t  length
*                      width of Line
*--------------------------------------------------------------------------
* STACK ARG    : None
*--------------------------------------------------------------------------
* REG OUTPUT   : None
*--------------------------------------------------------------------------
* MEM INPUT    : p_y      - a line of Y pixels
*                p_cr     - a line of Cr pixels
*                p_cb     - a line of Cb pixels
*                length   - the width of the input line
*--------------------------------------------------------------------------
* MEM OUTPUT   : p_abgr8888 - the converted ABGR pixels
*--------------------------------------------------------------------------
* REG AFFECTED : ARM:  R0-R4, R12
*                NEON: Q0-Q15
*--------------------------------------------------------------------------
* STACK USAGE  : none
*--------------------------------------------------------------------------
* CYCLES       : none
*
*--------------------------------------------------------------------------
* NOTES        :
*--------------------------------------------------------------------------
*/
.type yyvup2abgr8888_venum, %function
yyvup2abgr8888_venum:
    /*-------------------------------------------------------------------------
     *  Store stack registers
     * ------------------------------------------------------------------------ */
    STMFD SP!, {LR}

    VPUSH {D8-D15}

    PLD [R0, R3]                       @ preload luma line

    ADR   R12, constants

    VLD1.S16  {D6, D7}, [R12]!         @ D6, D7: 359 |  -88 | -183 | 454 | 256 | 0 | 255 | 0
    VLD1.S32  {D30, D31}, [R12]        @ Q15   :  -45824    |    34816   |  -57984 |     X

    /*-------------------------------------------------------------------------
     *  Load the 5th parameter via stack
     *  R0 ~ R3 are used to pass the first 4 parameters, the 5th and above
     *  parameters are passed via stack
     * ------------------------------------------------------------------------ */
    LDR R12, [SP, #68]                 @ LR is pushed into the stack so SP is
                                       @ decreased by 4,
                                       @ D8-D15 are also pushed into the stack
                                       @ so SP is decreased by
                                       @ 8-byte/D-Register * 8 D-Registers = 64,
                                       @ so SP needs to be increased by 64+4=68
                                       @ to get the value that was first pushed
                                       @ into stack (the 5th parameter passed in
                                       @ throught stack)

    /*-------------------------------------------------------------------------
     *  Load clamping parameters to duplicate vector elements
     * ------------------------------------------------------------------------ */
    VDUP.S16  Q4,  D7[1]               @ Q4:  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0
    VDUP.S16  Q5,  D7[2]               @ Q5: 255 | 255 | 255 | 255 | 255 | 255 | 255 | 255

    /*-------------------------------------------------------------------------
     *  Read bias
     * ------------------------------------------------------------------------ */
    VDUP.S32  Q0,   D30[0]             @ Q0:  -45824 | -45824 | -45824 | -45824
    VDUP.S32  Q1,   D30[1]             @ Q1:   34816 |  34816 |  34816 |  34816
    VDUP.S32  Q2,   D31[0]             @ Q2:  -70688 | -70688 | -70688 | -70688


    /*-------------------------------------------------------------------------
     *  The main loop
     * ------------------------------------------------------------------------ */
loop_yyvup2abgr:

    /*-------------------------------------------------------------------------
     *  Load input from Y, V and U
     *  D12, D13: Y0 Y2 Y4 Y6 Y8 Y10 Y12 Y14, Y1 Y3 Y5 Y7 Y9 Y11 Y13 Y15
     *  D14  : V0  V1  V2  V3  V4  V5  V6  V7
     *  D15  : U0  U1  U2  U3  U4  U5  U6  U7
     * ------------------------------------------------------------------------ */
    VLD2.U8  {D12,D13}, [p_y]!         @ Load 16 Luma elements (uint8) to D12, D13
    VLD1.U8  {D14},  [p_cr]!           @ Load 8 Cr elements (uint8) to D14
    VLD1.U8  {D15},  [p_cb]!           @ Load 8 Cb elements (uint8) to D15

    /*-------------------------------------------------------------------------
     *  Expand uint8 value to uint16
     *  D24, D25: Y0 Y2 Y4 Y6 Y8 Y10 Y12 Y14
     *  D26, D27: Y1 Y3 Y5 Y7 Y9 Y11 Y13 Y15
     *  D28, D29: V0 V1 V2 V3 V4 V5  V6  V7
     *  D30, D31: U0 U1 U2 U3 U4 U5  U6  U7
     * ------------------------------------------------------------------------ */
    VMOVL.U8 Q12, D12
    VMOVL.U8 Q13, D13
    VMOVL.U8 Q14, D14
    VMOVL.U8 Q15, D15

    /*-------------------------------------------------------------------------
     *  Multiply contribution from chrominance, results are in 32-bit
     * ------------------------------------------------------------------------ */
    VMULL.S16  Q6, D28, D6[0]          @ Q6:  359*(V0,V1,V2,V3)     Red
    VMULL.S16  Q7, D30, D6[1]          @ Q7: -88*(U0,U1,U2,U3)     Green
    VMLAL.S16  Q7, D28, D6[2]          @ Q7: -88*(U0,U1,U2,U3) - 183*(V0,V1,V2,V3)
    VMULL.S16  Q8, D30, D6[3]          @ Q8:  454*(U0,U1,U2,U3)     Blue

    /*-------------------------------------------------------------------------
     *  Add bias
     * ------------------------------------------------------------------------ */
    VADD.S32  Q6, Q0                   @ Q6 add Red   bias -45824
    VADD.S32  Q7, Q1                   @ Q7 add Green bias  34816
    VADD.S32  Q8, Q2                   @ Q8 add Blue  bias -57984

    /*-------------------------------------------------------------------------
     *  Calculate Red, Green, Blue
     * ------------------------------------------------------------------------ */
    VMOV.S32   Q9, Q6
    VMLAL.S16  Q6, D24, D7[0]          @ Q6: R0, R2, R4, R6 in 32-bit Q8 format
    VMLAL.S16  Q9, D26, D7[0]          @ Q9: R1, R3, R5, R7 in 32-bit Q8 format

    VMOV.S32   Q10, Q7
    VMLAL.S16  Q7,  D24, D7[0]         @ Q7:  G0, G2, G4, G6 in 32-bit Q8 format
    VMLAL.S16  Q10, D26, D7[0]         @ Q10: G1, G3, G5, G7 in 32-bit Q8 format

    VMOV.S32   Q11, Q8
    VMLAL.S16  Q8,  D24, D7[0]         @ Q8:  B0, B2, B4, B6 in 32-bit Q8 format
    VMLAL.S16  Q11, D26, D7[0]         @ Q11: B1, B3, B5, B7 in 32-bit Q8 format

    /*-------------------------------------------------------------------------
     *  Right shift eight bits with rounding
     * ------------------------------------------------------------------------ */
    VSHRN.S32   D12, Q6,  #8           @ D12: R0 R2 R4 R6 in 16-bit Q0 format
    VSHRN.S32   D13, Q9,  #8           @ D13: R1 R3 R5 R7 in 16-bit Q0 format
    VZIP.16     D12, D13               @ Q6 : R0 R1 R2 R3 R4 R5 R6 R7

    VSHRN.S32   D18, Q7,  #8           @ D18: G0 G2 G4 G6 in 16-bit Q0 format
    VSHRN.S32   D19, Q10, #8           @ D19: G1 G3 G5 G7 in 16-bit Q0 format
    VZIP.16     D18, D19               @ Q9 : G0 G1 G2 G3 G4 G5 G6 G7

    VSHRN.S32   D20, Q8,  #8           @ D20: B0 B2 B4 B6 in 16-bit Q0 format
    VSHRN.S32   D21, Q11, #8           @ D21: B1 B3 B5 B7 in 16-bit Q0 format
    VZIP.16     D20, D21               @ Q10: B0 B1 B2 B3 B4 B5 B6 B7

    /*-------------------------------------------------------------------------
     *  Clamp the value to be within [0~255]
     * ------------------------------------------------------------------------ */
    VMAX.S16  Q10, Q10, Q4             @ if Q10 <   0, Q10 =   0
    VMIN.S16  Q10, Q10, Q5             @ if Q10 > 255, Q10 = 255
    VQMOVUN.S16   D23, Q10             @ store Blue to D23, narrow the value from int16 to int8

    VMAX.S16  Q9, Q9, Q4               @ if Q9 <   0, Q9 =   0
    VMIN.S16  Q9, Q9, Q5               @ if Q9 > 255, Q9 = 255
    VQMOVUN.S16  D22, Q9               @ store Green to D22, narrow the value from int16 to int8

    VMAX.S16  Q6, Q6, Q4               @ if Q6 <   0, Q6 =   0
    VMIN.S16  Q6, Q6, Q5               @ if Q6 > 255, Q6 = 255
    VQMOVUN.S16  D21, Q6               @ store Red to D21, narrow the value from int16 to int8

    /*-------------------------------------------------------------------------
     *  abgr format with leading 0xFF byte
     * ------------------------------------------------------------------------ */
    VMOVN.I16  D24, Q5                 @ D24:  255 | 255 | 255 | 255 | 255 | 255 | 255 | 255

    SUBS length, length, #8            @ check if the length is less than 8

    BMI  trailing_yyvup2abgr           @ jump to trailing processing if remaining length is less than 8

    VST4.U8  {D21,D22,D23,D24}, [p_bgr]!   @ vector store Blue, Green, Red to destination
                                       @ Red at LSB

    BEQ  end_yyvup2abgr                @ done if exactly 8 pixel processed in the loop


    /*-------------------------------------------------------------------------
     *  Done with the first 8 elements, continue on the next 8 elements
     * ------------------------------------------------------------------------ */

    /*-------------------------------------------------------------------------
     *  Multiply contribution from chrominance, results are in 32-bit
     * ------------------------------------------------------------------------ */
    VMULL.S16  Q6, D29, D6[0]          @ Q6: 359*(V4,V5,V6,V7)       Red
    VMULL.S16  Q7, D31, D6[1]          @ Q7: -88*(U4,U5,U6,U7)      Green
    VMLAL.S16  Q7, D29, D6[2]          @ Q7: -88*(U4,U5,U6,U7) - 183*(V4,V5,V6,V7)
    VMULL.S16  Q8, D31, D6[3]          @ Q8: 454*(U4,U5,U6,U7)       Blue

    /*-------------------------------------------------------------------------
     *  Add bias
     * ------------------------------------------------------------------------ */
    VADD.S32  Q6, Q0                   @ Q6 add Red   bias -45824
    VADD.S32  Q7, Q1                   @ Q7 add Green bias  34816
    VADD.S32  Q8, Q2                   @ Q8 add Blue  bias -57984

    /*-------------------------------------------------------------------------
     *  Calculate Red, Green, Blue
     * ------------------------------------------------------------------------ */
    VMOV.S32   Q9, Q6
    VMLAL.S16  Q6, D25, D7[0]          @ Q6: R8 R10 R12 R14 in 32-bit Q8 format
    VMLAL.S16  Q9, D27, D7[0]          @ Q9: R9 R11 R13 R15 in 32-bit Q8 format

    VMOV.S32   Q10, Q7
    VMLAL.S16  Q7,  D25, D7[0]         @ Q7: G0, G2, G4, G6 in 32-bit Q8 format
    VMLAL.S16  Q10, D27, D7[0]         @ Q10 : G1, G3, G5, G7 in 32-bit Q8 format

    VMOV.S32   Q11, Q8
    VMLAL.S16  Q8,  D25, D7[0]         @ Q8: B0, B2, B4, B6 in 32-bit Q8 format
    VMLAL.S16  Q11, D27, D7[0]         @ Q11 : B1, B3, B5, B7 in 32-bit Q8 format

    /*-------------------------------------------------------------------------
     *  Right shift eight bits with rounding
     * ------------------------------------------------------------------------ */
    VSHRN.S32   D12, Q6,  #8           @ D12: R8 R10 R12 R14 in 16-bit Q0 format
    VSHRN.S32   D13, Q9,  #8           @ D13: R9 R11 R13 R15 in 16-bit Q0 format
    VZIP.16     D12, D13               @ Q6: R8 R9 R10 R11 R12 R13 R14 R15

    VSHRN.S32   D18, Q7,  #8           @ D18: G8 G10 G12 G14 in 16-bit Q0 format
    VSHRN.S32   D19, Q10, #8           @ D19: G9 G11 G13 G15 in 16-bit Q0 format
    VZIP.16     D18, D19               @ Q9:  G8 G9 G10 G11 G12 G13 G14 G15

    VSHRN.S32   D20, Q8,  #8           @ D20: B8 B10 B12 B14 in 16-bit Q0 format
    VSHRN.S32   D21, Q11, #8           @ D21: B9 B11 B13 B15 in 16-bit Q0 format
    VZIP.16     D20, D21               @ Q10: B8 B9 B10 B11 B12 B13 B14 B15

    /*-------------------------------------------------------------------------
     *  Clamp the value to be within [0~255]
     * ------------------------------------------------------------------------ */
    VMAX.S16  Q10, Q10, Q4             @ if Q10 <   0, Q10 =   0
    VMIN.S16  Q10, Q10, Q5             @ if Q10 > 255, Q10 = 255
    VQMOVUN.S16   D23, Q10             @ store Blue to D23, narrow the value from int16 to int8

    VMAX.S16  Q9, Q9, Q4               @ if Q9 <   0, Q9 =   0
    VMIN.S16  Q9, Q9, Q5               @ if Q9 > 255, Q9 = 255
    VQMOVUN.S16  D22, Q9               @ store Green to D22, narrow the value from int16 to int8

    VMAX.S16  Q6, Q6, Q4               @ if Q6 <   0, Q6 =   0
    VMIN.S16  Q6, Q6, Q5               @ if Q6 > 255, Q6 = 255
    VQMOVUN.S16  D21, Q6               @ store Red to D21, narrow the value from int16 to int8

    /*-------------------------------------------------------------------------
     *  abgr format with leading 0xFF byte
     * ------------------------------------------------------------------------ */
    VMOVN.I16  D24, Q5                 @ D24:  255 | 255 | 255 | 255 | 255 | 255 | 255 | 255

    SUBS length, length, #8            @ check if the length is less than 8

    BMI  trailing_yyvup2abgr           @ jump to trailing processing if remaining length is less than 8

    VST4.U8  {D21,D22,D23,D24}, [p_bgr]!   @ vector store Blue, Green, Red to destination
                                       @ Red at LSB

    BHI loop_yyvup2abgr                @ loop if more than 8 pixels left

    BEQ  end_yyvup2abgr                @ done if exactly 8 pixel processed in the loop


trailing_yyvup2abgr:
    /*-------------------------------------------------------------------------
     *  There are from 1 ~ 7 pixels left in the trailing part.
     *  First adding 7 to the length so the length would be from 0 ~ 6.
     *  eg: 1 pixel left in the trailing part, so 1-8+7 = 0.
     *  Then save 1 pixel unconditionally since at least 1 pixels left in the
     *  trailing part.
     * ------------------------------------------------------------------------ */
    ADDS length, length, #7            @ there are 7 or less in the trailing part

    VST4.U8 {D21[0],D22[0],D23[0],D24[0]}, [p_bgr]! @ at least 1 pixel left in the trailing part
    BEQ end_yyvup2abgr                 @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST4.U8 {D21[1],D22[1],D23[1],D24[1]}, [p_bgr]!  @ store one more pixel
    BEQ end_yyvup2abgr                 @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST4.U8 {D21[2],D22[2],D23[2],D24[2]}, [p_bgr]!  @ store one more pixel
    BEQ end_yyvup2abgr                 @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST4.U8 {D21[3],D22[3],D23[3],D24[3]}, [p_bgr]!  @ store one more pixel
    BEQ end_yyvup2abgr                 @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST4.U8 {D21[4],D22[4],D23[4],D24[4]}, [p_bgr]!  @ store one more pixel
    BEQ end_yyvup2abgr                 @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST4.U8 {D21[5],D22[5],D23[5],D24[5]}, [p_bgr]!  @ store one more pixel
    BEQ end_yyvup2abgr                 @ done if 0 pixel left

    SUBS length, length, #1            @ update length counter
    VST4.U8 {D21[6],D22[6],D23[6],D24[6]}, [p_bgr]!  @ store one more pixel

end_yyvup2abgr:
    VPOP  {D8-D15}
    LDMFD SP!, {PC}
                                       @ end of yyvup2abgr

.end

