/**
 * Copyright 2012 Kamran Zafar 
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

package org.kamranzafar.jtar;

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
		header = new TarHeader();
	}

	public TarEntry(File file, String entryName) {
		this();
		this.file = file;
		this.extractTarHeader(entryName);
	}

	public TarEntry(byte[] headerBuf) {
		this();
		this.parseTarHeader(headerBuf);
	}

	/**
	 * Constructor to create an entry from an existing TarHeader object.
	 * 
	 * This method is useful to add new entries programmatically (e.g. for
	 * adding files or directories that do not exist in the file system).
	 * 
	 * @param header
	 * 
	 */
	public TarEntry(TarHeader header) {
		this.file = null;
		this.header = header;
	}

	public boolean equals(TarEntry it) {
		return header.name.toString().equals(it.header.name.toString());
	}

	public boolean isDescendent(TarEntry desc) {
		return desc.header.name.toString().startsWith(header.name.toString());
	}

	public TarHeader getHeader() {
		return header;
	}

	public String getName() {
		String name = header.name.toString();
		if (header.namePrefix != null && !header.namePrefix.toString().equals("")) {
			name = header.namePrefix.toString() + "/" + name;
		}

		return name;
	}

	public void setName(String name) {
		header.name = new StringBuffer(name);
	}

	public int getUserId() {
		return header.userId;
	}

	public void setUserId(int userId) {
		header.userId = userId;
	}

	public int getGroupId() {
		return header.groupId;
	}

	public void setGroupId(int groupId) {
		header.groupId = groupId;
	}

	public String getUserName() {
		return header.userName.toString();
	}

	public void setUserName(String userName) {
		header.userName = new StringBuffer(userName);
	}

	public String getGroupName() {
		return header.groupName.toString();
	}

	public void setGroupName(String groupName) {
		header.groupName = new StringBuffer(groupName);
	}

	public void setIds(int userId, int groupId) {
		this.setUserId(userId);
		this.setGroupId(groupId);
	}

	public void setModTime(long time) {
		header.modTime = time / 1000;
	}

	public void setModTime(Date time) {
		header.modTime = time.getTime() / 1000;
	}

	public Date getModTime() {
		return new Date(header.modTime * 1000);
	}

	public File getFile() {
		return this.file;
	}

	public long getSize() {
		return header.size;
	}

	public void setSize(long size) {
		header.size = size;
	}

	/**
	 * Checks if the org.kamrazafar.jtar entry is a directory
	 * 
	 * @return
	 */
	public boolean isDirectory() {
		if (this.file != null)
			return this.file.isDirectory();

		if (header != null) {
			if (header.linkFlag == TarHeader.LF_DIR)
				return true;

			if (header.name.toString().endsWith("/"))
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
		header = TarHeader.createHeader(entryName, file.length(), file.lastModified() / 1000, file.isDirectory());
	}

	/**
	 * Calculate checksum
	 * 
	 * @param buf
	 * @return
	 */
	public long computeCheckSum(byte[] buf) {
		long sum = 0;

		for (int i = 0; i < buf.length; ++i) {
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

		offset = TarHeader.getNameBytes(header.name, outbuf, offset, TarHeader.NAMELEN);
		offset = Octal.getOctalBytes(header.mode, outbuf, offset, TarHeader.MODELEN);
		offset = Octal.getOctalBytes(header.userId, outbuf, offset, TarHeader.UIDLEN);
		offset = Octal.getOctalBytes(header.groupId, outbuf, offset, TarHeader.GIDLEN);

		long size = header.size;

		offset = Octal.getLongOctalBytes(size, outbuf, offset, TarHeader.SIZELEN);
		offset = Octal.getLongOctalBytes(header.modTime, outbuf, offset, TarHeader.MODTIMELEN);

		int csOffset = offset;
		for (int c = 0; c < TarHeader.CHKSUMLEN; ++c)
			outbuf[offset++] = (byte) ' ';

		outbuf[offset++] = header.linkFlag;

		offset = TarHeader.getNameBytes(header.linkName, outbuf, offset, TarHeader.NAMELEN);
		offset = TarHeader.getNameBytes(header.magic, outbuf, offset, TarHeader.USTAR_MAGICLEN);
		offset = TarHeader.getNameBytes(header.userName, outbuf, offset, TarHeader.USTAR_USER_NAMELEN);
		offset = TarHeader.getNameBytes(header.groupName, outbuf, offset, TarHeader.USTAR_GROUP_NAMELEN);
		offset = Octal.getOctalBytes(header.devMajor, outbuf, offset, TarHeader.USTAR_DEVLEN);
		offset = Octal.getOctalBytes(header.devMinor, outbuf, offset, TarHeader.USTAR_DEVLEN);
		offset = TarHeader.getNameBytes(header.namePrefix, outbuf, offset, TarHeader.USTAR_FILENAME_PREFIX);

		for (; offset < outbuf.length;)
			outbuf[offset++] = 0;

		long checkSum = this.computeCheckSum(outbuf);

		Octal.getCheckSumOctalBytes(checkSum, outbuf, csOffset, TarHeader.CHKSUMLEN);
	}

	/**
	 * Parses the tar header to the byte buffer
	 * 
	 * @param header
	 * @param bh
	 */
	public void parseTarHeader(byte[] bh) {
		int offset = 0;

		header.name = TarHeader.parseName(bh, offset, TarHeader.NAMELEN);
		offset += TarHeader.NAMELEN;

		header.mode = (int) Octal.parseOctal(bh, offset, TarHeader.MODELEN);
		offset += TarHeader.MODELEN;

		header.userId = (int) Octal.parseOctal(bh, offset, TarHeader.UIDLEN);
		offset += TarHeader.UIDLEN;

		header.groupId = (int) Octal.parseOctal(bh, offset, TarHeader.GIDLEN);
		offset += TarHeader.GIDLEN;

		header.size = Octal.parseOctal(bh, offset, TarHeader.SIZELEN);
		offset += TarHeader.SIZELEN;

		header.modTime = Octal.parseOctal(bh, offset, TarHeader.MODTIMELEN);
		offset += TarHeader.MODTIMELEN;

		header.checkSum = (int) Octal.parseOctal(bh, offset, TarHeader.CHKSUMLEN);
		offset += TarHeader.CHKSUMLEN;

		header.linkFlag = bh[offset++];

		header.linkName = TarHeader.parseName(bh, offset, TarHeader.NAMELEN);
		offset += TarHeader.NAMELEN;

		header.magic = TarHeader.parseName(bh, offset, TarHeader.USTAR_MAGICLEN);
		offset += TarHeader.USTAR_MAGICLEN;

		header.userName = TarHeader.parseName(bh, offset, TarHeader.USTAR_USER_NAMELEN);
		offset += TarHeader.USTAR_USER_NAMELEN;

		header.groupName = TarHeader.parseName(bh, offset, TarHeader.USTAR_GROUP_NAMELEN);
		offset += TarHeader.USTAR_GROUP_NAMELEN;

		header.devMajor = (int) Octal.parseOctal(bh, offset, TarHeader.USTAR_DEVLEN);
		offset += TarHeader.USTAR_DEVLEN;

		header.devMinor = (int) Octal.parseOctal(bh, offset, TarHeader.USTAR_DEVLEN);
		offset += TarHeader.USTAR_DEVLEN;

		header.namePrefix = TarHeader.parseName(bh, offset, TarHeader.USTAR_FILENAME_PREFIX);
	}
}