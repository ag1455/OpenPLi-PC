#
#  Converter Bitrate2
#
#
#  This plugin is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.

#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially 
#  distributed other than under the conditions noted above.
#

from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService, eTimer
from Components.Element import cached
try:
	from bitratecalc import eBitrateCalculator
except:
	pass


class Bitrate2(Converter, object):

	VPID = 0
	APID = 1
	FORMAT = 2

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "VideoBitrate":
			self.type = self.VPID
		elif type == "AudioBitrate":
			self.type = self.APID
		else:
			# format:
			#   %V - video bitrate value
			#   %A - audio bitrate value
			self.type = self.FORMAT
			self.sfmt = type[:]
			if self.sfmt == "":
				self.sfmt = "V:%V Kb/s A:%A Kb/s"
		self.clearData()
		self.initTimer = eTimer()
		self.initTimer.callback.append(self.initBitrateCalc)

	def clearData(self):
		self.videoBitrate = None
		self.audioBitrate = None
		self.video = self.audio = 0

	def initBitrateCalc(self):
		service = self.source.service
		vpid = apid = dvbnamespace = tsid = onid = -1
		if service:
			serviceInfo = service.info()
			vpid = serviceInfo.getInfo(iServiceInformation.sVideoPID)
			apid = serviceInfo.getInfo(iServiceInformation.sAudioPID)
			tsid = serviceInfo.getInfo(iServiceInformation.sTSID)
			onid = serviceInfo.getInfo(iServiceInformation.sONID)
			dvbnamespace = serviceInfo.getInfo(iServiceInformation.sNamespace)
		if vpid > 0 and (self.type == self.VPID or (self.type == self.FORMAT and "%V" in self.sfmt)):
			self.videoBitrate = eBitrateCalculator(vpid, dvbnamespace, tsid, onid, 1000, 1024*1024) # pid, dvbnamespace, tsid, onid, refresh intervall, buffer size
			self.videoBitrate.callback.append(self.getVideoBitrateData)
		if apid > 0 and (self.type == self.APID or (self.type == self.FORMAT and "%A" in self.sfmt)):
			self.audioBitrate = eBitrateCalculator(apid, dvbnamespace, tsid, onid, 1000, 64*1024)
			self.audioBitrate.callback.append(self.getAudioBitrateData)

	@cached
	def getText(self):
		if self.type == self.VPID:
			ret = "%d"%(self.video)
		elif self.type == self.APID:
			ret = "%d"%(self.audio)
		else:
			ret = ""
			tmp = self.sfmt[:]
			while True:
				pos = tmp.find('%')
				if pos == -1:
					ret += tmp
					break
				ret += tmp[:pos]
				pos += 1
				l = len(tmp)
				f = pos < l and tmp[pos] or '%'
				if f == 'V':	# %V - VideoBitrate
					ret += "%d"%(self.video)
				elif f == 'A':	# %A - AudioBitrate
					ret += "%d"%(self.audio)
				else:
					ret += f
				if pos+1 >= l: break
				tmp = tmp[pos+1:]
		return ret

	text = property(getText)

	def getVideoBitrateData(self, value, status): # value = rate in kbit/s, status ( 1  = ok || 0 = nok (zapped?))
		if status:
			self.video = value
		else:
			self.videoBitrate = None
			self.video = 0
		Converter.changed(self, (self.CHANGED_POLL,))

	def getAudioBitrateData(self, value, status):
		if status:
			self.audio = value
		else:
			self.audioBitrate = None
			self.audio = 0
		Converter.changed(self, (self.CHANGED_POLL,))

	def changed(self, what):
		if what[0] == self.CHANGED_SPECIFIC:
			if what[1] == iPlayableService.evStart:
				self.initTimer.start(100, True)
			elif what[1] == iPlayableService.evEnd:
				self.clearData()
				#Converter.changed(self, (self.CHANGED_POLL,))
				Converter.changed(self, what)
