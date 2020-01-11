#Coders by Nikolasi
# -*- coding: UTF-8 -*-
from Renderer import Renderer
from enigma import ePixmap, eEnv
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Components.Converter.Poll import Poll

class RatingTmbd(Renderer, Poll):
	__module__ = __name__
	searchPaths = ('/usr/share/enigma2/%s/', '/media/hdd/%s/',  '/media/usb/%s/', '/media/USB/%s/')

	def __init__(self):
		Poll.__init__(self)
		Renderer.__init__(self)
		self.path = 'starsbar'
		self.nameCache = {}
		self.pngname = ''

	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value,) in self.skinAttributes:
			if (attrib == 'path'):
				self.path = value
			else:
				attribs.append((attrib, value))

		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		self.poll_interval = 2000
		self.poll_enabled = True
		if self.instance:
			pngname = ''
			if (what[0] != self.CHANGED_CLEAR):
				sname = self.source.text
				pngname = self.nameCache.get(sname, '')
				if (pngname == ''):
					pngname = self.findPicon(sname)
					if (pngname != ''):
						self.nameCache[sname] = pngname
			if (pngname == ''):
				pngname = self.nameCache.get('00', '')
				if (pngname == ''):
					pngname = self.findPicon('00')
					self.nameCache['00'] = pngname
			if (self.pngname != pngname):
				self.instance.setPixmapFromFile(pngname)
				self.pngname = pngname


	def findPicon(self, serviceName):
                IMAGE_PATH2 = resolveFilename(SCOPE_CURRENT_SKIN, 'starsbar')
                path2 = resolveFilename(SCOPE_SKIN_IMAGE, IMAGE_PATH2)
                if fileExists(path2):
                        pngname = ((path2 + "/" + serviceName) + ".png")
			if fileExists(pngname):
				return pngname
		else:	
		        for path in self.searchPaths:
			        pngname = (((path % self.path) + serviceName) + ".png")
			        if fileExists(pngname):
				        return pngname

		return ''

