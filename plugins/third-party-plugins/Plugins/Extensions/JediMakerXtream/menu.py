#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from plugin import skin_path, playlist_file
from collections import OrderedDict
import os
import json
import jediglobals as jglob
import globalfunctions as jfunc


class JediMakerXtream_Menu(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        skin = skin_path + 'jmx_mainmenu.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()

        self.setup_title = _('Main Menu')
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['ColorActions', 'OkCancelActions', 'MenuActions'], {
         'ok': self.openSelected,
         'cancel': self.quit,
         'red': self.quit,
         'menu': self.quit})
        self['key_red'] = StaticText(_('Close'))
        self.list = []
        self['menu'] = MenuList(self.list)
        self.createSetup()
        self.onLayoutFinish.append(self.__layoutFinished)


    def __layoutFinished(self):
        self.setTitle(self.setup_title)


    def createSetup(self):
        self.list = []
        self.list.append((_('Playlists'), 'm_playlists'))
        self.list.append((_('Settings'), 'm_settings'))

        self.playlists_all = jfunc.getPlaylistJson()

        for playlist in self.playlists_all:
            if 'bouquet_info' in playlist:
                jglob.bouquets_exist = True
                break

        if jglob.bouquets_exist:
                self.list.append((_('Update Bouquets'), 'm_update'))
                self.list.append((_('Delete Individual Bouquets'), 'm_delete_set'))
                self.list.append((_('Delete All Jedi IPTV Bouquets'), 'm_delete_all'))

        self.list.append((_('About'), 'm_about'))
        self['menu'].l.setList(self.list)


    def openSelected(self):
        import settings, playlists, deletebouquets, about, update2
        returnValue = self['menu'].getCurrent()[1]
        if returnValue is not None:
            if returnValue is 'm_settings':
                self.session.open(settings.JediMakerXtream_Settings)
                return
            if returnValue is 'm_playlists':
                self.session.openWithCallback(self.createSetup, playlists.JediMakerXtream_Playlist)
                return
            if returnValue is 'm_delete_all':
                self.deleteBouquets()
                return
            if returnValue is 'm_delete_set':
                self.session.openWithCallback(self.createSetup, deletebouquets.JediMakerXtream_DeleteBouquets)
                return
            if returnValue is 'm_about':
                self.session.openWithCallback(self.createSetup, about.JediMakerXtream_About)
                return
            if returnValue is 'm_update':
                self.session.openWithCallback(self.createSetup, update2.JediMakerXtream_Update, 'manual')
                self.close()
                return
            return


    def quit(self):
        jglob.firstrun = 0
        self.close(False)


    def deleteBouquets(self, answer = None):
        if answer is None:
            self.session.openWithCallback(self.deleteBouquets, MessageBox, _('Permanently delete all Jedi created bouquets?'))
        elif answer:
            with open('/etc/enigma2/bouquets.tv', 'r+') as f:
                lines = f.readlines()
                f.seek(0)
                for line in lines:
                    if 'jmx' not in line:
                        f.write(line)
                f.truncate()

            jfunc.purge('/etc/enigma2', 'jmx')

            if jglob.has_epg_importer:
                jfunc.purge('/etc/epgimport', 'jmx')

            self.playlists_all = jfunc.getPlaylistJson()

            jglob.bouquets_exist = False
            jfunc.resetUnique()
            jglob.firstrun = 0
            jglob.current_selection = 0
            jglob.current_playlist = []

            # delete leftover empty dicts
            self.playlists_all = filter(None, self.playlists_all)


            os.remove(playlist_file)
            jfunc.refreshBouquets()

            self.createSetup()
        return
