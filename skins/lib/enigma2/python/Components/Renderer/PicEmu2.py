# -*- coding: utf-8 -*-
# coders Nikolasi
from Tools.LoadPixmap import LoadPixmap
from Components.Pixmap import Pixmap
from Renderer import Renderer
from enigma import ePixmap, loadPic, eTimer, iServiceInformation, iPlayableService, eDVBFrontendParametersSatellite, eDVBFrontendParametersCable
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Components.config import *
from Components.Converter.Poll import Poll

class PicEmu2(Renderer, Poll):
    searchPaths = ('/usr/share/enigma2/%s/', '/media/ba/%s/', '/media/hdd/%s/', '/media/sda1/%s/', '/media/sda/%s/', '/media/usb/%s/')

    def __init__(self):
        Poll.__init__(self)
        Renderer.__init__(self)
        self.piconWidth = 150
        self.piconHeight = 90
        self.path = 'picon'
        self.nameCache = {}
        self.nameCache1 = {}
        self.pngname = ''
        self.pngname1 = ''
        self.timerpicsPS1 = eTimer()
        self.timerpicsPS1.callback.append(self.timerpicsPSEvent1)

    def applySkin(self, desktop, parent):
        attribs = []
        for attrib, value in self.skinAttributes:
            if attrib == 'path':
                self.path = value
            elif attrib == 'piconWidth':
                self.piconWidth = int(value)
            elif attrib == 'piconHeight':
                self.piconHeight = int(value)
            else:
                attribs.append((attrib, value))
        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        self.poll_interval = 3000
        self.poll_enabled = True        
        sname = ''
        if self.instance:
            pngname = ''    
            if what[0] != self.CHANGED_CLEAR:
                service = self.source.service
                if service:
                    info = (service and service.info())
                    if info:
                        caids = info.getInfoObject(iServiceInformation.sCAIDs)
                        self.path = 'PiconCam'
                        sname = self.camPicon()
			if caids:
                            if (len(caids) > 0):
                                for caid in caids:
                                    caid = self.int2hex(caid)
                                    if (len(caid) == 3):
                                        caid = ("0%s" % caid)
                                    caid = caid[:2]
                                    caid = caid.upper()
                                    if (caid != "") and (sname == ""):
                                            sname = "Unknown"                        
                        pngname = self.nameCache.get(sname, '')
                        if pngname == '':
                            pngname = self.findPicon(sname)
                            if pngname != '':
                                self.nameCache[sname] = pngname
                        if pngname == '':
                            pngname = self.nameCache.get('Fta', '')
                            if pngname == '':
                                pngname = self.findPicon('Fta')
                                if pngname == '':
                                    tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
                                    if fileExists(tmp):
                                        pngname = tmp
                                    else:
                                        pngname = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_default.png')
                                self.nameCache['default'] = pngname
                        if self.pngname != pngname:
                            self.pngname = pngname
                        if SCOPE_CURRENT_SKIN:
                                if caids:
                                     sname = self.criptPicon(caids)
                                pngname1 = self.nameCache1.get(sname, '')
                                self.path = 'cript'
                                if pngname1 == '':
                                    pngname1 = self.findPicon(sname)
                                    if pngname1 != '':
                                        self.nameCache1[sname] = pngname1
                                if pngname1 == '':
                                    pngname1 = self.nameCache1.get('none', '')
                                    if pngname1 == '':
                                        pngname1 = self.findPicon('none')
                                        if pngname1 == '':
                                            tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
                                            if fileExists(tmp):
                                                pngname1 = tmp
                                            else:
                                                pngname1 = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_default.png')
                                        self.nameCache1['default'] = pngname1
                                if self.pngname1 != pngname1:
                                    self.pngname1 = pngname1
                                self.runanim1(pngname, pngname1)

    def camPicon(self):
	    control = 0 
            cfgfile = "/tmp/ecm.info"
            sname = ""
            content = ""
            if fileExists(cfgfile):
                try:
                    f = open(cfgfile, "r")
                    content = f.read()
                    f.close()
                except:
                    content = ""
                if content != '':   
                    contentInfo = content.split("\n")
                    for line in contentInfo:
                        if ("=====" in line):
                                control = 1 
                        if ("using" in line):
                                sname = "CCcam"
                        elif ("source" in line) and control == 0:
                                sname = "Mgcamd"
                        elif ("reader" in line):
                                sname = "OScam"
                        elif ("source" in line) and control == 1 or ('Service:'in line):
                                sname = "Wicardd"
                        elif ("Internal" in line):
                                sname = "Gbox"
                        elif ("FROM:" in line):
                                sname = "Camd3"
                        elif ("slot" in line) or ("Local" in line):
                                sname = "Card"                                
                else:
                    sname = "Unknown"                                
            else:
                 sname = ""
            return sname

    def criptPicon(self, caids):
            sname = "none"
	    if caids:
                if (len(caids) > 0):
                    for caid in caids:
                        caid = self.int2hex(caid)
                        if (len(caid) == 3):
                           caid = ("0%s" % caid)
                        caid = caid[:2]
                        caid = caid.upper()
                        if (caid == "26"):
                            sname = "BiSS"
                        elif (caid == "01"):
                            sname = "SEC"
                        elif (caid == "06"):
                            sname = "IRD"
                        elif (caid == "17"):
                            sname = "BET"
                        elif (caid == "05"):
                            sname = "VIA"
                        elif (caid == "18"):
                            sname = "NAG"
                        elif (caid == "09"):
                            sname = "NDS"
                        elif (caid == "0B"):
                            sname = "CONN"
                        elif (caid == "0D"):
                            sname = "CRW"
                        elif (caid == "4A"):
                            sname = "DRE"
                        elif (caid == "27"):
                            sname = "EXSET"                            
                    return sname
                
    def int2hex(self, int):
            return ("%x" % int)
                

    def findPicon(self, serviceName):
        for path in self.searchPaths:
            pngname = path % self.path + serviceName + '.png'
            if fileExists(pngname):
                return pngname

        return ''

    def runanim1(self, pic1, pic2):
        self.slide = 2
        self.steps = 9
        self.pics = []
        self.pics.append(loadPic(pic1, self.piconWidth, self.piconHeight, 0, 0, 0, 1))
        self.pics.append(loadPic(pic2, self.piconWidth, self.piconHeight, 0, 0, 0, 1))
        self.timerpicsPS1.start(100, True)

    def timerpicsPSEvent1(self):
            if self.steps == 0:
                self.steps = 9
            self.timerpicsPS1.stop()
            self.instance.setPixmap(self.pics[self.slide - 1])
            self.steps = self.steps - 1
            self.slide = self.slide - 1
            if self.slide == 0:
                self.slide = 2
            self.timerpicsPS1.start(1000, True)
 
