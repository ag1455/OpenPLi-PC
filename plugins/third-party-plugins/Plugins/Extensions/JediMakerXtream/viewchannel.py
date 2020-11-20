#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Components.Label import Label
from plugin import skin_path
from Screens.Screen import Screen


import jediglobals as jglob


class JediMakerXtream_ViewChannels(Screen):

    def __init__(self, session, current):
        Screen.__init__(self, session)
        self.session = session
        skin = skin_path + 'jmx_channels.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = _('Channel List')

        self.current = current
        self.channellist = []
        self['list'] = MenuList(self.channellist)

        self['description'] = Label('')

        self['actions'] = ActionMap(['SetupActions'], {
         'ok': self.quit,
         'cancel': self.quit,
         'menu': self.quit,
         'up': self['list'].up,
         'down': self['list'].down,
         'right': self['list'].pageDown,
         'left': self['list'].pageUp}, -2)

        self['key_red'] = StaticText(_('Close'))
        self.getchannels()
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)


    def quit(self):
        self.close()


    def getchannels(self):
        if self.current[1] == 'Live':
            for channel in jglob.livestreams:
                if str(channel['category_id']) == str(self.current[2]):
                    self.channellist.append(str(channel['name']).strip())

        if self.current[1] == 'VOD':
            for channel in jglob.vodstreams:
                if str(channel['category_id']) == str(self.current[2]):
                    self.channellist.append(str(channel['name']).strip())

        if self.current[1] == 'Series':
            for channel in jglob.seriesstreams:
                if str(channel['category_id']) == str(self.current[2]):
                    self.channellist.append(str(channel['name']).strip())

        self.channellist.sort()
