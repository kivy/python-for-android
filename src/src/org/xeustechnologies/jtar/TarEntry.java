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

import java.io.File;
import java.util.Date;

/**
 * @author Kamran Zafar
 * 
 */
public class TarEntry {
    protected File file;
    protected TarHeader header;

    private TarEntry() {
        this.file = null;
        this.header = new TarHeader();
    }

    public TarEntry(File file, String entryName) {
        this();
        this.file = file;
        this.extractTarHeader( entryName );
    }

    public TarEntry(byte[] headerBuf) {
        this();
        this.parseTarHeader( headerBuf );
    }

    public boolean equals(TarEntry it) {
        return this.header.name.toString().equals( it.header.name.toString() );
    }

    public boolean isDescendent(TarEntry desc) {
        return desc.header.name.toString().startsWith( this.header.name.toString() );
    }

    public TarHeader getHeader() {
        return this.header;
    }

    public String getName() {
        return this.header.name.toString();
    }

    public void setName(String name) {
        this.header.name = new StringBuffer( name );
    }

    public int getUserId() {
        return this.header.userId;
    }

    public void setUserId(int userId) {
        this.header.userId = userId;
    }

    public int getGroupId() {
        return this.header.groupId;
    }

    public void setGroupId(int groupId) {
        this.header.groupId = groupId;
    }

    public String getUserName() {
        return this.header.userName.toString();
    }

    public void setUserName(String userName) {
        this.header.userName = new StringBuffer( userName );
    }

    public String getGroupName() {
        return this.header.groupName.toString();
    }

    public void setGroupName(String groupName) {
        this.header.groupName = new StringBuffer( groupName );
    }

    public void setIds(int userId, int groupId) {
        this.setUserId( userId );
        this.setGroupId( groupId );
    }

    public void setModTime(long time) {
        this.header.modTime = time / 1000;
    }

    public void setModTime(Date time) {
        this.header.modTime = time.getTime() / 1000;
    }

    public Date getModTime() {
        return new Date( this.header.modTime * 1000 );
    }

    public File getFile() {
        return this.file;
    }

    public long getSize() {
        return this.header.size;
    }

    public void setSize(long size) {
        this.header.size = size;
    }

    /**
     * Checks if the org.xeustechnologies.jtar entry is a directory
     * 
     * @return
     */
    public boolean isDirectory() {
        if( this.file != null )
            return this.file.isDirectory();

        if( this.header != null ) {
            if( this.header.linkFlag == TarHeader.LF_DIR )
                return true;

            if( this.header.name.toString().endsWith( "/" ) )
                return true;
        }

        return false;
    }

    /**
     * Extract header from File
     * 
     * @param entryName
     */
    public void extractTarHeader(String entryName) {
        String name = entryName;

        name = name.replace( File.separatorChar, '/' );

        if( name.startsWith( "/" ) )
            name = name.substring( 1 );

        header.linkName = new StringBuffer( "" );

        header.name = new StringBuffer( name );

        if( file.isDirectory() ) {
            header.mode = 040755;
            header.linkFlag = TarHeader.LF_DIR;
            if( header.name.charAt( header.name.length() - 1 ) != '/' )
                header.name.append( "/" );
        } else {
            header.mode = 0100644;
            header.linkFlag = TarHeader.LF_NORMAL;
        }

        header.size = file.length();
        header.modTime = file.lastModified() / 1000;
        header.checkSum = 0;
        header.devMajor = 0;
        header.devMinor = 0;
    }

    /**
     * Calculate checksum
     * 
     * @param buf
     * @return
     */
    public long computeCheckSum(byte[] buf) {
        long sum = 0;

        for( int i = 0; i < buf.length; ++i ) {
            sum += 255 & buf[i];
        }

        return sum;
    }

    /**
     * Writes the header to the byte buffer
     * 
     * @param outbuf
     */
    public void writeEntryHeader(byte[] outbuf) {
        int offset = 0;

        offset = TarHeader.getNameBytes( this.header.name, outbuf, offset, TarHeader.NAMELEN );
        offset = Octal.getOctalBytes( this.header.mode, outbuf, offset, TarHeader.MODELEN );
        offset = Octal.getOctalBytes( this.header.userId, outbuf, offset, TarHeader.UIDLEN );
        offset = Octal.getOctalBytes( this.header.groupId, outbuf, offset, TarHeader.GIDLEN );

        long size = this.header.size;

        offset = Octal.getLongOctalBytes( size, outbuf, offset, TarHeader.SIZELEN );
        offset = Octal.getLongOctalBytes( this.header.modTime, outbuf, offset, TarHeader.MODTIMELEN );

        int csOffset = offset;
        for( int c = 0; c < TarHeader.CHKSUMLEN; ++c )
            outbuf[offset++] = (byte) ' ';

        outbuf[offset++] = this.header.linkFlag;

        offset = TarHeader.getNameBytes( this.header.linkName, outbuf, offset, TarHeader.NAMELEN );
        offset = TarHeader.getNameBytes( this.header.magic, outbuf, offset, TarHeader.MAGICLEN );
        offset = TarHeader.getNameBytes( this.header.userName, outbuf, offset, TarHeader.UNAMELEN );
        offset = TarHeader.getNameBytes( this.header.groupName, outbuf, offset, TarHeader.GNAMELEN );
        offset = Octal.getOctalBytes( this.header.devMajor, outbuf, offset, TarHeader.DEVLEN );
        offset = Octal.getOctalBytes( this.header.devMinor, outbuf, offset, TarHeader.DEVLEN );

        for( ; offset < outbuf.length; )
            outbuf[offset++] = 0;

        long checkSum = this.computeCheckSum( outbuf );

        Octal.getCheckSumOctalBytes( checkSum, outbuf, csOffset, TarHeader.CHKSUMLEN );
    }

    /**
     * Parses the tar header to the byte buffer
     * 
     * @param header
     * @param bh
     */
    public void parseTarHeader(byte[] bh) {
        int offset = 0;

        header.name = TarHeader.parseName( bh, offset, TarHeader.NAMELEN );
        offset += TarHeader.NAMELEN;

        header.mode = (int) Octal.parseOctal( bh, offset, TarHeader.MODELEN );
        offset += TarHeader.MODELEN;

        header.userId = (int) Octal.parseOctal( bh, offset, TarHeader.UIDLEN );
        offset += TarHeader.UIDLEN;

        header.groupId = (int) Octal.parseOctal( bh, offset, TarHeader.GIDLEN );
        offset += TarHeader.GIDLEN;

        header.size = Octal.parseOctal( bh, offset, TarHeader.SIZELEN );
        offset += TarHeader.SIZELEN;

        header.modTime = Octal.parseOctal( bh, offset, TarHeader.MODTIMELEN );
        offset += TarHeader.MODTIMELEN;

        header.checkSum = (int) Octal.parseOctal( bh, offset, TarHeader.CHKSUMLEN );
        offset += TarHeader.CHKSUMLEN;

        header.linkFlag = bh[offset++];

        header.linkName = TarHeader.parseName( bh, offset, TarHeader.NAMELEN );
        offset += TarHeader.NAMELEN;

        header.magic = TarHeader.parseName( bh, offset, TarHeader.MAGICLEN );
        offset += TarHeader.MAGICLEN;

        header.userName = TarHeader.parseName( bh, offset, TarHeader.UNAMELEN );
        offset += TarHeader.UNAMELEN;

        header.groupName = TarHeader.parseName( bh, offset, TarHeader.GNAMELEN );
        offset += TarHeader.GNAMELEN;

        header.devMajor = (int) Octal.parseOctal( bh, offset, TarHeader.DEVLEN );
        offset += TarHeader.DEVLEN;

        header.devMinor = (int) Octal.parseOctal( bh, offset, TarHeader.DEVLEN );
    }
}