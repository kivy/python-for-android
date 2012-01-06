/**
 * Copyright 2010 Xeus Technologies 
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
 * 
 */

package org.xeustechnologies.jtar;

/**
 * Header
 * 
 * <pre>
 * Offset  Size     Field
 * 0       100      File name
 * 100     8        File mode
 * 108     8        Owner's numeric user ID
 * 116     8        Group's numeric user ID
 * 124     12       File size in bytes
 * 136     12       Last modification time in numeric Unix time format
 * 148     8        Checksum for header block
 * 156     1        Link indicator (file type)
 * 157     100      Name of linked file
 * </pre>
 * 
 * 
 * File Types
 * 
 * <pre>
 * Value        Meaning
 * '0'          Normal file
 * (ASCII NUL)  Normal file (now obsolete)
 * '1'          Hard link
 * '2'          Symbolic link
 * '3'          Character special
 * '4'          Block special
 * '5'          Directory
 * '6'          FIFO
 * '7'          Contigous
 * </pre>
 * 
 * 
 * 
 * Ustar header
 * 
 * <pre>
 * Offset  Size    Field
 * 257     6       UStar indicator "ustar"
 * 263     2       UStar version "00"
 * 265     32      Owner user name
 * 297     32      Owner group name
 * 329     8       Device major number
 * 337     8       Device minor number
 * 345     155     Filename prefix
 * </pre>
 */

public class TarHeader {

    /*
     * Header
     */
    public static final int NAMELEN = 100;
    public static final int MODELEN = 8;
    public static final int UIDLEN = 8;
    public static final int GIDLEN = 8;
    public static final int SIZELEN = 12;
    public static final int MODTIMELEN = 12;
    public static final int CHKSUMLEN = 8;
    public static final byte LF_OLDNORM = 0;

    /*
     * File Types
     */
    public static final byte LF_NORMAL = (byte) '0';
    public static final byte LF_LINK = (byte) '1';
    public static final byte LF_SYMLINK = (byte) '2';
    public static final byte LF_CHR = (byte) '3';
    public static final byte LF_BLK = (byte) '4';
    public static final byte LF_DIR = (byte) '5';
    public static final byte LF_FIFO = (byte) '6';
    public static final byte LF_CONTIG = (byte) '7';

    /*
     * Ustar header
     */

    public static final int MAGICLEN = 8;
    /**
     * The magic tag representing a POSIX tar archive.
     */
    public static final String TMAGIC = "ustar";

    /**
     * The magic tag representing a GNU tar archive.
     */
    public static final String GNU_TMAGIC = "ustar  ";

    public static final int UNAMELEN = 32;
    public static final int GNAMELEN = 32;
    public static final int DEVLEN = 8;

    // Header values
    public StringBuffer name;
    public int mode;
    public int userId;
    public int groupId;
    public long size;
    public long modTime;
    public int checkSum;
    public byte linkFlag;
    public StringBuffer linkName;
    public StringBuffer magic;
    public StringBuffer userName;
    public StringBuffer groupName;
    public int devMajor;
    public int devMinor;

    public TarHeader() {
        this.magic = new StringBuffer( TarHeader.TMAGIC );

        this.name = new StringBuffer();
        this.linkName = new StringBuffer();

        String user = System.getProperty( "user.name", "" );

        if( user.length() > 31 )
            user = user.substring( 0, 31 );

        this.userId = 0;
        this.groupId = 0;
        this.userName = new StringBuffer( user );
        this.groupName = new StringBuffer( "" );
    }

    /**
     * Parse an entry name from a header buffer.
     * 
     * @param name
     * @param header
     *            The header buffer from which to parse.
     * @param offset
     *            The offset into the buffer from which to parse.
     * @param length
     *            The number of header bytes to parse.
     * @return The header's entry name.
     */
    public static StringBuffer parseName(byte[] header, int offset, int length) {
        StringBuffer result = new StringBuffer( length );

        int end = offset + length;
        for( int i = offset; i < end; ++i ) {
            if( header[i] == 0 )
                break;
            result.append( (char) header[i] );
        }

        return result;
    }

    /**
     * Determine the number of bytes in an entry name.
     * 
     * @param name
     * @param header
     *            The header buffer from which to parse.
     * @param offset
     *            The offset into the buffer from which to parse.
     * @param length
     *            The number of header bytes to parse.
     * @return The number of bytes in a header's entry name.
     */
    public static int getNameBytes(StringBuffer name, byte[] buf, int offset, int length) {
        int i;

        for( i = 0; i < length && i < name.length(); ++i ) {
            buf[offset + i] = (byte) name.charAt( i );
        }

        for( ; i < length; ++i ) {
            buf[offset + i] = 0;
        }

        return offset + length;
    }

}