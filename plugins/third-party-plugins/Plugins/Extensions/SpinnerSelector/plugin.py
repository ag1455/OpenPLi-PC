# coding=utf-8
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.config import config
from enigma import ePicLoad, getDesktop, eConsoleAppContainer
from Plugins.Extensions.SpinnerSelector.SpinnerSelector import SpinnerSelector
import os

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
    lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
    os_environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
    gettext.bindtextdomain("SpinnerSelector", resolveFilename(SCOPE_PLUGINS, "Extensions/SpinnerSelector/locale"))

def _(txt):
    t = gettext.dgettext("SpinnerSelector", txt)
    if t == txt:
        print "[SpinnerSelector] fallback to default translation for", txt
        t = gettext.gettext(txt)
    return t

localeInit()
language.addCallback(localeInit)

def main(session, **kwargs):
	SpinnerSelector(session)
			
def autostart(reason, **kwargs):
	pass
		
def Plugins(**kwargs):
	screenwidth = getDesktop(0).size().width()
	if screenwidth and screenwidth == 1920:
		return [PluginDescriptor(name=_("Spinner"), description=_("Configuration tool for Spinner"), where = PluginDescriptor.WHERE_PLUGINMENU, icon='pluginfhd.png', fnc=main)]
	else:
		return [PluginDescriptor(name=_("Spinner"), description=_("Configuration tool for Spinner"), where = PluginDescriptor.WHERE_PLUGINMENU, icon='plugin.png', fnc=main)]

