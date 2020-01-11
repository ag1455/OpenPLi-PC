# -*- coding: UTF-8 -*-
## Calendar
## Coded by Sirius
##
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText
from Components.Language import language
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigSelection, ConfigSubsection, ConfigYesNo, configfile, NoSave
from Tools.Directories import fileExists
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_LANGUAGE
from skin import parseColor, parseFont
from calendar import month
from time import localtime
from os import environ
from os import system
import gettext
import datetime
import os

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("Calendar", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/Calendar/locale"))

def _(txt):
	t = gettext.dgettext("Calendar", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

config.plugins.calendar = ConfigSubsection()
config.plugins.calendar.menu = ConfigSelection(default="no", choices = [
	("no", _("no")),
	("yes", _("yes"))])

class Calendar(ConfigListScreen, Screen):
	skin = """
	<!-- Calendar -->
	<screen name="Calendar" position="40,55" size="1200,650" title=" " >
		<eLabel position="20,610" size="1160,3" backgroundColor="#00555555" zPosition="1" />

		<widget name="w0" position="10,40" size="40,40" font="Regular;20" halign="center" valign="center" backgroundColor="#00555555" />
		<widget name="w1" position="55,40" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="#00555555" />
		<widget name="w2" position="100,40" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="#00555555" />
		<widget name="w3" position="145,40" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="#00555555" />
		<widget name="w4" position="190,40" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="#00555555" />
		<widget name="w5" position="235,40" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="#00555555" />
		<widget name="w6" position="280,40" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="#00555555" />
		<widget name="w7" position="325,40" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="#00555555" />

		<widget name="wn0" position="10,85" size="40,40" font="Regular;20" halign="center" valign="center" backgroundColor="#00555555" />
		<widget name="wn1" position="10,130" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="#00555555" />
		<widget name="wn2" position="10,175" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="#00555555" />
		<widget name="wn3" position="10,220" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="#00555555" />
		<widget name="wn4" position="10,265" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="#00555555" />
		<widget name="wn5" position="10,310" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="#00555555" />

		<widget name="d0" position="55,85" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d1" position="100,85" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d2" position="145,85" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d3" position="190,85" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d4" position="235,85" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d5" position="280,85" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d6" position="325,85" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />

		<widget name="d7" position="55,130" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d8" position="100,130" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d9" position="145,130" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d10" position="190,130" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d11" position="235,130" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d12" position="280,130" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d13" position="325,130" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />

		<widget name="d14" position="55,175" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d15" position="100,175" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d16" position="145,175" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d17" position="190,175" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d18" position="235,175" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d19" position="280,175" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d20" position="325,175" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />

		<widget name="d21" position="55,220" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d22" position="100,220" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d23" position="145,220" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d24" position="190,220" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d25" position="235,220" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d26" position="280,220" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d27" position="325,220" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />

		<widget name="d28" position="55,265" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d29" position="100,265" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d30" position="145,265" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d31" position="190,265" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d32" position="235,265" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d33" position="280,265" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d34" position="325,265" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />

		<widget name="d35" position="55,310" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d36" position="100,310" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d37" position="145,310" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d38" position="190,310" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d39" position="235,310" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d40" position="280,310" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />
		<widget name="d41" position="325,310" size="40,40" font="Regular;22" halign="center" valign="center" backgroundColor="background" />

		<widget name="monthname" position="10,5" size="355,30" font="Regular; 24" foregroundColor="#00ffcc33" backgroundColor="background" halign="center" transparent="1" />
		<widget name="date" position="370,10" size="820,25" font="Regular; 20" foregroundColor="#00ffcc33" backgroundColor="background" halign="left" transparent="1" />
		<widget name="datepeople" position="370,40" size="820,25" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
		<widget name="monthpeople" position="10,360" size="355,245" font="Regular; 20" foregroundColor="#008f8f8f" backgroundColor="background" halign="left" transparent="1" />
		<widget name="sign" position="370,70" size="820,50" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
		<widget name="holiday" position="370,125" size="820,50" font="Regular; 20" foregroundColor="#00f4f4f4" backgroundColor="background" halign="left" transparent="1" />
		<widget name="description" position="370,180" size="820,425" font="Regular; 20" foregroundColor="#008f8f8f" backgroundColor="background" halign="left" transparent="1" />

		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Calendar/buttons/key_menu.png" position="1080,620" size="40,20" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Calendar/buttons/key_epg.png" position="1130,620" size="40,20" alphatest="on" />
		<widget source="key_red" render="Label" position="75,615" size="165,30" font="Regular; 22" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
		<widget source="key_green" render="Label" position="295,615" size="165,30" font="Regular; 22" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
		<widget source="key_yellow" render="Label" position="515,615" size="165,30" font="Regular; 22" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
		<widget source="key_blue" render="Label" position="735,615" size="165,30" font="Regular; 22" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Calendar/buttons/key_red.png" position="30,620" size="40,20" alphatest="blend" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Calendar/buttons/key_green.png" position="250,620" size="40,20" alphatest="blend" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Calendar/buttons/key_yellow.png" position="470,620" size="40,20" alphatest="blend" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Calendar/buttons/key_blue.png" position="690,620" size="40,20" alphatest="blend" />
	</screen>"""

	def __init__(self, session):

		Screen.__init__(self, session)
		self.session = session

		self.year = localtime()[0]
		self.month = localtime()[1]
		self.day = localtime()[2]

		self.language = config.osd.language.value.split("_")[0].strip()

		self.path = "/usr/lib/enigma2/python/Plugins/Extensions/Calendar/"
		self["shortcuts"] = ActionMap(["OkCancelActions", "ColorActions", "MenuActions", "EPGSelectActions"], 
		{ "cancel": self.exit,
		"red": self.prevmonth,
		"green": self.nextmonth,
		"yellow": self.prevday,
		"blue": self.nextday,
		"menu": self.config,
		"info": self.about,
		}, -1)

		for x in range(7):
			self['wn' + str(x)] = Label()
		for x in range(48):
			if x < 8:
				weekname = (_('...'),
				_('Mo'),
				_('Tu'),
				_('We'),
				_('Th'),
				_('Fr'),
				_('Sa'),
				_('Su'))
				self['w' + str(x)] = Label(weekname[x])
			self['d' + str(x)] = Label()

		self["Title"] = StaticText(_("Calendar"))
		self["key_red"] = StaticText(_("Month -"))
		self["key_green"] = StaticText(_("Month +"))
		self["key_yellow"] = StaticText(_("Day -"))
		self["key_blue"] = StaticText(_("Day +"))
		self["monthname"] = Label(_("..."))
		self["date"] = Label(_("No file in database..."))
		self["datepeople"] = Label(_("..."))
		self["monthpeople"] = Label(_("..."))
		self["sign"] = Label(_("..."))
		self["holiday"] = Label(_("..."))
		self["description"] = ScrollLabel(_("..."))

		self.date()
		self.datepeople()
		self.monthpeople()
		self.sign()
		self.holiday()
		self.description()
		self.onLayoutFinish.append(self.calendar)

	def calendar(self):
		monthname = (
		_('January'),
		_('February'),
		_('March'),
		_('April'),
		_('May'),
		_('June'),
		_('July'),
		_('August'),
		_('September'),
		_('October'),
		_('November'),
		_('December'))

		i = 1
		ir = 0
		d1 = datetime.date(self.year, self.month, 1)
		d2 = d1.weekday()

		if self.month == 12:
			sdt1 = datetime.date(self.year + 1, 1, 1) - datetime.timedelta(1)
		else:
			sdt1 = datetime.date(self.year, self.month + 1, 1) - datetime.timedelta(1)
		self.monthday = int(sdt1.day)
		self.monthname = monthname[self.month - 1]
		self["monthname"].setText(str(self.year)+' '+str(self.monthname))

		for x in range(42):
			self['d' + str(x)].setText('')
			self['d' + str(x)].instance.clearForegroundColor()
			self['d' + str(x)].instance.clearBackgroundColor()
			if (x + 7) % 7 == 0:
				ir += 1
				self['wn' + str(ir)].setText('')
			if x >= d2 and i <= self.monthday:
				r = datetime.datetime(self.year, self.month, i)
				wn1 = r.isocalendar()[1]
				self['wn' + str(ir - 1)].setText('%0.2d' % wn1)
				self['d' + str(x)].setText(str(i))
				self['d' + str(x)].instance.setForegroundColor(parseColor('white'))
				if datetime.date(self.year, self.month, i) == datetime.date.today():
					self['d' + str(x)].instance.setBackgroundColor(parseColor('green'))
				if datetime.date(self.year, self.month, i).weekday() == 5:
					self['d' + str(x)].instance.setForegroundColor(parseColor('yellow'))
				if datetime.date(self.year, self.month, i).weekday() == 6:
					self['d' + str(x)].instance.setForegroundColor(parseColor('red'))
				i = i + 1

		self.date()
		self.datepeople()
		self.monthpeople()
		self.sign()
		self.holiday()
		self.description()

	def nextday(self):
		if self.day == 31 and self.month == 1:
			self.day = 0
			self.month = self.month + 1
		if self.day == 29 and self.month == 2:
			self.day = 0
			self.month = self.month + 1
		if self.day == 31 and self.month == 3:
			self.day = 0
			self.month = self.month + 1
		if self.day == 30 and self.month == 4:
			self.day = 0
			self.month = self.month + 1
		if self.day == 31 and self.month == 5:
			self.day = 0
			self.month = self.month + 1
		if self.day == 30 and self.month == 6:
			self.day = 0
			self.month = self.month + 1
		if self.day == 31 and self.month == 7:
			self.day = 0
			self.month = self.month + 1
		if self.day == 31 and self.month == 8:
			self.day = 0
			self.month = self.month + 1
		if self.day == 30 and self.month == 9:
			self.day = 0
			self.month = self.month + 1
		if self.day == 31 and self.month == 10:
			self.day = 0
			self.month = self.month + 1
		if self.day == 30 and self.month == 11:
			self.day = 0
			self.month = self.month + 1
		if self.day == 31 and self.month == 12:
			self.day = 1
			self.month = 1
			self.year = self.year + 1
		else:
			self.day = self.day + 1
		self.calendar()

	def prevday(self):
		if self.day == 1 and self.month == 1:
			self.day = 32
			self.month = 12
			self.year = self.year - 1
		if self.day == 1 and self.month == 2:
			self.day = 32
			self.month = self.month - 1
		if self.day == 1 and self.month == 3:
			self.day = 30
			self.month = self.month - 1
		if self.day == 1 and self.month == 4:
			self.day = 32
			self.month = self.month - 1
		if self.day == 1 and self.month == 5:
			self.day = 31
			self.month = self.month - 1
		if self.day == 1 and self.month == 6:
			self.day = 32
			self.month = self.month - 1
		if self.day == 1 and self.month == 7:
			self.day = 31
			self.month = self.month - 1
		if self.day == 1 and self.month == 8:
			self.day = 32
			self.month = self.month - 1
		if self.day == 1 and self.month == 9:
			self.day = 32
			self.month = self.month - 1
		if self.day == 1 and self.month == 10:
			self.day = 31
			self.month = self.month - 1
		if self.day == 1 and self.month == 11:
			self.day = 32
			self.month = self.month - 1
		if self.day == 1 and self.month == 12:
			self.day = 30
			self.month = self.month - 1
		else:
			self.day = self.day - 1
		self.calendar()

	def nextmonth(self):
		if self.month == 12:
			self.month = 1
			self.year = self.year + 1
		else:
			self.month = self.month + 1
		self.calendar()

	def prevmonth(self):
		if self.month == 1:
			self.month = 12
			self.year = self.year - 1
		else:
			self.month = self.month - 1
			self.year = self.year
		self.calendar()

	def date(self):
		list = ""
		try:
			text = open("%sbase/%s/day/m%sd%s.txt" % (self.path, self.language, self.month, self.day), "r").readlines()[0]
			for line in text:
				list += line
			self["date"].setText(list)
			text.close()
			return list
		except:
			return ""

	def datepeople(self):
		list = ""
		try:
			text = open("%sbase/%s/day/m%sd%s.txt" % (self.path, self.language, self.month, self.day), "r").readlines()[1]
			for line in text:
				list += line
			self["datepeople"].setText(list)
			text.close()
			return list
		except:
			return ""

	def monthpeople(self):
		list = ""
		try:
			text = open("%sbase/%s/month/m%s.txt" % (self.path, self.language, self.month), "r").readlines()[1]
			for line in text:
				list += line
			self["monthpeople"].setText(list)
			text.close()
			return list
		except:
			return ""

	def sign(self):
		list = ""
		try:
			text = open("%sbase/%s/day/m%sd%s.txt" % (self.path, self.language, self.month, self.day), "r").readlines()[2]
			for line in text:
				list += line
			self["sign"].setText(list)
			text.close()
			return list
		except:
			return ""

	def holiday(self):
		list = ""
		try:
			text = open("%sbase/%s/day/m%sd%s.txt" % (self.path, self.language, self.month, self.day), "r").readlines()[3]
			for line in text:
				list += line
			self["holiday"].setText(list)
			text.close()
			return list
		except:
			return ""

	def description(self):
		list = ""
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"], { "up": self["description"].pageUp, "down": self["description"].pageDown,}, -1)
		try:
			text = open("%sbase/%s/day/m%sd%s.txt" % (self.path, self.language, self.month, self.day), "r").readlines()[4]
			for line in text:
				list += line
			self["description"].setText(list)
			text.close()
			return list
		except:
			return ""

	def config (self):
		self.session.open(ConfigCalendar)

	def about(self):
		self.session.open(MessageBox, _("Calendar\nDeveloper: Sirius0103 \nHomepage: www.gisclub.tv \n\nDonate:\nWMZ  Z395874509364\nWME  E284580190260\nWMR  R213063691482\nWMU  U658742613505"), MessageBox.TYPE_INFO)

	def exit(self):
		self.close()

class ConfigCalendar(ConfigListScreen, Screen):
	skin = """
	<!-- Config Calendar -->
	<screen name="ConfigCalendar" position="center,160" size="750,370" title=" ">
		<eLabel position="20,325" size="710,3" backgroundColor="#00555555" zPosition="1" />
		<widget name="config" position="15,10" size="720,300" scrollbarMode="showOnDemand" transparent="1" />
		<widget source="key_red" render="Label" position="80,330" size="165,30" font="Regular; 22" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
		<widget source="key_green" render="Label" position="310,330" size="165,30" font="Regular; 22" halign="left" valign="center" foregroundColor="#00f4f4f4" backgroundColor="background" transparent="1" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Calendar/buttons/key_red.png" position="30,335" size="40,20" alphatest="blend" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Calendar/buttons/key_green.png" position="260,335" size="40,20" alphatest="blend" />
	</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)

		self.setTitle(_("Config Calendar"))
		self.convertorpath = "/usr/lib/enigma2/python/Components/Converter/"
		self.pluginpath = "/usr/lib/enigma2/python/Plugins/Extensions/Calendar/components/"

		list = []
		list.append(getConfigListEntry(_("Show Calendar in menu information:"), config.plugins.calendar.menu))
		ConfigListScreen.__init__(self, list)

		self["setupActions"] = ActionMap(["DirectionActions", "SetupActions", "ColorActions"],
		{ "red": self.cancel,
		"cancel": self.cancel,
		"green": self.save,
		"ok": self.save
		}, -2)
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))

	def createConvertor(self):
		os.system("cp %sCalendarToText.py %sCalendarToText.py" % (self.pluginpath, self.convertorpath))

	def cancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close(False)

	def save(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()
		self.createConvertor()
		self.mbox = self.session.open(MessageBox,(_("Configuration is saved")), MessageBox.TYPE_INFO, timeout = 3 )
		self.close()

def CalendarMenu(menuid):
	if menuid != "information":
		return [ ]
	return [(_("Calendar"), openCalendar, "Calendar", None)]

def openCalendar(session, **kwargs):
	session.open(Calendar)

def main(session, **kwargs):
	session.open(Calendar)

def Plugins(**kwargs):
	if config.plugins.calendar.menu.value == 'yes':
		result = [
		PluginDescriptor(name=_("Calendar"),
		where=PluginDescriptor.WHERE_MENU,
		fnc=CalendarMenu),
		PluginDescriptor(name=_("Calendar"),
		description=_("Calendar"),
		where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
		icon="plugin.png",
		fnc=main)
		]
		return result
	else:
		result = [
		PluginDescriptor(name=_("Calendar"),
		description=_("Calendar"),
		where = [PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
		icon="plugin.png",
		fnc=main)
		]
		return result