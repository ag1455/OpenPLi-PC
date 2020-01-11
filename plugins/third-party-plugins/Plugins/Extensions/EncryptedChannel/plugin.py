#  Plugin displays messages encrypted channel
#  
#  Coders: aka Uchkun & Nomad
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  version: 1.3 mod 1.1
#



from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.ServiceEventTracker import ServiceEventTracker
from Components.config import config, ConfigInteger, getConfigListEntry, ConfigSelection, ConfigYesNo, ConfigSubsection
from Components.Language import language
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.MenuList import MenuList
from enigma import iPlayableService, iServiceInformation, eServiceCenter, eServiceReference, iFrontendInformation, eTimer
from Components.Label import Label
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, fileExists
from Screens.Setup import SetupSummary
from Components.Sources.StaticText import StaticText
from os import environ, system
import os
import gettext
import time

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("EncryptedChannelSetup", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/EncryptedChannel/locale/"))


def _(txt):
	t = gettext.dgettext("EncryptedChannelSetup", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

pluginversion = "1.3"
config.plugins.EncryptedChannel = ConfigSubsection()
config.plugins.EncryptedChannel.enabled = ConfigYesNo(default = False)
config.plugins.EncryptedChannel.mesmode = ConfigSelection(default = "2", choices =
 [( "1", _("Encrypted channel")), ( "2", _("Encoded channel")),
 ( "3", _("Encrypted channel!")), ( "4", _("Encoded channel!"))])
config.plugins.EncryptedChannel.timemode = ConfigSelection(default = "1", choices =
 [( "1", _("1 second")), ( "2", _("2 seconds")),
 ( "3", _("3 seconds")), ( "4", _("4 seconds")),
 ( "5", _("5 seconds"))])
config.plugins.EncryptedChannel.minsnrmode = ConfigSelection(default = "34", choices =
 [( "5", "5" ), ( "6", "6" ), ( "7", "7" ), ( "8", "8" ), ( "9", "9" ),
 ( "10", "10" ), ( "12", "12" ), ( "14", "14" ), ( "16", "16" ), ( "18", "18" ),
 ( "20", "20" ), ( "22", "22" ), ( "24", "24" ), ( "26", "26" ), ( "28", "28" ),
 ( "30", "30" ), ( "32", "32" ), ( "34", "34" ), ( "36", "36" ), ( "38", "38" ),
 ( "40", "40" ), ( "42", "42" ), ( "46", "46" ), ( "50", "50" ), ( "55", "55" ),
 ( "60", "60" )])



EncryptMessage = None
isCrypted = None
service = None
serviceref = None

class CodedMessage(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.__event_tracker = ServiceEventTracker(screen = self, eventmap =
			{
				iPlayableService.evStart: self.__evStart,
				iPlayableService.evTunedIn: self.__evStart,
				iPlayableService.evEnd: self.__evEnd,
				iPlayableService.evStopped: self.__evEnd
			})

		self.Timer = eTimer()
		self.Timer.callback.append(self.encoded)

	def encoded(self):
		self.Timer.stop()

		global service, isCrypted

		service = self.session.nav.getCurrentService()
		if service:
			info = service and service.info()
			if info:
				isCrypted = info and info.getInfo(iServiceInformation.sIsCrypted)
				sCaIDs = info and info.getInfoObject(iServiceInformation.sCAIDs)
				ChannelEncoding = False
				signal = False
				minsignal = False
				FeInfo = service and service.frontendInfo()
				if FeInfo:
					frontendData = FeInfo.getAll(True)
					if frontendData is not None:
						if frontendData.get('tuner_type') == 'DVB-S':
							if isCrypted and sCaIDs:
								if fileExists('/var/volatile/log/messages'):
									lines = [line.rstrip() for line in open('/var/volatile/log/messages')]
									if lines[-1].__contains__('VIDEO_GET_SIZE aspect: 1 0') and not lines[-8].__contains__('VIDEO_PLAY 1  5 2'):
										ChannelEncoding = True
									else:
										system('rm -rf ' + '/var/volatile/log/messages')
								elif fileExists("/tmp/ecm.info"):
									if os.path.getsize("/tmp/ecm.info") == 0:
										if fileExists("/tmp/camd.socket"):
											if os.path.getsize("/tmp/camd.socket") == 0:
												ChannelEncoding = True
										else:
											ChannelEncoding = True
									elif os.stat('/tmp/ecm.info')[8] +20 < int(time.time()):
										ChannelEncoding = True
								elif fileExists("/tmp/camd.socket"):
									if os.path.getsize("/tmp/camd.socket") == 0:
										ChannelEncoding = True
									elif os.stat('/tmp/camd.socket')[8] +20 < int(time.time()):
										ChannelEncoding = True
								else:
									width = info and info.getInfo(iServiceInformation.sVideoWidth) or -1
									height = info and info.getInfo(iServiceInformation.sVideoHeight) or -1
									if width == -1 and height == -1:
										ChannelEncoding = True
							nSNR = FeInfo.getFrontendInfo(iFrontendInformation.signalQuality) / 655
							if nSNR < 3:
								signal = True
							elif nSNR < int(config.plugins.EncryptedChannel.minsnrmode.value):
								minsignal = True
		self.valuedict = {
					'1':"Encrypted channel",
					'2':"Encoded channel",
					'3':"Encrypted channel!",
					'4':"Encoded channel!",
				}
		if config.plugins.EncryptedChannel.mesmode.value in self.valuedict:
				txt = self.valuedict[config.plugins.EncryptedChannel.mesmode.value]
		if ChannelEncoding:
			EncryptMessage["content"].setText(_(txt))
			EncryptMessage.show()
		elif signal:
			EncryptMessage["content"].setText(_("No Signal!"))
			EncryptMessage.show()
		elif minsignal:
			EncryptMessage["content"].setText(_("Signal is too weak!"))
			EncryptMessage.show()
		else:
			EncryptMessage.hide()
		self.Timer.start(1000 * int(config.plugins.EncryptedChannel.timemode.value), False)

	def __evStart(self):
		global service, serviceref, isCrypted
		self.Timer.stop()
		EncryptMessage.hide()
		service = self.session.nav.getCurrentService()
		info = service and service.info()
		isCrypted = info and info.getInfo( iServiceInformation.sIsCrypted )
		sCaIDs = info and info.getInfoObject( iServiceInformation.sCAIDs )
		serviceref = info and info.getInfoString( iServiceInformation.sServiceref )
		if config.plugins.EncryptedChannel.enabled:
			self.Timer.start(1000 * (int(config.plugins.EncryptedChannel.timemode.value ) + 2), False)
	def __evEnd(self):
		global EncryptMessage, service

		self.Timer.stop()
		EncryptMessage.hide()
		service = None
		
class EncMessage(Screen):

	skin = """<screen position="center,center" size="380,50" flags="wfNoBorder" backgroundColor="#00000000" zPosition="-1">
		<widget name="content" halign="center" position="0,10" size="380,30" font="Regular;26" transparent="0" />
		</screen>""" 

	def __init__(self, session):
		Screen.__init__( self, session )
		self.session = session
		self["content"] = Label()


class EncryptedChannelSetup(Screen, ConfigListScreen):
	skin = """
<screen name="EncryptedChannelSetup" position="center,160" size="650,460" title="EncryptedChannelSetup settings">
  <widget position="15,10" size="620,300" name="config" scrollbarMode="showOnDemand" />
  <eLabel text="%s" position="370,330" zPosition="2" size="270,25" foregroundColor="#00009a00" halign="right" font="Regular; 22" transparent="1" />
    <ePixmap position="100,418" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/EncryptedChannel/images/red.png" alphatest="blend" />
  <widget source="red_key" render="Label" position="100,388" zPosition="2" size="165,30" font="Regular; 20" halign="center" valign="center" transparent="1" />
  <ePixmap position="385,418" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/EncryptedChannel/images/green.png" alphatest="blend" />
  <widget source="green_key" render="Label" position="385,388" zPosition="2" size="165,30" font="Regular; 20" halign="center" valign="center" transparent="1" />
</screen>""" % _("Author: a.k.a. Uchkun (c)")

	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["EncryptedChannelSetup"]
		self.setup_title = _("EncryptedChannel - Version: %s") % pluginversion

		self.onChangedEntry = []
		self.list = []
		ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)

		self["actions"] = ActionMap(["SetupActions"],
			{
				"cancel": self.keyCancel,
				"save":   self.apply,
				"ok":     self.apply
			}, -2 )

		self["green_key"] = StaticText(_("Save"))
		self["red_key"] = StaticText(_("Cancel"))

		self.createSetup()
		self.onLayoutFinish.append( self.layoutFinished )

	def layoutFinished(self):
		self.setTitle(_("EncryptedChannel - Version: %s") % pluginversion)

	def createSetup(self):
		self.list = [getConfigListEntry(_("Enabled EncryptedChannel"), config.plugins.EncryptedChannel.enabled)]
		if config.plugins.EncryptedChannel.enabled.value:
			self.list.extend((
				getConfigListEntry(_("Set text message"), config.plugins.EncryptedChannel.mesmode),
				getConfigListEntry(_("scan Rate"), config.plugins.EncryptedChannel.timemode),
				getConfigListEntry(_("Minimum acceptable level of SNR (%)"), config.plugins.EncryptedChannel.minsnrmode)
				))

		self["config"].list = self.list
		self["config"].setList(self.list)

	def apply(self):
		for x in self["config"].list:
			x[ 1 ].save()
		self.close()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		if self["config"].getCurrent()[1] == config.plugins.EncryptedChannel.enabled:
			self.createSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		if self["config"].getCurrent()[1] == config.plugins.EncryptedChannel.enabled:
			self.createSetup()

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue( self ):
		return str(self["config"].getCurrent()[1].getText())

	def createSummary(self):
		return SetupSummary
		
def autostart(reason, **kwargs):
	if config.plugins.EncryptedChannel.enabled:
		session = kwargs["session"]

		global EncryptMessage
		EncryptMessage = session.instantiateDialog(EncMessage)
		CodedMessage(session)

def encchannelSetup(session, **kwargs):
	autostart( reason = 0, session = session )
	session.open( EncryptedChannelSetup )

def Plugins(**kwargs):
	return [PluginDescriptor( name = _("EncryptedChannel"),
		description = _("EncryptedChannel MessageBox"),
			where = [PluginDescriptor.WHERE_SESSIONSTART ], fnc = autostart),
		PluginDescriptor(name = _("EncryptedChannel"),
			description = _("Show message when channel encrypted"),
			where = PluginDescriptor.WHERE_PLUGINMENU, fnc = encchannelSetup)]
