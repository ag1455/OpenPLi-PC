#!/usr/bin/python
# -*- coding: utf-8 -*-

# for localized messages
from . import _

from . import addplaylist, info, setupbouquet
from . import jediglobals as jglob
from . import globalfunctions as jfunc

from .plugin import skin_path, cfg, playlist_path, playlist_file, hdr
from .jediStaticText import StaticText

from collections import OrderedDict
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.List import List
from datetime import datetime
from enigma import getDesktop, eTimer

from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.LoadPixmap import LoadPixmap

import json
import os
import sys

pythonVer = 2
if sys.version_info.major == 3:
    pythonVer = 3

if pythonVer == 3:
    from urllib.request import urlopen, Request
else:
    from urllib2 import urlopen, Request

try:
    from urlparse import urlparse, parse_qs
except:
    from urllib.parse import urlparse, parse_qs

screenwidth = getDesktop(0).size()


class JediMakerXtream_Playlist(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        skin = skin_path + 'jmx_playlist.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()

        self.setup_title = _('Playlists')

        self.drawList = []
        self.playlists_all = []

        # check if playlists.txt file exists in specified location
        if os.path.isfile(playlist_path) and os.stat(playlist_path).st_size > 0:
            self.removeBlanks()
            self.checkFile()
        else:
            open(playlist_path, 'a').close()

        self["playlists"] = List(self.drawList)
        self['lab1'] = Label(_('Loading data... Please wait...'))

        if jglob.playlist_exists is False:
            self['key_red'] = StaticText(_('Back'))
            self['key_green'] = StaticText(_('Add Playlist'))
            self['key_yellow'] = StaticText('')
            self['key_blue'] = StaticText('')
            self['key_channelup'] = StaticText('')
            self['key_info'] = StaticText('')
            self['lastupdate'] = Label('')
            self['liveupdate'] = Label('')
            self['vodupdate'] = Label('')
            self['seriesupdate'] = Label('')
            self['description'] = Label('Press Green to add your playlist details.\nOr enter your playlist url in %s' % cfg.location.value + 'playlists.txt\ne.g. http://domain.xyx:8000/get.php?username=user&password=pass&type=m3u_plus&output=ts')

            self['setupActions'] = ActionMap(['ColorActions', 'OkCancelActions'], {
                'red': self.quit,
                'green': self.addPlaylist,
                'cancel': self.quit}, -2)

        else:
            self['setupActions'] = ActionMap(['ColorActions', 'SetupActions', 'TvRadioActions', 'ChannelSelectEPGActions'], {
                'red': self.quit,
                'green': self.addPlaylist,
                'yellow': self.editPlaylist,
                'blue': self.deletePlaylist,
                'info': self.openUserInfo,
                'showEPGList': self.openUserInfo,
                'keyTV': self.createBouquet,
                'ok': self.createBouquet,
                'cancel': self.quit}, -2)

            self['key_red'] = StaticText(_('Back'))
            self['key_green'] = StaticText(_('Add Playlist'))
            self['key_yellow'] = StaticText(_('Edit Playlist'))
            self['key_blue'] = StaticText(_('Delete Playlist'))
            self['key_info'] = StaticText(_('User Info'))
            self['description'] = Label(_('Press OK to create bouquets. \nView your bouquets by exiting the Jedi plugin and then press the TV button. \nGo into EPG Importer plugin settings, select your playlist in sources... Save... Manually download sources.'))
            self['lastupdate'] = Label(_('Last Update:'))
            self['liveupdate'] = Label('Live: ---')
            self['vodupdate'] = Label('Vod: ---')
            self['seriesupdate'] = Label('Series: ---')

        self.onLayoutFinish.append(self.__layoutFinished)

        jglob.current_selection = 0

        self.list = []

        self.timer = eTimer()
        self.timer.start(100, 1)
        try:  # DreamOS fix
            self.timer_conn = self.timer.timeout.connect(self.loadPlaylist)
        except:
            self.timer.callback.append(self.loadPlaylist)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)
        if self.list != []:
            self.getCurrentEntry()

    def buildListEntry(self, index, status, name, extra):

        if status == 'Active':
            pixmap = LoadPixmap(cached=True, path=skin_path + 'images/active.png')
        if status == 'Invalid':
            pixmap = LoadPixmap(cached=True, path=skin_path + 'images/invalid.png')
        if status == 'ValidExternal':
            pixmap = LoadPixmap(cached=True, path=skin_path + 'images/external.png')
        if status == 'Unknown':
            pixmap = LoadPixmap(cached=True, path=skin_path + 'images/blank.png')
        return(pixmap, str(name), extra)

    def loadPlaylist(self):
        if jglob.firstrun == 0:
            self.playlists_all = jfunc.getPlaylistJson()
            self.getPlaylistUserFile()
        self.createSetup()

    def removeBlanks(self):
        with open(playlist_path, 'r+') as f:
            lines = f.readlines()
            f.seek(0)
            f.writelines((line.strip(' ') for line in lines if line.strip()))
            f.truncate()

    def checkFile(self):
        jglob.playlist_exists = False
        with open(playlist_path, 'r+') as f:
            lines = f.readlines()
            f.seek(0)

            for line in lines:
                if not line.startswith('http://') and not line.startswith('https://') and not line.startswith('#'):
                    line = '# ' + line
                if line.startswith('http://') or line.startswith('https://'):
                    jglob.playlist_exists = True
                f.write(line)
            f.truncate()

    def getPlaylistUserFile(self):
        self.playlists_all_new = []

        with open(playlist_path, 'r+') as f:
            lines = f.readlines()
            f.seek(0)
            f.writelines((line.strip(' ') for line in lines if line.strip()))
            f.seek(0)
            for line in lines:
                if not line.startswith('http://') and not line.startswith('https://') and not line.startswith('#'):
                    line = '# ' + line
                if "=mpegts" in line:
                    line = line.replace("=mpegts", "=ts")
                if "=hls" in line:
                    line = line.replace("=hls", "=m3u8")
                if line.strip() == "#":
                    line = ""
                f.write(line)
            f.seek(0)

        self.index = 0

        for line in lines:
            self.protocol = 'http://'
            self.domain = ''
            self.port = 80
            self.username = ''
            self.password = ''
            self.type = 'm3u'
            self.output = 'ts'
            self.host = ''
            self.name = ''
            player_api = ''
            player = False
            valid = False
            response = ""
            self.playlist_data = {}

            if not line.startswith("#") and line.startswith('http'):
                line = line.strip()

                parsed_uri = urlparse(line)

                self.protocol = parsed_uri.scheme + "://"

                if not self.protocol == "http://" and not self.protocol == "https://":
                    continue

                self.domain = parsed_uri.hostname
                self.name = self.domain
                if line.partition(" #")[-1]:
                    self.name = line.partition(" #")[-1]

                if parsed_uri.port:
                    self.port = parsed_uri.port

                self.host = "%s%s:%s" % (self.protocol, self.domain, self.port)

                query = parse_qs(parsed_uri.query, keep_blank_values=True)

                if "username" in query:
                    self.username = query['username'][0].strip()

                if "password" in query:
                    self.password = query['password'][0].strip()

                if "type" in query:
                    self.type = query['type'][0].strip()

                if "output" in query:
                    self.output = query['output'][0].strip()

                player_api = "%s/player_api.php?username=%s&password=%s" % (self.host, self.username, self.password)
                player_req = Request(player_api, headers=hdr)

                # check if iptv playlist
                if 'get.php' in line and self.domain != '' and self.username != '' and self.password != '':
                    try:
                        response = urlopen(player_req, timeout=cfg.timeout.value + 2)
                        player = True
                        valid = self.checkPanel(response)

                    except Exception as e:
                        print(e)
                        pass

                    except:
                        pass

                    if not valid or response == "":
                        try:
                            req = Request(line, headers=hdr)
                            response = urlopen(req, None, cfg.timeout.value + 5)
                            if 'EXTINF' in response.read():
                                valid = True

                        except Exception as e:
                            print(e)
                            pass

                        except:
                            pass

                else:
                    if 'http' in line:
                        try:
                            req = Request(line, headers=hdr)

                            response = urlopen(req, None, cfg.timeout.value + 5)
                            if pythonVer == 3:
                                if 'EXTINF' in response.read().decode('utf-8'):
                                    valid = True
                            else:
                                if 'EXTINF' in response.read():
                                    valid = True

                        except Exception as e:
                            print(e)
                            pass

                        except:
                            pass

                if player:
                    self.buildPlaylist(line, valid, "xtream")
                else:
                    self.buildPlaylist(line, valid, "extinf")

        # add local M3Us
        filename = ''
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

        self.playlists_all = self.playlists_all_new

        # output to file for testing
        with open(playlist_file, 'w') as f:
            json.dump(self.playlists_all, f)
        jglob.firstrun = 1

    def checkPanel(self, response):
        try:
            self.playlist_data = json.load(response, object_pairs_hook=OrderedDict)

            if 'username' in self.playlist_data['user_info'] and 'password' in self.playlist_data['user_info'] and 'auth' in self.playlist_data['user_info'] and \
                'status' in self.playlist_data['user_info'] and 'active_cons' in self.playlist_data['user_info'] and 'max_connections' in self.playlist_data['user_info'] and \
                    'allowed_output_formats' in self.playlist_data['user_info'] and 'url' in self.playlist_data['server_info'] and 'port' in self.playlist_data['server_info'] and \
                    'server_protocol' in self.playlist_data['server_info']:
                return True
            else:
                return False
        except:
            return False
            pass

    def buildPlaylist(self, line, valid, paneltype):
        serveroffset = 0
        if 'user_info' in self.playlist_data:
            if 'message' in self.playlist_data['user_info']:
                del self.playlist_data['user_info']['message']

            if 'server_info' in self.playlist_data:
                if 'https_port' in self.playlist_data['server_info']:
                    del self.playlist_data['server_info']['https_port']

                if 'rtmp_port' in self.playlist_data['server_info']:
                    del self.playlist_data['server_info']['rtmp_port']

                if 'timestamp_now' in self.playlist_data['server_info']:
                    del self.playlist_data['server_info']['timestamp_now']

                if 'time_now' in self.playlist_data['server_info']:
                    time_now_datestamp = datetime.strptime(str(self.playlist_data['server_info']['time_now']), "%Y-%m-%d %H:%M:%S")
                    serveroffset = datetime.now().hour - time_now_datestamp.hour

            # if user entered output type not valid, get output type from provider.
            if 'allowed_output_formats' in self.playlist_data['user_info']:
                if self.output not in self.playlist_data['user_info']['allowed_output_formats']:
                    try:
                        self.output = str(self.playlist_data['user_info']['allowed_output_formats'][0])
                    except:
                        self.output = "ts"

        if paneltype == "xtream":
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
                ("playlisttype", "xtream"),
                ("name", self.name),
                ("serveroffset", serveroffset),
            ])

        else:
            self.playlist_data['playlist_info'] = OrderedDict([
                ("index", self.index),
                ("protocol", self.protocol),
                ("domain", self.domain),
                ("port", self.port),
                ("address", line),
                ("valid", valid),
                ("playlisttype", 'external'),
                ("name", self.name),
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

    def createSetup(self):
        self['playlists'].setIndex(0)

        self['lab1'].setText('')
        self.list = []
        for playlist in self.playlists_all:
            playlisttext = ''
            validstate = 'Invalid'

            if playlist != {}:
                if playlist['playlist_info']['playlisttype'] == 'xtream' or 'get.php' in playlist['playlist_info']['address']:
                    alias = playlist['playlist_info']['name']
                else:
                    alias = playlist['playlist_info']['address']

                if 'user_info' in playlist:
                    if 'auth' in playlist['user_info']:
                        if playlist['user_info']['auth'] == 1:
                            if 'status' in playlist['user_info']:
                                if playlist['user_info']['status'] == 'Active':
                                    validstate = 'Active'
                                    playlisttext = _('Active: ') + str(playlist['user_info']['active_cons']) + _('  Max: ') + str(playlist['user_info']['max_connections'])
                                elif playlist['user_info']['status'] == 'Banned':
                                    playlisttext = _('Banned')
                                elif playlist['user_info']['status'] == 'Disabled':
                                    playlisttext = _('Disabled')
                                elif playlist['user_info']['status'] == 'Expired':
                                    playlisttext = _('Expired')
                else:
                    if playlist['playlist_info']['playlisttype'] == 'external' and playlist['playlist_info']['valid'] is True and playlist['playlist_info']['domain'] != '':
                        validstate = 'ValidExternal'
                    elif playlist['playlist_info']['playlisttype'] == 'local':
                        validstate = 'Unknown'
                    else:
                        playlisttext = 'Server Not Responding'

                self.list.append([playlist['playlist_info']['index'], validstate, str(alias), playlisttext])

        if self.list != []:
            self.getCurrentEntry()
            self['playlists'].onSelectionChanged.append(self.getCurrentEntry)

        self.drawList = []
        self.drawList = [self.buildListEntry(x[0], x[1], x[2], x[3]) for x in self.list]
        self["playlists"].setList(self.drawList)

    def getCurrentEntry(self):
        if self.list != []:
            jglob.current_selection = self['playlists'].getIndex()
            jglob.current_playlist = self.playlists_all[jglob.current_selection]

        else:
            jglob.current_selection = 0
            jglob.current_playlist = []

        if os.path.isfile(playlist_path) and os.stat(playlist_path).st_size > 0:

            self['liveupdate'].setText('Live: ---')
            self['vodupdate'].setText('Vod: ---')
            self['seriesupdate'].setText('Series: ---')

            for playlist in self.playlists_all:
                if 'bouquet_info' in playlist:
                    if playlist['playlist_info']['address'] == jglob.current_playlist['playlist_info']['address']:
                        self['liveupdate'].setText(_(str('Live: ' + playlist['bouquet_info']['live_update'])))
                        self['vodupdate'].setText(_(str('Vod: ' + playlist['bouquet_info']['vod_update'])))
                        self['seriesupdate'].setText(_(str('Series: ' + playlist['bouquet_info']['series_update'])))

    def quit(self):
        jglob.firstrun = 0
        self.close()

    def openUserInfo(self):
        if 'user_info' in jglob.current_playlist:
            if 'auth' in jglob.current_playlist['user_info']:
                if jglob.current_playlist['user_info']['auth'] == 1:
                    self.session.open(info.JediMakerXtream_UserInfo)
                else:
                    self.session.open(MessageBox, _('Server down or user no longer authorised!'), MessageBox.TYPE_ERROR, timeout=5)
        else:
            if jglob.current_playlist['playlist_info']['playlisttype'] == 'xtream' and jglob.current_playlist['playlist_info']['valid'] is False:
                self.session.open(MessageBox, _('Url is invalid or playlist/user no longer authorised!'), MessageBox.TYPE_ERROR, timeout=5)

            if jglob.current_playlist['playlist_info']['playlisttype'] == 'external':
                self.session.open(MessageBox, _('User Info not available for this playlist\n') + jglob.current_playlist['playlist_info']['address'], MessageBox.TYPE_ERROR, timeout=5)

            if jglob.current_playlist['playlist_info']['playlisttype'] == 'local':
                self.session.open(MessageBox, _('User Info not available for this playlist\n') + cfg.m3ulocation.value + jglob.current_playlist['playlist_info']['address'], MessageBox.TYPE_ERROR, timeout=5)

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
            self.session.open(MessageBox, _('Edit unavailable for local M3Us.\nManually Delete/Amend M3U files in folder.\n') + cfg.m3ulocation.value, MessageBox.TYPE_ERROR, timeout=5)

    def deletePlaylist(self, answer=None):
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

                self['playlists'].setIndex(0)
                jglob.current_selection = 0
                self.refresh()

        else:
            self.session.open(MessageBox, _('Delete unavailable for local M3Us.\nManually Delete/Amend M3U files in folder.\n') + cfg.m3ulocation.value, MessageBox.TYPE_ERROR, timeout=5)
        return

    def createBouquet(self):
        jglob.finished = False
        if 'user_info' in jglob.current_playlist:
            if 'auth' in jglob.current_playlist['user_info']:
                if jglob.current_playlist['user_info']['auth'] == 1:
                    if 'status' in jglob.current_playlist['user_info']:
                        if jglob.current_playlist['user_info']['status'] == 'Active':

                            self.session.openWithCallback(self.refresh, setupbouquet.JediMakerXtream_Bouquets)
                        else:
                            self.session.open(MessageBox, _('Playlist is ') + str(jglob.current_playlist['user_info']['status']), MessageBox.TYPE_ERROR, timeout=10)
                else:
                    self.session.open(MessageBox, _('Server down or user no longer authorised!'), MessageBox.TYPE_ERROR, timeout=5)

        elif 'playlist_info' in jglob.current_playlist:
            if jglob.current_playlist['playlist_info']['valid'] is True:
                self.session.openWithCallback(self.refresh, setupbouquet.JediMakerXtream_Bouquets)
            else:
                self.session.open(MessageBox, _('Url is invalid or playlist/user no longer authorised!'), MessageBox.TYPE_ERROR, timeout=5)
