# -*- coding: utf-8 -*-
#
# This plugin is open source but it is NOT free software.
#
# This plugin may only be distributed to and executed on hardware which
# is licensed by Dream Multimedia GmbH.
# In other words:
# It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
# to hardware which is NOT licensed by Dream Multimedia GmbH.
# It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
# on hardware which is NOT licensed by Dream Multimedia GmbH.
#
from Components.ActionMap import *
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmap, MultiContentEntryPixmapAlphaTest
from Components.config import config
from Components.GUIComponent import GUIComponent
from enigma import ePicLoad
from Components.Pixmap import Pixmap, MovingPixmap
from Tools.LoadPixmap import LoadPixmap
from Tools import Notifications
from Components.AVSwitch import AVSwitch
from Screens.InfoBar import MoviePlayer
from Components.PluginComponent import plugins
from Components.PluginList import PluginEntryComponent, PluginList
from Components.Button import Button
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor

from Components.ServicePosition import ServicePositionGauge
from Tools.NumericalTextInput import NumericalTextInput
from Components.ConfigList import *
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigText, getConfigListEntry, ConfigSelection, ConfigPIN

from Screens.HelpMenu import HelpableScreen
from Screens.InputBox import InputBox
from Screens.InputBox import PinInput
from Screens.ChoiceBox import ChoiceBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.BoundFunction import boundFunction
from Screens.InfoBarGenerics import InfoBarChannelSelection
from enigma import eListboxPythonMultiContent, eListbox, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, loadPNG, RT_WRAP, eServiceReference, getDesktop, loadJPG
from Tools.Directories import pathExists, fileExists, SCOPE_SKIN_IMAGE, resolveFilename
import sys, os, base64, re, time, sha, shutil, inspect
from dirSelect import dirSelectDlg1

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
    lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
    os_environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
    gettext.bindtextdomain("navibar", resolveFilename(SCOPE_PLUGINS, "Extensions/navibar/locale"))

def _(txt):
    t = gettext.dgettext("navibar", txt)
    if t == txt:
        print "[navibar] fallback to default translation for", txt
        t = gettext.gettext(txt)
    return t

localeInit()
language.addCallback(localeInit)

found_new = False
version="1.9-mod_tr"
###########################
### mod by shadowrider ####
### speedup by jadne ######
### thanks at dirtylion ###
###########################


# config settings
config.plugins.navibar = ConfigSubsection()
config.plugins.navibar.hits = ConfigSelection(default="1", choices = [("0",_("abc")),("1",_("hits")),("2",_("own"))])
config.plugins.navibar.placesize = ConfigSelection(default="450", choices = [("0",_("0")),("50",_("50")),("100",_("100")),("150",_("150")),("200",_("200")),("250",_("250")),("300",_("300")),("350",_("350")),("400",_("400")),("450",_("450")),("500",_("500")),("525",_("525")),("550",_("550")),("575",_("575"))])
config.plugins.navibar.fontsize = ConfigSelection(default="24", choices = [("22",_("22")),("24",_("24")),("26",_("26")),("28",_("28"))])
config.plugins.navibar.transparent = ConfigYesNo(default=False)
config.plugins.navibar.blue = ConfigYesNo(default=True)
config.plugins.navibar.close1 = ConfigYesNo(default=True)
config.plugins.navibar.which = ConfigSelection(default="bar", choices = [("bar",_("bar")),("wall",_("wall"))])
config.plugins.navibar.pw = ConfigPIN(default = 0000)
config.plugins.navibar.dlpath = ConfigText(default = "/usr/lib/enigma2/python/Plugins/Extensions/navibar/icons")

class mylist(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setFont(0, gFont("Regular", 14))
		self.l.setFont(1, gFont("Regular", 16))
		self.l.setFont(2, gFont("Regular", 18))
		self.l.setFont(3, gFont("Regular", 17))
		self.l.setFont(4, gFont("Regular", 22))
		self.l.setFont(5, gFont("Regular", 24))
		self.l.setFont(6, gFont("Regular", 26))
		self.l.setFont(7, gFont("Regular", 20))
		self.l.setFont(8, gFont("Regular", 19))

class navibar_config1(Screen, ConfigListScreen, HelpableScreen):
	skin = """
		<screen position="center,center" size="800,455" title="NaviBar Setup">
			<widget name="config" position="25,5" size="750,125" scrollbarMode="showOnDemand" />
			<eLabel position="0,138" size="800,3" zPosition="10" backgroundColor="#aaaaaa"/>
			<widget name="config2" position="5,145" size="610,245" scrollbarMode="showOnDemand" />
			<widget name="label_green" position="180,429" size="120,39" zPosition="2" backgroundColor="#404040" font="Regular;20"/>
			<widget name="label_red" position="375,429" size="120,39" zPosition="2" backgroundColor="#404040" font="Regular;20"/>
			<widget name="label_blue" position="260,429" size="160,39" zPosition="2" backgroundColor="#404040" font="Regular;20"/>
			<widget name="balken" position="10,425" size="800,30" valign="center" backgroundColor="#404040" font="Regular;20"/>
			<widget name="config3" position="620,145" size="180,245" scrollbarMode="showOnDemand" />
			<widget name="descrip2" position="10,395" valign="center" halign="left" zPosition="2" size="610,24" backgroundColor="#404040" font="Regular;20" />
			<widget name="pic_red" pixmap="~/images/button_red.png" zPosition="3" position="340,427" size="35,25" alphatest="blend" />
			<widget name="pic_green" pixmap="~/images/button_green.png" position="145,427" size="35,25" alphatest="blend" />
			<widget name="pic_blue" pixmap="~/images/button_blue.png" position="220,427" zPosition="2" size="35,25" alphatest="blend" />
			<widget name="ok" position="620,427" size="35,25" pixmap="~/images/button_ok.png" zPosition="2" alphatest="blend" />
			<widget name="info" position="580,427" size="35,25" pixmap="~/images/button_info.png" zPosition="2" alphatest="blend" />
			<widget name="pvr" position="500,427" size="35,25" pixmap="~/images/button_pvr.png" zPosition="2" alphatest="blend" />
			<widget name="menu" position="540,427" size="35,25" pixmap="~/images/button_menu.png" zPosition="2" alphatest="blend" />
			<ePixmap  position="660,427" size="35,25" pixmap="~/images/button_bouquet.png" alphatest="blend" />
			<ePixmap  position="730,427" size="35,25" pixmap="~/images/button_help.png" alphatest="blend" />
		</screen>"""

	def __init__(self, session, plugin_path):
		Screen.__init__(self, session)
		self.plugin_path = plugin_path
		self.skin_path = plugin_path
		self.session = session
		self.setTitle(_("NaviBar Setup ")+version)
		HelpableScreen.__init__(self)
		self.list = []
		self["config2"] = mylist([])
		self["config3"] = mylist([])
		self["descrip2"] = Label()
		self["balken"] = Label("  "+_("Settings"))
		self["label_green"] = Label(_("Add"))
		self["label_red"] = Label(_("Delete"))
		self["label_blue"] = Label(_("Rename"))
		self["descrip2"].hide()
		self["label_green"].hide()
		self["label_red"].hide()
		self["label_blue"].hide()
		self["pic_red"] = Pixmap()
		self["pic_green"] = Pixmap()
		self["pic_blue"] = Pixmap()
		self["info"] = Pixmap()
		self["ok"] = Pixmap()
		self["pvr"] = Pixmap()
		self["menu"] = Pixmap()
		self["pic_red"].hide()
		self["pic_green"].hide()
		self["pic_blue"].hide()
		self["info"].hide()
		self["menu"].hide()
		self["pvr"].hide()

		self.selected = False
		self.move_on = False
		self.select_screen = 1
		ConfigListScreen.__init__(self, self.list)

		self.list.append(getConfigListEntry(_("Plugins sortieren nach:"), config.plugins.navibar.hits))
		self.list.append(getConfigListEntry(_("NaviBar mit Blue Button starten (enigma2 neustart erforderlich!):"), config.plugins.navibar.blue))
		self.list.append(getConfigListEntry(_("NaviBar Text groesse:"), config.plugins.navibar.fontsize))
		self.list.append(getConfigListEntry(_("NaviBar Position:"), config.plugins.navibar.placesize))
		self.list.append(getConfigListEntry(_("NaviBar Transparent:"), config.plugins.navibar.transparent))
		self.list.append(getConfigListEntry(_("NaviBar Style:"), config.plugins.navibar.which))
		self.list.append(getConfigListEntry(_("NaviBar automatisch schliessen:"), config.plugins.navibar.close1))
		self.list.append(getConfigListEntry(_("Icons Path:"), config.plugins.navibar.dlpath))

		self["config"].setList(self.list)

		self["shortcuts"] = NumberActionMap(["ShortcutActions", "WizardActions", "NumberActions", "InputActions", "InputAsciiActions", "KeyboardInputActions" ],
		{
			"up":		self.up,
			"down":		self.down,
			"right":	self.right,
			"left":		self.left,
		}, -1)

		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
		{
			"cancel":	(self.saveConfig,_("Save and close")),
			"ok":		(self.change_hide,_("Set Pic-Folder / Change/Hide Plugin")),
		}, -1)

		self["EPGSelectActions"] = HelpableActionMap(self, "EPGSelectActions",
		{
			"input_date_time":	(self.switchtpw,_("Password on/off")),
			"red":			(self.del_section,_("Delete Section")),
			"blue":			(self.change_descrip,_("Change Description")),
			"timerAdd":		(self.add_section,_("Add Section")),
			"info":			(self.select,_("Manually sort")),
			"nextBouquet":		(self.cup,_("Next list")),
			"prevBouquet":		(self.cdown,_("Previous list")),
		}, -1)

		self["InfobarActions"] = HelpableActionMap(self, "InfobarActions",
		{
			"showMovies":		(self.change_section,_("Change Section")),
		}, -1)

		self.readconfig()
		self.readsections()
		self.onLayoutFinish.append(self.startup)

	def startup(self):
		self["config2"].instance.setSelectionEnable(0)
		self["config3"].instance.setSelectionEnable(0)

	def right(self):
		if self.select_screen == 1:
			self["config"].handleKey(KEY_RIGHT)
		elif self.select_screen == 2:
			self["config2"].pageDown()
		elif self.select_screen == 3:
			self["config3"].pageDown()

	def left(self):
		if self.select_screen == 1:
			self["config"].handleKey(KEY_LEFT)
		elif self.select_screen == 2:
			self["config2"].pageUp()
		elif self.select_screen == 3:
			self["config3"].pageUp()

	def cup(self):
		self["descrip2"].setText("")
		if self.select_screen == 1:
			self.select_screen = 3
			self.screen3a()
		elif self.select_screen == 2:
			self.select_screen = 1
			self.screen1a()
		elif self.select_screen == 3:
			self.select_screen = 2
			self.screen2a()
		print self.select_screen

	def cdown(self):
		self["descrip2"].setText("")
		if self.select_screen == 1:
			self.select_screen = 2
			self.screen2a()
		elif self.select_screen == 2:
			self.select_screen = 3
			self.screen3a()
		elif self.select_screen == 3:
			self.select_screen = 1
			self.screen1a()
		print self.select_screen

	def screen1a(self):
			self["info"].hide()
			self["menu"].hide()
			self["pvr"].hide()
			self["ok"].show()
			self["label_green"].hide()
			self["label_red"].hide()
			self["label_blue"].hide()
			self["pic_red"].hide()
			self["pic_green"].hide()
			self["pic_blue"].hide()
			self["descrip2"].hide()
			self["balken"].setText("  "+_("Settings"))
			self["config3"].instance.setSelectionEnable(0)
			self["config"].instance.setSelectionEnable(1)

	def screen2a(self):  #pluginlist
			self["descrip2"].show()
			self["pic_red"].hide()
			self["ok"].show()
			self["pic_green"].hide()
			self["pic_blue"].show()
			self["info"].show()
			self["menu"].show()
			self["pvr"].show()
			self["balken"].setText("  "+_("Plugins"))
			self["label_green"].hide()
			self["label_red"].hide()
			self["label_blue"].show()
			self["config"].instance.setSelectionEnable(0)
			self["config2"].instance.setSelectionEnable(1)
			self.textset()
	def screen3a(self):  #sections
			self["info"].hide()
			self["menu"].hide()
			self["pvr"].hide()
			self["ok"].hide()
			self["pic_red"].show()
			self["pic_green"].show()
			self["balken"].setText("  "+_("Sections"))
			self["pic_blue"].hide()
			self["label_blue"].hide()
			self["label_green"].show()
			self["label_red"].show()
			self["descrip2"].hide()
			self["config2"].instance.setSelectionEnable(0)
			self["config3"].instance.setSelectionEnable(1)

	def textset(self):  #sections
			if len(self["config2"].getCurrent()[0][6]):
                            self["descrip2"].setText("  Name:  "+self["config2"].getCurrent()[0][6])
			else:
                            self["descrip2"].setText("  Name:  "+self["config2"].getCurrent()[0][0])

	def up(self):
		if self.select_screen == 1:
			if self["config"].getCurrentIndex() <= len(self["config"].list)-1:
				idx = int(self["config"].getCurrentIndex())-1
				self["config"].setCurrentIndex(idx)
		elif self.select_screen == 2:
			self["config2"].up()
			self.textset()
		elif self.select_screen == 3:
			self["config3"].up()

	def down(self):
		if self.select_screen == 1:
			if len(self["config"].list)-1 > self["config"].getCurrentIndex() and not len(self["config"].list)-1 == self["config"].getCurrentIndex():
				print self["config"].getCurrentIndex
				idx = idx = int(self["config"].getCurrentIndex())+1
				self["config"].setCurrentIndex(idx)
		elif self.select_screen == 2:
			self["config2"].down()
			self.textset()
		elif self.select_screen == 3:
			self["config3"].down()

	def readconfig(self):
		config_read = open(self.plugin_path+"/config2" , "r")
		self.config_list = []
		self.config_list_select = []
		for line in config_read.readlines():
			ok = re.findall('"(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)"', line, re.S)
			if ok:
				(name, hits, hide, sort, pw, section, descrip) = ok[0]
				self.config_list_select.append((name, hits, hide, sort, pw, section, descrip))
		config_read.close()

		self.config_list_select.sort(key=lambda x: int(x[3]))

		for each in self.config_list_select:
			(name, hits, hide, sort, pw, section, descrip) = each
			self.config_list.append(self.show_menu(name, hits, hide, sort, pw, section, descrip))
		self["config2"].l.setList(self.config_list)
		self["config2"].l.setItemHeight(22)

	def show_menu(self, name, hits, hide, sort, pw, section, descrip):
		res = [(name, hits, hide, sort, pw, section, descrip)]
		if int(hide) == 0:
			res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 2), size=(20, 20), png=loadPNG(self.plugin_path+"/images/green.png")))
		else:
			res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 2), size=(20, 20), png=loadPNG(self.plugin_path+"/images/red.png")))
		if int(pw) == 1:
			res.append(MultiContentEntryPixmapAlphaTest(pos=(40, 2), size=(20, 20), png=loadPNG(self.plugin_path+"/images/lock.png")))
		res.append(MultiContentEntryText(pos=(100, 0), size=(390, 22), font=8, text=name, flags=RT_HALIGN_LEFT))
		res.append(MultiContentEntryText(pos=(490, 0), size=(120, 22), font=8, text=section, flags=RT_HALIGN_LEFT))
		if self.selected and name == self.last_plugin_name:
			res.append(MultiContentEntryPixmapAlphaTest(pos=(70, 2), size=(20, 20), png=loadPNG(self.plugin_path+"/images/move.png")))
		return res

	def readsections(self):
		section_read = open(self.plugin_path+"/sections" , "r")
		self.section_list = []
		self.section_list_select = []
		for line in section_read.readlines():
			ok = re.findall('"(.*?)"', line, re.S)
			if ok:
				(section_name) = ok[0]
				self.section_list_select.append(section_name)
				#self.config_list.append(self.show_menu(name, hits, hide, sort))
		section_read.close()

		self.section_list_select.sort()
		#self.config_list_select.reverse()
		
		for each in self.section_list_select:
			(section_name) = each
			self.section_list.append(self.show_menu_section(section_name))
		self["config3"].l.setList(self.section_list)
		self["config3"].l.setItemHeight(22)

	def show_menu_section(self, section_name):
		res = [(section_name)]
		res.append(MultiContentEntryText(pos=(0, 0), size=(180, 22), font=7, text=section_name, flags=RT_HALIGN_LEFT))
		return res

	def change_section(self):
		if self.select_screen == 2:
			item = self["config2"].getCurrent()
			if item:
				list_name = item[0][0]
				section_name = item[0][5]
				print self.next_item(section_name, self.section_list_select)
				next_name = self.next_item(section_name, self.section_list_select)
				config_read = open(self.plugin_path+"/config2" , "r")
				config_tmp = open(self.plugin_path+"/config_tmp" , "w")
				for line in config_read.readlines():
					ok = re.findall('"(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)"', line, re.S)
					if ok:
						(name, hits, hide, sort, pw, section, descrip) = ok[0]
						if list_name.lower() == name.lower():
							config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits , hide, sort, pw, next_name, descrip))
						else:
							config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits , hide, sort, pw, section, descrip))
				config_tmp.close()
				config_read.close()
				shutil.move(self.plugin_path+"/config_tmp", self.plugin_path+"/config2")
				self.readconfig()

	def next_item(sel, item, list):
		count = len(list)
		idx = 0
		for each in list:
			if each == item:
				idx += 1
				break
			else:
				idx += 1

		if count == idx:
			return list[0]
		else:
			return list[int(idx)]

	def change_hide(self):
		if self.select_screen == 2:
			item = self["config2"].getCurrent()
			if item:
				list_name = item[0][0]
				print list_name
				config_read = open(self.plugin_path+"/config2" , "r")
				config_tmp = open(self.plugin_path+"/config_tmp" , "w")
				for line in config_read.readlines():
					ok = re.findall('"(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)"', line, re.S)
					if ok:
						(name, hits, hide, sort, pw, section, descrip) = ok[0]
						if list_name.lower() == name.lower():
							if int(hide) == 0:
								config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits , "1", sort, pw, section, descrip))
							else:
								config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits , "0", sort, pw, section, descrip))
						else:
							config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits , hide, sort, pw, section, descrip))
				config_tmp.close()
				config_read.close()
				shutil.move(self.plugin_path+"/config_tmp", self.plugin_path+"/config2")
				self.readconfig()

		elif self.select_screen == 1:
			print "open select dir.."
			self.openDirSelectScreen()

	def del_section(self):
		if self.select_screen == 3:
			item = self["config3"].getCurrent()
			if item:
				list_name = item[0]
				if not list_name == "main":
					print "Navibar: del section ->", list_name
					section_read = open(self.plugin_path+"/sections" , "r")
					section_tmp = open(self.plugin_path+"/sections_tmp" , "w")
					for line in section_read.readlines():
						ok = re.findall('"(.*?)"', line, re.S)
						if ok:
							(name) = ok[0]
							if not list_name.lower() == name.lower():
								section_tmp.write('"%s"\n' % (name))
					section_tmp.close()
					section_read.close()
					shutil.move(self.plugin_path+"/sections_tmp", self.plugin_path+"/sections")
					self.readsections()

	def add_section(self):
		if self.select_screen == 3:
			self.session.openWithCallback(self.write_section, VirtualKeyBoard, title = _("Enter section name:"))

	def write_section(self, section_name = None):
		if not section_name == None:
			print "Navibar: add section ->", section_name
			section = open(self.plugin_path+"/sections" , "a")
			section.write('"%s"\n' % (section_name))
			section.close()
			self.readsections()

	def change_descrip(self):
		if self.select_screen == 2:
			item = self["config2"].getCurrent()[0][6]
                        self.session.openWithCallback(self.write_descrip, VirtualKeyBoard, title = _("Enter Plugin description:"),text=item)

	def write_descrip(self, descrip1 = None):
		if not descrip1 == None:
			item = self["config2"].getCurrent()
			if item:
				list_name = item[0][0]
				print list_name
				config_read = open(self.plugin_path+"/config2" , "r")
				config_tmp = open(self.plugin_path+"/config_tmp" , "w")
				for line in config_read.readlines():
					ok = re.findall('"(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)"', line, re.S)
					if ok:
						(name, hits, hide, sort, pw, section, descrip) = ok[0]
						if list_name.lower() == name.lower():
							config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits , "0", sort, pw, section, descrip1))
						else:
							config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits , hide, sort, pw, section, descrip))
				config_tmp.close()
				config_read.close()
				shutil.move(self.plugin_path+"/config_tmp", self.plugin_path+"/config2")
				self["descrip2"].setText(descrip1)
                                self.readconfig()

	def select(self):
		if self.select_screen == 2:
			if not self.selected:
				self.last_plugin_name = self["config2"].getCurrent()[0][0]
				self.last_plugin_hits = self["config2"].getCurrent()[0][1]
				self.last_plugin_hide = self["config2"].getCurrent()[0][2]
				self.last_plugin_pw = self["config2"].getCurrent()[0][4]
				self.last_plugin_section = self["config2"].getCurrent()[0][5]
				self.last_plugin_descrip = self["config2"].getCurrent()[0][6]
				print self.last_plugin_name
				self.selected = True
				self.readconfig()
			else:
				self.now_plugin_name = self["config2"].getCurrent()[0][0]
				self.now_newidx = [y[0] for y in self.config_list_select].index(self.now_plugin_name)
				count_move = 0
				config_tmp = open(self.plugin_path+"/config_tmp" , "w")
				for each in self.config_list_select:
					(name, hits, hide, sort, pw, section, descrip) = each
					if name == self.last_plugin_name:
						continue
					elif int(self.now_newidx) == int(count_move):
						print "MOVED:", self.last_plugin_name, count_move
						config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (self.last_plugin_name, self.last_plugin_hits , self.last_plugin_hide, count_move, self.last_plugin_pw, self.last_plugin_section, self.last_plugin_descrip))
						count_move += 1

					print each[0], count_move
					config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits, hide, count_move, pw, section, descrip))
					count_move += 1

				config_tmp.close()
				shutil.move(self.plugin_path+"/config_tmp", self.plugin_path+"/config2")
				self.selected = False
				self.readconfig()

	def switchtpw(self):
		if self.select_screen == 2:
			item = self["config2"].getCurrent()
			if item:
				list_name = item[0][0]
				locked = item[0][4]
				print list_name
				if int(locked) == 1:
					lock_key = int(time.strftime("%d%m"))
					self.session.openWithCallback(self.pin_callback, PinInput, pinList = [(lock_key)], triesEntry = self.getTriesEntry(), title = _("Please enter the correct pin code"), windowTitle = _("Enter pin code"))
				else:
					self.switch_lock()

	def getTriesEntry(self):
		return config.ParentalControl.retries.setuppin

	def pin_callback(self, pin):
		if pin:
			self.switch_lock()

	def switch_lock(self):
		item = self["config2"].getCurrent()
		if item:
			list_name = item[0][0]
			config_read = open(self.plugin_path+"/config2" , "r")
			config_tmp = open(self.plugin_path+"/config_tmp" , "w")
			for line in config_read.readlines():
				ok = re.findall('"(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)"', line, re.S)
				if ok:
					(name, hits, hide, sort, pw, section, descrip) = ok[0]
					if list_name.lower() == name.lower():
						if int(pw) == 0:
							config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits , hide, sort, "1", section, descrip))
						else:
							config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits , hide, sort, "0", section, descrip))
					else:
						config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits , hide, sort, pw, section, descrip))
			config_tmp.close()
			config_read.close()
			shutil.move(self.plugin_path+"/config_tmp", self.plugin_path+"/config2")
			self.readconfig()

	def openDirSelectScreen(self):
		self.session.openWithCallback(self.dirSelectDlgClosed, dirSelectDlg1, "/media/dummy/", False)  # just add any (not even existing) subdir to start in /media

	def dirSelectDlgClosed(self, directory):
		if directory != False:
			config.plugins.navibar.dlpath.value = directory

	def saveConfig(self):
		print "save"
		for x in self["config"].list:
			print x[1]
			x[1].save()
		self.close()

	def exit(self):
		print "closen"
		self.close()

from Tools.BoundFunction import boundFunction
import inspect

class navi_wall(Screen):
	def __init__(self, session, plugin_path, pluginlist, section, sectionlist):
		self.plugin_path = plugin_path
		self.skin_path = plugin_path
		self.session = session
		self.pluginlist_old = pluginlist
		self.section = section
		self.sectionlist = sectionlist
		#print "Navobar:", self.section, self.sectionlist

		self.dump_list = []
		for each in self.pluginlist_old:
			(plugin_start, name, hits, hide, sort, pw, section, descrip) = each
			#if any(item == each[5] for item in self.sectionlist):
			if each[6] == self.section:
				#print each[1]
				self.dump_list.append((plugin_start, name, hits, hide, sort, pw, section, descrip))

		# skin stuff
		self.textcolor = "#FFFFFF"
		if config.plugins.navibar.transparent.value:
			self.color = "#FF000000"
		else:
			self.color = "#30000000"

		self.fontsize = config.plugins.navibar.fontsize.value
		self.placesize = config.plugins.navibar.placesize.value
		
		self.pluginlist = self.dump_list
		self.plugin_counting = len(self.pluginlist)
		self.widget_list()

		skincontent = ""
		count_pages = self.count_mainlist + 1
		#print count_pages
		pagebar_size = int(count_pages) * 30
		#print pagebar_size
		ok = 720 - int(pagebar_size)
		#print ok
		start_pagebar = int(ok) / 2
		#print start_pagebar
		for x in range(1,len(self.mainlist)+1):
			#print x, start_pagebar
			normal = 572
			skincontent += "<widget name=\"page" + str(x) + "\" position=\"" + str(start_pagebar) + "," + str(normal) + "\" size=\"18,18\" zPosition=\"2\" transparent=\"1\" alphatest=\"blend\" />"
			skincontent += "<widget name=\"page_sel" + str(x) + "\" position=\"" + str(start_pagebar) + "," + str(normal) + "\" size=\"18,18\" zPosition=\"2\" transparent=\"1\" alphatest=\"blend\" />"
			start_pagebar += 30

		posx = 25
		posy = 20
		for x in range(1,len(self.pluginlist)+1):
			if x == 6 or x == 11 or x == 16 or x == 26 or x == 31 or x == 36 or x == 46 or x == 51 or x == 56 or x == 66 or x == 71 or x == 76 or x == 86 or x == 91 or x == 96:
				posx = 25
				posy += 135
			elif x == 21 or x == 41 or x == 61 or x == 81 or x == 101:
				posx = 25
				posy = 20
			#print "zeile", x, posx, posy
			skincontent += "<widget name=\"zeile" + str(x) + "\" position=\"" + str(posx) + "," + str(posy) + "\" size=\"100,100\" zPosition=\"2\" transparent=\"1\" alphatest=\"blend\" />"
			posx += 135

		self.skin = "<screen position=\"center,center\" size=\"700,600\" flags=\"wfNoBorder\" backgroundColor=\"" + self.color + "\" title=\"\"><eLabel position=\"0,55\" zPosition=\"0\" size=\"1280,120\" backgroundColor=\"" + self.color + "\" /><widget name=\"frame\" position=\"0,0\" size=\"110,115\" pixmap=\"~/images/sel.png\" zPosition=\"5\" alphatest=\"blend\" /><widget name=\"info\" position=\"0,535\" size=\"700,30\" valign=\"center\" halign=\"center\" zPosition=\"10\" font=\"Regular;" + self.fontsize + "\" transparent=\"1\" backgroundColor=\"#000000\" /><widget name=\"disc\" position=\"0,378\" size=\"610,20\" valign=\"center\" halign=\"center\" zPosition=\"10\" font=\"Regular;19\" transparent=\"1\" />" + skincontent + "</screen>"
		Screen.__init__(self, session)

		self["frame"] = MovingPixmap()
		self["info"] = Label("")
		self["disc"] = Label("")

		# paint icons
		for x in range(1,len(self.pluginlist)+1):
			#print "zeile",x
			self["zeile"+str(x)] = Pixmap()
			self["zeile"+str(x)].show()

		# paint page icons
		for x in range(1,len(self.mainlist)+1):
			#print "page2",x
			self["page"+str(x)] = Pixmap()
			self["page"+str(x)].show()
			self["page_sel"+str(x)] = Pixmap()
			self["page_sel"+str(x)].show()

		self.count_mainlist = len(self.mainlist)
		print "Navibar:", self.mainlist, self.count_mainlist

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MovieSelectionActions"],
		{
			"cancel":		self.exit,
			"ok":			self.ok,
			"left":			self.left,
			"right":		self.right,
			"contextMenu":	self.navibar_config,
			"up":			self.up,
			"down":		self.down
		}, -1)

		self["EPGSelectActions"] = HelpableActionMap(self, "EPGSelectActions",
		{
			"nextBouquet":		self.cup,
			"prevBouquet":		self.cdown,
		}, -1)

		# navifations stuff
		self.startpoint = 1
		self.select_list = 0

		self.onFirstExecBegin.append(self._onFirstExecBegin)
		#self.onLayoutFinish.append(self.speedup)

	def _onFirstExecBegin(self):
		# move to first icon
		self.start_selector()

		# load plugin icons
		for x in range(1,len(self.pluginlist)+1):
		#for x in range(1,len(self.mainlist[0])+1):
			postername = self.pluginlist[int(x)-1][1]
			#poster_path = "%s/icons/%s.png" % (self.plugin_path, postername.replace(' ','_'))
			#print config.plugins.navibar.dlpath.value
			poster_path = "%s/%s.png" % (config.plugins.navibar.dlpath.value, postername.replace(' ','_'))

			postername_check = ("%s" % postername)
			if postername_check in self.sectionlist:
				if not fileExists(poster_path):
					poster_path = "%s/images/no_icon_folder.png" % (self.plugin_path)

			elif not fileExists(poster_path):
				poster_path = "%s/images/no_icon.png" % (self.plugin_path)
			#print "postername:", postername, poster_path
			self["zeile"+str(x)].instance.setPixmap(None)
			self["zeile"+str(x)].hide()
			pic = LoadPixmap(cached=True, path=poster_path)
			if pic != None:
				self["zeile"+str(x)].instance.setPixmap(pic)
				if x <= 20:
					self["zeile"+str(x)].show()

		for x in range(1,len(self.mainlist)+1):
			poster_path = "%s/images/page_select.png" % (self.plugin_path)
			#print "postername:", postername, poster_path
			self["page_sel"+str(x)].instance.setPixmap(None)
			self["page_sel"+str(x)].hide()
			pic = LoadPixmap(cached=True, path=poster_path)
			if pic != None:
				self["page_sel"+str(x)].instance.setPixmap(pic)
				if x == 1:
					self["page_sel"+str(x)].show()

		for x in range(1,len(self.mainlist)+1):
			poster_path = "%s/images/page.png" % (self.plugin_path)
			self["page"+str(x)].instance.setPixmap(None)
			self["page"+str(x)].hide()
			pic = LoadPixmap(cached=True, path=poster_path)
			if pic != None:
				self["page"+str(x)].instance.setPixmap(pic)
				if x > 1:
					self["page"+str(x)].show()

	def left(self):
		print "[NaviBar]: Position:", self.startpoint, self.select_list
		print self.mainlist[int(self.select_list)]
		if not self.startpoint <= 1:
			self.startpoint -= 1
			dumppoint = self.startpoint
			self.startpoint = self.mainlist[int(self.select_list)][int(self.startpoint)-1]
			print self.startpoint
			self.paint_sel()
			self.startpoint = dumppoint
			print self.startpoint

	def right(self):
		print "[NaviBar]: Position:", self.startpoint, self.mainlist, self.select_list, len(self.mainlist[int(self.select_list)])
		if self.startpoint < 20 and self.startpoint != len(self.mainlist[int(self.select_list)]):
			self.startpoint += 1
			dumppoint = self.startpoint
			self.startpoint = self.mainlist[int(self.select_list)][int(self.startpoint)-1]
			print self.startpoint
			self.paint_sel()
			self.startpoint = dumppoint
			print self.startpoint

	def up(self):
		print "[NaviBar]: Position:", self.startpoint, self.select_list
		if self.startpoint >= 6:
			self.startpoint -= 5
			dumppoint = self.startpoint
			self.startpoint = self.mainlist[int(self.select_list)][int(self.startpoint)-1]
			print self.startpoint
			self.paint_sel()
			self.startpoint = dumppoint
			print self.startpoint

	def down(self):
		print "[NaviBar]: Position:", self.startpoint
		if self.startpoint <= 15 and not self.startpoint+5 > len(self.mainlist[int(self.select_list)]):
			self.startpoint += 5
			dumppoint = self.startpoint
			self.startpoint = self.mainlist[int(self.select_list)][int(self.startpoint)-1]
			print self.startpoint
			self.paint_sel()
			self.startpoint = dumppoint
			print self.startpoint
		else:
			self.startpoint = len(self.mainlist[int(self.select_list)])
			self.paint_sel()

	def cup(self):
		print self.select_list, len(self.mainlist)
		print "++"
		#if len(self.mainlist) > 0 and not self.select_list == 0:
		if len(self.mainlist) > 0 and self.select_list+1 < len(self.mainlist):
			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: hide zeile%s " % x
				self["zeile"+str(x)].hide()

			self["page_sel"+str(self.select_list+1)].hide()
			self["page"+str(self.select_list+1)].show()
			self.select_list += 1
			self["page"+str(self.select_list+1)].hide()
			self["page_sel"+str(self.select_list+1)].show()

			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: show zeile%s " % x
				self["zeile"+str(x)].show()

			#self.startpoint += 20
			print self.startpoint
			if self.startpoint > len(self.mainlist[int(self.select_list)]):
				self.startpoint = len(self.mainlist[int(self.select_list)])
				self.paint_sel()
				print self.startpoint
			else:
				self.paint_sel()

	def cdown(self):
		print "--"
		print self.select_list, len(self.mainlist)
		#if len(self.mainlist) > 0 and not self.select_list == len(self.mainlist):
		if len(self.mainlist) > 0 and not self.select_list == 0:
			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: hide zeile%s " % x
				self["zeile"+str(x)].hide()

			self["page_sel"+str(self.select_list+1)].hide()
			self["page"+str(self.select_list+1)].show()
			self.select_list -= 1
			self["page"+str(self.select_list+1)].hide()
			self["page_sel"+str(self.select_list+1)].show()

			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: show zeile%s " % x
				self["zeile"+str(x)].show()

			#self.startpoint -= 20
			#if self.startpoint > len(self.mainlist[int(self.select_list)]):
			#self.startpoint = len(self.mainlist[int(self.select_list)])
			#self.paint_sel()
			#else:
			self.paint_sel()

	def start_selector(self):
                pname = self.pluginlist[int(self.startpoint)-1][1]
                if len(self.pluginlist[int(self.startpoint)-1])>6:
                   if len(self.pluginlist[int(self.startpoint)-1][7]):
                       pname = str(self.pluginlist[int(self.startpoint)-1][7])
		self["info"].setText(pname)
		self.title = pname
		position = self["zeile1"].instance.position()
		self["frame"].moveTo(int(position.x()-5), int(position.y()-5), 1)
		self["frame"].show()
		self["frame"].startMoving()

	def widget_list(self):
		count = 1
		counting = 1
		self.mainlist = []
		list_dummy = []

		for x in range(1,int(self.plugin_counting)+1):
			if count == 20:
				count += 1
				counting += 1
				list_dummy.append(x)
				self.mainlist.append(list_dummy)
				count = 1
				list_dummy = []
			else:
				count += 1
				counting += 1
				list_dummy.append(x)
				if int(counting) == int(self.plugin_counting)+1:
					self.mainlist.append(list_dummy)

		self.count_mainlist = len(self.mainlist)
		print "Navibar:", self.mainlist, self.count_mainlist

	def paint_sel(self):
                pname = self.pluginlist[int(self.startpoint)-1][1]
                if len(self.pluginlist[int(self.startpoint)-1])>6:
                   if len(self.pluginlist[int(self.startpoint)-1][7]):
                       pname = str(self.pluginlist[int(self.startpoint)-1][7])
		self["info"].setText(pname)
		self.title = pname
		position = self["zeile"+str(self.startpoint)].instance.position()
		self["frame"].moveTo(int(position.x()-5), int(position.y()-5), 1)
		self["frame"].show()
		self["frame"].startMoving()

	def navibar_config(self):
		self.session.openWithCallback(self.reload, navibar_config1, plugin_path)

	def reload(self):
		print config.plugins.navibar.hits.value
		self.close(self.session, "restart")

	def ok(self):
		dumppoint = self.startpoint
		self.startpoint = self.mainlist[int(self.select_list)][int(self.startpoint)-1]
		print "lock", int(self.pluginlist[int(self.startpoint)-1][5])
		print time.strftime("%d%m")
		if int(self.pluginlist[int(self.startpoint)-1][5]) == 1:
			lock_key = int(time.strftime("%d%m"))
			self.startpoint = dumppoint
			self.session.openWithCallback(self.pin_callback, PinInput, pinList = [(lock_key)], triesEntry = self.getTriesEntry(), title = _("Please enter the correct pin code"), windowTitle = _("Enter pin code"))
		else:
			self.startpoint = dumppoint
			self.starte_plugin()

	def getTriesEntry(self):
		return config.ParentalControl.retries.setuppin

	def pin_callback(self, pin):
		print "JAAA:", pin
		if pin:
			self.starte_plugin()

	def backdana(self, bli, blu):
		print self.select_list, self.startpoint

	def starte_plugin(self):
		dumppoint = self.startpoint
		self.startpoint = self.mainlist[int(self.select_list)][int(self.startpoint)-1]
		plugin_name_old = self.pluginlist[int(self.startpoint)-1]
		print "section:", plugin_name_old[1], self.sectionlist
		plugin_name = ("%s" % plugin_name_old[1])
		print plugin_name, self.select_list, self.startpoint
		if plugin_name in self.sectionlist:
			if any(item[6] == plugin_name_old[1] for item in self.pluginlist_old):
				self.startpoint = dumppoint
				self.session.openWithCallback(self.backdana, navi_wall, plugin_path, self.pluginlist_old, plugin_name_old[1], self.sectionlist)
			else:
				self.session.open(MessageBox, "This section have no plugins added! Press Menu", type = MessageBox.TYPE_INFO,timeout = 3)
				self.startpoint = dumppoint
				print "Navibar: this section have no plugins added.."
		else:
			## schreibe plugin aufrufe.. hits..
			config_read = open(self.plugin_path+"/config2" , "rw")
			config_tmp = open(self.plugin_path+"/config.tmp2" , "w")
			for line in config_read.readlines():
				ok = re.findall('"(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)"', line, re.S)
				if ok:
					(name, hits, hide, sort, pw, section, descrip) = ok[0]
					if self.pluginlist[int(self.startpoint)-1][1] == name:
						hits = int(hits) + 1
						config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits, hide, sort, pw, section, descrip))
					else:
						config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits, hide, sort, pw, section, descrip))
			config_read.close()
			config_tmp.close()
			shutil.move(self.plugin_path+"/config.tmp2", self.plugin_path+"/config2")

			#starte plugin
			plugin = self.pluginlist[int(self.startpoint)-1][0]
			self.startpoint = dumppoint
			if config.plugins.navibar.close1.value:
                            self.close(self.session, plugin)
			else:
                            plugin[1]()
	def exit(self):
		self.close(self.session, "exit")

class navi_bar(Screen):
	def __init__(self, session, plugin_path, pluginlist, section, sectionlist):
		self.plugin_path = plugin_path
		self.skin_path = plugin_path
		self.session = session
		self.pluginlist_old = pluginlist
		self.section = section
		self.sectionlist = sectionlist
		#print "Navobar:", self.section, self.sectionlist

		self.dump_list = []
		for each in self.pluginlist_old:
			(plugin_start, name, hits, hide, sort, pw, section, descrip) = each
			#if any(item == each[5] for item in self.sectionlist):
			if each[6] == self.section:
				#print each[1]
				self.dump_list.append((plugin_start, name, hits, hide, sort, pw, section, descrip))

		# skin stuff
		self.textcolor = "#FFFFFF"
		if config.plugins.navibar.transparent.value:
			self.color = "#FF000000"
		else:
			self.color = "#30000000"

		self.fontsize = config.plugins.navibar.fontsize.value
		self.placesize = config.plugins.navibar.placesize.value

		self.pluginlist = self.dump_list
		self.plugin_counting = len(self.pluginlist)
		self.widget_list()

		# create widgets
		skincontent = ""
		count_pages = self.count_mainlist + 1
		#print count_pages
		pagebar_size = int(count_pages) * 30
		#print pagebar_size
		ok = 1300 - int(pagebar_size)
		#print ok
		start_pagebar = int(ok) / 2
		#print start_pagebar
		for x in range(1,len(self.mainlist)+1):
			#print x, start_pagebar
			normal = 150
			skincontent += "<widget name=\"page" + str(x) + "\" position=\"" + str(start_pagebar) + "," + str(normal) + "\" size=\"18,18\" zPosition=\"2\" transparent=\"1\" alphatest=\"blend\" />"
			skincontent += "<widget name=\"page_sel" + str(x) + "\" position=\"" + str(start_pagebar) + "," + str(normal) + "\" size=\"18,18\" zPosition=\"2\" transparent=\"1\" alphatest=\"blend\" />"
			start_pagebar += 30

		posx = 50
		posy = 5
		for x in range(1,len(self.pluginlist)+1):
			if x == 10 or x == 19 or x == 28 or x == 37 or x == 46 or x == 55 or x == 64 or x == 73 or x == 82 or x == 91:
				posx = 50
			#print "zeile", x, posx, posy
			skincontent += "<widget name=\"zeile" + str(x) + "\" position=\"" + str(posx) + "," + str(posy) + "\" size=\"100,100\" zPosition=\"2\" transparent=\"1\" alphatest=\"blend\" />"
			posx += 135

		self.skin = "<screen position=\"center," + self.placesize +"\" size=\"1280,200\" flags=\"wfNoBorder\" backgroundColor=\"transparent\" title=\"\"><eLabel position=\"0,55\" zPosition=\"0\" size=\"1280,120\" backgroundColor=\"" + self.color + "\" /><widget name=\"frame\" position=\"0,0\" size=\"110,115\" pixmap=\"~/images/sel.png\" zPosition=\"5\" alphatest=\"blend\" /><widget name=\"info\" position=\"0,115\" size=\"1280,30\" valign=\"center\" halign=\"center\" zPosition=\"10\" font=\"Regular;" + self.fontsize + "\" transparent=\"1\" backgroundColor=\"#000000\" /><widget name=\"disc\" position=\"0,378\" size=\"610,20\" valign=\"center\" halign=\"center\" zPosition=\"10\" font=\"Regular;19\" transparent=\"1\" />" + skincontent + "</screen>"
		Screen.__init__(self, session)

		self["frame"] = MovingPixmap()
		self["info"] = Label("")
		self["disc"] = Label("")

		# paint icons
		for x in range(1,len(self.pluginlist)+1):
			#print "zeile",x
			self["zeile"+str(x)] = Pixmap()
			self["zeile"+str(x)].show()

		# paint page icons
		for x in range(1,len(self.mainlist)+1):
			#print "page2",x
			self["page"+str(x)] = Pixmap()
			self["page"+str(x)].show()
			self["page_sel"+str(x)] = Pixmap()
			self["page_sel"+str(x)].show()

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MovieSelectionActions"],
		{
			"cancel":		self.exit,
			"ok":			self.ok,
			"left":			self.left,
			"right":		self.right,
			"contextMenu":	self.navibar_config,
			"up":			self.up,
			"down":			self.down
		}, -1)

		# navifations stuff
		self.startpoint = 1
		self.select_list = 0

		# restart if new plugin found
		if found_new:
			print "Navibar: reSTART..."
			global found_new
			found_new = False
			self.close(self.session, "restart")

		self.onFirstExecBegin.append(self._onFirstExecBegin)
		#self.onLayoutFinish.append(self.speedup)

	def _onFirstExecBegin(self):
		# move to first icon
		self.start_selector()

		# load plugin icons
		for x in range(1,len(self.pluginlist)+1):
		#for x in range(1,len(self.mainlist[0])+1):
			postername = self.pluginlist[int(x)-1][1]
			#poster_path = "%s/icons/%s.png" % (self.plugin_path, postername.replace(' ','_'))
			#print config.plugins.navibar.dlpath.value
			poster_path = "%s/%s.png" % (config.plugins.navibar.dlpath.value, postername.replace(' ','_'))

			postername_check = ("%s" % postername)
			if postername_check in self.sectionlist:
				if not fileExists(poster_path):
					poster_path = "%s/images/no_icon_folder.png" % (self.plugin_path)

			elif not fileExists(poster_path):
				poster_path = "%s/images/no_icon.png" % (self.plugin_path)
			#print "postername:", postername, poster_path
			self["zeile"+str(x)].instance.setPixmap(None)
			self["zeile"+str(x)].hide()
			pic = LoadPixmap(cached=True, path=poster_path)
			if pic != None:
				self["zeile"+str(x)].instance.setPixmap(pic)
				if x <= 9:
					self["zeile"+str(x)].show()

		for x in range(1,len(self.mainlist)+1):
			poster_path = "%s/images/page_select.png" % (self.plugin_path)
			#print "postername:", postername, poster_path
			self["page_sel"+str(x)].instance.setPixmap(None)
			self["page_sel"+str(x)].hide()
			pic = LoadPixmap(cached=True, path=poster_path)
			if pic != None:
				self["page_sel"+str(x)].instance.setPixmap(pic)
				if x == 1:
					self["page_sel"+str(x)].show()

		for x in range(1,len(self.mainlist)+1):
			poster_path = "%s/images/page.png" % (self.plugin_path)
			self["page"+str(x)].instance.setPixmap(None)
			self["page"+str(x)].hide()
			pic = LoadPixmap(cached=True, path=poster_path)
			if pic != None:
				self["page"+str(x)].instance.setPixmap(pic)
				if x > 1:
					self["page"+str(x)].show()

	def speedup(self):
		for x in range(10,len(self.pluginlist)+1):
			postername = self.pluginlist[int(x)-1][1]
			#poster_path = "%s/icons/%s.png" % (self.plugin_path, postername.replace(' ','_'))
			#print config.plugins.navibar.dlpath.value
			poster_path = "%s/%s.png" % (config.plugins.navibar.dlpath.value, postername.replace(' ','_'))

			if not fileExists(poster_path):
				poster_path = "%s/images/no_icon.png" % (self.plugin_path)

			#self["zeile"+str(x)].instance.setPixmap(None)
			#self["zeile"+str(x)].hide()
			#sc = AVSwitch().getFramebufferScale()
			#self.picload = ePicLoad()
			#size = self["zeile"+str(x)].instance.size()
			#self.picload.setPara((size.width(), size.height(), sc[0], sc[1], False, 1, "#FF000000")) # Backgroun
			#if self.picload.startDecode(poster_path, 0, 0, False) == 0:
			#	ptr = self.picload.getData()
			#	if ptr != None:
			#		self["zeile"+str(x)].instance.setPixmap(ptr)
			self["zeile"+str(x)].instance.setPixmapFromFile(poster_path)
			self["zeile"+str(x)].hide()

		for x in range(1,len(self.mainlist)+1):
			if x == 1:
				poster_path = "%s/images/page_select.png" % (self.plugin_path)
				#self["page_sel"+str(x)].instance.setPixmap(None)
				#self["page_sel"+str(x)].hide()
				#sc = AVSwitch().getFramebufferScale()
				#self.picload = ePicLoad()
				#size = self["page_sel"+str(x)].instance.size()
				#self.picload.setPara((size.width(), size.height(), sc[0], sc[1], False, 1, "#FF000000")) # Backgroun
				#if self.picload.startDecode(poster_path, 0, 0, False) == 0:
				#	ptr = self.picload.getData()
				#	if ptr != None:
				#		self["page_sel"+str(x)].instance.setPixmap(ptr)
				#		self["page_sel"+str(x)].show()
				self["page_sel"+str(x)].instance.setPixmapFromFile(poster_path)
				self["page_sel"+str(x)].show()

		for x in range(1,len(self.mainlist)+1):
			if x > 1:
				poster_path = "%s/images/page.png" % (self.plugin_path)
				#self["page"+str(x)].instance.setPixmap(None)
				#self["page"+str(x)].hide()
				#sc = AVSwitch().getFramebufferScale()
				#self.picload = ePicLoad()
				#size = self["page"+str(x)].instance.size()
				#self.picload.setPara((size.width(), size.height(), sc[0], sc[1], False, 1, "#FF000000")) # Backgroun
				#if self.picload.startDecode(poster_path, 0, 0, False) == 0:
				#	ptr = self.picload.getData()
				#	if ptr != None:
				#		self["page"+str(x)].instance.setPixmap(ptr)
				#		self["page"+str(x)].show()
				self["page"+str(x)].instance.setPixmapFromFile(poster_path)
				self["page"+str(x)].show()

	def widget_list(self):
		count = 1
		counting = 1
		self.mainlist = []
		list_dummy = []

		for x in range(1,int(self.plugin_counting)+1):
			if count == 9:
				count += 1
				counting += 1
				list_dummy.append(x)
				self.mainlist.append(list_dummy)
				count = 1
				list_dummy = []

			else:
				count += 1
				counting += 1
				list_dummy.append(x)
				if int(counting) == int(self.plugin_counting)+1:
					self.mainlist.append(list_dummy)

		self.count_mainlist = len(self.mainlist)
		print "Navibar:", self.mainlist, self.count_mainlist

	def start_selector(self):
                pname = self.pluginlist[int(self.startpoint)-1][1]
                if len(self.pluginlist[int(self.startpoint)-1])>6:
                   if len(self.pluginlist[int(self.startpoint)-1][7]):
                       pname = str(self.pluginlist[int(self.startpoint)-1][7])

		#pname = self.pluginlist[int(self.startpoint)-1][1]
		self["info"].setText(pname)
		self.title = pname
		position = self["zeile1"].instance.position()
		self["frame"].moveTo(int(position.x()-5), int(position.y()-5), 1)
		self["frame"].show()
		self["frame"].startMoving()

	def left(self):
		print "Navibar:", self.startpoint
		if int(self.startpoint) > 1:
			self.startpoint -= 1
			print "Navibar: -", self.startpoint

			if int(self.startpoint) == 9 or int(self.startpoint) == 18 or int(self.startpoint) == 27 or int(self.startpoint) == 36 or int(self.startpoint) == 45 or int(self.startpoint) == 54 or int(self.startpoint) == 63 or int(self.startpoint) == 72 or int(self.startpoint) == 81:
				print "Navibar: go to last page", self.select_list+1, self.select_list, self.count_mainlist
				if self.select_list > 0:
					self.paint_sel()
					for x in self.mainlist[int(self.select_list)]:
						#print "Navibar: hide zeile%s " % x
						self["zeile"+str(x)].hide()

					self["page_sel"+str(self.select_list+1)].hide()
					self["page"+str(self.select_list+1)].show()
					self.select_list -= 1
					self["page"+str(self.select_list+1)].hide()
					self["page_sel"+str(self.select_list+1)].show()

					for x in self.mainlist[int(self.select_list)]:
						#print "Navibar: show zeile%s " % x
						self["zeile"+str(x)].show()
			else:
				print "Navibar: movie selector"
				self.paint_sel()
		else:
			self.startpoint = int(self.plugin_counting)
			self.paint_sel()
			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: hide zeile%s " % x
				self["zeile"+str(x)].hide()

			self["page_sel"+str(self.select_list+1)].hide()
			self["page"+str(self.select_list+1)].show()
			self.select_list = self.count_mainlist-1
			self["page"+str(self.select_list+1)].hide()
			self["page_sel"+str(self.select_list+1)].show()
			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: show zeile%s " % x
				self["zeile"+str(x)].show()

	def right(self):
		print "Navibar:", self.startpoint
		if not int(self.startpoint) == int(self.plugin_counting):
			self.startpoint += 1
			print "Navibar: +", self.startpoint

			if int(self.startpoint) == 10 or int(self.startpoint) == 19 or int(self.startpoint) == 28 or int(self.startpoint) == 37 or int(self.startpoint) == 46 or int(self.startpoint) == 55 or int(self.startpoint) == 64 or int(self.startpoint) == 73 or int(self.startpoint) == 82:
				print "Navibar: go to next page", self.select_list+1, self.select_list+2, self.count_mainlist
				if not int(self.select_list) == int(self.count_mainlist)-1:
					self.paint_sel()
					for x in self.mainlist[int(self.select_list)]:
						#print "Navibar: hide zeile%s " % x
						self["zeile"+str(x)].hide()

					self["page_sel"+str(self.select_list+1)].hide()
					self["page"+str(self.select_list+1)].show()
					self.select_list += 1
					self["page"+str(self.select_list+1)].hide()
					self["page_sel"+str(self.select_list+1)].show()

					for x in self.mainlist[int(self.select_list)]:
						#print "Navibar: show zeile%s " % x
						self["zeile"+str(x)].show()
			else:
				"Navibar: movie selector"
				self.paint_sel()
		else:
			self.startpoint = 1
			self.paint_sel()
			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: hide zeile%s " % x
				self["zeile"+str(x)].hide()

			self["page_sel"+str(self.select_list+1)].hide()
			self["page"+str(self.select_list+1)].show()
			self.select_list = 0
			self["page"+str(self.select_list+1)].hide()
			self["page_sel"+str(self.select_list+1)].show()

			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: show zeile%s " % x
				self["zeile"+str(x)].show()

	def up(self):
		print "up"
		print "Navibar:", self.startpoint
		if not int(self.startpoint)+9 > int(self.plugin_counting) and not int(self.select_list) == int(self.count_mainlist)-1:
			self.startpoint += 9
			print "Navibar: +", self.startpoint
			print "Navibar: go to next page", self.select_list, self.select_list+1, self.count_mainlist
			self.paint_sel()
			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: hide zeile%s " % x
				self["zeile"+str(x)].hide()

			self["page_sel"+str(self.select_list+1)].hide()
			self["page"+str(self.select_list+1)].show()
			self.select_list += 1
			self["page"+str(self.select_list+1)].hide()
			self["page_sel"+str(self.select_list+1)].show()

			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: show zeile%s " % x
				self["zeile"+str(x)].show()
		else:
			self.startpoint = int(self.mainlist[-1][-1])
			self.paint_sel()
			print "Navibar: +", self.startpoint
			print "Navibar: go to next page", self.select_list+1, self.select_list+2, self.count_mainlist
			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: hide zeile%s " % x
				self["zeile"+str(x)].hide()

			self["page_sel"+str(self.select_list+1)].hide()
			self["page"+str(self.select_list+1)].show()
			self.select_list = self.count_mainlist-1
			self["page"+str(self.select_list+1)].hide()
			self["page_sel"+str(self.select_list+1)].show()

			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: show zeile%s " % x
				self["zeile"+str(x)].show()

	def down(self):
		print "down"
		print "Navibar:", self.startpoint
		if int(self.startpoint)-9 > 0:
			self.startpoint -= 9
			print "Navibar: go to last page", self.select_list+1, self.select_list, self.count_mainlist
			self.paint_sel()
			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: hide zeile%s " % x
				self["zeile"+str(x)].hide()

			self["page_sel"+str(self.select_list+1)].hide()
			self["page"+str(self.select_list+1)].show()
			self.select_list -= 1
			self["page"+str(self.select_list+1)].hide()
			self["page_sel"+str(self.select_list+1)].show()

			for x in self.mainlist[int(self.select_list)]:
				#print "Navibar: show zeile%s " % x
				self["zeile"+str(x)].show()
		else:
			self.startpoint = int(self.mainlist[0][0])
			self.paint_sel()
			print "Navibar: -", self.startpoint
			print "Navibar: go to last page", self.select_list, self.select_list+1, self.count_mainlist

	def paint_sel(self):
                pname = self.pluginlist[int(self.startpoint)-1][1]
                if len(self.pluginlist[int(self.startpoint)-1])>6:
                   if len(self.pluginlist[int(self.startpoint)-1][7]):
                       pname = str(self.pluginlist[int(self.startpoint)-1][7])
		self["info"].setText(pname)
		self.title = pname
		position = self["zeile"+str(self.startpoint)].instance.position()
		self["frame"].moveTo(int(position.x()-5), int(position.y()-5), 1)
		self["frame"].show()
		self["frame"].startMoving()

	def navibar_config(self):
		self.session.openWithCallback(self.reload, navibar_config1, plugin_path)

	def reload(self):
		print config.plugins.navibar.hits.value
		self.close(self.session, "restart")

	def read_config(self):
		list = []
		config_read = open(self.plugin_path+"/config2" , "r")
		for line in config_read.readlines():
			ok = re.findall('"(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)', line, re.S)
			if ok:
				(name, hits, hide, sort, pw, section, descrip) = ok[0]
				list.append((name, hits, hide, sort, pw, section, descrip))
		config_read.close()
		return list

	def ok(self):
		print "lock", int(self.pluginlist[int(self.startpoint)-1][5])
		print time.strftime("%d%m")
		if int(self.pluginlist[int(self.startpoint)-1][5]) == 1:
			lock_key = int(time.strftime("%d%m"))
			self.session.openWithCallback(self.pin_callback, PinInput, pinList = [(lock_key)], triesEntry = self.getTriesEntry(), title = _("Please enter the correct pin code"), windowTitle = _("Enter pin code"))
		else:
			self.starte_plugin()

	def getTriesEntry(self):
		return config.ParentalControl.retries.setuppin

	def pin_callback(self, pin):
		print "JAAA:", pin
		if pin:
			self.starte_plugin()

	def starte_plugin(self):
		plugin_name_old = self.pluginlist[int(self.startpoint)-1]
		print "section:", plugin_name_old[1], self.sectionlist
		plugin_name = ("%s" % plugin_name_old[1])
		print plugin_name
		if plugin_name in self.sectionlist:
			if any(item[6] == plugin_name_old[1] for item in self.pluginlist_old):
				self.session.open(navi_bar, plugin_path, self.pluginlist_old, plugin_name_old[1], self.sectionlist)
			else:
				self.session.open(MessageBox, "This section have no plugins added! Press Menu", type = MessageBox.TYPE_INFO,timeout = 3)
				print "Navibar: this section have no plugins added.."
		else:
			## schreibe plugin aufrufe.. hits..
			config_read = open(self.plugin_path+"/config2" , "rw")
			config_tmp = open(self.plugin_path+"/config.tmp2" , "w")
			for line in config_read.readlines():
				ok = re.findall('"(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)"', line, re.S)
				if ok:
					(name, hits, hide, sort, pw, section, descrip) = ok[0]
					if self.pluginlist[int(self.startpoint)-1][1] == name:
						hits = int(hits) + 1
						config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits, hide, sort, pw, section, descrip))
					else:
						config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits, hide, sort, pw, section, descrip))
			config_read.close()
			config_tmp.close()
			shutil.move(self.plugin_path+"/config.tmp2", self.plugin_path+"/config2")

			#starte plugin
			plugin = self.pluginlist[int(self.startpoint)-1][0]

			#plugin[1]()
			if config.plugins.navibar.close1.value: 
                            self.close(self.session, plugin)
			else:
                            plugin[1]()

	def exit(self):
		self.close(self.session, "exit")

def main(session, **kwargs):
		from Screens.InfoBar import InfoBar
		InfoBar.Original_showExtensionSelection = InfoBar.showExtensionSelection
		InfoBar.showExtensionSelection = start
		InfoBar.instance.showExtensionSelection()
		InfoBar.showExtensionSelection = InfoBar.Original_showExtensionSelection

def closen(session, result):
	print result
	if result == "restart":
		from Screens.InfoBar import InfoBar
		InfoBar.Original_showExtensionSelection = InfoBar.showExtensionSelection
		InfoBar.showExtensionSelection = start
		InfoBar.instance.showExtensionSelection()
		InfoBar.showExtensionSelection = InfoBar.Original_showExtensionSelection
	elif result == "exit":
		pass
        else:
            result[1]()
def getPluginName(self, name):
	return name

def getPluginList(self):
	from Screens.InfoBar import InfoBar
	l = []
	dupelist = []
	for p in plugins.getPlugins(where = PluginDescriptor.WHERE_PLUGINMENU):
		dupelist.append(p.name)
		l.append(((boundFunction(self.getPluginName, p.name), boundFunction(self.runPlugin, p), lambda: True), None, p.name))

	for p in plugins.getPlugins(where = PluginDescriptor.WHERE_EXTENSIONSMENU):
		if not p.name in dupelist:
			args = inspect.getargspec(p.__call__)[0]
			if len(args) == 1 or len(args) == 2 and isinstance(InfoBar.instance, InfoBarChannelSelection):
				l.append(((boundFunction(self.getPluginName, p.name), boundFunction(self.runPlugin, p), lambda: True), None, p.name))
	print "dupelist", dupelist

	l.sort(key = lambda e: e[2]) # sort by name
	return l

def runPlugin(self, plugin):
	from Screens.InfoBar import InfoBar
	if isinstance(InfoBar.instance, InfoBarChannelSelection):
		plugin(session = self.session, servicelist = InfoBar.instance.servicelist)
	else:
		plugin(session = self.session)

def start(self):
		self.pluginlist = []
		self.pluginlist = getPluginList(self)
		self.plugin_counting = len(self.pluginlist)

		## erstellt das config file beim ersten plugin start
		if not fileExists(plugin_path+"/config2"):
			config_first = open(plugin_path+"/config2" , "w")
			for each in self.pluginlist:
				config_first.write('"%s" "0" "0" "99" "0" "main" ""\n' % each[2])
			config_first.close()

		elif fileExists(plugin_path+"/config2"):
			leer = os.path.getsize(plugin_path+"/config2")
			if leer == 0:
				config_first = open(plugin_path+"/config2" , "w")
				for each in self.pluginlist:
					config_first.write('"%s" "0" "0" "99" "0" "main" ""\n' % each[2])
				config_first.close()

		#if any(item[0] == name for item in config_list):
		## check ob ein plugin in/dein-stalliert wurde.
		self.found_new = False
		config_tmp = open(plugin_path+"/config2.tmp" , "w")
		self.list_new = []
		for plugin_data in self.pluginlist:
			#print plugin_data
			(plugin_start, none, plugin_name) = plugin_data
			config_read = open(plugin_path+"/config2","r")
			stepper_all = len(config_read.readlines())
			config_read.close()
			stepper = 0
			config_read = open(plugin_path+"/config2" , "r")

			for line in config_read.readlines():
				ok = re.findall('"(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)"', line, re.S)
				if ok:
					(name, hits, hide, sort, pw, section, bez) = ok[0]
					stepper += 1
					if plugin_name.lower() == name.lower():
						config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (name, hits, hide, sort, pw, section, bez))
						if int(hide) == 1:
							break
						else:
							self.list_new.append((plugin_start, plugin_name, hits, hide, sort, pw, section, bez))
						break

					if stepper == stepper_all:
						config_tmp.write('"%s" "%s" "%s" "%s" "%s" "%s" "%s"\n' % (plugin_name, "0" , "0", "99", "0", "main", ""))
						print plugin_name
						global found_new
						found_new = True
						if int(hide) == 1:
							break
						else:
							self.list_new.append((plugin_start, plugin_name, "0", "0", "99", "0", "main", ""))
			config_read.close()
		config_tmp.close()
		shutil.move(plugin_path+"/config2.tmp", plugin_path+"/config2")

		if not int(self.plugin_counting) == int(stepper_all):
			print "Navibar: found new plugins..need restart.."
			global found_new
			found_new = True

		#ConfigSelection(default="1", choices = [("0",_("abc")),("1",_("hits")),("2",_("own"))])
		if config.plugins.navibar.hits.value == "1":
			self.list_new.sort(key=lambda x: int(x[2]))
			self.list_new.reverse()
		elif config.plugins.navibar.hits.value == "2":
			self.list_new.sort(key=lambda x: int(x[4]))

		# add sections
		if not fileExists(plugin_path+"/sections"):
			section_first = open(plugin_path+"/sections" , "w")
			section_first.write('"main"\n')
			section_first.close()

		elif fileExists(plugin_path+"/sections"):
			leer = os.path.getsize(plugin_path+"/sections")
			if leer == 0:
				section_first = open(plugin_path+"/sections" , "w")
				section_first.write('"main"\n')
				section_first.close()

		sectionlist = []
		sections_read = open(plugin_path+"/sections" , "r")
		for line in sections_read.readlines():
			ok = re.findall('"(.*?)"', line, re.S)
			if ok:
				(section) = ok[0]
				#if not any(item[1] == section and not item[1] == "main" for item in self.list_new):
				if not section == "main":
					print section
					sectionlist.append(section)
					self.list_new.append(("none", section, "0", "0", "99", "0", "main", ""))
		sections_read.close()

		self.pluginlist = self.list_new

		if config.plugins.navibar.which.value == "bar":
			self.session.openWithCallback(closen, navi_bar, plugin_path, self.pluginlist, "main", sectionlist)
		else:
			self.session.openWithCallback(closen, navi_wall, plugin_path, self.pluginlist, "main", sectionlist)

if config.plugins.navibar.blue.value:
	from Screens.InfoBar import InfoBar
	InfoBar.showExtensionSelection = start

def Plugins(path, **kwargs):
	global plugin_path
	plugin_path = path
	return [
		PluginDescriptor(name=_("NaviBar"), description=_("Navigate your plugins."), where = [PluginDescriptor.WHERE_PLUGINMENU], fnc=main, icon="plugin.png")
		]