#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict
from Components.ActionMap import ActionMap
from Components.Label import Label
from enigma import eTimer
from plugin import skin_path, playlist_file, hdr, cfg
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
import urllib2
import json
import socket
import os
from datetime import datetime

from Components.ProgressBar import ProgressBar
from JediSelectionList import SelectionList, SelectionEntryComponent

import jediglobals as jglob
import globalfunctions as jfunc
import buildxml as bx
import downloads


class JediMakerXtream_Update(Screen):

    def __init__(self, session, runtype):
        Screen.__init__(self, session)
        self.session = session
        self.runtype = runtype

        if os.path.isdir('/usr/lib/enigma2/python/Plugins/Extensions/EPGImport'):
            jglob.has_epg_importer = True
            if not os.path.exists('/etc/epgimport'):
                os.makedirs('/etc/epgimport')
        else:
            jglob.has_epg_importer = False

        if self.runtype == 'manual':
            skin = skin_path + 'jmx_progress.xml'
            with open(skin, 'r') as f:
                self.skin = f.read()

        Screen.setTitle(self, _('Updating Bouquets'))

        self['action'] = Label('')
        self['status'] = Label('')
        self['progress'] = ProgressBar()
        self['actions'] = ActionMap(['SetupActions'], {'cancel': self.keyCancel}, -2)

        self.pause = 100
        self.job_bouquet_name = ''
        self.firstrun = True
        self.x = 0

        self.playlists_bouquets = []
        self.playlists_all = jfunc.getPlaylistJson()

        for playlist in self.playlists_all:
            if 'bouquet_info' in playlist:
                self.playlists_bouquets.append(playlist)

        self.rytec_ref = {}
        self.epg_alias_names = []

        if jglob.epg_rytec_uk:
            self.rytec_ref, self.epg_alias_names = downloads.downloadrytec()
        self.start()


    def keyCancel(self):
        self.close()


    def start(self):
        self['action'].setText(_('Starting Update...'))
        self.progresscount = len(self.playlists_bouquets)

        self.progresscurrent = 0
        self['progress'].setRange((0, self.progresscount))
        self['progress'].setValue(self.progresscurrent)
        self.timer = eTimer()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.loopPlaylists)


    def loopPlaylists(self):

        if self.x < len(self.playlists_bouquets):
            self.catloop()
        else:
            jfunc.refreshBouquets()
            if self.runtype == 'manual':
                self.session.openWithCallback(self.done, MessageBox, str(len(self.playlists_bouquets)) + ' Providers IPTV Updated', MessageBox.TYPE_INFO, timeout=30)
            else:
                self.close()

    def catloop(self):
        self.valid = False
        jglob.current_playlist = self.playlists_bouquets[self.x]
        jfunc.readbouquetdata()

        # delete existing references in bouquets.tv / etc/enimga2 bouquet refs / etc/epgimport/ xmltv refs
        jfunc.deleteBouquets()

        self['progress'].setValue(self.progresscurrent)
        self['progress'].setRange((0, self.progresscount))
        self['action'].setText(_('Updating Playlist %d of %d') % (self.progresscurrent, self.progresscount))
        self['status'].setText(_('Playlist: %s') % str(jglob.name))

        self.address = jglob.current_playlist['playlist_info']['address']
        self.playlisttype = jglob.current_playlist['playlist_info']['playlisttype']



        if self.playlisttype == 'xtream' or self.playlisttype == 'external':
            self.protocol = jglob.current_playlist['playlist_info']['protocol']
            self.domain = jglob.current_playlist['playlist_info']['domain']
            self.port = str(jglob.current_playlist['playlist_info']['port'])   
            self.host = str(self.protocol) + str(self.domain) + ':' + str(self.port) + '/'

        if self.playlisttype == 'xtream':
            self.username = jglob.current_playlist['playlist_info']['username']
            self.password = jglob.current_playlist['playlist_info']['password']
            self.type = jglob.current_playlist['playlist_info']['type']
            self.output = jglob.current_playlist['playlist_info']['output']

            self.player_api = str(self.host) + 'player_api.php?username=' + str(self.username) + '&password=' + str(self.password)
            self.get_api = str(self.host) + 'get.php?username=' + str(self.username) + '&password=' + str(self.password) + '&type=m3u_plus&output=' + str(self.output)

            jglob.xmltv_address = str(self.host) + 'xmltv.php?username=' + str(self.username) + '&password=' + str(self.password) 

            LiveCategoriesUrl = self.player_api + '&action=get_live_categories'
            VodCategoriesUrl = self.player_api + '&action=get_vod_categories'
            SeriesCategoriesUrl = self.player_api + '&action=get_series_categories'

            LiveStreamsUrl = self.player_api + '&action=get_live_streams'
            VodStreamsUrl = self.player_api + '&action=get_vod_streams'
            SeriesUrl = self.player_api + '&action=get_series'

        jglob.categories = []

        if self.playlisttype == 'xtream':
            self.checkactive()

            if self.valid:

                #download all live categories
                # jglob.livecategories & jglob.haslive
                downloads.downloadlivecategories(LiveCategoriesUrl)

                #download all vod categories
                # jglob.vodcategories & jglob.hasvod
                downloads.downloadvodcategories(VodCategoriesUrl)

                # download all series categories
                # jglob.seriescategories & jglob.hasseries
                downloads.downloadseriescategories(SeriesCategoriesUrl)

                #download all live streams
                if jglob.haslive:
                    downloads.downloadlivestreams(LiveStreamsUrl)

                #download all vod streams
                if jglob.hasvod:
                    downloads.downloadvodstreams(VodStreamsUrl)

                #download all series streams
                if jglob.hasseries:
                    downloads.downloadseriesstreams(SeriesUrl)

                # jglob.categories only lists categories that actually have any streams and makes them in the format (name, type, id, false)
                jfunc.checkcategories(jglob.live ,jglob.vod, jglob.series)

                # check if category in bouquet file if so mark as true in the format (name, type, id, true)
                if 'bouquet_info' in jglob.current_playlist and jglob.current_playlist['bouquet_info'] != {}:
                    #jfunc.SelectedCategories(jglob.live, jglob.vod, jglob.series)
                    jfunc.IgnoredCategories(jglob.live, jglob.vod, jglob.series)

        else:
            # make jglob.getm3ustreams in format (grouptitle, epg_name, source, type)
            downloads.getM3uCategories(jglob.live, jglob.vod)

        #get selected categories from bouquet file
        if self.playlisttype == 'xtream':
            jglob.selectedcategories = []
            jglob.ignoredcategories = []

            for category in jglob.categories:
                if category[3] == True:
                    jglob.selectedcategories.append(category)
                elif category[3] == False:
                    jglob.ignoredcategories.append(category)


        self.categories = jglob.selectedcategories

        if jglob.current_playlist['playlist_info']['playlisttype'] != 'xtream':
            self.categories = []

        self.category_num = 0
        self.m3uValues = []
        self.firstrun = True

        # m3uValues[series_group_title] = [{'name': series_name, 'url': series_url}]
        if jglob.current_playlist['playlist_info']['playlisttype'] == 'xtream':
            if jglob.series:
                self.m3uValues = downloads.downloadgetfile(self.get_api)

        if jglob.current_playlist['playlist_info']['playlisttype'] == 'xtream':

            self.buildBouquets()

            jfunc.refreshBouquets()
        else:
            self.buildM3uBouquets()
            jfunc.refreshBouquets()

        self.progresscurrent += 1
        self.x += 1
        self.timer = eTimer()
        self.timer.callback.append(self.loopPlaylists)
        self.timer.start(self.pause, 1)


    def buildBouquets(self):
        if self.firstrun == True:
            self.epg_name_list = []

        self.firstrun = False

        if self.category_num < len(self.categories):
            self.process_category()
        else:
            if jglob.live and jglob.has_epg_importer and jglob.epg_provider and jglob.xmltv_address != '':
                bx.buildXMLTVChannelFile(self.epg_name_list)
                bx.buildXMLTVSourceFile()
                self.updateBouquetJsonFile()


    def process_category(self):
        category_name = self.categories[self.category_num][0]
        category_type = self.categories[self.category_num][1]
        category_id = self.categories[self.category_num][2]
        self.protocol = self.protocol.replace(':', '%3a')
        self.epg_name_list = jfunc.process_category(category_name, category_type, category_id, self.domain, self.port, self.username, self.password, self.protocol, self.output, jglob.current_playlist, self.epg_alias_names, self.epg_name_list, self.rytec_ref, self.m3uValues)
        self.category_num += 1
        self.buildBouquets()


    def checkactive(self):
        response = ''
        self.valid = False
        req = urllib2.Request(self.player_api, headers=hdr)

        try:
            response = urllib2.urlopen(req)

        except urllib2.URLError as e:
            print "\n ***** checkactive URLError"
            self.valid = False
            print e
            pass
        except socket.timeout as e:
            print "\n ***** checkactive socket timeout"
            self.valid = False
            print e
            pass

        try:
            self.active = json.load(response)
            if 'user_info' in self.active:
                if self.active['user_info']['auth'] == 1:
                    self.valid = True
                else:
                    self.valid = False

        except ValueError as e:
            print "\n ***** checkactive json error"
            self.valid = False
            print e


    def buildM3uBouquets(self):

        self.categories = []

        for x in jglob.getm3ustreams:
            if x[0] != '':
                if [x[0], x[4]] not in self.categories:
                    self.categories.append([x[0], x[4]])

        if self.firstrun == True:
            self.epg_name_list = []

            self.unique_ref = cfg.unique.value

        self.firstrun = False


        if self.category_num < len(self.categories):
            self.m3u_process_category()

        else:
            if jglob.live and jglob.has_epg_importer and jglob.epg_provider and jglob.xmltv_address != '':
                bx.buildXMLTVChannelFile(self.epg_name_list)
                bx.buildXMLTVSourceFile()


    def m3u_process_category(self):
        category_name = self.categories[self.category_num][0]
        category_type = self.categories[self.category_num][1]
        self.epg_name_list = jfunc.m3u_process_category(category_name, category_type, self.unique_ref, self.epg_name_list, jglob.current_playlist)
        self.category_num += 1
        self.buildM3uBouquets()


    def updateBouquetJsonFile(self):
        #self.selectedCategories = self.categories
        #bouquet_values = {}
        #bouquet_values['live_categories'] = []
        #bouquet_values['vod_categories'] = []
        #bouquet_values['series_categories'] = []

        ############################
        # is this section correct? #
        ############################

        """
        if self.playlisttype == 'xtream':
            for category in self.selectedCategories:
                if category[1] == 'Live':
                    bouquet_values['live_categories'].append(category[0])
                elif category[1] == 'VOD':
                    bouquet_values['vod_categories'].append(category[0])
                elif category[1] == 'Series':
                    bouquet_values['series_categories'].append(category[0])

        else:
            for category in self.getm3ustreams:
                if category[4] == 'live':
                    bouquet_values['live_categories'].append(category[0])
                elif category[4] == 'vod':
                    bouquet_values['vod_categories'].append(category[0])
        """

        if jglob.live:
            #jglob.current_playlist['bouquet_info']['live_categories'] = bouquet_values['live_categories']
            jglob.current_playlist['bouquet_info']['liveupdate'] = datetime.now().strftime('%c')

        if jglob.vod:
            #jglob.current_playlist['bouquet_info']['vod_categories'] = bouquet_values['vod_categories']
            jglob.current_playlist['bouquet_info']['vodupdate']  = datetime.now().strftime('%c') 

        if jglob.series:
            #jglob.current_playlist['bouquet_info']['series_categories'] = bouquet_values['series_categories']
            jglob.current_playlist['bouquet_info']['seriesupdate'] = datetime.now().strftime('%c')

        #replace only amended bouquet
        for playlist in self.playlists_all:
            if jglob.current_playlist['playlist_info']['address'] == playlist['playlist_info']['address']:
                 playlist = jglob.current_playlist

        # output to file
        with open(playlist_file, 'w') as f:
            json.dump(self.playlists_all, f)


    def done(self, answer = None):
        self.close()
