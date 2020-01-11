# AlwaysTrue by 2boom 2012 v.0.1

from Components.Converter.Converter import Converter
from Components.Element import cached

class AlwaysTrue(Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)

	@cached
	def getBoolean(self):
		return True
		
	boolean = property(getBoolean)

	def changed(self, what):
		Converter.changed(self, what)
