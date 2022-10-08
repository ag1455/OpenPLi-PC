# -*- coding: utf-8 -*-
from . import _
from Screens.Screen import Screen
from Screens.InputBox import PinInput
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from Components.ActionMap import NumberActionMap
from Components.config import config, getConfigListEntry, ConfigPIN, NoSave, ConfigNothing
from Components.ConfigList import ConfigListScreen
from Tools.BoundFunction import boundFunction





class BouquetProtectSetup(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["BouquetProtectSetup", "Setup"]
		self.setup_title = _("Bouquet Protection Setup")
		self.onChangedEntry = [ ]

		self["key_green"] = StaticText(_("Save"))
		self["key_red"] = StaticText(_("Cancel"))
		self["actions"] = NumberActionMap(["SetupActions"],
		{
			"cancel": self.keyRed,	# KEY_RED, KEY_ESC
			"ok": self.keyOk,	# KEY_OK
			"save": self.keyGreen,	# KEY_GREEN
		}, -1)

		ConfigListScreen.__init__(self, [])

		self.access = False
		self.BPS = config.BouquetProtect
		self.prev_enabled = self.BPS.enabled.value
		self.prev_protect = self.BPS.protect.enable.value
		self.prev_store   = self.BPS.protect.store.value
		self.prev_showkey = self.BPS.unwanted.showkey.value
		self.initConfig()
		self.createSetup()

		self["config"].onSelectionChanged.append(self.__configSelChanged)
		self.onClose.append(self.__closed)
		self.onLayoutFinish.append(self.__layoutFinished)

	def __closed(self):
		pass

	def __layoutFinished(self):
		self.setTitle(self.setup_title)
		if self["config"].getCurrentIndex() == 0:
			self["config"].setCurrentIndex(1)

	def __configSelChanged(self):
		cur = self["config"].getCurrent()
		index = self["config"].getCurrentIndex()
		if cur == self.none_entry:
			self["config"].setCurrentIndex(index+2)
		elif cur in (self.nane_entry,self.pass_entry):
			self["config"].setCurrentIndex(index-2)
		elif cur == self.nune_entry:
			self["config"].setCurrentIndex(1)

	def initConfig(self):
		self.none_entry     = getConfigListEntry("", NoSave(ConfigNothing()))
		self.nune_entry     = getConfigListEntry(_("Bouquets protection:"), NoSave(ConfigNothing()))
		self.nane_entry     = getConfigListEntry(_("Advanced:"), NoSave(ConfigNothing()))
		self.pass_entry     = getConfigListEntry(_("Password setup:"), NoSave(ConfigNothing()))
		
		self.enable_hide    = getConfigListEntry(_("enable bouquets protection"), self.BPS.enabled)
		self.enable_protect = getConfigListEntry(_("enable password on protection"), self.BPS.protect.enable)
		self.store_pass     = getConfigListEntry(_("remember entered password"), self.BPS.protect.store)
		self.setup_pass     = getConfigListEntry(_("<< setup password (4 digits) >>"), NoSave(ConfigNothing()))
		self.change_pass    = getConfigListEntry(_("<< change password >>"), NoSave(ConfigNothing()))
		
		self.unwan_enabled  = getConfigListEntry(_("hide unwanted services in channellist"), self.BPS.unwanted.enalbed)
		self.unwan_showkey  = getConfigListEntry(_("show unwanted services list on key press"), self.BPS.unwanted.showkey)

	def createSetup(self):
		list = [ self.nune_entry, self.enable_hide, self.none_entry, self.nane_entry, self.unwan_enabled ]
		if self.BPS.unwanted.enalbed.value:
			list.append(self.unwan_showkey)
		if self.BPS.enabled.value != 'none' or  self.BPS.unwanted.enalbed.value:
			list.append(self.none_entry)
			
			list.append(self.pass_entry)
			list.append(self.enable_protect)
			if self.BPS.protect.enable.value:
				list.append(self.store_pass)
				if self.BPS.protect.index.value == self.BPS.protect.index.default:
					list.append(self.setup_pass)
				else:
					list.append(self.change_pass)
		
		self["config"].list = list
		self["config"].l.setList(list)

	def newConfig(self):
		cur = self["config"].getCurrent()
		if cur in (self.enable_hide, self.enable_protect, self.unwan_enabled):
			self.createSetup()
		elif cur in (self.change_pass, self.setup_pass):
			if self.access or self.BPS.protect.index.value == self.BPS.protect.index.default:
				self.passEntered(None,True)
			else:
				self.session.openWithCallback(boundFunction(self.passEntered, None), PinInput, triesEntry = self.BPS.protect, pinList = [self.BPS.protect.index.value], title = _("please enter the old password"), windowTitle = _("Bouquet Protection Setup"))

	def passEntered(self, callback, result):
		if result:
			self.access = result
			if callback is None:
				self.session.open(PasswordSetup, self.BPS.protect.index, _("Bouquet Protection Setup"))
			else:
				callback()
		else:
			if result is False:
				self.session.open(MessageBox, _("The password you entered is wrong."), MessageBox.TYPE_ERROR)

	def keyOk(self):
		pass

	def keyRed(self):
		self.BPS.enabled.cancel()
		self.BPS.protect.enable.cancel()
		self.BPS.protect.store.cancel()
		self.BPS.unwanted.enalbed.cancel()
		self.BPS.unwanted.showkey.cancel()
		self.close()

	def keyGreen(self):
		def updateActionMap():
			from Screens.ChannelSelection import ChannelSelectionBase as CSB
			if CSB.inst["ChannelSelectBaseActions"].actions.has_key(self.prev_showkey):
				#CSB.inst["ChannelSelectBaseActions"].actions.update({self.prev_showkey:lambda:None})
				del CSB.inst["ChannelSelectBaseActions"].actions[self.prev_showkey]
			if self.BPS.unwanted.enalbed.value and self.BPS.unwanted.showkey.value != 'none':
				CSB.inst["ChannelSelectBaseActions"].actions.update({self.BPS.unwanted.showkey.value:boundFunction(CSB.showAllHiddenServices, CSB.inst)})
		
		if self.BPS.protect.enable.value and self.BPS.protect.index.value == self.BPS.protect.index.default:
			self.BPS.protect.enable.value = False
		if self.access or self.BPS.protect.index.value == self.BPS.protect.index.default or \
		(self.prev_protect == self.BPS.protect.enable.value and self.prev_protect == False):
			self.BPS.enabled.save()
			self.BPS.protect.enable.save()
			self.BPS.protect.store.save()
			self.BPS.unwanted.enalbed.save()
			self.BPS.unwanted.showkey.save()
			updateActionMap()
			self.close()
		else:
			self.session.openWithCallback(boundFunction(self.passEntered, self.keyGreen), PinInput, triesEntry = self.BPS.protect, pinList = [self.BPS.protect.index.value], title = _("please enter password"), windowTitle = _("Bouquet Protection Setup"))

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.newConfig()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.newConfig()



class PasswordSetup(Screen, ConfigListScreen):
	def __init__(self, session, pin, title = _("Change password")):
		Screen.__init__(self, session)
		self.skinName = ["PasswordSetup", "Setup"]
		self.setup_title = title
		self.onChangedEntry = [ ]

		self.pin = pin
		self.list = []
		self.pass1 = ConfigPIN(default = 1111, censor = "*")
		self.pass1.addEndNotifier(boundFunction(self.passChanged, 1))
		self.pass2 = ConfigPIN(default = 1112, censor = "*")
		self.pass2.addEndNotifier(boundFunction(self.passChanged, 2))
		self.list.append(getConfigListEntry(_("Enter new password"), NoSave(self.pass1)))
		self.list.append(getConfigListEntry(_("Reenter new password"), NoSave(self.pass2)))
		ConfigListScreen.__init__(self, self.list)
		
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["actions"] = NumberActionMap(["DirectionActions", "ColorActions", "OkCancelActions"],
		{
			"cancel": self.cancel,
			"red": self.cancel,
			"save": self.keyOK,
			"green": self.keyOK,
		}, -1)
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def passChanged(self, pin, ConfigElement):
		if pin == 1:
			self["config"].setCurrentIndex(1)
		elif pin == 2:
			self.keyOK()

	def keyOK(self):
		if self.pass1.value == self.pass2.value:
			self.pin.value = self.pass1.value
			self.pin.save()
			self.session.openWithCallback(self.close, MessageBox, _("The password has been changed successfully."), MessageBox.TYPE_INFO)
		else:
			self.session.open(MessageBox, _("The passwords you entered are different."), MessageBox.TYPE_ERROR)

	def cancel(self):
		self.close(None)

	def keyNumberGlobal(self, number):
		ConfigListScreen.keyNumberGlobal(self, number)

