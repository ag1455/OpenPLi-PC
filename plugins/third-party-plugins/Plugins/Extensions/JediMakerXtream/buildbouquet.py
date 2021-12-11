#!/usr/bin/python
# -*- coding: utf-8 -*-

# for localized messages
from . import _

from . import buildxml as bx
from . import downloads
from . import globalfunctions as jfunc
from . import jediglobals as jglob

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from enigma import eTimer
from .plugin import skin_path, cfg
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen


class JediMakerXtream_BuildBouquets(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        skin = skin_path + 'jmx_progress.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()

        Screen.setTitle(self, _('Building Bouquets'))

        self.bouquet = jglob.current_playlist
        self.categories = jglob.selectedcategories

        if self.bouquet['playlist_info']['playlisttype'] != 'xtream':
            self.categories = []

        self['action'] = Label(_('Building Bouquets...'))
        self['status'] = Label('')
        self['progress'] = ProgressBar()
        self['actions'] = ActionMap(['SetupActions'], {'cancel': self.keyCancel}, -2)

        self.pause = 5
        self.index = 0

        self.category_num = 0
        self.job_current = 0
        self.job_type = ''
        self.job_category_name = ''
        self.job_total = len(self.categories)

        self.progresscurrent = 0
        self.progresscount = int(len(self.categories) + 2)

        if jglob.live:
            self.progresscount += 1

        if jglob.vod:
            self.progresscount += 1

        if jglob.series:
            self.progresscount += 2

        if jglob.epg_rytec_uk:
            self.progresscount += 1

        if self.bouquet['playlist_info']['playlisttype'] != 'xtream':
            # 1 delete bouquets, 2 bouquetType, 3 build m3u bouquet file, 4 refresh bouquets
            self.progresscount = 4

        self['progress'].setRange((0, self.progresscount))
        self['progress'].setValue(self.progresscurrent)

        self.m3uValues = []

        self.rytec_ref = {}

        self.epg_alias_names = []

        self.firstrun = True

        self.onFirstExecBegin.append(self.start)

    def keyCancel(self):
        self.close()

    def nextjob(self, actiontext, function):
        self['action'].setText(actiontext)
        self.timer = eTimer()
        self.timer.start(self.pause, 1)
        try:
            self.timer_conn = self.timer.timeout.connect(function)
        except:
            self.timer.callback.append(function)

    def start(self):
        if self.bouquet['playlist_info']['playlisttype'] == 'xtream':

            self.protocol = self.bouquet['playlist_info']['protocol']
            self.domain = self.bouquet['playlist_info']['domain']
            self.port = self.bouquet['playlist_info']['port']
            self.username = self.bouquet['playlist_info']['username']
            self.password = self.bouquet['playlist_info']['password']
            self.output = self.bouquet['playlist_info']['output']
            self.host = str(self.protocol) + str(self.domain) + ':' + str(self.port) + '/'
            self.get_api = str(self.host) + 'get.php?username=' + str(self.username) + '&password=' + str(self.password) + '&type=m3u_plus&output=' + str(self.output)
            self.player_api = str(self.host) + 'player_api.php?username=' + str(self.username) + '&password=' + str(self.password)
            self.LiveStreamsUrl = self.player_api + '&action=get_live_streams'
            self.VodStreamsUrl = self.player_api + '&action=get_vod_streams'
            self.SeriesUrl = self.player_api + '&action=get_series'

        self['progress'].setValue(self.progresscurrent)

        if jglob.epg_rytec_uk:
            self.nextjob(_('Downloading Rytec UK EPG data...'), self.downloadrytec)
        else:
            self.nextjob(_('Starting...'), self.startcreate)

    def downloadrytec(self):
        self.rytec_ref, self.epg_alias_names = downloads.downloadrytec()

        self.progresscurrent += 1
        self['progress'].setValue(self.progresscurrent)
        self.nextjob(_('Starting...'), self.startcreate)

    def startcreate(self):
        if self.bouquet['playlist_info']['playlisttype'] == 'xtream':

            if len(self.categories) > 0:
                self.nextjob(_('Downloading Live data...'), self.downloadLive)
            else:
                self.showError(_('No categories selected.'))
        else:
            if len(jglob.getm3ustreams) > 0:
                self.nextjob(_('Deleting Existing Bouquets...'), self.deleteBouquets)
            else:
                self.showError(_('No valid M3U streams in file.'))

    def downloadLive(self):
        if jglob.live:
            downloads.downloadlivestreams(self.LiveStreamsUrl)
            self.progresscurrent += 1
            self['progress'].setValue(self.progresscurrent)
        self.nextjob(_('Downloading VOD data'), self.downloadVod)

    def downloadVod(self):
        if jglob.vod:
            downloads.downloadvodstreams(self.VodStreamsUrl)
            self.progresscurrent += 1
            self['progress'].setValue(self.progresscurrent)
        self.nextjob(_('Downloading Series data'), self.downloadSeries)

    def downloadSeries(self):
        if jglob.series:
            downloads.downloadseriesstreams(self.SeriesUrl)
            self.progresscurrent += 1
            self['progress'].setValue(self.progresscurrent)
            self.nextjob(_('Downloading get.php file for series stream data'), self.downloadgetfile)
        else:
            self.nextjob(_('Deleting Existing Bouquets...'), self.deleteBouquets)

    def downloadgetfile(self):
        self.m3uValues = downloads.downloadgetfile(self.get_api)
        self.progresscurrent += 1
        self['progress'].setValue(self.progresscurrent)
        self.nextjob(_('Deleting Existing Bouquets...'), self.deleteBouquets)

    def deleteBouquets(self):
        jfunc.deleteBouquets()
        self.progresscurrent += 1
        self['progress'].setValue(self.progresscurrent)
        self.nextjob(_('Saving Bouquet Data File...'), self.bouquetType)

    def bouquetType(self):
        if self.bouquet['playlist_info']['playlisttype'] == 'xtream':
            self.nextjob(_('Building Bouquets...'), self.buildBouquets)
        else:
            self.nextjob(_('Building M3U Bouquets...'), self.buildM3uBouquets)

    def buildBouquets(self):
        self['progress'].setRange((0, self.progresscount))
        self['progress'].setValue(self.progresscurrent)
        self['action'].setText(_('Building Categories %d of %d') % (self.job_current, self.job_total))
        self['status'].setText('%s: %s' % (self.job_type, self.job_category_name))

        if self.firstrun is True:
            self.epg_name_list = []

        self.firstrun = False

        if self.category_num < len(self.categories):
            self.process_category()
        else:
            if jglob.live and jglob.has_epg_importer and jglob.epg_provider and jglob.xmltv_address != '':
                if jglob.fixepg:
                    bx.downloadXMLTV()
                bx.buildXMLTVChannelFile(self.epg_name_list)
                bx.buildXMLTVSourceFile()

            jglob.bouquet_id += 10
            cfg.bouquet_id.value = jglob.bouquet_id
            cfg.bouquet_id.save()

            self.progresscurrent += 1
            self['progress'].setValue(self.progresscurrent)

            # self.nextjob(_('Refreshing Bouquets...'), jfunc.refreshBouquets)

            self.session.openWithCallback(self.done, MessageBox, str(len(self.categories)) + _(' IPTV Bouquets Created'), MessageBox.TYPE_INFO, timeout=30)

    def process_category(self):
        category_name = self.categories[self.category_num][0]
        category_type = self.categories[self.category_num][1]
        category_id = self.categories[self.category_num][2]
        self.protocol = self.protocol.replace(':', '%3a')

        self.epg_name_list = jfunc.process_category(category_name, category_type, category_id, self.domain, self.port, self.username, self.password, self.protocol, self.output, self.bouquet, self.epg_alias_names, self.epg_name_list, self.rytec_ref, self.m3uValues)

        self.job_current = self.category_num
        self.job_type = category_type
        self.job_category_name = category_name

        self.progresscurrent += 1
        self['progress'].setRange((0, self.progresscount))
        self['progress'].setValue(self.progresscurrent)
        self.category_num += 1

        if self.category_num % 5 == 1:
            self.nextjob(_('Building Categories %d of %d') % (self.job_current, self.job_total), self.buildBouquets)
        else:
            self.buildBouquets()

    def buildM3uBouquets(self):

        self['progress'].setValue(self.progresscurrent)
        self['action'].setText(_('Building Categories %d of %d') % (self.job_current, self.job_total))

        if len(self.categories) <= 1:
            self['status'].setText(_("Building 'General' Bouquet"))
        else:
            self['status'].setText(_('Building Categories'))

        self.categories = []

        for x in jglob.getm3ustreams:
            if [x[0], x[4]] not in self.categories:
                self.categories.append([x[0], x[4]])

        if self.firstrun is True:
            self.epg_name_list = []

            if cfg.unique.value:
                self.unique_ref = cfg.unique.value
            else:
                self.unique_ref = 0

        self.firstrun = False

        if self.category_num < len(self.categories):
            self.m3u_process_category()

        else:
            if jglob.live and jglob.has_epg_importer and jglob.epg_provider and jglob.xmltv_address != '':

                bx.buildXMLTVChannelFile(self.epg_name_list)
                bx.buildXMLTVSourceFile()

            self.progresscurrent += 1
            self['progress'].setValue(self.progresscurrent)

            # self.nextjob(_('Refreshing Bouquets...'), jfunc.refreshBouquets)
            self.session.openWithCallback(self.done, MessageBox, str(len(self.categories)) + ' IPTV Bouquets Created', MessageBox.TYPE_INFO, timeout=30)

    def m3u_process_category(self):
        category_name = self.categories[self.category_num][0]
        category_type = self.categories[self.category_num][1]
        self.epg_name_list = jfunc.m3u_process_category(category_name, category_type, self.unique_ref, self.epg_name_list, jglob.current_playlist)
        self.category_num += 1
        self.nextjob(_('Building M3U Bouquets...'), self.buildM3uBouquets)
        self.buildM3uBouquets()

    def showError(self, message):
        question = self.session.open(MessageBox, message, MessageBox.TYPE_ERROR)
        question.setTitle(_('Create Bouquets'))
        self.close()

    def done(self, answer=None):
        jglob.finished = True
        jfunc.refreshBouquets()
        self.close()
