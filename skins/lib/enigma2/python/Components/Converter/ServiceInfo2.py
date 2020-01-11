from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService
from Components.Element import cached

class ServiceInfo2(Converter, object):

	xAPID = 0
	xVPID = 1
	xSID = 2
	xONID = 3
	xTSID = 4
	sCAIDs = 5
	yAll = 6
	xAll = 7

	def __init__(self, type):
		Converter.__init__(self, type)
		self.type, self.interesting_events = {
				"xAPID": (self.xAPID, (iPlayableService.evUpdatedInfo,)),
				"xVPID": (self.xVPID, (iPlayableService.evUpdatedInfo,)),
				"xSID": (self.xSID, (iPlayableService.evUpdatedInfo,)),
				"xONID": (self.xONID, (iPlayableService.evUpdatedInfo,)),
				"xTSID": (self.xTSID, (iPlayableService.evUpdatedInfo,)),
				"sCAIDs": (self.sCAIDs, (iPlayableService.evUpdatedInfo,)),
				"yAll": (self.yAll, (iPlayableService.evUpdatedInfo,)),
				"xAll": (self.xAll, (iPlayableService.evUpdatedInfo,)),
			}[type]

	def getServiceInfoString(self, info, what, convert = lambda x: "%d" % x):
		v = info.getInfo(what)
		if v == -1:
			return "N/A"
		if v == -2:
			return info.getInfoString(what)
		if v == -3:
			t_objs = info.getInfoObject(what)
			if t_objs and (len(t_objs) > 0):
				ret_val=""
				for t_obj in t_objs:
					ret_val += "%.4X " % t_obj
				return ret_val[:-1]
			else:
				return ""
		return convert(v)


	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""

		if self.type == self.xAPID:
			try:
				return "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sAudioPID))
			except:
				return "N/A"
		elif self.type == self.xVPID:
			try:
				return "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sVideoPID))
			except:
				return "N/A"
		elif self.type == self.xSID:
			try:
				return "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sSID))
			except:
				return "N/A"
		elif self.type == self.xTSID:
			try:
				return "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sTSID))
			except:
				return "N/A"
		elif self.type == self.xONID:
			try:
				return "%0.4X" % int(self.getServiceInfoString(info, iServiceInformation.sONID))
			except:
				return "N/A"
		elif self.type == self.sCAIDs:
			try:
				return self.getServiceInfoString(info, iServiceInformation.sCAIDs)
			except:
				return "N/A"
		elif self.type == self.yAll:
			try:
				return "SID: %0.4X  VPID: %0.4X  APID: %0.4X  TSID: %0.4X  ONID: %0.4X" % (int(self.getServiceInfoString(info, iServiceInformation.sSID)), int(self.getServiceInfoString(info, iServiceInformation.sVideoPID)), int(self.getServiceInfoString(info, iServiceInformation.sAudioPID)), int(self.getServiceInfoString(info, iServiceInformation.sTSID)), int(self.getServiceInfoString(info, iServiceInformation.sONID)))
			except:
				try:
					return "SID: %0.4X  VPID: %0.4X  TSID: %0.4X  ONID: %0.4X" % (int(self.getServiceInfoString(info, iServiceInformation.sSID)), int(self.getServiceInfoString(info, iServiceInformation.sVideoPID)), int(self.getServiceInfoString(info, iServiceInformation.sTSID)), int(self.getServiceInfoString(info, iServiceInformation.sONID)))
				except:
					return "N/A"
		elif self.type == self.xAll:
			try:
				return "SID: %0.4X  VPID: %0.4X APID: %0.4X" % (int(self.getServiceInfoString(info, iServiceInformation.sSID)), int(self.getServiceInfoString(info, iServiceInformation.sVideoPID)), int(self.getServiceInfoString(info, iServiceInformation.sAudioPID)))
			except:
				try:
					return "SID: %0.4X  APID: %0.4X" % (int(self.getServiceInfoString(info, iServiceInformation.sSID)), int(self.getServiceInfoString(info, iServiceInformation.sAudioPID)))
				except:
					return "N/A"
		return ""

	text = property(getText)


	def changed(self, what):
		if what[0] != self.CHANGED_SPECIFIC or what[1] in self.interesting_events:
			Converter.changed(self, what)
