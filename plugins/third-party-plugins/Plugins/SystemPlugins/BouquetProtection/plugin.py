# -*- coding: utf-8 -*-
from . import _
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.ChannelSelection import ChannelSelectionBase, ChannelContextMenu
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigYesNo, ConfigPIN, ConfigInteger, ConfigNumber
from enigma import eServiceReference, eServiceCenter, eDVBDB, eTimer
from Components.ChoiceList import ChoiceEntryComponent
from Tools import Notifications
from Tools.BoundFunction import boundFunction
from Tools.Directories import resolveFilename, SCOPE_CONFIG
import BouquetProtect


baseChannelContextMenu__init__ = None
baseChannelSelectionBase__init__ = None


config.BouquetProtect = ConfigSubsection()
config.BouquetProtect.enabled = ConfigSelection(default = 'none', choices = [('none', 'no'),('bouq', 'yes')])
config.BouquetProtect.protect = ConfigSubsection()
config.BouquetProtect.protect.enable = ConfigYesNo(default = False)
config.BouquetProtect.protect.index  = ConfigPIN(default = -1)
config.BouquetProtect.protect.tries  = ConfigInteger(default = 3)
config.BouquetProtect.protect.time   = ConfigInteger(default = 3)
config.BouquetProtect.protect.store  = ConfigSelection(default = "standby", choices = [("1", _("1 minute")),("5", _("5 minutes")),("15", _("15 minutes")),("30", _("30 minutes")),("45", _("45 minutes")),("60", _("60 minutes")),("120", _("2 hours")),("180", _("3 hours")),("360", _("6 hours")),("720", _("12 hours")),("1440",_("24 hours")),("standby", _("until standby/restart"))])
config.BouquetProtect.unwanted = ConfigSubsection()
config.BouquetProtect.unwanted.enalbed = ConfigYesNo(default = False)
config.BouquetProtect.unwanted.showkey = ConfigSelection(default = 'none', choices = [('none', _('none')),('breakAudio', 'AUDIO'),('longAudio', _('long AUDIO')),('breakVideo', _('VIDEO(Vkey)')),('longVideo', _('long VIDEO(Vkey)'))])

#if config.BouquetProtect.protect.value:
#	config.ParentalControl.configured.value = False
#	config.ParentalControl.configured.save()





def newChannelContextMenu__init__(self, session, csel):
	baseChannelContextMenu__init__(self, session, csel)
	self["menu"].enableWrapAround = True
	if config.BouquetProtect.enabled.value == 'none': return
	if csel.bouquet_mark_edit != 0 or csel.movemode: return
	
	idx = max(0, len(self["menu"].list)-1)
	current = csel.getCurrentSelection()
	current_root = csel.getRoot()
	if not (current_root and current_root.getPath().find('FROM BOUQUET "bouquets.') != -1): # inBouquetRootList ?
		inBouquet = csel.getMutableList() is not None
		if not (current.flags & (eServiceReference.isMarker|eServiceReference.isDirectory)): # isPlayable ?
			if inBouquet and config.BouquetProtect.enabled.value in ('bouq'):
				if not csel.hidden_shown:
					self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("unlock protected services"), self.menuShowAllHiddenBouquetServices)))
					self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("add to bouquets protection"), boundFunction(self.menuHideCurrentService, True))))
				else:
					self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("lock protected services"), self.menuShowAllHiddenBouquetServices)))
					if current.toString() in getHiddenList():
						self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("remove from bouquets protection"), boundFunction(self.menuHideCurrentService, False))))
					else:
						self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("add to bouquets protection"), boundFunction(self.menuHideCurrentService, True))))
			elif not inBouquet and config.BouquetProtect.unwanted.enalbed.value:
				if current_root and current_root.getPath().find("flags == 2") != -1:
					self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("restore all hidden services"), boundFunction(self.menuHideUnwantedServices, False))))
					self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("restore hidden service"), boundFunction(self.menuHideUnwantedService, False))))
				else:
					self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("hide as unwanted service"), boundFunction(self.menuHideUnwantedService, True))))
			
		else:
			if config.BouquetProtect.unwanted.enalbed.value:
				if not inBouquet and current.getPath().find("PROVIDERS") == -1:
					self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("hide all as unwanted services"), boundFunction(self.menuHideUnwantedServices, True))))
	else:
		if not csel.hidden_shown:
			self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("unlock protected services"), self.menuShowAllHiddenBouquetServices)))
			self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("add to bouquets protection"), boundFunction(self.menuHideCurrentBouquet, True))))
		else:
			self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("lock protected services"), self.menuShowAllHiddenBouquetServices)))
			if current.toString() in getHiddenList():
				self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("remove from bouquets protection"), boundFunction(self.menuHideCurrentBouquet, False))))
			else:
				self["menu"].list.insert(idx, ChoiceEntryComponent(text = (_("add to bouquets protection"), boundFunction(self.menuHideCurrentBouquet, True))))

def menuHideUnwantedServices(self, hide):
	if hide:
		root = self.csel.servicelist.getCurrent()
	else:
		root = self.csel.servicelist.getRoot()
	serviceHandler = eServiceCenter.getInstance()
	servicelist = serviceHandler.list(root)
	if not servicelist is None:
		db = eDVBDB.getInstance()
		while True:
			service = servicelist.getNext()
			if not service.valid(): break
			if hide:
				db.addFlag(service, 0xfffffffd)
			else:
				db.removeFlag(service, 0x00000002)
		db.saveServicelist()
		if hide:
			self.csel.servicelist.removeCurrent()
		else:
			self.csel.showAllHiddenServices()
	self.close()

def menuHideUnwantedService(self, hide):
	if not self.csel.checkpass and not self.csel.checkProtect(boundFunction(self.menuHideUnwantedService, hide)): return
	db = eDVBDB.getInstance()
	if hide:
		ret = db.addFlag(self.csel.servicelist.getCurrent(), 0xfffffffd)
	else:
		ret = db.removeFlag(self.csel.servicelist.getCurrent(), 0x00000002)
	if ret == 0:
		db.saveServicelist()
		self.csel.servicelist.removeCurrent()
	else:
		self.session.open(MessageBox, _("Sorry, hide current service failed :("), MessageBox.TYPE_ERROR, timeout=10)
	self.close()

def menuHideCurrentBouquet(self, hide):
	if not self.csel.checkpass and not self.csel.checkProtect(boundFunction(self.menuHideCurrentBouquet, hide)): return
	ref = self.csel.servicelist.getCurrent()
	refstr = ref.toString() # + ':#'
	excludelist = ['', refstr]
	serviceHandler = eServiceCenter.getInstance()
	servicelist = serviceHandler.list(ref)
	if not servicelist is None:
		while True:
			service = servicelist.getNext()
			if not service.valid(): break
			excludelist.append( service.toString() )

	services = getHiddenList(excludelist)
	if hide:
		services += excludelist[1:]
		check = setHiddenList(services) and not self.csel.hidden_shown
	else:
		check = setHiddenList(services) # and self.csel.hidden_shown
	if check:
		db = eDVBDB.getInstance()
		filename = self.csel.mode == 0 and 'bouquets.tv' or 'bouquets.radio'
		bouquets = getBouquetsList(filename, [refstr])
		if not hide: bouquets += [refstr]
		if setBouquetsList(filename, bouquets): db.reloadBouquets()
		for cur in excludelist[2:]:
			curref = eServiceReference(cur)
			if not curref.valid(): continue
			if hide:
				db.addFlag(curref, 0xfffffffd)
			else:
				db.removeFlag(curref, 0x00000002)
		db.saveServicelist()
		self.csel.bouquetNumOffsetCache = { }
		if hide: self.csel.servicelist.removeCurrent()
	self.close()

def menuHideCurrentService(self, hide):
	if not self.csel.checkpass and not self.csel.checkProtect(boundFunction(self.menuHideCurrentService, hide)): return
	ref = self.csel.servicelist.getCurrent()
	refstr = ref.toString()
	services = getHiddenList(['', refstr])
	if hide:
		services.append(refstr)
		check = setHiddenList(services) and not self.csel.hidden_shown
	else:
		check = setHiddenList(services) # and self.csel.hidden_shown
	if check:
		db = eDVBDB.getInstance()
		if hide:
			db.addFlag(ref, 0xfffffffd)
		else:
			db.removeFlag(ref, 0x00000002)
		db.saveServicelist()
		if hide: self.csel.servicelist.removeCurrent()
	self.close()

def menuShowAllHiddenBouquetServices(self):
	if not self.csel.checkpass and not self.csel.checkProtect(self.menuShowAllHiddenBouquetServices): return
	self.csel.showAllHiddenBouquetServices()
	self.close()





def getAllHiddenList():
	list = [ ]
	try:
		f = open(resolveFilename(SCOPE_CONFIG, 'lamedb'), 'r')
		services_found = False
		while True:
			ln1 = f.readline()
			if not ln1: break
			if services_found:
				flags = 0
				ln2 = f.readline()
				if not ln2: break
				ln3 = f.readline()
				if not ln3: break
				pos = ln3.find(',f:')
				if pos != -1:
					s = ln3[pos+3:]
					pos = s.find(',')
					flags = int('0x'+s[:pos], 0x10)
				if (flags & 2):
					data = ln1.strip().split(':')
					if len(data) > 4:
						name = ln2.strip().replace('\xc2\x86', '').replace('\xc2\x87', '')
						list.append( (name, "1:0:%s:%s:%s:%s:%s:0:0:0:"%(data[4], data[0], data[2], data[3], data[1])) )
			elif ln1 == "services\n":
				services_found = True
		f.close()
	except:
		pass
	return list

def getHiddenList(exclude=['']):
	list = [ ]
	try:
		file = open(resolveFilename(SCOPE_CONFIG, 'hidelist'), 'r')
		lines = file.readlines()
		for ln in lines:
			currefstr = ln.strip()
			if currefstr[0] == "#" or currefstr in exclude: continue
			list.append(currefstr)
		file.close()
	except:
		pass
	return list

def setHiddenList(servicelist=[]):
	try:
		file = open(resolveFilename(SCOPE_CONFIG, 'hidelist'), 'w')
		file.write("")
		for service in servicelist:
			file.write(service + "\n")
		file.close()
	except:
		return False
	return True

def getBouquetsList(filename, exclude=['']):
	list = [ ]
	try:
		file = open(resolveFilename(SCOPE_CONFIG, filename), 'r')
		lines = file.readlines()
		for ln in lines:
			ln = ln.strip()
			if len(ln) < 9: continue
			if ln[:8] == '#SERVICE':
				offs = ln[8] == ':' and 10 or 9
				if ln[offs:] in exclude: continue
				list.append(ln[offs:])
			elif ln[:6] == '#NAME ':
				list.insert(0, ln)
		file.close()
	except:
		pass
	return list

def setBouquetsList(filename, bouquets=[]):
	try:
		file = open(resolveFilename(SCOPE_CONFIG, filename), 'w')
		file.write("")
		for bouquet in bouquets:
			if len(bouquet) < 9: continue
			if bouquet[:6] == '#NAME ':
				file.write(bouquet + "\r\n")
			else:
				file.write("#SERVICE " + bouquet + "\r\n")
		file.close()
	except:
		return False
	return True

def unlockAllHiddenBouquetServices(unlock):
	tv_bouquets = []
	rd_bouquets = []
	db = eDVBDB.getInstance()
	for service in getHiddenList():
		if service[2] == '7':
			pos = service.rfind(':#')
			if pos != -1:
				index = int(service[pos+2:])
				service = service[:pos]
			if service[4] == '1':
				if not tv_bouquets: tv_bouquets = getBouquetsList('bouquets.tv')
				for bq in tv_bouquets:
					if bq == service: tv_bouquets.remove(bq)
				if unlock: tv_bouquets.append(service)
			elif service[4] == '2':
				if not rd_bouquets: rd_bouquets = getBouquetsList('bouquets.radio')
				for bq in rd_bouquets:
					if bq == service: rd_bouquets.remove(bq)
				if unlock: rd_bouquets.append(service)
			continue
		ref = eServiceReference(service)
		if ref.valid():
			if unlock is True:
				db.removeFlag(ref, 0x00000002)
			else:
				db.addFlag(ref, 0xfffffffd)
	if len(tv_bouquets): setBouquetsList('bouquets.tv', tv_bouquets)
	if len(rd_bouquets): setBouquetsList('bouquets.radio', rd_bouquets)
	if len(tv_bouquets) or len(rd_bouquets): db.reloadBouquets()





def newChannelSelectionBase__init__(self, session):
	ChannelSelectionBase.inst = self
	baseChannelSelectionBase__init__(self, session)
	self.hidden_shown = config.BouquetProtect.enabled.value == 'none'
	self.checkpass = False
	self.protectTimer = eTimer()
	self.protectTimer.callback.append(self.protectTimerLoop)
	
	if config.BouquetProtect.unwanted.enalbed.value and config.BouquetProtect.unwanted.showkey.value != 'none':
		self["ChannelSelectBaseActions"].actions.update({config.BouquetProtect.unwanted.showkey.value:self.showAllHiddenServices})

def showAllHiddenBouquetServices(self):
	self.hidden_shown = not self.hidden_shown
	unlockAllHiddenBouquetServices(self.hidden_shown)
	
	ref = self.servicelist.getCurrent()
	self.bouquetNumOffsetCache = { }
	self.setRoot(self.getRoot())
	serviceHandler = eServiceCenter.getInstance()
	servicelist = serviceHandler.list(self.getRoot())
	if not servicelist is None:
		current = None
		while True:
			service = servicelist.getNext()
			if not service.valid(): break
			if current is None: current = service
			if service.toString() == ref.toString():
				current = service
				break
		if not current is None: self.servicelist.setCurrent(current)
	if not self.hidden_shown:
		hidden = getHiddenList()
		for path in self.history:
			if path[-1].toString() in hidden:
				self.history.remove(path)
		self.history_pos = max(0, len(self.history)-1)

def checkProtect(self, callback=None):
	if self.checkpass or \
	not config.BouquetProtect.protect.enable.value or \
	config.BouquetProtect.protect.index.value == config.BouquetProtect.protect.index.default:
		return True
	from Screens.InputBox import PinInput
	self.session.openWithCallback(boundFunction(self.checkProtectEntered, callback), PinInput, triesEntry = config.BouquetProtect.protect, pinList = [config.BouquetProtect.protect.index.value], title = _("please enter the password"), windowTitle = _("Bouquets Protection"))
	return self.checkpass

def checkProtectEntered(self, callback, result):
	if result:
		self.checkpass = True
		if not callback is None: callback()
		if config.BouquetProtect.protect.store.value == 'standby':
			config.misc.standbyCounter.addNotifier(self.standbyCounterCallback, initial_call = False)
		else:
			self.protectTimer.start(int(config.BouquetProtect.protect.store.value)*60*1000,True)
	else:
		if result is False:
			self.session.open(MessageBox, _("The password you entered is wrong."), MessageBox.TYPE_ERROR)

def protectTimerLoop(self):
	self.checkpass = False
	self.hidden_shown = not self.checkpass
	self.showAllHiddenBouquetServices()
	self.protectTimer.stop()

def standbyCounterCallback(self, ConfigElement):
	if config.BouquetProtect.protect.store.value == 'standby':
		self.protectTimerLoop()

def showAllHiddenServices(self):
	if self.pathChangeDisabled: return False
	if not self.checkpass and not self.checkProtect(self.showAllHiddenServices): return False
	pos = self.service_types.rfind(':')
	refstr = '%s (flags == 2) && %s ORDER BY flags' %(self.service_types[:pos+1], self.service_types[pos+1:])
	if not self.preEnterPath(refstr):
		ref = eServiceReference(refstr)
		ref.setName(_("All hidden services"))
		currentRoot = self.getRoot()
		if currentRoot is None or currentRoot != ref:
			self.clearPath()
			self.enterPath(ref, True)
			services = getAllHiddenList()
			if services: services.sort(reverse=True)
			for s in services:
				service = eServiceReference(s[1])
				if service and service.valid():
					if s[0] == "":
						info = eServiceCenter.getInstance().info(service)
						name = info and info.getName(service)
					else:
						name = s[0]
					service.setName(name)
					self.servicelist.addService(service)
			self.servicelist.finishFill()
			return True
	return False





def StartMainSession(session, **kwargs):
	global baseChannelContextMenu__init__, baseChannelSelectionBase__init__
	if baseChannelSelectionBase__init__ is None:
		baseChannelSelectionBase__init__ = ChannelSelectionBase.__init__
	ChannelSelectionBase.__init__ = newChannelSelectionBase__init__
	ChannelSelectionBase.showAllHiddenBouquetServices = showAllHiddenBouquetServices
	ChannelSelectionBase.checkProtect = checkProtect
	ChannelSelectionBase.checkProtectEntered = checkProtectEntered
	ChannelSelectionBase.protectTimerLoop = protectTimerLoop
	ChannelSelectionBase.standbyCounterCallback = standbyCounterCallback
	ChannelSelectionBase.showAllHiddenServices = showAllHiddenServices

	if baseChannelContextMenu__init__ is None:
		baseChannelContextMenu__init__ = ChannelContextMenu.__init__
	ChannelContextMenu.__init__ = newChannelContextMenu__init__
	ChannelContextMenu.menuHideCurrentBouquet = menuHideCurrentBouquet
	ChannelContextMenu.menuHideCurrentService = menuHideCurrentService
	ChannelContextMenu.menuShowAllHiddenBouquetServices = menuShowAllHiddenBouquetServices
	ChannelContextMenu.menuHideUnwantedService = menuHideUnwantedService
	ChannelContextMenu.menuHideUnwantedServices = menuHideUnwantedServices

	unlockAllHiddenBouquetServices(config.BouquetProtect.enabled.value == 'none')

def OpenBouquetProtectSetup(session, **kwargs):
	session.open(BouquetProtect.BouquetProtectSetup)

def OpenSetup(menuid, **kwargs):
	if menuid == "setup":
		return [(_("Bouquets protection"), OpenBouquetProtectSetup, "bouquet_protect_setup", 15)]
	else:
		return []


def Plugins(**kwargs):
	return [
		PluginDescriptor(name=_("Bouquets protection"), description=_("advanced parental control for user bouquets"), where = PluginDescriptor.WHERE_SESSIONSTART, fnc = StartMainSession),
		PluginDescriptor(name=_("Bouquets protection"), description=_("advanced parental control for user bouquets"), where = PluginDescriptor.WHERE_MENU, fnc = OpenSetup)
		]
