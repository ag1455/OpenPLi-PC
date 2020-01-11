#Coders by Nikolasi
# -*- coding: UTF-8 -*-
from Tools.Directories import fileExists
from Tools.LoadPixmap import LoadPixmap
from Components.Pixmap import Pixmap
from Renderer import Renderer
from enigma import ePixmap, eServiceCenter, loadPic, eTimer, ePicLoad
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Components.Converter.Poll import Poll
import os

class CoverTmbd(Renderer, Poll):
	__module__ = __name__
	searchPaths = ('/media/hdd/%s/',  '/media/usb/%s/', '/media/sdb2/%s/')

	def __init__(self):
                Poll.__init__(self)
		Renderer.__init__(self)
		self.path = 'covers'
		self.nameCache = {}
		self.pics = []
		self.pixmaps = []
		self.pngname = ''
		self.png = ''
		self.picon = ePicLoad()
		self.pixdelay = 60
		self.size = []

        def applySkin(self, desktop, parent):
            atrs = []
            for atr, value in self.skinAttributes:
		if (atr == 'path'):
			self.path = value
                elif atr == 'size':
                    self.size = value.split(',')
		elif atr == "pixdelay":
			self.pixdelay = int(value)
                atrs.append((atr, value))
            self.skinAttributes = atrs
            aply = Renderer.applySkin(self, desktop, parent)
            return aply

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
				pngname = self.nameCache.get('default', '')
				if (pngname == ''):
                                        pngname = self.findPicon('picon_default')
                                        if (pngname == ''):
					    tmp = '/usr/lib/enigma2/python/Plugins/Extensions/TMBD/picon_default.png'
					    if fileExists(tmp):
						    pngname = tmp
					    self.nameCache['default'] = pngname
			if (self.pngname != pngname):
				self.pngname = pngname
				self.instance.setScale(1)
                                self.picon.setPara((int(self.size[0]), int(self.size[1]), 1, 1, False, 1, '#00000000'))
                                self.picon.startDecode(self.pngname, 0, 0, False)
                                self.png = self.picon.getData()
	                        self.instance.setPixmap(self.png)
				self.runAnim()

	def findPicon(self, serviceName):
		for path in self.searchPaths:
			pngname = (((path % self.path) + serviceName) + '.jpg')
			if fileExists(pngname):
				return pngname
		return ''

	def runAnim(self):
                txt=[]
                text = ""
                IMAGE_PATH2 = resolveFilename(SCOPE_CURRENT_SKIN, 'Movieanim')
                path2 = resolveFilename(SCOPE_SKIN_IMAGE, IMAGE_PATH2)
                if fileExists(path2):
                    l = os.listdir(path2)
                    for x in l:
                         x = os.path.join(path2, x)
                         txt.append(x)
                    text = ','.join(txt)
                    self.pixmaps = text.split(',')
		    if len(self.pics) == 0:
			for x in self.pixmaps:
				self.pics.append(loadPic(resolveFilename(SCOPE_SKIN_IMAGE, x), int(self.size[0]), int(self.size[1]), 0, 0, 0, 1))
		    self.slide = len(self.pics)
		    self.timer = eTimer()
		    self.timer.callback.append(self.timerEvent)
		    self.timer.start(self.pixdelay, True)
		else:
                    self.instance.setPixmap(self.png)
		
	def timerEvent(self):
		if self.slide > 0:
			self.timer.stop()
			self.instance.setPixmap(self.pics[len(self.pics) - self.slide])
			self.slide = self.slide - 1
			self.timer.start(self.pixdelay, True)
		else:
			self.timer.stop()
			self.instance.setPixmap(self.png)
