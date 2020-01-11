from Renderer import Renderer
from enigma import eLabel
from Components.VariableText import VariableText
from enigma import eServiceReference

class TuxNextReference(VariableText, Renderer):

	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)

	GUI_WIDGET = eLabel

	def connect(self, source):
		Renderer.connect(self, source)
		self.changed((self.CHANGED_DEFAULT,))

	def changed(self, what):
		if self.instance:
			if what[0] == self.CHANGED_CLEAR:
				self.text = "Reference not found !"
			else:
				service = self.source.service
				sname = service.toString()
				pos = sname.rfind(':')
				if pos != -1:
					self.text = "SR: " + sname[:-1]
				else:
					self.text = "Reference reading error !"
