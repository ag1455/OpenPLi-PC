#!/usr/bin/python
# -*- coding: utf-8 -*-

from Screens.Screen import Screen
from plugin import skin_path, cfg, autoStartTimer

from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Components.Sources.List import List
from Components.ConfigList import *
from Components.config import *

from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox


class JediMakerXtream_Settings(ConfigListScreen, Screen):

    def __init__(self, session):
        Screen.__init__(self, session)


        skin = skin_path + 'jmx_settings.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()

        self.setup_title = _('Settings')

        self.onChangedEntry = [ ]
        self.session = session

        self['actions'] = ActionMap(["SetupActions"],
        {
         'cancel': self.cancel,
         'save': self.save,
         'ok': self.ok,

        }, -2)

        self["HelpWindow"] = Pixmap()
        self["VKeyIcon"] = Pixmap()
        self["VKeyIcon"].hide()


        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Save'))
        self['description'] = Label('')


        self.list = []
        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
        self.initConfig()
        self.createSetup()
        self.onLayoutFinish.append(self.layoutFinished)


    def layoutFinished(self):
        self.setTitle(self.setup_title)

    def initConfig(self):
        self.cfg_location = getConfigListEntry(_('playlists.txt location'), cfg.location, _("Select the location of your playlists.txt file. i.e. /media/hdd/playlists. Press 'OK' to change location.\n\nDefault location is /etc/enigma2/jediplaylists"))
        self.cfg_m3ulocation = getConfigListEntry(_('Local M3U File location'), cfg.m3ulocation, _("Select the location of your local m3u files. i.e. /media/hdd/playlists. Press 'OK' to change location.\n\nDefault location is /etc/enigma2/jediplaylists"))
        self.cfg_enabled = getConfigListEntry(_('Automatic live bouquet update'), cfg.enabled, _('Update your live bouquets automatically.'))
        self.cfg_wakeup =  getConfigListEntry(_('Automatic live update start time'), cfg.wakeup, _('Select the time of the automatic update.'))
        self.cfg_main = getConfigListEntry(_('Show in main menu'), cfg.main, _('Display JediMakerXtream in Main Menu.\n*Restart GUI required.'))
        self.cfg_extensions = getConfigListEntry(_('Show in extensions'), cfg.extensions, _('Quick start JediMakerXtream playlists from extensions menu.\n*Restart GUI required.'))
        self.cfg_skin = getConfigListEntry(_('Select skin'), cfg.skin, _('Select from the available skins.\n*Restart GUI required.'))
        self.cfg_timeout = getConfigListEntry(_('Server timeout (seconds)'), cfg.timeout, _('Amend the timeout on server calls.\n\nCan be increased for very large playlists, slow servers, or slow proxies.'))
        self.cfg_catchup = getConfigListEntry(_('Prefix CatchUp channels'), cfg.catchup, _('Mark channels that have catchup with a prefix in your bouquets.'))
        self.cfg_catchupprefix = getConfigListEntry(_('Select Catchup prefix symbol'), cfg.catchupprefix, _('Select the symbol to prefix your catchup channels with.'))

    def createSetup(self):
        self.list = []
        self.list.append(self.cfg_location)
        self.list.append(self.cfg_m3ulocation)
        self.list.append(self.cfg_enabled)

        if cfg.enabled.value == True:
            self.list.append(self.cfg_wakeup)

        self.list.append(self.cfg_catchup)
        if cfg.catchup.value == True:
            self.list.append(self.cfg_catchupprefix)
        self.list.append(self.cfg_timeout)
        self.list.append(self.cfg_main)
        self.list.append(self.cfg_extensions)
        self.list.append(self.cfg_skin)

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
            if isinstance(self['config'].getCurrent()[1], ConfigEnableDisable):
                self.createSetup()
        except:
            pass


	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())   


    def save(self):
        global autoStartTimer

        if self['config'].isChanged():
            for x in self['config'].list:
                x[1].save()
            configfile.save()

        if autoStartTimer is not None:
            autoStartTimer.update()
        self.close(True)
        return


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


    def ok(self):
        ConfigListScreen.keyOK(self)
        sel = self['config'].getCurrent()[1]
        if sel and sel == cfg.location:
            self.setting = 'playlist'
            self.openDirectoryBrowser(cfg.location.value)
        if sel and sel == cfg.m3ulocation:
            self.setting = 'm3u'
            self.openDirectoryBrowser(cfg.m3ulocation.value)
        else:
            pass


    def openDirectoryBrowser(self, path):
        try:
            self.session.openWithCallback(
             self.openDirectoryBrowserCB,
             LocationBox,
             windowTitle=_('Choose Directory:'),
             text=_('Choose directory'),
             currDir=str(path),
             bookmarks=config.movielist.videodirs,
             autoAdd=False,
             editDir=True,
             inhibitDirs=['/bin', '/boot', '/dev', '/home', '/lib', '/proc', '/run', '/sbin', '/sys', '/var'],
             minFree=15)
        except Exception as e:
            print ('[jmxSettings] openDirectoryBrowser get failed: ', str(e))


    def openDirectoryBrowserCB(self, path):
            if path is not None:
                if self.setting == 'playlist':
                    cfg.location.setValue(path)
                if self.setting == 'm3u':
                    cfg.m3ulocation.setValue(path)
            return
