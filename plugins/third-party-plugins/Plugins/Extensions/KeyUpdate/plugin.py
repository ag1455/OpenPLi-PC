#!/bin/sh
################################################################
# Title:.......KeyUpdate                                       #
# Author:......audi06_19   2018                                #
# Support:.....www.dreamosat-forum.com                         #
# E-Mail:......admin@dreamosat-forum.com                       #
# Date:........26.11.2018                                      #
# Description:.KeyUpdate                                       #
################################################################

from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.MessageBox import MessageBox
import os
from os import remove, rename, system
import sys

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
    lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
    os_environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
    gettext.bindtextdomain("KeyUpdate", resolveFilename(SCOPE_PLUGINS, "Extensions/KeyUpdate/locale"))

def _(txt):
    t = gettext.dgettext("KeyUpdate", txt)
    if t == txt:
        print "[KeyUpdate] fallback to default translation for", txt
        t = gettext.gettext(txt)
    return t

localeInit()
language.addCallback(localeInit)

def menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('KeyUpdate'),
          main,
          'KeyUpdate',
          1)]
    return []
def runbackup(session, result):
    if result:
        session.open(Console, title=_('KeyUpdate'), cmdlist=["sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/KeyUpdate/KeyUpdate.sh"])

def main(session, **kwargs):
    session.openWithCallback(lambda r: runbackup(session, r), MessageBox, _('KeyUpdate \nKeyUpdate Do you want to update?'), MessageBox.TYPE_YESNO, timeout=20, default=True)

def Plugins(**kwargs):
    return [PluginDescriptor(name=_('KeyUpdate'), description=_('KeyUpdate for online Generator'), where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main, icon='plugin.png')]

