###############################################################################
# event.py module
#
# Copyright (C) 2012 vlamo <vlamodev@gmail.com>
# Version: 0.2 (13.07.2012 23:10)
#
# This module is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program; if not, write to the Free Software Foundation, Inc., 59
# Temple Place, Suite 330, Boston, MA 0.1.2-1307 USA
###############################################################################

import array
import time
from dvbstring import convertDVBUTF8, convertUTF8DVB


def fromBCD(bcd):
	if ((bcd & 0xF0) >= 0xA0) or ((bcd & 0xF) >= 0xA):
		return -1;
	return ((bcd & 0xF0) >> 4)*10 + (bcd & 0xF);

def toBCD(dec):
	if (dec >= 100):
		return -1;
	return int(dec / 10) * 0x10 + (dec % 10);

def parseDVBtime(t1, t2, t3, t4, t5):
	mjd = (t1 << 8) | t2;
	jdn = mjd + 2400001;
	
	a = jdn + 32044;
	b = int((4*a+3)/146097);
	c = a - int((146097*b)/4);
	d = int((4*c+3)/1461);
	e = c - int((1461*d)/4);
	m = int((5*e+2)/153);
	
	year = 100*b + d - 4800 + m/10;
	mon = m + 3 - (m/10)*12;
	mday = e - int((153*m+2)/5) + 1;
	hour = fromBCD(t3);
	min  = fromBCD(t4);
	sec  = fromBCD(t5);
	return time.mktime((year, mon, mday, hour, min, sec, 0, 0, 0));
	

class ShortEventDescriptor:
	def __init__(self, buffer):
		self.iso639LanguageCode = '---';
		self.eventName = '';
		self.text = '';
		
		bufferLen = len(buffer);
		headerLength = 5;
		if headerLength < bufferLen:
			self.iso639LanguageCode = ''.join([chr(x) for x in buffer[2:5]]);
			eventNameLength = buffer[5];
			headerLength += eventNameLength;
			if headerLength < bufferLen:
				self.eventName = convertDVBUTF8([x for x in buffer[6:6+eventNameLength]], eventNameLength);
				textLength = buffer[6 + eventNameLength];
				headerLength += textLength;
				if headerLength < bufferLen:
					self.text = convertDVBUTF8([x for x in buffer[7+eventNameLength:7+eventNameLength+textLength]], textLength);

	def getIso639LanguageCode(self):
		return self.iso639LanguageCode;

	def setIso639LanguageCode(self, value):
		self.iso639LanguageCode = value;

	def getEventName(self):
		return self.eventName;

	def setEventName(self, value):
		self.eventName = value;

	def getText(self):
		return self.text;

	def setText(self, value):
		self.text = value;

class ExtendedEvent:
	def __init__(self, buffer):
		self.itemDescriptionLength = buffer[0];
		self.itemDescription = [x for x in buffer[1:1+self.itemDescriptionLength]];
		self.itemLength = buffer[self.itemDescriptionLength + 1];
		self.item = [x for x in buffer[self.itemDescriptionLength + 2:self.itemDescriptionLength + 2 + self.itemLength]];

	def getItemDescription(self):
		return self.itemDescription;

	def getItem(self):
		return self.item;

class ExtendedEventDescriptor:
	def __init__(self, buffer):
		self.iso639LanguageCode = '---';
		self.descriptorNumber = 0;
		self.lastDescriptorNumber = 0;
		self.items = [ ];
		self.text = '';
		
		bufferLen = len(buffer);
		headerLength = 6;
		if headerLength < bufferLen:
			self.descriptorNumber = (buffer[2] >> 4) & 0x0f;
			self.lastDescriptorNumber = buffer[2] & 0x0f;
			self.iso639LanguageCode = ''.join([chr(x) for x in buffer[3:6]]);
			lengthOfItems = buffer[6];
			headerLength += lengthOfItems;
			if headerLength < bufferLen:
				i = 0
				while i < lengthOfItems:
					e = ExtendedEvent(buffer[i+7:]);
					self.items.append(e);
					i += e.itemDescriptionLength + e.itemLength + 2;
				textLength = buffer[lengthOfItems + 7];
				headerLength += textLength;
				if headerLength < bufferLen:
					self.text = convertDVBUTF8([x for x in buffer[8+lengthOfItems:8+lengthOfItems+textLength]], textLength);

	def getIso639LanguageCode(self):
		return self.iso639LanguageCode;

	def setIso639LanguageCode(self, value):
		self.iso639LanguageCode = value;

	def getDescriptorNumber(self):
		return self.descriptorNumber;

	def setDescriptorNumber(self, value):
		self.descriptorNumber = value;

	def getLastDescriptorNumber(self):
		return self.lastDescriptorNumber;

	def setLastDescriptorNumber(self, value):
		self.lastDescriptorNumber = value;

	def getItems(self):
		return self.items;

	def setItems(self, value):
		self.items = value;

	def getText(self):
		return self.text;

	def setText(self, value):
		self.text = value;


class Event:
	EIT_LOOP_SIZE                 = 12;
	EIT_LENGTH                    = 4108;
	MAX_DESCRIPTOR_LOOP_LENGTH    = 4095;
	EIT_SHORT_EVENT_DESCRIPTOR    = 0x4d;
	EIT_EXTENDED_EVENT_DESCRIPTOR = 0x4e;
	
	def __init__(self, buffer=None):
		if buffer is None:
			buffer = [0]*12;
		self.__readFromBuffer(buffer)
	
	def __readFromBuffer(self, buffer):
		self.eventId = (buffer[0] << 8) | buffer[1];
		self.startTimeMjd = (buffer[2] << 8) | buffer[3];			# modified julian date
		self.startTimeBcd = (buffer[4] << 16) | (buffer[5] << 8) | buffer[6];	# binary-coded decimal time, e.g.: 0x010203 = 01:02:03
		self.durationBcd = (buffer[7] << 16) | (buffer[8] << 8) | buffer[9];	# binary-coded decimal time, e.g.: 0x010203 = 1 hour 2 min and 3 sec
		self.runningStatus = (buffer[10] >> 5) & 0x07;
		self.freeCaMode = (buffer[10] >> 4) & 0x01;
		descriptorsLoopLength = ((buffer[10] & 0x0f) << 8) | buffer[11];

		self.shortEventDescriptor = None;
		self.extendedEventDescriptor = None;
		i = 12
		while i < descriptorsLoopLength + 12:
			if buffer[i] == self.EIT_SHORT_EVENT_DESCRIPTOR:
				self.shortEventDescriptor = ShortEventDescriptor(buffer[i:]);
			elif buffer[i] == self.EIT_EXTENDED_EVENT_DESCRIPTOR:
				eed = ExtendedEventDescriptor(buffer[i:]);
				if self.extendedEventDescriptor is None:
					self.extendedEventDescriptor = eed;
				else:
					self.extendedEventDescriptor.setText(self.extendedEventDescriptor.getText() + eed.getText());
			else:
				pass;
			i += buffer[i+1] + 2;
	
	def __saveToBuffer(self, buffer):
		buffer[0] = self.eventId >> 8;
		buffer[1] = self.eventId &  0xff;
		buffer[2] = self.startTimeMjd >> 8;
		buffer[3] = self.startTimeMjd &  0xff;
		buffer[4] = self.startTimeBcd >> 16;
		buffer[5] =(self.startTimeBcd >> 8) & 0xff;
		buffer[6] = self.startTimeBcd &  0xff;
		buffer[7] = self.durationBcd >> 16;
		buffer[8] =(self.durationBcd >> 8) & 0xff;
		buffer[9] = self.durationBcd &  0xff;
		
		descriptorsLoopLength = 0
		if not self.shortEventDescriptor is None:
			lang = self.shortEventDescriptor.getIso639LanguageCode();
			table, name = convertUTF8DVB(self.shortEventDescriptor.getEventName(), lang);
			name = table + name[0:248-len(table)]		# may be '250-len(table)'???
			namelen = len(name);
			table, text = convertUTF8DVB(self.shortEventDescriptor.getText(), lang);
			text = table + text[0:248-namelen-len(table)]	# may be '250-namelen-len(table)'???
			textlen = len(text);
			length = 5 + namelen + textlen;			# max. length == 253 (or 255???)
			
			sbuf = array.array('B', '\0'*(length+2));	# +2 for tag and length bytes
			sbuf[0] = self.EIT_SHORT_EVENT_DESCRIPTOR;
			sbuf[1] = length;
			for i in range(2,5):
				sbuf[i] = ord(lang[i-2]);
			sbuf[5] = namelen;
			if namelen:
				for i in range(6,6+namelen):
					sbuf[i] = ord(name[i-6]);
			sbuf[6+namelen] = textlen;
			if textlen:
				sbuf[7+namelen] = 1;
				for i in range(7+namelen,7+namelen+textlen):
					sbuf[i] = ord(text[i-7-namelen]);
			buffer.extend(sbuf);
			descriptorsLoopLength += length+2;
		
		if not self.extendedEventDescriptor is None:
			itemlen = 0;
			lang = self.extendedEventDescriptor.getIso639LanguageCode();
			table, text = convertUTF8DVB(self.extendedEventDescriptor.getText(), lang);
			textlen = min(self.MAX_DESCRIPTOR_LOOP_LENGTH, len(text));
			tablelen = len(table);
			MAX_LEN = 247-tablelen;	# may be '249-tablelen'???
			lastDescriptorNumber = (textlen + MAX_LEN-1) / MAX_LEN - 1;
			remainingTextLength = textlen - lastDescriptorNumber * MAX_LEN;
			while (lastDescriptorNumber+1) * 256 + descriptorsLoopLength > self.MAX_DESCRIPTOR_LOOP_LENGTH:
				lastDescriptorNumber -= 1;
				remainingTextLength = MAX_LEN;
			
			descrIndex = 0;
			while descrIndex <= lastDescriptorNumber:
				curtextlen = descrIndex < lastDescriptorNumber and MAX_LEN or remainingTextLength;
				curtext = table + text[descrIndex*MAX_LEN:descrIndex*MAX_LEN+curtextlen]
				length = 6 + itemlen + curtextlen+tablelen;	# max. length == 253 (or 255???)
				
				ebuf = array.array('B', '\0'*(length+2));	# +2 for tag and length bytes
				ebuf[0] = self.EIT_EXTENDED_EVENT_DESCRIPTOR;
				ebuf[1] = length;
				ebuf[2] = (descrIndex << 4) | lastDescriptorNumber;
				for i in range(3,6):
					ebuf[i] = ord(lang[i-3]);
				ebuf[6] = itemlen;
				ebuf[7+itemlen] = curtextlen + tablelen;
				if curtextlen:
					for i in range(8+itemlen,8+itemlen+curtextlen+tablelen):
						ebuf[i] = ord(curtext[i-8-itemlen]);
				
				buffer.extend(ebuf);
				descriptorsLoopLength += length+2;
				descrIndex += 1;
		
		buffer[10] = ((self.runningStatus & 0x07) >> 5) | ((self.freeCaMode & 0x01) >> 1) | ((descriptorsLoopLength >> 8) & 0x0f);
		buffer[11] = descriptorsLoopLength & 0xff;
		return buffer
	
	def readFromFile(self, filename):
		buffer = None
		try:
			buffer = array.array('B', open(filename, 'rb').read());
			self.__readFromBuffer(buffer);
		except:
			import traceback
			fd = open('/tmp/event.log', 'a+');
			print>>fd, 'readFromFile(): error:\n', traceback.format_exc();

		return buffer is None and -1 or buffer.buffer_info()[1];
	
	def saveToFile(self, filename):
		try:
			buffer = array.array('B', '\0'*12);
			self.__saveToBuffer(buffer);
			res = buffer.buffer_info()[1];
			fd = open(filename, 'wb');
			buffer.tofile(fd);
			fd.flush();
			fd.close();
			return res;
			
		except:
			import traceback
			fd = open('/tmp/event.log', 'a+');
			print>>fd, 'saveToFile(): error:\n', traceback.format_exc();
			res = -1;

		return res;

	def getEventId(self):
		return self.eventId;

	def setEventId(self, value):
		self.eventId = value;

	def getStartTimeMjd(self):
		return self.startTimeMjd;

	def setStartTimeMjd(self, value):
		self.startTimeMjd = value & 0xffff;

	def getStartTimeBcd(self):
		return self.startTimeBcd;

	def setStartTimeBcd(self, value):
		self.startTimeBcd = value & 0xffffff;

	def getStartTime(self):
		return parseDVBtime(
				self.startTimeMjd >> 8,
				self.startTimeMjd & 0xff,
				self.startTimeBcd >> 16,
				(self.startTimeBcd >> 8) & 0xff,
				self.startTimeBcd & 0xff
			);

	def setStartTime(self, value):
		t = time.gmtime(value);
		a = (14 - t.tm_mon)/12;
		y = t.tm_year + 4800 - a;
		m = t.tm_mon + 12*a - 3;
		jdn = t.tm_mday + ((153*m + 2)/5) + (365*y) + (y/4) - (y/100) + (y/400) - 32045;
		mjd  = int(jdn + ((t.tm_hour-12)/24.00) + (t.tm_min/1440.00) + (t.tm_sec/86400.00) - 2400000.5);
		bcd = (toBCD(t.tm_hour) << 16) | (toBCD(t.tm_min) << 8) | toBCD(t.tm_sec);
		self.setStartTimeMjd(mjd);
		self.setStartTimeBcd(bcd);

	def getDurationBcd(self):
		return self.durationBcd;

	def setDurationBcd(self, value):
		self.durationBcd = value;

	def getDuration(self):
		return  fromBCD(self.durationBcd >> 16) * 3600 + \
			fromBCD(self.durationBcd >> 8) * 60 + \
			fromBCD(self.durationBcd);

	def setDuration(self, value):
		(h,m) = divmod(value, 3600);
		(m,s) = divmod(m, 60);
		self.setDurationBcd((toBCD(h) << 16) | (toBCD(m) << 8) | toBCD(s));

	def getRunningStatus(self):
		return self.runningStatus;

	def setRunningStatus(self, value):
		self.runningStatus = value;

	def getFreeCaMode(self):
		return self.freeCaMode;

	def setFreeCaMode(self, value):
		self.freeCaMode = value;

	def getShortEventDescriptor(self):
		return self.shortEventDescriptor;

	def setShortEventDescriptor(self, value):
		self.shortEventDescriptor = value;

	def getExtendedEventDescriptor(self):
		return self.extendedEventDescriptor;

	def setExtendedEventDescriptor(self, value):
		self.extendedEventDescriptor = value;

	def getEventName(self):
		return self.shortEventDescriptor and self.shortEventDescriptor.getEventName() or '';

	def getShortDescription(self):
		return self.shortEventDescriptor and self.shortEventDescriptor.getText() or '';

	def getExtendedDescription(self):
		return self.extendedEventDescriptor and self.extendedEventDescriptor.getText() or '';

