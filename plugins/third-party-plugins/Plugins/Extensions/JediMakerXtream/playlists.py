#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from Components.Sources.StaticText import StaticText
from enigma import getDesktop, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.LoadPixmap import LoadPixmap
from plugin import skin_path, cfg, playlist_path, playlist_file, hdr
import re
import json
import urllib2
import os
import addplaylist, info, setupbouquet
import socket
import sys
import jediglobals as jglob
import globalfunctions as jfunc

screenwidth = getDesktop(0).size()


def PlaylistEntryComponent(index, status, name, extra):
    res = [index]
    if status == 'Active':
        png = LoadPixmap(skin_path + 'images/active.png')
    if status == 'Invalid':
        png = LoadPixmap(skin_path + 'images/invalid.png')
    if status == 'ValidExternal':
        png = LoadPixmap(skin_path + 'images/external.png')
    if status == 'Unknown':
        png = LoadPixmap(skin_path + 'images/blank.png')
    if screenwidth.width() > 1280:
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(18, 13), size=(30, 30), png=png))
        res.append(MultiContentEntryText(pos=(70, 0), size=(830, 56), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=name))
        res.append(MultiContentEntryText(pos=(910, 0), size=(431, 56), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=extra))
    else:
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(12, 5), size=(20, 20), png=png))
        res.append(MultiContentEntryText(pos=(47, 0), size=(551, 37), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=name))
        res.append(MultiContentEntryText(pos=(607, 0), size=(288, 37), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=extra))
    return res


class Playlist_Menu(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if screenwidth.width() > 1280:
            self.l.setFont(0, gFont('jediregular', 36))
            self.l.setItemHeight(56)
        else:
            self.l.setFont(0, gFont('jediregular', 24))
            self.l.setItemHeight(37)


class JediMakerXtream_Playlist(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        skin = skin_path + 'jmx_playlist.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()

        self.setup_title = _('Playlists')


        self['setupActions'] = ActionMap(['ColorActions', 'OkCancelActions'], {'red': self.quit,
         'green': self.addPlaylist,
         'cancel': self.quit}, -2)

        self['key_red'] = StaticText(_('Back'))
        self['key_green'] = StaticText(_('Add Playlist'))
        self['key_yellow'] = StaticText('')
        self['key_blue'] = StaticText('')
        self['key_channelup'] = StaticText('')
        self['key_info'] = StaticText('')
        self['liveupdate'] = Label('')
        self['vodupdate'] = Label('')
        self['seriesupdate'] = Label('')
        jglob.current_selection = 0

        self.list = []
        self.playlists_all = []

        self['playlists'] = Playlist_Menu(self.list)
        self.loadPlaylist()
        self.onLayoutFinish.append(self.__layoutFinished)


    def __layoutFinished(self):
        self.setTitle(self.setup_title)
        if self.list != []:
            self.getCurrentEntry()


    def loadPlaylist(self):
        # check if playlists.txt file exists in specified location
        if os.path.isfile(playlist_path) and os.stat(playlist_path).st_size > 0:

            self['setupActions'] = ActionMap(['ColorActions', 'SetupActions', 'TvRadioActions', 'ChannelSelectEPGActions'], 
            {'red': self.quit,
             'green': self.addPlaylist,
             'yellow': self.editPlaylist,
             'blue': self.deletePlaylist,
             'info': self.openUserInfo,
             'showEPGList':  self.openUserInfo,
             'keyTV': self.createBouquet,
             'ok': self.createBouquet,
             'cancel': self.quit}, -2)

            self['key_yellow'] = StaticText(_('Edit Playlist'))
            self['key_blue'] = StaticText(_('Delete Playlist'))
            self['key_info'] = StaticText(_('User Info'))
            self['description'] =  Label(_('Press OK to create bouquets. \nView your bouquets by exiting the Jedi plugin and then press the TV button. \nGo into EPG Importer plugin settings, select your playlist in sources... Save... Manually download sources.'))
            self['liveupdate'] = Label(_('Live: ---'))
            self['vodupdate'] = Label(_('Vod: ---'))
            self['seriesupdate'] = Label(_('Series: ---'))

            self.playlists_all = jfunc.getPlaylistJson()

            if jglob.firstrun == 0:

                self.getPlaylistUserFile()
                self.removeBlanks()
                self.checkFile()

            self.createSetup()

        # if playlists.txt not exist create one in specified location
        else:
            open(playlist_path, 'a').close()


    def removeBlanks(self):
        with open(playlist_path, 'r+') as f:
            lines = f.readlines()
            f.seek(0)
            f.writelines((line.strip(' ') for line in lines if line.strip()))
            f.truncate()


    def checkFile(self):
        with open(playlist_path, 'r+') as f:
            lines = f.readlines()
            f.seek(0)
            for line in lines:
                if not line.startswith('http://') and not line.startswith('https://') and not line.startswith('#'):
                    line = '# ' + line
                f.write(line)
            f.truncate()


    def getPlaylistUserFile(self):

        self.playlists_all_new = []

        with open(playlist_path) as f:
            lines = f.readlines()
            f.seek(0)
            self.index = 0

            for line in lines:
                #line = line.rstrip()
                valid = False
                address = ''
                playlisttype = ''
                self.playlist_data = {}

                #declare defaults
                self.protocol = 'http://'
                self.domain = ''
                self.port = 80
                self.username = ''
                self.password = ''
                self.type = 'm3u'
                self.output = 'ts'
                host = ''
                #panel_api = ''
                player_api = ''
                output_format = ''
                filename = ''

                if line.startswith('http://'):
                    self.protocol = 'http://'
                elif line.startswith('https://'):
                    self.protocol = 'https://'
                else:
                    continue

                if re.search('(?<=http:\/\/)[^:|^\/]+', line) is not None:
                    self.domain = re.search('(?<=http:\/\/)[^:|^\/]+', line).group()

                if re.search('(?<=https:\/\/)[^:|^\/]+', line) is not None:
                    self.domain = re.search('(?<=https:\/\/)[^:|^\/]+', line).group()

                if re.search('(?<=:)(\d+)(?=\/)', line) is not None:
                    self.port = int(re.search('(?<=:)(\d+)(?=\/)', line).group())

                if re.search('(?<=username=)[^&]+', line) is not None:
                    self.username = re.search('(?<=username=)[^&]+', line).group()

                if re.search('(?<=password=)[^&]+', line) is not None:
                    self.password = re.search('(?<=password=)[^&]+', line).group()

                if re.search('(?<=type=)\w+', line) is not None:
                    self.type = re.search('(?<=type=)\w+', line).group()  

                #self.type = 'm3u'

                if re.search('(?<=output=)\w+', line) is not None:
                    self.output = re.search('(?<=output=)\w+', line).group()

                host =  str(self.protocol) + str(self.domain) + ':' + str(self.port) + '/'
                player_api = str(host) + 'player_api.php?username=' + str(self.username) + '&password=' + str(self.password)
                player_req = urllib2.Request(player_api, headers=hdr)

                if 'get.php' in line and self.domain != '' and self.username != '' and self.password != '':
                    try:
                        response = urllib2.urlopen(player_req, timeout=cfg.timeout.value+2)
                        valid = True

                    except urllib2.URLError as e:
                        print e
                        pass

                    except socket.timeout as e:
                        print e
                        pass

                    except SocketError as e:
                        print e
                        pass

                    if valid == True:
                        try:
                            self.playlist_data = json.load(response, object_pairs_hook=OrderedDict)

                            if 'message' in self.playlist_data['user_info']:
                                del self.playlist_data['user_info']['message']

                            if 'https_port' in self.playlist_data['server_info']:
                                del self.playlist_data['server_info']['https_port']

                            if 'rtmp_port' in self.playlist_data['server_info']:
                                del self.playlist_data['server_info']['rtmp_port']

                            if 'timestamp_now' in self.playlist_data['server_info']:
                                del self.playlist_data['server_info']['timestamp_now']

                            if self.output not in self.playlist_data['user_info']['allowed_output_formats']:
                                self.output = str(self.playlist_data['user_info']['allowed_output_formats'][0])

                        except:
                            pass

                    self.playlist_data['playlist_info'] = OrderedDict([
                      ("index", self.index),
                      ("protocol", self.protocol),
                      ("domain", self.domain),
                      ("port", self.port),
                      ("username", self.username),
                      ("password", self.password),
                      ("type", self.type),
                      ("output", self.output),
                      ("address", line),
                      ("valid", valid),
                      ("playlisttype", 'xtream'),
                    ])


                # Check if external m3u playlist
                elif 'http' in line:
                    try:
                        req = urllib2.Request(line, headers=hdr)
                        response = urllib2.urlopen(req, None, cfg.timeout.value)
                        if 'EXTINF' in response.read():
                            valid = True

                        print e
                        pass

                    except socket.timeout as e:
                        print e
                        pass

                    except SocketError as e:
                        print e
                        pass

                    self.playlist_data['playlist_info'] = OrderedDict([
                      ("index", self.index),
                      ("protocol", self.protocol),
                      ("domain", self.domain),
                      ("port", self.port),
                      ("address", line),
                      ("valid", valid),
                      ("playlisttype", 'external'),
                    ])

                if self.playlists_all != []:
                    for playlist in self.playlists_all:
                        if playlist != {}:
                            if self.playlist_data['playlist_info']['address'] == playlist['playlist_info']['address']:
                                if 'bouquet_info' in playlist:
                                    self.playlist_data['bouquet_info'] = playlist['bouquet_info']
                                break

                self.playlists_all_new.append(self.playlist_data)

                self.index += 1


        # add local M3Us
        for filename in os.listdir(cfg.m3ulocation.value):

            self.playlist_data = {}
            if filename.endswith('.m3u') or filename.endswith('.m3u8'):

                self.playlist_data['playlist_info'] = OrderedDict([
                  ("index", self.index),
                  ("address", filename),
                  ("valid", True),
                  ("playlisttype", 'local'),
                ])

                self.playlists_all_new.append(self.playlist_data)
                self.index += 1

        self.playlists_all =  self.playlists_all_new

        #output to file for testing
        with open(playlist_file, 'w') as f:
            json.dump(self.playlists_all, f)

        jglob.firstrun = 1

    def createSetup(self):
        self.list = []

        for playlist in self.playlists_all:
            playlisttext = ''
            validstate = 'Invalid'

            if playlist != {}:
                if playlist['playlist_info']['playlisttype'] == 'xtream':
                    if 'bouquet_info' in playlist and 'name' in playlist['bouquet_info']:
                        alias = playlist['bouquet_info']['name']
                    else:
                        alias = playlist['playlist_info']['domain']
                else:
                    alias = playlist['playlist_info']['address']

                if 'user_info' in playlist:
                    if playlist['user_info']['auth'] == 1:
                        if playlist['user_info']['status'] == 'Active':
                            validstate = 'Active'
                            playlisttext = 'Active: ' + str(playlist['user_info']['active_cons']) + '  Max: ' + str(playlist['user_info']['max_connections'])
                        elif playlist['user_info']['status'] == 'Banned':
                            validstate = 'Invalid'
                            playlisttext = 'Banned'
                        elif playlist['user_info']['status'] == 'Disabled':
                            validstate = 'Invalid'
                            playlisttext = 'Disabled'   
                else: 
                     if playlist['playlist_info']['playlisttype'] == 'external' and playlist['playlist_info']['valid'] == True and playlist['playlist_info']['domain'] != '':
                        validstate = 'ValidExternal'
                     if playlist['playlist_info']['playlisttype'] == 'local':
                        validstate = 'Unknown'
                self.list.append(PlaylistEntryComponent(playlist['playlist_info']['index'], validstate, str(alias), playlisttext))

        if self.list != []:
            self['playlists'].onSelectionChanged.append(self.getCurrentEntry)
        self['playlists'].l.setList(self.list)

    def getCurrentEntry(self):
        if self.playlists_all != []:
            jglob.current_selection = self['playlists'].getSelectionIndex()
            jglob.current_playlist = self.playlists_all[jglob.current_selection]
        else:
            jglob.current_selection = 0
            jglob.current_playlist = []


        if os.path.isfile(playlist_path) and os.stat(playlist_path).st_size > 0:

            self['liveupdate'].setText(_('Live: ---'))
            self['vodupdate'].setText(_('Vod: ---'))
            self['seriesupdate'].setText(_('Series: ---'))

            for playlist in self.playlists_all:
                if 'bouquet_info' in playlist:
                    if playlist['playlist_info']['address'] == jglob.current_playlist['playlist_info']['address']:
                         self['liveupdate'].setText(_(str('Live: ' + playlist['bouquet_info']['live_update'])))
                         self['vodupdate'].setText(_(str('Vod: ' + playlist['bouquet_info']['vod_update'])))
                         self['seriesupdate'].setText(_(str('Series: ' + playlist['bouquet_info']['series_update'])))


    def quit(self):
        self.close()


    def openUserInfo(self):
        if 'user_info' in jglob.current_playlist:
            if jglob.current_playlist['user_info']['auth'] == 1:
                self.session.open(info.JediMakerXtream_UserInfo)
            else:
                self.session.open(MessageBox, _('Server down or user no longer authorised!'), MessageBox.TYPE_ERROR, timeout=5)
        else:
            if jglob.current_playlist['playlist_info']['playlisttype'] == 'xtream' and jglob.current_playlist['playlist_info']['valid'] == False:
                self.session.open(MessageBox, _('Url is invalid or playlist/user no longer authorised!'), MessageBox.TYPE_ERROR, timeout=5)

            if jglob.current_playlist['playlist_info']['playlisttype'] == 'external':
                self.session.open(MessageBox, _('User Info not avalable for this playlist\n' + jglob.current_playlist['playlist_info']['address']), MessageBox.TYPE_ERROR, timeout=5)  

            if jglob.current_playlist['playlist_info']['playlisttype'] == 'local':
                self.session.open(MessageBox, _('User Info not avalable for this playlist\n' + cfg.m3ulocation.value + jglob.current_playlist['playlist_info']['address']), MessageBox.TYPE_ERROR, timeout=5)


    def refresh(self):
        self.playlists_all = jfunc.getPlaylistJson()
        self.removeBlanks()
        self.getPlaylistUserFile()
        self.createSetup()


    def addPlaylist(self):
        self.session.openWithCallback(self.refresh, addplaylist.JediMakerXtream_AddPlaylist, False)
        return


    def editPlaylist(self):
        if jglob.current_playlist['playlist_info']['playlisttype'] != 'local':
            self.session.openWithCallback(self.refresh, addplaylist.JediMakerXtream_AddPlaylist, True)
        else:
            self.session.open(MessageBox, _('Edit unavailable for local M3Us.\nManually Delete/Amend M3U files in folder.\n' + cfg.m3ulocation.value), MessageBox.TYPE_ERROR, timeout=5)


    def deletePlaylist(self, answer = None):

        if jglob.current_playlist['playlist_info']['playlisttype'] != 'local':
            if answer is None:
                self.session.openWithCallback(self.deletePlaylist, MessageBox, _('Permanently delete selected playlist?'))
            elif answer:
                with open(playlist_path, 'r+') as f:
                    lines = f.readlines()
                    f.seek(0)

                    for line in lines:
                        if line.startswith(jglob.current_playlist['playlist_info']['address']):
                            continue
                        f.write(line)
                    f.truncate()
                    f.close()

                self.playlists_all = jfunc.getPlaylistJson()
                tempplaylist = self.playlists_all

                if self.playlists_all != []:
                    x = 0
                    for playlist in self.playlists_all:
                        if jglob.current_playlist['playlist_info']['address'] == playlist['playlist_info']['address']:
                            del tempplaylist[x]
                            break
                        x += 1

                    self.playlists_all = tempplaylist

                    with open(playlist_file, 'w') as f:
                        json.dump(self.playlists_all, f)
                self['playlists'].moveToIndex(0)
                jglob.current_selection = 0
                self.refresh()

        else:
            self.session.open(MessageBox, _('Delete unavailable for local M3Us.\nManually Delete/Amend M3U files in folder.\n' + cfg.m3ulocation.value), MessageBox.TYPE_ERROR, timeout=5)
        return


    def createBouquet(self):
        jglob.finished = False
        if 'user_info' in jglob.current_playlist:
            if jglob.current_playlist['user_info']['auth'] == 1:
                if jglob.current_playlist['user_info']['status'] == 'Active':

                    self.session.openWithCallback(self.refresh, setupbouquet.JediMakerXtream_Bouquets)
                else:
                    self.session.open(MessageBox, _('Playlist is ' + str(jglob.current_playlist['user_info']['status'])), MessageBox.TYPE_ERROR, timeout=10)
            else:
                self.session.open(MessageBox, _('Server down or user no longer authorised!'), MessageBox.TYPE_ERROR, timeout=5)

        elif 'playlist_info' in jglob.current_playlist:
            if jglob.current_playlist['playlist_info']['valid'] == True:    
                self.session.openWithCallback(self.refresh, setupbouquet.JediMakerXtream_Bouquets)
            else:
                self.session.open(MessageBox, _('Url is invalid or playlist/user no longer authorised!'), MessageBox.TYPE_ERROR, timeout=5)
