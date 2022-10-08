from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigSubsection, ConfigBoolean, ConfigText
from enigma import eServiceReference, eServiceCenter
from Screens.InfoBarGenerics import InfoBarNumberZap, InfoBarPiP, NumberZap
import HotkeysSetup

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
    lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
    os_environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
    gettext.bindtextdomain("BouquetHotkeys", resolveFilename(SCOPE_PLUGINS, "Extensions/BouquetHotkeys/locale"))

def _(txt):
    t = gettext.dgettext("BouquetHotkeys", txt)
    if t == txt:
        print "[BouquetHotkeys] fallback to default translation for", txt
        t = gettext.gettext(txt)
    return t

localeInit()
language.addCallback(localeInit)

config.usage.bouquethotkeys = ConfigBoolean(default = False)

config.plugins.BouquetHotkeys = ConfigSubsection()
config.plugins.BouquetHotkeys.key1 = ConfigText(_("none"))
config.plugins.BouquetHotkeys.key2 = ConfigText(_("none"))
config.plugins.BouquetHotkeys.key3 = ConfigText(_("none"))
config.plugins.BouquetHotkeys.key4 = ConfigText(_("none"))
config.plugins.BouquetHotkeys.key5 = ConfigText(_("none"))
config.plugins.BouquetHotkeys.key6 = ConfigText(_("none"))
config.plugins.BouquetHotkeys.key7 = ConfigText(_("none"))
config.plugins.BouquetHotkeys.key8 = ConfigText(_("none"))
config.plugins.BouquetHotkeys.key9 = ConfigText(_("none"))

def OpenBouquetByRef(instance, bouquet):
	if isinstance(bouquet, eServiceReference):
		if instance.servicelist.getRoot() != bouquet:
			instance.servicelist.clearPath()
			if instance.servicelist.bouquet_root != bouquet:
				instance.servicelist.enterPath(instance.servicelist.bouquet_root)
			instance.servicelist.enterPath(bouquet)
		instance.session.execDialog(instance.servicelist)

def keyNumberGlobal(instance, number):
#	print "You pressed number " + str(number)
	if number == 0:
		if isinstance(instance, InfoBarPiP) and instance.pipHandles0Action():
			instance.pipDoHandle0Action()
		else:
			instance.servicelist.recallPrevService()
	else:
		if instance.has_key("TimeshiftActions") and not instance.timeshiftEnabled():
			if config.usage.bouquethotkeys.value and config.usage.multibouquet.value:
				refstr = eval("config.plugins.BouquetHotkeys.key"+str(number)).value
				if not refstr in ("", "none"):
					OpenBouquetByRef(instance, eServiceReference(refstr))
				else:
					instance.session.openWithCallback(instance.numberEntered, NumberZap, number, instance.searchNumber)
			else:
				instance.session.openWithCallback(instance.numberEntered, NumberZap, number, instance.searchNumber)

InfoBarNumberZap.keyNumberGlobal = keyNumberGlobal

def StartMainSession(session, **kwargs):
	if config.usage.bouquethotkeys.value and config.usage.multibouquet.value:
		pass

def OpenHotkeysSetup(session, **kwargs):
	reload(HotkeysSetup)
	session.open(HotkeysSetup.HotkeysSetupScreen)

def Plugins(**kwargs):
	return [PluginDescriptor(name=_("BouquetHotkeys"), description=_("bouquet hotkeys plugin"), where = PluginDescriptor.WHERE_SESSIONSTART, fnc = StartMainSession),
		PluginDescriptor(name=_("BouquetHotkeys"), description=_("bouquet hotkeys plugin"), where = PluginDescriptor.WHERE_PLUGINMENU, fnc = OpenHotkeysSetup)]