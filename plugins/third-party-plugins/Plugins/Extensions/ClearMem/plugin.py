# for localized messages  	 
from . import _
#################################################################################
#
#    Plugin for Dreambox-Enigma2		ver. 1.06
#    Coded by shamann (c)2012
#    Modify by ims:
#	-translate,ngettext,getMemory,freeMemory,WHERE_PLUGINMENU,Info
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#################################################################################

from Screens.Screen import Screen
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *
from Components.ActionMap import ActionMap
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from os import system
from enigma import eTimer
from Components.ProgressBar import ProgressBar

config.plugins.ClearMem = ConfigSubsection()
config.plugins.ClearMem.enable = ConfigYesNo(default = False)
NGETTEXT = False
try:	# can be used ngettext ?
	ngettext("%d minute", "%d minutes", 5)
	NGETTEXT = True
except Exception, e:
	print "[ClearMem] ngettext is not supported:", e
	
choicelist = []
for i in range(5, 151, 5):
	if NGETTEXT:
		choicelist.append(("%d" % i, ngettext("%d minute", "%d minutes", i) % i))
	else:
		choicelist.append(("%d" % i))
config.plugins.ClearMem.timeout = ConfigSelection(default = "30", choices = choicelist)
config.plugins.ClearMem.scrinfo = ConfigYesNo(default = True)
choicelist = []
for i in range(1, 11):
	if NGETTEXT:
		choicelist.append(("%d" % i, ngettext("%d second", "%d seconds", i) % i))
	else:
		choicelist.append(("%d" % i))
config.plugins.ClearMem.timescrinfo = ConfigSelection(default = "10", choices = choicelist)
config.plugins.ClearMem.where = ConfigSelection(default = "0", choices = [("0",_("plugins")),("1",_("menu-system")),("2",_("extensions")),("3",_("event info"))])
cfg = config.plugins.ClearMem

# display mem, used, free and progressbar
ALL = 0x17

def clearMem():
	system("sync")
	system("echo 3 > /proc/sys/vm/drop_caches")

def startSetup(menuid, **kwargs):
	if menuid != "system":
		return [ ]
	return [(_("Setup ClearMem"), main, "ClearMem", None)]

def sessionAutostart(reason, **kwargs):
	if reason == 0:
		ClearMemAuto.startClearMem(kwargs["session"])

def Plugins(path, **kwargs):
	name = _("ClearMem")
	descr = _("Automatic clearing memory")
	list = [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionAutostart),]
	if cfg.where.value == "0":
		list.append(PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_PLUGINMENU, needsRestart = True, icon = 'plugin.png', fnc=main))
	elif cfg.where.value == "1":
		list.append(PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_MENU, needsRestart = True, fnc=startSetup))
	elif cfg.where.value == "2":
		list.append(PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_EXTENSIONSMENU, needsRestart = True, fnc=main))
	elif cfg.where.value == "3":
		list.append(PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_EVENTINFO, needsRestart = True, fnc=main))
	return list

def main(session,**kwargs):
	session.open(SetupMenu)

class SetupMenu(Screen, ConfigListScreen):

	skin = """
	<screen name="ClearMem" position="center,center" size="500,215" title="" backgroundColor="#31000000" >
		<widget name="config" position="10,10" size="480,125" zPosition="1" transparent="0" backgroundColor="#31000000" scrollbarMode="showOnDemand" />
		<widget name="memory" position="10,145" zPosition="2" size="480,24" valign="center" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />
		<widget name="slide" position="10,170" zPosition="2" borderWidth="1" size="480,8" backgroundColor="dark" />
		<ePixmap pixmap="skin_default/div-h.png" position="0,183" zPosition="2" size="500,2" />
		<widget name="key_red" position="0,187" zPosition="2" size="120,30" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />
		<widget name="key_green" position="120,187" zPosition="2" size="120,30" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
		<widget name="key_yellow" position="240,187" zPosition="2" size="120,30" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="yellow" />
		<widget name="key_blue" position="360,187" zPosition="2" size="120,30" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="blue" />
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)

		self.onChangedEntry = [ ]
		self.list = [ ]
		ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)
		self.setup_title = _("Setup ClearMem")
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.keyCancel,
				"green": self.keySave,
				"ok": self.keySave,
				"red": self.keyCancel,
				"blue": self.freeMemory,
				"yellow": self.memoryInfo,
			}, -2)

		self["key_green"] = Label(_("Save"))
		self["key_red"] = Label(_("Cancel"))
		self["key_blue"] = Label(_("Clear Now"))
		self["key_yellow"] = Label(_("Info"))

		self["slide"] = ProgressBar()
		self["slide"].setValue(100)
		self["slide"].hide()
		self["memory"] = Label()

		self.runSetup()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(_("Setup ClearMem"))
		self["memory"].setText(self.getMemory(ALL))

	def runSetup(self):
		self.list = [ getConfigListEntry(_("Enable ClearMem"), cfg.enable) ]
		if cfg.enable.value:
			autotext = _("Auto timeout:")
			timetext = _("Time of info message:")
			if not NGETTEXT:
				autotext = _("Auto timeout (5-150min):")
				timetext = _("Time of info message (1-10sec):")
			self.list.extend((
				getConfigListEntry(autotext, cfg.timeout),
				getConfigListEntry(_("Show info on screen:"), cfg.scrinfo),
				getConfigListEntry(timetext, cfg.timescrinfo),
				getConfigListEntry(_("Display plugin in:"), cfg.where),
			))

		self["config"].list = self.list
		self["config"].setList(self.list)

	def keySave(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()
		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		if self["config"].getCurrent()[1] == cfg.enable:
			self.runSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		if self["config"].getCurrent()[1] == cfg.enable:
			self.runSetup()

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def freeMemory(self):
		clearMem()
		self["memory"].setText(self.getMemory(ALL))

	def getMemory(self, par=0x01):
		try:
			mm = mu = mf = 0
			for line in open('/proc/meminfo','r'):
				line = line.strip()
				if "MemTotal:" in line:
					line = line.split()
					mm = int(line[1])
				if "MemFree:" in line:
					line = line.split()
					mf = int(line[1])
					break
			mu = mm - mf
			self["memory"].setText("")
			self["slide"].hide()
			memory = ""
			if par&0x01:
				memory += "".join((_("Memory:")," %d " % (mm/1024),_("MB"),"  "))
			if par&0x02:
				memory += "".join((_("Used:")," %.2f%s" % (100.*mu/mm,'%'),"  "))
			if par&0x04:
				memory += "".join((_("Free:")," %.2f%s" % (100.*mf/mm,'%')))
			if par&0x10:
				self["slide"].setValue(int(100.0*mu/mm+0.25))
				self["slide"].show()
			return memory
		except Exception, e:
			print "[ClearMem] getMemory FAIL:", e
			return ""

	def memoryInfo(self):
		self.session.openWithCallback(self.afterInfo, ClearMemInfoScreen)

	def afterInfo(self, answer=False):
		self["memory"].setText(self.getMemory(ALL))

class ClearMemAutoMain():
	def __init__(self):
		self.dialog = None

	def startClearMem(self, session):
		self.dialog = session.instantiateDialog(ClearMemAutoScreen)
		self.makeShow()

	def makeShow(self):
		if cfg.scrinfo.value:
			self.dialog.show()
		else:
			self.dialog.hide()

ClearMemAuto = ClearMemAutoMain()

class ClearMemAutoScreen(Screen):

	skin = """<screen name="ClearMemAutoScreen" position="830,130" zPosition="10" size="250,30" title="ClearMem Status" backgroundColor="#31000000" >
			<widget name="message_label" font="Regular;24" position="0,0" zPosition="2" valign="center" halign="center" size="250,30" backgroundColor="#31000000" transparent="1" />
		</screen>"""
                        
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skin = ClearMemAutoScreen.skin
		self['message_label'] = Label(_("Starting"))
		self.ClearMemTimer = eTimer()
		self.ClearMemTimer.timeout.get().append(self.__makeWhatYouNeed)
		self.ClearMemWatchDog = eTimer()
		self.ClearMemWatchDog.timeout.get().append(self.__chckState)
		self.showTimer = eTimer()
		self.showTimer.timeout.get().append(self.__endShow)
		self.state = None
		self.onLayoutFinish.append(self.__chckState)
 		self.onShow.append(self.__startsuspend)

	def __startsuspend(self):
		self.setTitle(_("ClearMem Status"))
		if self.showTimer.isActive():
			self.showTimer.stop()
		self.showTimer.start(int(cfg.timescrinfo.value) * 1000)		
	
	def __chckState(self):
		def subStart():
			if cfg.enable.value:
				self.state = cfg.enable.value
				self.ClearMemTimer.start(int(cfg.timeout.value)*60000)
				self['message_label'].setText(_("Started"))
			else:
				self['message_label'].setText(_("Stopped"))
			if cfg.scrinfo.value and ClearMemAuto.dialog is not None:
				ClearMemAuto.dialog.show()
		self.ClearMemWatchDog.stop()
		if self.instance and cfg.enable.value != self.state:
			if self.ClearMemTimer.isActive():
				self.ClearMemTimer.stop()
			subStart()
		self.ClearMemWatchDog.start(int(cfg.timescrinfo.value) * 1000)
		
	def __makeWhatYouNeed(self):
		self.ClearMemTimer.stop()
		clearMem()
		if self.instance:
			self['message_label'].setText(_("Mem cleared"))
			if cfg.scrinfo.value and ClearMemAuto.dialog is not None:
				ClearMemAuto.dialog.show()
		self.ClearMemTimer.start(int(cfg.timeout.value)*60000)

	def __endShow(self):
		self.showTimer.stop()
		ClearMemAuto.dialog.hide()

class ClearMemInfoScreen(Screen):
	skin = """<screen name="ClearMemInfoScreen" position="center,center" zPosition="2" size="400,580" title="ClearMem Info" backgroundColor="#31000000" >
			<widget name="memtext" font="Regular;18" position="10,0" zPosition="2" valign="center" halign="left" size="230,550" backgroundColor="#31000000" transparent="1" />
			<widget name="memvalue" font="Regular;18" position="250,0" zPosition="2" valign="center" halign="right" size="140,550" backgroundColor="#31000000" transparent="1" />
			<ePixmap pixmap="skin_default/div-h.png" position="0,550" zPosition="2" size="400,2" />
			<widget name="key_red" position="10,552" zPosition="2" size="130,28" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="red" />
			<widget name="key_green" position="130,552" zPosition="2" size="130,28" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
			<widget name="key_blue" position="260,552" zPosition="2" size="130,28" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="blue" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setup_title = _("ClearMem Info")
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"blue": self.freeMemory,
				"green": self.getMemInfo,
			}, -2)

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Refresh"))
		self["key_blue"] = Label(_("Clear Now"))

		self['memtext'] = Label()
		self['memvalue'] = Label()
		self.setTitle(_("ClearMem Info"))
		self.onLayoutFinish.append(self.getMemInfo)

	def getMemInfo(self):
		try:
			text = ""
			value = ""
			for line in open('/proc/meminfo','r'):
				line = line.strip().split()
				print line
				text += "".join((line[0],"\n"))
				value += "".join((line[1]," ",line[2],"\n"))
			self['memtext'].setText(text)
			self['memvalue'].setText(value)

		except Exception, e:
			print "[ClearMem] getMemory FAIL:", e

	def freeMemory(self):
		clearMem()
		self.getMemInfo()

	def cancel(self):
		self.close()
