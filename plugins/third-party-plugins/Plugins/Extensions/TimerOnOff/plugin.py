# -*- coding: utf-8 -*-
# Timer ON/OFF plugin
# Copyright (c) 2boom 2012-14
# 0.4-r1 03.02.2014
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from Components.ActionMap import ActionMap
from Components.config import config, getConfigListEntry, ConfigText, NoSave, ConfigPassword, ConfigClock, ConfigSelection, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigNumber, configfile
from Components.ConfigList import ConfigListScreen
from ServiceReference import ServiceReference
from enigma import iPlayableService,eServiceReference
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Sources.List import List
from Tools.Directories import fileExists
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Components.ScrollLabel import ScrollLabel
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from os import environ
import os
import gettext



lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("timeoff", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/TimerOnOff/locale/"))

def _(txt):
	t = gettext.dgettext("timeoff", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t
######################################################################################
config.plugins.timeroff = ConfigSubsection()
config.plugins.timeroff.mode = ConfigSelection(default = "0", choices = [
		("0", _("Off")),
		("1", _("Standby")),
		("2", _("Wakeup")),
		("3", _("Standby/Wakeup")),
		("4", _("DeepStandby")),
		])
config.plugins.timeroff.weekday = ConfigSelection(default = "*", choices = [
		("*", _("All")),
		("1-5", _("Weekdays")),
		("0,6", _("Weekend")),
		("1", _("Mo")),
		("2", _("Tu")),
		("3", _("We")),
		("4", _("Th")),
		("5", _("Fr")),
		("6", _("Sa")),
		("0", _("Su")),
		])
config.plugins.timeroff.standby = ConfigClock(default = ((20*60) + 15) * 60) # 22:15
config.plugins.timeroff.standby2 = ConfigClock(default = ((20*60) + 15) * 60) # 22:15
config.plugins.timeroff.wakeup = ConfigClock(default = ((7*60) + 15) * 60) # 9:15
config.plugins.timeroff.pwd = NoSave(ConfigPassword(default = "", fixed_size = False))
config.plugins.timeroff.volume = ConfigInteger(default = 20, limits = (0, 99))
config.plugins.timeroff.channel = ConfigSelection(default = "no", choices = [
		("no", _("no")),
		("yes", _("yes")),
		])
config.plugins.timeroff.secondtimer = ConfigYesNo(default = False)
######################################################################
class timeoff(ConfigListScreen, Screen):
	skin = """
<screen name="timeoff" position="center,160" size="750,370" title="Set time to stanby/wakeup">
  <widget position="15,10" size="720,200" name="config" scrollbarMode="showOnDemand" />
   <ePixmap position="10,358" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/images/red.png" alphatest="blend" />
  <widget source="red_key" render="Label" position="10,328" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
  <ePixmap position="175,358" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/images/green.png" alphatest="blend" />
  <widget source="green_key" render="Label" position="175,328" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("Set time to stanby/wakeup"))
		self.list = []
		self.list.append(getConfigListEntry(_("Set mode"), config.plugins.timeroff.mode))
		self.list.append(getConfigListEntry(_("Set time to wakeup"), config.plugins.timeroff.wakeup))
		self.list.append(getConfigListEntry(_("Set time to standby/deepstanby #1"), config.plugins.timeroff.standby))
		self.list.append(getConfigListEntry(_("Turn on second stanby timer"), config.plugins.timeroff.secondtimer))
		self.list.append(getConfigListEntry(_("Set time to standby/deepstanby #2"), config.plugins.timeroff.standby2))
		self.list.append(getConfigListEntry(_("Set day of week"), config.plugins.timeroff.weekday))
		self.list.append(getConfigListEntry(_("Type box password, if you have it"), config.plugins.timeroff.pwd))
		self.list.append(getConfigListEntry(_("Set wakeup volume (0-99)"), config.plugins.timeroff.volume))
		self.list.append(getConfigListEntry(_("Set current channel at wakeup"), config.plugins.timeroff.channel))
		ConfigListScreen.__init__(self, self.list)
		self["red_key"] = StaticText(_("Close"))
		if not self.cronpath() is '':
			self["green_key"] = StaticText(_("Save"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"red": self.cancel,
			"cancel": self.cancel,
			"green": self.save,
			"ok": self.save
		}, -2)

	def cancel(self):
		for i in self["config"].list:
			i[1].cancel()
		self.close(False)
		
	def getcurrentref(self, zapto = None):
		self.zap_service = zapto or self.session.nav.getCurrentlyPlayingServiceReference()
		ref_cur = self.zap_service
		refstr = ref_cur.toString()
		return ServiceReference(eServiceReference(refstr))
		
	def deltasks(self):
		path = self.cronpath()
		os.system("sed -i '/standby/d' %s" % path)
		os.system("sed -i '/wakeup/d' %s" % path)
		
	def save(self):
		path = self.cronpath()
		config.plugins.timeroff.mode.save()
		config.plugins.timeroff.standby.save()
		config.plugins.timeroff.standby2.save()
		config.plugins.timeroff.secondtimer.save()
		config.plugins.timeroff.wakeup.save()
		os.system("tar -C/ -xzpvf /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/scripts.tar.gz")
		if config.plugins.timeroff.channel.value is "yes":
			os.system("echo -e '\twget -qO -  http://root@localhost/web/zap?sRef=%s' >>/usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/wakeup.sh" % self.getcurrentref())
		if len(config.plugins.timeroff.pwd.value) >= 1:
			os.system("sed -i 's/root/root:%s/g' /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/standby.sh" % config.plugins.timeroff.pwd.value)
			if config.plugins.timeroff.secondtimer.value:
				os.system("sed -i 's/root/root:%s/g' /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/standby2.sh" % config.plugins.timeroff.pwd.value)
			os.system("sed -i 's/root/root:%s/g' /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/wakeup.sh" % config.plugins.timeroff.pwd.value)
		if config.plugins.timeroff.mode.value is "0":
			self.deltasks()
		elif config.plugins.timeroff.mode.value is "1":
			self.deltasks()
			os.system("echo -e '%s %s * * %s /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/standby.sh' >> %s" % (config.plugins.timeroff.standby.value[1], config.plugins.timeroff.standby.value[0], config.plugins.timeroff.weekday.value, path))
			if config.plugins.timeroff.secondtimer.value:
				os.system("echo -e '%s %s * * %s /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/standby2.sh' >> %s" % (config.plugins.timeroff.standby2.value[1], config.plugins.timeroff.standby2.value[0], config.plugins.timeroff.weekday.value, path))
		elif config.plugins.timeroff.mode.value is "2":
			self.deltasks()
			os.system("sed -i 's/set=setxx/set=set%s/g' /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/wakeup.sh" % config.plugins.timeroff.volume.value)
			os.system("echo -e '%s %s * * %s /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/wakeup.sh' >> %s" % (config.plugins.timeroff.wakeup.value[1], config.plugins.timeroff.wakeup.value[0], config.plugins.timeroff.weekday.value, path))
		elif config.plugins.timeroff.mode.value is "3":
			self.deltasks()
			os.system("sed -i 's/set=setxx/set=set%s/g' /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/wakeup.sh" % config.plugins.timeroff.volume.value)
			os.system("echo -e '%s %s * * %s /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/standby.sh' >> %s" % (config.plugins.timeroff.standby.value[1], config.plugins.timeroff.standby.value[0], config.plugins.timeroff.weekday.value, path))
			if config.plugins.timeroff.secondtimer.value:
				os.system("echo -e '%s %s * * %s /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/standby2.sh' >> %s" % (config.plugins.timeroff.standby2.value[1], config.plugins.timeroff.standby2.value[0], config.plugins.timeroff.weekday.value, path))
			os.system("echo -e '%s %s * * %s /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/wakeup.sh' >> %s" % (config.plugins.timeroff.wakeup.value[1], config.plugins.timeroff.wakeup.value[0], config.plugins.timeroff.weekday.value, path))
		elif config.plugins.timeroff.mode.value is "4":
			self.deltasks()
			os.system("echo -e '%s %s * * %s /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/deepstandby.sh' >> %s" % (config.plugins.timeroff.standby.value[1], config.plugins.timeroff.standby.value[0], config.plugins.timeroff.weekday.value, path))
			if config.plugins.timeroff.secondtimer.value:
				os.system("echo -e '%s %s * * %s /usr/lib/enigma2/python/Plugins/Extensions/TimerOnOff/deepstandby2.sh' >> %s" % (config.plugins.timeroff.standby2.value[1], config.plugins.timeroff.standby2.value[0], config.plugins.timeroff.weekday.value, path))
		os.system("echo -e 'root' >> %scron.update" % path[:-4])
		for i in self["config"].list:
			i[1].save()
		configfile.save()
		self.mbox = self.session.open(MessageBox,(_("configuration is saved")), MessageBox.TYPE_INFO, timeout = 4 )
################################################################################################################
	def cronpath(self):
		path = ''
		if os.path.exists("/etc/cron/crontabs"):
			path = "/etc/cron/crontabs/root"
		elif os.path.exists("/etc/bhcron"):
			path = "/etc/bhcron/root"
		elif os.path.exists("/etc/crontabs"):
			path = "/etc/crontab/root"
		elif os.path.exists("/var/spool/cron/crontabs"):
			path = "/var/spool/cron/crontabs/root"
		return path
#####################################################
def main(session, **kwargs):
	session.open(timeoff)

def menu(menuid, **kwargs):
	if menuid == "shutdown":
		return [(_("OnOff timer"), main, "OnOff timer", 49)]
	return []
	
def Plugins(**kwargs):
	list = [PluginDescriptor(name=_("OnOff timer"), description=_("set time to stanby/wakeup"), where = [PluginDescriptor.WHERE_PLUGINMENU], icon="timeoff.png", fnc=main)]
	list.append(PluginDescriptor(name=_("OnOff timer"), description=_("set time to stanby/wakeup"), where = [PluginDescriptor.WHERE_MENU], fnc=menu))
	return list

