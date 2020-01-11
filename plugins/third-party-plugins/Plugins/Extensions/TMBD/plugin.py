# -*- coding: UTF-8 -*-
###############################################################################
# TMBD details plugin for enigma2
#
# Coded by Nikolasi and Dima73 (c) 2012
# Version: 4.0-rc2 (01.08.2012 22:00)
# Support: http://dream.altmaster.net
#
# This module is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program; if not, write to the Free Software Foundation, Inc., 59
# Temple Place, Suite 330, Boston, MA 0.1.2-1307 USA
###############################################################################

from Plugins.Plugin import PluginDescriptor
from twisted.web.client import downloadPage
from threading import Thread
from enigma import ePicLoad, eServiceReference, eTimer, eServiceCenter, getDesktop, ePoint, eSize
from Screens.Screen import Screen
from Screens.EpgSelection import EPGSelection
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarCueSheetSupport
from Screens.ChannelSelection import SimpleChannelSelection
from Screens.MovieSelection import MovieSelection, SelectionEventInfo
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.ChannelSelection import ChannelContextMenu, OFF, MODE_TV
from Screens.ChannelSelection import service_types_tv
from Components.ChoiceList import ChoiceEntryComponent
from Tools.BoundFunction import boundFunction
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.PluginComponent import plugins
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Button import Button
from Components.AVSwitch import AVSwitch
from Components.MenuList import MenuList
from Components.MovieList import MovieList
from Components.Language import language
from Components.Input import Input
from Components.ServiceEventTracker import InfoBarBase
from Screens.Console import Console
from Screens.InputBox import InputBox
from Components.ProgressBar import ProgressBar
from Components.Sources.StaticText import StaticText
from Components.EpgList import EPGList, EPG_TYPE_SINGLE, EPG_TYPE_MULTI
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Sources.Event import Event
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigText, getConfigListEntry, ConfigSelection, ConfigInteger
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from os import environ as os_environ
from os import environ, listdir
from Screens.VirtualKeyBoard import VirtualKeyBoard
import re
import os, sys
import gettext, random
import tmdb, urllib
import array, struct, fcntl
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SHUT_RDWR
from event import Event, ShortEventDescriptor, ExtendedEventDescriptor
from time import strftime, localtime, mktime
from meta import MetaParser, getctime, fileSize
from os import system as os_system, path as os_path


TMDB_LANGUAGE_CODES = {
  'en': 'eng',
  'ru': 'rus',
  'fr': 'fra',
  'bg': 'bul',
  'it': 'ita',
  'po': 'pol',
  'lv': 'lav',
  'de': 'ger',
  'da': 'dan',
  'nl': 'dut',
  'fi': 'fin',
  'el': 'gre',
  'he': 'heb',
  'hu': 'hun',
  'no': 'nor',
  'pt': 'por',
  'ro': 'ron',
  'sk': 'slo',
  'sl': 'slv',
  'es': 'est',
  'sv': 'swe',
  'tr': 'tur',
  'uk': 'ukr',
  'cz': 'cze'
}


SIOCGIFCONF = 0x8912
BYTES = 4096

def localeInit():
	lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
	os_environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
	gettext.bindtextdomain("TMBD", resolveFilename(SCOPE_PLUGINS, "Extensions/TMBD/locale"))

def _(txt):
	t = gettext.dgettext("TMBD", txt)
	if t == txt:
		print("[TMBD] fallback to default translation for", txt)
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)

def GetLanguageCode():
	lang = config.plugins.tmbd.locale.value
	return TMDB_LANGUAGE_CODES.get(lang, 'rus')

config.plugins.tmbd = ConfigSubsection()
config.plugins.tmbd.locale = ConfigText(default="ru")
config.plugins.tmbd.skins = ConfigSelection(default = "0", choices = [
                        ("0", _("Small poster")), ("1", _("Large poster"))])
config.plugins.tmbd.enabled = ConfigYesNo(default=True)
config.plugins.tmbd.virtual_text = ConfigSelection(default = "0", choices = [
                         ("0", _("< empty >")), ("1", _("< text >"))])
config.plugins.tmbd.menu = ConfigYesNo(default=True)
config.plugins.tmbd.add_tmbd_to_epg = ConfigYesNo(default=False)
config.plugins.tmbd.add_tmbd_to_multi = ConfigYesNo(default=False)
config.plugins.tmbd.add_tmbd_to_graph = ConfigYesNo(default=False)
config.plugins.tmbd.add_ext_menu = ConfigYesNo(default=False)
config.plugins.tmbd.test_connect = ConfigYesNo(default=False)
config.plugins.tmbd.exit_key = ConfigSelection(default = "0", choices = [
                        ("0", _("close")), ("1", _("ask user"))])
config.plugins.tmbd.position_x = ConfigInteger(default=100)
config.plugins.tmbd.position_y = ConfigInteger(default=100)
config.plugins.tmbd.new_movieselect = ConfigYesNo(default=True)
config.plugins.tmbd.size = ConfigSelection(choices=["285x398", "185x278", "130x200", "104x150"], default="130x200")

SKIN = """
	<screen position="0,0" size="130,200" zPosition="10" flags="wfNoBorder" backgroundColor="#ff000000" >
		<widget name="background" position="0,0" size="130,200" zPosition="1" backgroundColor="#00000000" />
		<widget name="preview" position="0,0" size="130,200" zPosition="2" alphatest="blend"/>
	</screen>"""

baseGraphMultiEPG__init__ = None

def GraphMultiEPGInit():
	global baseGraphMultiEPG__init__
	try:
		from Plugins.Extensions.GraphMultiEPG.GraphMultiEpg import GraphMultiEPG
	except ImportError:
		return
	if baseGraphMultiEPG__init__ is None:
		baseGraphMultiEPG__init__ = GraphMultiEPG.__init__
	GraphMultiEPG.__init__ = GraphMultiEPG__init__

def GraphMultiEPG__init__(self, session, services, zapFunc=None, bouquetChangeCB=None, bouquetname=""):
	baseGraphMultiEPG__init__(self, session, services, zapFunc, bouquetChangeCB, bouquetname="")
	if config.plugins.tmbd.add_tmbd_to_graph.value:
		def showTMBD():
			from Plugins.Extensions.TMBD.plugin import TMBD
			cur = self["list"].getCurrent()
			if cur[0] is not None:
				name2 = cur[0].getEventName()
				name3 = name2.split("(")[0].strip()
				eventname = name3.replace('"', '').replace('Х/Ф', '').replace('М/Ф', '').replace('Х/ф', '').replace('.', '')
				self.session.open(TMBD, eventname, False)
		
		#self["actions"] = ActionMap(["InfobarEPGActions"], # key GUDE(only ETxx00)
		#self["tmbd_actions"] = ActionMap(["EPGSelectActions"],
		self["tmbd_actions"] = HelpableActionMap(self, "EPGSelectActions",
				{
					"info": (showTMBD, _("Lookup in TMBD")),
				}, -1)

def_SelectionEventInfo_updateEventInfo = None

def new_SelectionEventInfo_updateEventInfo(self):
	serviceref = self.getCurrent()
	if config.plugins.tmbd.new_movieselect.value:
		if serviceref and serviceref.type == eServiceReference.idUser+1:
			import os
			pathname = serviceref.getPath()
			if len(pathname) > 2 and os.path.exists(pathname[:-2]+'eit'):
				serviceref = eServiceReference(serviceref.toString())
				serviceref.type = eServiceReference.idDVB
	self["Service"].newService(serviceref)

def_MovieSelection_showEventInformation = None
	
def new_MovieSelection_showEventInformation(self):
	from Screens.EventView import EventViewSimple
	from ServiceReference import ServiceReference
	evt = self["list"].getCurrentEvent()
	if not evt:
		import os;
		l = self["list"].l.getCurrentSelection()
		serviceref = l[0];
		pathname = serviceref and serviceref.getPath() or '';
		if len(pathname) > 2 and os.path.exists(pathname[:-2]+'eit'):
			serviceref = eServiceReference(serviceref.toString());
			serviceref.type = eServiceReference.idDVB;
			info = eServiceCenter.getInstance().info(serviceref);
			evt = info and info.getEvent(serviceref);
	if evt:
		self.session.open(EventViewSimple, evt, ServiceReference(self.getCurrent()))

baseEPGSelection__init__ = None
def EPGSelectionInit():
	global baseEPGSelection__init__
	if baseEPGSelection__init__ is None:
		baseEPGSelection__init__ = EPGSelection.__init__
	EPGSelection.__init__ = EPGSelection__init__


def EPGSelection__init__(self, session, service, zapFunc=None, eventid=None, bouquetChangeCB=None, serviceChangeCB=None):
	baseEPGSelection__init__(self, session, service, zapFunc, eventid, bouquetChangeCB, serviceChangeCB)
	if self.type != EPG_TYPE_MULTI and config.plugins.tmbd.add_tmbd_to_epg.value:
		def redPressed():
			from Plugins.Extensions.TMBD.plugin import TMBD
			cur = self["list"].getCurrent()
			if cur[0] is not None:
				name2 = cur[0].getEventName()
				name3 = name2.split("(")[0].strip()
				eventname = name3.replace('"', '').replace('Х/Ф', '').replace('М/Ф', '').replace('Х/ф', '').replace('.', '')
				self.session.open(TMBD, eventname, False)


		self["tmbdActions"] = ActionMap(["EPGSelectActions"],
				{
					"red": redPressed,
				})
		self["key_red"].text = _("Lookup in TMBD")

	elif self.type == EPG_TYPE_MULTI and config.plugins.tmbd.add_tmbd_to_multi.value:
		def infoKeyPressed():
			from Plugins.Extensions.TMBD.plugin import TMBD
			cur = self["list"].getCurrent()
			if cur[0] is not None:
				name2 = cur[0].getEventName()
				name3 = name2.split("(")[0].strip()
				eventname = name3.replace('"', '').replace('Х/Ф', '').replace('М/Ф', '').replace('Х/ф', '').replace('.', '')
				self.session.open(TMBD, eventname, False)

		self["Tmbdactions"] = ActionMap(["EPGSelectActions"],
				{
					"info": infoKeyPressed,
				})

baseChannelContextMenu__init__ = None
def TMBDChannelContextMenuInit():
	global baseChannelContextMenu__init__
	if baseChannelContextMenu__init__ is None:
		baseChannelContextMenu__init__ = ChannelContextMenu.__init__
	ChannelContextMenu.__init__ = TMBDChannelContextMenu__init__
	# new methods
        ChannelContextMenu.showServiceInformations2 = showServiceInformations2

def TMBDChannelContextMenu__init__(self, session, csel):
	baseChannelContextMenu__init__(self, session, csel)
	if csel.mode == MODE_TV:
                current = csel.getCurrentSelection()
		current_root = csel.getRoot()
		current_sel_path = current.getPath()
		current_sel_flags = current.flags
		inBouquetRootList = current_root and current_root.getPath().find('FROM BOUQUET "bouquets.') != -1 #FIXME HACK
		inBouquet = csel.getMutableList() is not None
		isPlayable = not (current_sel_flags & (eServiceReference.isMarker|eServiceReference.isDirectory))
		if isPlayable:
			      if config.plugins.tmbd.menu.value:
			              callFunction = self.showServiceInformations2
                                      self["menu"].list.insert(0, ChoiceEntryComponent(text = (_("TMBD Details"), boundFunction(callFunction,1))))
                              else:
                                      pass

def showServiceInformations2(self, eventName=""):
        global eventname
        s = self.csel.servicelist.getCurrent()
        info = s and eServiceCenter.getInstance().info(s)
        event = info and info.getEvent(s)
        if event != None:
                try:
                        epg_name = event.getEventName() or ''
                        eventName = epg_name.replace('"', '').replace('Х/Ф', '').replace('М/Ф', '').replace('Х/ф', '').replace('.', '')
                        eventname = eventName
	                self.session.open(TMBD, eventName)
	        except ImportError as ie:
                        pass


class TMBDChannelSelection(SimpleChannelSelection):
	def __init__(self, session):
		SimpleChannelSelection.__init__(self, session, _("Channel Selection"))
		self.skinName = "SimpleChannelSelection"

		self["ChannelSelectEPGActions"] = ActionMap(["ChannelSelectEPGActions"],
			{
				"showEPGList": self.channelSelected
			}
		)

	def channelSelected(self):
		ref = self.getCurrentSelection()
		if (ref.flags & 7) == 7:
			self.enterPath(ref)
		elif not (ref.flags & eServiceReference.isMarker):
			self.session.openWithCallback(
				self.epgClosed,
				TMBDEPGSelection,
				ref,
				openPlugin = False
			)

	def epgClosed(self, ret = None):
		if ret:
			self.close(ret)

class TMBDEPGSelection(EPGSelection):
	def __init__(self, session, ref, openPlugin = True):
		EPGSelection.__init__(self, session, ref)
		self.skinName = "EPGSelection"
		self["key_red"].setText(_("Lookup in TMBD"))
		self.openPlugin = openPlugin


	def zapTo(self):
                global eventname
                eventname = ""
                name2 = ""
                name3 = ""
		cur = self["list"].getCurrent()
		evt = cur[0]
		if evt != None:
			sref = cur[1]
			name2 = evt.getEventName()
			name3 = name2.split("(")[0].strip()
			eventname = name3.replace('"', '').replace('Х/Ф', '').replace('М/Ф', '').replace('Х/ф', '').replace('.', '')


		if self.openPlugin:
			self.session.open(
				TMBD,
				eventname
			)
		else:
			self.close(eventname)
			
	def eventSelected(self):
		self.zapTo()

testOK = None
HDSkn = False
movie2 = ""
class TMBD(Screen):

        skin_hd1 = """
  <screen name="TMBD" position="90,90" size="1100,570" title="TMBD Details Plugin">
    <eLabel backgroundColor="#00bbbbbb" position="0,0" size="1100,2" />
    <widget font="Regular;22" name="titellabel" position="20,20" size="760,28" transparent="1" valign="center" />
    <widget alphatest="blend" name="starsbg" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/starsbar_empty.png" position="790,10" size="210,21" zPosition="2" />
    <widget name="stars" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/starsbar_filled.png" position="790,10"  size="210,21" transparent="1" zPosition="3" />
    <widget font="Regular;20" halign="left" name="ratinglabel" foregroundColor="#00f0b400" position="790,34" size="210,23" transparent="1" />
    <widget font="Regular;20" name="voteslabel" halign="left" position="790,57" size="290,23" foregroundColor="#00f0b400" transparent="1" />
    <widget alphatest="blend" name="poster" position="30,60" size="285,398" />
    <widget name="menu" position="325,100" scrollbarMode="showOnDemand" size="750,130" zPosition="3"  selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/ig/button1080x25.png" />
    <widget name="detailslabel" position="325,59" size="570,35" font="Regular;19" transparent="1" />
    <widget font="Regular;20" name="castlabel" position="320,245" size="760,240" transparent="1" />
    <widget font="Regular;20" name="extralabel" position="320,77" size="760,180" transparent="1" />
    <widget font="Regular;18" name="statusbar" position="10,490" size="1080,20" transparent="1" />
    <eLabel backgroundColor="#00bbbbbb" position="0,518" size="1100,2" />
    <ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/ig/red25.png" position=" 20,532" size="250,38" zPosition="1" />
    <ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/ig/green25.png" position="290,532" size="250,38" zPosition="1" />
    <ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/ig/yellow25.png" position="560,532" size="250,38" zPosition="1" />
    <ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/ig/blue25.png" position="830,532" size="250,38" zPosition="1" />
    <ePixmap pixmap="skin_default/buttons/key_menu.png" position="1048,5" zPosition="1" size="35,25" alphatest="on" />
    <ePixmap pixmap="skin_default/buttons/key_info.png" position="1048,35" zPosition="1" size="35,25" alphatest="on" />
    <widget backgroundColor="#9f1313" font="Regular;20" foregroundColor="#00ff2525" halign="center" name="key_red" position=" 20,536" size="250,38" transparent="1" valign="center" zPosition="2" />
    <widget backgroundColor="#1f771f" font="Regular;20" foregroundColor="#00389416" halign="center" name="key_green" position="290,536" size="250,38" transparent="1" valign="center" zPosition="2" />
    <widget backgroundColor="#a08500" font="Regular;20" foregroundColor="#00bab329" halign="center" name="key_yellow" position="560,536" size="250,38" transparent="1" valign="center" zPosition="2" />
    <widget backgroundColor="#18188b" font="Regular;20" foregroundColor="#006565ff" halign="center" name="key_blue" position="830,536" size="250,38" transparent="1" valign="center" zPosition="2" />
  </screen>"""

        skin_hd = """
  <screen name="TMBD" position="90,90" size="1100,570" title="TMBD Details Plugin">
    <eLabel backgroundColor="#00bbbbbb" position="0,0" size="1100,2" />
    <widget font="Regular;22" name="titellabel" position="20,20" size="760,28" transparent="1" valign="center" />
    <widget alphatest="blend" name="starsbg" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/starsbar_empty.png" position="790,10" size="210,21" zPosition="2" />
    <widget name="stars" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/starsbar_filled.png" position="790,10" size="210,21" transparent="1" zPosition="3" />
    <widget font="Regular;20" foregroundColor="#00f0b400" halign="left" name="ratinglabel" position="790,34" size="210,23" transparent="1" />
    <widget font="Regular;20" halign="left" name="voteslabel" position="790,57" size="290,23" foregroundColor="#00f0b400" transparent="1" />
    <widget alphatest="blend" name="poster" position="30,60" size="110,180" />
    <widget name="menu" position="170,100" scrollbarMode="showOnDemand" size="920,130" zPosition="3" />
    <widget name="detailslabel" position="325,59" size="570,35" font="Regular;19" transparent="1" />
    <widget font="Regular;20" name="castlabel" position="20,245" size="1060,240" transparent="1" />
    <widget font="Regular;20" name="extralabel" position="164,77" size="920,180" transparent="1" />
    <widget font="Regular;18" foregroundColor="#00cccccc" name="statusbar" position="10,490" size="1080,20" transparent="1" />
    <eLabel backgroundColor="#00bbbbbb" position="0,518" size="1100,2" />
    <ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/ig/red25.png" position=" 20,532" size="250,38" zPosition="1" />
    <ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/ig/green25.png" position="290,532" size="250,38" zPosition="1" />
    <ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/ig/yellow25.png" position="560,532" size="250,38" zPosition="1" />
    <ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/ig/blue25.png" position="830,532" size="250,38" zPosition="1" />
    <ePixmap pixmap="skin_default/buttons/key_menu.png" position="1048,5" zPosition="1" size="35,25" alphatest="on" />
    <ePixmap pixmap="skin_default/buttons/key_info.png" position="1048,35" zPosition="1" size="35,25" alphatest="on" />
    <widget backgroundColor="#9f1313" font="Regular;20" foregroundColor="#00ff2525" halign="center" name="key_red" position=" 20,536" size="250,38" transparent="1" valign="center" zPosition="2" />
    <widget backgroundColor="#1f771f" font="Regular;20" foregroundColor="#00389416" halign="center" name="key_green" position="290,536" size="250,38" transparent="1" valign="center" zPosition="2" />
    <widget backgroundColor="#a08500" font="Regular;20" foregroundColor="#00bab329" halign="center" name="key_yellow" position="560,536" size="250,38" transparent="1" valign="center" zPosition="2" />
    <widget backgroundColor="#18188b" font="Regular;20" foregroundColor="#006565ff" halign="center" name="key_blue" position="830,536" size="250,38" transparent="1" valign="center" zPosition="2" />
  </screen>"""

        skin_sd = """
  <screen name="TMBD" position="center,center" size="600,420" title="TMBD Details Plugin" >
    <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
    <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
    <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
    <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
    <ePixmap pixmap="skin_default/buttons/key_menu.png" position="565,5" zPosition="0" size="35,25" alphatest="on" />
    <ePixmap pixmap="skin_default/buttons/key_info.png" position="565,33" zPosition="1" size="35,25" alphatest="on" />
    <widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;18" valign="center" halign="center" backgroundColor="#9f1313" transparent="1" />
    <widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;18" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
    <widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;18" valign="center" halign="center" backgroundColor="#a08500" transparent="1" />
    <widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;18" valign="center" halign="center" backgroundColor="#18188b" transparent="1" />
    <widget source="title" render="Label" position="10,40" size="330,45" valign="center" font="Regular;20"/>
    <widget name="extralabel" position="105,90" size="485,140" font="Regular;18" />
    <widget name="castlabel" position="10,235" size="580,155" font="Regular;18"  zPosition="3"/>
    <widget name="ratinglabel" position="340,62" size="250,20" halign="center" font="Regular;18" foregroundColor="#f0b400"/>
    <widget name="statusbar" position="10,404" size="580,16" font="Regular;16" foregroundColor="#cccccc" />
    <widget font="Regular;16" halign="center" name="voteslabel" foregroundColor="#00f0b400" position="380,404" size="210,16" transparent="1" />
    <widget name="poster" position="4,90" size="96,140" alphatest="on" />
    <widget name="menu" position="105,90" size="485,140" zPosition="2" scrollbarMode="showOnDemand" />
    <widget name="starsbg" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/starsbar_empty.png" position="340,40" zPosition="0" size="210,21" transparent="1" alphatest="on" />
    <widget name="stars" position="340,40" size="210,21" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/starsbar_filled.png" transparent="1" />

  </screen>"""

        def __chooseSkin(self):
	      try:
	        screenWidth = getDesktop(0).size().width()
	      except:
	        screenWidth = 720
	      print "Screen width=%d" % (screenWidth)

	      if (screenWidth == 1280):
                      if config.plugins.tmbd.skins.value == "0":
	                      return TMBD.skin_hd
	              if config.plugins.tmbd.skins.value == "1":
                              return TMBD.skin_hd1
	      else:
	        return TMBD.skin_sd
	
	def __init__(self, session, eventName, callbackNeeded=False, movielist = False):
		Screen.__init__(self, session)
		self.skin=self.__chooseSkin()
		self.eventName = eventName
		self.curResult = False
		self.noExit = False
		self.onShow.append(self.selectionChanged)
		self.movielist = movielist
		self.callbackNeeded = callbackNeeded
		self.callbackData = ""
		self.callbackGenre = ""
		self["poster"] = Pixmap()
		self.picload = ePicLoad()
		self.picload.PictureData.get().append(self.paintPosterPixmapCB)
		self["stars"] = ProgressBar()
		self["starsbg"] = Pixmap()
		self["stars"].hide()
		self["starsbg"].hide()
		self.ratingstars = -1
		self.working = False
		self["title"] = StaticText(_("The Internet Movie Database"))
		# map new source -> old component
		def setText(txt):
			StaticText.setText(self["title"], txt)
			self["titellabel"].setText(txt)
		self["title"].setText = setText
		self["titellabel"] = Label()
		self["detailslabel"] = ScrollLabel("")
		self["castlabel"] = ScrollLabel("")
		self["extralabel"] = ScrollLabel("")
		self["statusbar"] = Label("")
		self["ratinglabel"] = Label("")
		self["voteslabel"] = Label("")
		self.resultlist = []
		self["menu"] = MenuList(self.resultlist)
		self["menu"].hide()
		self["menu"].onSelectionChanged.append(self.selectionChanged)
		self["key_red"] = Button(_("Exit"))
		self["key_green"] = Button("")
		self["key_yellow"] = Button("")
		self["key_blue"] = Button(_("Manual input"))
		# 0 = multiple query selection menu page
		# 1 = movie info page
		# 2 = extra infos page
		self.Page = 0
		self.working = False
		self.refreshTimer = eTimer()
		self.refreshTimer.callback.append(self.TMBDPoster)

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "MovieSelectionActions", "DirectionActions"],
		{
			"ok": self.showExtras,
			"cancel": self.exit2,
			"down": self.pageDown,
			"up": self.pageUp,
			"left": self.scrollLabelPageUp,
			"right": self.scrollLabelPageDown,
			"red": self.exit,
			"green": self.searchYttrailer2,
			"yellow": self.showExtras,
			"blue": self.openVirtualKeyBoard,
			"contextMenu": self.contextMenuPressed,
			"showEventInfo": self.aboutAutor
		}, -1)
		
		self.setTitle(_("TMBD Details Plugin..."))
		self.removCovers()
		self.testThread = None
		self.testTime = 2.0		# 1 seconds
		self.testHost = "www.themoviedb.org"
		self.testPort = 80		# www port
		if config.plugins.tmbd.test_connect.value:
			self.TestConnection()
		else:
			self.getTMBD()


	def TestConnection(self):
		self.testThread = Thread(target=self.test)
		self.testThread.start()

	def get_iface_list(self):
		names = array.array('B', '\0' * BYTES)
		sck = socket(AF_INET, SOCK_DGRAM)
		bytelen = struct.unpack('iL', fcntl.ioctl(sck.fileno(), SIOCGIFCONF, struct.pack('iL', BYTES, names.buffer_info()[0])))[0]
		sck.close()
		namestr = names.tostring()
		return [namestr[i:i+32].split('\0', 1)[0] for i in range(0, bytelen, 32)]

	def test(self):
		global testOK
		link = "down"
		for iface in self.get_iface_list():
			if "lo" in iface: continue
			if os_path.exists("/sys/class/net/%s/operstate"%(iface)):
				fd = open("/sys/class/net/%s/operstate"%(iface), "r")
				link = fd.read().strip()
				fd.close()
			if link != "down": break
		if link != "down":
			s = socket(AF_INET, SOCK_STREAM)
			s.settimeout(self.testTime)
			try:
				testOK = not bool(s.connect_ex((self.testHost, self.testPort)))
			except:
				testOK = None
			if not testOK:
				print 'Conection failed'
				self.resetLabels()
				self["statusbar"].setText(_("No connect to www.themoviedb.org"))
				return
			else:
				s.shutdown(SHUT_RDWR)
				self.getTMBD()
			s.close()
		else:
			testOK = None
			self.resetLabels()
			self["statusbar"].setText(_("No connect to www.themoviedb.org"))
			return


	def exit(self):
		self.close()

	def exit2(self):
		if config.plugins.tmbd.exit_key.value == "1":
			self.session.openWithCallback(self.exitConfirmed, MessageBox, _("Close plugin?"), MessageBox.TYPE_YESNO)
		else:
			self.exit()

	def exitConfirmed(self, answer):
		if answer:
			self.close()

	def aboutAutor(self):
		self.session.open(MessageBox, _("TMBD Details Plugin\nDeveloper: Nikolasi,vlamo,Dima73\n(c)2012"), MessageBox.TYPE_INFO)
		
	def removCovers(self):
		os.system('[ -e /tmp/preview.jpg ] && rm -rf /tmp/preview.jpg')


	def resetLabels(self):
		self["detailslabel"].setText("")
		self["ratinglabel"].setText("")
		self["title"].setText(_("The Internet Movie Database"))
		self["castlabel"].setText("")
		self["titellabel"].setText("")
		self["extralabel"].setText("")
		self["voteslabel"].setText("")
		self["key_green"].setText("")
		self.ratingstars = -1

	def pageUp(self):
		if self.Page == 0:
			self["menu"].instance.moveSelection(self["menu"].instance.moveUp)
			self["castlabel"].pageUp()
		if self.Page == 1:
			self["extralabel"].pageUp()


	def pageDown(self):
		if self.Page == 0:
			self["menu"].instance.moveSelection(self["menu"].instance.moveDown)
			self["castlabel"].pageUp()
		if self.Page == 1:
			self["extralabel"].pageDown()
        def scrollLabelPageUp(self):
                self["castlabel"].pageUp()

        def scrollLabelPageDown(self):
                self["castlabel"].pageDown()


	def showMenu(self):
		global eventname, total
		self.noExit = False
		if self.curResult:
			self["menu"].show()
			self["ratinglabel"].show()
			self["castlabel"].show()
			self["poster"].show()
			self["extralabel"].hide()
			self["title"].setText(_("Search results for: %s") % (eventname))
			if total > 1:
				self["detailslabel"].setText(_("Please select the matching entry:"))
			self["detailslabel"].show()
			self["key_blue"].setText(_("Manual input"))
			if self.movielist:
				self["key_green"].setText(_("Save info / poster"))
			else:
				self["key_green"].setText(_("Search Trailer"))
			self["key_yellow"].setText(_("Show movie details"))
			if self.ratingstars > 0:
				self["starsbg"].show()
				self["stars"].show()
				self["stars"].setValue(self.ratingstars)
			self.working = True


	def showExtras(self):
		if self.curResult:
			if not self.noExit:
				self.Page = 1
				self.noExit = True
				self["menu"].hide()
				self["extralabel"].show()
				self["detailslabel"].hide()
				self["key_yellow"].setText("")
				self.showExtras2()
			else:
				self.Page = 0
				self.noExit = False
				self.showMenu()


	def showExtras2(self):
		if self.curResult:
			current = self["menu"].l.getCurrentSelection()
			def tryGetInfo(cast, column):
				try:
					return cast[column]
				except KeyError:
					return (_('Not available'))
			if current:
				cast = current[1]
				self["key_yellow"].setText(_("Show search results"))
				namedetals = self['menu'].l.getCurrentSelection()[0]
				self["title"].setText(_("Details for: %s") % (namedetals))
				ids = cast["id"].encode("utf-8")
				cast = tmdb.getMovieInfo(ids)['cast']
				Extratext = ""
				genres = tryGetInfo(cast, 'genre')
				if genres != _('Not available'):
					Extratext += "%s: %s\n" % (_("Genre"), genres)
				directors = tryGetInfo(cast, 'director')
				if directors != _('Not available'):
					Extratext += "%s: %s\n" % (_("Director"), directors)
				producers = tryGetInfo(cast, 'producer')
				if producers != _('Not available'):
					Extratext += "%s: %s\n" % (_("Producers"), producers)
				actors = tryGetInfo(cast, 'actor')
				if actors != _('Not available'):
					Extratext += "%s: %s\n" % (_("Actors"), actors)
				cast3 = tmdb.getMovieInfo(ids)['countries']
				Extratext2 = ""
				if cast3 and cast3 != "":
					Extratext2 = "%s: %s\n" % (_("Country"), cast3)
				cast4 = tmdb.getMovieInfo(ids)['studios']
				if cast4 and cast4 != _('Not available'):
					Extratext2 += "%s: %s\n" % (_("Studios"), cast4)
				self["extralabel"].setText("%s%s" % (Extratext2, Extratext))

	def removmenu(self):
		list = [
			(_("Current poster and info"), self.removcurrent),
			(_("Only current poster"), self.removcurrentposter),
			(_("Only current info"), self.removcurrentinfo),
			(_("All posters for movie"), self.removresult),
		]
		self.session.openWithCallback(
			self.menuCallback,
			ChoiceBox,
			list = list,
			title= _("What exactly do you want to delete?"),
		)

	def contextMenuPressed(self):
		if self.movielist:
			list = [
				(_("Text editing"), self.openKeyBoard),
				(_("Select from Favourites"), self.openChannelSelection),
				(_("Search Trailer"), self.searchYttrailer3),
				(_("Remove poster / info"), self.removmenu),
				(_("Settings"), self.Menu2),
			]
		else:
			list = [
				(_("Text editing"), self.openKeyBoard),
				(_("Select from Favourites"), self.openChannelSelection),
				(_("Settings"), self.Menu2),
			]
		self.session.openWithCallback(
			self.menuCallback,
			ChoiceBox,
			list = list,
			title= _("Select action:"),
		)

	def Menu2(self):
		self.session.openWithCallback(self.workingFinished, Settings)

	def saveresult(self):
		global name
		list = [
			(_("Yes"), self.savePosterInfo),
			(_("Yes,but write new meta-file"), self.writeMeta),
			(_("No"), self.exitChoice),
		]
		self.session.openWithCallback(
			self.menuCallback,
			ChoiceBox,
			title= _("Save poster and info for:\n %s ?") % (name),
			list = list,
		)

	def exitChoice(self):
		self.close()
		
	def savePosterInfo(self):
		global name
		import os
		import shutil
		if self.curResult:
			self.savedescrip()
		if not fileExists("/media/hdd/covers"):
			try:
				os.makedirs("/media/hdd/covers")
			except OSError:
				pass
		if fileExists("/media/hdd/covers"):
			try:
				if fileExists("/tmp/preview.jpg"):
					shutil.copy2("/tmp/preview.jpg", "/media/hdd/covers/" + name + ".jpg")
					self.session.open(MessageBox, _("Poster %s saved!") % (name), MessageBox.TYPE_INFO, timeout=2)
			except OSError:
				pass

	def writeMeta(self):
		if self.curResult:
			global name, movie2, eventname
			Extratext2 = ""
			namedetals2 = ""
			def tryGetInfo(cast, column):
				try:
					return cast[column]
				except KeyError:
					return ""
			if len(movie2):
					TSFILE = movie2
			else:
				return
			current = self["menu"].l.getCurrentSelection()
			if current:
				namedetals2 = self['menu'].l.getCurrentSelection()[0]
				cast = current[1]
				ids = cast["id"].encode("utf-8")
				cast = tmdb.getMovieInfo(ids)['cast']
				genres = tryGetInfo(cast, 'genre')
				cast3 = tmdb.getMovieInfo(ids)['countries']
				namedetals2 = namedetals2[:-7]
				if movie2.endswith(".ts"):
					name = namedetals2
				else:
					Extratext2 = "%s /" % ( namedetals2)
				if genres != "":
					Extratext2 += " %s /" % ( genres)
				if cast3 and cast3 != "":
					Extratext2 += " %s /" % ( cast3)
				actors = tryGetInfo(cast, 'actor')
				if actors != "":
					Extratext2 += " %s" % ( actors)
				metaParser = MetaParser();
				metaParser.name = namedetals2
				metaParser.description = Extratext2;
				if os.path.exists(TSFILE + '.meta') and movie2.endswith(".ts"):
					readmetafile = open("%s.meta"%(movie2), "r")
					linecnt = 0
					line = readmetafile.readline()
					if line:
						line = line.strip()
						if linecnt == 0:
							metaParser.ref = eServiceReference(line)
					else:
						metaParser.ref = eServiceReference('1:0:0:0:0:0:0:0:0:0:')
					readmetafile.close()
				else:
					metaParser.ref = eServiceReference('1:0:0:0:0:0:0:0:0:0:')
				metaParser.time_create = getctime(TSFILE);
				metaParser.tags = '';
				metaParser.length = 0;
				metaParser.filesize = fileSize(TSFILE);
				metaParser.service_data = '';
				metaParser.data_ok = 1;
				metaParser.updateMeta(TSFILE);
				self.session.open(MessageBox, _("Write to new meta-file for:\n") + "%s" % (TSFILE), MessageBox.TYPE_INFO, timeout=3)
				self.timer = eTimer()
				self.timer.callback.append(self.savePosterInfo)
				self.timer.start(1500, True)



	def savedescrip(self):
		global name, movie2
		descrip = ""
		Extratext = ""
		namedetals = ""
		def tryGetInfo(cast, column):
			try:
				return cast[column]
			except KeyError:
				return ""
		if len(movie2):
				EITFILE = movie2[:-2] + 'eit'
		else:
			return
		current = self["menu"].l.getCurrentSelection()
		if current:
			namedetals = self['menu'].l.getCurrentSelection()[0]
			cast = current[1]
			cast2 = current[1]
			ids = cast["id"].encode("utf-8")
			cast = tmdb.getMovieInfo(ids)['cast']
			genres = tryGetInfo(cast, 'genre')
			cast3 = tmdb.getMovieInfo(ids)['countries']
			if cast3 and cast3 != "":
				Extratext = "%s %s\n" % (_("Country:"), cast3)
			if genres != "":
				Extratext += "%s %s\n" % (_("Genre:"), genres)
			try:
				descrip = " %s\n" % cast2['overview'].encode("utf-8")
			except:
				descrip = _('Not available...\n')
			try:
				runtimes = "%s" % self.textNo(str(cast2['runtime'].encode("utf-8")))
				if runtimes != (_('0 min.')):
					descrip += " %s" % (runtimes)
			except:
				print 'no answer'
			try:
				rating = str(cast2['rating'])
				votes = str(cast2['votes'])
			except:
				rating = "0.0"
				votes ="0"
			if rating != "0.0" and votes != "0":
				descrip += _(" User Rating: ") + rating + "/10" + _(" (%s times)\n") % (votes)
			actors = tryGetInfo(cast, 'actor')
			if actors != "":
				descrip += " %s %s\n" % (_("Actors:"), actors)
			Extratext = Extratext.replace('\xc2\xab', '"').replace('\xc2\xbb', '"').replace('\xe2\x80\xa6', '...').replace('\xe2\x80\x94', '-');
			Extratext = self.Cutext(Extratext)
			descrip = descrip.replace('\xc2\xab', '"').replace('\xc2\xbb', '"').replace('\xe2\x80\xa6', '...').replace('\xe2\x80\x94', '-');
			namedetals = namedetals.replace('\xc2\xab', '"').replace('\xc2\xbb', '"').replace('\xe2\x80\xa6', '...').replace('\xe2\x80\x94', '-');
			sed = ShortEventDescriptor([]);
			sed.setIso639LanguageCode(GetLanguageCode());
			sed.setEventName(namedetals);
			sed.setText(Extratext);
			eed = ExtendedEventDescriptor([]);
			eed.setIso639LanguageCode(GetLanguageCode());
			eed.setText(descrip);
			newEvent = Event();
			newEvent.setShortEventDescriptor(sed);
			newEvent.setExtendedEventDescriptor(eed);
			ret = newEvent.saveToFile(EITFILE);
			self.session.open(MessageBox, _("Write event to new eit-file:\n") + "%s\n" % (EITFILE) + _("%d bytes") % (ret), MessageBox.TYPE_INFO, timeout=3)

	def Cutext(self, text):
		if text > 0:
			return text[:179]
		else:
			return text

	def removcurrent(self):
		global name
		self.session.openWithCallback(self.removcurrentConfirmed, MessageBox, _("Remove current poster and info for:\n%s ?") % (name), MessageBox.TYPE_YESNO)


	def removcurrentposter(self):
		global movie2, name
		if len(movie2):
			dir_cover = '/media/hdd/covers/'
			if movie2.endswith(".ts"):
				if os.path.exists(movie2 + '.meta'):
					try:
						readmetafile = open("%s.meta"%(movie2), "r")
						name_cur = readmetafile.readline()[0:-1]
						name_cover = name_cur + '.jpg'
					except:
						name_cover = ""
					readmetafile.close()
				else:
					name_cover = name + '.jpg'
			else:
					name_cover = name + '.jpg'
			remove_jpg = dir_cover + name_cover
			if os.path.exists(remove_jpg):
				try:
					os.remove(remove_jpg)
					self.session.open(MessageBox, _("%s poster removed!") % (remove_jpg), MessageBox.TYPE_INFO, timeout=3)
				except:
					pass
		else:
			return

	def removcurrentinfo(self):
		global movie2, name
		if len(movie2):
			remove_eit = movie2[:-2] + 'eit'
			if os.path.exists(remove_eit):
				try:
					os.remove(remove_eit)
					self.session.open(MessageBox, _("%s eit-file removed!") % (remove_eit), MessageBox.TYPE_INFO, timeout=3)
				except:
					pass
			remove_meta = movie2 + '.meta'
			if os.path.exists(remove_meta):
				try:
					os.remove(remove_meta)
					self.session.open(MessageBox, _("%s meta-file removed!") % (remove_meta), MessageBox.TYPE_INFO, timeout=3)
				except:
					pass
		else:
			return

	def removcurrentConfirmed(self, confirmed):
		if not confirmed:
			return
		else:
			global movie2, name
			if len(movie2):
				dir_cover = '/media/hdd/covers/'
				remove_eit = movie2[:-2] + 'eit'
				if os.path.exists(remove_eit):
					try:
						os.remove(remove_eit)
						self.session.open(MessageBox, _("%s eit-file removed!") % (remove_eit), MessageBox.TYPE_INFO, timeout=3)
					except:
						pass
				if movie2.endswith(".ts"):
					if os.path.exists(movie2 + '.meta'):
						try:
							readmetafile = open("%s.meta"%(movie2), "r")
							name_cur = readmetafile.readline()[0:-1]
							name_cover = name_cur + '.jpg'
						except:
							name_cover = ""
						readmetafile.close()
					else:
						name_cover = name + '.jpg'
				else:
					name_cover = name + '.jpg'
				remove_jpg = dir_cover + name_cover
				if os.path.exists(remove_jpg):
					try:
						os.remove(remove_jpg)
						self.session.open(MessageBox, _("%s poster removed!") % (remove_jpg), MessageBox.TYPE_INFO, timeout=3)
					except:
						pass
				remove_meta = movie2 + '.meta'
				if os.path.exists(remove_meta):
					try:
						os.remove(remove_meta)
						self.session.open(MessageBox, _("%s meta-file removed!") % (remove_meta), MessageBox.TYPE_INFO, timeout=3)
					except:
						pass
			else:
				return

	def removresult(self):
		self.session.openWithCallback(self.removresultConfirmed, MessageBox, _("Remove all posters?"), MessageBox.TYPE_YESNO)

	def removresultConfirmed(self, confirmed):
		import os
		import shutil
		if not confirmed:
			return
		else:
			if fileExists("/media/hdd/covers"):
				try:
					shutil.rmtree("/media/hdd/covers")
					self.session.open(MessageBox, _("All posters removed!"), MessageBox.TYPE_INFO, timeout=3)
				except OSError:
					pass

	def menuCallback(self, ret = None):
		ret and ret[1]()

	def searchYttrailer3(self):
		if fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/YTTrailer/plugin.pyc")) or fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/YTTrailer/plugin.pyc")):
			self.searchYttrailer()
		else:
			if fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/TMBD/enigma2-plugin-extensions-yttrailer_2.0_all.ipk")):
				self.session.openWithCallback(self.yesNo, MessageBox, _("YTTrailer is not installed.\nInstall YTTrailer now?"), MessageBox.TYPE_YESNO, default = False)
			else:
				self.session.openWithCallback(self.workingFinished, MessageBox, ("YTTrailer is not installed. Please install YTTrailer."), MessageBox.TYPE_INFO, timeout=5)

	def searchYttrailer2(self):
		if self.movielist and self.curResult:
			self.saveresult()
		else:
			if fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/YTTrailer/plugin.pyc")) or fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/YTTrailer/plugin.pyc")):
				self.searchYttrailer()
			else:
				if fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/TMBD/enigma2-plugin-extensions-yttrailer_2.0_all.ipk")):
					self.session.openWithCallback(self.yesNo, MessageBox, _("YTTrailer is not installed.\nInstall YTTrailer now?"), MessageBox.TYPE_YESNO, default = False)
				else:
					self.session.openWithCallback(self.workingFinished, MessageBox, ("YTTrailer is not installed. Please install YTTrailer."), MessageBox.TYPE_INFO, timeout=5)

	def yesNo(self, answer):
		if answer is True:
			self.yesInstall()

	def yesInstall(self):
		if fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/TMBD/enigma2-plugin-extensions-yttrailer_2.0_all.ipk")):
			cmd = "opkg install -force-overwrite -force-downgrade /usr/lib/enigma2/python/Plugins/Extensions/TMBD/enigma2-plugin-extensions-yttrailer_2.0_all.ipk"
			self.session.open(Console, _("Install YTTrailer..."), [cmd])

	def searchYttrailer(self):
		try:
			from Plugins.Extensions.YTTrailer.plugin import YTTrailerList, baseEPGSelection__init__
		except ImportError as ie:
			pass
		if baseEPGSelection__init__ is None:
			return
		if self.curResult:
			current = self["menu"].l.getCurrentSelection()
			if current:
				namedetals = self['menu'].l.getCurrentSelection()[0]
				namedetals = namedetals[:-7]
				self.session.open(YTTrailerList, namedetals)


	def workingFinished(self, callback=None):
		self.working = False

	def openKeyBoard(self):
		global eventname
		self.session.openWithCallback(
			self.gotSearchString,
			InputBox,
			title = _("Edit text to search for"), text=eventname, visible_width = 40, maxSize=False, type=Input.TEXT)


	def openVirtualKeyBoard(self):
		if config.plugins.tmbd.virtual_text.value == "0":
			self.session.openWithCallback(
				self.gotSearchString,
				VirtualKeyBoard,
				title = _("Enter text to search for")
			)
		else:
			global eventname
			self.session.openWithCallback(
				self.gotSearchString,
				VirtualKeyBoard,
				title = _("Edit text to search for"),
				text=eventname
			)

	def openChannelSelection(self):
		self.session.openWithCallback(
			self.gotSearchString,
			TMBDChannelSelection
		)

	def gotSearchString(self, ret = None):
		if ret:
			global total
			self.eventName = ret
			self.Page = 0
			self.resultlist = []
			self["menu"].hide()
			self["ratinglabel"].hide()
			self["castlabel"].hide()
			self["detailslabel"].hide()
			self["poster"].hide()
			self["stars"].hide()
			self["starsbg"].hide()
			self.removCovers()
			total = ""
			self["detailslabel"].setText("")
			self["statusbar"].setText("")
			self.noExit = False
			self.curResult = False
			self["key_yellow"].setText("")
			self["key_green"].setText("")
			if config.plugins.tmbd.test_connect.value:
				self.TestConnection()
			else:
				self.getTMBD()


	def getTMBD(self):
		global eventname, total
		total = ""
		results = ""
		self.resetLabels()
		if not self.eventName:
			s = self.session.nav.getCurrentService()
			info = s and s.info()
			event = info and info.getEvent(0) # 0 = now, 1 = next
			if event:
				self.eventName = event.getEventName()
		if self.eventName:
			title = self.eventName.split("(")[0].strip()
			try:
				results = tmdb.search(title)
			except:
				results = []
			if len(results) == 0:
				self["statusbar"].setText(_("Nothing found for: %s") % (self.eventName))
				eventname = self.eventName
				self.curResult = False
				return False
			self.resultlist = []
			for searchResult in results:
				try:
					movie = tmdb.getMovieInfo(searchResult['id'])
					released = movie['released'][:4]
					if released:
						self.resultlist.append((movie['name'].encode("utf-8") + " - " + released, movie))
					else:
						self.resultlist.append((movie['name'].encode("utf-8"), movie))
					total = len(results)
					if len(results) > 0:
						self["statusbar"].setText(_("Total results: %s") % (total))
					eventname = self.eventName
					self.curResult = True
				except:
					pass
			self.showMenu()
			self["menu"].setList(self.resultlist)

	def selectionChanged(self):
		self["poster"].hide()
		self["stars"].hide()
		self["starsbg"].hide()
		self["ratinglabel"].hide()
		self["castlabel"].hide()
		current = self["menu"].l.getCurrentSelection()
		if current and self.curResult:
			try:
				movie = current[1]
				self["castlabel"].setText("%s / %s%s / %s%s\n\n%s" % (str(movie['name'].encode("utf-8")), _("Appeared: "),str(movie['released'].encode("utf-8")), _("Duration: "), self.textNo(str(movie['runtime'].encode("utf-8"))), str(movie['overview'].encode("utf-8"))))
				self["castlabel"].show()
				jpg_file = "/tmp/preview.jpg"
				cover_url = movie['images'][0]['cover']
				urllib.urlretrieve (cover_url, jpg_file)
				self.refreshTimer.start(100, True)
				rating = str(movie['rating'])
				votes = str(movie['votes'])
				Votestext = ""
				Ratingtext = _("no user rating yet")
				if rating and rating != "0.0":
					Ratingtext = _("User Rating") + ": " + rating + " / 10"
					self.ratingstars = int(10*round(float(rating.replace(',','.')),1))
					self["stars"].show()
					self["stars"].setValue(self.ratingstars)
					self["starsbg"].show()
				self["ratinglabel"].show()
				self["ratinglabel"].setText(Ratingtext)
				if votes and votes != "0":
					Votestext = _("Votes") + ": " + votes + _(" times")
				self["voteslabel"].setText(Votestext)
			except Exception, e:
				print e

	def TMBDPoster(self):
		if not self.curResult:
			self.removCovers()
		if fileExists("/tmp/preview.jpg"):
			jpg_file = "/tmp/preview.jpg"
		else:
			jpg_file = resolveFilename(SCOPE_PLUGINS, "Extensions/TMBD/picon_default.png")
		sc = AVSwitch().getFramebufferScale()
		self.picload.setPara((self["poster"].instance.size().width(), self["poster"].instance.size().height(), sc[0], sc[1], False, 1, "#00000000"))
		self.picload.startDecode(jpg_file)

        def textNo(self, text):
            if text == None or text == "0":
                return (_('0 min.'))
            else:
                return text + _(" min.")


	def paintPosterPixmapCB(self, picInfo=None):
		ptr = self.picload.getData()
		if ptr != None and self.curResult:
			self["poster"].instance.setPixmap(ptr.__deref__())
			self["poster"].show()
		else:
			self["poster"].hide()

	def createSummary(self):
		return TMBDLCDScreen

class TMBDLCDScreen(Screen):
	skin = """
	<screen position="0,0" size="132,64" title="TMBD Plugin">
		<widget name="headline" position="4,0" size="128,22" font="Regular;20"/>
		<widget source="parent.title" render="Label" position="6,26" size="120,34" font="Regular;14"/>
	</screen>"""

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent)
		self["headline"] = Label(_("TMBD Plugin"))


class Settings(Screen, ConfigListScreen):
	skin = """<screen position="center,center" size="620,330" title="Settings" backgroundColor="#31000000" >
                    <widget name="config" position="10,10" size="600,280" zPosition="1" transparent="0" backgroundColor="#31000000" scrollbarMode="showOnDemand" />
                    <widget name="key_red" position="10,303" zPosition="2" size="235,25" halign="center" font="Regular;22" transparent="1" foregroundColor="red"  />
                    <widget name="key_green" position="365,303" zPosition="2" size="235,25" halign="center" font="Regular;22" transparent="1" foregroundColor="green" />
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/ig/red25.png" position="10,293" size="235,44" zPosition="1" alphatest="on" />
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TMBD/ig/green25.png" position="365,293" size="235,44" zPosition="1" alphatest="on" />
                  </screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Settings TMBD Details Plugin..."))
		self.prev_ext_menu = config.plugins.tmbd.add_ext_menu.value
		self['key_red'] = Button(_('Cancel'))
		self['key_green'] = Button(_('Save'))
		self['actions'] = ActionMap(['SetupActions',
		    'ColorActions'], {'green': self.save,
	            'ok': self.save,
	            'red': self.exit,
	            'cancel': self.exit}, -2)

		list = []
		list.append(getConfigListEntry(_('Select the search language'), config.plugins.tmbd.locale))
		list.append(getConfigListEntry(_('Select your skins'), config.plugins.tmbd.skins))
		list.append(getConfigListEntry(_('Add \"Lookup in TMBD\" Red Button to single-EPG'), config.plugins.tmbd.add_tmbd_to_epg))
		list.append(getConfigListEntry(_('Add \"Lookup in TMBD\" Info Button to multi-EPG'), config.plugins.tmbd.add_tmbd_to_multi))
		list.append(getConfigListEntry(_('Add \"Lookup in TMBD\" Info Button to GraphMultiEpg'), config.plugins.tmbd.add_tmbd_to_graph))
		list.append(getConfigListEntry(_('Open VirtualKeyBoard'), config.plugins.tmbd.virtual_text))
		list.append(getConfigListEntry(_('Show plugin in channel selection menu'), config.plugins.tmbd.menu))
		list.append(getConfigListEntry(_('Show plugin in extensions menu'), config.plugins.tmbd.add_ext_menu))
		list.append(getConfigListEntry(_('Check status Internet'), config.plugins.tmbd.test_connect))
		list.append(getConfigListEntry(_('Show info for all types of movies'), config.plugins.tmbd.new_movieselect))
		list.append(getConfigListEntry(_('Close plugin EXIT Button'), config.plugins.tmbd.exit_key))

		ConfigListScreen.__init__(self, list)

	def save(self):
		if self.prev_ext_menu != config.plugins.tmbd.add_ext_menu.value:
			plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		ConfigListScreen.keySave(self)
		
	def exit(self):
		self.close()

class MovielistPreviewScreen(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skin = SKIN
		self["background"] = Label("")
		self["preview"] = Pixmap()
		self.onShow.append(self.movePosition)

	def movePosition(self):
		if self.instance:
			self.instance.move(ePoint(config.plugins.tmbd.position_x.value, config.plugins.tmbd.position_y.value))
			size = config.plugins.tmbd.size.value.split("x")
			self.instance.resize(eSize(int(size[0]), int(size[1])))
			self["background"].instance.resize(eSize(int(size[0]), int(size[1])))
			self["preview"].instance.resize(eSize(int(size[0]), int(size[1])))

class MovielistPreview():
	def __init__(self):
		self.dialog = None
		self.mayShow = True
		self.working = False
                self.path = '/media/hdd/covers/'
	def gotSession(self, session):
		if not self.dialog:
			self.dialog = session.instantiateDialog(MovielistPreviewScreen)

	def changeVisibility(self):
		if config.plugins.tmbd.enabled.value:
			config.plugins.tmbd.enabled.value = False
		else:
			config.plugins.tmbd.enabled.value = True
		config.plugins.tmbd.enabled.save()

	def showPreview(self, movie):
		if self.working == False:
			self.dialog.hide()
			if movie and self.mayShow and config.plugins.tmbd.enabled.value:
                                png2 = os.path.split(movie)[1] 
                                if movie.endswith(".ts"):
			             if fileExists("%s.meta"%(movie)):
				            readmetafile = open("%s.meta"%(movie), "r")
				            servicerefname = readmetafile.readline()[0:-1]
				            eventname = readmetafile.readline()[0:-1]
				            readmetafile.close()
                                            png2 = eventname
				     else:
                                            png2 = os.path.split(movie)[1]
				png = self.path + png2 + ".jpg"
				if fileExists(png):
					self.working = True
					sc = AVSwitch().getFramebufferScale()
					self.picload = ePicLoad()
					self.picload.PictureData.get().append(self.showPreviewCallback)
					size = config.plugins.tmbd.size.value.split("x")
					self.picload.setPara((int(size[0]), int(size[1]), sc[0], sc[1], False, 1, "#00000000"))
					self.picload.startDecode(png)

	def showPreviewCallback(self, picInfo=None):
		if picInfo:
			ptr = self.picload.getData()
			if ptr != None:
				self.dialog["preview"].instance.setPixmap(ptr)
				self.dialog.show()
		self.working = False

	def hideDialog(self):
		self.mayShow = False
		self.dialog.hide()

	def showDialog(self):
		self.mayShow = True
		self.dialog.show()
movielistpreview = MovielistPreview()

class MovielistPreviewPositionerCoordinateEdit(ConfigListScreen, Screen):
	skin = """
		<screen position="center,center" size="560,110" title="%s">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" transparent="1" alphatest="on" />
			<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="config" position="0,45" size="560,60" scrollbarMode="showOnDemand" />
		</screen>""" % _("Poster Preview")

	def __init__(self, session, x, y, w, h):
		Screen.__init__(self, session)
		
		self["key_green"] = Label(_("OK"))
		
		self.xEntry = ConfigInteger(default=x, limits=(0, w))
		self.yEntry = ConfigInteger(default=y, limits=(0, h))
		ConfigListScreen.__init__(self, [
			getConfigListEntry("x position:", self.xEntry),
			getConfigListEntry("y position:", self.yEntry)])
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"green": self.ok,
				 "cancel": self.close
			}, -1)

	def ok(self):
		self.close([self.xEntry.value, self.yEntry.value])

class MovielistPreviewPositioner(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skin = SKIN
		self["background"] = Label("")
		self["preview"] = Pixmap()
		
		self["actions"] = ActionMap(["EPGSelectActions", "MenuActions", "WizardActions"],
		{
			"left": self.left,
			"up": self.up,
			"right": self.right,
			"down": self.down,
			"ok": self.ok,
			"back": self.exit,
			"menu": self.editCoordinates,
			"nextBouquet": self.bigger,
			"prevBouquet": self.smaller
		}, -1)
		
		desktop = getDesktop(0)
		self.desktopWidth = desktop.size().width()
		self.desktopHeight = desktop.size().height()
		
		self.moveTimer = eTimer()
		self.moveTimer.callback.append(self.movePosition)
		self.moveTimer.start(50, 1)
		
		self.onShow.append(self.__onShow)

	def __onShow(self):
		if self.instance:
			size = config.plugins.tmbd.size.value.split("x")
			self.instance.resize(eSize(int(size[0]), int(size[1])))
			self["background"].instance.resize(eSize(int(size[0]), int(size[1])))
			self["preview"].instance.resize(eSize(int(size[0]), int(size[1])))

	def movePosition(self):
		self.instance.move(ePoint(config.plugins.tmbd.position_x.value, config.plugins.tmbd.position_y.value))
		self.moveTimer.start(50, 1)

	def left(self):
		value = config.plugins.tmbd.position_x.value
		value -= 1
		if value < 0:
			value = 0
		config.plugins.tmbd.position_x.value = value

	def up(self):
		value = config.plugins.tmbd.position_y.value
		value -= 1
		if value < 0:
			value = 0
		config.plugins.tmbd.position_y.value = value

	def right(self):
		value = config.plugins.tmbd.position_x.value
		value += 1
		if value > self.desktopWidth:
			value = self.desktopWidth
		config.plugins.tmbd.position_x.value = value

	def down(self):
		value = config.plugins.tmbd.position_y.value
		value += 1
		if value > self.desktopHeight:
			value = self.desktopHeight
		config.plugins.tmbd.position_y.value = value

	def ok(self):
		config.plugins.tmbd.position_x.save()
		config.plugins.tmbd.position_y.save()
		self.close()

	def exit(self):
		config.plugins.tmbd.position_x.cancel()
		config.plugins.tmbd.position_y.cancel()
		self.close()

	def editCoordinates(self):
		self.session.openWithCallback(self.editCoordinatesCallback, MovielistPreviewPositionerCoordinateEdit, config.plugins.tmbd.position_x.value, config.plugins.tmbd.position_y.value, self.desktopWidth, self.desktopHeight)

	def editCoordinatesCallback(self, callback=None):
		if callback:
			config.plugins.tmbd.position_x.value = callback[0]
			config.plugins.tmbd.position_y.value = callback[1]

	def bigger(self):
		if config.plugins.tmbd.size.value == "185x278":
			config.plugins.tmbd.size.value = "285x398"
		elif config.plugins.tmbd.size.value == "130x200":
			config.plugins.tmbd.size.value = "185x278"
		elif config.plugins.tmbd.size.value == "104x150":
			config.plugins.tmbd.size.value = "130x200"
		config.plugins.tmbd.size.save()
		self.__onShow()

	def smaller(self):
		if config.plugins.tmbd.size.value == "130x200":
			config.plugins.tmbd.size.value = "104x150"
		elif config.plugins.tmbd.size.value == "185x278":
			config.plugins.tmbd.size.value = "130x200"
		elif config.plugins.tmbd.size.value == "285x398":
			config.plugins.tmbd.size.value = "185x278"
		config.plugins.tmbd.size.save()
		self.__onShow()

class MovielistPreviewMenu(Screen):
	skin = """
		<screen position="center,center" size="420,105" title="%s">
			<widget name="list" position="5,5" size="410,100" />
		</screen>""" % _("Poster Preview")

	def __init__(self, session, service):
		Screen.__init__(self, session)
		self.session = session
		self.service = service
		self["list"] = MenuList([])
		self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
		self.onLayoutFinish.append(self.showMenu)

	def showMenu(self):
		list = []
		if config.plugins.tmbd.enabled.value:
			list.append(_("Deactivate Poster Preview"))
		else:
			list.append(_("Activate Poster Preview"))
		list.append(_("Change Poster Preview position"))
		self["list"].setList(list)

	def okClicked(self):
		idx = self["list"].getSelectionIndex()
		if movielistpreview.dialog is None:
			movielistpreview.gotSession(self.session)
		if idx == 0:
			movielistpreview.changeVisibility()
			self.showMenu()
		else:
			movielistpreview.dialog.hide()
			self.session.open(MovielistPreviewPositioner)

SelectionChanged = MovieList.selectionChanged

def selectionChanged(instance):
	global movie2
	SelectionChanged(instance)
	curr = instance.getCurrent()
	if curr and isinstance(curr, eServiceReference):
		movielistpreview.showPreview(curr.getPath())
		movie2 = curr.getPath()
MovieList.selectionChanged = selectionChanged

Hide = MovieSelection.hide
def hideMovieSelection(instance):
	Hide(instance)
	movielistpreview.hideDialog()
MovieSelection.hide = hideMovieSelection

Show = MovieSelection.show
def showMovieSelection(instance):
	Show(instance)
	movielistpreview.showDialog()
MovieSelection.show = showMovieSelection

def selectionChanged2(instance):
	SelectionChanged2(instance)
	curr = instance.getCurrent()
	if curr and isinstance(curr, eServiceReference):
		movielistpreview.showPreview(curr.getPath())

def hideMovieSelection2(instance):
	Hide2(instance)
	movielistpreview.hideDialog()

def showMovieSelection2(instance):
	Show2(instance)
	movielistpreview.showDialog()

try:
	from Plugins.Extensions.Suomipoeka.MovieList import MovieList as MovieList2
	from Plugins.Extensions.Suomipoeka.MovieSelection import MovieSelectionSP
	SelectionChanged2 = MovieList2.selectionChanged
	MovieList2.selectionChanged = selectionChanged2
	Hide2 = MovieSelectionSP.hide
	MovieSelectionSP.hide = hideMovieSelection2
	Show2 = MovieSelectionSP.show
	MovieSelectionSP.show = showMovieSelection2
except ImportError:
	print "[Movielist Preview] Could not import Suomipoeka Plugin, maybe not installed or too old version?"


def eventinfo(session, servicelist, **kwargs):
	ref = session.nav.getCurrentlyPlayingServiceReference()
	session.open(TMBDEPGSelection, ref)
	
def main(session, **kwargs):
	session.open(Settings)


def main3(session, eventName="", **kwargs):
	global eventname
	s = session.nav.getCurrentService()
	info = s and s.info()
	event = info and info.getEvent(0) # 0 = now, 1 = next
	if event:
		eventName = event.getEventName().split("(")[0].strip()        
		eventname = eventName.replace('"', '').replace('Х/Ф', '').replace('М/Ф', '').replace('Х/ф', '').replace('.', '')
	session.open(TMBD, eventname)


def movielist(session, service, **kwargs):
        global name
        global eventname
        eventName=""
	serviceHandler = eServiceCenter.getInstance()
	info = serviceHandler.info(service)
	name = info and info.getName(service) or ''
	eventName = name.split(".")[0].strip()
	eventname = eventName
	session.open(TMBD, eventname, movielist = True)

def autostart_ChannelContextMenu(session, **kwargs):
	TMBDChannelContextMenuInit()

def sessionstart(reason, **kwargs):
	if reason == 0:
		movielistpreview.gotSession(kwargs["session"])
		global def_SelectionEventInfo_updateEventInfo
		if def_SelectionEventInfo_updateEventInfo is None:
			def_SelectionEventInfo_updateEventInfo = SelectionEventInfo.updateEventInfo
			SelectionEventInfo.updateEventInfo = new_SelectionEventInfo_updateEventInfo
		global def_MovieSelection_showEventInformation
		if def_MovieSelection_showEventInformation is None:
			def_MovieSelection_showEventInformation = MovieSelection.showEventInformation
			MovieSelection.showEventInformation = new_MovieSelection_showEventInformation

def autostart(reason, **kwargs):
	if reason == 0:
		try:
			EPGSelectionInit()
		except Exception:
			pass
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/GraphMultiEPG/plugin.pyc") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/GraphMultiEPG/plugin.pyc"):
			try:
				GraphMultiEPGInit()
			except Exception:
				pass

def main2(session, service):
	session.open(MovielistPreviewMenu, service)


def Plugins(**kwargs):
	if config.plugins.tmbd.add_ext_menu.value:
		return [PluginDescriptor(name=_("TMBD Details"),
				description=_("Setup menu"),
				icon="tmdb.png",
				where=PluginDescriptor.WHERE_PLUGINMENU,
				fnc=main,
				),
				PluginDescriptor(name=_("TMBD Details"),
				description=_("Query details from the Internet Movie Database"),
				where=PluginDescriptor.WHERE_EVENTINFO,
				fnc=eventinfo,
				),
				PluginDescriptor(
				description = _("TMBD Details"),
				where = PluginDescriptor.WHERE_MOVIELIST,
				fnc = movielist,
				),
				PluginDescriptor(
				where = PluginDescriptor.WHERE_SESSIONSTART,
				fnc = autostart_ChannelContextMenu,
				),
				PluginDescriptor(
				where = PluginDescriptor.WHERE_SESSIONSTART,
				fnc = sessionstart,
				),
				PluginDescriptor(
				where = PluginDescriptor.WHERE_AUTOSTART,
				fnc = autostart,
				),
				PluginDescriptor(name=_("Poster Preview"),
				description=_("Poster Preview"),
				where=PluginDescriptor.WHERE_MOVIELIST,
				fnc=main2,
				),
				PluginDescriptor(name=_("TMBD Details"),
				description=_("Query details from the Internet Movie Database"),
				where=PluginDescriptor.WHERE_EXTENSIONSMENU,
				fnc=main3,
				),
		]
	else:
		return [PluginDescriptor(name=_("TMBD Details"),
				description=_("Setup menu"),
				icon="tmdb.png",
				where=PluginDescriptor.WHERE_PLUGINMENU,
				fnc=main,
				),
				PluginDescriptor(name=_("TMBD Details"),
				description=_("Query details from the Internet Movie Database"),
				where=PluginDescriptor.WHERE_EVENTINFO,
				fnc=eventinfo,
				),
				PluginDescriptor(
				description = _("TMBD Details"),
				where = PluginDescriptor.WHERE_MOVIELIST,
				fnc = movielist,
				),
				PluginDescriptor(
				where = PluginDescriptor.WHERE_SESSIONSTART,
				fnc = autostart_ChannelContextMenu,
				),
				PluginDescriptor(
				where = PluginDescriptor.WHERE_SESSIONSTART,
				fnc = sessionstart,
				),
				PluginDescriptor(
				where = PluginDescriptor.WHERE_AUTOSTART,
				fnc = autostart,
				),
				PluginDescriptor(name=_("Poster Preview"),
				description=_("Poster Preview"),
				where=PluginDescriptor.WHERE_MOVIELIST,
				fnc=main2,
				),
			]
