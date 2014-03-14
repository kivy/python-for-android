/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package org.apache.commons.compress.archivers.tar;

import static org.apache.commons.compress.archivers.tar.TarConstants.CHKSUMLEN;
import static org.apache.commons.compress.archivers.tar.TarConstants.CHKSUM_OFFSET;

import java.io.IOException;
import java.math.BigInteger;
import java.nio.ByteBuffer;
import org.apache.commons.compress.archivers.zip.ZipEncoding;
import org.apache.commons.compress.archivers.zip.ZipEncodingHelper;

/**
 * This class provides static utility methods to work with byte streams.
 *
 * @Immutable
 */
// CheckStyle:HideUtilityClassConstructorCheck OFF (bc)
public class TarUtils {

    private static final int BYTE_MASK = 255;

    static final ZipEncoding DEFAULT_ENCODING =
        ZipEncodingHelper.getZipEncoding(null);

    /**
     * Encapsulates the algorithms used up to Commons Compress 1.3 as
     * ZipEncoding.
     */
    static final ZipEncoding FALLBACK_ENCODING = new ZipEncoding() {
            public boolean canEncode(String name) { return true; }

            public ByteBuffer encode(String name) {
                final int length = name.length();
                byte[] buf = new byte[length];

                // copy until end of input or output is reached.
                for (int i = 0; i < length; ++i) {
                    buf[i] = (byte) name.charAt(i);
                }
                return ByteBuffer.wrap(buf);
            }

            public String decode(byte[] buffer) {
                final int length = buffer.length;
                StringBuilder result = new StringBuilder(length);

                for (int i = 0; i < length; ++i) {
                    byte b = buffer[i];
                    if (b == 0) { // Trailing null
                        break;
                    }
                    result.append((char) (b & 0xFF)); // Allow for sign-extension
                }

                return result.toString();
            }
        };

    /** Private constructor to prevent instantiation of this utility class. */
    private TarUtils(){
    }

    /**
     * Parse an octal string from a buffer.
     *
     * <p>Leading spaces are ignored.
     * The buffer must contain a trailing space or NUL,
     * and may contain an additional trailing space or NUL.</p>
     *
     * <p>The input buffer is allowed to contain all NULs,
     * in which case the method returns 0L
     * (this allows for missing fields).</p>
     *
     * <p>To work-around some tar implementations that insert a
     * leading NUL this method returns 0 if it detects a leading NUL
     * since Commons Compress 1.4.</p>
     *
     * @param buffer The buffer from which to parse.
     * @param offset The offset into the buffer from which to parse.
     * @param length The maximum number of bytes to parse - must be at least 2 bytes.
     * @return The long value of the octal string.
     * @throws IllegalArgumentException if the trailing space/NUL is missing or if a invalid byte is detected.
     */
    public static long parseOctal(final byte[] buffer, final int offset, final int length) {
        long    result = 0;
        int     end = offset + length;
        int     start = offset;

        if (length < 2){
            throw new IllegalArgumentException("Length "+length+" must be at least 2");
        }

        if (buffer[start] == 0) {
            return 0L;
        }

        // Skip leading spaces
        while (start < end){
            if (buffer[start] == ' '){
                start++;
            } else {
                break;
            }
        }

        // Must have trailing NUL or space
        byte trailer;
        trailer = buffer[end-1];
        if (trailer == 0 || trailer == ' '){
            end--;
        } else {
            throw new IllegalArgumentException(
                    exceptionMessage(buffer, offset, length, end-1, trailer));
        }
        // May have additional NULs or spaces
        trailer = buffer[end - 1];
        while (start < end - 1 && (trailer == 0 || trailer == ' ')) {
            end--;
            trailer = buffer[end - 1];
        }

        for ( ;start < end; start++) {
            final byte currentByte = buffer[start];
            // CheckStyle:MagicNumber OFF
            if (currentByte < '0' || currentByte > '7'){
                throw new IllegalArgumentException(
                        exceptionMessage(buffer, offset, length, start, currentByte));
            }
            result = (result << 3) + (currentByte - '0'); // convert from ASCII
            // CheckStyle:MagicNumber ON
        }

        return result;
    }

    /** 
     * Compute the value contained in a byte buffer.  If the most
     * significant bit of the first byte in the buffer is set, this
     * bit is ignored and the rest of the buffer is interpreted as a
     * binary number.  Otherwise, the buffer is interpreted as an
     * octal number as per the parseOctal function above.
     *
     * @param buffer The buffer from which to parse.
     * @param offset The offset into the buffer from which to parse.
     * @param length The maximum number of bytes to parse.
     * @return The long value of the octal or binary string.
     * @throws IllegalArgumentException if the trailing space/NUL is
     * missing or an invalid byte is detected in an octal number, or
     * if a binary number would exceed the size of a signed long
     * 64-bit integer.
     * @since 1.4
     */
    public static long parseOctalOrBinary(final byte[] buffer, final int offset,
                                          final int length) {

        if ((buffer[offset] & 0x80) == 0) {
            return parseOctal(buffer, offset, length);
        }
        final boolean negative = buffer[offset] == (byte) 0xff;
        if (length < 9) {
            return parseBinaryLong(buffer, offset, length, negative);
        }
        return parseBinaryBigInteger(buffer, offset, length, negative);
    }

    private static long parseBinaryLong(final byte[] buffer, final int offset,
                                        final int length,
                                        final boolean negative) {
        if (length >= 9) {
            throw new IllegalArgumentException("At offset " + offset + ", "
                                               + length + " byte binary number"
                                               + " exceeds maximum signed long"
                                               + " value");
        }
        long val = 0;
        for (int i = 1; i < length; i++) {
            val = (val << 8) + (buffer[offset + i] & 0xff);
        }
        if (negative) {
            // 2's complement
            val--;
            val ^= (long) Math.pow(2, (length - 1) * 8) - 1;
        }
        return negative ? -val : val;
    }

    private static long parseBinaryBigInteger(final byte[] buffer,
                                              final int offset,
                                              final int length,
                                              final boolean negative) {
        byte[] remainder = new byte[length - 1];
        System.arraycopy(buffer, offset + 1, remainder, 0, length - 1);
        BigInteger val = new BigInteger(remainder);
        if (negative) {
            // 2's complement
            val = val.add(BigInteger.valueOf(-1)).not();
        }
        if (val.bitLength() > 63) {
            throw new IllegalArgumentException("At offset " + offset + ", "
                                               + length + " byte binary number"
                                               + " exceeds maximum signed long"
                                               + " value");
        }
        return negative ? -val.longValue() : val.longValue();
    }

    /**
     * Parse a boolean byte from a buffer.
     * Leading spaces and NUL are ignored.
     * The buffer may contain trailing spaces or NULs.
     *
     * @param buffer The buffer from which to parse.
     * @param offset The offset into the buffer from which to parse.
     * @return The boolean value of the bytes.
     * @throws IllegalArgumentException if an invalid byte is detected.
     */
    public static boolean parseBoolean(final byte[] buffer, final int offset) {
        return buffer[offset] == 1;
    }

    // Helper method to generate the exception message
    private static String exceptionMessage(byte[] buffer, final int offset,
            final int length, int current, final byte currentByte) {
        // default charset is good enough for an exception message,
        //
        // the alternative was to modify parseOctal and
        // parseOctalOrBinary to receive the ZipEncoding of the
        // archive (deprecating the existing public methods, of
        // course) and dealing with the fact that ZipEncoding#decode
        // can throw an IOException which parseOctal* doesn't declare
        String string = new String(buffer, offset, length);

        string=string.replaceAll("\0", "{NUL}"); // Replace NULs to allow string to be printed
        final String s = "Invalid byte "+currentByte+" at offset "+(current-offset)+" in '"+string+"' len="+length;
        return s;
    }

    /**
     * Parse an entry name from a buffer.
     * Parsing stops when a NUL is found
     * or the buffer length is reached.
     *
     * @param buffer The buffer from which to parse.
     * @param offset The offset into the buffer from which to parse.
     * @param length The maximum number of bytes to parse.
     * @return The entry name.
     */
    public static String parseName(byte[] buffer, final int offset, final int length) {
        try {
            return parseName(buffer, offset, length, DEFAULT_ENCODING);
        } catch (IOException ex) {
            try {
                return parseName(buffer, offset, length, FALLBACK_ENCODING);
            } catch (IOException ex2) {
                // impossible
                throw new RuntimeException(ex2);
            }
        }
    }

    /**
     * Parse an entry name from a buffer.
     * Parsing stops when a NUL is found
     * or the buffer length is reached.
     *
     * @param buffer The buffer from which to parse.
     * @param offset The offset into the buffer from which to parse.
     * @param length The maximum number of bytes to parse.
     * @param encoding name of the encoding to use for file names
     * @since 1.4
     * @return The entry name.
     */
    public static String parseName(byte[] buffer, final int offset,
                                   final int length,
                                   final ZipEncoding encoding)
        throws IOException {

        int len = length;
        for (; len > 0; len--) {
            if (buffer[offset + len - 1] != 0) {
                break;
            }
        }
        if (len > 0) {
            byte[] b = new byte[len];
            System.arraycopy(buffer, offset, b, 0, len);
            return encoding.decode(b);
        }
        return "";
    }

    /**
     * Copy a name into a buffer.
     * Copies characters from the name into the buffer
     * starting at the specified offset. 
     * If the buffer is longer than the name, the buffer
     * is filled with trailing NULs.
     * If the name is longer than the buffer,
     * the output is truncated.
     *
     * @param name The header name from which to copy the characters.
     * @param buf The buffer where the name is to be stored.
     * @param offset The starting offset into the buffer
     * @param length The maximum number of header bytes to copy.
     * @return The updated offset, i.e. offset + length
     */
    public static int formatNameBytes(String name, byte[] buf, final int offset, final int length) {
        try {
            return formatNameBytes(name, buf, offset, length, DEFAULT_ENCODING);
        } catch (IOException ex) {
            try {
                return formatNameBytes(name, buf, offset, length,
                                       FALLBACK_ENCODING);
            } catch (IOException ex2) {
                // impossible
                throw new RuntimeException(ex2);
            }
        }
    }

    /**
     * Copy a name into a buffer.
     * Copies characters from the name into the buffer
     * starting at the specified offset. 
     * If the buffer is longer than the name, the buffer
     * is filled with trailing NULs.
     * If the name is longer than the buffer,
     * the output is truncated.
     *
     * @param name The header name from which to copy the characters.
     * @param buf The buffer where the name is to be stored.
     * @param offset The starting offset into the buffer
     * @param length The maximum number of header bytes to copy.
     * @param encoding name of the encoding to use for file names
     * @since 1.4
     * @return The updated offset, i.e. offset + length
     */
    public static int formatNameBytes(String name, byte[] buf, final int offset,
                                      final int length,
                                      final ZipEncoding encoding)
        throws IOException {
        int len = name.length();
        ByteBuffer b = encoding.encode(name);
        while (b.limit() > length && len > 0) {
            b = encoding.encode(name.substring(0, --len));
        }
        final int limit = b.limit() - b.position();
        System.arraycopy(b.array(), b.arrayOffset(), buf, offset, limit);

        // Pad any remaining output bytes with NUL
        for (int i = limit; i < length; ++i) {
            buf[offset + i] = 0;
        }

        return offset + length;
    }

    /**
     * Fill buffer with unsigned octal number, padded with leading zeroes.
     * 
     * @param value number to convert to octal - treated as unsigned
     * @param buffer destination buffer
     * @param offset starting offset in buffer
     * @param length length of buffer to fill
     * @throws IllegalArgumentException if the value will not fit in the buffer
     */
    public static void formatUnsignedOctalString(final long value, byte[] buffer,
            final int offset, final int length) {
        int remaining = length;
        remaining--;
        if (value == 0) {
            buffer[offset + remaining--] = (byte) '0';
        } else {
            long val = value;
            for (; remaining >= 0 && val != 0; --remaining) {
                // CheckStyle:MagicNumber OFF
                buffer[offset + remaining] = (byte) ((byte) '0' + (byte) (val & 7));
                val = val >>> 3;
                // CheckStyle:MagicNumber ON
            }
            if (val != 0){
                throw new IllegalArgumentException
                (value+"="+Long.toOctalString(value)+ " will not fit in octal number buffer of length "+length);
            }
        }

        for (; remaining >= 0; --remaining) { // leading zeros
            buffer[offset + remaining] = (byte) '0';
        }
    }

    /**
     * Write an octal integer into a buffer.
     *
     * Uses {@link #formatUnsignedOctalString} to format
     * the value as an octal string with leading zeros.
     * The converted number is followed by space and NUL
     * 
     * @param value The value to write
     * @param buf The buffer to receive the output
     * @param offset The starting offset into the buffer
     * @param length The size of the output buffer
     * @return The updated offset, i.e offset+length
     * @throws IllegalArgumentException if the value (and trailer) will not fit in the buffer
     */
    public static int formatOctalBytes(final long value, byte[] buf, final int offset, final int length) {

        int idx=length-2; // For space and trailing null
        formatUnsignedOctalString(value, buf, offset, idx);

        buf[offset + idx++] = (byte) ' '; // Trailing space
        buf[offset + idx]   = 0; // Trailing null

        return offset + length;
    }

    /**
     * Write an octal long integer into a buffer.
     * 
     * Uses {@link #formatUnsignedOctalString} to format
     * the value as an octal string with leading zeros.
     * The converted number is followed by a space.
     * 
     * @param value The value to write as octal
     * @param buf The destinationbuffer.
     * @param offset The starting offset into the buffer.
     * @param length The length of the buffer
     * @return The updated offset
     * @throws IllegalArgumentException if the value (and trailer) will not fit in the buffer
     */
    public static int formatLongOctalBytes(final long value, byte[] buf, final int offset, final int length) {

        int idx=length-1; // For space

        formatUnsignedOctalString(value, buf, offset, idx);
        buf[offset + idx] = (byte) ' '; // Trailing space

        return offset + length;
    }

    /**
     * Write an long integer into a buffer as an octal string if this
     * will fit, or as a binary number otherwise.
     * 
     * Uses {@link #formatUnsignedOctalString} to format
     * the value as an octal string with leading zeros.
     * The converted number is followed by a space.
     * 
     * @param value The value to write into the buffer.
     * @param buf The destination buffer.
     * @param offset The starting offset into the buffer.
     * @param length The length of the buffer.
     * @return The updated offset.
     * @throws IllegalArgumentException if the value (and trailer)
     * will not fit in the buffer.
     * @since 1.4
     */
    public static int formatLongOctalOrBinaryBytes(
        final long value, byte[] buf, final int offset, final int length) {

        // Check whether we are dealing with UID/GID or SIZE field
        final long maxAsOctalChar = length == TarConstants.UIDLEN ? TarConstants.MAXID : TarConstants.MAXSIZE;

        final boolean negative = value < 0;
        if (!negative && value <= maxAsOctalChar) { // OK to store as octal chars
            return formatLongOctalBytes(value, buf, offset, length);
        }

        if (length < 9) {
            formatLongBinary(value, buf, offset, length, negative);
        }
        formatBigIntegerBinary(value, buf, offset, length, negative);

        buf[offset] = (byte) (negative ? 0xff : 0x80);
        return offset + length;
    }

    private static void formatLongBinary(final long value, byte[] buf,
                                         final int offset, final int length,
                                         final boolean negative) {
        final int bits = (length - 1) * 8;
        final long max = 1l << bits;
        long val = Math.abs(value);
        if (val >= max) {
            throw new IllegalArgumentException("Value " + value +
                " is too large for " + length + " byte field.");
        }
        if (negative) {
            val ^= max - 1;
            val |= 0xff << bits;
            val++;
        }
        for (int i = offset + length - 1; i >= offset; i--) {
            buf[i] = (byte) val;
            val >>= 8;
        }
    }

    private static void formatBigIntegerBinary(final long value, byte[] buf,
                                               final int offset,
                                               final int length,
                                               final boolean negative) {
        BigInteger val = BigInteger.valueOf(value);
        final byte[] b = val.toByteArray();
        final int len = b.length;
        final int off = offset + length - len;
        System.arraycopy(b, 0, buf, off, len);
        final byte fill = (byte) (negative ? 0xff : 0);
        for (int i = offset + 1; i < off; i++) {
            buf[i] = fill;
        }
    }

    /**
     * Writes an octal value into a buffer.
     * 
     * Uses {@link #formatUnsignedOctalString} to format
     * the value as an octal string with leading zeros.
     * The converted number is followed by NUL and then space.
     *
     * @param value The value to convert
     * @param buf The destination buffer
     * @param offset The starting offset into the buffer.
     * @param length The size of the buffer.
     * @return The updated value of offset, i.e. offset+length
     * @throws IllegalArgumentException if the value (and trailer) will not fit in the buffer
     */
    public static int formatCheckSumOctalBytes(final long value, byte[] buf, final int offset, final int length) {

        int idx=length-2; // for NUL and space
        formatUnsignedOctalString(value, buf, offset, idx);

        buf[offset + idx++]   = 0; // Trailing null
        buf[offset + idx]     = (byte) ' '; // Trailing space

        return offset + length;
    }

    /**
     * Compute the checksum of a tar entry header.
     *
     * @param buf The tar entry's header buffer.
     * @return The computed checksum.
     */
    public static long computeCheckSum(final byte[] buf) {
        long sum = 0;

        for (byte element : buf) {
            sum += BYTE_MASK & element;
        }

        return sum;
    }

    /**
     * Wikipedia <a href="http://en.wikipedia.org/wiki/Tar_(file_format)#File_header">says</a>:
     * <blockquote>
     * The checksum is calculated by taking the sum of the unsigned byte values
     * of the header block with the eight checksum bytes taken to be ascii
     * spaces (decimal value 32). It is stored as a six digit octal number with
     * leading zeroes followed by a NUL and then a space. Various
     * implementations do not adhere to this format. For better compatibility,
     * ignore leading and trailing whitespace, and get the first six digits. In
     * addition, some historic tar implementations treated bytes as signed.
     * Implementations typically calculate the checksum both ways, and treat it
     * as good if either the signed or unsigned sum matches the included
     * checksum.
     * </blockquote>
     * <p>
     * In addition there are
     * <a href="https://issues.apache.org/jira/browse/COMPRESS-117">some tar files</a>
     * that seem to have parts of their header cleared to zero (no detectable
     * magic bytes, etc.) but still have a reasonable-looking checksum field
     * present. It looks like we can detect such cases reasonably well by
     * checking whether the stored checksum is <em>greater than</em> the
     * computed unsigned checksum. That check is unlikely to pass on some
     * random file header, as it would need to have a valid sequence of
     * octal digits in just the right place.
     * <p>
     * The return value of this method should be treated as a best-effort
     * heuristic rather than an absolute and final truth. The checksum
     * verification logic may well evolve over time as more special cases
     * are encountered.
     *
     * @param header tar header
     * @return whether the checksum is reasonably good
     * @see <a href="https://issues.apache.org/jira/browse/COMPRESS-191">COMPRESS-191</a>
     * @since 1.5
     */
    public static boolean verifyCheckSum(byte[] header) {
        long storedSum = 0;
        long unsignedSum = 0;
        long signedSum = 0;

        int digits = 0;
        for (int i = 0; i < header.length; i++) {
            byte b = header[i];
            if (CHKSUM_OFFSET  <= i && i < CHKSUM_OFFSET + CHKSUMLEN) {
                if ('0' <= b && b <= '7' && digits++ < 6) {
                    storedSum = storedSum * 8 + b - '0';
                } else if (digits > 0) {
                    digits = 6; // only look at the first octal digit sequence
                }
                b = ' ';
            }
            unsignedSum += 0xff & b;
            signedSum += b;
        }

        return storedSum == unsignedSum || storedSum == signedSum
                || storedSum > unsignedSum; // COMPRESS-177
    }

}
