#!/usr/bin/python
# -*- coding: utf-8 -*-

# for localized messages
from . import _

import owibranding


from collections import OrderedDict

from Components.ActionMap import ActionMap, HelpableActionMap
from Components.Sources.List import List
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from Components.Sources.StaticText import StaticText
from enigma import eConsoleAppContainer, eListboxPythonMultiContent, getDesktop, gFont, loadPic, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER, RT_WRAP, eTimer, eEnv, pNavigation, eDVBDB
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Screens.Screen import Screen
from plugin import epg_file, sourcelist, hdr, json_file, cfg, has_epg_importer
import os

from Components.ConfigList import *
from Components.config import *
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Pixmap import Pixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_SKIN, fileExists
from Tools.LoadPixmap import LoadPixmap

# download / parse
import urllib2
from StringIO import StringIO
import gzip
import xml.etree.ElementTree as ET
import socket

# fuzzy logic
from difflib import *

import json
import fileinput


screenwidth = getDesktop(0).size()

divider = "────────────────────────────"


class JediEPGXtream_Main(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        skin = """
        <screen name="EPGMain" position="0,0" size="1280,720" backgroundColor="#232323" flags="wfNoBorder">

            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/logo.png" position="20,20" size="167,94" alphatest="blend" />

            <widget name="selection" position="345,20" size="915,30" font="jediepgregular;20" foregroundColor="#39b54a" backgroundColor="#232323" halign="left" valign="top" transparent="1" />
            <widget name="description" position="345,50" size="915,80" font="jediepgregular;20" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" valign="top" transparent="1" />

            <eLabel position="0,139" size="1280,1" backgroundColor="#0e6382" transparent="0" zPosition="3" />

            <widget name="bouquet" position="32,140" size="276,38" font="jediepgregular;20" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />
            <widget name="channel" position="345,140" size="276,38" font="jediepgregular;20" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />
            <widget name="epgsource" position="658,140" size="276,38" font="jediepgregular;20" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />
            <widget name="epgselection" position="971,140" size="276,38" font="jediepgregular;20" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />

            <eLabel position="0,179" size="1280,1" backgroundColor="#0e6382" transparent="0" zPosition="3" />

            <eLabel position="20,206" size="300,450" backgroundColor="#000000" transparent="0" zPosition="-1" />
            <eLabel position="333,206" size="300,450" backgroundColor="#000000" transparent="0" zPosition="-1" />
            <eLabel position="646,206" size="300,450" backgroundColor="#000000" transparent="0" zPosition="-1" />
            <eLabel position="959,206" size="300,450" backgroundColor="#000000" transparent="0" zPosition="-1" />

            <widget name="list1" position="20,206" size="300,450" foregroundColor="#ffffff" backgroundColor="#000000"
                foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="30" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />


            <widget name="list2" position="333,206" size="300,450" foregroundColor="#ffffff" backgroundColor="#000000"
                foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="30" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />


            <widget name="list3" position="646,206" size="300,450" foregroundColor="#ffffff" backgroundColor="#000000"
                foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="30" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />


            <widget name="list4" position="959,206" size="300,450" foregroundColor="#ffffff" backgroundColor="#000000"
                foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="30" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />

            <eLabel position="0,679" size="1280,1" backgroundColor="#0e6382" transparent="0" zPosition="-1" />

            <widget source="global.CurrentTime" render="Label" position="20,686" size="300,28" font="jediepgregular;16" foregroundColor="#ffffff" backgroundColor="#161616" valign="center" halign="center" transparent="1" >
                <convert type="ClockToText">Format:%A, %b %d, %H.%M</convert>
            </widget>

            <widget source="key_red" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_red.png" position="333,686" size="6,28" zPosition="1" >
                <convert type="ConditionalShowHide" />
            </widget>

            <widget source="key_red" render="Label" position="345,686" size="150,28" font="jediepgregular;16" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

            <widget source="key_green" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_green.png"  position="495,686" size="6,28" zPosition="1" >
                <convert type="ConditionalShowHide" />
            </widget>

            <widget source="key_green" render="Label" position="507,686" size="150,28" font="jediepgregular;16" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

            <widget source="key_yellow" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_yellow.png" position="657,686" size="6,28" zPosition="1" >
                <convert type="ConditionalShowHide" />
            </widget>

            <widget source="key_yellow" render="Label" position="669,686" size="150,28" font="jediepgregular;16" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

            <widget source="key_blue" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_blue.png" position="819,686" size="6,28" zPosition="1" >
                <convert type="ConditionalShowHide" />
            </widget>

            <widget source="key_blue" render="Label" position="831,686" size="150,28" font="jediepgregular;16" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_0.png" position="1103,687" size="25,25" alphatest="blend" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_2.png" position="1136,687" size="25,25" alphatest="blend" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_8.png" position="1169,687" size="25,25" alphatest="blend" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_plus.png" position="1202,687" size="25,25" alphatest="blend" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_minus.png" position="1235,687" size="25,25" alphatest="blend" />

        </screen> """

        if screenwidth.width() > 1280:

            skin = """
            <screen name="EPGMain" position="0,0" size="1920,1080" backgroundColor="#232323" flags="wfNoBorder">

                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/logo-large.png" position="30,30" size="250,140" alphatest="blend" />

                <widget name="selection" position="518,30" size="1372,45" font="jediepgregular;30" foregroundColor="#39b54a" backgroundColor="#232323" halign="left" valign="top" transparent="1" />
                <widget name="description" position="518,75" size="1372,120" font="jediepgregular;30" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" valign="top" transparent="1" />

                <eLabel position="0,210" size="1920,1" backgroundColor="#0e6382" transparent="0" zPosition="3" />

                <widget name="bouquet" position="48,211" size="414,58" font="jediepgregular;30" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />
                <widget name="channel" position="518,211" size="414,58" font="jediepgregular;30" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />
                <widget name="epgsource" position="988,211" size="414,58" font="jediepgregular;30" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />
                <widget name="epgselection" position="1458,211" size="414,58" font="jediepgregular;30" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />

                <eLabel position="0,270" size="1920,1" backgroundColor="#0e6382" transparent="0" zPosition="3" />

                <eLabel position="30,310" size="450,675" backgroundColor="#000000" transparent="0" zPosition="-1" />
                <eLabel position="500,310" size="450,675" backgroundColor="#000000" transparent="0" zPosition="-1" />
                <eLabel position="970,310" size="450,675" backgroundColor="#000000" transparent="0" zPosition="-1" />
                <eLabel position="1440,310" size="450,675" backgroundColor="#000000" transparent="0" zPosition="-1" />

                <widget name="list1" position="30,310" size="450,675" foregroundColor="#ffffff" backgroundColor="#000000"
                    foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="45" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />


                <widget name="list2" position="500,310" size="450,675" foregroundColor="#ffffff" backgroundColor="#000000"
                    foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="45" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />


                <widget name="list3" position="970,310" size="450,675" foregroundColor="#ffffff" backgroundColor="#000000"
                    foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="45" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />


                <widget name="list4" position="1440,310" size="450,675" foregroundColor="#ffffff" backgroundColor="#000000"
                    foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="45" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />

                <eLabel position="0,1019" size="1920,1" backgroundColor="#0e6382" transparent="0" zPosition="-1"/>

                <widget source="global.CurrentTime" render="Label" position="30,1029" size="450,42" font="jediepgregular;24" foregroundColor="#ffffff" backgroundColor="#161616" valign="center" halign="center" transparent="1" >
                    <convert type="ClockToText">Format:%A, %b %d, %H.%M</convert>
                </widget>

                <widget source="key_red" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_red_large.png" position="500,1029" size="9,42" zPosition="1" >
                    <convert type="ConditionalShowHide" />
                </widget>

                <widget source="key_red" render="Label" position="518,1029" size="225,42" font="jediepgregular;24" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

                <widget source="key_green" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_green_large.png"  position="743,1029" size="9,42" zPosition="1" >
                    <convert type="ConditionalShowHide" />
                </widget>

                <widget source="key_green" render="Label" position="761,1029" size="225,42" font="jediepgregular;24" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

                <widget source="key_yellow" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_yellow_large.png" position="986,1029" size="9,42" zPosition="1" >
                    <convert type="ConditionalShowHide" />
                </widget>

                <widget source="key_yellow" render="Label" position="1004,1029" size="225,42" font="jediepgregular;24" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

                <widget source="key_blue" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_blue_large.png" position="1229,1029" size="9,42" zPosition="1" >
                    <convert type="ConditionalShowHide" />
                </widget>

                <widget source="key_blue" render="Label" position="1247,1029" size="225,42" font="jediepgregular;24" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_0_large.png" position="1660,1031" size="38,38" alphatest="blend" />
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_2_large.png" position="1708,1031" size="38,38" alphatest="blend" />
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_8_large.png" position="1756,1031" size="38,38" alphatest="blend" />
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_plus_large.png" position="1804,1031" size="38,38" alphatest="blend" />
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_minus_large.png" position="1852,1031" size="38,38" alphatest="blend" />

            </screen> """

        self.dreamos = False
        try:
            from boxbranding import getImageDistro, getImageVersion, getOEVersion
        except:
            self.dreamos = True
            pass

        if owibranding.getMachineBrand() == "Dream Multimedia" or owibranding.getOEVersion() == "OE 2.2" or owibranding.getOEVersion() == "OpenVuplus 2.1" or self.dreamos is True:
            skin = """
            <screen name="EPGMain" position="0,0" size="1280,720" backgroundColor="#232323" flags="wfNoBorder">

                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/logo.png" position="20,20" size="167,94" alphatest="blend" />

                <widget name="selection" position="345,20" size="915,30" font="jediepgregular;20" foregroundColor="#39b54a" backgroundColor="#232323" halign="left" valign="top" transparent="1" />
                <widget name="description" position="345,50" size="915,80" font="jediepgregular;20" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" valign="top" transparent="1" />

                <eLabel position="0,139" size="1280,1" backgroundColor="#0e6382" transparent="0" zPosition="3" />

                <widget name="bouquet" position="32,140" size="276,38" font="jediepgregular;20" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />
                <widget name="channel" position="345,140" size="276,38" font="jediepgregular;20" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />
                <widget name="epgsource" position="658,140" size="276,38" font="jediepgregular;20" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />
                <widget name="epgselection" position="971,140" size="276,38" font="jediepgregular;20" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />

                <eLabel position="0,179" size="1280,1" backgroundColor="#0e6382" transparent="0" zPosition="3" />

                <eLabel position="20,206" size="300,450" backgroundColor="#000000" transparent="0" zPosition="-1" />
                <eLabel position="333,206" size="300,450" backgroundColor="#000000" transparent="0" zPosition="-1" />
                <eLabel position="646,206" size="300,450" backgroundColor="#000000" transparent="0" zPosition="-1" />
                <eLabel position="959,206" size="300,450" backgroundColor="#000000" transparent="0" zPosition="-1" />

                <widget name="list1" position="20,206" size="300,450" foregroundColor="#ffffff" backgroundColor="#000000"
                    foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="30" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />


                <widget name="list2" position="333,206" size="300,450" foregroundColor="#ffffff" backgroundColor="#000000"
                    foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="30" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />


                <widget name="list3" position="646,206" size="300,450" foregroundColor="#ffffff" backgroundColor="#000000"
                    foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="30" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />


                <widget name="list4" position="959,206" size="300,450" foregroundColor="#ffffff" backgroundColor="#000000"
                    foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="30" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />

                <eLabel position="0,679" size="1280,1" backgroundColor="#0e6382" transparent="0" zPosition="-1"/>

                <widget source="global.CurrentTime" render="Label" position="20,686" size="300,28" font="jediepgregular;16" foregroundColor="#ffffff" backgroundColor="#161616" valign="center" halign="center" transparent="1" >
                    <convert type="ClockToText">Format:%A, %b %d, %H.%M</convert>
                </widget>

                <widget source="key_red" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_red.png" position="333,686" size="6,28" zPosition="1" />
                <widget source="key_red" render="Label" position="345,686" size="150,28" font="jediepgregular;16" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

                <widget source="key_green" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_green.png"  position="495,686" size="6,28" zPosition="1" />
                <widget source="key_green" render="Label" position="507,686" size="150,28" font="jediepgregular;16" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

                <widget source="key_yellow" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_yellow.png" position="657,686" size="6,28" zPosition="1" />
                <widget source="key_yellow" render="Label" position="669,686" size="150,28" font="jediepgregular;16" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

                <widget source="key_blue" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_blue.png" position="819,686" size="6,28" zPosition="1" />
                <widget source="key_blue" render="Label" position="831,686" size="150,28" font="jediepgregular;16" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_0.png" position="1103,687" size="25,25" alphatest="blend" />
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_2.png" position="1136,687" size="25,25" alphatest="blend" />
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_8.png" position="1169,687" size="25,25" alphatest="blend" />
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_plus.png" position="1202,687" size="25,25" alphatest="blend" />
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_minus.png" position="1235,687" size="25,25" alphatest="blend" />

            </screen> """

            if screenwidth.width() > 1280:

                skin = """
                <screen name="EPGMain" position="0,0" size="1920,1080" backgroundColor="#232323" flags="wfNoBorder">

                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/logo-large.png" position="30,30" size="250,140" alphatest="blend" />

                    <widget name="selection" position="518,30" size="1372,45" font="jediepgregular;30" foregroundColor="#39b54a" backgroundColor="#232323" halign="left" valign="top" transparent="1" />
                    <widget name="description" position="518,75" size="1372,120" font="jediepgregular;30" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" valign="top" transparent="1" />

                    <eLabel position="0,210" size="1920,1" backgroundColor="#0e6382" transparent="0" zPosition="3"/>

                    <widget name="bouquet" position="48,211" size="414,58" font="jediepgregular;30" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />
                    <widget name="channel" position="518,211" size="414,58" font="jediepgregular;30" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />
                    <widget name="epgsource" position="988,211" size="414,58" font="jediepgregular;30" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />
                    <widget name="epgselection" position="1458,211" size="414,58" font="jediepgregular;30" backgroundColor="#232323" valign="center" transparent="1" zPosition="-1" />

                    <eLabel position="0,270" size="1920,1" backgroundColor="#0e6382" transparent="0" zPosition="3" />

                    <eLabel position="30,310" size="450,675" backgroundColor="#000000" transparent="0" zPosition="-1" />
                    <eLabel position="500,310" size="450,675" backgroundColor="#000000" transparent="0" zPosition="-1" />
                    <eLabel position="970,310" size="450,675" backgroundColor="#000000" transparent="0" zPosition="-1" />
                    <eLabel position="1440,310" size="450,675" backgroundColor="#000000" transparent="0" zPosition="-1" />

                    <widget name="list1" position="30,310" size="450,675" foregroundColor="#ffffff" backgroundColor="#000000"
                        foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="45" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />


                    <widget name="list2" position="500,310" size="450,675" foregroundColor="#ffffff" backgroundColor="#000000"
                        foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="45" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />


                    <widget name="list3" position="970,310" size="450,675" foregroundColor="#ffffff" backgroundColor="#000000"
                        foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="45" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />


                    <widget name="list4" position="1440,310" size="450,675" foregroundColor="#ffffff" backgroundColor="#000000"
                        foregroundColorSelected="#ffffff" backgroundColorSelected="#0e6382" itemHeight="45" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />

                    <eLabel position="0,1019" size="1920,1" backgroundColor="#0e6382" transparent="0" zPosition="-1"/>

                    <widget source="global.CurrentTime" render="Label" position="30,1029" size="450,42" font="jediepgregular;24" foregroundColor="#ffffff" backgroundColor="#161616" valign="center" halign="center" transparent="1" >
                        <convert type="ClockToText">Format:%A, %b %d, %H.%M</convert>
                    </widget>

                    <widget source="key_red" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_red_large.png" position="500,1029" size="9,42" zPosition="1" />
                    <widget source="key_red" render="Label" position="518,1029" size="225,42" font="jediepgregular;24" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

                    <widget source="key_green" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_green_large.png"  position="743,1029" size="9,42" zPosition="1" />
                    <widget source="key_green" render="Label" position="761,1029" size="225,42" font="jediepgregular;24" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

                    <widget source="key_yellow" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_yellow_large.png" position="986,1029" size="9,42" zPosition="1" />
                    <widget source="key_yellow" render="Label" position="1004,1029" size="225,42" font="jediepgregular;24" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

                    <widget source="key_blue" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_blue_large.png" position="1229,1029" size="9,42" zPosition="1" />
                    <widget source="key_blue" render="Label" position="1247,1029" size="225,42" font="jediepgregular;24" valign="center" transparent="1" noWrap="1" foregroundColor="#ffffff" backgroundColor="#232323" halign="left" zPosition="1" />

                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_0_large.png" position="1660,1031" size="38,38" alphatest="blend" />
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_2_large.png" position="1708,1031" size="38,38" alphatest="blend" />
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_8_large.png" position="1756,1031" size="38,38" alphatest="blend" />
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_plus_large.png" position="1804,1031" size="38,38" alphatest="blend" />
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/key_minus_large.png" position="1852,1031" size="38,38" alphatest="blend" />

                </screen> """

        self.skin = skin
        Screen.setTitle(self, _("Jedi EPG Xtream Main"))

        self['bouquet'] = Label(_("Bouquet"))
        self['channel'] = Label(_("Channel"))
        self['epgsource'] = Label(_("EPG Source"))
        self['epgselection'] = Label(_("EPG Selection"))

        self['key_red'] = StaticText(_('Exit'))
        self['key_green'] = StaticText('')
        self['key_yellow'] = StaticText('')
        self['key_blue'] = StaticText('')

        self["selection"] = Label()
        self["description"] = Label()

        self.menu = 0
        self.list1 = []
        self["list1"] = MenuList1(self.list1)

        self.list2 = []
        self["list2"] = MenuList2(self.list2)

        self.list3 = []
        self["list3"] = MenuList3(self.list3)

        self.list4 = []
        self["list4"] = MenuList4(self.list4)

        self.selectedList = []
        self.onChangedEntry = []

        self.defaultEpgList = True

        self["list1"].onSelectionChanged.append(self.selection1Changed)
        self["list2"].onSelectionChanged.append(self.selection2Changed)
        self["list3"].onSelectionChanged.append(self.selection3Changed)
        self["list4"].onSelectionChanged.append(self.selection4Changed)
        self["actions"] = ActionMap(["SetupActions", "DirectionActions", "WizardActions", "ColorActions", "MenuActions", "MoviePlayerActions"], {
            "ok": self.ok,
            "back": self.keyred,
            "cancel": self.keyred,
            "left": self.goLeft,
            "right": self.goRight,
            "up": self.goUp,
            "down": self.goDown,
            "red": self.keyred,
            "green": self.keygreen,
            "yellow": self.keyyellow,
            "blue": self.keyblue,
            "channelUp": self.pageUp,
            "channelDown": self.pageDown,
            "0": self.reset,
            "2": self.prevLetter,
            "8": self.nextLetter
        }, -1)

        self.getJsonFile()
        self.checkJsonFile()
        self.getBouquets()
        self.getJediSources()
        self.getSources()

        self.selectedList = self["list1"]
        self.selection1Changed()

        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self["list2"].selectionEnabled(0)
        self["list3"].selectionEnabled(0)
        self["list4"].selectionEnabled(0)

    def getJsonFile(self):
        temp = {"Bouquets": [], "Sources": []}
        self.epg_json = None
        if not os.path.isfile(json_file):
            open(json_file, 'a').close()

        if not os.stat(json_file).st_size > 0:
            with open(json_file, "w+") as f:
                json.dump(temp, f)

        with open(json_file) as f:
            try:
                self.epg_json = json.load(f, object_pairs_hook=OrderedDict)
            except:
                print("***** json fail ***** ")

    def checkJsonFile(self):
        for bouquet in self.epg_json['Bouquets']:
            bouquetfile = bouquet['bouquet']
            if os.path.exists(('/etc/enigma2/' + bouquetfile).encode("utf-8")):
                continue
            else:
                self.epg_json['Bouquets'].remove(bouquet)

        if self.epg_json['Bouquets'] == [{}]:
            self.epg_json['Bouquets'] = []

        if self.epg_json['Bouquets'] == []:
            self.epg_json['Sources'] = []

        with open(json_file, "w") as f:
            json.dump(self.epg_json, f)

    def selection1Changed(self):
        if self.selectedList == self["list1"]:
            item = self["list1"].getCurrent()
            if item:
                self['selection'].text = item[0]
                self["description"].text = (_("Select Bouquet."))

                if item[3] is False:
                    self.getNextList()

    def selection2Changed(self):
        if self.selectedList == self["list2"]:
            item = self["list2"].getCurrent()
            if item:
                self['selection'].text = self["list1"].getCurrent()[0] + " / " + self["list2"].getCurrent()[0]
                self["description"].text = (_("Select Channel."))
            if self["list2"].getCurrent()[4] != '':
                self['key_green'].text = (_('Unassign EPG'))
            else:
                self['key_green'].text = ('')

    def selection3Changed(self):
        if self.selectedList == self["list3"]:
            item = self["list3"].getCurrent()
            if item:
                self["description"].text = (_("Select EPG Source. Press Yellow to refresh and update EPG Source. Optional"))
                name = item[0]
                url = item[2]
                self.getMatchList(name, url)

    def selection4Changed(self):
        if self.selectedList == self["list4"]:
            item = self["list4"].getCurrent()
            if item:
                self["description"].text = (_("Select the closest EPG ID reference."))

    def goLeft(self):

        self.prevmenu = self.menu
        if self.menu > 0:
            self.menu = self.menu - 1

            if self.menu == 0:
                self['key_green'].text = ('')
                self.selectedList = self["list1"]
                self["list1"].selectionEnabled(1)
                self["list2"].selectionEnabled(0)
                self["list3"].selectionEnabled(0)
                self["list4"].selectionEnabled(0)
                self['key_blue'].text = ('')
                self.selection1Changed()

            if self.menu == 1:
                self.selectedList = self["list2"]
                self["list2"].selectionEnabled(1)
                self["list3"].selectionEnabled(0)
                self["list4"].selectionEnabled(0)
                self['key_blue'].text = (_('Unassign All'))
                self.selection2Changed()

            if self.menu == 1 and self["list2"].getCurrent()[4] != '':
                self['key_green'].text = (_('Unassign EPG'))
            else:
                self['key_green'].text = ('')

            if self.menu == 2:
                self['key_green'].text = ('')
                self['key_yellow'].text = (_('Update Source'))
                self['key_blue'].text = (_('Hide Source'))
                self.selectedList = self["list3"]
                self["list3"].selectionEnabled(1)
                self["list4"].selectionEnabled(0)
                self.selection3Changed()
            else:
                self['key_yellow'].text = ('')

            if self.menu == 3:
                self['key_blue'].text = ('')

        if self.selectedList.getCurrent():
            if self.menu == 0 and self["list1"].getCurrent()[5] == "Level2":
                if self.prevmenu == 0:
                    self.getBouquets()
            if self.menu == 0 and self["list1"].getCurrent()[5] == "Level1" and self["list1"].getCurrent()[3] is True:
                self.list2 = []
                self["list2"].l.setList(self.list2)

    def goRight(self):
        if self.selectedList.getCurrent():
            if self.menu < 3:
                if self.menu == 0 and self["list1"].getCurrent()[3] is True:
                    self.getSubBouquets(self["list1"].getCurrent()[4])
                else:
                    if (self.menu == 0 and self.list2 != []) or (self.menu == 1 and self.list3 != []) or (self.menu == 2 and self.list4 != []):
                        self.menu = self.menu + 1

                        if self.menu == 1:
                            self.selectedList = self["list2"]
                            self["list2"].selectionEnabled(1)
                            self.selection2Changed()

                        if self.menu == 2:
                            self.selectedList = self["list3"]
                            self["list3"].selectionEnabled(1)
                            self.selection3Changed()
                        if self.menu == 3:
                            self.selectedList = self["list4"]
                            self["list4"].selectionEnabled(1)
                            self["list4"].moveToIndex(0)
                            self.selection4Changed()

        if self.menu == 0:
            self['key_green'].text = ('')
            self['key_blue'].text = ('')

        if self.menu == 1:
            self['key_blue'].text = (_('Unassign All'))

        if self.menu == 1 and self["list2"].getCurrent()[4] != '':
            self['key_green'].text = (_('Unassign EPG'))
        else:
            self['key_green'].text = ('')

        if self.menu == 2:
            self['key_green'].text = ('')
            self['key_yellow'].text = (_('Update Source'))
            self['key_blue'].text = (_('Hide Source'))
        else:
            self['key_yellow'].text = ('')

        if self.menu == 3:
            self['key_green'].text = (_('Assign EPG'))
            self['key_blue'].text = (_('ID/Display Name'))

        if self.menu != 0 and self["list2"].getCurrent()[4] != '':
            self.moveToAssigned()

    def getNextList(self):
        if self.menu == 0:
            if self["list1"].getCurrent()[3] is False:
                self.getChannels(self["list1"].getCurrent()[4])

    def goUp(self):
        self.selectedList.up()
        if self.menu == 3 and self["list4"].getCurrent()[0] == divider:
            self.selectedList.up()

    def goDown(self):
        self.selectedList.down()

        if self.menu == 3 and self["list4"].getCurrent()[0] == divider:
            self.selectedList.down()

    def pageUp(self):
        self.selectedList.pageUp()
        if self.menu == 3 and self["list4"].getCurrent()[0] == divider:
            self.goDown()

    def pageDown(self):
        self.selectedList.pageDown()
        if self.menu == 3 and self["list4"].getCurrent()[0] == divider:
            self.goDown()

    def reset(self):
        self.selectedList.moveToIndex(0)

    def prevLetter(self):
        if self.selectedList.getCurrent():
            if self.menu != 0:
                count = 0
                letterlist = []
                letterindex = 0
                current = ord((self.selectedList.getCurrent()[0][0]).lower())

                if self.menu == 1:
                    currentlist = self.list2
                if self.menu == 2:
                    currentlist = self.list3
                if self.menu == 3:
                    currentlist = self.list4
                    if self.selectedList.getCurrent()[2] is True:
                        self.goUp()
                        return

                for item in currentlist:
                    letter = ord((item[0][0].lower()))
                    if not (self.menu == 3 and item[2] is True):
                        if letter not in letterlist:
                            letterlist.append(letter)

                for item in currentlist:
                    letter2 = ord((item[0][0].lower()))

                    if not (self.menu == 3 and item[2] is True):
                        letterindex = letterlist.index(current)
                        if letterindex == 0:
                            if self.menu == 3:
                                self.goUp()
                                break
                            if letter2 == letterlist[len(letterlist) - 1]:
                                self.selectedList.moveToIndex(count)
                                break
                        else:
                            if letter2 == letterlist[letterindex - 1]:
                                self.selectedList.moveToIndex(count)
                                break
                    count += 1

    def nextLetter(self):
        if self.selectedList.getCurrent():
            if self.menu != 0:
                count = 0
                letterlist = []
                letterindex = 0
                current = ord((self.selectedList.getCurrent()[0][0]).lower())

                if self.menu == 0:
                    currentlist = self.list1
                if self.menu == 1:
                    currentlist = self.list2
                if self.menu == 2:
                    currentlist = self.list3
                if self.menu == 3:
                    currentlist = self.list4
                    if self.selectedList.getCurrent()[2] is True:
                        self.goDown()
                        return

                for item in currentlist:
                    letter = ord((item[0][0].lower()))

                    if not (self.menu == 3 and item[2] is True):
                        if letter not in letterlist:
                            letterlist.append(letter)

                for item in currentlist:
                    letter2 = ord((item[0][0].lower()))

                    if not (self.menu == 3 and item[2] is True):
                        letterindex = letterlist.index(current)

                        if letterindex + 1 >= len(letterlist):
                            if letter2 == letterlist[0]:
                                self.selectedList.moveToIndex(0)
                                break
                        else:
                            if letter2 == letterlist[letterindex + 1]:
                                self.selectedList.moveToIndex(count)
                                break
                    count += 1

    def keyred(self):
        self.close()

    def keygreen(self):
        if self['key_green'].getText():
            if self.menu == 1:
                self.unassignEPG()
            if self.menu == 3:
                self.assignEPG()

    def keyyellow(self):
        if self['key_yellow'].getText():
            if self.menu == 2:
                item = self["list3"].getCurrent()
                if item:
                    name = item[0]
                    url = item[2]
                    self.downloadSource(name, url)

    def keyblue(self):
        if self['key_blue'].getText():

            if self.menu == 1:
                self.unassignBouquet()
            if self.menu == 2:
                self.hideSource()
            if self.menu == 3:
                self.defaultEpgList = not self.defaultEpgList

    def ok(self):
        if self.menu == 0:
            self.goRight()

        elif self.menu == 1:
            self.goRight()

        elif self.menu == 2:
            if self.list4 == []:
                self.keyyellow()
            else:
                self.goRight()

        elif self.menu == 3:
            self.keygreen()

    def getBouquets(self):
        self.menu = 0
        self.list1 = []

        if os.path.isfile('/etc/enigma2/bouquets.tv') and os.stat('/etc/enigma2/bouquets.tv').st_size > 0:
            with open('/etc/enigma2/bouquets.tv') as f:
                for line in f:
                    bouquetname = ''
                    hassubbouquet = False
                    if line.startswith('#SERVICE'):
                        if "userbouquet.abm" in line or "#SERVICE 1:519" in line or "userbouquet.favourites" in line or "userbouquet.LastScanned.tv" in line or "_vod_" in line or "_series_" in line:
                            continue
                        else:
                            userbouquet = line.split('"')[1::2][0]
                            with open(('/etc/enigma2/' + userbouquet).encode('utf-8'), "r") as b:
                                for bline in b:
                                    if "#NAME" in bline:
                                        bouquetname = ' '.join(bline.split()[1:])
                                        if " - " in bouquetname:
                                            bouquetname = ' '.join(bline.split()[1:]).split(" - ")[1:][0]

                                    if "subbouquet" in bline:
                                        hassubbouquet = True

                                        if bouquetname != "":
                                            break

                            self.list1.append(MenuEntryComponent1(bouquetname, hassubbouquet, userbouquet, "Level1"))
        # self.list1.sort(key=lambda y: y[0].lower())
        self["list1"].l.setList(self.list1)

    def getSubBouquets(self, subbouquet):
        self.menu = 0
        self.list1 = []

        with open(('/etc/enigma2/' + subbouquet).encode('utf-8'), "r") as f:
            for line in f:
                bouquetname = ''
                if line.startswith('#SERVICE'):
                    userbouquet = line.split('"')[1::2][0]
                    with open(('/etc/enigma2/' + userbouquet).encode('utf-8'), "r") as b:
                        for bline in b:
                            if "#NAME" in bline:
                                bouquetname = ' '.join(bline.split()[1:])
                                if " - " in bouquetname:
                                    bouquetname = ' '.join(bline.split()[1:]).split(" - ")[1:][0]
                                if bouquetname != "":
                                    break

                    self.list1.append(MenuEntryComponent1(bouquetname, False, userbouquet, "Level2"))
        # self.list1.sort(key=lambda y: y[0].lower())
        self["list1"].l.setList(self.list1)

    def getChannels(self, bouquet):
        self.list2 = []

        with open(('/etc/enigma2/' + bouquet).encode('utf-8'), "r") as f:

            channelname = ''
            serviceref = ''
            epgid = ''

            for line in f:

                if line.startswith('#SERVICE'):
                    serviceref = line.split(' ')[1:][0].split('http')[0]

                if line.startswith('#DESCRIPTION'):
                    channelname = line.replace("#DESCRIPTION ", "")
                    for bouq in self.epg_json['Bouquets']:
                        if bouq['bouquet'] == bouquet:
                            for channel in bouq['channel']:
                                if channel['description'] == channelname.strip():
                                    epgid = channel['epgid']
                                    break
                                else:
                                    epgid = ''

                    self.list2.append(MenuEntryComponent2(channelname.strip().upper(), serviceref.strip(), epgid.strip()))
        self.list2.sort(key=lambda y: y[0].lower())
        self["list2"].l.setList(self.list2)

    def getJediSources(self):
        try:
            cfg_location = cfg.location.value
        except:
            cfg_location = '/etc/enigma2/jediplaylists/'

        if os.path.isfile(cfg_location + "playlists.txt") and os.stat(cfg_location + "playlists.txt").st_size > 0:
            with open(cfg_location + "playlists.txt", "r") as f:
                iptvs = []
                lines = f.readlines()
                f.seek(0)
                for line in lines:
                    protocol = 'http://'
                    host = ''
                    domain = ''
                    username = ''
                    password = ''
                    port = 80
                    xmltv_api = ''

                    urlsplit1 = line.split("/")
                    urlsplit2 = line.split("?")

                    protocol = urlsplit1[0] + "//"

                    if not (protocol == "http://" or protocol == "https://"):
                        continue

                    if len(urlsplit1) > 2:
                        domain = urlsplit1[2].split(':')[0]
                        if len(urlsplit1[2].split(':')) > 1:
                            port = urlsplit1[2].split(':')[1]

                    host = str(protocol) + str(domain) + ':' + str(port) + '/'

                    if len(urlsplit2) > 1:
                        for param in urlsplit2[1].split("&"):
                            if param.startswith("username"):
                                username = param.split('=')[1]
                            if param.startswith("password"):
                                password = param.split('=')[1]

                    xmltv_api = str(host) + 'xmltv.php?username=' + str(username) + '&password=' + str(password)

                    if 'get.php' in line and domain != '' and username != '' and password != '':
                        iptvline = "\n" + str(domain) + " " + str(xmltv_api)
                        if iptvline.strip() not in iptvs:
                            iptvs.append(iptvline)

                for iptv in iptvs:
                    exists = False
                    with open(epg_file, "r") as f:
                        for line in f:
                            if iptv.strip() in line.strip():
                                exists = True
                                break

                    if exists is False:
                        with open(epg_file, "a") as f:
                            f.write(iptv)

    def getSources(self):
        self.list3 = []
        if os.path.isfile(epg_file) and os.stat(epg_file).st_size > 0:
            with open(epg_file) as f:
                for line in f:
                    if line != "\n" and not line.startswith("#") and len(line.strip()) != 0:
                        if " " in line:
                            name = line.split(" ")[0]
                            source = line.split(" ")[1].strip()
                            self.list3.append(MenuEntryComponent3(name, source))

        # self.list3.sort(key=lambda y: y[0].lower())
        self["list3"].l.setList(self.list3)

    def downloadSource(self, name, url):
        req = urllib2.Request(url, headers=hdr)

        try:
            response = urllib2.urlopen(req)

            if url.endswith('xz'):
                with open(sourcelist + "/" + name + ".xz", 'wb') as output:
                    output.write(response.read())
            elif url.endswith('gz'):
                with open(sourcelist + "/" + name + ".gz", 'wb') as output:
                    output.write(response.read())
            elif url.endswith('xml'):
                with open(sourcelist + "/" + name + ".xml", 'wb') as output:
                    output.write(response.read())
            elif "xmltv.php" in url:
                with open(sourcelist + "/" + name + ".xml", 'wb') as output:
                    output.write(response.read())

        except urllib2.URLError as e:
            print(e)
            pass

        except socket.timeout as e:
            print(e)
            pass

        except socket.error as e:
            print(e)
            pass

        except:
            print("\n ***** download unknown error")
            pass

        self.openSource(name, url)

    def openSource(self, name, url):
        haslzma = False

        if url.endswith('xz') or url.endswith('gz'):
            try:
                import lzma
                print('\nlzma success')
                haslzma = True

            except ImportError:
                try:
                    from backports import lzma
                    print("\nbackports lzma success")
                    haslzma = True

                except ImportError:
                    print("\nlzma failed")
                    pass

                except:
                    print("\n ***** missing lzma module ***** ")
                    pass

        if url.endswith('xz') and haslzma:

            if os.path.isfile(sourcelist + "/" + name + ".xz"):
                with lzma.open(sourcelist + "/" + name + ".xz", 'rb') as f:
                    with open(sourcelist + "/" + name + ".xml", 'w') as outfile:
                        for line in f:
                            # some errors found
                            if ">>" in line:
                                line = line.replace(">>", ">")
                            if "<<" in line:
                                line = line.replace("<<", "<")

                            outfile.write(line)

        elif url.endswith('gz') and haslzma:
            if os.path.isfile(sourcelist + "/" + name + ".gz"):
                with gzip.open(sourcelist + "/" + name + ".gz", 'rb') as f:
                    with open(sourcelist + "/" + name + ".xml", 'w') as outfile:
                        for line in f:
                            if ">>" in line:
                                line = line.replace(">>", ">")
                            if "<<" in line:
                                line = line.replace("<<", "<")
                            outfile.write(line)
        self.parseXMLFile(name, url)

    def parseXMLFile(self, name, url):
        self.namelist = {}
        epgidlist = []
        self.list4 = []
        try:
            tree = ET.parse(sourcelist + "/" + name + ".xml")
            validxml = True
        except:
            tree = ""
            validxml = False
            pass

        if validxml:
            root = tree.getroot()

            if root.tag == "channels":
                for channel in root.findall('channel'):
                    channelid = str(channel.get('id')).strip()
                    displayname = str(channel.find('display-name').text)
                    self.namelist[channelid] = displayname

                for channel in root.findall('programme'):
                    channelid = channel.get('channel').strip()
                    if [channelid, self.namelist[channelid]] not in epgidlist and channelid is not None:
                        epgidlist.append([channelid, self.namelist[channelid]])

            if root.tag == "tv":
                for channel in root.findall('channel'):
                    channelid = str(channel.get('id')).strip()
                    displayname = str(channel.find('display-name').text)
                    self.namelist[channelid] = displayname

                for channel in root.findall('programme'):
                    channelid = channel.get('channel').strip()
                    if [channelid, self.namelist[channelid]] not in epgidlist and channelid is not None:
                        epgidlist.append([channelid, self.namelist[channelid]])

            epgidlist.sort(key=lambda y: y[0].lower())

            # output simple channel list to .txt file
            with open(sourcelist + "/" + name + ".json", 'w') as f:
                json.dump(epgidlist, f)

            # remove xml, gz, xz files
            if os.path.isfile(sourcelist + "/" + name + ".xz"):
                os.remove(sourcelist + "/" + name + ".xz")
            if os.path.isfile(sourcelist + "/" + name + ".gz"):
                os.remove(sourcelist + "/" + name + ".gz")
            if os.path.isfile(sourcelist + "/" + name + ".xml"):
                os.remove(sourcelist + "/" + name + ".xml")
            self.getMatchList(name, url)

    def getMatchList(self, name, url):

        self.list4 = []
        epgidlist = []
        channellist = []
        idlist = []
        if os.path.isfile(sourcelist + "/" + name + ".json"):
            with open(sourcelist + "/" + name + ".json", "r") as f:
                epgidlist = json.load(f)


        matchlist = []

        for item in epgidlist:
            idlist.append(str(item[0]).upper())
            channellist.append(str(item[1].upper()))

        if self.defaultEpgList:
            matchlist = get_close_matches(self["list2"].getCurrent()[0], idlist, n=13, cutoff=0.25)
        else:
            matchlist = get_close_matches(self["list2"].getCurrent()[0], channellist, n=13, cutoff=0.25)
        if matchlist != []:
            matchlist.append(divider)

        print("********** matchlist ********* %s" % matchlist)

        """
        for match in matchlist:
            if match != divider:
                for item in epgidlist:
                    if match in item[0]:
                        print("******* match found ***** %s" % match)
                        try:
                            channellist.remove(item)
                        except:
                            pass
                            """

        # add true/false flag for the different lists
        for item in epgidlist:
            item.append(False)
        #epgidlist = [[i, False] for i in epgidlist]

        for item in matchlist:
            item.append(True)

        #matchlist = [[i, True] for i in matchlist]

        print("********** epgidlist ********* %s" % epgidlist)
        print("********** matchlist ********* %s" % matchlist)

        finallist = matchlist + epgidlist

        for id in finallist:
            self.list4.append(MenuEntryComponent4(id[0], id[1]))

        self["list4"].l.setList(self.list4)

    def hideSource(self):
        templist = []
        item = self["list3"].getCurrent()
        if item:
            name = item[0]
            url = item[2]

        if os.path.isfile(epg_file) and os.stat(epg_file).st_size > 0:
            with open(epg_file, 'r+') as f:
                new_f = f.readlines()
                f.seek(0)
                for line in new_f:
                    if name in line and url in line:
                        line = line = "#" + line
                    f.write(line)
                f.truncate()

        self.getSources()

    def assignEPG(self):
        bouquet = self["list1"].getCurrent()[4]
        channelname = self["list2"].getCurrent()[0]
        serviceref = self["list2"].getCurrent()[3]
        sourcename = self["list3"].getCurrent()[0]
        sourceurl = self["list3"].getCurrent()[2]
        epgid = self["list4"].getCurrent()[0]

        # add source to source list
        sourceexists = False
        if self.epg_json['Sources'] == []:
            self.epg_json['Sources'].append({"name": sourcename, "source": sourceurl})
        else:
            for source in self.epg_json['Sources']:
                if source['name'] == sourcename and source['source'] == sourceurl:
                    sourceexists = True

            if sourceexists is False:
                self.epg_json['Sources'].append({"name": sourcename, "source": sourceurl})

        # if bouquet doesn't exist create new entry
        if self.epg_json['Bouquets'] == []:
            new_bouquet = {"bouquet": bouquet, "channel": [{"serviceid": serviceref, "description": channelname, "epgid": epgid, "source": sourceurl, "sourcename": sourcename}]}
            self.epg_json['Bouquets'].append(new_bouquet)
        else:
            bouquetexists = False

            for jsonbouquet in self.epg_json['Bouquets']:
                channelexists = False

                if jsonbouquet["bouquet"] == bouquet:
                    bouquetexists = True

                    for channel in jsonbouquet["channel"]:
                        if channel["serviceid"] == serviceref and channel["description"] == channelname:
                            channelexists = True
                            channel["epgid"] = epgid
                            channel["source"] = sourceurl
                            channel["sourcename"] = sourcename
                            break

                    if not channelexists:
                        new_channel = {"serviceid": serviceref, "description": channelname, "epgid": epgid, "source": sourceurl, "sourcename": sourcename}
                        jsonbouquet['channel'].append(new_channel)

                    break

            if not bouquetexists:
                new_bouquet = {"bouquet": bouquet, "channel": [{"serviceid": serviceref, "description": channelname, "epgid": epgid, "source": sourceurl, "sourcename": sourcename}]}
                self.epg_json['Bouquets'].append(new_bouquet)

        # remove sources from source list
        if self.epg_json['Sources'] != []:
            sourcelist = []
            if self.epg_json['Bouquets'] != []:
                for jsonbouquet in self.epg_json['Bouquets']:
                    if "channel" in jsonbouquet:
                        if jsonbouquet["channel"] != []:
                            for channel in jsonbouquet["channel"]:
                                if channel['source'] not in sourcelist:
                                    sourcelist.append(channel['source'])

            for source in self.epg_json['Sources']:
                if source['source'] not in sourcelist:
                    self.epg_json['Sources'].remove(source)

        with open(json_file, "w") as f:
            json.dump(self.epg_json, f)

        self.buildXMLSourceFile()
        self.buildXMLChannelFile()

        self.goLeft()
        self.goLeft()
        self.getChannels(bouquet)

    def unassignEPG(self):
        bouquet = self["list1"].getCurrent()[4]
        channelname = self["list2"].getCurrent()[0]
        serviceref = self["list2"].getCurrent()[3]

        for jsonbouquet in self.epg_json['Bouquets']:
            if jsonbouquet['bouquet'] == bouquet:
                for channel in jsonbouquet["channel"]:
                    if channel["serviceid"] == serviceref and channel["description"] == channelname:
                        jsonbouquet["channel"].remove(channel)
                        if jsonbouquet["channel"] == []:
                            self.epg_json['Bouquets'].remove(jsonbouquet)
                        break

                if self.epg_json['Bouquets'] == [{}]:
                    self.epg_json['Bouquets'] = []

                if self.epg_json['Bouquets'] == []:
                    self.epg_json['Sources'] = []

                break

        # remove sources from source list
        if self.epg_json['Sources'] != []:
            sourcelist = []
            if self.epg_json['Bouquets'] != []:
                for jsonbouquet in self.epg_json['Bouquets']:
                    if "channel" in jsonbouquet:
                        if jsonbouquet["channel"] != []:
                            for channel in jsonbouquet["channel"]:
                                if channel['source'] not in sourcelist:
                                    sourcelist.append(channel['source'])

            for source in self.epg_json['Sources']:
                if source['source'] not in sourcelist:
                    self.epg_json['Sources'].remove(source)

        with open(json_file, "w") as f:
            json.dump(self.epg_json, f)

        self.buildXMLSourceFile()
        self.buildXMLChannelFile()
        self.getChannels(bouquet)

    def unassignBouquet(self):
        bouquet = self["list1"].getCurrent()[4]

        for jsonbouquet in self.epg_json['Bouquets']:
            if jsonbouquet['bouquet'] == bouquet:
                self.epg_json['Bouquets'].remove(jsonbouquet)
                break

        with open(json_file, "w") as f:
            json.dump(self.epg_json, f)

        self.buildXMLSourceFile()
        self.buildXMLChannelFile()
        self.getChannels(bouquet)

    def buildXMLSourceFile(self):
        filepath = '/etc/epgimport/'
        epgfilename = 'jex.epg.channels.xml'
        channelpath = filepath + epgfilename
        filename = 'jex.epg.sources.xml'
        sourcepath = filepath + filename

        with open(sourcepath, 'w') as f:
            xml_str = '<?xml version="1.0" encoding="utf-8"?>\n'
            xml_str += '<sources>\n'
            xml_str += '<sourcecat sourcecatname="Jedi EPG">\n'

            if 'Sources' in self.epg_json:
                for epgsources in self.epg_json['Sources']:
                    xml_str += '<source type="gen_xmltv" nocheck="1" channels="' + str(epgfilename) + '">\n'
                    xml_str += '<description>' + str(epgsources["name"]) + '</description>\n'
                    xml_str += '<url><![CDATA[' + str(epgsources["source"]) + ']]></url>\n'
                    xml_str += '</source>\n'

            xml_str += '</sourcecat>\n'
            xml_str += '</sources>\n'
            f.write(xml_str)

    def buildXMLChannelFile(self):
        filepath = '/etc/epgimport/'
        epgfilename = 'jex.epg.channels.xml'
        channelpath = filepath + epgfilename

        with open(channelpath, 'w') as f:
            xml_str = '<?xml version="1.0" encoding="utf-8"?>\n'
            xml_str += '<channels>\n'

            if 'Bouquets' in self.epg_json:
                for bouquet in self.epg_json['Bouquets']:
                    if "channel" in bouquet:
                        for channel in bouquet["channel"]:
                            serviceid = str(channel["serviceid"])
                            convertedserviceid = serviceid.replace(serviceid.split(":")[0], "1")
                            xml_str += '<channel id="' + str(channel["epgid"]) + '">' + str(convertedserviceid) + 'http%3a//example.m3u8</channel> <!-- ' + str(channel["description"]) + '-->\n'

            xml_str += '</channels>\n'
            f.write(xml_str)

    def moveToAssigned(self):
        pos = 0
        current_bouquet = self["list1"].getCurrent()[4]
        current_channel = self["list2"].getCurrent()[0]
        current_ref = self["list2"].getCurrent()[3]

        for jsonbouquet in self.epg_json['Bouquets']:
            if jsonbouquet["bouquet"] == current_bouquet:

                for channel in jsonbouquet["channel"]:
                    if channel["serviceid"] == current_ref and channel["description"] == current_channel:
                        if self.menu == 2:
                            for position in self.list3:
                                if "sourcename" in channel:
                                    if position[0] == channel["sourcename"]:
                                        self["list3"].moveToIndex(pos)
                                    pos += 1
                        if self.menu == 3:
                            for position in self.list4:
                                if position[0] == channel["epgid"]:
                                    self["list4"].moveToIndex(pos)
                                pos += 1


# ####### Create MENULIST format #######################
def MenuEntryComponent1(bouquetname, subbouquet, userbouquet, Level):

    if screenwidth.width() > 1280:
        png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/tv-large.png")

        if subbouquet is True:
            png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/folder-large.png")

        return [
            bouquetname,
            MultiContentEntryPixmapAlphaBlend(pos=(18, 8), size=(30, 30), png=png),
            MultiContentEntryText(pos=(68, 0), size=(364, 45), font=0, color=0x00ffffff, color_sel=0x00ffffff, backcolor_sel=None, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=bouquetname),
            subbouquet, userbouquet, Level
        ]

    else:
        png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/tv.png")

        if subbouquet is True:
            png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/folder.png")

        return [
            bouquetname,
            MultiContentEntryPixmapAlphaBlend(pos=(12, 5), size=(20, 20), png=png),
            MultiContentEntryText(pos=(46, 0), size=(242, 30), font=0, color=0x00ffffff, color_sel=0x00ffffff, backcolor_sel=None, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=bouquetname),
            subbouquet, userbouquet, Level
        ]


def MenuEntryComponent2(channel, serviceref, epgid):
    png = None
    png2 = None

    if screenwidth.width() > 1280:
        if epgid != '':
            png2 = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/link-large.png")

        return [
            channel,
            MultiContentEntryText(pos=(18, 0), size=(364, 45), font=0, color=0x00ffffff, color_sel=0x00ffffff, backcolor_sel=None, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=channel),
            MultiContentEntryPixmapAlphaBlend(pos=(402, 8), size=(30, 30), png=png2),
            serviceref, epgid
        ]

    else:
        if epgid != '':
            png2 = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/JediEPGXtream/icons/link.png")

        return [
            channel,
            MultiContentEntryText(pos=(12, 0), size=(242, 30), font=0, color=0x00ffffff, color_sel=0x00ffffff, backcolor_sel=None, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=channel),
            MultiContentEntryPixmapAlphaBlend(pos=(268, 5), size=(20, 20), png=png2),
            serviceref, epgid
        ]


def MenuEntryComponent3(name, source):
    png = None

    if screenwidth.width() > 1280:
        return [name, MultiContentEntryText(pos=(18, 0), size=(414, 45), font=0, color=0x00ffffff, color_sel=0x00ffffff, backcolor_sel=None, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=name), source]
    else:
        return [name, MultiContentEntryText(pos=(12, 0), size=(276, 30), font=0, color=0x00ffffff, color_sel=0x00ffffff, backcolor_sel=None, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=name), source]


def MenuEntryComponent4(epg_id, fuzzy):
    png = None
    if screenwidth.width() > 1280:
        return [epg_id, MultiContentEntryText(pos=(18, 0), size=(414, 45), font=0, color=0x00ffffff, color_sel=0x00ffffff, backcolor_sel=None, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=epg_id), fuzzy]
    else:
        return [epg_id, MultiContentEntryText(pos=(12, 0), size=(276, 30), font=0, color=0x00ffffff, color_sel=0x00ffffff, backcolor_sel=None, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=epg_id), fuzzy]


class MenuList1(MenuList):
    def __init__(self, list1, enableWrapAround=True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        if screenwidth.width() > 1280:
            self.l.setFont(0, gFont("jediepgregular", 24))
            self.l.setItemHeight(45)
        else:
            self.l.setFont(0, gFont("jediepgregular", 16))
            self.l.setItemHeight(30)


class MenuList2(MenuList):
    def __init__(self, list2, enableWrapAround=True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        if screenwidth.width() > 1280:
            self.l.setFont(0, gFont("jediepgregular", 24))
            self.l.setItemHeight(45)
        else:
            self.l.setFont(0, gFont("jediepgregular", 16))
            self.l.setItemHeight(30)


class MenuList3(MenuList):
    def __init__(self, list3, enableWrapAround=True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        if screenwidth.width() > 1280:
            self.l.setFont(0, gFont("jediepgregular", 24))
            self.l.setItemHeight(45)
        else:
            self.l.setFont(0, gFont("jediepgregular", 16))
            self.l.setItemHeight(30)


class MenuList4(MenuList):
    def __init__(self, list4, enableWrapAround=True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        if screenwidth.width() > 1280:
            self.l.setFont(0, gFont("jediepgregular", 24))
            self.l.setItemHeight(45)
        else:
            self.l.setFont(0, gFont("jediepgregular", 16))
            self.l.setItemHeight(30)
