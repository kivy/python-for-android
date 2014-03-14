/*
 *  Licensed to the Apache Software Foundation (ASF) under one or more
 *  contributor license agreements.  See the NOTICE file distributed with
 *  this work for additional information regarding copyright ownership.
 *  The ASF licenses this file to You under the Apache License, Version 2.0
 *  (the "License"); you may not use this file except in compliance with
 *  the License.  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 */

/*
 * This package is based on the work done by Timothy Gerard Endres
 * (time@ice.com) to whom the Ant project is very grateful for his great code.
 */

package org.apache.commons.compress.archivers.tar;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

import org.apache.commons.compress.archivers.ArchiveEntry;
import org.apache.commons.compress.archivers.ArchiveInputStream;
import org.apache.commons.compress.archivers.zip.ZipEncoding;
import org.apache.commons.compress.archivers.zip.ZipEncodingHelper;
import org.apache.commons.compress.utils.ArchiveUtils;
import org.apache.commons.compress.utils.CharsetNames;
import org.apache.commons.compress.utils.IOUtils;

/**
 * The TarInputStream reads a UNIX tar archive as an InputStream.
 * methods are provided to position at each successive entry in
 * the archive, and the read each entry as a normal input stream
 * using read().
 * @NotThreadSafe
 */
public class TarArchiveInputStream extends ArchiveInputStream {

    private static final int SMALL_BUFFER_SIZE = 256;

    private final byte[] SMALL_BUF = new byte[SMALL_BUFFER_SIZE];

    /** The size the TAR header */
    private final int recordSize;

    /** The size of a block */
    private final int blockSize;

    /** True if file has hit EOF */
    private boolean hasHitEOF;

    /** Size of the current entry */
    private long entrySize;

    /** How far into the entry the stream is at */
    private long entryOffset;

    /** An input stream to read from */
    private final InputStream is;

    /** The meta-data about the current entry */
    private TarArchiveEntry currEntry;

    /** The encoding of the file */
    private final ZipEncoding encoding;

    /**
     * Constructor for TarInputStream.
     * @param is the input stream to use
     */
    public TarArchiveInputStream(InputStream is) {
        this(is, TarConstants.DEFAULT_BLKSIZE, TarConstants.DEFAULT_RCDSIZE);
    }

    /**
     * Constructor for TarInputStream.
     * @param is the input stream to use
     * @param encoding name of the encoding to use for file names
     * @since 1.4
     */
    public TarArchiveInputStream(InputStream is, String encoding) {
        this(is, TarConstants.DEFAULT_BLKSIZE, TarConstants.DEFAULT_RCDSIZE,
             encoding);
    }

    /**
     * Constructor for TarInputStream.
     * @param is the input stream to use
     * @param blockSize the block size to use
     */
    public TarArchiveInputStream(InputStream is, int blockSize) {
        this(is, blockSize, TarConstants.DEFAULT_RCDSIZE);
    }

    /**
     * Constructor for TarInputStream.
     * @param is the input stream to use
     * @param blockSize the block size to use
     * @param encoding name of the encoding to use for file names
     * @since 1.4
     */
    public TarArchiveInputStream(InputStream is, int blockSize,
                                 String encoding) {
        this(is, blockSize, TarConstants.DEFAULT_RCDSIZE, encoding);
    }

    /**
     * Constructor for TarInputStream.
     * @param is the input stream to use
     * @param blockSize the block size to use
     * @param recordSize the record size to use
     */
    public TarArchiveInputStream(InputStream is, int blockSize, int recordSize) {
        this(is, blockSize, recordSize, null);      
    }

    /**
     * Constructor for TarInputStream.
     * @param is the input stream to use
     * @param blockSize the block size to use
     * @param recordSize the record size to use
     * @param encoding name of the encoding to use for file names
     * @since 1.4
     */
    public TarArchiveInputStream(InputStream is, int blockSize, int recordSize,
                                 String encoding) {
        this.is = is;
        this.hasHitEOF = false;
        this.encoding = ZipEncodingHelper.getZipEncoding(encoding);
        this.recordSize = recordSize;
        this.blockSize = blockSize;
    }

    /**
     * Closes this stream. Calls the TarBuffer's close() method.
     * @throws IOException on error
     */
    @Override
    public void close() throws IOException {
        is.close();
    }

    /**
     * Get the record size being used by this stream's buffer.
     *
     * @return The TarBuffer record size.
     */
    public int getRecordSize() {
        return recordSize;
    }

    /**
     * Get the available data that can be read from the current
     * entry in the archive. This does not indicate how much data
     * is left in the entire archive, only in the current entry.
     * This value is determined from the entry's size header field
     * and the amount of data already read from the current entry.
     * Integer.MAX_VALUE is returned in case more than Integer.MAX_VALUE
     * bytes are left in the current entry in the archive.
     *
     * @return The number of available bytes for the current entry.
     * @throws IOException for signature
     */
    @Override
    public int available() throws IOException {
        if (entrySize - entryOffset > Integer.MAX_VALUE) {
            return Integer.MAX_VALUE;
        }
        return (int) (entrySize - entryOffset);
    }

    /**
     * Skip bytes in the input buffer. This skips bytes in the
     * current entry's data, not the entire archive, and will
     * stop at the end of the current entry's data if the number
     * to skip extends beyond that point.
     *
     * @param numToSkip The number of bytes to skip.
     * @return the number actually skipped
     * @throws IOException on error
     */
    @Override
    public long skip(long numToSkip) throws IOException {

        long available = entrySize - entryOffset;
        numToSkip = Math.min(numToSkip, available);

        long skipped = IOUtils.skip(is, numToSkip); 
        count(skipped);
        entryOffset += skipped;
        return skipped;
    }

    /**
     * Since we do not support marking just yet, we do nothing.
     */
    @Override
    public synchronized void reset() {
    }

    /**
     * Get the next entry in this tar archive. This will skip
     * over any remaining data in the current entry, if there
     * is one, and place the input stream at the header of the
     * next entry, and read the header and instantiate a new
     * TarEntry from the header bytes and return that entry.
     * If there are no more entries in the archive, null will
     * be returned to indicate that the end of the archive has
     * been reached.
     *
     * @return The next TarEntry in the archive, or null.
     * @throws IOException on error
     */
    public TarArchiveEntry getNextTarEntry() throws IOException {
        if (hasHitEOF) {
            return null;
        }

        if (currEntry != null) {
            /* Skip will only go to the end of the current entry */
            skip(Long.MAX_VALUE);

            /* skip to the end of the last record */
            skipRecordPadding();
        }

        byte[] headerBuf = getRecord();

        if (headerBuf == null) {
            /* hit EOF */
            currEntry = null;
            return null;
        }

        try {
            currEntry = new TarArchiveEntry(headerBuf, encoding);
        } catch (IllegalArgumentException e) {
            IOException ioe = new IOException("Error detected parsing the header");
            ioe.initCause(e);
            throw ioe;
        }

        entryOffset = 0;
        entrySize = currEntry.getSize();

        if (currEntry.isGNULongLinkEntry()) {
            byte[] longLinkData = getLongNameData();
            if (longLinkData == null) {
                // Bugzilla: 40334
                // Malformed tar file - long link entry name not followed by
                // entry
                return null;
            }
            currEntry.setLinkName(encoding.decode(longLinkData));
        }

        if (currEntry.isGNULongNameEntry()) {
            byte[] longNameData = getLongNameData();
            if (longNameData == null) {
                // Bugzilla: 40334
                // Malformed tar file - long entry name not followed by
                // entry
                return null;
            }
            currEntry.setName(encoding.decode(longNameData));
        }

        if (currEntry.isPaxHeader()){ // Process Pax headers
            paxHeaders();
        }

        if (currEntry.isGNUSparse()){ // Process sparse files
            readGNUSparse();
        }

        // If the size of the next element in the archive has changed
        // due to a new size being reported in the posix header
        // information, we update entrySize here so that it contains
        // the correct value.
        entrySize = currEntry.getSize();

        return currEntry;
    }
    
    /**
     * The last record block should be written at the full size, so skip any
     * additional space used to fill a record after an entry
     */
    private void skipRecordPadding() throws IOException {
        if (this.entrySize > 0 && this.entrySize % this.recordSize != 0) {
            long numRecords = (this.entrySize / this.recordSize) + 1;
            long padding = (numRecords * this.recordSize) - this.entrySize;
            long skipped = IOUtils.skip(is, padding);
            count(skipped);
        }
    }

    /**
     * Get the next entry in this tar archive as longname data.
     *
     * @return The next entry in the archive as longname data, or null.
     * @throws IOException on error
     */
    protected byte[] getLongNameData() throws IOException {
        // read in the name
        ByteArrayOutputStream longName = new ByteArrayOutputStream();
        int length = 0;
        while ((length = read(SMALL_BUF)) >= 0) {
            longName.write(SMALL_BUF, 0, length);
        }
        getNextEntry();
        if (currEntry == null) {
            // Bugzilla: 40334
            // Malformed tar file - long entry name not followed by entry
            return null;
        }
        byte[] longNameData = longName.toByteArray();
        // remove trailing null terminator(s)
        length = longNameData.length;
        while (length > 0 && longNameData[length - 1] == 0) {
            --length;
        }
        if (length != longNameData.length) {
            byte[] l = new byte[length];
            System.arraycopy(longNameData, 0, l, 0, length);
            longNameData = l;
        }
        return longNameData;
    }

    /**
     * Get the next record in this tar archive. This will skip
     * over any remaining data in the current entry, if there
     * is one, and place the input stream at the header of the
     * next entry.
     *
     * <p>If there are no more entries in the archive, null will be
     * returned to indicate that the end of the archive has been
     * reached.  At the same time the {@code hasHitEOF} marker will be
     * set to true.</p>
     *
     * @return The next header in the archive, or null.
     * @throws IOException on error
     */
    private byte[] getRecord() throws IOException {
        byte[] headerBuf = readRecord();
        hasHitEOF = isEOFRecord(headerBuf);
        if (hasHitEOF && headerBuf != null) {
            tryToConsumeSecondEOFRecord();
            consumeRemainderOfLastBlock();
            headerBuf = null;
        }
        return headerBuf;
    }

    /**
     * Determine if an archive record indicate End of Archive. End of
     * archive is indicated by a record that consists entirely of null bytes.
     *
     * @param record The record data to check.
     * @return true if the record data is an End of Archive
     */
    protected boolean isEOFRecord(byte[] record) {
        return record == null || ArchiveUtils.isArrayZero(record, recordSize);
    }
    
    /**
     * Read a record from the input stream and return the data.
     *
     * @return The record data or null if EOF has been hit.
     * @throws IOException on error
     */
    protected byte[] readRecord() throws IOException {

        byte[] record = new byte[recordSize];

        int readNow = IOUtils.readFully(is, record);
        count(readNow);
        if (readNow != recordSize) {
            return null;
        }

        return record;
    }

    private void paxHeaders() throws IOException{
        Map<String, String> headers = parsePaxHeaders(this);
        getNextEntry(); // Get the actual file entry
        applyPaxHeadersToCurrentEntry(headers);
    }

    Map<String, String> parsePaxHeaders(InputStream i) throws IOException {
        Map<String, String> headers = new HashMap<String, String>();
        // Format is "length keyword=value\n";
        while(true){ // get length
            int ch;
            int len = 0;
            int read = 0;
            while((ch = i.read()) != -1) {
                read++;
                if (ch == ' '){ // End of length string
                    // Get keyword
                    ByteArrayOutputStream coll = new ByteArrayOutputStream();
                    while((ch = i.read()) != -1) {
                        read++;
                        if (ch == '='){ // end of keyword
                            String keyword = coll.toString(CharsetNames.UTF_8);
                            // Get rest of entry
                            byte[] rest = new byte[len - read];
                            int got = i.read(rest);
                            if (got != len - read){
                                throw new IOException("Failed to read "
                                                      + "Paxheader. Expected "
                                                      + (len - read)
                                                      + " bytes, read "
                                                      + got);
                            }
                            // Drop trailing NL
                            String value = new String(rest, 0,
                                                      len - read - 1, CharsetNames.UTF_8);
                            headers.put(keyword, value);
                            break;
                        }
                        coll.write((byte) ch);
                    }
                    break; // Processed single header
                }
                len *= 10;
                len += ch - '0';
            }
            if (ch == -1){ // EOF
                break;
            }
        }
        return headers;
    }

    private void applyPaxHeadersToCurrentEntry(Map<String, String> headers) {
        /*
         * The following headers are defined for Pax.
         * atime, ctime, charset: cannot use these without changing TarArchiveEntry fields
         * mtime
         * comment
         * gid, gname
         * linkpath
         * size
         * uid,uname
         * SCHILY.devminor, SCHILY.devmajor: don't have setters/getters for those
         */
        for (Entry<String, String> ent : headers.entrySet()){
            String key = ent.getKey();
            String val = ent.getValue();
            if ("path".equals(key)){
                currEntry.setName(val);
            } else if ("linkpath".equals(key)){
                currEntry.setLinkName(val);
            } else if ("gid".equals(key)){
                currEntry.setGroupId(Integer.parseInt(val));
            } else if ("gname".equals(key)){
                currEntry.setGroupName(val);
            } else if ("uid".equals(key)){
                currEntry.setUserId(Integer.parseInt(val));
            } else if ("uname".equals(key)){
                currEntry.setUserName(val);
            } else if ("size".equals(key)){
                currEntry.setSize(Long.parseLong(val));
            } else if ("mtime".equals(key)){
                currEntry.setModTime((long) (Double.parseDouble(val) * 1000));
            } else if ("SCHILY.devminor".equals(key)){
                currEntry.setDevMinor(Integer.parseInt(val));
            } else if ("SCHILY.devmajor".equals(key)){
                currEntry.setDevMajor(Integer.parseInt(val));
            }
        }
    }

    /**
     * Adds the sparse chunks from the current entry to the sparse chunks,
     * including any additional sparse entries following the current entry.
     *
     * @throws IOException on error
     *
     * @todo Sparse files get not yet really processed.
     */
    private void readGNUSparse() throws IOException {
        /* we do not really process sparse files yet
        sparses = new ArrayList();
        sparses.addAll(currEntry.getSparses());
        */
        if (currEntry.isExtended()) {
            TarArchiveSparseEntry entry;
            do {
                byte[] headerBuf = getRecord();
                if (headerBuf == null) {
                    currEntry = null;
                    break;
                }
                entry = new TarArchiveSparseEntry(headerBuf);
                /* we do not really process sparse files yet
                sparses.addAll(entry.getSparses());
                */
            } while (entry.isExtended());
        }
    }

    /**
     * Returns the next Archive Entry in this Stream.
     *
     * @return the next entry,
     *         or {@code null} if there are no more entries
     * @throws IOException if the next entry could not be read
     */
    @Override
    public ArchiveEntry getNextEntry() throws IOException {
        return getNextTarEntry();
    }
    
    /**
     * Tries to read the next record rewinding the stream if it is not a EOF record.
     *
     * <p>This is meant to protect against cases where a tar
     * implementation has written only one EOF record when two are
     * expected.  Actually this won't help since a non-conforming
     * implementation likely won't fill full blocks consisting of - by
     * default - ten records either so we probably have already read
     * beyond the archive anyway.</p>
     */
    private void tryToConsumeSecondEOFRecord() throws IOException {
        boolean shouldReset = true;
        boolean marked = is.markSupported();
        if (marked) {
            is.mark(recordSize);
        }
        try {
            shouldReset = !isEOFRecord(readRecord());
        } finally {
            if (shouldReset && marked) {
                pushedBackBytes(recordSize);
            	is.reset();
            }
        }
    }

    /**
     * Reads bytes from the current tar archive entry.
     *
     * This method is aware of the boundaries of the current
     * entry in the archive and will deal with them as if they
     * were this stream's start and EOF.
     *
     * @param buf The buffer into which to place bytes read.
     * @param offset The offset at which to place bytes read.
     * @param numToRead The number of bytes to read.
     * @return The number of bytes read, or -1 at EOF.
     * @throws IOException on error
     */
    @Override
    public int read(byte[] buf, int offset, int numToRead) throws IOException {
    	int totalRead = 0;

        if (hasHitEOF || entryOffset >= entrySize) {
            return -1;
        }

        numToRead = Math.min(numToRead, available());
        
        totalRead = is.read(buf, offset, numToRead);
        count(totalRead);
        
        if (totalRead == -1) {
            hasHitEOF = true;
        } else {
            entryOffset += totalRead;
        }

        return totalRead;
    }

    /**
     * Whether this class is able to read the given entry.
     *
     * <p>May return false if the current entry is a sparse file.</p>
     */
    @Override
    public boolean canReadEntryData(ArchiveEntry ae) {
        if (ae instanceof TarArchiveEntry) {
            TarArchiveEntry te = (TarArchiveEntry) ae;
            return !te.isGNUSparse();
        }
        return false;
    }

    /**
     * Get the current TAR Archive Entry that this input stream is processing
     * 
     * @return The current Archive Entry
     */
    public TarArchiveEntry getCurrentEntry() {
        return currEntry;
    }

    protected final void setCurrentEntry(TarArchiveEntry e) {
        currEntry = e;
    }

    protected final boolean isAtEOF() {
        return hasHitEOF;
    }

    protected final void setAtEOF(boolean b) {
        hasHitEOF = b;
    }

    /**
     * This method is invoked once the end of the archive is hit, it
     * tries to consume the remaining bytes under the assumption that
     * the tool creating this archive has padded the last block.
     */
    private void consumeRemainderOfLastBlock() throws IOException {
        long bytesReadOfLastBlock = getBytesRead() % blockSize;
        if (bytesReadOfLastBlock > 0) {
            long skipped = IOUtils.skip(is, blockSize - bytesReadOfLastBlock);
            count(skipped);
        }
    }

    /**
     * Checks if the signature matches what is expected for a tar file.
     *
     * @param signature
     *            the bytes to check
     * @param length
     *            the number of bytes to check
     * @return true, if this stream is a tar archive stream, false otherwise
     */
    public static boolean matches(byte[] signature, int length) {
        if (length < TarConstants.VERSION_OFFSET+TarConstants.VERSIONLEN) {
            return false;
        }

        if (ArchiveUtils.matchAsciiBuffer(TarConstants.MAGIC_POSIX,
                signature, TarConstants.MAGIC_OFFSET, TarConstants.MAGICLEN)
            &&
            ArchiveUtils.matchAsciiBuffer(TarConstants.VERSION_POSIX,
                signature, TarConstants.VERSION_OFFSET, TarConstants.VERSIONLEN)
                ){
            return true;
        }
        if (ArchiveUtils.matchAsciiBuffer(TarConstants.MAGIC_GNU,
                signature, TarConstants.MAGIC_OFFSET, TarConstants.MAGICLEN)
            &&
            (
             ArchiveUtils.matchAsciiBuffer(TarConstants.VERSION_GNU_SPACE,
                signature, TarConstants.VERSION_OFFSET, TarConstants.VERSIONLEN)
            ||
            ArchiveUtils.matchAsciiBuffer(TarConstants.VERSION_GNU_ZERO,
                signature, TarConstants.VERSION_OFFSET, TarConstants.VERSIONLEN)
            )
                ){
            return true;
        }
        // COMPRESS-107 - recognise Ant tar files
        if (ArchiveUtils.matchAsciiBuffer(TarConstants.MAGIC_ANT,
                signature, TarConstants.MAGIC_OFFSET, TarConstants.MAGICLEN)
            &&
            ArchiveUtils.matchAsciiBuffer(TarConstants.VERSION_ANT,
                signature, TarConstants.VERSION_OFFSET, TarConstants.VERSIONLEN)
                ){
            return true;
        }
        return false;
    }

}
