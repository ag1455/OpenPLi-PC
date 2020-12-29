#!/usr/bin/python
# -*- coding: utf-8 -*-

# for localized messages
from . import _
from . import globalfunctions as jfunc
from . import jediglobals as jglob

from .plugin import skin_path, playlist_file
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText

from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

import os
import sys

try:
    pythonVer = sys.version_info.major
except:
    pythonVer = 2


class JediMakerXtream_Menu(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        skin = skin_path + 'jmx_mainmenu.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()

        self.list = []
        self['menu'] = List(self.list)

        self.setup_title = _('Main Menu')

        self['actions'] = ActionMap(['ColorActions', 'OkCancelActions', 'MenuActions'], {
            'ok': self.openSelected,
            'cancel': self.quit,
            'red': self.quit,
            'menu': self.quit}, -2)

        self['key_red'] = StaticText(_('Close'))

        self.onFirstExecBegin.append(self.check_dependencies)
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def check_dependencies(self):
        dependencies = True
        
        try:
            import lzma
        except:
            try:
                from backports import lzma
            except:
                dependencies = False
            
        if dependencies is False:
            os.chmod("/usr/lib/enigma2/python/Plugins/Extensions/JediMakerXtream/dependencies.sh", 0o0755)
            cmd1 = ". /usr/lib/enigma2/python/Plugins/Extensions/JediMakerXtream/dependencies.sh"
            self.session.openWithCallback(self.createSetup, Console, title="Checking Python Dependencies", cmdlist=[cmd1], closeOnSuccess=False)
        else:
            self.createSetup()
            

    def createSetup(self):
        self.list = []

        self.list.append((_('Playlists'), 'm_playlists'))
        self.list.append((_('Settings'), 'm_settings'))

        self.playlists_all = jfunc.getPlaylistJson()
        jglob.bouquets_exist = False
        for playlist in self.playlists_all:
            if 'bouquet_info' in playlist:
                jglob.bouquets_exist = True
                break

        if jglob.bouquets_exist:
            self.list.append((_('Update Bouquets'), 'm_update'))
            self.list.append((_('Delete Individual Bouquets'), 'm_delete_set'))
            self.list.append((_('Delete All Jedi IPTV Bouquets'), 'm_delete_all'))

        self.list.append((_('About'), 'm_about'))

        self['menu'].list = self.list
        self['menu'].setList(self.list)

    def openSelected(self):
        from . import settings
        from . import playlists
        from . import deletebouquets
        from . import about
        from . import update
        returnValue = self['menu'].getCurrent()[1]
        if returnValue is not None:
            if returnValue == 'm_settings':
                self.session.open(settings.JediMakerXtream_Settings)
                return
            if returnValue == 'm_playlists':
                self.session.openWithCallback(self.createSetup, playlists.JediMakerXtream_Playlist)
                return
            if returnValue == 'm_delete_all':
                self.deleteBouquets()
                return
            if returnValue == 'm_delete_set':
                self.session.openWithCallback(self.createSetup, deletebouquets.JediMakerXtream_DeleteBouquets)
                return
            if returnValue == 'm_about':
                self.session.openWithCallback(self.createSetup, about.JediMakerXtream_About)
                return
            if returnValue == 'm_update':
                self.session.openWithCallback(self.createSetup, update.JediMakerXtream_Update, 'manual')
                self.close()
                return

            return

    def quit(self):
        jglob.firstrun = 0
        self.close(False)

    def deleteBouquets(self, answer=None):
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
            self.playlists_all = [_f for _f in self.playlists_all if _f]

            os.remove(playlist_file)
            # jfunc.refreshBouquets()

            self.createSetup()
        return
