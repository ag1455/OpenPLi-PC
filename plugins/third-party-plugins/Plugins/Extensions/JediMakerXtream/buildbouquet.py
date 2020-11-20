#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.ActionMap import ActionMap
from Components.Label import Label
from enigma import eTimer
from plugin import skin_path, cfg, rytec_file, rytec_url, alias_file, sat28_file, hdr
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from datetime import datetime
from Components.ProgressBar import ProgressBar

import re
import json
import urllib2
import os
import socket
import jediglobals as jglob
import globalfunctions as jfunc
import buildxml as bx
import downloads


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
        #self.categories = jglob.ignoredcategories

        if self.bouquet['playlist_info']['playlisttype'] != 'xtream':
            self.categories = []

        self['action'] = Label(_('Building Bouquets...'))
        self['status'] = Label('')
        self['progress'] = ProgressBar()
        self['actions'] = ActionMap(['SetupActions'], {'cancel': self.keyCancel}, -2)

        self.pause = 100
        self.index = 0

        self.category_num = 0
        self.job_current = 0
        self.job_type = ''
        self.job_category_name = ''
        self.job_total = len(self.categories)

        self.m3uValues = []

        self.rytec_ref = {}
        self.epg_alias_names = []

        self.firstrun = True
        if jglob.epg_rytec_uk:
            self.rytec_ref, self.epg_alias_names = downloads.downloadrytec()

        self.onFirstExecBegin.append(self.start)

    def keyCancel(self):
        self.close()


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

            if len(self.categories) > 0:
                self['action'].setText(_('Starting...'))

                if jglob.series:
                    #1 download series get file, 2 delete existing bouquets, 3 build bouquets,
                    self.progresscount = int(len(self.categories) + 3)

                else:
                    # 1 delete existing bouquets, 2 build bouquets, 
                    self.progresscount = int(len(self.categories) + 2)

                self.progresscurrent = 0
                self['progress'].setRange((0, self.progresscount))
                self['progress'].setValue(self.progresscurrent)
                self.timer = eTimer()

                if jglob.series:
                    self['action'].setText(_('Downloading Series Data...'))
                    self.timer.start(self.pause, 1)
                    self.timer.callback.append(self.downloadgetfile)

                else:
                    self['action'].setText(_('Deleting Existing Bouquets...'))
                    self.timer.start(self.pause, 1)
                    self.timer.callback.append(self.deleteBouquets)

                self.timer.start(self.pause, 1)
            else:
                self.showError(_('No categories selected.'))

        else:
            if len(jglob.getm3ustreams) > 0:
                self['action'].setText(_('Starting...'))

                #1 delete bouquets, 2 bouquetType, 3 build m3u bouquet file, 4 refresh bouquets

                self.progresscount = 4
                self.progresscurrent = 0

                self['progress'].setRange((0, self.progresscount))
                self['progress'].setValue(self.progresscurrent)

                self.timer = eTimer()
                self.timer.start(self.pause, 1)
                self.timer.callback.append(self.deleteBouquets)

            else:
                self.showError(_('No valid M3U streams in file.'))


    def downloadgetfile(self):
        self.m3uValues = downloads.downloadgetfile(self.get_api)

        self.progresscurrent += 1
        self['progress'].setValue(self.progresscurrent)

        self.timer = eTimer()
        self['action'].setText(_('Deleting Existing Bouquets...'))
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.deleteBouquets)


    def deleteBouquets(self):
        jfunc.deleteBouquets()

        self.progresscurrent += 1
        self['progress'].setValue(self.progresscurrent)

        self.timer = eTimer()
        self['action'].setText(_('Saving Bouquet Data File...'))
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.bouquetType)


    def bouquetType(self):
        if self.bouquet['playlist_info']['playlisttype'] == 'xtream':
            self.timer = eTimer()
            self['action'].setText(_('Building Bouquets'))
            self.timer.start(self.pause, 1)
            self.timer.callback.append(self.buildBouquets)
        else:
            self.timer = eTimer()
            self['action'].setText(_('Building Bouquets from M3U File'))
            self.timer.start(self.pause, 1)
            self.timer.callback.append(self.buildM3uBouquets)


    def buildBouquets(self):
        self.timer = eTimer()
        self['progress'].setValue(self.progresscurrent)
        self['action'].setText(_('Building Categories %d of %d') % (self.job_current, self.job_total))
        self['status'].setText(_('%s: %s') % (self.job_type, self.job_category_name))
        self.timer.start(self.pause, 1)

        if self.firstrun == True:
            self.epg_name_list = []

        self.firstrun = False

        if self.category_num < len(self.categories):
            self.process_category()

        else:
            if jglob.live and jglob.has_epg_importer and jglob.epg_provider and jglob.xmltv_address != '':
                bx.buildXMLTVChannelFile(self.epg_name_list)
                bx.buildXMLTVSourceFile()

            jglob.bouquet_id +=10
            cfg.bouquet_id.value = jglob.bouquet_id
            cfg.bouquet_id.save()

            self.progresscurrent += 1
            self['progress'].setValue(self.progresscurrent)

            self.timer = eTimer()
            self.timer.start(self.pause, 1)
            self['action'].setText(_('Refreshing Bouquets...'))
            self.timer.callback.append(jfunc.refreshBouquets)

            self.session.openWithCallback(self.done, MessageBox, str(len(self.categories)) + ' IPTV Bouquets Created', MessageBox.TYPE_INFO, timeout=30)

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
        self.category_num += 1

        self.timer = eTimer()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.buildBouquets)


    def buildM3uBouquets(self):

        self.timer = eTimer()
        self['progress'].setValue(self.progresscurrent)
        self['action'].setText(_('Building Categories %d of %d') % (self.job_current, self.job_total))

        if len(self.categories) <= 1:
            self['status'].setText(_("Building 'General' Bouquet"))
        else:
            self['status'].setText(_('Building Categories'))

        self.categories = []

        for x in jglob.getm3ustreams:
            if x[0] != '':
                if [x[0], x[4]] not in self.categories:
                    self.categories.append([x[0], x[4]])

        if self.firstrun == True:
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

            self.timer = eTimer()
            self.timer.start(self.pause, 1)
            self['action'].setText(_('Refreshing Bouquets...'))
            self.timer.callback.append(jfunc.refreshBouquets)

            self.session.openWithCallback(self.done, MessageBox, str(len(self.categories)) + ' IPTV Bouquets Created', MessageBox.TYPE_INFO, timeout=30)


    def m3u_process_category(self):
        category_name = self.categories[self.category_num][0]
        category_type = self.categories[self.category_num][1]

        self.epg_name_list = jfunc.m3u_process_category(category_name, category_type, self.unique_ref, self.epg_name_list, jglob.current_playlist)

        self.category_num += 1
        self.timer = eTimer()
        self.timer.start(self.pause, 1)
        self.timer.callback.append(self.buildM3uBouquets)


    def showError(self, message):
        question = self.session.open(MessageBox, message, MessageBox.TYPE_ERROR)
        question.setTitle(_('Create Bouquets'))
        self.close()


    def done(self, answer = None):
        jglob.finished = True
        self.close()
