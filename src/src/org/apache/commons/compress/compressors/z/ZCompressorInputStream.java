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
package org.apache.commons.compress.compressors.z;

import java.io.IOException;
import java.io.InputStream;
import org.apache.commons.compress.compressors.z._internal_.InternalLZWInputStream;

/**
 * Input stream that decompresses .Z files.
 * @NotThreadSafe
 * @since 1.7
 */
public class ZCompressorInputStream extends InternalLZWInputStream {
    private static final int MAGIC_1 = 0x1f;
    private static final int MAGIC_2 = 0x9d;
    private static final int BLOCK_MODE_MASK = 0x80;
    private static final int MAX_CODE_SIZE_MASK = 0x1f;
    private final boolean blockMode;
    private final int maxCodeSize;
    private long totalCodesRead = 0;
    
    public ZCompressorInputStream(InputStream inputStream) throws IOException {
        super(inputStream);
        int firstByte = in.read();
        int secondByte = in.read();
        int thirdByte = in.read();
        if (firstByte != MAGIC_1 || secondByte != MAGIC_2 || thirdByte < 0) {
            throw new IOException("Input is not in .Z format");
        }
        blockMode = (thirdByte & BLOCK_MODE_MASK) != 0;
        maxCodeSize = thirdByte & MAX_CODE_SIZE_MASK;
        if (blockMode) {
            setClearCode(codeSize);
        }
        initializeTables(maxCodeSize);
        clearEntries();
    }
    
    private void clearEntries() {
        tableSize = 1 << 8;
        if (blockMode) {
            tableSize++;
        }
    }

    /**
     * {@inheritDoc}
     * <p><strong>This method is only protected for technical reasons
     * and is not part of Commons Compress' published API.  It may
     * change or disappear without warning.</strong></p>
     */
    @Override
    protected int readNextCode() throws IOException {
        int code = super.readNextCode();
        if (code >= 0) {
            ++totalCodesRead;
        }
        return code;
    }
    
    private void reAlignReading() throws IOException {
        // "compress" works in multiples of 8 symbols, each codeBits bits long.
        // When codeBits changes, the remaining unused symbols in the current
        // group of 8 are still written out, in the old codeSize,
        // as garbage values (usually zeroes) that need to be skipped.
        long codeReadsToThrowAway = 8 - (totalCodesRead % 8);
        if (codeReadsToThrowAway == 8) {
            codeReadsToThrowAway = 0;
        }
        for (long i = 0; i < codeReadsToThrowAway; i++) {
            readNextCode();
        }
        bitsCached = 0;
        bitsCachedSize = 0;
    }
    
    /**
     * {@inheritDoc}
     * <p><strong>This method is only protected for technical reasons
     * and is not part of Commons Compress' published API.  It may
     * change or disappear without warning.</strong></p>
     */
    @Override
    protected int addEntry(int previousCode, byte character) throws IOException {
        final int maxTableSize = 1 << codeSize;
        int r = addEntry(previousCode, character, maxTableSize);
        if (tableSize == maxTableSize && codeSize < maxCodeSize) {
            reAlignReading();
            codeSize++;
        }
        return r;
    }

    /**
     * {@inheritDoc}
     * <p><strong>This method is only protected for technical reasons
     * and is not part of Commons Compress' published API.  It may
     * change or disappear without warning.</strong></p>
     */
    @Override
    protected int decompressNextSymbol() throws IOException {
        //
        //                   table entry    table entry
        //                  _____________   _____
        //    table entry  /             \ /     \
        //    ____________/               \       \
        //   /           / \             / \       \
        //  +---+---+---+---+---+---+---+---+---+---+
        //  | . | . | . | . | . | . | . | . | . | . |
        //  +---+---+---+---+---+---+---+---+---+---+
        //  |<--------->|<------------->|<----->|<->|
        //     symbol        symbol      symbol  symbol
        //
        final int code = readNextCode();
        if (code < 0) {
            return -1;
        } else if (blockMode && code == clearCode) {
            clearEntries();
            reAlignReading();
            codeSize = 9;
            previousCode = -1;
            return 0;
        } else {
            boolean addedUnfinishedEntry = false;
            if (code == tableSize) {
                addRepeatOfPreviousCode();
                addedUnfinishedEntry = true;
            } else if (code > tableSize) {
                throw new IOException(String.format("Invalid %d bit code 0x%x", Integer.valueOf(codeSize), Integer.valueOf(code)));
            }
            return expandCodeToOutputStack(code, addedUnfinishedEntry);
        }
    }
    
}
