from . import _
from Components.NimManager import nimmanager
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import fileExists
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Tools.BoundFunction import boundFunction
import satedit
import os

loadScript = "/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/update-xml-oe.sh"

def SatellitesEditorMain(session, **kwargs):
	menu = []
	text = _("Select action:")
	if fileExists('/etc/enigma2/satellites.xml'):
		menu.append((_("Open user '/etc/enigma2/satellites.xml'"), "openedit"))
		menu.append((_("Disable user '/etc/enigma2/satellites.xml'"), "disable"))
		menu.append((_("Remove user '/etc/enigma2/satellites.xml'"), "remove"))
	else:
		if not fileExists('/etc/enigma2/satellites.xml.disabled'):
			menu.append((_("Create user '/etc/enigma2/satellites.xml'"), "create"))
			menu.append((_("Create user '/etc/enigma2/satellites.xml' (use default)"), "createdefault"))
		else:
			menu.append((_("Enable user '/etc/enigma2/satellites.xml'"), "enable"))
	if nimmanager.hasNimType('DVB-T'):
		if fileExists('/etc/enigma2/terrestrial.xml'):
			menu.append((_("Remove user '/etc/enigma2/terrestrial.xml'"), "removedvbt"))
		else:
			menu.append((_("Create user '/etc/enigma2/terrestrial.xml'"), "createdvbt"))
	if nimmanager.hasNimType('DVB-C'):
		if fileExists('/etc/enigma2/cables.xml'):
			menu.append((_("Remove user '/etc/enigma2/cables.xml'"), "removedvbc"))
		else:
			menu.append((_("Create user '/etc/enigma2/cables.xml'"), "createdvbc"))
	if menu:
		def boxAction(choice):
			if choice:
				restart = True
				if choice[1] == "openedit":
					restart = False
					session.openWithCallback(restartGui, satedit.SatellitesEditor)
				elif choice[1] == "disable":
					os.system("mv /etc/enigma2/satellites.xml /etc/enigma2/satellites.xml.disabled")
				elif choice[1] == "remove":
					os.system("rm /etc/enigma2/satellites.xml && rm /etc/enigma2/satellites.xml.disabled")
				elif choice[1] == "enable":
					os.system("mv /etc/enigma2/satellites.xml.disabled /etc/enigma2/satellites.xml")
				elif choice[1] == "createdefault":
					os.system("cp /etc/tuxbox/satellites.xml /etc/enigma2/satellites.xml")
				elif choice[1] == "removedvbt":
					os.system("rm /etc/enigma2/terrestrial.xml")
				elif choice[1] == "removedvbc":
					os.system("rm /etc/enigma2/cables.xml")
				elif choice[1] == "create":
					restart = False
					os.system("chmod 755 %s" % loadScript)
					cmd = "%s dvbs" % loadScript
					text = _("Create user '/etc/enigma2/satellites.xml'")
					session.openWithCallback(boundFunction(restartGui, session), Console, text, [cmd])
				elif choice[1] == "createdvbt":
					restart = False
					os.system("chmod 755 %s" % loadScript)
					cmd = "%s dvbt" % loadScript
					text = _("Create user '/etc/enigma2/terrestrial.xml'")
					session.openWithCallback(boundFunction(restartGui, session), Console, text, [cmd])
				elif choice[1] == "createdvbc":
					restart = False
					os.system("chmod 755 %s" % loadScript)
					cmd = "%s dvbc" % loadScript
					text = _("Create user '/etc/enigma2/cables.xml'")
					session.openWithCallback(boundFunction(restartGui, session), Console, text, [cmd])
				if restart:
					restartGui(session)
		session.openWithCallback(boxAction, ChoiceBox, title=text, list=menu)

def restartGui(session=None):
	if session and not session.nav.getRecordings():
		session.openWithCallback(boundFunction(restartGuiNow, session), MessageBox, _("Restart the GUI now?"), MessageBox.TYPE_YESNO, default = False)

def restartGuiNow(session, answer):
	if answer and session:
		session.open(TryQuitMainloop, 3)

def SatellitesEditorStart(menuid, **kwargs):
	if menuid == 'scan':
		return [(_('TS-Satellites Editor'), SatellitesEditorMain, 'sat_editor', None)]
	return []

def Plugins(**kwargs):
	if nimmanager.hasNimType('DVB-S'):
		return[PluginDescriptor(name='TS-Satellites Editor', description=_('User satellites.xml'), where=PluginDescriptor.WHERE_MENU, fnc=SatellitesEditorStart)]
	return []
