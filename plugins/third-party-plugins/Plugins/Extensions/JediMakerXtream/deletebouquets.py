#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from plugin import skin_path, cfg, playlist_file
from Screens.Screen import Screen
from JediSelectionList import SelectionList, SelectionEntryComponent
import os, json, re
import jediglobals as jglob
import globalfunctions as jfunc


class JediMakerXtream_DeleteBouquets(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = skin_path + 'jmx_bouquets.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = _('Delete Bouquets')

        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Delete'))
        self['key_yellow'] = StaticText(_('Toggle All'))
        self['key_blue'] = StaticText('')
        self['description'] = Label(_('Select all the iptv bouquets you wish to delete. \nPress OK to toggle the selection'))

        self.playlists_all = jfunc.getPlaylistJson()
        self.bouquets = []
        self.getBouquets()
        self.bouquet_list = [ SelectionEntryComponent(x[0], x[1], x[2], x[3]) for x in self.bouquets ]

        self['list'] = SelectionList(self.bouquet_list, enableWrapAround=True) 

        self.onLayoutFinish.append(self.__layoutFinished)

        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {'red': self.keyCancel,
         'green': self.deleteBouquets,
         'yellow': self['list'].toggleAllSelection,
         'save': self.deleteBouquets,
         'cancel': self.keyCancel,
         'ok': self['list'].toggleSelection}, -2)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)


    def ok(self):
        index = self['list'].getIndex()
        self['list'].setIndex(index)


    def keyCancel(self):
        self.close()


    def getBouquets(self):

        for playlist in self.playlists_all:
            if 'bouquet_info' in playlist and 'name' in playlist['bouquet_info']:
                bouquetValues = [str(playlist['bouquet_info']['name']), playlist['playlist_info']['index'], '', False]
                self.bouquets.append(bouquetValues)  


    def deleteBouquets(self):
        selectedBouquetList = self['list'].getSelectionsList()
        for x in selectedBouquetList:
            bouquet_name = x[0]

            cleanName = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '_', str(bouquet_name))
            cleanName = re.sub(r' ', '_', cleanName)
            cleanName = re.sub(r'_+', '_', cleanName)

            with open('/etc/enigma2/bouquets.tv', 'r+') as f:
                lines = f.readlines()
                f.seek(0)
                for line in lines:
                    if 'jmx_live_' + str(cleanName) + "_" in line or 'jmx_vod_' + str(cleanName) + "_" in line or 'jmx_series_' + str(cleanName)  + "_" in line:
                        continue
                    f.write(line)

                f.truncate()
                jfunc.purge('/etc/enigma2', 'jmx_live_' + str(cleanName)  + "_")
                jfunc.purge('/etc/enigma2', 'jmx_vod_' + str(cleanName)  + "_")
                jfunc.purge('/etc/enigma2', 'jmx_series_' + str(cleanName)  + "_")

                if jglob.has_epg_importer:
                    jfunc.purge('/etc/epgimport', 'jmx.' + str(cleanName) + '.channels.xml')
                    jfunc.purge('/etc/epgimport', 'jmx.' + str(cleanName) + '.sources.xml')

            jfunc.refreshBouquets()
            self.deleteBouquetFile(bouquet_name)
            jglob.firstrun = 0
            jglob.current_selection = 0
            jglob.current_playlist = []
        self.close()


    def deleteBouquetFile(self, bouquet_name):

        for playlist in self.playlists_all:
            if 'bouquet_info' in playlist and 'name' in playlist['bouquet_info']:
                if playlist['bouquet_info']['name'] == bouquet_name:
                    del playlist['bouquet_info']

        jglob.bouquets_exist = False
        for playlist in self.playlists_all:
            if 'bouquet_info' in playlist:
                jglob.bouquets_exist = True
                break

        if jglob.bouquets_exist == False:
            jfunc.resetUnique()

        # delete leftover empty dicts
        self.playlists_all = filter(None, self.playlists_all)

        with open(playlist_file, 'w') as f:
            json.dump(self.playlists_all, f)
