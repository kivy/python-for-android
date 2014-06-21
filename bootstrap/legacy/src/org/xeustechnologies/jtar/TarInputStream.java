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

import java.io.FilterInputStream;
import java.io.IOException;
import java.io.InputStream;

/**
 * @author Kamran Zafar
 * 
 */
public class TarInputStream extends FilterInputStream {

    private TarEntry currentEntry;
    private long currentFileSize;
    private long bytesRead;

    public TarInputStream(InputStream in) {
        super( in );
        currentFileSize = 0;
        bytesRead = 0;
    }

    @Override
    public boolean markSupported() {
        return false;
    }

    /**
     * Not supported
     * 
     */
    @Override
    public synchronized void mark(int readlimit) {
    }

    /**
     * Not supported
     * 
     */
    @Override
    public synchronized void reset() throws IOException {
        throw new IOException( "mark/reset not supported" );
    }

    /**
     * Read a byte
     * 
     * @see java.io.FilterInputStream#read()
     */
    @Override
    public int read() throws IOException {
        byte[] buf = new byte[1];

        int res = this.read( buf, 0, 1 );

        if( res != -1 ) {
            return buf[0];
        }

        return res;
    }

    /**
     * Checks if the bytes being read exceed the entry size and adjusts the byte
     * array length. Updates the byte counters
     * 
     * 
     * @see java.io.FilterInputStream#read(byte[], int, int)
     */
    @Override
    public int read(byte[] b, int off, int len) throws IOException {
        if( currentEntry != null ) {
            if( currentFileSize == currentEntry.getSize() ) {
                return -1;
            } else if( ( currentEntry.getSize() - currentFileSize ) < len ) {
                len = (int) ( currentEntry.getSize() - currentFileSize );
            }
        }

        int br = super.read( b, off, len );

        if( br != -1 ) {
            if( currentEntry != null ) {
                currentFileSize += br;
            }

            bytesRead += br;
        }

        return br;
    }

    /**
     * Returns the next entry in the tar file
     * 
     * @return TarEntry
     * @throws IOException
     */
    public TarEntry getNextEntry() throws IOException {
        closeCurrentEntry();

        byte[] header = new byte[TarConstants.HEADER_BLOCK];

        int res = read( header );

        // Invalid header size
        if( res != TarConstants.HEADER_BLOCK ) {
            throw new IOException( "Invalid entry header of size [" + res + "]; expected [" + TarConstants.HEADER_BLOCK
                    + "]" );
        }

        // Check if record is null
        boolean eof = true;
        for( byte b : header ) {
            if( b != 0 ) {
                eof = false;
                break;
            }
        }

        if( !eof ) {
            currentEntry = new TarEntry( header );
        }

        return currentEntry;
    }

    /**
     * Closes the current tar entry
     * 
     * @throws IOException
     */
    protected void closeCurrentEntry() throws IOException {
        if( currentEntry != null ) {
            if( currentEntry.getSize() > currentFileSize ) {
                // Not fully read, skip rest of the bytes
                skip( currentEntry.getSize() - currentFileSize );
                bytesRead += ( currentEntry.getSize() - currentFileSize );
            }

            currentEntry = null;
            currentFileSize = 0L;
            skipPad();
        }
    }

    /**
     * Skips the pad at the end of each tar entry file content
     * 
     * @throws IOException
     */
    protected void skipPad() throws IOException {
        if( bytesRead > 0 ) {
            int extra = (int) ( bytesRead % TarConstants.DATA_BLOCK );

            if( extra > 0 ) {
                skip( TarConstants.DATA_BLOCK - extra );
                bytesRead += ( TarConstants.DATA_BLOCK - extra );
            }
        }
    }
}
