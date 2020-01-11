###############################################################################
# meta.py module
#
# Copyright (C) 2012 vlamo <vlamodev@gmail.com>
# Version: 0.2 (15.07.2012 14:38)
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

import os
from enigma import eServiceReference

def getctime(basename):
	try:
		st = os.stat(basename);
		time = st.st_ctime;
	except:
		time = 0;
	return time;

def fileSize(basename):
	def getsize(filename):
		try:
			st = os.stat(filename);
			res = st.st_size;
		except:
			res = 0;
		return res
	
	# get filesize
	filesize = getsize(basename);
	# handling for old splitted recordings (enigma 1)
	slice = 0;
	while True:
		slice += 1;
		size = getsize("%s.%03d" % (basename,slice));
		if not size:
			break;
		filesize += size;
	return filesize;

class MetaParser:
	def __init__(self):
		self.time_create = 0;
		self.data_ok = 0;
		self.length = 0;
		self.filesize = 0;
		self.name = '';
		self.description = '';
		self.tags = '';
		self.service_data = '';
		self.ref = eServiceReference('1:0:0:0:0:0:0:0:0:0:');
	
	def parseFile(self, basename):
		# first, try parsing the .meta file
		if not self.parseMeta(basename):
			return 0;
		# otherwise, use recordings.epl
		if not self.parseRecordings(basename):
			return 0;
		self.filesize = fileSize(basename);
		self.time_create = getctime(basename);
		return -1;
	
	def parseMeta(self, tsname):
		try:
			f = open(tsname + ".meta", "r");
		except:
			return -1;

		linecnt = 0;
		self.time_create = 0;
		while True:
			line = f.readline();
			if not line:
				break;
			line = line.strip();
			if   linecnt == 0:
				self.ref = eServiceReference(line);
			elif linecnt == 1:
				self.name = line;		# event name
			elif linecnt == 2:
				self.description = line;	# event short description
			elif linecnt == 3:
				self.time_create = int(line or '0') or getctime(tsname);
			elif linecnt == 4:
				self.tags = line;
			elif linecnt == 5:
				self.length = int(line or '0');	# movie length in pts
			elif linecnt == 6:
				self.filesize = int(line or '0');
			elif linecnt == 7:
				self.service_data = line;
			else:
				break;
			linecnt += 1;
		f.close();
		self.data_ok = 1;
		return 0;
	
	def parseRecordings(self, filename):
		slash = filename.rfind('/');
		if slash == -1:
			return -1;
		
		recordings = filename[0:slash] + "/recordings.epl";
		try:
			f = open(recordings, "r");
		except:
			#print "no recordings.epl found: %s" % (recordings);
			return -1;
		
		description = '';
		ref = None;
		
		while True:
			line = f.readline();
			if not line:
				break;
			if len(line) < 2:
				# Lines with less than one char aren't meaningful
				continue;
			# Remove trailing \r\n
			line = line.strip();
			
			if   line.find("#SERVICE: ") == 0:
				ref = eServiceReference(line[10:]);
			elif line.find("#DESCRIPTION: ") == 0:
				description = line[14:];
			elif line[0] == '/' and ref and ref.getPath().split('/')[-1] == filename.split('/')[-1]:
				#print "hit! ref %s descr %s" % (self.ref.toString(), self.name);
				self.ref = ref;
				self.name = description;
				self.description = "";
				self.time_create = getctime(filename);
				self.length = 0;
				self.filesize = fileSize(filename);
				self.data_ok = 1;
				f.close();
				self.updateMeta(filename);
				return 0;
		f.close();
		return -1;
	
	def updateMeta(self, tsname):
		if not self.data_ok:
			return -1;
		ref = self.ref;
		ref.setPath("");
		try:
			f = open(tsname + ".meta", "w");
			f.write("%s\n%s\n%s\n%d\n%s\n%d\n%u\n%s\n" % (
					ref.toString(),
					self.name,
					self.description,
					self.time_create,
					self.tags,
					self.length,
					self.filesize,
					self.service_data
				));
			f.close();
		except:
			return -1;
		return 0;
