#
# Softcam setup mod for openPLi
# Coded by vlamo (c) 2012
# Version: 3.0-rc2
# Support: http://dream.altmaster.net/
#
# Modified for e2pc by 1455 (c) 2019
# Support: Dima-73@inbox.lv
#

from . import _
from Sc import *
import Sc
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigText


config.plugins.SoftcamSetup = ConfigSubsection()
config.plugins.SoftcamSetup.autocam = ConfigSubsection()
config.plugins.SoftcamSetup.autocam.enabled = ConfigYesNo(False)
config.plugins.SoftcamSetup.autocam.checkrec = ConfigYesNo(False)
config.plugins.SoftcamSetup.autocam.switchinfo = ConfigYesNo(False)
config.plugins.SoftcamSetup.autocam.defcam = ConfigText('None')

def sessionstart(reason, session, **kwargs):
	from autocam import StartMainSession
	StartMainSession(session)
	global quick_softcam_setup
	if reason == 0: 
		if config.plugins.SoftcamMenu.quickButton.value and quick_softcam_setup is None:
			quick_softcam_setup = QuickSoftcamSetup(session)
			quick_softcam_setup.enable()

def autostart(reason, **kwargs):
	if reason == 1:
		if quick_softcam_setup is not None:
			quick_softcam_setup.disable()

def main(session, **kwargs):
	import Sc
	session.open(Sc.ScNewSelection)

def menu(menuid, **kwargs):
	if menuid == "cam":
		return [(_("Softcam setup..."), main, "softcam_setup", 45)]
	return []

def softcam_installed():
	found = False
	for x in os.listdir('/usr/local/bin'):
		if x.find('softcam.') > -1 and x <> 'softcam.None':
			found = True
			break;
	return found

def Plugins(**kwargs):
	from Plugins.Plugin import PluginDescriptor
	if softcam_installed():
		if config.plugins.SoftcamMenu.MenuExt.value:
			return [PluginDescriptor(name = _("Softcam setup"), description = _("Lets you configure your softcams"), where = PluginDescriptor.WHERE_MENU, fnc = menu),
					PluginDescriptor(name = _("Softcam setup"), description= _("Lets you configure your softcams"), where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc= main),
					PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc= sessionstart),
					PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, fnc= autostart),
				]
		else:
			return [PluginDescriptor(name = _("Softcam setup"), description = _("Lets you configure your softcams"), where = PluginDescriptor.WHERE_MENU, fnc = menu),
					PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc= sessionstart),
					PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, fnc= autostart),
				]
	else:
		return [PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc= sessionstart),
				PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, fnc= autostart),
			]
