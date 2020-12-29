#!/usr/bin/python
# -*- coding: utf-8 -*-


# for localized messages
from . import _
from . import globalfunctions as jfunc
from . import jediglobals as jglob
from . import owibranding

from .plugin import skin_path, playlist_path, playlist_file

from Components.ActionMap import ActionMap
from Components.config import NoSave, ConfigText, ConfigSelection, ConfigNumber, getConfigListEntry, ConfigYesNo, configfile
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText

from Screens.Screen import Screen

import json


class JediMakerXtream_AddPlaylist(ConfigListScreen, Screen):

    def __init__(self, session, editmode):
        Screen.__init__(self, session)
        self.session = session

        skin = skin_path + 'jmx_settings.xml'

        self.dreamos = False

        try:
            from boxbranding import getImageDistro, getImageVersion, getOEVersion
        except:
            self.dreamos = True
            if owibranding.getMachineBrand() == "Dream Multimedia" or owibranding.getOEVersion() == "OE 2.2":
                skin = skin_path + 'DreamOS/jmx_settings.xml'

        with open(skin, 'r') as f:
            self.skin = f.read()

        self.setup_title = _('Add Playlist')

        self.editmode = editmode
        if self.editmode:
            self.setup_title = _('Edit Playlist')

        self.onChangedEntry = []

        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)

        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Save'))
        self['information'] = Label('')

        self['VirtualKB'].setEnabled(False)
        self['VKeyIcon'] = Pixmap()
        self['VKeyIcon'].hide()
        self['HelpWindow'] = Pixmap()
        self['HelpWindow'].hide()

        self['lab1'] = Label('')

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

        self['actions'] = ActionMap(['SetupActions'], {
            'cancel': self.cancel,
            'save': self.save,
        }, -2)

        self.initConfig()
        self.createSetup()

        self.onLayoutFinish.append(self.layoutFinished)

        if self.setInfo not in self['config'].onSelectionChanged:
            self['config'].onSelectionChanged.append(self.setInfo)

    def layoutFinished(self):
        self.setTitle(self.setup_title)

    def initConfig(self):
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
                self.outputCfg = NoSave(ConfigSelection(default=self.output, choices=[('ts', 'ts'), ('m3u8', 'm3u8')]))
            else:
                self.playlisttypeCfg = NoSave(ConfigSelection(default='m3u', choices=[('standard', _('Standard Playlist')), ('m3u', _('M3U File'))]))
                self.addressCfg = NoSave(ConfigText(default=self.address, fixed_size=False))
        else:
            self.playlisttypeCfg = NoSave(ConfigSelection(default='standard', choices=[('standard', _('Standard Playlist')), ('m3u', _('M3U File'))]))
            self.protocolCfg = NoSave(ConfigSelection(default='http://', choices=[('http://', _('http://')), ('https://', _('https://'))]))
            self.serverCfg = NoSave(ConfigText(default='domain.xyz', fixed_size=False))
            self.portCfg = NoSave(ConfigNumber(default=80))
            self.usernameCfg = NoSave(ConfigText(default=_('username'), fixed_size=False))
            self.passwordCfg = NoSave(ConfigText(default=_('password'), fixed_size=False))
            self.outputCfg = NoSave(ConfigSelection(default=self.output, choices=[('ts', 'ts'), ('m3u8', 'm3u8')]))
            self.addressCfg = NoSave(ConfigText(default=self.address, fixed_size=False))

    def createSetup(self):
        self.list = []
        if not self.editmode:
            self.list.append(getConfigListEntry(_('Select playlist type'), self.playlisttypeCfg))

            if self.playlisttypeCfg.value == 'standard':
                self.list.append(getConfigListEntry(_('Protocol'), self.protocolCfg))
                self.list.append(getConfigListEntry(_('Server URL'), self.serverCfg))
                self.list.append(getConfigListEntry(_('Port'), self.portCfg))
                self.list.append(getConfigListEntry(_('Username'), self.usernameCfg))
                self.list.append(getConfigListEntry(_('Password'), self.passwordCfg))
                self.list.append(getConfigListEntry(_('Output Type'), self.outputCfg))
            else:
                self.list.append(getConfigListEntry(_('M3U external location'), self.addressCfg))

        elif jglob.current_playlist['playlist_info']['playlisttype'] == 'xtream':
            if 'bouquet_info' in jglob.current_playlist:
                self.list.append(getConfigListEntry(_('Bouquet Name'), self.aliasCfg))
            self.list.append(getConfigListEntry(_('Protocol'), self.protocolCfg))
            self.list.append(getConfigListEntry(_('Server URL'), self.serverCfg))
            self.list.append(getConfigListEntry(_('Port'), self.portCfg))
            self.list.append(getConfigListEntry(_('Username'), self.usernameCfg))
            self.list.append(getConfigListEntry(_('Password'), self.passwordCfg))
            self.list.append(getConfigListEntry(_('Output Type'), self.outputCfg))
            if 'bouquet_info' in jglob.current_playlist:
                self.list.append(getConfigListEntry(_('Epg Url'), self.xmltvCfg))

        else:
            self.list.append(getConfigListEntry(_('M3U external location'), self.addressCfg))

        self['config'].list = self.list
        self['config'].l.setList(self.list)

        self.setInfo()
        self.handleInputHelpers()

    # dreamos workaround for showing setting descriptions
    def setInfo(self):

        entry = str(self.getCurrentEntry())

        if entry == _('Select playlist type'):
            self['information'].setText(_("\nSelect the type of playlist to add. Standard playlist or external M3U file.\nTry M3U File for non standard playlists that use custom urls."))
            return

        if entry == _('Protocol'):
            self['information'].setText(_("\nSelect the protocol for your playlists url."))
            return

        if entry == _('Server URL'):
            self['information'].setText(_("\nEnter playlist url without protocol http:// \ne.g. domain.xyz"))
            return

        if entry == _('Port'):
            self['information'].setText(_("\nEnter Port Number without colon : \ne.g. 25461"))
            return

        if entry == _('Username'):
            self['information'].setText(_("\nEnter username."))
            return

        if entry == _('Password'):
            self['information'].setText(_("\nEnter password."))
            return

        if entry == _('Output Type'):
            self['information'].setText(_("\nEnter stream output type."))
            return

        if entry == _('M3U external location'):
            self['information'].setText(_("\nEnter M3U list url including protocol. \neg. http://www.domain.xyz"))
            return

        if entry == _('Bouquet Name'):
            self['information'].setText(_("\nEnter the name to be displayed in bouquets."))
            return

        if entry == _('Epg Url'):
            self['information'].setText(_("\nEnter EPG Url."))
            return

    def handleInputHelpers(self):
        from enigma import ePoint
        currConfig = self["config"].getCurrent()

        if currConfig is not None:
            if isinstance(currConfig[1], ConfigText):
                if 'VKeyIcon' in self:
                    if isinstance(currConfig[1], ConfigNumber):
                        self['VirtualKB'].setEnabled(False)
                        self['VKeyIcon'].hide()
                    else:
                        self['VirtualKB'].setEnabled(True)
                        self['VKeyIcon'].show()

                if "HelpWindow" in self and currConfig[1].help_window and currConfig[1].help_window.instance is not None:
                    helpwindowpos = self["HelpWindow"].getPosition()
                    currConfig[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))
            else:
                if 'VKeyIcon' in self:
                    self['VirtualKB'].setEnabled(False)
                    self['VKeyIcon'].hide()

    def changedEntry(self):
        self.item = self['config'].getCurrent()
        for x in self.onChangedEntry:
            x()

        try:
            if isinstance(self['config'].getCurrent()[1], ConfigYesNo) or isinstance(self['config'].getCurrent()[1], ConfigSelection):
                self.createSetup()
        except:
            pass

    def getCurrentEntry(self):
        return self['config'].getCurrent() and self['config'].getCurrent()[0] or ''

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
  
        ConfigListScreen.keySave(self)

    def cancel(self, answer=None):
        from Screens.MessageBox import MessageBox
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
            self.newEntry = '\n' + str(self.protocolCfg.value) + str(self.serverCfg.value) + ':' + str(self.portCfg.value) + '/get.php?username=' + str(self.usernameCfg.value) + \
                '&password=' + str(self.passwordCfg.value) + '&type=' + self.type + '&output=' + str(self.outputCfg.value) + '\n'
        else:
            self.newEntry = '\n' + str(self.addressCfg.value)
        with open(playlist_path, 'a') as f:
            f.write(self.newEntry)
            f.close()

    def editEntry(self):
        if self.playlisttypeCfg.value == 'standard':

            oldEntry = str(self.protocol) + str(self.domain) + ':' + str(self.port) + '/get.php?username=' + str(self.username) + '&password=' + str(self.password) + '&type=' + str(self.type) + \
                '&output=' + str(self.output)

            editEntry = '\n' + str(self.protocolCfg.value) + str(self.serverCfg.value) + ':' + str(self.portCfg.value) + '/get.php?username=' + str(self.usernameCfg.value) + \
                '&password=' + str(self.passwordCfg.value) + '&type=' + str(self.type) + '&output=' + str(self.outputCfg.value) + '\r\n'

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
                '/get.php?username=' + str(self.usernameCfg.value) + '&password=' + str(self.passwordCfg.value) + '&type=' + str(self.type) + '&output=' + str(self.outputCfg.value)
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
