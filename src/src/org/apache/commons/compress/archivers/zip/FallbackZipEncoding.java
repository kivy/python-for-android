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

package org.apache.commons.compress.archivers.zip;

import java.io.IOException;
import java.nio.ByteBuffer;

/**
 * A fallback ZipEncoding, which uses a java.io means to encode names.
 *
 * <p>This implementation is not suitable for encodings other than
 * UTF-8, because java.io encodes unmappable character as question
 * marks leading to unreadable ZIP entries on some operating
 * systems.</p>
 * 
 * <p>Furthermore this implementation is unable to tell whether a
 * given name can be safely encoded or not.</p>
 * 
 * <p>This implementation acts as a last resort implementation, when
 * neither {@link Simple8BitZipEnoding} nor {@link NioZipEncoding} is
 * available.</p>
 * 
 * <p>The methods of this class are reentrant.</p>
 * @Immutable
 */
class FallbackZipEncoding implements ZipEncoding {
    private final String charsetName;

    /**
     * Construct a fallback zip encoding, which uses the platform's
     * default charset.
     */
    public FallbackZipEncoding() {
        this.charsetName = null;
    }

    /**
     * Construct a fallback zip encoding, which uses the given charset.
     * 
     * @param charsetName The name of the charset or {@code null} for
     *                the platform's default character set.
     */
    public FallbackZipEncoding(String charsetName) {
        this.charsetName = charsetName;
    }

    /**
     * @see
     * org.apache.commons.compress.archivers.zip.ZipEncoding#canEncode(java.lang.String)
     */
    public boolean canEncode(String name) {
        return true;
    }

    /**
     * @see
     * org.apache.commons.compress.archivers.zip.ZipEncoding#encode(java.lang.String)
     */
    public ByteBuffer encode(String name) throws IOException {
        if (this.charsetName == null) { // i.e. use default charset, see no-args constructor
            return ByteBuffer.wrap(name.getBytes());
        } else {
            return ByteBuffer.wrap(name.getBytes(this.charsetName));
        }
    }

    /**
     * @see
     * org.apache.commons.compress.archivers.zip.ZipEncoding#decode(byte[])
     */
    public String decode(byte[] data) throws IOException {
        if (this.charsetName == null) { // i.e. use default charset, see no-args constructor
            return new String(data);
        } else {
            return new String(data,this.charsetName);
        }
    }
}
