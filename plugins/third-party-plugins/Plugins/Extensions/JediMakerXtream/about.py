#!/usr/bin/python
# -*- coding: utf-8 -*-

# for localized messages
from . import _

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from .plugin import skin_path
from Screens.Screen import Screen


class JediMakerXtream_About(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        skin = skin_path + 'jmx_about.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()

        self.setup_title = _('About')

        self['actions'] = ActionMap(['SetupActions'], {
            'ok': self.quit,
            'cancel': self.quit,
            'menu': self.quit}, -2)
        self['key_red'] = StaticText(_('Close'))
        self['about'] = Label('')
        self.onFirstExecBegin.append(self.createSetup)
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def createSetup(self):
        self.credit = 'JediMakerXtream V6.20 (C) 2018 - 2021 - KiddaC\n\n'
        self.credit += 'Support for this plugin can be found on https://linuxsat-support.com\n\n'
        self.credit += 'Plugin enables the simple bouquet creation of standard xtream and M3U playlist(s).\n'
        self.credit += '*Playing streams via the plugin is currently unavailable.\n'
        self.credit += 'Play your files via your TV bouquets.\n\n'
        self.credit += 'Credits:\n'
        self.credit += 'AutoBouquetMaker, EpgImporter, AutoBackup (used as code reference).\n'
        self.credit += 'Lululla for all the hard work done on XCPlugin and assistance with the project.\n'
        self.credit += 'Massive thanks to Seagen for his endless multi image testing.\n'
        self.credit += 'And thanks to all the other testers and those who helped in the development of this project.\n\n'
        self.credit += "If you would like to donate to my redbull, cigs and stress fund. https://paypal.me/kiddac \n"
        self.credit += 'Cheers'
        self['about'].setText(self.credit)

    def quit(self):
        self.close()
