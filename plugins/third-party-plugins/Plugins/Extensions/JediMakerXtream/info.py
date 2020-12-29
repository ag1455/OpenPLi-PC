#!/usr/bin/python
# -*- coding: utf-8 -*-

# for localized messages
from . import _
from . import jediglobals as jglob

from .plugin import skin_path

from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from datetime import datetime

from Screens.Screen import Screen


class JediMakerXtream_UserInfo(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        skin = skin_path + 'jmx_userinfo.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()

        self.setup_title = _('User Information')

        self['actions'] = ActionMap(['SetupActions'], {
            'ok': self.quit,
            'cancel': self.quit,
            'menu': self.quit}, -2)
        self['userinfo'] = Label('')
        self['description'] = Label('')
        self['key_red'] = StaticText(_('Close'))

        self.createUserSetup()
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def createUserSetup(self):

        domain = ""
        port = ""
        username = ""
        password = ""

        protocol = jglob.current_playlist['playlist_info']['protocol']
        if 'server_info' in jglob.current_playlist:
            domain = jglob.current_playlist['server_info']['url']
            port = jglob.current_playlist['server_info']['port']
        if 'user_info' in jglob.current_playlist:
            username = jglob.current_playlist['user_info']['username']
            password = jglob.current_playlist['user_info']['password']
        utype = jglob.current_playlist['playlist_info']['type']
        output = jglob.current_playlist['playlist_info']['output']

        self.urltext = str(protocol) + str(domain) + ':' + str(port) + '/get.php?username=' + str(username) + '&password=' + str(password) + '&type=' + str(utype) + '&output=' + str(output)
        self['description'].setText(self.urltext)

        self.usertext = ''

        if 'user_info' in jglob.current_playlist:
            for value in jglob.current_playlist['user_info']:

                if value == 'max_connections':
                    self.usertext += str(value) + ':\t\t' + str(jglob.current_playlist['user_info'][value]) + '\n'
                elif value == 'allowed_output_formats':
                    # remove unicode prefix in json list.
                    output_formats_list = []
                    for output_formats in jglob.current_playlist['user_info'][value]:
                        output_formats_list.append(output_formats.encode('ascii'))
                    self.usertext += str(value) + ':\t' + str(output_formats_list) + '\n'

                # convert unix date to normal date
                elif value == 'exp_date' or value == 'created_at':
                    # if dates are not null convert to normal date
                    if jglob.current_playlist['user_info'][value]:
                        self.usertext += str(value) + ':\t\t' + str(datetime.fromtimestamp(int(jglob.current_playlist['user_info'][value])).strftime('%d-%m-%Y  %H:%M:%S')) + '\n'
                    else:
                        self.usertext += str(value) + ':\t\t' + str(jglob.current_playlist['user_info'][value]) + '\n'
                else:
                    self.usertext += str(value) + ':\t\t' + str(jglob.current_playlist['user_info'][value]) + '\n'

        self['userinfo'].setText(self.usertext)
        self.usertext += '\n'

        if 'server_info' in jglob.current_playlist:
            for value in jglob.current_playlist['server_info']:

                if value == 'time_now':
                    self.usertext += 'local_time' + ':\t\t' + str(jglob.current_playlist['server_info'][value]) + '\n'
                else:
                    self.usertext += str(value) + ':\t\t' + str(jglob.current_playlist['server_info'][value]) + '\n'

        self['userinfo'].setText(self.usertext)

    def quit(self):
        self.close()
