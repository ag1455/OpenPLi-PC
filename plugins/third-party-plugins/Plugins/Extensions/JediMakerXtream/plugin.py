#!/usr/bin/python
# -*- coding: utf-8 -*-

# for localized messages
from . import _
from . import jediglobals as jglob

from Components.ActionMap import HelpableActionMap
from Components.config import config, ConfigSelection, ConfigNumber, ConfigClock, ConfigDirectory, ConfigSubsection, ConfigYesNo
from enigma import eTimer, eServiceReference, getDesktop, addFont
from Plugins.Plugin import PluginDescriptor
from Screens.EpgSelection import EPGSelection
from Screens.MessageBox import MessageBox
from ServiceReference import ServiceReference

import os


vixEPG = False

try:
    from Screens.EpgSelectionGrid import EPGSelectionGrid
    vixEPG = True
except:
    pass


autoStartTimer = None
screenwidth = getDesktop(0).size()

if screenwidth.width() > 1280:
    skin_directory = '/usr/lib/enigma2/python/Plugins/Extensions/JediMakerXtream/skin/fhd/'

else:
    skin_directory = '/usr/lib/enigma2/python/Plugins/Extensions/JediMakerXtream/skin/hd/'

folders = os.listdir(skin_directory)

for folder in folders:
    skinlist = folder

config.plugins.JediMakerXtream = ConfigSubsection()

cfg = config.plugins.JediMakerXtream
cfg.extensions = ConfigYesNo(default=False)
cfg.location = ConfigDirectory(default='/etc/enigma2/jediplaylists/')
cfg.m3ulocation = ConfigDirectory(default='/etc/enigma2/jediplaylists/')
cfg.main = ConfigYesNo(default=True)
cfg.unique = ConfigNumber()
cfg.usershow = ConfigSelection(default='domain', choices=[('domain', _('Domain')), ('domainconn', _('Domain | Connections'))])
cfg.enabled = ConfigYesNo(default=False)
cfg.wakeup = ConfigClock(default=((7 * 60) + 9) * 60)  # 7:00
cfg.skin = ConfigSelection(default='default', choices=folders)
cfg.bouquet_id = ConfigNumber()
cfg.timeout = ConfigNumber(default=3)
cfg.catchup = ConfigYesNo(default=False)
cfg.catchupprefix = ConfigSelection(default='~', choices=[('~', '~'), ('!', '!'), ('#', '#'), ('-', '-'), ('<', '<'), ('^', '^')])
cfg.groups = ConfigYesNo(default=False)

skin_path = skin_directory + cfg.skin.value + '/'
playlist_path = cfg.location.text + 'playlists.txt'

playlist_file = '/etc/enigma2/jediplaylists/playlist_all.json'
rytec_file = '/etc/enigma2/jediplaylists/rytec.channels.xml.xz'
rytec_url = 'http://www.xmltvepg.nl/rytec.channels.xml.xz'
alias_file = '/etc/enigma2/jediplaylists/alias.txt'
sat28_file = '/etc/enigma2/jediplaylists/28.2e.txt'


hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
       'Accept-Encoding': 'deflate'}


if not os.path.exists('/etc/enigma2/jediplaylists/'):
    os.makedirs('/etc/enigma2/jediplaylists/')

if not os.path.isfile(playlist_path):
    open(playlist_path, 'a').close()

if os.path.isdir('/usr/lib/enigma2/python/Plugins/Extensions/EPGImport'):
    jglob.has_epg_importer = True
    if not os.path.exists('/etc/epgimport'):
        os.makedirs('/etc/epgimport')
else:
    jglob.has_epg_importer = False
    jglob.epg_provider = False


def add_skin_font():
    fontpath = '/usr/lib/enigma2/python/Plugins/Extensions/JediMakerXtream/fonts/'
    addFont(fontpath + 'SourceSansPro-Regular.ttf', 'jediregular', 100, 0)
    addFont(fontpath + 'slyk-regular.ttf', 'slykregular', 100, 0)
    addFont(fontpath + 'slyk-medium.ttf', 'slykbold', 100, 0)
    addFont(fontpath + 'MavenPro-Regular.ttf', 'onyxregular', 100, 0)
    addFont(fontpath + 'MavenPro-Medium.ttf', 'onyxbold', 100, 0)
    addFont(fontpath + 'VSkin-Light.ttf', 'vskinregular', 100, 0)


def main(session, **kwargs):
    from . import menu
    session.open(menu.JediMakerXtream_Menu)
    return


def mainmenu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('Jedi Maker Xtream'), main, 'JediMakerXtream', 4)]
    else:
        return []


def extensionsmenu(session, **kwargs):
    from . import playlists
    session.open(playlists.JediMakerXtream_Playlist)


class AutoStartTimer:
    def __init__(self, session):
        self.session = session
        self.timer = eTimer()
        try:  # DreamOS fix
            self.timer_conn = self.timer.timeout.connect(self.onTimer)
        except:
            self.timer.callback.append(self.onTimer)
        self.update()

    def getWakeTime(self):
        import time
        if cfg.enabled.value:
            clock = cfg.wakeup.value
            nowt = time.time()
            now = time.localtime(nowt)
            return int(time.mktime((now.tm_year, now.tm_mon, now.tm_mday, clock[0], clock[1], 0, now.tm_wday, now.tm_yday, now.tm_isdst)))
        else:
            return -1

    def update(self, atLeast=0):
        import time
        self.timer.stop()
        wake = self.getWakeTime()
        nowtime = time.time()
        if wake > 0:
            if wake < nowtime + atLeast:
                # Tomorrow.
                wake += 24 * 3600
            next = wake - int(nowtime)
            if next > 3600:
                next = 3600
            if next <= 0:
                next = 60
            self.timer.startLongTimer(next)
        else:
            wake = -1
        return wake

    def onTimer(self):
        import time
        self.timer.stop()
        now = int(time.time())
        wake = self.getWakeTime()
        atLeast = 0
        if abs(wake - now) < 60:
            self.runUpdate()
            atLeast = 60
        self.update(atLeast)

    def runUpdate(self):
        print('\n *********** Updating Jedi Bouquets************ \n')
        from . import update
        self.session.open(update.JediMakerXtream_Update, 'auto')


def autostart(reason, session=None, **kwargs):

    if session is not None:
        global jediEPGSelection__init__
        jediEPGSelection__init__ = EPGSelection.__init__

        if vixEPG:
            global jediEPGSelectionGrid__init__
            jediEPGSelectionGrid__init__ = EPGSelectionGrid.__init__

            try:
                check = EPGSelectionGrid.togglePIG
                EPGSelectionGrid.__init__ = EPGSelectionVIX__init__
                EPGSelectionGrid.showJediCatchup = showJediCatchup
                EPGSelectionGrid.playOriginalChannel = playOriginalChannel
            except AttributeError:
                print("******** VIX check failed *****")
                pass
        else:
            try:
                check = EPGSelection.setPiPService
                EPGSelection.__init__ = EPGSelectionVTi__init__
            except AttributeError:
                print("******** VTI check failed *****")
                try:
                    check = EPGSelection.togglePIG
                    EPGSelection.__init__ = EPGSelectionATV__init__
                except AttributeError:
                    print("******** ATV check failed *****")
                    try:
                        check = EPGSelection.runPlugin
                        EPGSelection.__init__ = EPGSelectionPLI__init__
                    except AttributeError:
                        print("******** PLI check failed *****")
                        EPGSelection.__init__ = EPGSelection__init__

            EPGSelection.showJediCatchup = showJediCatchup
            EPGSelection.playOriginalChannel = playOriginalChannel

    global autoStartTimer
    if reason == 0:
        if session is not None:
            if autoStartTimer is None:
                autoStartTimer = AutoStartTimer(session)
    return


def EPGSelection__init__(self, session, service, zapFunc=None, eventid=None, bouquetChangeCB=None, serviceChangeCB=None):
    print("**** EPGSelection ****")
    jediEPGSelection__init__(self, session, service, zapFunc, eventid, bouquetChangeCB, serviceChangeCB)
    self['jediCatchupAction'] = HelpableActionMap(self, "JediCatchupActions", {
        'catchup': self.showJediCatchup,
    })


def EPGSelectionVTi__init__(self, session, service, zapFunc=None, eventid=None, bouquetChangeCB=None, serviceChangeCB=None, isEPGBar=None, switchBouquet=None, EPGNumberZap=None, togglePiP=None):
    print("**** EPGSelectionVTi ****")
    jediEPGSelection__init__(self, session, service, zapFunc, eventid, bouquetChangeCB, serviceChangeCB, isEPGBar, switchBouquet, EPGNumberZap, togglePiP)
    self['jediCatchupAction'] = HelpableActionMap(self, "JediCatchupActions", {
        'catchup': self.showJediCatchup,
    })


def EPGSelectionATV__init__(self, session, service=None, zapFunc=None, eventid=None, bouquetChangeCB=None, serviceChangeCB=None, EPGtype=None, StartBouquet=None, StartRef=None, bouquets=None):
    print("**** EPGSelectionATV ****")
    jediEPGSelection__init__(self, session, service, zapFunc, eventid, bouquetChangeCB, serviceChangeCB, EPGtype, StartBouquet, StartRef, bouquets)
    if EPGtype != "vertical":
        self['jediCatchupAction'] = HelpableActionMap(self, "JediCatchupActions", {
            'catchup': self.showJediCatchup,
        })


def EPGSelectionVIX__init__(self, session, zapFunc, startBouquet, startRef, bouquets, timeFocus=None, isInfobar=False):
    print("**** EPGSelectionVIX ****")
    jediEPGSelectionGrid__init__(self, session, zapFunc, startBouquet, startRef, bouquets, timeFocus, isInfobar)
    self['jediCatchupAction'] = HelpableActionMap(self, "JediCatchupActions", {
        'catchup': self.showJediCatchup,
    })


def EPGSelectionPLI__init__(self, session, service=None, zapFunc=None, eventid=None, bouquetChangeCB=None, serviceChangeCB=None, parent=None):
    print("**** EPGSelectionPLI ****")
    jediEPGSelection__init__(self, session, service, zapFunc, eventid, bouquetChangeCB, serviceChangeCB, parent)
    self['jediCatchupAction'] = HelpableActionMap(self, "JediCatchupActions", {
        'catchup': self.showJediCatchup,
    })


def showJediCatchup(self):

    error_message = ""
    hascatchup = False

    self.oldref = self.session.nav.getCurrentlyPlayingServiceReference()
    self.oldrefstring = self.oldref.toString()

    listcurrent = self['list'].getCurrent()
    service_ref = listcurrent[1]

    current_service = service_ref.ref.toString()

    if self.oldrefstring != current_service:
        self.session.nav.playService(eServiceReference(current_service))
    service = self.session.nav.getCurrentService()

    jglob.currentref = self.session.nav.getCurrentlyPlayingServiceReference()
    jglob.currentrefstring = jglob.currentref.toString()
    jglob.name = ServiceReference(jglob.currentref).getServiceName()

    self.playOriginalChannel()

    if service.streamed():
        from . import catchup
        try:
            error_message, hascatchup = catchup.downloadSimpleData()
        except:
            pass

        if error_message != "":
            self.session.open(MessageBox, '%s' % error_message, MessageBox.TYPE_ERROR, timeout=5)
        elif hascatchup:
            self.session.openWithCallback(self.playOriginalChannel, catchup.JediMakerXtream_Catchup)
    else:
        self.session.open(MessageBox, _('Catchup only available on IPTV Streams.'), MessageBox.TYPE_ERROR, timeout=5)


def playOriginalChannel(self):
    if self.oldrefstring != jglob.currentrefstring:
        self.session.nav.playService(eServiceReference(self.oldrefstring))


def Plugins(**kwargs):
    add_skin_font()
    iconFile = 'icons/JediMakerXtream.png'
    if screenwidth.width() > 1280:
        iconFile = 'icons/JediMakerXtreamFHD.png'
    description = _('IPTV Bouquets Creator')
    pluginname = _('JediMakerXtream')

    main_menu = PluginDescriptor(name=pluginname, description=description, where=PluginDescriptor.WHERE_MENU, fnc=mainmenu, needsRestart=True)
    extensions_menu = PluginDescriptor(name=pluginname, description=description, where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=extensionsmenu, needsRestart=True)

    result = [PluginDescriptor(name=pluginname, description=description, where=[PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart),
              PluginDescriptor(name=pluginname, description=description, where=PluginDescriptor.WHERE_PLUGINMENU, icon=iconFile, fnc=main)]

    if cfg.main.getValue():
        result.append(main_menu)
    if cfg.extensions.getValue():
        result.append(extensions_menu)
    return result
