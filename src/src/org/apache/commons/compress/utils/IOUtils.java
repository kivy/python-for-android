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
package org.apache.commons.compress.utils;

import java.io.ByteArrayOutputStream;
import java.io.Closeable;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

/**
 * Utility functions
 * @Immutable
 */
public final class IOUtils {

    /** Private constructor to prevent instantiation of this utility class. */
    private IOUtils(){
    }

    /**
     * Copies the content of a InputStream into an OutputStream.
     * Uses a default buffer size of 8024 bytes.
     *
     * @param input
     *            the InputStream to copy
     * @param output
     *            the target Stream
     * @throws IOException
     *             if an error occurs
     */
    public static long copy(final InputStream input, final OutputStream output) throws IOException {
        return copy(input, output, 8024);
    }

    /**
     * Copies the content of a InputStream into an OutputStream
     *
     * @param input
     *            the InputStream to copy
     * @param output
     *            the target Stream
     * @param buffersize
     *            the buffer size to use
     * @throws IOException
     *             if an error occurs
     */
    public static long copy(final InputStream input, final OutputStream output, int buffersize) throws IOException {
        final byte[] buffer = new byte[buffersize];
        int n = 0;
        long count=0;
        while (-1 != (n = input.read(buffer))) {
            output.write(buffer, 0, n);
            count += n;
        }
        return count;
    }
    
    /**
     * Skips the given number of bytes by repeatedly invoking skip on
     * the given input stream if necessary.
     *
     * <p>This method will only skip less than the requested number of
     * bytes if the end of the input stream has been reached.</p>
     *
     * @param input stream to skip bytes in
     * @param numToSkip the number of bytes to skip
     * @return the number of bytes actually skipped
     * @throws IOException
     */
    public static long skip(InputStream input, long numToSkip) throws IOException {
        long available = numToSkip;
        while (numToSkip > 0) {
            long skipped = input.skip(numToSkip);
            if (skipped == 0) {
                break;
            }
            numToSkip -= skipped;
        }
        return available - numToSkip;
    }

    /**
     * Reads as much from input as possible to fill the given array.
     *
     * <p>This method may invoke read repeatedly to fill the array and
     * only read less bytes than the length of the array if the end of
     * the stream has been reached.</p>
     *
     * @param input stream to read from
     * @param b buffer to fill
     * @return the number of bytes actually read
     * @throws IOException
     */
    public static int readFully(InputStream input, byte[] b) throws IOException {
        return readFully(input, b, 0, b.length);
    }

    /**
     * Reads as much from input as possible to fill the given array
     * with the given amount of bytes.
     *
     * <p>This method may invoke read repeatedly to read the bytes and
     * only read less bytes than the requested length if the end of
     * the stream has been reached.</p>
     *
     * @param input stream to read from
     * @param b buffer to fill
     * @param offset offset into the buffer to start filling at
     * @param len of bytes to read
     * @return the number of bytes actually read
     * @throws IOException
     *             if an I/O error has occurred
     */
    public static int readFully(InputStream input, byte[] b, int offset, int len)
        throws IOException {
        if (len < 0 || offset < 0 || len + offset > b.length) {
            throw new IndexOutOfBoundsException();
        }
        int count = 0, x = 0;
        while (count != len) {
            x = input.read(b, offset + count, len - count);
            if (x == -1) {
                break;
            }
            count += x;
        }
        return count;
    }

    // toByteArray(InputStream) copied from:
    // commons/proper/io/trunk/src/main/java/org/apache/commons/io/IOUtils.java?revision=1428941
    // January 8th, 2013
    //
    // Assuming our copy() works just as well as theirs!  :-)

    /**
     * Gets the contents of an <code>InputStream</code> as a <code>byte[]</code>.
     * <p>
     * This method buffers the input internally, so there is no need to use a
     * <code>BufferedInputStream</code>.
     *
     * @param input  the <code>InputStream</code> to read from
     * @return the requested byte array
     * @throws NullPointerException if the input is null
     * @throws IOException if an I/O error occurs
     * @since 1.5
     */
    public static byte[] toByteArray(final InputStream input) throws IOException {
        final ByteArrayOutputStream output = new ByteArrayOutputStream();
        copy(input, output);
        return output.toByteArray();
    }

    /**
     * Closes the given Closeable and swallows any IOException that may occur.
     * @param c Closeable to close, can be null
     * @since 1.7
     */
    public static void closeQuietly(Closeable c) {
        if (c != null) {
            try {
                c.close();
            } catch (IOException ignored) { // NOPMD
            }
        }
    }
}
