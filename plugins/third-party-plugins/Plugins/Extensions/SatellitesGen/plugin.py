from __init__ import _
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import NumberActionMap, ActionMap
from Components.Sources.StaticText import StaticText
from Components.Language import language
from Components.config import config, ConfigSelection, getConfigListEntry, ConfigSubsection, ConfigSelection, ConfigEnableDisable, ConfigYesNo, ConfigInteger, NoSave, ConfigText, ConfigDirectory
from Components.ConfigList import ConfigListScreen
from Components.FileList import FileList
from Components import SelectionList
from Components.Button import Button
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, SCOPE_SKIN_IMAGE
from Tools.LoadPixmap import LoadPixmap
from skin import loadSkin
import xml.etree.cElementTree as etree
from twisted.web.client import downloadPage, getPage
from enigma import *
import gettext
import os
import urllib


SKIN_PATH = '/usr/lib/enigma2/python/Plugins/Extensions/SatellitesGen/'
loadSkin(SKIN_PATH + '/SatellitesGen_skin_1080.xml')
SatellitesGen_version = '1.0'
SatellitesGen_plugindir = '/usr/lib/enigma2/python/Plugins/Extensions/SatellitesGen'


SatellitesGen_title = 'SatellitesGen'
sp = config.osd.language.value.split('_')
SatellitesGen_language = sp[0]

if os.path.exists('%s/locale/%s' % (SatellitesGen_plugindir, SatellitesGen_language)):
    _ = gettext.Catalog('SatellitesGen', '%s/locale' % SatellitesGen_plugindir).gettext

pluginversion = 'Prof'


def startSetup(session, **kwargs):
    session.open(SatellitesGen)


def Plugins(**kwargs):
    return [
     PluginDescriptor(name=_('SatellitesGen'), description=_('Satellites Generator'), where=PluginDescriptor.WHERE_PLUGINMENU, icon='SatellitesGen.png', fnc=startSetup)]


UserAgent = 'Mozilla/5.0 (X11; U; Linux x86_64; de; rv:1.9.0.15) Gecko/2009102815 Ubuntu/9.04 (jaunty) Firefox/3.'
URL = 'https://raw.githubusercontent.com/OpenPLi/tuxbox-xml/master/xml/satellites.xml'
FILE = '/etc/tuxbox/satellites.xml'
Plugin_Path = '/usr/lib/enigma2/python/Plugins/Extensions/SatellitesGen/'
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
