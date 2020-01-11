# (c) 2boom mod
from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr
from Components.Element import cached

class ServiceOrbitalPosition2(Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)

	@cached
	def getText(self):
		service = self.source.service
		if isinstance(service, iPlayableServicePtr):
			info = service and service.info()
			ref = None
		else: # reference
			info = service and self.source.info
			ref = service
		if info is None:
			return ""
		if ref:
			transponder_info = info.getInfoObject(ref, iServiceInformation.sTransponderData)
		else:
			transponder_info = info.getInfoObject(iServiceInformation.sTransponderData)
		if transponder_info and "orbital_position" in transponder_info.keys():
			pos = int(transponder_info["orbital_position"])
			direction = 'E'
			if pos > 1800:
				pos = 3600 - pos
				direction = 'W'
			return "%d%d%s" % (pos/10, pos%10, direction)
		else:
			return 'picon_default'

	text = property(getText)

	def changed(self, what):
		if what[0] != self.CHANGED_SPECIFIC or what[1] in [iPlayableService.evStart]:
			Converter.changed(self, what)
