#!/usr/bin/python
# -*- coding: utf-8 -*-

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.config import *
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.Pixmap import Pixmap
from Components.Label import Label
from collections import OrderedDict
from plugin import skin_path, cfg, playlist_path, playlist_file

import json
import os
import jediglobals as jglob
import globalfunctions as jfunc


class JediMakerXtream_AddPlaylist(Screen, ConfigListScreen):

    def __init__(self, session, editmode):
        Screen.__init__(self, session)
        self.session = session


        skin = skin_path + 'jmx_settings.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()

        self.setup_title = _('Add Playlist') 
        self.editmode = editmode
        if self.editmode:
            self.setup_title = _('Edit Playlist')

        self.xmltv = ''
        self.alias = ''
        self.paylisttype = ''
        self.address = 'http://'
        self.type = 'm3u'
        self.output = 'ts'

        if self.editmode:

            if 'bouquet_info' in jglob.current_playlist:
                self.alias = jglob.current_playlist['bouquet_info']['name']
                self.xmltv = jglob.current_playlist['bouquet_info']['xmltv_address']

            if jglob.current_playlist['playlist_info']['playlisttype'] == 'xtream':
                self.protocol = jglob.current_playlist['playlist_info']['protocol']
                self.domain = jglob.current_playlist['playlist_info']['domain']
                self.port = str(jglob.current_playlist['playlist_info']['port'])
                self.username = jglob.current_playlist['playlist_info']['username']
                self.password = jglob.current_playlist['playlist_info']['password']
                self.type = jglob.current_playlist['playlist_info']['type']
                self.output = jglob.current_playlist['playlist_info']['output']
                self.index = jglob.current_playlist['playlist_info']['index']
            else:
                self.address = jglob.current_playlist['playlist_info']['address']


        self['actions'] = ActionMap(['SetupActions'],
         {
         'save': self.save,
         'cancel': self.cancel,
         }, -2)

        self.onChangedEntry = []
        self.list = []

        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)

        self.createConfig()
        self.createSetup()

        self.onLayoutFinish.append(self.layoutFinished)

        self['VirtualKB'].setEnabled(False)
        self['HelpWindow'] = Pixmap()
        self['VKeyIcon'] = Pixmap()
        self['HelpWindow'].hide()
        self['VKeyIcon'].hide()

        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Save'))
        self['description'] = Label('')


    def layoutFinished(self):
        self.setTitle(self.setup_title)


    def exit(self):
        self.close()


    def createConfig(self):
        if self.editmode:
            if 'bouquet_info' in jglob.current_playlist:
                self.aliasCfg = NoSave(ConfigText(default=self.alias, fixed_size=False))
                self.xmltvCfg = NoSave(ConfigText(default=self.xmltv, fixed_size=False))
            if jglob.current_playlist['playlist_info']['playlisttype'] == 'xtream':
                self.protocolCfg = NoSave(ConfigSelection(default=self.protocol, choices=[('http://', _('http://')), ('https://', _('https://'))]))
                self.playlisttypeCfg = NoSave(ConfigSelection(default='standard', choices=[('standard', _('Standard Playlist')), ('m3u', _('M3U File'))]))
                self.serverCfg = NoSave(ConfigText(default=self.domain, fixed_size=False))
                self.portCfg = NoSave(ConfigNumber(default=self.port))
                self.usernameCfg = NoSave(ConfigText(default=self.username, fixed_size=False))
                self.passwordCfg = NoSave(ConfigText(default=self.password, fixed_size=False))    
                self.outputCfg = NoSave(ConfigSelection(default=self.output, choices=[('ts', _('ts')), ('m3u8', _('m3u8'))]))
            else:
                self.playlisttypeCfg = NoSave(ConfigSelection(default='m3u', choices=[('standard', _('Standard Playlist')), ('m3u', _('M3U File'))]))
                self.addressCfg = NoSave(ConfigText(default=self.address, fixed_size=False))
        else:
            self.playlisttypeCfg = NoSave(ConfigSelection(default='standard', choices=[('standard', _('Standard Playlist')), ('m3u', _('M3U File'))]))
            self.protocolCfg = NoSave(ConfigSelection(default='http://', choices=[('http://', _('http://')), ('https://', _('https://'))]))
            self.serverCfg = NoSave(ConfigText(default='domain.xyz', fixed_size=False))
            self.portCfg = NoSave(ConfigNumber(default=80))
            self.usernameCfg = NoSave(ConfigText(default='username', fixed_size=False))
            self.passwordCfg = NoSave(ConfigText(default='password', fixed_size=False))
            self.outputCfg = NoSave(ConfigSelection(default=self.output, choices=[('ts', _('ts')), ('m3u8', _('m3u8'))]))
            self.addressCfg = NoSave(ConfigText(default=self.address, fixed_size=False))


    def createSetup(self):
        self.list = []
        if not self.editmode:
            self.list.append(getConfigListEntry(_('Select playlist type'), self.playlisttypeCfg, _('\nSelect the type of playlist to add. Standard playlist or external M3U file.\nTry M3U File for non standard playlists that use custom urls.')))

            if self.playlisttypeCfg.value == 'standard':
                self.list.append(getConfigListEntry(_('Protocol'), self.protocolCfg, _('\nSelect the protocol for your playlists url.')))
                self.list.append(getConfigListEntry(_('Server URL'), self.serverCfg, _('\nEnter playlist url without protocol http:// \ne.g. domain.xyz')))
                self.list.append(getConfigListEntry(_('Port'), self.portCfg, _('\nEnter Port Number without colon : \ne.g. 25461')))
                self.list.append(getConfigListEntry(_('Username'), self.usernameCfg, _('\nEnter username.')))
                self.list.append(getConfigListEntry(_('Password'), self.passwordCfg, _('\nEnter password.')))
                self.list.append(getConfigListEntry(_('Output Type'), self.outputCfg, _('\nEnter stream output type.')))
            else:
                self.list.append(getConfigListEntry(_('M3U external location'), self.addressCfg, _('\nEnter M3U list url including protocol. \neg. http://www.domain.xyz')))

        elif jglob.current_playlist['playlist_info']['playlisttype'] == 'xtream':
            if 'bouquet_info' in jglob.current_playlist:
                self.list.append(getConfigListEntry(_('Bouquet Name'), self.aliasCfg, _('\nEnter the name to be displayed in bouquets.')))
            self.list.append(getConfigListEntry(_('Protocol'), self.protocolCfg, _('\nSelect the protocol for your playlists url.')))
            self.list.append(getConfigListEntry(_('Server URL'), self.serverCfg, _('\nEnter playlist url without protocol http:// \ne.g. domain.xyz')))
            self.list.append(getConfigListEntry(_('Port'), self.portCfg, _('\nEnter Port Number without colon : \ne.g. 25461')))
            self.list.append(getConfigListEntry(_('Username'), self.usernameCfg, _('\nEnter username.')))
            self.list.append(getConfigListEntry(_('Password'), self.passwordCfg, _('\nEnter password.')))
            self.list.append(getConfigListEntry(_('Output Type'), self.outputCfg, _('\nEnter stream output type.')))
            if 'bouquet_info' in jglob.current_playlist:
                self.list.append(getConfigListEntry(_('Epg Url'), self.xmltvCfg, _('\nEnter EPG Url.')))

        else:
            self.list.append(getConfigListEntry(_('M3U external location'), self.addressCfg, _('\nEnter M3U list url including protocol. \neg. http://www.domain.xyz')))

        self['config'].list = self.list
        self['config'].l.setList(self.list)
        self.handleInputHelpers()


    def handleInputHelpers(self):
        if self['config'].getCurrent() is not None:
            if isinstance(self['config'].getCurrent()[1], ConfigText) or isinstance(self['config'].getCurrent()[1], ConfigPassword):
                if self.has_key('VKeyIcon'):
                    if isinstance(self['config'].getCurrent()[1], ConfigNumber):
                        self['VirtualKB'].setEnabled(False)
                        self['VKeyIcon'].hide()
                    else:
                        self['VirtualKB'].setEnabled(True)
                        self['VKeyIcon'].show()

                if not isinstance(self['config'].getCurrent()[1], ConfigNumber):

                     if isinstance(self['config'].getCurrent()[1].help_window, ConfigText) or isinstance(self['config'].getCurrent()[1].help_window, ConfigPassword):
                        if self['config'].getCurrent()[1].help_window.instance is not None:
                            helpwindowpos = self['HelpWindow'].getPosition()

                            if helpwindowpos:
                                helpwindowposx, helpwindowposy = helpwindowpos
                                if helpwindowposx and helpwindowposy:
                                    from enigma import ePoint
                                    self['config'].getCurrent()[1].help_window.instance.move(ePoint(helpwindowposx,helpwindowposy))

            else:
                if self.has_key('VKeyIcon'):
                    self['VirtualKB'].setEnabled(False)
                    self['VKeyIcon'].hide()
        else:
            if self.has_key('VKeyIcon'):
                self['VirtualKB'].setEnabled(False)
                self['VKeyIcon'].hide()




    def changedEntry(self):
        self.item = self['config'].getCurrent()
        for x in self.onChangedEntry:
            x()
        try:
            if isinstance(self['config'].getCurrent()[1], ConfigSelection):
                self.createSetup()
        except:
            pass


    def save(self):
        if self['config'].isChanged():
            for x in self['config'].list:
                x[1].save()

        jglob.firstrun = 0

        if self.playlisttypeCfg.value == 'standard':
            if self.serverCfg.value.startswith('http://'):
                self.serverCfg.value = self.serverCfg.value.replace('http://', '')
            if self.serverCfg.value.startswith('https://'):
                self.serverCfg.value = self.serverCfg.value.replace('https://', '')

            self.serverCfg.value = self.serverCfg.value.strip()
            self.usernameCfg.value = self.usernameCfg.value.strip()
            self.passwordCfg.value = self.passwordCfg.value.strip()
            self.outputCfg.value = self.outputCfg.value.strip()


        elif self.addressCfg.value != 'http://' or self.addressCfg.value != '':
            self.addressCfg.value = self.addressCfg.value.strip()

        if self.editmode:
            self.editEntry()
        else:
            self.createNewEntry()
        configfile.save()
        self.close()


    def cancel(self, answer = None):
        if answer is None:
            if self['config'].isChanged():
                self.session.openWithCallback(self.cancel, MessageBox, _('Really close without saving settings?'))
            else:
                self.close()
        elif answer:
            for x in self['config'].list:
                x[1].cancel()

            self.close()
        return


    def createNewEntry(self):
        if self.playlisttypeCfg.value == 'standard':
            self.newEntry = '\n' +  str(self.protocolCfg.value) + str(self.serverCfg.value) + ':' + str(self.portCfg.value) + '/get.php?username=' + str(self.usernameCfg.value) + \
            '&password=' + str(self.passwordCfg.value) + '&type=' + self.type + '&output=' + str(self.outputCfg.value) + '\n'
        else:
            self.newEntry = '\n' + str(self.addressCfg.value)
        with open(playlist_path, 'a') as f:
            f.write(self.newEntry)
            f.close()


    def editEntry(self):
        if self.playlisttypeCfg.value == 'standard':


            '&output=' + str(self.output)

            editEntry = '\n' +  str(self.protocolCfg.value) + str(self.serverCfg.value) + ':' + str(self.portCfg.value) + '/get.php?username=' + str(self.usernameCfg.value) + \
            '&password=' + str(self.passwordCfg.value)  + '&type=' + str(self.type) + '&output=' + str(self.outputCfg.value) + '\r\n'

        else:
            oldEntry = self.address
            editEntry = '\n' + str(self.addressCfg.value) + '\n'

        with open(playlist_path, 'r+') as f:
            new_f = f.readlines()
            f.seek(0)
            for line in new_f:
                if line.startswith(oldEntry):
                    line = editEntry
                f.write(line)

            f.truncate()

        if 'bouquet_info' in jglob.current_playlist:
            jglob.current_playlist['bouquet_info']['name'] = str(self.aliasCfg)
            jglob.current_playlist['bouquet_info']['xmltv_address'] = str(self.xmltvCfg)

        if jglob.current_playlist['playlist_info']['playlisttype'] == 'xtream':
            jglob.current_playlist['playlist_info']['protocol'] = str(self.protocolCfg.value)
            jglob.current_playlist['playlist_info']['domain'] = str(self.serverCfg.value)
            jglob.current_playlist['playlist_info']['port'] = str(self.portCfg.value)
            jglob.current_playlist['playlist_info']['username'] = str(self.usernameCfg.value)
            jglob.current_playlist['playlist_info']['password'] = str(self.passwordCfg.value)
            jglob.current_playlist['playlist_info']['output'] = str(self.outputCfg.value)
            jglob.current_playlist['playlist_info']['address'] = str(self.protocolCfg.value) + str(self.serverCfg.value) + ':' + str(self.portCfg.value) + \
            '/get.php?username=' + str(self.usernameCfg.value) + '&password=' + str(self.passwordCfg.value)  + '&type=' + str(self.type) + '&output=' + str(self.outputCfg.value)
        else:
            jglob.current_playlist['playlist_info']['address'] = str(self.addressCfg.value)

        self.playlists_all = jfunc.getPlaylistJson()
        if self.playlists_all != []:

                for playlist in self.playlists_all:

                    if playlist != {}:

                        if jglob.current_playlist['playlist_info']['index'] == playlist['playlist_info']['index']:
                             playlist['playlist_info'] = jglob.current_playlist['playlist_info']
                             break

        with open(playlist_file, 'w') as f:
            json.dump(self.playlists_all, f)
