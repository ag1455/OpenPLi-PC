#
# Softcam setup mod for openPLi
# Coded by vlamo (c) 2012
# Version: 3.0-rc2
#
# Modified by Dima73 (c) 2012
# Support: Dima-73@inbox.lv
#

from . import _
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox

from Components.FileList import FileEntryComponent, FileList
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Button import Button
from Components.Label import Label
from Components.config import config, ConfigElement, ConfigSubsection, ConfigSelection, ConfigSubList, getConfigListEntry, ConfigYesNo, ConfigEnableDisable, KEY_LEFT, KEY_RIGHT, KEY_OK
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Pixmap import Pixmap, MultiPixmap
from Tools.Directories import fileExists
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText
import os
from camcontrol import CamControl
from enigma import eTimer, eDVBCI_UI, eListboxPythonStringContent, eListboxPythonConfigContent
from GlobalActions import globalActionMap
from Tools import Notifications
import keymapparser
import os.path

REFRESH = 0
CCCAMINFO = 1
OSCAMINFO = 2

ISCCCAMINFO = None
ISOSCAMINFO = None

try:
	from Screens.CCcamInfo import CCcamInfoMain
	ISCCCAMINFO = True
except:
	pass
try:
	from Screens.OScamInfo import OscamInfoMenu
	ISOSCAMINFO = True
except:
	pass

PACKAGE_PATH = os.path.dirname(str((globals())["__file__"]))
KEYMAPPINGS = {"green": os.path.join(PACKAGE_PATH, "keymap-green.xml"), "help": os.path.join(PACKAGE_PATH, "keymap-help.xml"), "text": os.path.join(PACKAGE_PATH, "keymap-text.xml"), "red": os.path.join(PACKAGE_PATH, "keymap-red.xml"), "yellow": os.path.join(PACKAGE_PATH, "keymap-yellow.xml")}

config.plugins.SoftcamMenu = ConfigSubsection()
config.plugins.SoftcamMenu.MenuExt = ConfigYesNo(default = True)
config.plugins.SoftcamMenu.quickButton = ConfigEnableDisable(default = False)
config.plugins.SoftcamMenu.keymapBut = ConfigSelection([("green", _("Green key")),("help", _("Help key")),("text", _("TEXT key")), ("red", _("RED key")), ("yellow", _("YELLOW key"))], default="help")
config.plugins.SoftcamMenu.RestartChoice = ConfigSelection([("1", _("restart softcam")),("2", _("restart cardserver")),("3", _("restart both"))], default="1")
config.plugins.SoftcamMenu.showEcm = ConfigYesNo(default = False)
config.plugins.SoftcamMenu.CloseOnRestart = ConfigYesNo(default = True)

quick_softcam_setup = None

class ConfigAction(ConfigElement):
	def __init__(self, action, *args):
		ConfigElement.__init__(self)
		self.value = "(OK)"
		self.action = action
		self.actionargs = args 
	def handleKey(self, key):
		if (key == KEY_OK):
			self.action(*self.actionargs) 

class ScNewSelection(Screen):
	if config.plugins.SoftcamMenu.showEcm.value:
		skin = """
			<screen name="ScNewSelection" position="center,center" size="670,520" title="Softcam Setup">
				<widget name="cam" zPosition="2" position="5,5" size="310,21" font="Regular; 17" halign="left" foregroundColor="#00bab329" />
				<widget name="server" zPosition="2" position="320,5" size="328,21" font="Regular; 17" halign="left" foregroundColor="#00bab329" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/div-h.png" position="0,30" zPosition="2" size="650,2" />
				<widget name="entries" position="5,35" size="630,200" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/div-h.png" position="0,235" zPosition="2" size="650,2" />
				<widget name="text" position="5,240" size="345,260" zPosition="2"  font="Regular;17" />
				<widget name="text1" position="350,240" size="320,260" zPosition="2"  font="Regular;17" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/div-h.png" position="0,470" zPosition="2" size="650,2" />
				<ePixmap position="150,510" zPosition="1" size="150,2" pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/red.png" transparent="1" alphatest="on" />
				<ePixmap position="300,510" zPosition="1" size="150,2" pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/green.png" transparent="1" alphatest="on" />
				<ePixmap position="450,510" zPosition="1" size="150,2" pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/blue.png" transparent="1" alphatest="on" />
				<widget name="key_red" position="150,480" zPosition="2" size="150,25" valign="center" halign="center" font="Regular;21" transparent="1" />
				<widget name="key_green" position="300,480" zPosition="2" size="150,25" valign="center" halign="center" font="Regular;21" transparent="1" />
				<widget name="key_blue" position="450,480" zPosition="2" size="150,25" valign="center" halign="center" font="Regular;21" transparent="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/key_menu.png" position="20,480" zPosition="2" size="50,40" alphatest="on" />
			</screen>"""	
	else:
		skin = """
			<screen name="ScNewSelection" position="center,center" size="650,270" title="Softcam Setup">
				<widget name="cam" zPosition="2" position="5,5" size="310,21" font="Regular; 17" halign="left" foregroundColor="#00bab329" />
				<widget name="server" zPosition="2" position="320,5" size="328,21" font="Regular; 17" halign="left" foregroundColor="#00bab329" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/div-h.png" position="0,30" zPosition="2" size="650,2" />
				<widget name="entries" position="5,35" size="630,180" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/div-h.png" position="0,215" zPosition="2" size="650,2" />
				<ePixmap position="150,260" zPosition="1" size="150,2" pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/red.png" transparent="1" alphatest="on" />
				<ePixmap position="300,260" zPosition="1" size="150,2" pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/green.png" transparent="1" alphatest="on" />
				<ePixmap position="450,260" zPosition="1" size="150,2" pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/blue.png" transparent="1" alphatest="on" />
				<widget name="key_red" position="150,230" zPosition="2" size="150,25" valign="center" halign="center" font="Regular;21" transparent="1" />
				<widget name="key_green" position="300,230" zPosition="2" size="150,25" valign="center" halign="center" font="Regular;21" transparent="1" />
				<widget name="key_blue" position="450,230" zPosition="2" size="150,25" valign="center" halign="center" font="Regular;21" transparent="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/key_menu.png" position="20,230" zPosition="2" size="50,40" alphatest="on" />
			</screen>"""
			
	def __init__(self, session):
		Screen.__init__(self, session)

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "EPGSelectActions", "CiSelectionActions"],
			{
				"left": self.keyLeft,
				"right": self.keyRight,
				"cancel": self.cancel,
				"ok": self.ok,
				"green": self.save,
				"red": self.cancel,
				"blue": self.bluekey,
				"menu": self.keyMenu,
			},-1)
			
		self.setTitle(_("Softcam Setup"))
		if config.plugins.SoftcamMenu.showEcm.value:
			self["text"] = ScrollLabel()
			self["text1"] = ScrollLabel()
			self.timer = eTimer()
			self.timer.callback.append(self.listServices)
			self.timer.callback.append(self.listServices1)
			self.timer.start(50, True)
			
		self.softcam = CamControl('softcam')
		self.cardserver = CamControl('cardserver')
		self.blueAction = REFRESH
		
		self["entries"] = ConfigList([])
		self.initConfig()
		self.createConfig()
		
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))
		self["key_blue"] = Label(_("Refresh"))
		self["cam"] = Label()
		self["server"] = Label()
		
		self.nameSoftcam()
		self.nameCardserver()
		self.onClose.append(self.__onClose)

	def __onClose(self):
		config.plugins.SoftcamSetup.autocam.enabled.save()
		if config.plugins.SoftcamSetup.autocam.enabled.value:
			config.plugins.SoftcamSetup.autocam.defcam.value = self.softcams.value
			config.plugins.SoftcamSetup.autocam.defcam.save()
		else:
			config.plugins.SoftcamSetup.autocam.defcam.cancel()
			config.plugins.SoftcamSetup.autocam.checkrec.value = False
		config.plugins.SoftcamSetup.autocam.checkrec.save()

	def initConfig(self):
		self.softcams = ConfigSelection(choices = self.softcam.getList())
		self.cfg_autocam = getConfigListEntry(_("Enable Auto-Camd"), config.plugins.SoftcamSetup.autocam.enabled)
		self.cfg_checkrec = getConfigListEntry(_("Don't switch auto-camd while recording"), config.plugins.SoftcamSetup.autocam.checkrec)
		self.cfg_switchinfo = getConfigListEntry(_("Show (switch info camname)"), config.plugins.SoftcamSetup.autocam.switchinfo)
		self.cfg_aclsetup = getConfigListEntry(_("Setup Auto-Camd List"), ConfigAction(self.setupAutoCamList, None))

	def createConfig(self):
		cardservers = self.cardserver.getList()
		list = [ ]
		if config.plugins.SoftcamMenu.RestartChoice.value == "1":
			list.append(getConfigListEntry(_("Restart softcam"), ConfigAction(self.restart, "s")))
			if cardservers:
				list.append(getConfigListEntry(_("Restart cardserver"), ConfigAction(self.restart, "c"))) 
				list.append(getConfigListEntry(_("Restart both"), ConfigAction(self.restart, "sc")))
		elif config.plugins.SoftcamMenu.RestartChoice.value == "2":
			if cardservers:
				list.append(getConfigListEntry(_("Restart cardserver"), ConfigAction(self.restart, "c")))
			list.append(getConfigListEntry(_("Restart softcam"), ConfigAction(self.restart, "s")))
			if cardservers:
				list.append(getConfigListEntry(_("Restart both"), ConfigAction(self.restart, "sc")))
		elif config.plugins.SoftcamMenu.RestartChoice.value == "3":
			if cardservers:
				list.append(getConfigListEntry(_("Restart both"), ConfigAction(self.restart, "sc")))
			list.append(getConfigListEntry(_("Restart softcam"), ConfigAction(self.restart, "s")))
			if cardservers:
				list.append(getConfigListEntry(_("Restart cardserver"), ConfigAction(self.restart, "c")))
		list.append(self.cfg_autocam)
		if not config.plugins.SoftcamSetup.autocam.enabled.value:
			self.softcams.value = self.softcam.current()
			list.append(getConfigListEntry(_("Select Softcam"), self.softcams))
		else:
			self.softcams.value = config.plugins.SoftcamSetup.autocam.defcam.value
			list.append(getConfigListEntry(_("Default Camd"), self.softcams))
			list.append(self.cfg_checkrec)
			list.append(self.cfg_switchinfo)
			list.append(self.cfg_aclsetup)
		if cardservers:
			self.cardservers = ConfigSelection(choices = cardservers)
			self.cardservers.value = self.cardserver.current()
			list.append(getConfigListEntry(_("Select Card Server"), self.cardservers))
		self["entries"].list = list
		self["entries"].l.setList(list)

	def newConfig(self):
		cur = self["entries"].getCurrent()
		if cur == self.cfg_autocam:
			self.createConfig()
		elif cur == self.cfg_aclsetup:
			self.setupAutoCamList()

	def keyLeft(self):
		self["entries"].handleKey(KEY_LEFT)
		self.newConfig()

	def keyRight(self):
		self["entries"].handleKey(KEY_RIGHT)
		self.newConfig()
		
	def ok(self):
		self["entries"].handleKey(KEY_OK)
	

	def restart(self, what):
		self.what = what
		if "s" in what:
			if "c" in what:
				msg = _("Please wait, restarting softcam and cardserver.")
			else:
				msg  = _("Please wait, restarting softcam.")
		elif "c" in what:
			msg = _("Please wait, restarting cardserver.")
		self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.doStop)
		self.activityTimer.start(100, False)

	def doStop(self):
		self.activityTimer.stop()
		if "c" in self.what:
			self.cardserver.command('stop')
		if "s" in self.what:
			self.softcam.command('stop')
		self.oldref = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.doStart)
		self.activityTimer.start(1000, False)

	def doStart(self):
		self.activityTimer.stop()
		del self.activityTimer 
		if "c" in self.what:
			self.cardserver.select(self.cardservers.value)
			self.cardserver.command('force-reload')
		if "s" in self.what:
			self.softcam.select(self.softcams.value)
			self.softcam.command('force-reload')
		if self.mbox:
			self.mbox.close()
		if config.plugins.SoftcamMenu.CloseOnRestart.value:
			self.close()
		else:
			self.nameSoftcam()
			self.nameCardserver()
		self.session.nav.playService(self.oldref)
		del self.oldref

	def restartCardServer(self):
		if hasattr(self, 'cardservers'):
			self.restart("c")
	
	def restartSoftcam(self):
		self.restart("s")

	def save(self):
		what = ''
		if hasattr(self, 'cardservers') and (self.cardservers.value != self.cardserver.current()):
			what = 'sc'
		elif self.softcams.value != self.softcam.current():
			what = 's'
		if what:
			self.restart(what)
		else:
			self.close()

	def keyMenu(self):
		self.session.open(ScSetupScreen)
						
	def nameSoftcam(self):
		if fileExists("/etc/init.d/softcam"):
			name = ""
			try:
				f = os.popen("/etc/init.d/softcam info")
				for i in f.readlines():
					text = _("Current softcam: ")
					name = text + i
			except: 
				pass
		else:
			name = ""
		self["cam"].setText(name)
		self.setblueKey(name)
			
	def nameCardserver(self):
		if fileExists("/etc/init.d/cardserver"):
			name = ""
			try:
				f = os.popen("/etc/init.d/cardserver info")
				for i in f.readlines():
					text = _("Current cardserver: ")
					name = text + i
			except: 
				pass
		else:
			name = ""
		self["server"].setText(name)

	def listServices(self):
		list = "\n"
		prev_mtime = None
		if fileExists("/tmp/ecm.info"):
			try:
				st = os.stat("/tmp/ecm.info")
				if st.st_size > 0 and prev_mtime < st.st_mtime:
					prev_mtime = st.st_mtime
					fdd = open("/tmp/ecm.info", "r")
					for line in fdd:
						list += line
					fdd.close()
			except:
				pass
		self["text"].setText(list)
		self.timer.start(2000, True)
		
	def listServices1(self):
		list1 = "\n"
		prev1_mtime = None
		if fileExists("/tmp/ecm1.info"):
			try:
				st1 = os.stat("/tmp/ecm1.info")
				if st1.st_size > 0 and prev1_mtime < st1.st_mtime:
					prev1_mtime = st1.st_mtime
					fd = open("/tmp/ecm1.info", "r")
					for line in fd:
						list1 += line
					fd.close()
			except:
				pass
		self["text1"].setText(list1)
		self.timer.start(2000, True)
			
	def cancel(self):
		self.close()

	def setupAutoCamList(self, *args):
		from autocam import AutoCamListSetup
		self.session.open(AutoCamListSetup, self.softcam)

	def bluekey(self):
		if self.blueAction == CCCAMINFO:
			self.session.openWithCallback(self.CCcamInfoCallback, CCcamInfoMain)
		elif self.blueAction == OSCAMINFO:
			self.session.openWithCallback(self.CCcamInfoCallback, OscamInfoMenu)
		else:
			self.nameSoftcam()
			self.nameCardserver()

	def CCcamInfoCallback(self):
		pass
		
	def setblueKey(self, cam):
		print"[SOFTCAM] setblueKey=%s<" %cam
		if cam == None or cam == '':
			self.blueAction = REFRESH
			self["key_blue"].setText(_("Refresh"))
			return
		pretxt = _("Current softcam: ")
		if cam.upper().startswith(pretxt.upper() + 'CCCAM') and ISCCCAMINFO:
			self.blueAction = CCCAMINFO
			self["key_blue"].setText(_("CCcamInfo"))
		elif cam.upper().startswith(pretxt.upper() + 'OSCAM') and ISOSCAMINFO:
			self.blueAction = OSCAMINFO
			self["key_blue"].setText(_("OscamInfo"))
		else:
			self.blueAction = REFRESH
			self["key_blue"].setText(_("Refresh"))

class ScSetupScreen(Screen, ConfigListScreen):
	skin = """
		<screen position="center,center" size="570,200" title="Settings menu">
			<ePixmap position="100,30" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/red.png" transparent="1" alphatest="on" />
			<ePixmap position="300,30" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/green.png" transparent="1" alphatest="on" />
			<widget name="red" position="100,5" zPosition="2" size="170,25" valign="center" halign="center" font="Regular;21" transparent="1" />
			<widget name="green" position="300,5" zPosition="2" size="170,25" valign="center" halign="center" font="Regular;21" transparent="1" />
			<widget name="config" position="10,50" size="550,140" font="Regular;20" />
		</screen>
		""" 
	def __init__(self, session, args = None):
		self.skin = ScSetupScreen.skin
		self.setup_title = _("Settings menu")
		Screen.__init__(self, session)
		
		self["red"] = Button(_("Cancel"))
		self["green"] = Button(_("OK"))
		
		self["actions"] = ActionMap(["SetupActions", "ColorActions"], 
		{
			"ok": self.keyOk,
			"save": self.keyGreen,
			"cancel": self.keyRed,
		}, -2)

		ConfigListScreen.__init__(self, [])
		self.initConfig()
		self.createSetup()

		self.onClose.append(self.__closed)
		self.onLayoutFinish.append(self.__layoutFinished)
		
	def __closed(self):
		pass
		
	def __layoutFinished(self):
		self.setTitle(self.setup_title)
		
	def initConfig(self):
		def getPrevValues(section):
			res = { }
			for (key,val) in section.content.items.items():
				if isinstance(val, ConfigSubsection):
					res[key] = getPrevValues(val)
				else:
					res[key] = val.value
			return res
		
		self.SC = config.plugins.SoftcamMenu
		self.prev_values  = getPrevValues(self.SC)
		self.cfg_MenuExt = getConfigListEntry(_("Show plugin extensions menu"), config.plugins.SoftcamMenu.MenuExt)
		self.cfg_quickButton = getConfigListEntry(_("Quick button"), config.plugins.SoftcamMenu.quickButton)
		self.cfg_keymapBut = getConfigListEntry(_("Choice key"), config.plugins.SoftcamMenu.keymapBut)
		self.cfg_RestartChoice = getConfigListEntry(_("Open plugin - cursor to restart:"), config.plugins.SoftcamMenu.RestartChoice)
		self.cfg_showEcm = getConfigListEntry(_("Show ecm.info"), config.plugins.SoftcamMenu.showEcm)
		self.cfg_CloseOnRestart = getConfigListEntry(_("Close plugin on restart emu"), config.plugins.SoftcamMenu.CloseOnRestart)

	def createSetup(self):
		list = [ self.cfg_MenuExt ]
		list.append(self.cfg_quickButton)
		if config.plugins.SoftcamMenu.quickButton.value:
			list.append(self.cfg_keymapBut)
		list.append(self.cfg_RestartChoice)
		list.append(self.cfg_showEcm)
		if config.plugins.SoftcamMenu.showEcm.value:
			list.append(self.cfg_CloseOnRestart)
		self["config"].list = list
		self["config"].l.setList(list)

	def newConfig(self):
		cur = self["config"].getCurrent()
		if cur in (self.cfg_MenuExt, self.cfg_quickButton, self.cfg_keymapBut, self.cfg_RestartChoice, self.cfg_showEcm, self.cfg_CloseOnRestart):
			self.createSetup()


	def keyOk(self):
		pass

	def keyRed(self):
		def setPrevValues(section, values):
			for (key,val) in section.content.items.items():
				value = values.get(key, None)
				if value is not None:
					if isinstance(val, ConfigSubsection):
						setPrevValues(val, value)
					else:
						val.value = value
		setPrevValues(self.SC, self.prev_values)
		self.keyGreen()

	def keyGreen(self):
		global quick_softcam_setup		
		if config.plugins.SoftcamMenu.quickButton.isChanged():
			if config.plugins.SoftcamMenu.quickButton.value:
				quick_softcam_setup = QuickSoftcamSetup(self.session)
				quick_softcam_setup.enable()
			elif quick_softcam_setup is not None:
				quick_softcam_setup.disable()
		elif quick_softcam_setup is not None:
			if config.plugins.SoftcamMenu.keymapBut.isChanged():
				quick_softcam_setup.change_keymap(config.plugins.SoftcamMenu.keymapBut.value)
		if not config.plugins.SoftcamMenu.showEcm.value:
			self.SC.CloseOnRestart.value = True
		self.SC.save()
		self.close()
		

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.newConfig()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.newConfig()
		
class QuickSoftcamSetup:

	def __init__(self, session):
		self.session = session
		
	def change_keymap(self, keymap):
		if keymap not in KEYMAPPINGS:
			return
		self.unload_keymap()
		try:
			keymapparser.readKeymap(KEYMAPPINGS[keymap])
		except IOError, (errno, strerror):
			config.plugins.SoftcamMenu.quickButton.setValue(False)
			self.disable()
			Notifications.AddPopup(text=_("Changing keymap failed (%s).") % strerror, type=MessageBox.TYPE_ERROR, timeout=10, id='QuickSoftcamSetup')
			return
		global globalActionMap
		globalActionMap.actions['quickSoftcamSetup'] = self.quickSoftcamSetup
	

	def unload_keymap(self):
		for keymap in KEYMAPPINGS.values():
			keymapparser.removeKeymap(keymap)
		
		global globalActionMap
		if 'quickSoftcamSetup' in globalActionMap.actions:
			del globalActionMap.actions['quickSoftcamSetup']

	def enable(self):
		self.change_keymap(config.plugins.SoftcamMenu.keymapBut.value)

	
	def disable(self):
		global quick_softcam_setup
		self.unload_keymap()
		quick_softcam_setup = None

	def quickSoftcamSetup(self):
		self.session.open(ScNewSelection)
		
