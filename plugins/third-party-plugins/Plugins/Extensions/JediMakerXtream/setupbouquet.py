#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.ActionMap import ActionMap, NumberActionMap
from Components.config import *
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from plugin import skin_path, cfg, playlist_file
from Screens.Screen import Screen
from collections import OrderedDict
from Screens.VirtualKeyBoard import VirtualKeyBoard
from datetime import datetime
from JediSelectionList import SelectionList, SelectionEntryComponent

import os
import json
import buildbouquet, playlists
import jediglobals as jglob
import globalfunctions as jfunc
import downloads

class JediMakerXtream_Bouquets(ConfigListScreen, Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        skin = skin_path + 'jmx_settings.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()

        self.setup_title = _('Bouquets Settings')

        self['actions'] = ActionMap(['SetupActions'], {
         'save': self.save,
         'cancel': self.cancel
         }, -2)

        self.onChangedEntry = []
        self.list = []

        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)

        address = jglob.current_playlist['playlist_info']['address']
        self.playlisttype = jglob.current_playlist['playlist_info']['playlisttype']

        #defaults
        if cfg.bouquet_id.value:
            jglob.bouquet_id = cfg.bouquet_id.value
        else: 
            jglob.bouquet_id = 666

        if self.playlisttype != 'xtream':
            jglob.epg_provider = False
        else:
            jglob.epg_provider = True

        if self.playlisttype == 'xtream' or self.playlisttype == 'external':
            protocol = jglob.current_playlist['playlist_info']['protocol']
            domain = jglob.current_playlist['playlist_info']['domain']
            port = str(jglob.current_playlist['playlist_info']['port'])   
            host = str(protocol) + str(domain) + ':' + str(port) + '/' 

        if self.playlisttype == 'xtream':
            username = jglob.current_playlist['playlist_info']['username']
            password = jglob.current_playlist['playlist_info']['password']
            player_api = str(host) + 'player_api.php?username=' + str(username) + '&password=' + str(password)

            jglob.xmltv_address = str(host) + 'xmltv.php?username=' + str(username) + '&password=' + str(password) 

            LiveCategoriesUrl = player_api + '&action=get_live_categories'
            VodCategoriesUrl = player_api + '&action=get_vod_categories'
            SeriesCategoriesUrl = player_api + '&action=get_series_categories'

            LiveStreamsUrl = player_api + '&action=get_live_streams'
            VodStreamsUrl = player_api + '&action=get_vod_streams'
            SeriesUrl = player_api + '&action=get_series'

        if self.playlisttype != 'local':
            jglob.name = domain
        else:
            jglob.name = address

        jglob.old_name = jglob.name
        jglob.categories = []

        if self.playlisttype == 'xtream':
            downloads.downloadlivecategories(LiveCategoriesUrl)
            downloads.downloadvodcategories(VodCategoriesUrl)
            downloads.downloadseriescategories(SeriesCategoriesUrl)

            if jglob.haslive:
                downloads.downloadlivestreams(LiveStreamsUrl)
            if jglob.hasvod:
                downloads.downloadvodstreams(VodStreamsUrl)
            if jglob.hasseries:
                downloads.downloadseriesstreams(SeriesUrl)

        if 'bouquet_info' in jglob.current_playlist and jglob.current_playlist['bouquet_info'] != {}:
            jfunc.readbouquetdata()
        else:
            jglob.live_type = '4097'
            jglob.vod_type = '4097'
            jglob.vod_order = 'original'

            jglob.epg_rytec_uk = False
            jglob.epg_swap_names = False
            jglob.epg_force_rytec_uk = False

            jglob.live = True
            jglob.vod = False
            jglob.series = False
            jglob.prefix_name = True


        self.createConfig()
        self.createSetup()
        self.onLayoutFinish.append(self.__layoutFinished)

        self['VirtualKB'].setEnabled(False)
        self['HelpWindow'] = Pixmap()
        self['VKeyIcon'] = Pixmap()
        self['HelpWindow'].hide()
        self['VKeyIcon'].hide()

        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Continue'))
        self['description'] = Label('')


    def __layoutFinished(self):
        self.setTitle(self.setup_title)


    def createConfig(self):
        self.NameCfg = NoSave(ConfigText(default=jglob.name, fixed_size=False))

        self.PrefixNameCfg = NoSave(ConfigYesNo(default=jglob.prefix_name))

        self.LiveCategoriesCfg = NoSave(ConfigYesNo(default=jglob.live))
        self.VodCategoriesCfg = NoSave(ConfigYesNo(default=jglob.vod))
        self.SeriesCategoriesCfg = NoSave(ConfigYesNo(default=jglob.series))

        self.XmltvCfg = NoSave(ConfigText(default=jglob.xmltv_address, fixed_size=False))

        self.VodOrderCfg = NoSave(ConfigSelection(default='alphabetical', choices=[('original', _('Original Order')), ('alphabetical', _('A-Z')), ('date', _('Newest First')), ('date2', _('Oldest First'))]))

        self.EpgProviderCfg = NoSave(ConfigEnableDisable(default=jglob.epg_provider))
        self.EpgRytecUKCfg = NoSave(ConfigEnableDisable(default=jglob.epg_rytec_uk))
        self.EpgSwapNamesCfg = NoSave(ConfigEnableDisable(default=jglob.epg_swap_names))
        self.ForceRytecUKCfg = NoSave(ConfigEnableDisable(default=jglob.epg_force_rytec_uk))

        if os.path.isdir('/usr/lib/enigma2/python/Plugins/SystemPlugins/ServiceApp'):
            self.LiveTypeCfg = NoSave(ConfigSelection(default=jglob.live_type, choices=[
             ('1', _('DVB(1)')),
             ('4097', _('IPTV(4097)')),
             ('5001', _('GStreamer(5001)')),
             ('5002', 'ExtPlayer(5002)')]))
            self.VodTypeCfg = NoSave(ConfigSelection(default=jglob.vod_type, choices=[
             ('1', _('DVB(1)')),
             ('4097', _('IPTV(4097)')),
             ('5001', _('GStreamer(5001)')),
             ('5002', 'ExtPlayer(5002)')]))
        else:
            self.LiveTypeCfg = NoSave(ConfigSelection(default=jglob.live_type, choices=[('1', _('DVB(1)')), ('4097', _('IPTV(4097)'))]))
            self.VodTypeCfg = NoSave(ConfigSelection(default=jglob.vod_type, choices=[('1', _('DVB(1)')), ('4097', _('IPTV(4097)'))]))


    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_('Bouquet name'), self.NameCfg, _('\nEnter name to be shown as a prefix in your bouquets')))

        self.list.append(getConfigListEntry(_('Use name as bouquet prefix'), self.PrefixNameCfg, _('\nUse provider name prefix in your bouquets')))

        if self.playlisttype == 'xtream':

            if jglob.haslive:
                self.list.append(getConfigListEntry(_('Live categories'), self.LiveCategoriesCfg, _('\nInclude LIVE categories in your bouquets.')))

            if self.LiveCategoriesCfg.value == True:
                self.list.append(getConfigListEntry(_('Stream type for Live'), self.LiveTypeCfg, _('\nThis setting allows you to choose which player E2 will use for your live streams.\nIf your live streams do not play try changing this setting.')))

            if jglob.hasvod:
                self.list.append(getConfigListEntry(_('VOD categories'), self.VodCategoriesCfg, _('\nInclude VOD categories in your bouquets.')))

            if jglob.hasseries:
                self.list.append(getConfigListEntry(_('Series categories'), self.SeriesCategoriesCfg, _('\nInclude SERIES categories in your bouquets. \n** Note: Selecting Series can be slow to populate the lists.**')))

            if self.VodCategoriesCfg.value == True or self.SeriesCategoriesCfg.value == True:
                self.list.append(getConfigListEntry(_('Stream type for VOD/SERIES'), self.VodTypeCfg, _('\nThis setting allows you to choose which player E2 will use for your VOD/Series streams.\nIf your VOD streams do not play try changing this setting.')))

            if self.VodCategoriesCfg.value == True:
                self.list.append(getConfigListEntry(_('VOD bouquet order'), self.VodOrderCfg, _('\nSelect the sort order for your VOD Bouquets.')))

            if self.LiveCategoriesCfg.value == True and jglob.has_epg_importer: 
                self.list.append(getConfigListEntry(_('Use your provider EPG'), self.EpgProviderCfg, _('\nMake provider xmltv for use in EPG Importer.\nProvider source needs to be selected in EPG Importer plugin.')))

            if self.EpgProviderCfg.value == True and jglob.has_epg_importer:
                self.list.append(getConfigListEntry(_('EPG url'), self.XmltvCfg, _('Enter the EPG url for your playlist. If unknown leave as default.')))

            if self.LiveCategoriesCfg.value == True and jglob.has_epg_importer: 
                self.list.append(getConfigListEntry(_('Use Rytec UK EPG'), self.EpgRytecUKCfg, _("\nTry to match the UK Rytec names in the background to populate UK EPG.\nNote this will override your provider's UK EPG.")))

            if self.EpgRytecUKCfg.value == True:
                self.list.append(getConfigListEntry(_('Replace UK channel names in bouquets with swap names'), self.EpgSwapNamesCfg, _("\nThis will amend the UK channels names in channel bouquets to that of the computed swap names.")))    
                self.list.append(getConfigListEntry(_('UK only: Force UK name swap'), self.ForceRytecUKCfg, _('Use for UK providers that do not specify UK in the category title or channel title.\nMay cause non UK channels to have the wrong epg.\nTrying creating bouquets without this option turned off first.')))    

        else:
            self.list.append(getConfigListEntry(_('Live Categories'), self.LiveCategoriesCfg, _('\nInclude LIVE categories in your bouquets if available.')))

            if self.LiveCategoriesCfg.value == True:
                self.list.append(getConfigListEntry(_('Stream type for Live'), self.LiveTypeCfg, _('\nThis setting allows you to choose which player E2 will use for your live streams.\nIf your live streams do not play try changing this setting.')))

            self.list.append(getConfigListEntry(_('Vod Categories'), self.VodCategoriesCfg, _('\nInclude VOD categories in your bouquets if available.')))

            self.list.append(getConfigListEntry(_('Series categories'), self.SeriesCategoriesCfg, _('\nInclude SERIES categories in your bouquets. \n** Note: Selecting Series can be slow to populate the lists.**')))

            if self.VodCategoriesCfg.value == True or self.SeriesCategoriesCfg.value == True:
                self.list.append(getConfigListEntry(_('Stream type for VOD/Series'), self.VodTypeCfg, _('\nThis setting allows you to choose which player E2 will use for your VOD/Series streams.\nIf your VOD streams do not play try changing this setting.')))

            if self.LiveCategoriesCfg.value == True and jglob.has_epg_importer:
                self.list.append(getConfigListEntry(_('Use your provider EPG'), self.EpgProviderCfg, _('\nMake provider xmltv for use in EPG Importer.\n Source needs to be selected in EPG Importer plugin.')))

            if self.EpgProviderCfg.value == True and jglob.has_epg_importer:  
                self.list.append(getConfigListEntry(_('EPG url'), self.XmltvCfg, _('Enter the EPG url for your playlist. If unknown leave as default.')))

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
            if isinstance(self['config'].getCurrent()[1], ConfigYesNo) or isinstance(self['config'].getCurrent()[1], ConfigEnableDisable):
                self.createSetup()
        except:
            pass


    def save(self):
        if self['config'].isChanged():
            for x in self['config'].list:
                x[1].save()

        self['config'].instance.moveSelectionTo(1)

        jglob.finished = False
        jglob.name = self.NameCfg.value
        jglob.prefix_name = self.PrefixNameCfg.value
        jglob.live = self.LiveCategoriesCfg.value
        jglob.live_type = self.LiveTypeCfg.value
        jglob.vod = self.VodCategoriesCfg.value
        jglob.series = self.SeriesCategoriesCfg.value
        jglob.vod_type = self.VodTypeCfg.value
        jglob.vod_order = self.VodOrderCfg.value
        jglob.epg_provider = self.EpgProviderCfg.value
        jglob.epg_rytec_uk = self.EpgRytecUKCfg.value
        jglob.epg_swap_names = self.EpgSwapNamesCfg.value
        jglob.epg_force_rytec_uk = self.ForceRytecUKCfg.value

        jglob.xmltv_address = self.XmltvCfg.value

        self.session.openWithCallback(self.finishedCheck, JediMakerXtream_ChooseBouquets)


    def cancel(self):
        self.close()


    def finishedCheck(self):
        if jglob.finished:
            self.close()


class JediMakerXtream_ChooseBouquets(Screen):

    def __init__(self, session):
        self.session = session

        skin = skin_path + 'jmx_bouquets.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()

        self.setup_title = _('Choose Bouquets')
        Screen.__init__(self, session)

        cat_list = ''

        self.currentSelection = 0

        self['key_red'] = StaticText('')
        self['key_green'] = StaticText('')
        self['key_yellow'] = StaticText('')
        self['key_blue'] = StaticText('')
        self['key_info'] = StaticText('')
        self['description'] = Label('')

        self.playlisttype = jglob.current_playlist['playlist_info']['playlisttype']

        if self.playlisttype == 'xtream':

            jfunc.checkcategories(jglob.live ,jglob.vod, jglob.series)

            if 'bouquet_info' in jglob.current_playlist and jglob.current_playlist['bouquet_info'] != {}:
                #jfunc.SelectedCategories(jglob.live, jglob.vod, jglob.series)
                jfunc.IgnoredCategories(jglob.live, jglob.vod, jglob.series)

            self.cat_list = [ SelectionEntryComponent(x[0], x[1], x[2], x[3]) for x in jglob.categories ]

            self['list'] = SelectionList(self.cat_list, enableWrapAround=True)

            self['setupActions'] = ActionMap(['ColorActions', 'SetupActions', 'ChannelSelectEPGActions'],
            {'red': self.keyCancel,
             'green': self.keyGreen,
             'yellow': self['list'].toggleAllSelection,
             'blue': self.clearAll,
             'save': self.keyGreen,
             'cancel': self.keyCancel,
             'ok': self['list'].toggleSelection,
             'info': self.viewChannels,
             'showEPGList': self.viewChannels
             }, -2)

            self['key_red'] = StaticText(_('Cancel'))
            self['key_green'] = StaticText(_('Create'))
            self['key_yellow'] = StaticText(_('Toggle All'))
            self['key_blue'] = StaticText(_('Clear All'))
            self['key_info'] = StaticText(_('Show Channels'))

            self['description'] = Label(_('Select the playlist categories you wish to create bouquets for. \nPress OK to toggle the selection. \nPress INFO to show the channels in this category.'))

            self['list'].onSelectionChanged.append(self.getCurrentEntry)
        else:
            self.onFirstExecBegin.append(self.m3uStart)
        self.onLayoutFinish.append(self.__layoutFinished)


    def getCurrentEntry(self):
        self.currentSelection = self['list'].getSelectionIndex()


    def viewChannels(self):
        import viewchannel
        self.session.open(viewchannel.JediMakerXtream_ViewChannels, self.cat_list[self.currentSelection][0])


    def m3uStart(self):
        downloads.getM3uCategories(jglob.live, jglob.vod)
        self.makeBouquetData()
        self.session.open(buildbouquet.JediMakerXtream_BuildBouquets)
        self.close()


    def __layoutFinished(self):
        self.setTitle(self.setup_title)


    def clearAll(self):
        for idx, item in enumerate(self.cat_list):
            item = self.cat_list[idx][0]
            self.cat_list[idx] = SelectionEntryComponent(item[0], item[1], item[2], 0)
            self['list'].setList(self.cat_list)


    def keyCancel(self):
        self.close()


    def keyGreen(self):

        for selected in self['list'].getSelectionsList():
            if selected[1] == 'Live':
                jglob.live = True
                continue
            if selected[1] == 'VOD':
                jglob.vod = True
                continue
            if selected[1] == 'Series':
                jglob.series = True
                continue
            if jglob.live and jglob.vod and jglob.series:
                break


        self.makeBouquetData()
        self.session.openWithCallback(self.close, buildbouquet.JediMakerXtream_BuildBouquets)


    def makeBouquetData(self):

        jglob.current_playlist['bouquet_info'] = {}

        jglob.current_playlist['bouquet_info'] = OrderedDict([
        ('bouquet_id', jglob.bouquet_id),
        ('name', jglob.name),
        ('oldname', jglob.old_name),
        ('live_type', jglob.live_type),
        ('vod_type', jglob.vod_type),
        ('selected_live_categories', []),
        ('selected_vod_categories', []),
        ('selected_series_categories', []),
        ('ignored_live_categories', []),
        ('ignored_vod_categories', []),
        ('ignored_series_categories', []),
        ('live_update', '---'),
        ('vod_update',  '---'),
        ('series_update',  '---'),
        ('xmltv_address', jglob.xmltv_address),
        ('vod_order', jglob.vod_order),
        ('epg_provider', jglob.epg_provider),
        ('epg_rytec_uk', jglob.epg_rytec_uk),
        ('epg_swap_names', jglob.epg_swap_names),
        ('epg_force_rytec_uk', jglob.epg_force_rytec_uk),
        ('prefix_name', jglob.prefix_name),
         ])

        if jglob.live:
            jglob.current_playlist['bouquet_info']['live_update'] = datetime.now().strftime('%x  %X')

        if jglob.vod:
            jglob.current_playlist['bouquet_info']['vod_update'] = datetime.now().strftime('%x  %X')

        if jglob.series:
            jglob.current_playlist['bouquet_info']['series_update'] = datetime.now().strftime('%x  %X')

        if self.playlisttype == 'xtream':
            jglob.selectedcategories = self['list'].getSelectionsList()

            for category in self['list'].getSelectionsList():
                if category[1] == 'Live':
                    jglob.current_playlist['bouquet_info']['selected_live_categories'].append(category[0])
                elif category[1] == 'Series':
                    jglob.current_playlist['bouquet_info']['selected_series_categories'].append(category[0])
                elif category[1] == 'VOD':
                    jglob.current_playlist['bouquet_info']['selected_vod_categories'].append(category[0])

            jglob.ignoredcategories = self['list'].getUnSelectedList()

            for category in self['list'].getUnSelectedList():
                if category[1] == 'Live':
                    jglob.current_playlist['bouquet_info']['ignored_live_categories'].append(category[0])
                elif category[1] == 'Series':
                    jglob.current_playlist['bouquet_info']['ignored_series_categories'].append(category[0])
                elif category[1] == 'VOD':
                    jglob.current_playlist['bouquet_info']['ignored_vod_categories'].append(category[0])



        else:
            for category in jglob.getm3ustreams:
                if category[4] == 'live' and category[0] not in jglob.current_playlist['bouquet_info']['selected_live_categories']:
                    jglob.current_playlist['bouquet_info']['selected_live_categories'].append(category[0])
                elif category[4] == 'vod' and category[0] not in jglob.current_playlist['bouquet_info']['selected_vod_categories']:
                    jglob.current_playlist['bouquet_info']['selected_vod_categories'].append(category[0])

        self.playlists_all = jfunc.getPlaylistJson()

        for playlist in self.playlists_all:
            if playlist['playlist_info']['index'] == jglob.current_playlist['playlist_info']['index']:
                playlist['bouquet_info'] = jglob.current_playlist['bouquet_info']

                break

        with open(playlist_file, 'w') as f:
            json.dump(self.playlists_all, f)
