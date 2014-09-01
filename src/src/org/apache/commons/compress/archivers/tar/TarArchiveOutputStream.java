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

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.io.StringWriter;
import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.compress.archivers.ArchiveEntry;
import org.apache.commons.compress.archivers.ArchiveOutputStream;
import org.apache.commons.compress.archivers.zip.ZipEncoding;
import org.apache.commons.compress.archivers.zip.ZipEncodingHelper;
import org.apache.commons.compress.utils.CharsetNames;
import org.apache.commons.compress.utils.CountingOutputStream;

/**
 * The TarOutputStream writes a UNIX tar archive as an OutputStream.
 * Methods are provided to put entries, and then write their contents
 * by writing to this stream using write().
 * @NotThreadSafe
 */
public class TarArchiveOutputStream extends ArchiveOutputStream {
    /** Fail if a long file name is required in the archive. */
    public static final int LONGFILE_ERROR = 0;

    /** Long paths will be truncated in the archive. */
    public static final int LONGFILE_TRUNCATE = 1;

    /** GNU tar extensions are used to store long file names in the archive. */
    public static final int LONGFILE_GNU = 2;

    /** POSIX/PAX extensions are used to store long file names in the archive. */
    public static final int LONGFILE_POSIX = 3;

    /** Fail if a big number (e.g. size &gt; 8GiB) is required in the archive. */
    public static final int BIGNUMBER_ERROR = 0;

    /** star/GNU tar/BSD tar extensions are used to store big number in the archive. */
    public static final int BIGNUMBER_STAR = 1;

    /** POSIX/PAX extensions are used to store big numbers in the archive. */
    public static final int BIGNUMBER_POSIX = 2;

    private long      currSize;
    private String    currName;
    private long      currBytes;
    private final byte[]    recordBuf;
    private int       assemLen;
    private final byte[]    assemBuf;
    private int       longFileMode = LONGFILE_ERROR;
    private int       bigNumberMode = BIGNUMBER_ERROR;
    private int recordsWritten;
    private final int recordsPerBlock;
    private final int recordSize;

    private boolean closed = false;

    /** Indicates if putArchiveEntry has been called without closeArchiveEntry */
    private boolean haveUnclosedEntry = false;

    /** indicates if this archive is finished */
    private boolean finished = false;

    private final OutputStream out;

    private final ZipEncoding encoding;

    private boolean addPaxHeadersForNonAsciiNames = false;
    private static final ZipEncoding ASCII =
        ZipEncodingHelper.getZipEncoding("ASCII");

    /**
     * Constructor for TarInputStream.
     * @param os the output stream to use
     */
    public TarArchiveOutputStream(OutputStream os) {
        this(os, TarConstants.DEFAULT_BLKSIZE, TarConstants.DEFAULT_RCDSIZE);
    }

    /**
     * Constructor for TarInputStream.
     * @param os the output stream to use
     * @param encoding name of the encoding to use for file names
     * @since 1.4
     */
    public TarArchiveOutputStream(OutputStream os, String encoding) {
        this(os, TarConstants.DEFAULT_BLKSIZE, TarConstants.DEFAULT_RCDSIZE, encoding);
    }

    /**
     * Constructor for TarInputStream.
     * @param os the output stream to use
     * @param blockSize the block size to use
     */
    public TarArchiveOutputStream(OutputStream os, int blockSize) {
        this(os, blockSize, TarConstants.DEFAULT_RCDSIZE);
    }

    /**
     * Constructor for TarInputStream.
     * @param os the output stream to use
     * @param blockSize the block size to use
     * @param encoding name of the encoding to use for file names
     * @since 1.4
     */
    public TarArchiveOutputStream(OutputStream os, int blockSize,
                                  String encoding) {
        this(os, blockSize, TarConstants.DEFAULT_RCDSIZE, encoding);
    }

    /**
     * Constructor for TarInputStream.
     * @param os the output stream to use
     * @param blockSize the block size to use
     * @param recordSize the record size to use
     */
    public TarArchiveOutputStream(OutputStream os, int blockSize, int recordSize) {
        this(os, blockSize, recordSize, null);
    }

    /**
     * Constructor for TarInputStream.
     * @param os the output stream to use
     * @param blockSize the block size to use
     * @param recordSize the record size to use
     * @param encoding name of the encoding to use for file names
     * @since 1.4
     */
    public TarArchiveOutputStream(OutputStream os, int blockSize,
                                  int recordSize, String encoding) {
        out = new CountingOutputStream(os);
        this.encoding = ZipEncodingHelper.getZipEncoding(encoding);

        this.assemLen = 0;
        this.assemBuf = new byte[recordSize];
        this.recordBuf = new byte[recordSize];
        this.recordSize = recordSize;
        this.recordsPerBlock = blockSize / recordSize;
    }

    /**
     * Set the long file mode.
     * This can be LONGFILE_ERROR(0), LONGFILE_TRUNCATE(1) or LONGFILE_GNU(2).
     * This specifies the treatment of long file names (names &gt;= TarConstants.NAMELEN).
     * Default is LONGFILE_ERROR.
     * @param longFileMode the mode to use
     */
    public void setLongFileMode(int longFileMode) {
        this.longFileMode = longFileMode;
    }

    /**
     * Set the big number mode.
     * This can be BIGNUMBER_ERROR(0), BIGNUMBER_POSIX(1) or BIGNUMBER_STAR(2).
     * This specifies the treatment of big files (sizes &gt; TarConstants.MAXSIZE) and other numeric values to big to fit into a traditional tar header.
     * Default is BIGNUMBER_ERROR.
     * @param bigNumberMode the mode to use
     * @since 1.4
     */
    public void setBigNumberMode(int bigNumberMode) {
        this.bigNumberMode = bigNumberMode;
    }

    /**
     * Whether to add a PAX extension header for non-ASCII file names.
     * @since 1.4
     */
    public void setAddPaxHeadersForNonAsciiNames(boolean b) {
        addPaxHeadersForNonAsciiNames = b;
    }

    @Deprecated
    @Override
    public int getCount() {
        return (int) getBytesWritten();
    }

    @Override
    public long getBytesWritten() {
        return ((CountingOutputStream) out).getBytesWritten();
    }

    /**
     * Ends the TAR archive without closing the underlying OutputStream.
     * 
     * An archive consists of a series of file entries terminated by an
     * end-of-archive entry, which consists of two 512 blocks of zero bytes. 
     * POSIX.1 requires two EOF records, like some other implementations.
     * 
     * @throws IOException on error
     */
    @Override
    public void finish() throws IOException {
        if (finished) {
            throw new IOException("This archive has already been finished");
        }

        if (haveUnclosedEntry) {
            throw new IOException("This archives contains unclosed entries.");
        }
        writeEOFRecord();
        writeEOFRecord();
        padAsNeeded();
        out.flush();
        finished = true;
    }

    /**
     * Closes the underlying OutputStream.
     * @throws IOException on error
     */
    @Override
    public void close() throws IOException {
        if (!finished) {
            finish();
        }

        if (!closed) {
            out.close();
            closed = true;
        }
    }

    /**
     * Get the record size being used by this stream's TarBuffer.
     *
     * @return The TarBuffer record size.
     */
    public int getRecordSize() {
        return this.recordSize;
    }

    /**
     * Put an entry on the output stream. This writes the entry's
     * header record and positions the output stream for writing
     * the contents of the entry. Once this method is called, the
     * stream is ready for calls to write() to write the entry's
     * contents. Once the contents are written, closeArchiveEntry()
     * <B>MUST</B> be called to ensure that all buffered data
     * is completely written to the output stream.
     *
     * @param archiveEntry The TarEntry to be written to the archive.
     * @throws IOException on error
     * @throws ClassCastException if archiveEntry is not an instance of TarArchiveEntry
     */
    @Override
    public void putArchiveEntry(ArchiveEntry archiveEntry) throws IOException {
        if(finished) {
            throw new IOException("Stream has already been finished");
        }
        TarArchiveEntry entry = (TarArchiveEntry) archiveEntry;
        Map<String, String> paxHeaders = new HashMap<String, String>();
        final String entryName = entry.getName();
        boolean paxHeaderContainsPath = handleLongName(entryName, paxHeaders, "path",
                                                       TarConstants.LF_GNUTYPE_LONGNAME, "file name");

        final String linkName = entry.getLinkName();
        boolean paxHeaderContainsLinkPath = linkName != null && linkName.length() > 0
            && handleLongName(linkName, paxHeaders, "linkpath",
                              TarConstants.LF_GNUTYPE_LONGLINK, "link name");

        if (bigNumberMode == BIGNUMBER_POSIX) {
            addPaxHeadersForBigNumbers(paxHeaders, entry);
        } else if (bigNumberMode != BIGNUMBER_STAR) {
            failForBigNumbers(entry);
        }

        if (addPaxHeadersForNonAsciiNames && !paxHeaderContainsPath
            && !ASCII.canEncode(entryName)) {
            paxHeaders.put("path", entryName);
        }

        if (addPaxHeadersForNonAsciiNames && !paxHeaderContainsLinkPath
            && (entry.isLink() || entry.isSymbolicLink())
            && !ASCII.canEncode(linkName)) {
            paxHeaders.put("linkpath", linkName);
        }

        if (paxHeaders.size() > 0) {
            writePaxHeaders(entryName, paxHeaders);
        }

        entry.writeEntryHeader(recordBuf, encoding,
                               bigNumberMode == BIGNUMBER_STAR);
        writeRecord(recordBuf);

        currBytes = 0;

        if (entry.isDirectory()) {
            currSize = 0;
        } else {
            currSize = entry.getSize();
        }
        currName = entryName;
        haveUnclosedEntry = true;
    }

    /**
     * Close an entry. This method MUST be called for all file
     * entries that contain data. The reason is that we must
     * buffer data written to the stream in order to satisfy
     * the buffer's record based writes. Thus, there may be
     * data fragments still being assembled that must be written
     * to the output stream before this entry is closed and the
     * next entry written.
     * @throws IOException on error
     */
    @Override
    public void closeArchiveEntry() throws IOException {
        if (finished) {
            throw new IOException("Stream has already been finished");
        }
        if (!haveUnclosedEntry){
            throw new IOException("No current entry to close");
        }
        if (assemLen > 0) {
            for (int i = assemLen; i < assemBuf.length; ++i) {
                assemBuf[i] = 0;
            }

            writeRecord(assemBuf);

            currBytes += assemLen;
            assemLen = 0;
        }

        if (currBytes < currSize) {
            throw new IOException("entry '" + currName + "' closed at '"
                                  + currBytes
                                  + "' before the '" + currSize
                                  + "' bytes specified in the header were written");
        }
        haveUnclosedEntry = false;
    }

    /**
     * Writes bytes to the current tar archive entry. This method
     * is aware of the current entry and will throw an exception if
     * you attempt to write bytes past the length specified for the
     * current entry. The method is also (painfully) aware of the
     * record buffering required by TarBuffer, and manages buffers
     * that are not a multiple of recordsize in length, including
     * assembling records from small buffers.
     *
     * @param wBuf The buffer to write to the archive.
     * @param wOffset The offset in the buffer from which to get bytes.
     * @param numToWrite The number of bytes to write.
     * @throws IOException on error
     */
    @Override
    public void write(byte[] wBuf, int wOffset, int numToWrite) throws IOException {
        if (currBytes + numToWrite > currSize) {
            throw new IOException("request to write '" + numToWrite
                                  + "' bytes exceeds size in header of '"
                                  + currSize + "' bytes for entry '"
                                  + currName + "'");

            //
            // We have to deal with assembly!!!
            // The programmer can be writing little 32 byte chunks for all
            // we know, and we must assemble complete records for writing.
            // REVIEW Maybe this should be in TarBuffer? Could that help to
            // eliminate some of the buffer copying.
            //
        }

        if (assemLen > 0) {
            if (assemLen + numToWrite >= recordBuf.length) {
                int aLen = recordBuf.length - assemLen;

                System.arraycopy(assemBuf, 0, recordBuf, 0,
                                 assemLen);
                System.arraycopy(wBuf, wOffset, recordBuf,
                                 assemLen, aLen);
                writeRecord(recordBuf);

                currBytes += recordBuf.length;
                wOffset += aLen;
                numToWrite -= aLen;
                assemLen = 0;
            } else {
                System.arraycopy(wBuf, wOffset, assemBuf, assemLen,
                                 numToWrite);

                wOffset += numToWrite;
                assemLen += numToWrite;
                numToWrite = 0;
            }
        }

        //
        // When we get here we have EITHER:
        // o An empty "assemble" buffer.
        // o No bytes to write (numToWrite == 0)
        //
        while (numToWrite > 0) {
            if (numToWrite < recordBuf.length) {
                System.arraycopy(wBuf, wOffset, assemBuf, assemLen,
                                 numToWrite);

                assemLen += numToWrite;

                break;
            }

            writeRecord(wBuf, wOffset);

            int num = recordBuf.length;

            currBytes += num;
            numToWrite -= num;
            wOffset += num;
        }
    }

    /**
     * Writes a PAX extended header with the given map as contents.
     * @since 1.4
     */
    void writePaxHeaders(String entryName,
                         Map<String, String> headers) throws IOException {
        String name = "./PaxHeaders.X/" + stripTo7Bits(entryName);
        if (name.length() >= TarConstants.NAMELEN) {
            name = name.substring(0, TarConstants.NAMELEN - 1);
        }
        while (name.endsWith("/")) {
            // TarEntry's constructor would think this is a directory
            // and not allow any data to be written
            name = name.substring(0, name.length() - 1);
        }
        TarArchiveEntry pex = new TarArchiveEntry(name,
                                                  TarConstants.LF_PAX_EXTENDED_HEADER_LC);

        StringWriter w = new StringWriter();
        for (Map.Entry<String, String> h : headers.entrySet()) {
            String key = h.getKey();
            String value = h.getValue();
            int len = key.length() + value.length()
                + 3 /* blank, equals and newline */
                + 2 /* guess 9 < actual length < 100 */;
            String line = len + " " + key + "=" + value + "\n";
            int actualLength = line.getBytes(CharsetNames.UTF_8).length;
            while (len != actualLength) {
                // Adjust for cases where length < 10 or > 100
                // or where UTF-8 encoding isn't a single octet
                // per character.
                // Must be in loop as size may go from 99 to 100 in
                // first pass so we'd need a second.
                len = actualLength;
                line = len + " " + key + "=" + value + "\n";
                actualLength = line.getBytes(CharsetNames.UTF_8).length;
            }
            w.write(line);
        }
        byte[] data = w.toString().getBytes(CharsetNames.UTF_8);
        pex.setSize(data.length);
        putArchiveEntry(pex);
        write(data);
        closeArchiveEntry();
    }

    private String stripTo7Bits(String name) {
        final int length = name.length();
        StringBuilder result = new StringBuilder(length);
        for (int i = 0; i < length; i++) {
            char stripped = (char) (name.charAt(i) & 0x7F);
            if (stripped != 0) { // would be read as Trailing null
                result.append(stripped);
            }
        }
        return result.toString();
    }

    /**
     * Write an EOF (end of archive) record to the tar archive.
     * An EOF record consists of a record of all zeros.
     */
    private void writeEOFRecord() throws IOException {
        Arrays.fill(recordBuf, (byte) 0);
        writeRecord(recordBuf);
    }

    @Override
    public void flush() throws IOException {
        out.flush();
    }

    @Override
    public ArchiveEntry createArchiveEntry(File inputFile, String entryName)
            throws IOException {
        if(finished) {
            throw new IOException("Stream has already been finished");
        }
        return new TarArchiveEntry(inputFile, entryName);
    }
    
    /**
     * Write an archive record to the archive.
     *
     * @param record The record data to write to the archive.
     * @throws IOException on error
     */
    private void writeRecord(byte[] record) throws IOException {
        if (record.length != recordSize) {
            throw new IOException("record to write has length '"
                                  + record.length
                                  + "' which is not the record size of '"
                                  + recordSize + "'");
        }

        out.write(record);
        recordsWritten++;
    }
    
    /**
     * Write an archive record to the archive, where the record may be
     * inside of a larger array buffer. The buffer must be "offset plus
     * record size" long.
     *
     * @param buf The buffer containing the record data to write.
     * @param offset The offset of the record data within buf.
     * @throws IOException on error
     */
    private void writeRecord(byte[] buf, int offset) throws IOException {
 
        if (offset + recordSize > buf.length) {
            throw new IOException("record has length '" + buf.length
                                  + "' with offset '" + offset
                                  + "' which is less than the record size of '"
                                  + recordSize + "'");
        }

        out.write(buf, offset, recordSize);
        recordsWritten++;
    }

    private void padAsNeeded() throws IOException {
        int start = recordsWritten % recordsPerBlock;
        if (start != 0) {
            for (int i = start; i < recordsPerBlock; i++) {
                writeEOFRecord();
            }
        }
    }

    private void addPaxHeadersForBigNumbers(Map<String, String> paxHeaders,
                                            TarArchiveEntry entry) {
        addPaxHeaderForBigNumber(paxHeaders, "size", entry.getSize(),
                                 TarConstants.MAXSIZE);
        addPaxHeaderForBigNumber(paxHeaders, "gid", entry.getGroupId(),
                                 TarConstants.MAXID);
        addPaxHeaderForBigNumber(paxHeaders, "mtime",
                                 entry.getModTime().getTime() / 1000,
                                 TarConstants.MAXSIZE);
        addPaxHeaderForBigNumber(paxHeaders, "uid", entry.getUserId(),
                                 TarConstants.MAXID);
        // star extensions by J\u00f6rg Schilling
        addPaxHeaderForBigNumber(paxHeaders, "SCHILY.devmajor",
                                 entry.getDevMajor(), TarConstants.MAXID);
        addPaxHeaderForBigNumber(paxHeaders, "SCHILY.devminor",
                                 entry.getDevMinor(), TarConstants.MAXID);
        // there is no PAX header for file mode
        failForBigNumber("mode", entry.getMode(), TarConstants.MAXID);
    }

    private void addPaxHeaderForBigNumber(Map<String, String> paxHeaders,
                                          String header, long value,
                                          long maxValue) {
        if (value < 0 || value > maxValue) {
            paxHeaders.put(header, String.valueOf(value));
        }
    }

    private void failForBigNumbers(TarArchiveEntry entry) {
        failForBigNumber("entry size", entry.getSize(), TarConstants.MAXSIZE);
        failForBigNumber("group id", entry.getGroupId(), TarConstants.MAXID);
        failForBigNumber("last modification time",
                         entry.getModTime().getTime() / 1000,
                         TarConstants.MAXSIZE);
        failForBigNumber("user id", entry.getUserId(), TarConstants.MAXID);
        failForBigNumber("mode", entry.getMode(), TarConstants.MAXID);
        failForBigNumber("major device number", entry.getDevMajor(),
                         TarConstants.MAXID);
        failForBigNumber("minor device number", entry.getDevMinor(),
                         TarConstants.MAXID);
    }

    private void failForBigNumber(String field, long value, long maxValue) {
        if (value < 0 || value > maxValue) {
            throw new RuntimeException(field + " '" + value
                                       + "' is too big ( > "
                                       + maxValue + " )");
        }
    }

    /**
     * Handles long file or link names according to the longFileMode setting.
     *
     * <p>I.e. if the given name is too long to be written to a plain
     * tar header then
     * <ul>
     *   <li>it creates a pax header who's name is given by the
     *   paxHeaderName parameter if longFileMode is POSIX</li>
     *   <li>it creates a GNU longlink entry who's type is given by
     *   the linkType parameter if longFileMode is GNU</li>
     *   <li>it throws an exception if longFileMode is ERROR</li>
     *   <li>it truncates the name if longFileMode is TRUNCATE</li>
     * </ul></p>
     *
     * @param name the name to write
     * @param paxHeaders current map of pax headers
     * @param paxHeaderName name of the pax header to write
     * @param linkType type of the GNU entry to write
     * @param fieldName the name of the field
     * @return whether a pax header has been written.
     */
    private boolean handleLongName(String name,
                                   Map<String, String> paxHeaders,
                                   String paxHeaderName, byte linkType, String fieldName)
        throws IOException {
        final ByteBuffer encodedName = encoding.encode(name);
        final int len = encodedName.limit() - encodedName.position();
        if (len >= TarConstants.NAMELEN) {

            if (longFileMode == LONGFILE_POSIX) {
                paxHeaders.put(paxHeaderName, name);
                return true;
            } else if (longFileMode == LONGFILE_GNU) {
                // create a TarEntry for the LongLink, the contents
                // of which are the link's name
                TarArchiveEntry longLinkEntry = new TarArchiveEntry(TarConstants.GNU_LONGLINK, linkType);

                longLinkEntry.setSize(len + 1); // +1 for NUL
                putArchiveEntry(longLinkEntry);
                write(encodedName.array(), encodedName.arrayOffset(), len);
                write(0); // NUL terminator
                closeArchiveEntry();
            } else if (longFileMode != LONGFILE_TRUNCATE) {
                throw new RuntimeException(fieldName + " '" + name
                                           + "' is too long ( > "
                                           + TarConstants.NAMELEN + " bytes)");
            }
        }
        return false;
    }
}
