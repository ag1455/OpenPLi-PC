# uncompyle6 version 2.9.8
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.6 (default, Oct 26 2016, 20:32:47) 
# [GCC 4.8.4]
# Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/piconload/plugin.py
# Compiled at: 2015-11-22 23:33:21
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MenuList import MenuList
from Components.Input import Input
from Components.config import config
from Components.Label import Label
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eListboxPythonMultiContent, gFont, loadPNG, eConsoleAppContainer, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER
from Components.Sources.List import List
from os import system, listdir
from Screens.Standby import TryQuitMainloop
from Components.Button import Button
from Tools.Directories import fileExists
from twisted.web.client import downloadPage
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from skin import loadSkin
from Screens.ChannelSelection import service_types_tv, service_types_radio
from enigma import eServiceCenter, eServiceReference
from ServiceReference import ServiceReference
from Components.ActionMap import NumberActionMap, ActionMap
from Components.Sources.StaticText import StaticText
from threading import Thread
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, SCOPE_SKIN_IMAGE
from Components.Language import language
from os import environ
from Components.config import config, ConfigSelection, getConfigListEntry, ConfigSubsection, ConfigSelection, ConfigEnableDisable, ConfigYesNo, ConfigInteger, NoSave, ConfigText, ConfigDirectory
from Components.ConfigList import ConfigListScreen
from os import path as os_path
from Components.FileList import FileList
from Screens.Standby import TryQuitMainloop
from Screens.PluginBrowser import PluginBrowser
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.Language import language
from Tools.LoadPixmap import LoadPixmap
from os import environ
from Components import SelectionList
import xml.etree.cElementTree as etree
from twisted.web.client import getPage
from Tools.LoadPixmap import LoadPixmap
from enigma import eActionMap
from time import localtime, time
from os import system, path, mkdir, makedirs
from xml.dom import Node, minidom
from Screens.Console import Console
from twisted.web.client import downloadPage, getPage
from __init__ import _
from enigma import *
import gettext
import re
import os
import urllib
from . import _

SKIN_PATH = '/usr/lib/enigma2/python/Plugins/Extensions/piconload/'
loadSkin(SKIN_PATH + '/piconload_skin.xml')
piconload_version = '5.5'
piconload_plugindir = '/usr/lib/enigma2/python/Plugins/Extensions/piconload'
piconload_title = _('Piconload Menu')
sp = config.osd.language.value.split('_')
piconload_language = sp[0]
if os.path.exists('%s/locale/%s' % (piconload_plugindir, piconload_language)):
    _ = gettext.Catalog('piconload', '%s/locale' % piconload_plugindir).gettext
config.misc.picon_path = ConfigText(default='/media/usb')
if os.path.exists('%s' % config.misc.picon_path.value) is False:
    config.misc.picon_path.value = '/media/usb'
pluginversion = 'Prof'
config.plugins.shootyourscreen = ConfigSubsection()
config.plugins.shootyourscreen.enable = ConfigEnableDisable(default=False)
config.plugins.shootyourscreen.switchhelp = ConfigYesNo(default=True)
config.plugins.shootyourscreen.path = ConfigSelection(default='/media/hdd', choices=['/media/hdd',
 '/media/usb',
 '/media/hdd1',
 '/media/usb1',
 ('/tmp', '/tmp')])
config.plugins.shootyourscreen.pictureformat = ConfigSelection(default='bmp', choices=[('bmp', 'bmp'), ('-j', 'jpg'), ('-p', 'png')])
config.plugins.shootyourscreen.jpegquality = ConfigSelection(default='100', choices=['10',
 '20',
 '40',
 '60',
 '80',
 '100'])
config.plugins.shootyourscreen.picturetype = ConfigSelection(default='all', choices=[('all', 'OSD + Video'), ('-v', 'Video'), ('-o', 'OSD')])
config.plugins.shootyourscreen.picturesize = ConfigSelection(default='default', choices=[('default', _('Skin resolution')),
 ('-r 480', '480'),
 ('-r 576', '576'),
 ('-r 720', '720'),
 ('-r 1280', '1280'),
 ('-r 1920', '1920')])
config.plugins.shootyourscreen.timeout = ConfigSelection(default='3', choices=[('1', '1 sec'),
 ('3', '3 sec'),
 ('5', '5 sec'),
 ('10', '10 sec'),
 (
  'off', _('no message'))])

def getPicturePath():
    picturepath = config.plugins.shootyourscreen.path.value
    if picturepath.endswith('/'):
        picturepath = picturepath + 'screenshots'
    else:
        picturepath = picturepath + '/screenshots'
    try:
        if path.exists(picturepath) == False:
            makedirs(picturepath)
    except OSError:
        self.session.open(MessageBox, _('Sorry, your device for screenshots is not writeable.\n\nPlease choose another one.'), MessageBox.TYPE_INFO, timeout=10)

    return picturepath


def getMemory(par=1):
    try:
        memory = ''
        mm = mu = mf = 0
        for line in open('/proc/meminfo', 'r'):
            line = line.strip()
            if 'MemTotal:' in line:
                line = line.split()
                mm = int(line[1])
            if 'MemFree:' in line:
                line = line.split()
                mf = int(line[1])
                break

        mu = mm - mf
        if par & 1:
            memory += ''.join((_('mem:'),
             ' %d ' % (mm / 1024),
             _('MB'),
             ' '))
        if par & 2:
            memory += ''.join((_('used:'), ' %.2f%s' % (100.0 * mu / mm, '%'), ' '))
        if par & 4:
            memory += ''.join((_('free:'), ' %.2f%s' % (100.0 * mf / mm, '%')))
        return memory
    except Exception as e:
        print '[SetPicon] read file FAIL:', e
        return ''


def freeMemory():
    os.system('sync')
    os.system('echo 3 > /proc/sys/vm/drop_caches')


def cleanup():
    global Session
    Session = None
    freeMemory()
    return


def closed(ret=False):
    cleanup()


def startSetup(session, **kwargs):
    session.open(piconloadicon)


def autostart(reason, **kwargs):
    if kwargs.has_key('session') and reason == 0:
        session = kwargs['session']
        print _('[ShootYourScreen] start....')
        session.open(getScreenshot)


def Plugins(**kwargs):
    return [
     PluginDescriptor(name=_('Piconloader'), description=_('Piconload for USB and HDD'), where=PluginDescriptor.WHERE_PLUGINMENU, icon='Piconload.png', fnc=startSetup), PluginDescriptor(name=_('Piconloader'), description=_('Piconload for USB and HDD'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon='Piconload.png', fnc=startSetup), PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=autostart)]


class piconloadicon(Screen):

    def __init__(self, session, args=0):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_('Piconload'))
        list = []
        list.append(SimpleEntry(_('Setup Path for picon'), 'path.png'))
        list.append(SimpleEntry('---', 'qwe.png'))
        list.append(SimpleEntry(_('Selekt picon'), 'packages.png'))
        list.append(SimpleEntry(_('Delete all picon'), 'cleanup.png'))
        list.append(SimpleEntry(_('Symlink directory'), 'setup_selection.png'))
#        list.append(SimpleEntry(_('Plugin update'), 'run.png'))
        list.append(SimpleEntry(_('DownloadTransponders'), 'skin.png'))
        list.append(SimpleEntry(_('SelectOSD'), 'shoot.png'))
        self['menu'] = ExtrasList(list)
        self['statusbar'] = Label('Piconload.ru ,%s' % getMemory(7))
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.go,'back': self.close
           }, -1)

    def setWindowTitle(self):
        self.setTitle(_('piconload'))

    def selectKeys(self):
        self.clearSelectedKeys()
        self.selectKey('UP')
        self.selectKey('DOWN')

    def go(self):
        index = self['menu'].getSelectedIndex()
        if index == 0:
            self.session.open(SetpiconPath)
        elif index == 2:
            self.session.open(Allpicon)
        elif index == 3:
            self.session.open(delpicon)
        elif index == 4:
            self.session.open(picSymlink)
        elif index == 5:
            self.session.open(pluginupgrade)
        elif index == 6:
            self.session.open(skinSetup)
        elif index == 7:
            self.session.open(ShootYourScreenConfig)


class piconinfo(Screen):

    def __init__(self, session, args=0):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle = _('My piconLoad history')
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'ok': self.close,'cancel': self.close,
           'up': self['text'].pageUp,
           'down': self['text'].pageDown,
           'left': self['text'].pageUp,
           'right': self['text'].pageDown
           }, -1)
        try:
            fp = open('/etc/enigma2/piconload')
            count = 0
            self.labeltext = ' '
            while 1:
                s = fp.readline()
                count += 1
                self.labeltext += str(s)
                if not s:
                    break

            fp.close()
            self['text'].setText(self.labeltext)
        except:
            self['text'].setText(_('Error, can not read piconload.txt\n or picon not download'))

    def cancel(self):
        self.close()


class Allpicon(Screen):

    def __init__(self, session, args=0):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_('Selekt picon'))
        list = []
        list.append(SimpleEntry2(_('Picon White'), 'white.png'))
        list.append(SimpleEntry2(_('Picon Black'), 'black.png'))
        list.append(SimpleEntry2(_('Picon Transparent'), 'transparent.png'))
        list.append(SimpleEntry2(_('Picon Freezeframe'), 'freezeframe.png'))
        self['menu'] = ExtrasList2(list)
        self['actions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'SetupActions',
         'EPGSelectActions'], {'ok': self.go,'back': self.close,
           'info': self.infoKey
           }, -1)

    def setWindowTitle(self):
        self.setTitle(_('piconload'))

    def infoKey(self):
        self.session.open(piconinfo)

    def selectKeys(self):
        self.clearSelectedKeys()
        self.selectKey('UP')
        self.selectKey('DOWN')

    def go(self):
        index = self['menu'].getSelectedIndex()
        if index == 0:
            self.session.open(whitepic)
        elif index == 1:
            self.session.open(blackpic)
        elif index == 2:
            self.session.open(transparentpic)
        elif index == 3:
            self.session.open(freezeframepic)


class picSymlink(Screen):

    def __init__(self, session, args=0):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_('Symlink directory'))
        list = []
        list.append(SimpleEntry(_('Symlink on USB'), 'usbstick.png'))
        list.append(SimpleEntry(_('Symlink on HDD'), 'harddisk.png'))
        list.append(SimpleEntry(_('Symlink picon_freezeframe on USB'), 'usbstick.png'))
        list.append(SimpleEntry(_('Symlink picon_freezeframe on HDD'), 'harddisk.png'))
        self['menu'] = ExtrasList(list)
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.go,'back': self.close
           }, -1)

    def setWindowTitle(self):
        self.setTitle(_('piconload'))

    def selectKeys(self):
        self.clearSelectedKeys()
        self.selectKey('UP')
        self.selectKey('DOWN')

    def go(self):
        index = self['menu'].getSelectedIndex()
        if index == 0:
            self.linkusb()
        if index == 1:
            self.linkhdd()
        if index == 2:
            self.linkfreezeframeusb()
        if index == 3:
            self.linkfreezeframehdd()

    def linkusb(self):
        os.system('ln -sf /media/usb/picon /usr/share/enigma2/picon')
        os.system('ln -sf /media/usb/piconProv /usr/share/enigma2/piconProv')
        os.system('ln -sf /media/usb/piconSat /usr/share/enigma2/piconSat')
        self.mbox = self.session.open(MessageBox, _('Simlink created on the USB storage media'), MessageBox.TYPE_INFO, timeout=5)

    def linkhdd(self):
        os.system('ln -sf /media/hdd/picon /usr/share/enigma2/picon')
        os.system('ln -sf /media/hdd/piconProv /usr/share/enigma2/piconProv')
        os.system('ln -sf /media/hdd/piconSat /usr/share/enigma2/piconSat')
        self.mbox = self.session.open(MessageBox, _('Simlink created on the HDD storage media'), MessageBox.TYPE_INFO, timeout=5)

    def linkfreezeframeusb(self):
        os.system('ln -sf /media/usb/picon_freezeframe /usr/share/enigma2/picon_freezeframe')
        self.mbox = self.session.open(MessageBox, _('Simlink created on the USB storage media'), MessageBox.TYPE_INFO, timeout=5)

    def linkfreezeframehdd(self):
        os.system('ln -sf /media/hdd/picon_freezeframe /usr/share/enigma2/picon_freezeframe')
        self.mbox = self.session.open(MessageBox, _('Simlink created on the HDD storage media'), MessageBox.TYPE_INFO, timeout=5)


class whitepic(Screen):

    def __init__(self, session, args=0):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_('Download white picon reference'))
        self['key_blue'] = Label(_('PiconInfo'))
        self['key_green'] = Label(_('Restart GUI'))
        list = []
        list.append(SimpleEntry(_('PiconSat'), 'piconSat.png'))
        list.append(SimpleEntry(_('PiconProv'), 'piconProv.png'))
        list.append(SimpleEntry(_('Iptv PiconProv'), 'piconProv.png'))
        list.append(SimpleEntry(_('PiconCam'), 'cam_sys.png'))
        list.append(SimpleEntry('---', 'qwe.png'))
        list.append(SimpleEntry(_('Amos 3/7 '), '4.0w-Piconload.png'))
        list.append(SimpleEntry(_('Thor 5/6/7 &amp; Intelsat 10-02'), '0.8w-Piconload.png'))
        list.append(SimpleEntry(_('Eutelsat 3B &amp; Rascom QAF 1R'), '3.0e-Piconload.png'))
        list.append(SimpleEntry(_('4.8E Astra 4A &amp; SES 5'), '4.8e-Piconload.png'))
        list.append(SimpleEntry(_('Eutelsat 9B &amp; Ka-Sat 9A'), '9.0e-Piconload.png'))
        list.append(SimpleEntry(_('Hotbird 13B/13C/13E'), '13.0e-Piconload.png'))
        list.append(SimpleEntry(_('Eutelsat 16A'), '16.0e-Piconload.png'))
        list.append(SimpleEntry(_('Astra 1KR/1L/1M/1N'), '19.2e-Piconload.png'))
        list.append(SimpleEntry(_('Astra 3B'), '23.5e-Piconload.png'))
        list.append(SimpleEntry(_('Astra 2E/2F/2G'), '28.2e-Piconload.png'))
        list.append(SimpleEntry(_('Eutelsat 36B &amp; Express AMU1'), '36.0e-Piconload.png'))
        list.append(SimpleEntry(_('Express AM7'), '40.0e-Piconload.png'))
        list.append(SimpleEntry(_('Turksat 3A/4A'), '42.0e-Piconload.png'))
        list.append(SimpleEntry(_('TurkmenAlem/MonacoSat'), '52.0e-Piconload.png'))
        list.append(SimpleEntry(_('Express AM6'), '53.0e-Piconload.png'))
        list.append(SimpleEntry(_('Intelsat 33e'), '60.0e-Piconload.png'))
        list.append(SimpleEntry(_('ABS 2/2A'), '75.0e-Piconload.png'))
        list.append(SimpleEntry(_('Intelsat 15'), '85.1e-Piconload.png'))
        list.append(SimpleEntry(_('Yamal 201/300K'), '90.0e-Piconload.png'))
        list.append(SimpleEntry(_('DVB-T.Lattelecom.LV'), 'dvb-t.png'))
        list.append(SimpleEntry(_('Shura.Iptv'), 'shura.png'))
        self['menu'] = ExtrasList(list)
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.go,'back': self.close,
           'blue': self.mygo,
           'green': self.keygreen
           }, -1)

    def setWindowTitle(self):
        self.setTitle(_('piconload'))

    def selectKeys(self):
        self.clearSelectedKeys()
        self.selectKey('UP')
        self.selectKey('DOWN')

    def keygreen(self):
        self.session.openWithCallback(self.restart, MessageBox, _('Really reboot now?'), MessageBox.TYPE_YESNO, timeout=7)

    def restart(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)

    def mygo(self):
        self.session.open(whitedescription)

    def go(self):
        index = self['menu'].getSelectedIndex()
        if index == 0:
            self.session.open(Console2, _('PiconSat'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/piconSat.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 1:
            self.session.open(Console2, _('PiconProv'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/piconProv.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 2:
            self.session.open(Console2, _('Iptv PiconProv'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/iptvProv.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 3:
            self.session.open(Console2, _('PiconCam'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/piconCam.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 5:
            self.session.open(Console2, _('Amos 3/7'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/4.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 6:
            self.session.open(Console2, _('Thor 5/6/7 &amp; Intelsat 10-02'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/0.8W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 7:
            self.session.open(Console2, _('Eutelsat 3B &amp; Rascom QAF 1R 3.0E'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/3.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 8:
            self.session.open(Console2, _('4.8E Astra 4A &amp; SES 5'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/4.8E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 9:
            self.session.open(Console2, _('Eutelsat 9B &amp; Ka-Sat 9A'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/9.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 10:
            self.session.open(Console2, _('Hotbird 13B/13C/13E'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/13.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 11:
            self.session.open(Console2, _('Eutelsat 16A'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/16.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 12:
            self.session.open(Console2, _('Astra 1KR/1L/1M/1N'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/19.2E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 13:
            self.session.open(Console2, _('Astra 3B'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/23.5E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 14:
            self.session.open(Console2, _('Eurobird 1 & Astra 2A/2B/2D'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/28.2E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 15:
            self.session.open(Console2, _('Eutelsat 36B &amp; Express AMU1'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/36.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 16:
            self.session.open(Console2, _('Express AM7'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/40.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 17:
            self.session.open(Console2, _('Turksat 3A/4A'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/42.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 18:
            self.session.open(Console2, _('TurkmenAlem/MonacoSat'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/52.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 19:
            self.session.open(Console2, _('Express AM6'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/53.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 20:
            self.session.open(Console2, _('Intelsat 33e'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/60.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 21:
            self.session.open(Console2, _('ABS 2/2A'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/75.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 20:
            self.session.open(Console2, _('Intelsat 15'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/85.1E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 22:
            self.session.open(Console2, _('Yamal 201/300K'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/90.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 23:
            self.session.open(Console2, _('DVB-T.Lattelecom.LV'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/DVB-T.lv.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 24:
            self.session.open(Console2, _('Shura.Iptv'), cmdlist=['/usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/local/e2/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/white/Shura.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)


class whitedescription(Screen):

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        self.setTitle(_('Update description'))
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'ok': self.close,'cancel': self.close,
           'up': self['text'].pageUp,
           'down': self['text'].pageDown,
           'left': self['text'].pageUp,
           'right': self['text'].pageDown
           }, -1)
        try:
            fp = urllib.urlopen('http://piconload.ru/upload/picons/white/dateinfo.txt')
            count = 0
            self.labeltext = ''
            while 1:
                s = fp.readline()
                count += 1
                self.labeltext += str(s)
                if not s:
                    break

            fp.close()
            self['text'].setText(self.labeltext)
        except:
            self['text'].setText('Error in downloading INFO.text')


class blackpic(Screen):

    def __init__(self, session, args=0):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_('Download  picon Black reference'))
        self['key_blue'] = Label(_('PiconInfo'))
        self['key_green'] = Label(_('Restart GUI'))
        list = []
        list.append(SimpleEntry(_('PiconSat'), 'piconSat.png'))
        list.append(SimpleEntry(_('PiconProv'), 'piconProv.png'))
        list.append(SimpleEntry(_('PiconCam'), 'cam_sys.png'))
        list.append(SimpleEntry('---', 'qwe.png'))
        list.append(SimpleEntry(_('Amos 3/7 '), '4.0w-Piconload.png'))
        list.append(SimpleEntry(_('Thor 5/6/7 &amp; Intelsat 10-02'), '0.8w-Piconload.png'))
        list.append(SimpleEntry(_('Eutelsat 3B &amp; Rascom QAF 1R'), '3.0e-Piconload.png'))
        list.append(SimpleEntry(_('4.8E Astra 4A &amp; SES 5'), '4.8e-Piconload.png'))
        list.append(SimpleEntry(_('Eutelsat 7A'), '7.0e-Piconload.png'))
        list.append(SimpleEntry(_('Eutelsat 9B &amp; Ka-Sat 9A'), '9.0e-Piconload.png'))
        list.append(SimpleEntry(_('Eutelsat 10A'), '10.0e-Piconload.png'))
        list.append(SimpleEntry(_('Hotbird 13B/13C/13E'), '13.0e-Piconload.png'))
        list.append(SimpleEntry(_('Eutelsat 16A'), '16.0e-Piconload.png'))
        list.append(SimpleEntry(_('Astra 1KR/1L/1M/1N'), '19.2e-Piconload.png'))
        list.append(SimpleEntry(_('Astra 3B'), '23.5e-Piconload.png'))
        list.append(SimpleEntry(_('Astra 2E/2F/2G'), '28.2e-Piconload.png'))
        list.append(SimpleEntry(_('Astra 1G'), '31.5e-Piconload.png'))
        list.append(SimpleEntry(_('Eutelsat 36B &amp; Express AMU1'), '36.0e-Piconload.png'))
        list.append(SimpleEntry(_('Express AM7'), '40.0e-Piconload.png'))
        list.append(SimpleEntry(_('Turksat 3A/4A'), '42.0e-Piconload.png'))
        list.append(SimpleEntry(_('TurkmenAlem/MonacoSat'), '52.0e-Piconload.png'))
        list.append(SimpleEntry(_('Express AM6'), '53.0e-Piconload.png'))
        list.append(SimpleEntry(_('Intelsat 33e'), '60.0e-Piconload.png'))
        list.append(SimpleEntry(_('ABS 2/2A'), '75.0e-Piconload.png'))
        list.append(SimpleEntry(_('Intelsat 15'), '85.1e-Piconload.png'))
        list.append(SimpleEntry(_('Yamal 201/300K'), '90.0e-Piconload.png'))
        list.append(SimpleEntry(_('Shura.Iptv'), 'shura.png'))
        self['menu'] = ExtrasList(list)
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.go,'back': self.close,
           'blue': self.mygo,
           'green': self.keygreen
           }, -1)

    def setWindowTitle(self):
        self.setTitle(_('piconload'))

    def selectKeys(self):
        self.clearSelectedKeys()
        self.selectKey('UP')
        self.selectKey('DOWN')

    def keygreen(self):
        self.session.openWithCallback(self.restart, MessageBox, _('Really reboot now?'), MessageBox.TYPE_YESNO, timeout=7)

    def restart(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)

    def mygo(self):
        self.session.open(blackdescription)

    def go(self):
        index = self['menu'].getSelectedIndex()
        if index == 0:
            self.session.open(Console2, _('PiconSat'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/piconSat.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 1:
            self.session.open(Console2, _('PiconProv'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/piconProv.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 2:
            self.session.open(Console2, _('PiconCam'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/piconCam.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 4:
            self.session.open(Console2, _('Amos 3/7'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/4.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 5:
            self.session.open(Console2, _('Thor 5/6/7 &amp; Intelsat 10-02'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/0.8W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 6:
            self.session.open(Console2, _('Eutelsat 3B &amp; Rascom QAF 1R 3.0E'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/3.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 7:
            self.session.open(Console2, _('4.8E Astra 4A &amp; SES 5'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/4.8E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 8:
            self.session.open(Console2, _('Eutelsat 7A '), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/7.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 9:
            self.session.open(Console2, _('Eutelsat 9B &amp; Ka-Sat 9A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/9.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 10:
            self.session.open(Console2, _('Eutelsat 10A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/10.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 11:
            self.session.open(Console2, _('Hotbird 13B/13C/13E'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/13.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 12:
            self.session.open(Console2, _('Eutelsat 16A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/16.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 13:
            self.session.open(Console2, _('Astra 1KR/1L/1M/1N'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/19.2E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 14:
            self.session.open(Console2, _('Astra 3B'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/23.5E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 15:
            self.session.open(Console2, _('Eurobird 1 & Astra 2A/2B/2D'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/28.2E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 16:
            self.session.open(Console2, _('Astra 1G '), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/31.5E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 17:
            self.session.open(Console2, _('Eutelsat 36B &amp; Express AMU1'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/36.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 18:
            self.session.open(Console2, _('Express AM7'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/40.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 19:
            self.session.open(Console2, _('Turksat 3A/4A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/42.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 20:
            self.session.open(Console2, _('TurkmenAlem/MonacoSat'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/52.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 21:
            self.session.open(Console2, _('Express AM6'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/53.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 22:
            self.session.open(Console2, _('Intelsat 33e'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/60.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 23:
            self.session.open(Console2, _('ABS 2/2A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/75.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 24:
            self.session.open(Console2, _('Intelsat 15'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/85.1E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 25:
            self.session.open(Console2, _('Yamal 201/300K'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/90.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 26:
            self.session.open(Console2, _('Shura.Iptv'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/Shura.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)


class blackdescription(Screen):

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        self.setTitle(_('Update description'))
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'ok': self.close,'cancel': self.close,
           'up': self['text'].pageUp,
           'down': self['text'].pageDown,
           'left': self['text'].pageUp,
           'right': self['text'].pageDown
           }, -1)
        try:
            fp = urllib.urlopen('http://piconload.ru/upload/picons/black/dateinfo.txt')
            count = 0
            self.labeltext = ''
            while 1:
                s = fp.readline()
                count += 1
                self.labeltext += str(s)
                if not s:
                    break

            fp.close()
            self['text'].setText(self.labeltext)
        except:
            self['text'].setText(_('Error in downloading INFO.text'))


class transparentpic(Screen):

    def __init__(self, session, args=0):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_('Download picon Transparent reference'))
        self['key_blue'] = Label(_('PiconInfo'))
        self['key_green'] = Label(_('Restart GUI'))
        list = []
        list.append(SimpleEntry(_('PiconSat'), 'piconSat.png'))
        list.append(SimpleEntry(_('PiconProv'), 'piconProv.png'))
        list.append(SimpleEntry('---', 'qwe.png'))
        list.append(SimpleEntry(_('Amos 3/7'), '4.0w-Piconload.png'))
        list.append(SimpleEntry(_('Thor 5/6/7 &amp; Intelsat 10-02'), '0.8w-Piconload.png'))
        list.append(SimpleEntry(_('Eutelsat 3B &amp; Rascom QAF 1R'), '3.0e-Piconload.png'))
        list.append(SimpleEntry(_('4.8E Astra 4A &amp; SES 5'), '4.8e-Piconload.png'))
        list.append(SimpleEntry(_('Eurobird 9A '), '9.0e-Piconload.png'))
        list.append(SimpleEntry(_('Hotbird 13B/13C/13E'), '13.0e-Piconload.png'))
        list.append(SimpleEntry(_('Eutelsat 16A'), '16.0e-Piconload.png'))
        list.append(SimpleEntry(_('Astra 1KR/1L/1M/1N'), '19.2e-Piconload.png'))
        list.append(SimpleEntry(_('Astra 3B'), '23.5e-Piconload.png'))
        list.append(SimpleEntry(_('Astra 2E/2F/2G'), '28.2e-Piconload.png'))
        list.append(SimpleEntry(_('Eutelsat 36B &amp; Express AMU1'), '36.0e-Piconload.png'))
        list.append(SimpleEntry(_('Express AM7'), '40.0e-Piconload.png'))
        list.append(SimpleEntry(_('Turksat 3A/4A'), '42.0e-Piconload.png'))
        list.append(SimpleEntry(_('TurkmenAlem/MonacoSat'), '52.0e-Piconload.png'))
        list.append(SimpleEntry(_('Express AM6'), '53.0e-Piconload.png'))
        list.append(SimpleEntry(_('Bonum 1'), '56.0e-Piconload.png'))
        list.append(SimpleEntry(_('Intelsat 33e'), '60.0e-Piconload.png'))
        list.append(SimpleEntry(_('ABS 2/2A'), '75.0e-Piconload.png'))
        list.append(SimpleEntry(_('Intelsat 15'), '85.2e-Piconload.png'))
        list.append(SimpleEntry(_('Yamal 201/300K'), '90.0e-Piconload.png'))
        list.append(SimpleEntry(_('Shura.Iptv'), 'shura.png'))
        self['menu'] = ExtrasList(list)
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.go,'back': self.close,
           'blue': self.mygo,
           'green': self.keygreen
           }, -1)

    def setWindowTitle(self):
        self.setTitle(_('piconload'))

    def selectKeys(self):
        self.clearSelectedKeys()
        self.selectKey('UP')
        self.selectKey('DOWN')

    def keygreen(self):
        self.session.openWithCallback(self.restart, MessageBox, _('Really reboot now?'), MessageBox.TYPE_YESNO, timeout=7)

    def restart(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)

    def mygo(self):
        self.session.open(transparentdescription)

    def go(self):
        index = self['menu'].getSelectedIndex()
        if index == 0:
            self.session.open(Console2, _('PiconSat'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/piconSat.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 1:
            self.session.open(Console2, _('PiconProv'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/piconProv.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 3:
            self.session.open(Console2, _('Amos 3/7'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/4.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 4:
            self.session.open(Console2, _('Thor 5/6/7 &amp; Intelsat 10-02'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/0.8W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 5:
            self.session.open(Console2, _('Eutelsat 3B &amp; Rascom QAF 1R 3.0E'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/3.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 6:
            self.session.open(Console2, _('Astra 4A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/4.8E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 7:
            self.session.open(Console2, _('Eurobird 9A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/9.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 8:
            self.session.open(Console2, _('Hotbird 13B/13C/13E'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/13.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 9:
            self.session.open(Console2, _('Eutelsat 16A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/16.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 10:
            self.session.open(Console2, _('Astra 1KR/1L/1M/1N'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/19.2E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 11:
            self.session.open(Console2, _('Astra 3B'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/23.5E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 12:
            self.session.open(Console2, _('Eurobird 1 & Astra 2A/2B/2D'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/28.2E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 13:
            self.session.open(Console2, _('Eutelsat 36B &amp; Express AMU1'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/36.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 14:
            self.session.open(Console2, _('Express AM7'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/40.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 15:
            self.session.open(Console2, _('Turksat 3A/4A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/42.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 16:
            self.session.open(Console2, _('TurkmenAlem/MonacoSat'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/52.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 17:
            self.session.open(Console2, _('Express AM6'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/black/53.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 18:
            self.session.open(Console2, _('Bonum 1'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/56.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 19:
            self.session.open(Console2, _('Intelsat 33e'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/60.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 20:
            self.session.open(Console2, _('ABS 2/2A '), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/75.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 21:
            self.session.open(Console2, _('Intelsat 15'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/85.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 22:
            self.session.open(Console2, _('Yamal 201/300K'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/90.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 23:
            self.session.open(Console2, _('Shura.Iptv'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/transparent/Shura.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)


class transparentdescription(Screen):

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        self.setTitle(_('Update description'))
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'ok': self.close,'cancel': self.close,
           'up': self['text'].pageUp,
           'down': self['text'].pageDown,
           'left': self['text'].pageUp,
           'right': self['text'].pageDown
           }, -1)
        try:
            fp = urllib.urlopen('http://piconload.ru/upload/picons/transparent/dateinfo.txt')
            count = 0
            self.labeltext = ''
            while 1:
                s = fp.readline()
                count += 1
                self.labeltext += str(s)
                if not s:
                    break

            fp.close()
            self['text'].setText(self.labeltext)
        except:
            self['text'].setText('Error in downloading INFO.text')

# FREEZEFRAME
class freezeframepic(Screen):

    def __init__(self, session, args=0):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_('Download Picon Freezeframe picon reference'))
        self['key_blue'] = Label(_('PiconInfo'))
        self['key_green'] = Label(_('Restart GUI'))
        list = []
        list.append(SimpleEntry(_('45.0W Intelsat 14'), '45.0w-Piconload.png'))
        list.append(SimpleEntry(_('30.0W Hispasat 30W-4/30W-5'), '30.0w-Piconload.png'))
        list.append(SimpleEntry(_('27.5W Intelsat 907'), '27.5w-Piconload.png'))
        list.append(SimpleEntry(_('24.8W'), '24.8w-Piconload.png'))
        list.append(SimpleEntry(_('22.0W SES 4'), '22.0w-Piconload.png'))
        list.append(SimpleEntry(_('20.0W NSS 7'), '20.0w-Piconload.png'))
        list.append(SimpleEntry(_('15.0W Telstar 12 Vantage'), '15.0w-Piconload.png'))
        list.append(SimpleEntry(_('14.OW Express AM8'), '14.0w-Piconload.png'))
        list.append(SimpleEntry(_('12.5W Eutelsat 12 West B &amp; WGS 3'), '12.5w-Piconload.png'))
        list.append(SimpleEntry(_('11.0W Express AM44'), '11.0w-Piconload.png'))
        list.append(SimpleEntry(_('8.0W Eutelsat 8 West B'), '8.0w-Piconload.png'))
        list.append(SimpleEntry(_('7.0W Nilesat 201 &amp; Eutelsat 7 West A'), '7.0w-Piconload.png'))
        list.append(SimpleEntry(_('5.0W Eutelsat 5 West A'), '5.0w-Piconload.png'))
        list.append(SimpleEntry(_('4.0W Amos 3/7'), '4.0w-Piconload.png'))
        list.append(SimpleEntry(_('3.0W ABS 3A'), '3.0w-Piconload.png'))
        list.append(SimpleEntry(_('0.8W Thor 5/6/7 &amp; Intelsat 10-02'), '0.8w-Piconload.png'))
        list.append(SimpleEntry(_('1.9E BulgariaSat 1'), '1.9e-Piconload.png'))
        list.append(SimpleEntry(_('3.0E Eutelsat 3B &amp; Rascom QAF 1R'), '3.0e-Piconload.png'))
        list.append(SimpleEntry(_('4.8E Astra 4A &amp; SES 5'), '4.8e-Piconload.png'))
        list.append(SimpleEntry(_('7.0E Eutelsat 7A/7B'), '7.0e-Piconload.png'))
        list.append(SimpleEntry(_('9.0E Eutelsat 9B &amp; Ka-Sat 9A'), '9.0e-Piconload.png'))
        list.append(SimpleEntry(_('10.0E Eutelsat 10A'), '10.0e-Piconload.png'))
        list.append(SimpleEntry(_('13.0E Hotbird 13B/13C/13E'), '13.0e-Piconload.png'))
        list.append(SimpleEntry(_('16.0E Eutelsat 16A'), '16.0e-Piconload.png'))
        list.append(SimpleEntry(_('19.2E Astra 1KR/1L/1M/1N'), '19.2e-Piconload.png'))
        list.append(SimpleEntry(_('21.6E Eutelsat 21B'), '21.6e-Piconload.png'))
        list.append(SimpleEntry(_('23.5E Astra 3B'), '23.5e-Piconload.png'))
        list.append(SimpleEntry(_('26.0E Badr 4/5/6/7 &amp; Eshail 1/2'), '26.0e-Piconload.png'))
        list.append(SimpleEntry(_('28.2E Astra 2E/2F/2G'), '28.2e-Piconload.png'))
        list.append(SimpleEntry(_('31.5E Astra 5B'), '31.5e-Piconload.png'))
        list.append(SimpleEntry(_('33.0E Eutelsat 33E &amp; Intelsat 28'), '33.0e-Piconload.png'))
        list.append(SimpleEntry(_('36.0E Eutelsat 36B &amp; Express AMU1'), '36.0e-Piconload.png'))
        list.append(SimpleEntry(_('39.0E Hellas Sat 3'), '39.0e-Piconload.png'))
        list.append(SimpleEntry(_('42.0E Turksat 3A/4A'), '42.0e-Piconload.png'))
        list.append(SimpleEntry(_('45.0E AzerSpace 2/Intelsat 38'), '45.0e-Piconload.png'))
        list.append(SimpleEntry(_('46.0E AzerSpace 1/Africasat 1a'), '46.0e-Piconload.png'))
        list.append(SimpleEntry(_('51.5E Belintersat 1'), '51.5e-Piconload.png'))
        list.append(SimpleEntry(_('52.0E TurkmenAlem/MonacoSat'), '52.0e-Piconload.png'))
        list.append(SimpleEntry(_('53.0E Express AM6'), '53.0e-Piconload.png'))
        list.append(SimpleEntry(_('54.9E G-Sat 8/16 &amp; Yamal 402'), '54.9e-Piconload.png'))
        list.append(SimpleEntry(_('56.0E Express'), '56.0e-Piconload.png'))
        list.append(SimpleEntry(_('57.0E NSS 12'), '57.0e-Piconload.png'))
        list.append(SimpleEntry(_('60.0E Intelsat 33e'), '60.0e-Piconload.png'))
        list.append(SimpleEntry(_('62.0E Intelsat 902'), '62.0e-Piconload.png'))
        list.append(SimpleEntry(_('66.0E Intelsat 17'), '66.0e-Piconload.png'))
        list.append(SimpleEntry(_('68.5E Intelsat 20'), '68.5e-Piconload.png'))
        list.append(SimpleEntry(_('70.5E Eutelsat 70B'), '70.5e-Piconload.png'))
        list.append(SimpleEntry(_('75.0E ABS 2/2A'), '75.0e-Piconload.png'))
        list.append(SimpleEntry(_('85.0E Horizons 2 &amp; Intelsat 15'), '85.0e-Piconload.png'))
        list.append(SimpleEntry(_('90.0E Yamal 401'), '90.0e-Piconload.png'))
        self['menu'] = ExtrasList(list)
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.go,'back': self.close,
           'blue': self.mygo,
           'green': self.keygreen
           }, -1)

    def setWindowTitle(self):
        self.setTitle(_('piconload'))

    def selectKeys(self):
        self.clearSelectedKeys()
        self.selectKey('UP')
        self.selectKey('DOWN')

    def keygreen(self):
        self.session.openWithCallback(self.restart, MessageBox, _('Really reboot now?'), MessageBox.TYPE_YESNO, timeout=7)

    def restart(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)

    def mygo(self):
        self.session.open(freezeframedescription)

    def go(self):
        index = self['menu'].getSelectedIndex()
        if index == 0:
            self.session.open(Console2, _('45.0W Intelsat 14'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/45.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 1:
            self.session.open(Console2, _('30.0W Hispasat 30W-4/30W-5'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/30.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 2:
            self.session.open(Console2, _('27.5W Intelsat 907'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/27.5W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 3:
            self.session.open(Console2, _('24.8W'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/24.8W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 4:
            self.session.open(Console2, _('22.0W SES 4'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/22.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 5:
            self.session.open(Console2, _('20.0W NSS 7'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/20.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 6:
            self.session.open(Console2, _('15.0W Telstar 12 Vantage'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/15.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 7:
            self.session.open(Console2, _('14.OW Express AM8'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/14.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 8:
            self.session.open(Console2, _('12.5W Eutelsat 12 West B &amp; WGS 3'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/12.5W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 9:
            self.session.open(Console2, _('11.0W Express AM44'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/11.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 10:
            self.session.open(Console2, _('8.0W Eutelsat 8 West B'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/8.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 11:
            self.session.open(Console2, _('7.0W Nilesat 201 &amp; Eutelsat 7 West A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/7.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 12:
            self.session.open(Console2, _('5.0W Eutelsat 5 West A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/5.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 13:
            self.session.open(Console2, _('4.0W Amos 3/7'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/4.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 14:
            self.session.open(Console2, _('3.0W ABS 3A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/3.0W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 15:
            self.session.open(Console2, _('0.8W Thor 5/6/7 &amp; Intelsat 10-02'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/0.8W.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 16:
            self.session.open(Console2, _('1.9E BulgariaSat 1'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/1.9E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 17:
            self.session.open(Console2, _('3.0E Eutelsat 3B &amp; Rascom QAF 1R'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/3.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 18:
            self.session.open(Console2, _('4.8E Astra 4A &amp; SES 5'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/4.8E.piconf ' + config.misc.picon_path.value])
        elif index == 19:
            self.session.open(Console2, _('7.0E Eutelsat 7A/7B'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/7.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 20:
            self.session.open(Console2, _('9.0E Eutelsat 9B &amp; Ka-Sat 9A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/9.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 21:
            self.session.open(Console2, _('10.0E Eutelsat 10A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/10.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 22:
            self.session.open(Console2, _('13.0E Hotbird 13B/13C/13E'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/13.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 23:
            self.session.open(Console2, _('16.0E Eutelsat 16A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/16.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 24:
            self.session.open(Console2, _('19.2E Astra 1KR/1L/1M/1N'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/19.2E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 25:
            self.session.open(Console2, _('21.6E Eutelsat 21B'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/21.6E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 26:
            self.session.open(Console2, _('23.5E Astra 3B'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/23.5E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 27:
            self.session.open(Console2, _('26.0E Badr 4/5/6/7 &amp; Eshail 1/2'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/26.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 28:
            self.session.open(Console2, _('28.2E Astra 2E/2F/2G'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/28.2E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 29:
            self.session.open(Console2, _('31.5E Astra 5B'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/31.5E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 30:
            self.session.open(Console2, _('33.0E Eutelsat 33E &amp; Intelsat 28'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/33.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 31:
            self.session.open(Console2, _('36.0E Eutelsat 36B &amp; Express AMU1'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/36.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 32:
            self.session.open(Console2, _('39.0E Hellas Sat 3'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/39.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 33:
            self.session.open(Console2, _('42.0E Turksat 3A/4A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/42.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 34:
            self.session.open(Console2, _('45.0E AzerSpace 2/Intelsat 38'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/45.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 35:
            self.session.open(Console2, _('46.0E AzerSpace 1/Africasat 1a'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/46.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 36:
            self.session.open(Console2, _('51.5E Belintersat 1'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/51.5E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 37:
            self.session.open(Console2, _('52.0E TurkmenAlem/MonacoSat'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/52.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 38:
            self.session.open(Console2, _('53.0E Express AM6'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/53.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 39:
            self.session.open(Console2, _('54.9E G-Sat 8/16 &amp; Yamal 402'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/54.9E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 40:
            self.session.open(Console2, _('56.0E Intelsat 33e'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/56.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 41:
            self.session.open(Console2, _('57.0E NSS 12'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/57.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 42:
            self.session.open(Console2, _('60.0E Intelsat 33e'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/60.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 43:
            self.session.open(Console2, _('62.0E Intelsat 902'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/62.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 44:
            self.session.open(Console2, _('66.0E Intelsat 17'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/66.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 45:
            self.session.open(Console2, _('68.5E Intelsat 20'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/68.5E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 46:
            self.session.open(Console2, _('70.5E Eutelsat 70B'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/70.5E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 47:
            self.session.open(Console2, _('75.0E ABS 2/2A'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/75.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 48:
            self.session.open(Console2, _('85.0E Horizons 2 &amp; Intelsat 15'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/85.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)
        elif index == 49:
            self.session.open(Console2, _('90.0E Yamal 401'), cmdlist=['/usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/picon_install.sh /usr/lib/enigma2/python/Plugins/Extensions/piconload/script/Pic/load/freezeframe/90.0E.piconf ' + config.misc.picon_path.value], closeOnSuccess=True)


class freezeframedescription(Screen):

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        self.setTitle(_('Update description'))
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'ok': self.close,'cancel': self.close,
           'up': self['text'].pageUp,
           'down': self['text'].pageDown,
           'left': self['text'].pageUp,
           'right': self['text'].pageDown
           }, -1)
        try:
            fp = urllib.urlopen('http://piconload.ru/upload/picons/freezeframe/dateinfo.txt')
            count = 0
            self.labeltext = ''
            while 1:
                s = fp.readline()
                count += 1
                self.labeltext += str(s)
                if not s:
                    break

            fp.close()
            self['text'].setText(self.labeltext)
        except:
            self['text'].setText('Error in downloading INFO.text')


class delpicon(Screen):

    def __init__(self, session, args=0):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_('Delete all picon'))
        list = []
        list.append(SimpleEntry2(_('Sort&delette'), 'sort.png'))
        list.append(SimpleEntry2(_('Delete all picon'), 'del.png'))
        list.append(SimpleEntry2(_('Delete all Picon freezeframe'), 'del.png'))
        self['menu'] = ExtrasList2(list)
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.go,'back': self.close
           }, -1)

    def setWindowTitle(self):
        self.setTitle(_('piconload'))

    def selectKeys(self):
        self.clearSelectedKeys()
        self.selectKey('UP')
        self.selectKey('DOWN')

    def go(self):
        index = self['menu'].getSelectedIndex()
        if index == 0:
            self.session.open(SortPicons)
        if index == 1:
            self.deletusb()
        if index == 2:
            self.deletfreezeframe()

    def deletusb(self):
        os.system('rm -rf %s/picon' % config.misc.picon_path.value)
        os.system('rm -rf %s/piconProv' % config.misc.picon_path.value)
        os.system('rm -rf %s/piconSat' % config.misc.picon_path.value)
        os.system('rm -rf /etc/enigma2/piconload')
        self.mbox = self.session.open(MessageBox, _('All picon and xistori deletet'), MessageBox.TYPE_INFO, timeout=4)

    def deletfreezeframe(self):
        os.system('rm -rf %s/picon_freezeframe' % config.misc.picon_path.value)
        os.system('rm -rf /etc/enigma2/piconload')
        self.mbox = self.session.open(MessageBox, _('Picon freezeframe and xistori deletet'), MessageBox.TYPE_INFO, timeout=4)


class SortPicons(Screen):

    def __init__(self, session, args=0):
        self.session = session
        Screen.__init__(self, session)
        self['info'] = Label(_('Lese Kanalliste..'))
        self['cmd'] = Label(_('OK = Loeschen ----- EXIT = Beenden'))
        self['actions'] = ActionMap(['OkCancelActions',
         'ShortcutActions',
         'WizardActions',
         'ColorActions',
         'SetupActions',
         'NumberActions',
         'MenuActions'], {'ok': self.keyOK,'cancel': self.keyCancel
           }, -1)
        self.onLayoutFinish.append(self.getInfo)

    def getInfo(self):
        print 'info'
        kanaliste = buildChannellist()
        self.rm_list = None
        self.rm_list = []
        self.rm_list2 = None
        self.rm_list2 = []
        self.rm_list3 = None
        self.rm_list3 = []
        if fileExists('/usr/share/enigma2/picon/'):
            self['info'].setText(_('Lese Bouquets..'))
            self['info'].setText(_('Lese Picons..'))
            piconsliste = lsPicons()
            for picon in piconsliste:
                if picon not in kanaliste:
                    self.rm_list.append(picon)

        if fileExists('/media/hdd/picon/'):
            self['info'].setText(_('Lese Bouquets..'))
            self['info'].setText(_('Lese Picons..'))
            piconsliste = lshddPicons()
            for picon in piconsliste:
                if picon not in kanaliste:
                    self.rm_list2.append(picon)

        if fileExists('/media/usb/picon/'):
            self['info'].setText(_('Lese Bouquets..'))
            self['info'].setText(_('Lese Picons..'))
            piconsliste = lsusbPicons()
            for picon in piconsliste:
                if picon not in kanaliste:
                    self.rm_list3.append(picon)

        count = len(self.rm_list) + len(self.rm_list2) + len(self.rm_list3)
        self['info'].setText(_('Es wurden %s Picons gefunden die geloescht werden koennen.') % str(count))
        return

    def keyOK(self):
        if len(self.rm_list) > 0:
            for file in self.rm_list:
                file = file.replace(':', '_')
                file = file[:-1] + '.png'
                file = '/usr/share/enigma2/picon/%s' % file
                if fileExists(file):
                    os.remove(file)

            self['info'].setText(_('Picons geloescht.'))
        if len(self.rm_list2) > 0:
            for file in self.rm_list2:
                file = file.replace(':', '_')
                file = file[:-1] + '.png'
                file = '/media/hdd/picon/%s' % file
                if fileExists(file):
                    os.remove(file)

            self['info'].setText(_('HDD Picons geloescht.'))
        if len(self.rm_list3) > 0:
            for file in self.rm_list3:
                file = file.replace(':', '_')
                file = file[:-1] + '.png'
                file = '/media/usb/picon/%s' % file
                if fileExists(file):
                    os.remove(file)

            self['info'].setText(_('USB Picons geloescht.'))

    def keyCancel(self):
        self.close()


def lsPicons():
    rm_plist = None
    rm_plist = []
    if fileExists('/usr/share/enigma2/picon/'):
        for dirname, dirnames, filenames in os.walk('/usr/share/enigma2/picon/'):
            for filename in filenames:
                if filename.lower().endswith('.png'):
                    rm_plist.append(filename.replace('.png', ':').replace('_', ':'))

        return rm_plist
    else:
        return
        return


def lshddPicons():
    rm_plist = None
    rm_plist = []
    if fileExists('/media/hdd/picon/'):
        for dirname, dirnames, filenames in os.walk('/media/hdd/picon/'):
            for filename in filenames:
                if filename.lower().endswith('.png'):
                    rm_plist.append(filename.replace('.png', ':').replace('_', ':'))

        return rm_plist
    else:
        return
        return


def lsusbPicons():
    rm_plist = None
    rm_plist = []
    if fileExists('/media/usb/picon/'):
        for dirname, dirnames, filenames in os.walk('/media/usb/picon/'):
            for filename in filenames:
                if filename.lower().endswith('.png'):
                    rm_plist.append(filename.replace('.png', ':').replace('_', ':'))

        return rm_plist
    else:
        return
        return


def getServiceList(ref):
    root = eServiceReference(str(ref))
    serviceHandler = eServiceCenter.getInstance()
    return serviceHandler.list(root).getContent('SN', True)


def getRadioBouquets():
    return getServiceList(service_types_radio + ' FROM BOUQUET "bouquets.radio" ORDER BY bouquet')


def getTVBouquets():
    return getServiceList(service_types_tv + ' FROM BOUQUET "bouquets.tv" ORDER BY bouquet')


def buildChannellist():
    rm_chlist = None
    rm_chlist = []
    print _('[RemovePicons] read channellist..')
    tvbouquets = getTVBouquets()
    radiobouquets = getRadioBouquets()
    print _('[RemovePicons] found %s bouquet: %s') % (len(tvbouquets), tvbouquets)
    for bouquet in tvbouquets:
        bouquetlist = []
        bouquetlist = getServiceList(bouquet[0])
        for serviceref, servicename in bouquetlist:
            rm_chlist.append(':'.join(serviceref.split(':')[:11]))

    for bouquet in radiobouquets:
        bouquetlist = []
        bouquetlist = getServiceList(bouquet[0])
        for serviceref, servicename in bouquetlist:
            rm_chlist.append(':'.join(serviceref.split(':')[:11]))

    return rm_chlist


class helpinfo(Screen):

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        helpinfo = ''
        self.setTitle(_('helpinfo'))
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'ok': self.close,'cancel': self.close,
           'up': self['text'].pageUp,
           'down': self['text'].pageDown,
           'left': self['text'].pageUp,
           'right': self['text'].pageDown
           }, -1)
        try:
            fp = urllib.urlopen('http://piconload.ru/upload/picons/pluginupgrade/helpinfo.txt')
            count = 0
            self.labeltext = ''
            while 1:
                s = fp.readline()
                count += 1
                self.labeltext += str(s)
                if not s:
                    break

            fp.close()
            self['text'].setText(self.labeltext)
        except:
            self['text'].setText('Error in downloading INFO.text')


class Console2(Screen):

    def __init__(self, session, title='Console', cmdlist=None, finishedCallback=None, closeOnSuccess=False):
        Screen.__init__(self, session)
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self['text'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.cancel,'back': self.cancel,
           'up': self['text'].pageUp,
           'down': self['text'].pageDown
           }, -1)
        self.cmdlist = cmdlist
        self.newtitle = title
        self.onShown.append(self.updateTitle)
        self.container = eConsoleAppContainer()
        self.run = 0
        self.container.appClosed.append(self.runFinished)
        self.container.dataAvail.append(self.dataAvail)
        self.onLayoutFinish.append(self.startRun)

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        print 'Console: executing in run', self.run, ' the command:', self.cmdlist[self.run]
        if self.container.execute(self.cmdlist[self.run]):
            self.runFinished(-1)

    def runFinished(self, retval):
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]):
                self.runFinished(-1)
        else:
            str = self['text'].getText()
            str += '\n' + _(' ')
            self['text'].setText(str)
            self['text'].lastPage()
            if self.finishedCallback is not None:
                self.finishedCallback()
            if not retval and self.closeOnSuccess:
                self.cancel()
        return

    def cancel(self):
        if self.run == len(self.cmdlist):
            self.close()
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)

    def dataAvail(self, str):
        self['text'].setText(self['text'].getText() + str)


def SimpleEntry(name, picture):
    res = [
     (
      name, picture)]
    picture = '/usr/lib/enigma2/python/Plugins/Extensions/piconload/menu/' + picture
    if name == '---':
        if fileExists(picture):
            res.append(MultiContentEntryPixmapAlphaTest(pos=(100, 0), size=(400, 60), png=loadPNG(picture)))
    else:
        if fileExists(picture):
            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(100, 50), png=loadPNG(picture)))
        res.append(MultiContentEntryText(pos=(160, 10), size=(550, 50), font=0, text=name))
    return res


class ExtrasList(MenuList, HTMLComponent, GUIComponent):

    def __init__(self, list, enableWrapAround=False):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.list = list
        self.l.setList(list)
        self.l.setFont(0, gFont('Regular', 21))
        self.l.setItemHeight(48)
        self.onSelectionChanged = []
        self.enableWrapAround = enableWrapAround
        self.last = 0

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        instance.selectionChanged.get().append(self.selectionChanged)
        if self.enableWrapAround:
            self.instance.setWrapAround(True)

    def selectionChanged(self):
        isDiv = False
        try:
            for element in self.list[self.getSelectionIndex()]:
                if element[0] == '---':
                    isDiv = True
                    if self.getSelectionIndex() < self.last:
                        self.up()
                    else:
                        self.down()

        except Exception as e:
            pass

        self.last = self.getSelectionIndex()
        if not isDiv:
            for f in self.onSelectionChanged:
                f()


def SimpleEntry2(name, picture):
    res = [(name, picture)]
    picture = '/usr/lib/enigma2/python/Plugins/Extensions/piconload/menu/' + picture
    if name == '---':
        if fileExists(picture):
            res.append(MultiContentEntryPixmapAlphaTest(pos=(60, 0), size=(400, 60), png=loadPNG(picture)))
    else:
        if fileExists(picture):
            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(100, 60), png=loadPNG(picture)))
        res.append(MultiContentEntryText(pos=(160, 10), size=(550, 50), font=0, text=name))
    return res


class ExtrasList2(MenuList, HTMLComponent, GUIComponent):

    def __init__(self, list, enableWrapAround=False):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.list = list
        self.l.setList(list)
        self.l.setFont(0, gFont('Regular', 21))
        self.l.setItemHeight(60)
        self.onSelectionChanged = []
        self.enableWrapAround = enableWrapAround
        self.last = 0

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        instance.selectionChanged.get().append(self.selectionChanged)
        if self.enableWrapAround:
            self.instance.setWrapAround(True)

    def selectionChanged(self):
        isDiv = False
        try:
            for element in self.list[self.getSelectionIndex()]:
                if element[0] == '---':
                    isDiv = True
                    if self.getSelectionIndex() < self.last:
                        self.up()
                    else:
                        self.down()

        except Exception as e:
            pass

        self.last = self.getSelectionIndex()
        if not isDiv:
            for f in self.onSelectionChanged:
                f()


class info(Screen):

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        info = ''
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'ok': self.close,'cancel': self.close,
           'up': self['text'].pageUp,
           'down': self['text'].pageDown,
           'left': self['text'].pageUp,
           'right': self['text'].pageDown
           }, -1)
        try:
            fp = urllib.urlopen('http://piconload.ru/upload/picons/pluginupgrade/updates.txt')
            count = 0
            self.labeltext = ''
            while 1:
                s = fp.readline()
                count += 1
                self.labeltext += str(s)
                if not s:
                    break

            fp.close()
            self['text'].setText(self.labeltext)
        except:
            self['text'].setText(_('Error in downloading INFO.text'))


class SetpiconPath(Screen, ConfigListScreen):

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_('SetpiconPath'))
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Save'))
        path = config.misc.picon_path.value
        self.picon_path = NoSave(ConfigDirectory(default=path))
        list = []
        list.append(getConfigListEntry(_('picon path'), self.picon_path))
        ConfigListScreen.__init__(self, list)
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.keySelect,'green': self.save,
           'red': self.exit,
           'cancel': self.exit
           }, -1)

    def save(self):
        config.misc.picon_path.value = self.picon_path.value
        config.misc.picon_path.save()
        config.misc.picon_path.changed()
        restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, _('GUI needs a restart to apply the new piconpath\nDo you want to Restart the GUI now?'), MessageBox.TYPE_YESNO)
        restartbox.setTitle(_('Restart GUI now?'))

    def restartGUI(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)

    def exit(self):
        self.close()

    def keySelect(self):
        self.session.openWithCallback(self.pathSelected, piconPath, self.picon_path.value)

    def pathSelected(self, res):
        if res is not None:
            self.picon_path.value = res
        return


class piconPath(Screen):

    def __init__(self, session, initDir):
        Screen.__init__(self, session)
        self.setTitle(_('Select path for picons'))
        inhibitDirs = ['/bin',
         '/boot',
         '/dev',
         '/etc',
         '/lib',
         '/proc',
         '/sbin',
         '/sys',
         '/var']
        inhibitMounts = []
        self['filelist'] = FileList(initDir, showDirectories=True, showFiles=False, inhibitMounts=inhibitMounts, inhibitDirs=inhibitDirs)
        self['target'] = Label()
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'back': self.cancel,'left': self.left,
           'right': self.right,
           'up': self.up,
           'down': self.down,
           'ok': self.ok,
           'green': self.green,
           'red': self.cancel
           }, -1)
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('OK'))

    def cancel(self):
        self.close(None)
        return

    def green(self):
        self.close(self['filelist'].getSelection()[0])

    def up(self):
        self['filelist'].up()
        self.updateTarget()

    def down(self):
        self['filelist'].down()
        self.updateTarget()

    def left(self):
        self['filelist'].pageUp()
        self.updateTarget()

    def right(self):
        self['filelist'].pageDown()
        self.updateTarget()

    def ok(self):
        if self['filelist'].canDescent():
            self['filelist'].descent()
            self.updateTarget()

    def updateTarget(self):
        currFolder = self['filelist'].getSelection()[0]
        if currFolder is not None:
            self['target'].setText(currFolder)
        else:
            self['target'].setText(_('Invalid Location'))
        return


class pluginupgrade(Screen):

    def __init__(self, session, args=0):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_('Update sattellites.xml'))
        list = []
#        list.append(SimpleEntry(_('Download plugin PiconLoad'), 'install_now.png'))
#        list.append(SimpleEntry2(_('SatellitesGen'), 'SatGen.png'))
        list.append(SimpleEntry(_('SatellitesGen'), 'SatGen.png'))
        self['menu'] = ExtrasList(list)
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.go,'back': self.close
           }, -1)

    def setWindowTitle(self):
        self.setTitle(_('piconload'))

    def go(self):
        index = self['menu'].getSelectedIndex()
        if index == 0:
#            self.session.open(AddonsGroups)
#        elif index == 1:
            self.session.open(SatellitesGen)


class skinSetup(Screen):
    skin = '\n\t<screen name="InBSetup" position="center,center" size="750,370" title="piconload skin selekt">\n\t\t<widget position="90,24" render="Listbox" scrollbarMode="showNever" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/piconload/menu/buttonskins.png" size="575,430" source="menu" transparent="1">\n\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t{"template": [ MultiContentEntryText(pos = (280, 72), size = (270, 145), flags = RT_HALIGN_LEFT, text = 0), \n\t\t\t\tMultiContentEntryPixmapAlphaTest(pos = (5, 2), size = (258, 145), png = 2), # index 3 is the pixmap\n\t\t\t\t               ],\n                                "fonts": [gFont("Regular", 30)],\n\t\t\t\t"itemHeight":150\n\t\t\t\t}\n\t\t\t</convert>\n\t\t</widget>                                        \n\t</screen>'

    def __init__(self, session, args=None):
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_('piconload skin selekt'))
        self['shortcuts'] = ActionMap(['ShortcutActions', 'WizardActions'], {'ok': self.keyOK,'cancel': self.exit,
           'back': self.exit
           })
        self.list = []
        self['menu'] = List(self.list)
        self.mList()

    def mList(self):
        self.list = []
        defpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'Extensions/piconload/menu/screen1.png'))
        mtvpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'Extensions/piconload/menu/screen2.png'))
        self.list.append((_('Standart'), 'com_one', defpng))
        self.list.append((_('miniTV'), 'com_two', mtvpng))
        self['menu'].setList(self.list)

    def keyOK(self, returnValue=None):
        if returnValue == None:
            returnValue = self['menu'].getCurrent()[1]
            if returnValue is 'com_one':
                nlist = open('/usr/lib/enigma2/python/Plugins/Extensions/piconload/skin/piconload_skin1.xml', 'r').readlines()
                slist = open('/usr/lib/enigma2/python/Plugins/Extensions/piconload//piconload_skin.xml', 'w')
                slist.writelines(nlist)
                slist.close()
                self.session.open(MessageBox, _('GUI needs a restart to apply a new skins'), MessageBox.TYPE_INFO, timeout=5)
            elif returnValue is 'com_two':
                nlist = open('/usr/lib/enigma2/python/Plugins/Extensions/piconload/skin/piconload_skin2.xml', 'r').readlines()
                slist = open('/usr/lib/enigma2/python/Plugins/Extensions/piconload//piconload_skin.xml', 'w')
                slist.writelines(nlist)
                slist.close()
                self.session.open(MessageBox, _('GUI needs a restart to apply a new skins'), MessageBox.TYPE_INFO, timeout=5)
        return

    def exit(self):
        self.close()


UserAgent = 'Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.0.15) Gecko/2009102815 Ubuntu/9.04 (jaunty) Firefox/3.'
URL = 'https://raw.githubusercontent.com/OpenPLi/tuxbox-xml/master/xml/satellites.xml'
FILE = '/etc/tuxbox/satellites.xml'
Plugin_Path = '/usr/lib/enigma2/python/Plugins/Extensions/piconload/'
SelectionList.selectionpng = LoadPixmap(cached=True, path=Plugin_Path + 'tick.png')

def getXML(url):
    return getPage(url, agent=UserAgent)


def satcmp(a, b):
    if a[1] > b[1]:
        return 1
    elif a[1] == b[1]:
        return 0
    else:
        return -1


class SatellitesGen(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self['statustext'] = StaticText()
        self['key_red'] = Button(_('Close'))
        self['key_green'] = Button(_('Apply'))
        self['key_yellow'] = Button(_('Uncheck All'))
        self.list = SelectionList.SelectionList()
        self['list'] = self.list
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.list.toggleSelection,'cancel': self.close,
           'red': self.close,
           'green': self.write,
           'yellow': self.uncheckAll
           }, -1)
        self.satfile = open(FILE, 'r')
        self.satList = []
        self.finished = False
        self.onLayoutFinish.append(self.startDownload)

    def startDownload(self):
        self.currentList = []
        curroot = etree.parse(self.satfile)
        for sat in curroot.findall('sat'):
            name = sat.attrib.get('name')
            position = int(sat.attrib.get('position'))
            self.currentList.append(position)

        self.satfile.close()
        self['statustext'].text = _('Getting latest satellites list... It can take long time on slow internet connection!')
        getXML(URL).addCallback(self.xmlCallback).addErrback(self.error)

    def xmlCallback(self, xmlstring):
        self.root = etree.fromstring(xmlstring)
        index = 0
        for sat in self.root.findall('sat'):
            name = sat.attrib.get('name').encode('iso-8859-1')
            position = int(sat.attrib.get('position'))
            self.satList.append([name, position, index])
            index += 1

        self.satList.sort(cmp=satcmp)
        index = 0
        for x in self.satList:
            if x[1] == 192:
                center = index
            self.list.addSelection(x[0], x[1], x[2], x[1] in self.currentList)
            index += 1

        self.list.moveToIndex(center)
        self['statustext'].text = _('Now edit your satellites list!')
        self.finished = True

    def write(self):
        if self.finished:
            selList = self.list.getSelectionsList()
            posList = [ selList[i][1] for i in range(len(selList)) ]
            writeRoot = etree.Element('satellites')
            for item in self.root:
                if int(item.attrib.get('position')) in posList:
                    writeRoot.append(item)

            satfile = open(FILE, 'w')
            handle = etree.tostring(writeRoot, encoding='iso-8859-1')
            satfile.writelines(handle)
            satfile.close()
            self['statustext'].text = _('New satellites sucsessfully writen . Restart Enigma now')

    def error(self, error=None):
        if error is not None:
            self['statustext'].text = str(error.getErrorMessage())
        return

    def uncheckAll(self):
        for i in range(len(self.list.list)):
            item = self.list.list[i][0]
            self.list.list[i] = SelectionList.SelectionEntryComponent(item[0], item[1], item[2], False)

        self.list.setList(self.list.list)


class getScreenshot(Screen):
    skin = ''

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.skin = getScreenshot.skin
        self.previousflag = 0
        eActionMap.getInstance().bindAction('', -2147483647, self.screenshotKey)

    def screenshotKey(self, key, flag):
        if config.plugins.shootyourscreen.enable.value:
            if key == 138:
                if not config.plugins.shootyourscreen.switchhelp.value:
                    if flag == 3:
                        self.previousflag = flag
                        self.grabScreenshot()
                        return 1
                    if self.previousflag == 3 and flag == 1:
                        self.previousflag = 0
                        return 1
                else:
                    if flag == 0:
                        return 1
                    if flag == 3:
                        self.previousflag = flag
                        return 0
                    if flag == 1 and self.previousflag == 0:
                        self.grabScreenshot()
                        return 1
                    if self.previousflag == 3 and flag == 1:
                        self.previousflag = 0
                        return 0
        return 0

    def grabScreenshot(self, ret=None):
        self.filename = self.getFilename()
        print '[ShootYourScreen] grab screenshot to %s' % self.filename
        cmd = 'grab'
        if not config.plugins.shootyourscreen.picturetype.value == 'all':
            self.cmdoptiontype = ' ' + str(config.plugins.shootyourscreen.picturetype.value)
            cmd += self.cmdoptiontype
        if not config.plugins.shootyourscreen.picturesize.value == 'default':
            self.cmdoptionsize = ' ' + str(config.plugins.shootyourscreen.picturesize.value)
            cmd += self.cmdoptionsize
        if not config.plugins.shootyourscreen.pictureformat.value == 'bmp':
            self.cmdoptionformat = ' ' + str(config.plugins.shootyourscreen.pictureformat.value)
            cmd += self.cmdoptionformat
            if config.plugins.shootyourscreen.pictureformat.value == '-j':
                self.cmdoptionquality = ' ' + str(config.plugins.shootyourscreen.jpegquality.value)
                cmd += self.cmdoptionquality
        cmd += ' %s' % self.filename
        ret = system(cmd)
        self.gotScreenshot(ret)

    def gotScreenshot(self, ret):
        if not config.plugins.shootyourscreen.timeout.value == 'off':
            self.messagetimeout = int(config.plugins.shootyourscreen.timeout.value)
            if ret == 0:
                self.session.open(MessageBox, _('Screenshot successfully saved as:\n%s') % self.filename, MessageBox.TYPE_INFO, timeout=self.messagetimeout)
            else:
                self.session.open(MessageBox, _('Grabbing Screenshot failed !!!'), MessageBox.TYPE_ERROR, timeout=self.messagetimeout)

    def getFilename(self):
        time = localtime()
        year = str(time.tm_year)
        month = time.tm_mon
        day = time.tm_mday
        hour = time.tm_hour
        minute = time.tm_min
        second = time.tm_sec
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
        if hour < 10:
            hour = '0' + str(hour)
        else:
            hour = str(hour)
        if minute < 10:
            minute = '0' + str(minute)
        else:
            minute = str(minute)
        if second < 10:
            second = '0' + str(second)
        else:
            second = str(second)
        self.screenshottime = 'screenshot_' + year + '-' + month + '-' + day + '_' + hour + '-' + minute + '-' + second
        if config.plugins.shootyourscreen.pictureformat.value == 'bmp':
            self.fileextension = '.bmp'
        elif config.plugins.shootyourscreen.pictureformat.value == '-j':
            self.fileextension = '.jpg'
        elif config.plugins.shootyourscreen.pictureformat.value == '-p':
            self.fileextension = '.png'
        self.picturepath = getPicturePath()
        if self.picturepath.endswith('/'):
            self.screenshotfile = self.picturepath + self.screenshottime + self.fileextension
        else:
            self.screenshotfile = self.picturepath + '/' + self.screenshottime + self.fileextension
        return self.screenshotfile


class ShootYourScreenConfig(Screen, ConfigListScreen):
    skin = '\n\t\t<screen position="center,center" size="650,400" title="ShootScreen" >\n\t\t<widget name="config" position="10,10" size="630,350" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/piconload/menu/button1080x25.png" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/piconload/menu/red.png" zPosition="2" position="10,350" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/piconload/menu/green.png" zPosition="2" position="250,350" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/piconload/menu/yellow.png" zPosition="2" position="500,350" size="140,40" alphatest="on" />\n               <widget backgroundColor="red" font="Regular;18" name="key_red" position="10,355" size="140,40" valign="top" halign="center" transparent="1" zPosition="6" />\n               <widget backgroundColor="green" font="Regular;18" name="key_green" position="250,355" size="140,40" valign="top" halign="center" transparent="1" zPosition="6" />\n               <widget backgroundColor="yellow" font="Regular;18" name="key_yellow" position="500,355" size="140,40" valign="top" halign="center" transparent="1" zPosition="6" />\n    \n\t\t</screen>'

    def __init__(self, session, args=None):
        self.session = session
        Screen.__init__(self, session)
        self.createConfigList()
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self['statustext'] = StaticText()
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Save'))
        self['key_yellow'] = Button(_('Default'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {'green': self.keyGreen,'red': self.cancel,
           'yellow': self.revert,
           'cancel': self.cancel,
           'ok': self.keyGreen
           }, -2)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('Selected OSD for STB - %s') % pluginversion)

    def createConfigList(self):
        self.list = []
        self.list.append(getConfigListEntry(_('Enable ShootYourScreen :'), config.plugins.shootyourscreen.enable))
        if config.plugins.shootyourscreen.enable.value == True:
            self.list.append(getConfigListEntry(_('Screenshot of :'), config.plugins.shootyourscreen.picturetype))
            self.list.append(getConfigListEntry(_('Format for screenshots :'), config.plugins.shootyourscreen.pictureformat))
            if config.plugins.shootyourscreen.pictureformat.value == '-j':
                self.list.append(getConfigListEntry(_('Quality of jpg picture :'), config.plugins.shootyourscreen.jpegquality))
            self.list.append(getConfigListEntry(_('Picture size (width) :'), config.plugins.shootyourscreen.picturesize))
            self.list.append(getConfigListEntry(_('Path for screenshots :'), config.plugins.shootyourscreen.path))
            self.list.append(getConfigListEntry(_('Switch Help and Help long button :'), config.plugins.shootyourscreen.switchhelp))
            self.list.append(getConfigListEntry(_('Timeout for info message :'), config.plugins.shootyourscreen.timeout))

    def changedEntry(self):
        self.createConfigList()
        self['config'].setList(self.list)

    def save(self):
        for x in self['config'].list:
            x[1].save()

        self.changedEntry()

    def keyGreen(self):
        self.save()
        self.close(False, self.session)

    def cancel(self):
        if self['config'].isChanged():
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _('Really close without saving settings?'), MessageBox.TYPE_YESNO, default=True)
        else:
            for x in self['config'].list:
                x[1].cancel()

            self.close(False, self.session)

    def cancelConfirm(self, result):
        if result is None or result is False:
            print '[ShootYourScreen] Cancel not confirmed.'
        else:
            print '[ShootYourScreen] Cancel confirmed. Configchanges will be lost.'
            for x in self['config'].list:
                x[1].cancel()

            self.close(False, self.session)
        return

    def revert(self):
        self.session.openWithCallback(self.keyYellowConfirm, MessageBox, _('Reset ShootYourScreen settings to defaults?'), MessageBox.TYPE_YESNO, timeout=20, default=True)

    def keyYellowConfirm(self, confirmed):
        if not confirmed:
            print '[ShootYourScreen] Reset to defaults not confirmed.'
        else:
            print '[ShootYourScreen] Setting Configuration to defaults.'
            config.plugins.shootyourscreen.enable.setValue(1)
            config.plugins.shootyourscreen.switchhelp.setValue(1)
            config.plugins.shootyourscreen.path.setValue('/media/hdd')
            config.plugins.shootyourscreen.pictureformat.setValue('bmp')
            config.plugins.shootyourscreen.jpegquality.setValue('100')
            config.plugins.shootyourscreen.picturetype.setValue('all')
            config.plugins.shootyourscreen.picturesize.setValue('default')
            config.plugins.shootyourscreen.timeout.setValue('3')
            self.save()


class AddonsGroups(Screen):

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Update'))
        self['key_yellow'] = Button(_('Help'))
        self['key_blue'] = Button(_('About'))
        self.list = []
        self['list'] = MenuList([])
        self['info'] = Label()
        self['fspace'] = Label()
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['info'].setText('Downloading addons, Please wait...')
        self.timer = eTimer()
        self.timer.callback.append(self.downloadxmlpage)
        self.timer.start(100, 1)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,'blue': self.ShowAbout,
           'yellow': self.shownews,
           'green': self.pluginupdate,
           'red': self.close,
           'cancel': self.close
           }, -2)

    def updateable(self):
        try:
            selection = str(self.names[0])
            lwords = selection.split('_')
            lv = lwords[1]
            self.lastversion = lv
            if float(lv) == float(piconload_version):
                return False
            if float(lv) > float(piconload_version):
                return True
            return False
        except:
            return False

    def ShowAbout(self):
        title = _('piconload Plugin %s\nPiconmaster mooneyes \nPiconmaster Kiber12\nPluginmaster Maigais\nPluginmaster Technik') % piconload_version
        self.session.open(MessageBox, title, MessageBox.TYPE_INFO)

    def shownews(self):
        self.session.open(helpinfo)

    def pluginupdate(self):
        softupdate = self.updateable()
        if softupdate == True:
            com = 'http://piconload.ru/upload/picons/pluginupgrade/news/enigma2-extensions-piconload-usb-hdd' + self.lastversion + '_all.ipk'
        else:
            self.session.open(MessageBox, 'Plugin is up-to-date', MessageBox.TYPE_WARNING, 2)
            return
        dom = 'PICONLOAD addons manager' + self.lastversion
        self.session.open(Console, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com])

    def downloadxmlpage(self):
        url = 'http://piconload.ru/upload/picons/pluginupgrade/news/addonsnew.xml'
        getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print str(error)
        self['info'].setText(_('Addons Download Failure, No internet connection or Server down !'))
        self.downloading = False

    def _gotPageLoad(self, data):
        self.xml = data
        try:
            if self.xml:
                xmlstr = minidom.parseString(self.xml)
            else:
                self.downloading = False
                self['info'].setText(_('Addons Download Failure, No internet connection or server down !'))
                return
            self.data = []
            self.names = []
            icount = 0
            list = []
            xmlparse = xmlstr
            self.xmlparse = xmlstr
            for plugins in xmlstr.getElementsByTagName('plugins'):
                self.names.append(plugins.getAttribute('cont').encode('utf8'))

            self.list = list
            self['info'].setText('')
            self['list'].setList(self.names)
            self.downloading = True
        except:
            self.downloading = False
            self['info'].setText(_('Error processing server addons data.'))

    def okClicked(self):
        if self.downloading == True:
            try:
                selection = str(self['list'].getCurrent())
                self.session.open(IpkgPackages, self.xmlparse, selection)
            except:
                return

        else:
            self.close


class IpkgPackages(Screen):

    def __init__(self, session, xmlparse, selection):
        self.session = session
        Screen.__init__(self, session)
        self.xmlparse = xmlparse
        self.selection = selection
        list = []
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    list.append(plugin.getAttribute('name').encode('utf8'))

        list.sort()
        self['countrymenu'] = MenuList(list)
        self['actions'] = ActionMap(['SetupActions'], {'ok': self.selclicked,'cancel': self.close
           }, -2)

    def selclicked(self):
        try:
            selection_country = self['countrymenu'].getCurrent()
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.prombt(urlserver, pluginname)

    def prombt(self, com, dom):
        self.com = com
        self.dom = dom
        if self.selection == 'Skins':
            self.session.openWithCallback(self.callMyMsg, MessageBox, _('Do not install any skin unless you are sure it is compatible with your image.Are you sure?'), MessageBox.TYPE_YESNO)
        else:
            self.session.open(Console2, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com])

    def callMyMsg(self, result):
        if result:
            dom = self.dom
            com = self.com
            self.session.open(Console2, _('downloading-installing: %s') % dom, ['ipkg install -force-overwrite %s' % com])
