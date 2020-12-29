#!/usr/bin/python
# -*- coding: utf-8 -*-


# for localized messages
from . import _
from . import jediglobals as jglob

from .plugin import skin_path, cfg, hdr, screenwidth
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from enigma import eServiceReference
from Screens.InfoBar import MoviePlayer
from Screens.Screen import Screen

import base64
import calendar
import datetime
import json
import re
import socket
import sys

pythonVer = 2
if sys.version_info.major == 3:
    pythonVer = 3

if pythonVer == 3:
    from urllib.request import urlopen, Request
    from urllib.error import URLError
else:
    from urllib2 import urlopen, Request, URLError


def downloadSimpleData():
    refurl = ""
    refstream = ""
    jglob.refstreamnum = ""
    jglob.username = ""
    jglob.password = ""
    jglob.domain = ""
    error_message = ""
    isCatchupChannel = False

    refurl = jglob.currentref.getPath()
    # http://domain.xyx:0000/live/user/pass/12345.ts

    if refurl != "":
        refstream = refurl.split('/')[-1]
        # 12345.ts

        jglob.refstreamnum = int(''.join(filter(str.isdigit, refstream)))
        # 12345

        # get domain, username, password from path
        match1 = False
        if re.search(r'(https|http):\/\/[^\/]+\/(live|movie|series)\/[^\/]+\/[^\/]+\/\d+(\.m3u8|\.ts|$)', refurl) is not None:
            match1 = True

        match2 = False
        if re.search(r'(https|http):\/\/[^\/]+\/[^\/]+\/[^\/]+\/\d+(\.m3u8|\.ts|$)', refurl) is not None:
            match2 = True

        if match1:
            jglob.username = re.search(r'[^\/]+(?=\/[^\/]+\/\d+\.)', refurl).group()
            jglob.password = re.search(r'[^\/]+(?=\/\d+\.)', refurl).group()
            jglob.domain = re.search(r'(https|http):\/\/[^\/]+', refurl).group()

        elif match2:
            jglob.username = re.search(r'[^\/]+(?=\/[^\/]+\/[^\/]+$)', refurl).group()
            jglob.password = re.search(r'[^\/]+(?=\/[^\/]+$)', refurl).group()
            jglob.domain = re.search(r'(https|http):\/\/[^\/]+', refurl).group()

        simpleurl = "%s/player_api.php?username=%s&password=%s&action=get_simple_data_table&stream_id=%s" % (jglob.domain, jglob.username, jglob.password, jglob.refstreamnum)
        getLiveStreams = "%s/player_api.php?username=%s&password=%s&action=get_live_streams" % (jglob.domain, jglob.username, jglob.password)

        response = ''

        req = Request(getLiveStreams, headers=hdr)

        try:
            response = urlopen(req)

        except URLError as e:
            print(e)
            pass

        except socket.timeout as e:
            print(e)
            pass

        except:
            print("\n ***** download Live Streams unknown error")
            pass

        if response != "":
            liveStreams = json.load(response)

            isCatchupChannel = False
            for channel in liveStreams:
                if channel['stream_id'] == jglob.refstreamnum:
                    if int(channel['tv_archive']) == 1:
                        isCatchupChannel = True
                        break

        if isCatchupChannel:

            response = ''
            req = Request(simpleurl, headers=hdr)

            try:
                response = urlopen(req)

            except URLError as e:
                print(e)
                pass

            except socket.timeout as e:
                print(e)
                pass

            except:
                print("\n ***** downloadSimpleData unknown error")
                pass

            if response != "":
                simple_data_table = json.load(response)

                jglob.archive = []
                hasarchive = False
                if 'epg_listings' in simple_data_table:
                    for listing in simple_data_table['epg_listings']:
                        if 'has_archive' in listing:
                            if listing['has_archive'] == 1:
                                hasarchive = True
                                jglob.archive.append(listing)

                if hasarchive:
                    jglob.dates = []
                    for listing in jglob.archive:
                        date = datetime.datetime.strptime(listing['start'], '%Y-%m-%d %H:%M:%S')
                        day = calendar.day_abbr[date.weekday()]
                        start = ["%s\t%s" % (day, date.strftime("%d/%m/%Y")), date.strftime("%Y-%m-%d")]

                        if start not in jglob.dates:
                            jglob.dates.append(start)

                    dates_count = len(jglob.dates)

                    jglob.dates.append([(_("All %s days")) % dates_count, "0000-00-00"])

                    return error_message, True
                else:
                    jglob.archive = []

                    numberofdays = 7
                    currentDate = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())

                    manualArchiveStartDate = currentDate + datetime.timedelta(days=-numberofdays)
                    jglob.dates = []

                    for x in range(0, numberofdays):
                        manualDay = calendar.day_abbr[manualArchiveStartDate.weekday()]
                        manualStart = ["%s\t%s" % (manualDay, manualArchiveStartDate.strftime("%d/%m/%Y")), manualArchiveStartDate.strftime("%Y-%m-%d")]
                        jglob.dates.append(manualStart)
                        aStart = manualArchiveStartDate

                        for y in range(0, 24):
                            aEnd = (aStart + datetime.timedelta(hours=1))
                            aStartString = aStart.strftime("%Y-%m-%d %H:%M:%S")
                            aEndString = aEnd.strftime("%Y-%m-%d %H:%M:%S")
                            aStart_timestamp = aStart.strftime("%s")
                            aStop_timestamp = aEnd.strftime("%s")
                            listing = {"start": aStartString, "end": aEndString, "start_timestamp": aStart_timestamp, "stop_timestamp": aStop_timestamp, "title": "UHJvZ3JhbSBEYXRhIE5vdCBBdmFpbGFibGU=", "description": "UHJvZ3JhbSBEYXRhIE5vdCBBdmFpbGFibGU="}
                            jglob.archive.append(listing)
                            aStart = (aStart + + datetime.timedelta(hours=1))

                        manualArchiveStartDate = manualArchiveStartDate + datetime.timedelta(days=1)

                    jglob.dates.append([(_("Program Data Not Available")), "9999-99-99"])
                    return error_message, True

            else:
                error_message = _("Error: Downloading data error.")
                return error_message, False

        else:
            error_message = _("Channel has no TV Archive.")
            return error_message, False


class JediMakerXtream_Catchup(Screen):

    def __init__(self, session):

        skin = """
            <screen name="JediCatchup" position="center,center" size="600,600" >

                <widget source="newlist" render="Listbox" position="0,0" size="600,504" enableWrapAround="1" scrollbarMode="showOnDemand" transparent="1">
                    <convert type="TemplatedMultiContent">
                        {"template": [
                            MultiContentEntryText(pos = (15, 0), size = (570, 45), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 0 is the name
                        ],
                    "fonts": [gFont("jediregular", 36)],
                    "itemHeight": 54
                    }
                    </convert>
                </widget>

            </screen>"""

        if screenwidth.width() <= 1280:
            skin = """
                <screen name="JediCatchup" position="center,center" size="400,400" >
                    <widget source="newlist" render="Listbox" position="0,0" size="400,336" enableWrapAround="1" scrollbarMode="showOnDemand" transparent="1">
                        <convert type="TemplatedMultiContent">
                            {"template": [
                                MultiContentEntryText(pos = (10, 0), size = (380, 30), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 0 is the name
                            ],
                        "fonts": [gFont("jediregular", 24)],
                        "itemHeight": 36
                        }
                        </convert>
                    </widget>
                </screen>"""

        Screen.__init__(self, session)
        self.session = session

        self.skin = skin

        self.list = []
        self.catchup_all = []
        self.currentSelection = 0

        self["newlist"] = List(self.list)

        self['setupActions'] = ActionMap(['SetupActions'], {
            'ok': self.openSelected,
            'cancel': self.quit,
            'menu': self.quit,
        }, -2)

        self.setup_title = ""
        self.createSetup()
        self['newlist'].onSelectionChanged.append(self.getCurrentEntry)
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def getCurrentEntry(self):
        self.currentSelection = self['newlist'].getIndex()

    def quit(self):
        self.close()

    def openSelected(self):
        self.returnValue = self['newlist'].getCurrent()[1]
        if self.returnValue is not None:
            self.getSelectedDateData()
        return

    def createSetup(self):
        self.list = []

        self.setup_title = '%s' % jglob.name.lstrip(cfg.catchupprefix.value)
        for date in jglob.dates:
            self.list.append((str(date[0]), str(date[1])))

        self['newlist'].list = self.list
        self['newlist'].setList(self.list)

    def getSelectedDateData(self):
        selectedArchive = []

        if self.returnValue == "9999-99-99":
            return
        if self.returnValue == "0000-00-00":
            selectedArchive = jglob.archive
        else:
            for listing in jglob.archive:
                if 'start' in listing:
                    if listing['start'].startswith(str(self.returnValue)):
                        selectedArchive.append(listing)

        self.session.open(JediMakerXtream_Catchup_Listings, selectedArchive)


class JediMakerXtream_Catchup_Listings(Screen):
    def __init__(self, session, archive):

        Screen.__init__(self, session)
        self.session = session

        skin = skin_path + 'jmx_catchup.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()

        self.archive = archive
        self.setup_title = _('TV Archive: %s' % jglob.name.lstrip(cfg.catchupprefix.value))

        self.list = []
        self.catchup_all = []
        self['list'] = List(self.list)
        self['description'] = Label('')
        self['actions'] = ActionMap(['SetupActions'], {

            'ok': self.play,
            'cancel': self.quit,
            'menu': self.quit,
        }, -2)

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
                cu_duration = (int(listing['stop_timestamp']) - int(listing['start_timestamp'])) // 60

            if 'title' in listing:
                cu_title = base64.b64decode(listing['title']).decode("utf-8")

            if 'description' in listing:
                cu_description = base64.b64decode(listing['description']).decode("utf-8")

            self.catchup_all.append([self.index, str(cu_date_all), str(cu_time_all), str(cu_title), str(cu_description), str(cu_play_start), str(cu_duration)])

            self.index += 1

        self.createSetup()

    def createSetup(self):
        self.list = []

        for listing in self.catchup_all:
            self.list.append((str(listing[0]), str(listing[1]), str(listing[2]), str(listing[3]), str(listing[4]), str(listing[5]), str(listing[6])))

        self['list'].list = self.list
        self['list'].setList(self.list)

        if self.list != []:
            self['list'].onSelectionChanged.append(self.getCurrentEntry)

    def play(self):
        playurl = "%s/streaming/timeshift.php?username=%s&password=%s&stream=%s&start=%s&duration=%s" % (jglob.domain, jglob.username, jglob.password, jglob.refstreamnum, self.catchup_all[self.currentSelection][5], self.catchup_all[self.currentSelection][6])
        streamtype = jglob.currentref.type
        if streamtype == 1:
            streamtype = 4097
        sref = eServiceReference(streamtype, 0, playurl)
        sref.setName(self.catchup_all[self.currentSelection][3])
        self.session.open(MoviePlayer, sref)

    def getCurrentEntry(self):
        self.currentSelection = self['list'].getIndex()
        self['description'].setText(self.catchup_all[self.currentSelection][4])
