#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.ActionMap import ActionMap
from Components.ConfigList import *
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from Components.Sources.StaticText import StaticText
from enigma import eConsoleAppContainer, eListboxPythonMultiContent, eTimer, eEPGCache, eServiceReference, getDesktop, gFont, loadPic, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER, RT_WRAP, addFont, iServiceInformation, iPlayableService
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.config import *

from Tools.LoadPixmap import LoadPixmap
from plugin import skin_path, cfg, playlist_path, playlist_file, hdr
import re
import json
import urllib2
import os
import socket
import sys

from ServiceReference import ServiceReference

import datetime
import calendar
import jediglobals as jglob
import base64

from Screens.InfoBar import InfoBar, MoviePlayer

screenwidth = getDesktop(0).size()


def downloadSimpleData():
    refurl = ""
    refstream = ""
    jglob.refstreamnum = ""
    jglob.username = ""
    jglob.password = ""
    jglob.domain = ""
    error_message = ""

    refurl = jglob.currentref.getPath()
    # http://domain.xyx:0000/live/user/pass/12345.ts

    if refurl != "":
        refstream = refurl.split('/')[-1]
        # 12345.ts

        jglob.refstreamnum = int(filter(str.isdigit, refstream))
        # 12345

        # get domain, username, password from path
        match1 = False
        if re.search('(https|http):\/\/[^\/]+\/(live|movie|series)\/[^\/]+\/[^\/]+\/\d+(\.m3u8|\.ts|$)', refurl) is not None:
            match1 = True

        match2 = False
        if re.search('(https|http):\/\/[^\/]+\/[^\/]+\/[^\/]+\/\d+(\.m3u8|\.ts|$)', refurl) is not None:
            match1 = True

        if match1:
            jglob.username = re.search('[^\/]+(?=\/[^\/]+\/\d+\.)', refurl).group()
            jglob.password = re.search('[^\/]+(?=\/\d+\.)', refurl).group()
            jglob.domain = re.search('(https|http):\/\/[^\/]+', refurl).group()

        elif match2:
            jglob.username = re.search('[^\/]+(?=\/[^\/]+\/[^\/]+$)', refurl).group()
            jglob.password = re.search('[^\/]+(?=\/[^\/]+$)', refurl).group()
            jglob.domain = re.search('(https|http):\/\/[^\/]+', refurl).group()


        simpleurl = "%s/player_api.php?username=%s&password=%s&action=get_simple_data_table&stream_id=%s" % (jglob.domain, jglob.username, jglob.password, jglob.refstreamnum)

        response = ''

        req = urllib2.Request(simpleurl, headers=hdr)
        try:
            response = urllib2.urlopen(req)

        except urllib2.URLError as e:
            print e
            pass

        except socket.timeout as e:
            print e
            pass

        if response != "":
            simple_data_table = json.load(response)

            """
            with open('/etc/enigma2/jediplaylists/catchup_json.json', 'w') as f:
                json.dump(simple_data_table, f)
                """

            jglob.archive = []
            hasarchive = False
            if 'epg_listings' in simple_data_table:
                for listing in simple_data_table['epg_listings']:
                    if 'has_archive' in listing:
                        if listing['has_archive'] == 1:
                            hasarchive = True
                            jglob.archive.append(listing)

            if hasarchive:
                """
                with open('/etc/enigma2/jediplaylists/hasarchive_json.json', 'w') as f:
                    json.dump(jglob.archive, f)
                    """

                jglob.dates = []
                for listing in jglob.archive:
                    date = datetime.datetime.strptime(listing['start'], '%Y-%m-%d %H:%M:%S')
                    day = calendar.day_abbr[date.weekday()]
                    start = ["%s\t%s" % (day, date.strftime("%d/%m/%Y")), date.strftime("%Y-%m-%d")]

                    if start not in jglob.dates:
                        jglob.dates.append(start)

                dates_count = len(jglob.dates)
                jglob.dates.append(["All %s days" % dates_count, "0000-00-00"])

                return error_message, True

            else:
                error_message = "Channel has no TV Archive."
                return error_message, False 
        else:
            error_message = "Error: Downloading data error."
            return error_message, False



class JediMakerXtream_Catchup(Screen):

    def __init__(self, session):

        skin = """
            <screen name="JediCatchup" position="center,center" size="600,600" >
                <widget name="list" textOffset="15,0" position="0,0" size="1140,504" font="Regular;36"  itemHeight="54" enableWrapAround="1"  scrollbarMode="showOnDemand"  transparent="1" />
            </screen>"""

        Screen.__init__(self, session)
        self.session = session

        self.skin = skin

        self.list = []
        self.catchup_all = []

        self.currentSelection = 0

        self['list'] = MenuList(self.list)


        self['setupActions'] = ActionMap(['SetupActions'], 
        {
         'ok': self.openSelected,
         'cancel': self.quit,
         'menu': self.quit,
         'up': self['list'].up,
         'down': self['list'].down,
         'right': self['list'].pageDown,
         'left': self['list'].pageUp}, -2)


        self.setup_title = ""
        self.createSetup()
        self['list'].onSelectionChanged.append(self.getCurrentEntry)
        self.onLayoutFinish.append(self.__layoutFinished)


    def __layoutFinished(self):
        self.setTitle(self.setup_title)


    def getCurrentEntry(self):
        self.currentSelection = self['list'].getSelectionIndex()


    def quit(self):
        self.close()


    def openSelected(self):
        self.returnValue = self['list'].getCurrent()[1]
        if self.returnValue is not None:
            self.getSelectedDateData()
        return


    def createSetup(self):
        self.list = []

        self.setup_title = _('%s' % jglob.name.lstrip(cfg.catchupprefix.value))
        for date in jglob.dates:
            self.list.append((str(date[0]),str(date[1])))

        self['list'].list = self.list
        self['list'].l.setList(self.list)


    def getSelectedDateData(self):
        selectedArchive = []

        if self.returnValue == "0000-00-00":
             selectedArchive = jglob.archive 
        else:
            for listing in jglob.archive:
                if 'start' in listing:
                    if listing['start'].startswith(str(self.returnValue)):
                        selectedArchive.append(listing)
        """
        with open('/etc/enigma2/jediplaylists/selectedarchive_json.json', 'w') as f:
            json.dump(selectedArchive, f) 


        self.session.open(JediMakerXtream_Catchup_Listings, selectedArchive)


def CatchupEntryComponent(index, date, time, title, description, start, duration):
    res = [index]

    if screenwidth.width() > 1280:
        res.append(MultiContentEntryText(pos=(24, 0), size=(214, 56), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=date))
        res.append(MultiContentEntryText(pos=(240, 0), size=(240, 56), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=time))
        res.append(MultiContentEntryText(pos=(480, 0), size=(828, 56), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=title))
    else:
        res.append(MultiContentEntryText(pos=(16, 0), size=(142, 37), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=date))
        res.append(MultiContentEntryText(pos=(160, 0), size=(160, 37), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=time))
        res.append(MultiContentEntryText(pos=(320, 0), size=(552, 37), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=title))
    return res


class Catchup_Menu(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if screenwidth.width() > 1280:
            self.l.setFont(0, gFont('jediregular', 36))
            self.l.setItemHeight(56)
        else:
            self.l.setFont(0, gFont('jediregular', 24))
            self.l.setItemHeight(37)

class JediMakerXtream_Catchup_Listings(Screen):
    def __init__(self, session, archive):

        Screen.__init__(self, session)
        self.session = session

        skin = skin_path + 'jmx_channels.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()

        self.archive = archive
        self.setup_title = _('TV Archive: %s' % jglob.name.lstrip(cfg.catchupprefix.value))

        self.list = []
        self.catchup_all = []
        self['list'] = Catchup_Menu(self.list)
        self['description'] = Label('')
        self['actions'] = ActionMap(['SetupActions'], {

         'ok': self.play,
         'cancel': self.quit,
         'menu': self.quit,
         'up': self['list'].up,
         'down': self['list'].down,
         'right': self['list'].pageDown,
         'left': self['list'].pageUp}, -2)

        self['key_red'] = StaticText(_('Close'))
        self.getlistings()
        self.onLayoutFinish.append(self.__layoutFinished)


    def __layoutFinished(self):
        self.setTitle(self.setup_title)
        if self.list != []:
            self.getCurrentEntry()


    def quit(self):
        self.close()


    def getlistings(self):

        cu_date_all = ""
        cu_time_all = ""
        cu_title = ""
        cu_description = ""
        cu_play_start = ""
        cu_duration = ""

        self.index = 0
        for listing in self.archive:
            if 'start' in listing:

                cu_start = datetime.datetime.strptime(listing['start'], '%Y-%m-%d %H:%M:%S')
                cu_start_time = cu_start.strftime("%H:%M")
                cu_day = calendar.day_abbr[cu_start.weekday()]
                cu_start_date = cu_start.strftime("%d/%m")
                cu_play_start = cu_start.strftime('%Y-%m-%d:%H-%M')

                cu_date_all = "%s %s" % (cu_day, cu_start_date)

            if 'end' in listing:
                cu_end = datetime.datetime.strptime(listing['end'], '%Y-%m-%d %H:%M:%S')
                cu_end_time = cu_end.strftime("%H:%M")
                cu_time_all = "%s - %s" % (cu_start_time, cu_end_time)

            if 'start_timestamp' in listing and 'stop_timestamp' in listing:
                cu_duration = (int(listing['stop_timestamp']) - int(listing['start_timestamp'])) / 60 

            if 'title' in listing:
                cu_title = base64.b64decode(listing['title'])

            if 'description' in listing:
                cu_description = base64.b64decode(listing['description'])

            self.catchup_all.append([self.index, str(cu_date_all), str(cu_time_all), str(cu_title), str(cu_description), str(cu_play_start), str(cu_duration) ])
            self.index += 1


        self.createSetup()


    def createSetup(self):
        self.list = []

        for listing in  self.catchup_all:
                self.list.append(CatchupEntryComponent(str(listing[0]), str(listing[1]), str(listing[2]), str(listing[3]), str(listing[4]), str(listing[5]), str(listing[6]) ))

        if self.list != []:
            self['list'].onSelectionChanged.append(self.getCurrentEntry)
        self['list'].l.setList(self.list)


    def play(self):
        playurl = "%s/streaming/timeshift.php?username=%s&password=%s&stream=%s&start=%s&duration=%s" % (jglob.domain, jglob.username, jglob.password, jglob.refstreamnum, self.catchup_all[self.currentSelection][5], self.catchup_all[self.currentSelection][6])
        streamtype  = jglob.currentref.type
        if streamtype == 1:
            streamtype = 4097
        print "playing catchup channel"
        sref = eServiceReference(streamtype, 0, playurl)
        sref.setName(self.catchup_all[self.currentSelection][3])
        self.session.open(MoviePlayer, sref)


    def getCurrentEntry(self):
        self.currentSelection = self['list'].getSelectionIndex()
        self['description'].setText(self.catchup_all[self.currentSelection][4])
