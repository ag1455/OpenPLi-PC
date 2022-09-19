#!/usr/bin/python
# -*- coding: utf-8 -*-

# for localized messages
from . import _
from Components.config import *
from Plugins.Plugin import PluginDescriptor

import os
import socket

from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Label import Label
from enigma import eConsoleAppContainer, eListboxPythonMultiContent, eTimer, eEPGCache, eServiceReference, getDesktop, gFont, loadPic, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_WRAP, addFont, iServiceInformation, iPlayableService
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

screenwidth = getDesktop(0).size()


try:
    cfg = config.plugins.JediMakerXtream
except:
    cfg = ""
    pass


epg_file = '/etc/enigma2/jediepgxtream/epglist.txt'
sourcelist = '/etc/enigma2/jediepgxtream/sources'
json_file = '/etc/enigma2/jediepgxtream/epg.json'

hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
         'Accept': 'ext/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' }


if os.path.isdir('/usr/lib/enigma2/python/Plugins/Extensions/EPGImport'):
    has_epg_importer = True
    if not os.path.exists('/etc/epgimport'):
        os.makedirs('/etc/epgimport')
else:
    has_epg_importer = False


def main(session, **kwargs):
    from . import main
    session.open(main.JediEPGXtream_Main)
    return


def Plugins(**kwargs):
    fontpath = '/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/fonts/'
    addFont(fontpath + 'Etelka-Text-Pro.ttf', 'jediepgregular', 100, 0)

    iconFile = 'icons/JediEPGXtream.png'
    if screenwidth.width() > 1280:
        iconFile = 'icons/JediEPGXtreamFHD.png'
    description = (_('Assign 3rd Party EPG to IPTV Channels'))
    pluginname = (_('JediEPGXtream'))

    result = PluginDescriptor(name = pluginname, description = description,where = PluginDescriptor.WHERE_PLUGINMENU,icon = iconFile,fnc = main)

    return result
