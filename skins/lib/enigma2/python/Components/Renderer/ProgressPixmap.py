#
# ProgressPixmap Renderer for Enigma2 Dreamboxes and other (ProgressPixmap.py)
# Coded by vlamo (c) 2011
#
# Version: 0.1 (05.10.2011 21:11)
# Support: http://dream.altmaster.net/
#

from Renderer import Renderer
from enigma import ePixmap, loadPNG
from Tools.Directories import fileExists, resolveFilename, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN

class ProgressPixmap(Renderer):
	GUI_WIDGET = ePixmap

	def __init__(self):
		Renderer.__init__(self)
		self.pixmapCache = { }
		self.pixmapPath = ""
		self.pixmapCount = 0

	def applySkin(self, desktop, parent):
		attribs = [ ]
		for (attrib, value) in self.skinAttributes:
			if attrib == "pixmapPath":
				for scope in (SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN):
					tmp = resolveFilename(scope, value)
					if '%d' in tmp and fileExists(tmp%(0)):
						self.pixmapPath = tmp
						break
			elif attrib == "pixmapCount":
				self.pixmapCount = int(value)
			else:
				attribs.append((attrib,value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	def loadCurrentPixmap(self, path):
		if path in self.pixmapCache:
			return self.pixmapCache[path]
		else:
			png = loadPNG(path)
			if png:	self.pixmapCache[path] = png
			return png

	def changed(self, what):
		if self.instance is not None:
			png = None
			if what[0] != self.CHANGED_CLEAR:
				range = self.source.range
				value = self.source.value
				if value is None or value < 1:
					value = 0
				elif value > range:
					value = range
				if self.pixmapCount - 1 > 0 and self.pixmapPath:
					step = range / (self.pixmapCount - 1)
					v = (value + step - 1) / step
					path = self.pixmapPath%(v)
					png = self.loadCurrentPixmap(path)
			self.instance.setPixmap(png)
