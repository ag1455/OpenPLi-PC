# -*- coding: utf-8 -*-
# LuxSat_Users_Menu_v12.6
import os
import re
import time
import urllib2
import urllib
import json
import httplib
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


from urllib import unquote_plus
from urllib2 import Request, urlopen, URLError, HTTPError
from time import sleep
from time import ctime
from urllib import urlretrieve
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel
from skin import parseFont
from Components.Converter.ClockToText import ClockToText
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.AVSwitch import AVSwitch
from Components.FileList import FileList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest, MultiContentEntryPixmap, MultiContentEntryPixmapAlphaBlend
from Plugins.Plugin import PluginDescriptor
from enigma import ePicLoad, getDesktop
from enigma import eLabel, eListboxPythonMultiContent, loadPNG, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER
from enigma import eTimer
from twisted.web.client import downloadPage, getPage
from time import gmtime, strftime
import struct
from Components.ProgressBar import ProgressBar

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
    lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
    os_environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
    gettext.bindtextdomain("MenuLux", resolveFilename(SCOPE_PLUGINS, "Extensions/MenuLux/locale"))

def _(txt):
    t = gettext.dgettext("MenuLux", txt)
    if t == txt:
        print "[MenuLux] fallback to default translation for", txt
        t = gettext.gettext(txt)
    return t

localeInit()
language.addCallback(localeInit)


InstallOpkgName = ''
InstallOpkgUrl = ''

luxsatCurVer = 12.6
state = ["","","","","","",""]

def shadowAdd():
    distro = 'unknown'
    try:
        f = open('/etc/opkg/all-feed.conf', 'r')
        oeline = f.readline().strip().lower()
        f.close()
        distro = oeline.split()[1].replace('-all', '')
    except:
        None
    if distro == 'openpli'or distro == 'hdfreaks'or distro == 'openhdf'or distro == 'openatv':
        return False 
    else:
        return True

def remstatus(defile,regels,zoek):
    f = open(defile,"r")
    lines = f.readlines()
    f.close()

    f = open(defile,"w")

    liness = 0
    for line in lines:
        if line.find(zoek) > 0:
            print "delete: " + line
            liness = regels
        else:
            if liness > 0:
                liness = liness-1
                print "delete: " + line
            else:
                f.write(line)
    f.close()

def weatherchat(country):
    req = urllib2.Request("http://www.buienradar."+country+"/weerbericht")
    response = urllib2.urlopen(req)
    kaas = response.read()
    kaas = kaas.replace("\t", "").replace("\r", "").replace("\n", "").replace("<strong>", "")
    kaas = kaas.replace("<br />", "").replace("</strong>", "").replace("</a>", "")
    kaas = re.sub("""<a href=".*?">""" , "", kaas)
    regx = '''<div id="readarea" class="description">(.*?)</div>'''
    match = re.findall(regx, kaas, re.DOTALL)
    return match[0]

def get_image_info(pic):
    data = None
    with open(pic, "rb") as f:
        data = f.read()
    if is_png(data):
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)
    else:
        return 0
    return width, height

def is_png(data):
    return (data[:8] == "\211PNG\r\n\032\n"and (data[12:16] == "IHDR"))

def get_image_info(pic):
    data = None
    with open(pic, "rb") as f:
        data = f.read()
    if is_png(data):
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)
    else:
        return 0
    return width, height

def transhtml(text):
    text = text.replace('&nbsp;', ' ').replace('&szlig;', 'ss').replace('&quot;', '"').replace('&ndash;', '-').replace('&Oslash;', '').replace('&bdquo;', '"').replace('&ldquo;', '"').replace('&rsquo;', "'").replace('&gt;', '>').replace('&lt;', '<').replace('&shy;', '')
    text = text.replace('&copy;.*', ' ').replace('&amp;', '&').replace('&uuml;', '\xc3\xbc').replace('&auml;', '\xc3\xa4').replace('&ouml;', '\xc3\xb6').replace('&eacute;', '\xe9').replace('&hellip;', '...').replace('&egrave;', '\xe8').replace('&agrave;', '\xe0').replace('&mdash;', '-')
    text = text.replace('&Uuml;', 'Ue').replace('&Auml;', 'Ae').replace('&Ouml;', 'Oe').replace('&#034;', '"').replace('&#039;', "'").replace('&#34;', '"').replace('&#38;', 'und').replace('&#39;', "'").replace('&#133;', '...').replace('&#196;', '\xc3\x84').replace('&#214;', '\xc3\x96').replace('&#220;', '\xc3\x9c').replace('&#223;', '\xc3\x9f').replace('&#228;', '\xc3\xa4').replace('&#246;', '\xc3\xb6').replace('&#252;', '\xc3\xbc')
    text = text.replace('&#8211;', '-').replace('&#8212;', '\x97').replace('&#8216;', "'").replace('&#8217;', "'").replace('&#8220;', '"').replace('&#8221;', '"').replace('&#8230;', '...').replace('&#8242;', "'").replace('&#8243;', '"')
    text = text.replace('H?r', 'Huehner').replace('Arr?z', 'Arretez').replace('Belgi', 'Belgie').replace('p?can', 'pelican').replace('e.a', '').replace('A?a', 'Aissa').replace('Dsland', 'Duitsland').replace('pr?re', 'prefere').replace('&Agrave;', 'A').replace('é', 'e').replace('É', 'E').replace('é', 'e')
    text = text.replace('&Agrave;', 'À ').replace('&agrave;', 'à ').replace('&Acirc;', 'Â ').replace('&acirc;', 'â ').replace('&AElig;', 'Æ').replace('&aelig;', 'æ').replace('&Ccedil;', 'Ç').replace('&ccedil;', 'ç').replace('&Egrave;', 'È ').replace('&Uuml;', 'Ü').replace('&uuml;', 'ü').replace('&laquo;', '«')
    text = text.replace('&egrave;', 'è').replace('&Eacute;', 'É ').replace('&eacute;', 'é').replace('&Ecirc;', 'Ê ').replace('&ecirc;', 'ê ').replace('&Euml;', 'Ë ').replace('&euml;', 'ë ').replace('&Icirc;', 'Î ').replace('&icirc;', 'î ').replace('&raquo;', '»').replace('&euro;', '€').replace('&oacute;', 'ó')
    text = text.replace('&Iuml;', 'Ï ').replace('&iuml;', 'ï ').replace('&Ocirc;', 'Ô').replace('&ocirc;', 'ô').replace('&OElig;', 'Œ').replace('&oelig;', 'œ').replace('&Ugrave;', 'Ù').replace('&ugrave;', 'ù').replace('&Ucirc;', 'Û').replace('&ucirc;', 'û').replace('&Ocirc;', 'Ô')
    text = text.replace('<u>', '').replace('</u>', '').replace('<b>', '').replace('</b>', '').replace('&deg;', '°').replace('&ordm;', '°').replace('&euml;', 'e')
    return text


labeltext = ""


def checkInternet():
    try:
        response = urllib2.urlopen('http://google.com')
        return True
    except:
        print
        False


def displayError(session, msg):
    global displayErrorMsg
    displayErrorMsg = msg
    session.open(errorScreen)


def getScale():
    return AVSwitch().getFramebufferScale()


SERVER = 'http://www.luxsat.be/hpengine/'
PATH = 'download_files/keys/30/'
FILELB1 = 'filedistlb.txt'
FILELB2 = 'filedistlbu800.txt'
CONFIG1 = SERVER + PATH + FILELB1
CONFIG2 = SERVER + PATH + FILELB2
FILEB1LOC = '/tmp/filedistlb.txt'
FILEB2LOC = '/tmp/filedistlbu.txt'
DUMMY = '/tmp/count'
RESULTDOWN = '/tmp/result.txt'
SERVERPATH = 'download_files/'
FILEM = 'mofd.txt'
CONFIGF = SERVER + SERVERPATH + FILEM

FILEREM = '/usr/lib/enigma2/python/Plugins/'

classid_plugin = []
classid_plugin_num = 0

sz_w = getDesktop(0).size().width()
selectedframe = [0, 0]


class buttonmenuscreen(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w > 1800:
        skin = """
        <screen position="center,center" size="1920,1080" title=" " flags="wfNoBorder" >
            <widget name="framepic" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/framehd.png" position="910,163" size="225,225" zPosition="3" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/luxsatmenuhd.png" position="185,680" size="400,180" zPosition="3" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/buttonmenuhd.png" position="912,169" size="850,770" alphatest="on"/>
            <widget name="bmenu" position="30,7" size="1860,75" transparent="1" zPosition="1" font="Regular;36" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="left"/>
            <widget name="mess1" position="270,870" size="750,45" foregroundColor="green" font="Regular;27"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="30,120" size="720,405" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="30,125" size="720,30" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28" borderColor="black" borderWidth="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="on"/>
            <widget name="key_red" position="242,1030" size="370,42" zPosition="1" transparent="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
            <widget name="key_green" position="678,1030" size="370,38" zPosition="1" transparent="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/yellow34.png" position="1064,1032" size="34,34" alphatest="on"/>
            <widget name="key_yellow" position="1114,1030" size="370,42" zPosition="1" transparent="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/blue34.png" position="1500,1032" size="34,34" alphatest="on"/>
            <widget name="key_blue" position="1550,1030" size="370,38" zPosition="3" transparent="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    else:
        skin = """
        <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder" >
            <widget name="framepic" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/frame.png" position="637,127" size="135,135" zPosition="3" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/luxsatmenu.png" position="145,430" size="270,122" zPosition="3" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/buttonmenu.png" position="640,130" size="499,460" zPosition="2" alphatest="on"/>
            <widget name="bmenu" position="85,30" size="1085,55" transparent="1" zPosition="1" font="Regular;24" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="left"/>
            <widget name="mess1" position="180,580" size="500,30" foregroundColor="green" font="Console;18"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/buttonmenu.png" position="642,132" size="500,460" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="85,110" size="417,243" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="85,89" size="417,20" zPosition="1" foregroundColor="white" borderColor="black" borderWidth="1" transparent="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
            <widget name="key_red" position="185,643" size="220,28" zPosition="3" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/> 
            <widget name="key_green" position="460,643" size="220,28" zPosition="1" transparent="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/yellow26.png" position="695,643" size="26,26" alphatest="on"/>
            <widget name="key_yellow" position="735,643" size="320,28" zPosition="3" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/blue26.png" position="970,643" size="26,26" alphatest="on"/>
            <widget name="key_blue" position="1010,643" size="220,28" zPosition="3" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    def __init__(self, session, args=None):
        self.selected = 0
        self.selectedud = 0
        self.session = session
        self.visible = 0
        self["mess1"] = ScrollLabel(" ")
        response = urllib2.urlopen("http://claudck193.193.axc.nl/Plugin_Feed/version_menulux.txt")
        curver = float(response.read())

        if luxsatCurVer < curver:
            from enigma import eTimer
            self.pausetimer = eTimer()
            self.pausetimer.callback.append(self.luxsatUpdateMain)
            self.pausetimer.start(500, True)

        if shadowAdd():
            buttonmenuscreen.skin = buttonmenuscreen.skin.replace("""borderColor="black" borderWidth="1" ""","")
        self.skin = buttonmenuscreen.skin
        Screen.__init__(self, session)
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label((""))
        self["key_yellow"] = Label(_("Remove SettingList"))
        self["key_blue"] = Label(_("Remove IptvList"))
        self["bmenu"] = Label(_("LuxSat Users Menu 12.6"))
        self["framepic"] = MovingPixmap()
        self["actions"] = ActionMap(['OkCancelActions',
                                     'ShortcutActions',
                                     'WizardActions',
                                     'SetupActions',
                                     'NumberActions',
                                     'MenuActions',
                                     'HelpActions'],
                                    {"ok": self.go, "down": self.down, "up": self.up, "left": self.left, "right": self.right, "cancel": self.cancel, "red": self.exit, "green": self.unVis, "yellow": self.ChannelListrem, "blue": self.listRemIptv}, -1)

    def luxsatUpdateMain(self):
        self.session.openWithCallback(self.menuluxUpdate, MessageBox,
                                      _("Update available, do you want to update and restart Enigma? "))

    def menuluxUpdate(self, luxupg):
        if luxupg is True:
            self["mess1"].setText(_("Package will be Updated"))
            try:
                self.session.open(Console, _("downloading-installing: MenuLux") , ["echo Please wait while Downloading and Installing!!;opkg install -force-overwrite http://claudck193.193.axc.nl/Plugin_Feed/-arm/-Tools/enigma2-plugin-extensions-luxsat_all.ipk;sleep 2;killall -9 enigma2;"])

            except (IOError, RuntimeError, NameError):
                self["mess1"].setText(_("Package was NOT Updated"))


        self.updateFrameselect()

    def left(self):
        self.selected -= 1
        self.updateFrameselect()

    def right(self):
        self.selected += 1
        self.updateFrameselect()

    def up(self):
        self.selectedud -= 1
        self.updateFrameselect()

    def down(self):
        self.selectedud += 1
        self.updateFrameselect()

    def updateFrameselect(self):
        if self.selected < 0:
            self.selected = 2
        elif self.selected > 2:
            self.selected = 0
        if self.selectedud < 0:
            self.selectedud = 2
        elif self.selectedud > 2:
            self.selectedud = 0

        if sz_w > 1800:
            self["framepic"].moveTo(912 + (315 * self.selected), 163 + (275 * self.selectedud), 1)
        else:
            self["framepic"].moveTo(637 + (185 * self.selected), 127 + (165 * self.selectedud), 1)
        self["framepic"].startMoving()

    def go(self):
        global selectedframe
        selectedframe[0] = self.selected
        selectedframe[1] = self.selectedud
        if (selectedframe[0] == 0 and selectedframe[1] == 0):
            self.Messagedownloader()
        if (selectedframe[0] == 0 and selectedframe[1] == 1):
            locdirsave = "/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/iptvc.cfg"
            if os.path.exists(locdirsave):
                self.session.open(iptvplugin)
            elif self.visible >= 2:
                file = open(locdirsave, "w")
                file.close()
        if (selectedframe[0] == 0 and selectedframe[1] == 2):
            self.session.open(tvMovies)
        if (selectedframe[0] == 1 and selectedframe[1] == 0):
            self.Keydownloader()
        if (selectedframe[0] == 1 and selectedframe[1] == 1):
            filessoftcams("")
            filessoftcams2(_("Settings_Channellist/"))
            self.session.open(rootplugins2)
        if (selectedframe[0] == 1 and selectedframe[1] == 2):
            self.session.open(weatherStartMenu)
        if (selectedframe[0] == 2 and selectedframe[1] == 0):
            filessoftcams("")
            filessoftcams2(_("Softcams/"))
            self.session.open(rootplugins2)
        if (selectedframe[0] == 2 and selectedframe[1] == 1):
            self.session.open(rootplugins)
        if (selectedframe[0] == 2 and selectedframe[1] == 2):
            self.close()

    def unVis(self):
        self.visible += 1

    def Messagedownloader(self):
        try:
            filemofd = os.path.isfile('/tmp/mofd1.txt')
            if filemofd is True:
                os.remove('/tmp/mofd1.txt')
            urlretrieve(CONFIGF, '/tmp/mofd1.txt')
            f3 = open('/tmp/mofd1.txt', 'a')
            A = time.ctime()
            f3.write('\n\n********' + A + '********\n')
            f3.write('*********** Your Luxsat Team ***********\n')
            f3.write('************ End of message ************\n')
            f3.close()
            self.session.open(Console, title='Message of the Day', cmdlist=['cat /tmp/mofd1.txt'])
        except (IOError, RuntimeError, NameError):
            pass

    def Keydownloader(self):
        try:
            urlretrieve(CONFIG1, FILEB1LOC)
            urlretrieve(CONFIG2, FILEB2LOC)
            f3 = open(RESULTDOWN, 'w')
            A = time.ctime()
            f3.write('\n\n********** ' + A + ' ********** \n')
            f3.write('    Luxsat Plugin Enigma2 key downloader \n')
            f3.write('**********************************************\n')
            f3.close()
            A = os.path.isfile(FILEB1LOC)
            if A is True:
                f1 = open(FILEB1LOC)
                f3 = open(RESULTDOWN, 'a')
                f3.write('\nLuxsat File Distribution list available \n')
                f3.close()
                B = os.path.isfile(FILEB2LOC)
                if B is True:
                    x = True
                elif B == False:
                    f1.close()
                    f3.close()
                    x = False
            p = 0
            while x is True:
                a = f1.readline()
                if len(a) > 0:
                    c = a.split()
                    try:
                        if c[0] == '':
                            p = p + 1
                    except IndexError:
                        x = False
                        break

                    count = int(c[0])
                    rr = 0
                    f2 = open(FILEB2LOC)
                    while rr < count:
                        b = f2.readline()
                        rr = rr + 1

                    dir = "/var/keys/"
                    if not os.path.exists(dir):
                        os.makedirs(dir)
                    urlpath = b[:-1] + '/' + c[2]
                    filepathstore = c[1] + '/' + c[2]
                    if os.path.isfile(filepathstore):
                        os.remove(filepathstore)
                    urlretrieve(urlpath, filepathstore)
                    f3 = open(RESULTDOWN, 'a')
                    f3.write('\nServer number:' + c[0] + '\n')
                    f3.write('Downloading Key file: ' + c[2] + '\n')
                    f2.close()
                    f3.close()

            f1.close()
            f3 = open(RESULTDOWN, 'a')
            f3.write('\n**********************************************\n')
            f3.write('***  Thx to use the Luxsat key downloader  ***\n')
            f3.write('***            Your Luxsat Team            ***\n')
            f3.write('**********************************************\n')
            f3.close()
            A = os.path.isfile(FILEB1LOC)
            if A is True:
                os.remove(FILEB1LOC)
            A = os.path.isfile(FILEB2LOC)
            if A is True:
                os.remove(FILEB2LOC)
            A = os.path.isfile(DUMMY)
            if A is True:
                os.remove(DUMMY)
            self.session.open(Console, title='Luxsat Key downloader', cmdlist=['cat /tmp/result.txt'])
        except (IOError,
                RuntimeError,
                TypeError,
                NameError):
            self['mess1'].setText(('NO Keys Downloaded'))

    def ChannelListrem(self):
        self.session.openWithCallback(self.ChannelListrem1, MessageBox, ('Remove all setting lists?'))

    def ChannelListrem1(self, luxsetupg):
        if luxsetupg is True:
            for name in os.listdir("/etc/enigma2"):
                if name.endswith(".tv") or name.endswith(".radio"):
                    os.remove("/etc/enigma2/" + name)
            self.session.open(Console, ('SettingList Cleaned'),
                              ['wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &'])

    def listRemIptv(self):
        self.session.openWithCallback(self.RemoveIptv, MessageBox, ('Remove all IPTV lists?'))

    def RemoveIptv(self, luxiptv):
        if luxiptv is True:
            for name in os.listdir("/etc/enigma2"):
                if name.find("userbouquet.iptv") >= 0:
                    os.remove("/etc/enigma2/" + name)

            f = open("/etc/enigma2/bouquets.tv", "r+")
            d = f.readlines()
            f.seek(0)
            for i in d:
                if not i.find("userbouquet.iptv") >= 0:
                    f.write(i)
            f.truncate()
            f.close()
            self.session.open(Console, ('IptvList Cleaned'),
                              ['wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &'])

    def softplugin(self):
        filessoftcams("")
        self.session.open(rootplugins)

    def exit(self):
        self.close()

    def cancel(self):
        self.close(None)


plugins_ulrs = []
plugins_names = []


def filessoftcams(plugindir):
    baseurl = 'http://www.luxsat.be/hpengine/download_files/plugins/explorer.php?dir=' + plugindir

    def plugins_ulr():
        response = urllib2.urlopen(baseurl)
        html = response.read()
        regx = '''@(.*?)@'''
        match = re.findall(regx, html, re.M | re.I)
        list = []
        for name in match:
            list.append((name))
        response.close()
        return list

    def plugins_name():
        response = urllib2.urlopen(baseurl)
        html = response.read()
        regx = '''#(.*?)#'''
        match = re.findall(regx, html, re.M | re.I)
        list = []
        for name in match:
            list.append((name))
        response.close()
        return list

    global plugins_ulrs
    plugins_ulrs = plugins_ulr()
    global plugins_names
    plugins_names = plugins_name()


plugins_ulrs2 = []
plugins_names2 = []


def filessoftcams2(plugindir):
    baseurl = 'http://www.luxsat.be/hpengine/download_files/plugins/explorer.php?dir=' + plugindir

    def plugins_ulr2():
        response = urllib2.urlopen(baseurl)
        html = response.read()
        regx = '''@(.*?)@'''
        match = re.findall(regx, html, re.M | re.I)
        list = []
        for name in match:
            list.append((name))
        response.close()
        return list

    def plugins_name2():
        response = urllib2.urlopen(baseurl)
        html = response.read()
        regx = '''#(.*?)#'''
        match = re.findall(regx, html, re.M | re.I)
        list = []
        for name in match:
            list.append((name))
        response.close()
        return list

    global plugins_ulrs2
    plugins_ulrs2 = plugins_ulr2()
    global plugins_names2
    plugins_names2 = plugins_name2()


plugins_ulrs3 = []
plugins_names3 = []


def filessoftcams3(plugindir):
    baseurl = 'http://www.luxsat.be/hpengine/download_files/plugins/explorer.php?dir=' + plugindir

    def plugins_ulr3():
        response = urllib2.urlopen(baseurl)
        html = response.read()
        regx = '''@(.*?)@'''
        match = re.findall(regx, html, re.M | re.I)
        list = []
        for name in match:
            list.append((name))
        response.close()
        return list

    def plugins_name3():
        response = urllib2.urlopen(baseurl)
        html = response.read()
        regx = '''#(.*?)#'''
        match = re.findall(regx, html, re.M | re.I)
        list = []
        for name in match:
            list.append((name))
        response.close()
        return list

    global plugins_ulrs3
    plugins_ulrs3 = plugins_ulr3()
    global plugins_names3
    plugins_names3 = plugins_name3()
###################################################################
class rootplugins(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w > 1800:
        skin = """
        <screen position="center,center" size="1920,1080" title=" " flags="wfNoBorder" >
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/backgroundhd.png" position="0,0" size="1920,1080"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/requestHD.png" position="1143,300" size="600,194" zPosition="10" alphatest="on" />
            <widget name="list" position="130,315" size="850,630" zPosition="10" transparent="1" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/list/list85045.png"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/softcamHD.png" position="125,150" size="850,90" zPosition="10" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/earthHD.png" position="1043,675" size="800,344" zPosition="10" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="on"/>
            <widget name="key_red" position="242,1030" size="370,42" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/green34.png" position="628,1032" size="34,34" alphatest="on"/>
            <widget name="key_green" position="678,1030" size="370,42" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    else:
        skin = """
        <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder" >
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/background.png" position="0,0" size="1280,720"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget name="list" position="100,248" size="540,300" zPosition="10" transparent="1" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/list/list54030.png"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/softcam.png" position="101,130" size="540,57" zPosition="10" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/request.png" position="700,238" size="400,129" zPosition="10" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/earth.png" position="643,398" size="531,229" zPosition="10" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
            <widget name="key_red" position="185,643" size="220,28" zPosition="3" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/green26.png" position="420,643" size="26,26" alphatest="on"/>
            <widget name="key_green" position="460,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        if shadowAdd():
            iptvplugin.skin = iptvplugin.skin.replace("""borderColor="black" borderWidth="1" ""","")
        self.skin = rootplugins.skin

        response = urllib2.urlopen("http://claudck193.193.axc.nl/Plugin_Feed/main.php")
        html = response.read()
        self.allfiles = html.split("<br>")
        self.mycurelist = None
        self.lastsubdir = ""
        self.session = session
        self["key_red"] = Label(_("Close"))
        self["key_green"] = Label(_("Ok"))
        self["list"] = MenuList([], True, eListboxPythonMultiContent)
        self.currentList = 'list'
        self.visible = 0
        self["actions"] = ActionMap(['OkCancelActions',
                                     'ShortcutActions',
                                     'WizardActions',
                                     'SetupActions',
                                     'NumberActions',
                                     'MenuActions',
                                     'HelpActions'],
                                    {"ok": self.go, "down": self.down, "up": self.up, "left": self.left,
                                     "right": self.right, "cancel": self.cancel}, -1)
        self.fillmylistt()
        self.onLayoutFinish.append(self.fillmylistt)


    def getdata(self, folder):
            list = []
            subs = len(folder.split("/"))
            for x in self.allfiles:
                print(x)
                if x.startswith(folder):
                    path = x.split("/")
                    if len(path) == subs:
                        if path[-1] not in list:
                            list.append([path[-1], x])
            return(list)

    def fillmylistt(self):
        scalingskins = {"itemheight": 30, "setFont": 24, "setsize": [540, 30]}
        sz_w = getDesktop(0).size().width()
        if sz_w > 1800:
            scalingskins = {"itemheight": 45, "setFont": 36, "setsize": [850, 45]}
        self["list"].l.setItemHeight(scalingskins["itemheight"])
        self["list"].l.setFont(0, gFont("Regular", scalingskins["setFont"]))
        events = []
        self.mycurelist = self.getdata("")
        for filename in self.mycurelist:
            print(filename)
            res = []
            res.append(
                MultiContentEntryText(pos=(0, 5), size=(10, 25), font=0, flags=RT_HALIGN_LEFT))
            res.append(
                MultiContentEntryText(pos=(2, 0), size=(scalingskins["setsize"][0], scalingskins["setsize"][1]), font=0,
                                      flags=RT_HALIGN_LEFT, text=str(filename[0]), color=0x00D2D226,
                                      color_sel=0x00D2D226))
            events.append(res)
        self["list"].l.setList(events)
        self["list"].show()

    def up(self):
        self["list"].up()

    def down(self):
        self["list"].down()

    def left(self):
        self[self.currentList].pageUp()

    def right(self):
        self[self.currentList].pageDown()

    def reloadlist(self, dir):
            scalingskins = {"itemheight": 30, "setFont": 24, "setsize": [540, 30]}
            sz_w = getDesktop(0).size().width()
            if sz_w > 1800:
                scalingskins = {"itemheight": 45, "setFont": 36, "setsize": [850, 45]}
            self["list"].l.setItemHeight(scalingskins["itemheight"])
            self["list"].l.setFont(0, gFont("Regular", scalingskins["setFont"]))
            events = []
            self.mycurelist = self.getdata(dir)
            for filename in self.mycurelist:
                res = []
                res.append(
                    MultiContentEntryText(pos=(0, 5), size=(10, 25), font=0, flags=RT_HALIGN_LEFT))
                res.append(
                    MultiContentEntryText(pos=(2, 0), size=(scalingskins["setsize"][0], scalingskins["setsize"][1]), font=0,
                                          flags=RT_HALIGN_LEFT, text=str(filename[0]), color=0x00D2D226,
                                          color_sel=0x00D2D226))
                events.append(res)
            self["list"].l.setList(events)
            self["list"].show()

    def go(self):
        try:
            returnValue = self["list"].l.getCurrentSelection()
            print(returnValue)
            listindex = self['list'].l.getCurrentSelectionIndex()
            if "." not in returnValue[1][7]:
                print("ok")
                self.lastsubdir = self.mycurelist[listindex][1]+"/"
                self.reloadlist(self.lastsubdir)
            elif len(returnValue[1][7]) > 3:
                filetodownload = self.mycurelist[listindex][1]
                filename = self.mycurelist[listindex][0]
                self.session.open(Console, ('downloading-installing: %s') % filetodownload,['opkg install -force-overwrite %s; wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &' % ('http://claudck193.193.axc.nl/Plugin_Feed/' + filetodownload)])
        except:
            None

    def cancel(self):
        if self.lastsubdir == "":
            self.close(None)
        elif len(self.lastsubdir.split("/")) == 2:
            self.lastsubdir = ""
            print(self.lastsubdir)
            self.reloadlist(self.lastsubdir)
        else:
            self.lastsubdir = ("/").join(self.lastsubdir[:-1].split("/")[:-1])+"/"
            print(">>>> "+self.lastsubdir)
            self.reloadlist(self.lastsubdir)

class rootplugins2(Screen):

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        if shadowAdd():
            rootplugins.skin = rootplugins.skin.replace("""borderColor="black" borderWidth="1" ""","")
        self.skin = rootplugins.skin
        self.session = session
        self["key_red"] = Label(_("Close"))
        self["key_green"] = Label(_("Ok"))
        self["list"] = MenuList([], True, eListboxPythonMultiContent)
        self.currentList = 'list'
        self.visible = 0
        self["actions"] = ActionMap(['OkCancelActions',
                                     'ShortcutActions',
                                     'WizardActions',
                                     'SetupActions',
                                     'NumberActions',
                                     'MenuActions',
                                     'HelpActions'],
                                    {"ok": self.go, "down": self.down, "up": self.up, "left": self.left,
                                     "right": self.right, "cancel": self.cancel, "green": self.go}, -1)
        self.fillmylist()
        self.onLayoutFinish.append(self.fillmylist)

    def fillmylist(self):
        scalingskins = {"itemheight": 30, "setFont": 24, "setsize": [540, 30]}
        sz_w = getDesktop(0).size().width()
        if sz_w > 1800:
            scalingskins = {"itemheight": 45, "setFont": 36, "setsize": [850, 45]}
        self["list"].l.setItemHeight(scalingskins["itemheight"])
        self["list"].l.setFont(0, gFont("Regular", scalingskins["setFont"]))
        events = []

        for x in range(len(plugins_names2)):
            res = []
            res.append(MultiContentEntryText(pos=(0, 5), size=(10, 25), font=0, flags=RT_HALIGN_LEFT))
            res.append(
                MultiContentEntryText(pos=(2, 0), size=(scalingskins["setsize"][0], scalingskins["setsize"][1]), font=0,
                                      flags=RT_HALIGN_LEFT, text=plugins_names2[x], color=0x00D2D226,
                                      color_sel=0x00D2D226))

            events.append(res)

        self["list"].l.setList(events)
        self["list"].show()

    def up(self):
        self["list"].up()

    def down(self):
        self["list"].down()

    def left(self):
        self[self.currentList].pageUp()

    def right(self):
        self[self.currentList].pageDown()

    def go(self):
        returnValue = self["list"].getSelectedIndex()
        if plugins_ulrs2[returnValue][len(plugins_ulrs2[returnValue]) - 1] == '/':
            filessoftcams3(plugins_ulrs2[returnValue])
            self.session.open(rootplugins3)
        else:
            global InstallOpkgName
            global InstallOpkgUrl
            InstallOpkgName = plugins_names2[returnValue]
            InstallOpkgUrl = plugins_ulrs2[returnValue]
            self.session.openWithCallback(self.runInstallOpkg, MessageBox, ('Install? %s') % plugins_names2[returnValue])

    def runInstallOpkg(self, terurnval):
        if terurnval is True:
            if InstallOpkgUrl.endswith("settings.ipk"):
                for name in os.listdir("/etc/enigma2"):
                    if name.endswith(".tv") or name.endswith(".radio"):
                        os.remove("/etc/enigma2/" + name)

            remstatus("/var/lib/opkg/status", 5, "caught")
            remstatus("/var/lib/opkg/status", 5, "hans")
            downloadurlplugin = "http://www.luxsat.be/hpengine/download_files/plugins/" + InstallOpkgUrl
            self.session.open(Console, ('downloading-installing: %s') % InstallOpkgName,
                              [
                                  'opkg install -force-overwrite %s; wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &' % downloadurlplugin])

    def cancel(self):
        self.close()


class rootplugins3(Screen):

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        if shadowAdd():
            rootplugins.skin = rootplugins.skin.replace("""borderColor="black" borderWidth="1" ""","")
        self.skin = rootplugins.skin
        self.session = session
        self["key_red"] = Label(_("Close"))
        self["key_green"] = Label(_("Ok"))
        self["list"] = MenuList([], True, eListboxPythonMultiContent)
        self.currentList = 'list'
        self.visible = 0
        self["actions"] = ActionMap(['OkCancelActions',
                                     'ShortcutActions',
                                     'WizardActions',
                                     'SetupActions',
                                     'NumberActions',
                                     'MenuActions',
                                     'HelpActions'],
                                    {"ok": self.go, "down": self.down, "up": self.up, "left": self.left,
                                     "right": self.right, "cancel": self.cancel, "green": self.go}, -1)
        self.fillmylist()
        self.onLayoutFinish.append(self.fillmylist)

    def fillmylist(self):
        scalingskins = {"itemheight": 30, "setFont": 24, "setsize": [540, 30]}
        sz_w = getDesktop(0).size().width()
        if sz_w > 1800:
            scalingskins = {"itemheight": 45, "setFont": 36, "setsize": [850, 45]}
        self["list"].l.setItemHeight(scalingskins["itemheight"])
        self["list"].l.setFont(0, gFont("Regular", scalingskins["setFont"]))
        events = []

        for x in range(len(plugins_names3)):
            res = []
            res.append(MultiContentEntryText(pos=(0, 5), size=(10, 25), font=0, flags=RT_HALIGN_LEFT))
            res.append(
                MultiContentEntryText(pos=(2, 0), size=(scalingskins["setsize"][0], scalingskins["setsize"][1]), font=0,
                                      flags=RT_HALIGN_LEFT, text=plugins_names3[x], color=0x00D2D226,
                                      color_sel=0x00D2D226))
            events.append(res)

        self["list"].l.setList(events)
        self["list"].show()

    def up(self):
        self["list"].up()

    def down(self):
        self["list"].down()

    def left(self):
        self[self.currentList].pageUp()

    def right(self):
        self[self.currentList].pageDown()

    def go(self):
        returnValue = self["list"].getSelectedIndex()
        if plugins_ulrs3[returnValue][len(plugins_ulrs3[returnValue]) - 1] == '/':
            print
            "ok"
        else:
            global InstallOpkgName
            global InstallOpkgUrl
            InstallOpkgName = plugins_names3[returnValue]
            InstallOpkgUrl = plugins_ulrs3[returnValue]
            self.session.openWithCallback(self.runInstallOpkg, MessageBox, ('Install? %s') % plugins_names3[returnValue])

    def runInstallOpkg(self, terurnval):
        if terurnval is True:
            if InstallOpkgUrl.endswith("settings.ipk"):
                for name in os.listdir("/etc/enigma2"):
                    if name.endswith(".tv") or name.endswith(".radio"):
                        os.remove("/etc/enigma2/" + name)

            remstatus("/var/lib/opkg/status", 5, "caught")
            remstatus("/var/lib/opkg/status", 5, "hans")
            downloadurlplugin = "http://www.luxsat.be/hpengine/download_files/plugins/" + InstallOpkgUrl
            self.session.open(Console, ('downloading-installing: %s') % InstallOpkgName,
                              [
                                  'opkg install -force-overwrite %s; wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &' % downloadurlplugin])

    def cancel(self):
        self.close()


class iptvplugin(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w > 1800:
        skin = """
        <screen position="center,center" size="1920,1080" title=" " flags="wfNoBorder" >
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/backgroundhd.png" position="0,0" size="1920,1080"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/iptv_infHD.png" position="1143,300" size="600,194" zPosition="10" alphatest="on" />
            <widget name="list" position="130,315" size="850,630" zPosition="10" transparent="1" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/list/list85045.png"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/softcamHD.png" position="125,150" size="850,90" zPosition="10" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/earthHD.png" position="1043,675" size="800,344" zPosition="10" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="on"/>
            <widget name="key_red" position="242,1030" size="370,42" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/green34.png" position="628,1032" size="34,34" alphatest="on"/>
            <widget name="key_green" position="678,1030" size="370,42" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    else:
        skin = """
        <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder" >
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/background.png" position="0,0" size="1280,720"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget name="list" position="100,248" size="540,300" zPosition="10" transparent="1" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/list/list54030.png"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/softcam.png" position="101,130" size="540,57" zPosition="10" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/iptv_inf.png" position="700,238" size="400,129" zPosition="10" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/earth.png" position="643,398" size="531,229" zPosition="10" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
            <widget name="key_red" position="185,643" size="220,28" zPosition="3" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/green26.png" position="420,643" size="26,26" alphatest="on"/>
            <widget name="key_green" position="460,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    def __init__(self, session, args=0):
        Screen.__init__(self, session)
        if shadowAdd():
            iptvplugin.skin = iptvplugin.skin.replace("""borderColor="black" borderWidth="1" ""","")
        self.skin = iptvplugin.skin

        response = urllib2.urlopen("http://claudck193.193.axc.nl/IPTV_tv/main.php")
        html = response.read()
        self.allfiles = html.split("<br>")
        self.mycurelist = None
        self.lastsubdir = ""
        self.session = session
        self["key_red"] = Label(_("Close"))
        self["key_green"] = Label(_("Ok"))
        self["list"] = MenuList([], True, eListboxPythonMultiContent)
        self.currentList = 'list'
        self.visible = 0
        self["actions"] = ActionMap(['OkCancelActions',
                                     'ShortcutActions',
                                     'WizardActions',
                                     'SetupActions',
                                     'NumberActions',
                                     'MenuActions',
                                     'HelpActions'],
                                    {"ok": self.go, "down": self.down, "up": self.up, "left": self.left,
                                     "right": self.right, "cancel": self.cancel}, -1)
        self.fillmylistt()
        self.onLayoutFinish.append(self.fillmylistt)


    def getdata(self, folder):
            list = []
            subs = len(folder.split("/"))
            for x in self.allfiles:
                print(x)
                if x.startswith(folder):
                    path = x.split("/")
                    if len(path) == subs:
                        if path[-1] not in list:
                            list.append([path[-1], x])
            return(list)

    def fillmylistt(self):
        scalingskins = {"itemheight": 30, "setFont": 24, "setsize": [540, 30]}
        sz_w = getDesktop(0).size().width()
        if sz_w > 1800:
            scalingskins = {"itemheight": 45, "setFont": 36, "setsize": [850, 45]}
        self["list"].l.setItemHeight(scalingskins["itemheight"])
        self["list"].l.setFont(0, gFont("Regular", scalingskins["setFont"]))
        events = []
        self.mycurelist = self.getdata("")
        for filename in self.mycurelist:
            res = []
            res.append(
                MultiContentEntryText(pos=(0, 5), size=(10, 25), font=0, flags=RT_HALIGN_LEFT))
            res.append(
                MultiContentEntryText(pos=(2, 0), size=(scalingskins["setsize"][0], scalingskins["setsize"][1]), font=0,
                                      flags=RT_HALIGN_LEFT, text=str(filename[0]), color=0x00D2D226,
                                      color_sel=0x00D2D226))
            events.append(res)
        self["list"].l.setList(events)
        self["list"].show()

    def up(self):
        self["list"].up()

    def down(self):
        self["list"].down()

    def left(self):
        self[self.currentList].pageUp()

    def right(self):
        self[self.currentList].pageDown()

    def reloadlist(self, dir):
            scalingskins = {"itemheight": 30, "setFont": 24, "setsize": [540, 30]}
            sz_w = getDesktop(0).size().width()
            if sz_w > 1800:
                scalingskins = {"itemheight": 45, "setFont": 36, "setsize": [850, 45]}
            self["list"].l.setItemHeight(scalingskins["itemheight"])
            self["list"].l.setFont(0, gFont("Regular", scalingskins["setFont"]))
            events = []
            self.mycurelist = self.getdata(dir)
            for filename in self.mycurelist:
                res = []
                res.append(
                    MultiContentEntryText(pos=(0, 5), size=(10, 25), font=0, flags=RT_HALIGN_LEFT))
                res.append(
                    MultiContentEntryText(pos=(2, 0), size=(scalingskins["setsize"][0], scalingskins["setsize"][1]), font=0,
                                          flags=RT_HALIGN_LEFT, text=str(filename[0]), color=0x00D2D226,
                                          color_sel=0x00D2D226))
                events.append(res)
            self["list"].l.setList(events)
            self["list"].show()

    def go(self):
        try:
            returnValue = self["list"].l.getCurrentSelection()
            listindex = self['list'].l.getCurrentSelectionIndex()
            if "." not in returnValue[1][7]:
                self.lastsubdir = self.mycurelist[listindex][1]+"/"
                self.reloadlist(self.lastsubdir)
            elif len(returnValue[1][7]) > 3:
                filetodownload = self.mycurelist[listindex][1]
                filename = self.mycurelist[listindex][0]
                if filetodownload[-4:] == ".m3u":
                    urllib.urlretrieve('http://claudck193.193.axc.nl/IPTV_tv/' + filetodownload,'/tmp/' + filename)
                else:
                    f = open('/etc/enigma2/bouquets.tv', 'a')
                    f.write('#SERVICE: 1:7:1:0:0:0:0:0:0:0:' + filename + "\n")
                    f.close()
                    urllib.urlretrieve('http://claudck193.193.axc.nl/IPTV_tv/' + filetodownload,'/etc/enigma2/' + filename)
                self.myMsg(returnValue)
        except:
            None

    def myMsg(self, entry):
        self.session.open(Console, ('SettingList Cleaned'),
                          ['wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &'])

    def cancel(self):
        if self.lastsubdir == "":
            self.close(None)
        elif len(self.lastsubdir.split("/")) == 2:
            self.lastsubdir = ""
            print(self.lastsubdir)
            self.reloadlist(self.lastsubdir)
        else:
            self.lastsubdir = ("/").join(self.lastsubdir[:-1].split("/")[:-1])+"/"
            print(">>>> "+self.lastsubdir)
            self.reloadlist(self.lastsubdir)

def todayMovies():
    req = urllib2.Request("http://feeds.feedburner.com/Filmtotaal-FilmsOpTv")
    response = urllib2.urlopen(req)
    kaas = response.read()
    regx = '''<table.*?<img .*? src="(.*?)" alt=".*?" style="margin: 0px 5px 5px 0px; float: left;" /><span style="font-size:16px;font-weight:bold;"><a href=".*?">(.*?)</a>'''
    regx += '''</span><br />(.*?) - (.*?) op (.*?)<br />(.*?) [(](.*?)[)] uit (.*?)<br />IMDB-rating: (.*?) [(].*? stemmen[)]<br />(.*?)<p>(.*?)</p></td></tr>.*?</table>'''
    match = re.findall(regx, kaas, re.DOTALL)
    filmsToday = []
    details = ["cover", "titel", "begin", "einde", "zender", "type", "jaar", "land", "score", "acteurs", "beschrijving"]
    dir = "/tmp/TVMovies/"
    if not os.path.exists(dir):
        os.makedirs(dir)
    locdir = os.listdir(dir)
    for x in match:
        detailsDict = {}
        for y in range(len(details)):
            detailsDict.update({details[y]: x[y]})
        filmsToday.append(detailsDict)
        if not os.path.exists(dir + detailsDict["cover"][-14:].replace('rs/', '')):
            print
            ""
        else:
            try:
                locdir.remove(detailsDict["cover"][-14:].replace('rs/', ''))
            except:
                print
                "failed to remove: " + detailsDict["cover"][-14:].replace('rs/', '')
    urlretrieve(filmsToday[0]["cover"], dir + filmsToday[0]["cover"][-14:].replace('rs/', ''))
    for x in locdir:
        os.remove(dir + x)

    return filmsToday


def connectedToInternet():
    try:
        response = urllib2.urlopen('http://google.com')
        return True
    except:
        print
        False


def displayError(session, msg):
    global displayErrorMsg
    displayErrorMsg = msg
    session.open(errorScreen)


def gengres(gengre):
    response = None
    for repeat in range(20):
        try:
            req = urllib2.Request("http://www.tvgids.tv/genres/" + gengre)
            response = urllib2.urlopen(req)
            break
        except urllib2.HTTPError:
            print
            "error"

    kaas = ""
    if not response == None:
        kaas = response.read()
    kaas = kaas.replace("\t", "")
    regx = '''<a href.*?</a>\n<a href="/tv/(.*?)" title=".*?" class="section-item posible-progress-bar" .*?>\n<div class="content">\n.*?<div class="channel-icon sprite-channel-(.*?)"></div>\n<span class="section-item-title">\n(.*?)\n(.*?)\n</span>.*?</a>'''
    match = re.findall(regx, kaas, re.DOTALL)
    data = []

    for x in match:
        data.append({"id": x[1], "time": x[2], "title": x[3], "url": x[0]})
    return data


class tvMovies(Screen):
    def __init__(self, session):
        self.session = session
        self.movies = todayMovies()
        sz_w = getDesktop(0).size().width()
        if sz_w > 1800:
            skin = """
                <screen position="center,center" size="1920,1080" title=" " flags="wfNoBorder" >
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/backgroundhd.png" position="0,0" size="1920,1080"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/stars/emptystarshd.png" position="1416,848" size="342,63" zPosition="5"/>
                    <widget name="stars" position="1416,848" size="342,63" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/stars/fullstarshd.png" transparent="1" zPosition="10"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/moviestodayhd.png" position="165,189" size="750,90" zPosition="5"/>
                    <widget name="thumbpic" position="1416,330" size="330,495" zPosition="3"/>
                    <widget name="list" position="135,360" size="1178,436" zPosition="3" transparent="1" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/list/list1178218.png"/>\n
                    <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="3" zPosition="1" font="Regular;36" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="3" zPosition="1" font="Regular;24" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                    <widget name="version" position="165,980" size="660,33" zPosition="3" transparent="1" font="Regular;24" halign="left"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red34.png" position="192,1032" size="34,34" />
                    <widget name="key_red" position="242,1030" size="370,42" zPosition="1" transparent="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/green34.png" position="628,1032" size="34,34" />
                    <widget name="key_green" position="678,1030" size="370,42" zPosition="2" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
                </screen>"""

        else:
            skin = """
                <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder" >
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/background.png" position="0,0" size="1280,720"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/stars/emptystars.png" position="944,565" size="228,42" zPosition="3"/>
                    <widget name="stars" position="944,565" size="228,42" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/stars/fullstars.png" transparent="1" zPosition="10"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/moviestoday.png" position="110,126" size="500,60" zPosition="3"/>
                    <widget name="thumbpic" position="944,220" size="220,330" zPosition="3"/>
                    <widget name="list" position="90,240" size="785,290" zPosition="3" transparent="1" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/list/list785145.png"/>\n
                    <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" shadowColor="black" shadowOffset="-1,-1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                    <widget name="version" position="110,605" size="440,22" zPosition="3" transparent="1" font="Regular;16" halign="left"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red26.png" position="145,643" size="26,26"/>
                    <widget name="key_red" position="185,643" size="220,28" zPosition="3" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/> 
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/green26.png" position="420,643" size="26,26"/>
                    <widget name="key_green" position="460,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" borderColor="black" borderWidth="3" halign="left"/>
                </screen>"""

        Screen.__init__(self, session)
        if shadowAdd():
            skin = skin.replace("""borderColor="black" borderWidth="1" ""","")
        self.skin = skin
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("PlotInfo"))
        self["version"] = Label(_("Version 12.6 Created by Caught"))
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self.PicLoadPerformance = ePicLoad()
        self.currentList = 'list'
        self.picPath = "/tmp/TVMovies/"+self.movies[0]["cover"][-14:].replace('rs/', '')
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self["thumbpic"] = Pixmap()
        self.PicLoad.PictureData.get().append(self.DecodePicture1)
        self.onLayoutFinish.append(self.ShowPicture1)
        self["stars"] = ProgressBar()
        self["list"] = MenuList([], True, eListboxPythonMultiContent)
        self.currentList = 'list'
        self.visible = 0
        self["actions"] = ActionMap(['OkCancelActions',
                                     'ShortcutActions',
                                     'WizardActions',
                                     'SetupActions',
                                     'NumberActions',
                                     'MenuActions',
                                     'HelpActions'],
                                    {"ok": self.go, "down": self.down, "up": self.up, "left": self.left,
                                     "right": self.right, "cancel": self.cancel, "red": self.exit, "green": self.go},
                                    -1)
        self.fillmylist()
        self.onLayoutFinish.append(self.fillmylist)

    def fillmylist(self):
        scalingskins = {"itemheight": 145, "setFont": 24, "setsize": [785, 145]}
        sz_w = getDesktop(0).size().width()
        if sz_w > 1800:
            scalingskins = {"itemheight": 218, "setFont": 36, "setsize": [1178, 218]}
        self["list"].l.setItemHeight(scalingskins["itemheight"])
        self['list'].l.setFont(0, gFont("Regular", scalingskins["setFont"]))
        events = []

        for movie in self.movies:
            balk = "  %s\n    %s %s    (%s)\n    %s\n    %s - %s Zender: %s   IMDB: %s\n" % (
            transhtml(movie["titel"]), movie["type"], movie["land"], movie["jaar"], movie["acteurs"], movie["begin"],
            movie["einde"], transhtml(movie["zender"]), movie["score"])

            res = []
            res.append(
                MultiContentEntryText(pos=(0, 5), size=(10, 25), font=0, flags=RT_HALIGN_LEFT, text="",
                                      color=0x00000000, color_sel=0x00000000))
            res.append(
                MultiContentEntryText(pos=(2, 0), size=(scalingskins["setsize"][0], scalingskins["setsize"][1]), font=0,
                                      flags=RT_HALIGN_LEFT, text=balk, color=0x00D2D226, color_sel=0x00D2D226))
            events.append(res)

        self["list"].l.setList(events)
        self["list"].show()

    def DecodePicture1(self, PicInfo=""):
        if self.picPath is not None:
            ptr = self.PicLoad.getData()
            self["thumbpic"].instance.setPixmap(ptr)

    def ShowPicture1(self):
        self["stars"].setValue(int(10 * (float(self.movies[0]["score"]))))
        if self.picPath is not None:
            self.PicLoad.setPara([
                self["thumbpic"].instance.size().width(),
                self["thumbpic"].instance.size().height(),
                self.Scale[0],
                self.Scale[1],
                0,
                1,
                "#0x000000"])
            self.PicLoad.startDecode(self.picPath)

    def up(self):
        self[self.currentList].up()
        self.updateCover()

    def down(self):
        self[self.currentList].down()
        self.updateCover()

    def left(self):
        self[self.currentList].pageUp()
        self.updateCover()

    def right(self):
        self[self.currentList].pageDown()
        self.updateCover()

    def go(self):
        global movinfo
        movinfo = self.movies[self['list'].l.getCurrentSelectionIndex()]
        self.session.open(beschrijving)

    def updateCover(self):
        selected = self['list'].l.getCurrentSelectionIndex()
        self["stars"].setValue(int(10 * (float(self.movies[selected]["score"]))))
        dir = "/tmp/TVMovies/"
        if not os.path.exists(dir + self.movies[selected]["cover"][-14:].replace('rs/', '')):
            urlretrieve(self.movies[selected]["cover"], dir + self.movies[selected]["cover"][-14:].replace('rs/', ''))
        self.picPath = "/tmp/TVMovies/" + self.movies[selected]["cover"][-14:].replace('rs/', '')
        self.PicLoad.startDecode(self.picPath)

    def exit(self):
        self.close()

    def cancel(self):
        self.close(None)


class beschrijving(Screen):
    def __init__(self, session, args=None):
        self.session = session
        sz_w = getDesktop(0).size().width()
        if sz_w > 1800:
            skin = """
            <screen position="center,center" size="1920,1080" title=" " flags="wfNoBorder" > 
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/backgroundhd.png" position="0,0" size="1920,1080"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/stars/emptystarshd.png" position="1446,774" size="342,63" zPosition="3"/>
                <widget name="infothumb" position="1446,255" size="330,495" zPosition="3"/>
                <widget name="titelinfo" position="150,90" size="1500,63" valign="center" halign="left" zPosition="11" font="Regular;54" borderColor="black" borderWidth="1" transparent="1"/>
                <widget name="actinfo" position="150,180" size="1200,84" valign="center" halign="left" zPosition="11" font="Regular;36" borderColor="black" borderWidth="1" transparent="1"/>
                <widget name="plotinfo" position="150,300" size="1230,585" valign="top" halign="left" zPosition="11" font="Regular;36" borderColor="black" borderWidth="1" transparent="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red34.png" position="192,1032" size="34,34"/>
                <widget name="key_red" position="242,1030" size="370,42" zPosition="1" transparent="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
                <widget name="stars" position="1446,774" size="342,63" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/stars/fullstarshd.png" transparent="1" zPosition="10"/>
            </screen>"""

        else:
            skin = """
            <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder" > 
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/background.png" position="0,0" size="1280,720"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/stars/emptystars.png" position="964,516" size="228,42" zPosition="3"/>
                <widget name="infothumb" position="964,170" size="220,330" zPosition="3"/>
                <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                <widget name="titelinfo" position="100,40" size="1000,42" valign="center" halign="left" zPosition="11" font="Regular;36" borderColor="black" borderWidth="1" transparent="1"/>
                <widget name="actinfo" position="100,100" size="800,56" valign="center" halign="left" zPosition="11" font="Regular;24" borderColor="black" borderWidth="1" transparent="1"/>
                <widget name="plotinfo" position="100,180" size="820,390" valign="top" halign="left" zPosition="11" font="Regular;24" borderColor="black" borderWidth="1" transparent="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red26.png" position="145,643" size="26,26"/>
                <widget name="key_red" position="185,643" size="220,28" zPosition="3" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/> 
                <widget name="stars" position="964,516" size="228,42" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/stars/fullstars.png" transparent="1" zPosition="10"/>
            </screen>"""

        Screen.__init__(self, session)
        if shadowAdd():
            skin = skin.replace("""borderColor="black" borderWidth="1" ""","")
        self.skin = skin
        self["titelinfo"] = Label((transhtml(movinfo["titel"])))
        self["plotinfo"] = Label((transhtml(movinfo["beschrijving"])))
        self["actinfo"] = Label(("Cast\n" + movinfo["acteurs"][4:]))
        self["actions"] = ActionMap(["WizardActions"], {"ok": self.go, "back": self.close}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit}, -1)
        self["key_red"] = Label(_("Exit"))
        self.picPath = "/tmp/TVMovies/" + movinfo["cover"][-14:]
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self["infothumb"] = Pixmap()
        self.PicLoad.PictureData.get().append(self.DecodePicture3)
        self.onLayoutFinish.append(self.ShowPicture3)
        self["stars"] = ProgressBar()

    def DecodePicture3(self, PicInfo=""):
        if self.picPath is not None:
            ptr = self.PicLoad.getData()
            self["infothumb"].instance.setPixmap(ptr)

    def ShowPicture3(self):
        self["stars"].setValue(int(10 * (float(movinfo["score"]))))
        if self.picPath is not None:
            self.PicLoad.setPara([
                self["infothumb"].instance.size().width(),
                self["infothumb"].instance.size().height(),
                self.Scale[0],
                self.Scale[1],
                0,
                1,
                "#0x000000"])
            self.PicLoad.startDecode(self.picPath)

    def go(self):
        self.close(beschrijving)

    def exit(self):
        self.close(beschrijving)


class weatherStartMenu(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w > 1800:
        skin = """
        <screen position="center,center" size="1920,1080" title=" " flags="wfNoBorder" >
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="30,120" size="720,405" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="30,125" size="720,30" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28" borderColor="black" borderWidth="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
            <widget name="list" position="920,110" size="900,198" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/list/list90066.png"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/beflaghd.png" position="794,118" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/nlflaghd.png" position="794,185" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/euflaghd.png" position="794,252" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="on"/>
            <widget name="key_red" position="242,1030" size="370,42" zPosition="1" transparent="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/green34.png" position="628,1032" size="34,34" alphatest="on"/>
            <widget name="key_green" position="678,1030" size="370,42" zPosition="1" transparent="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    else:
        skin = """
        <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder" >
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="85,110" size="417,243" backgroundColor="#ff000000" zPosition="3"/>
            <widget source="session.CurrentService" render="Label" position="85,89" size="417,20" zPosition="1" foregroundColor="white" transparent="1" font="Regular;19" borderColor="black" borderWidth="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
            <widget name="list" position="630,106" size="620,132" zPosition="3" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/list/list62044.png"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/beflagsd.png" position="550,111" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/nlflagsd.png" position="550,154" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/euflagsd.png" position="550,197" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
            <widget name="key_red" position="185,643" size="220,28" zPosition="1" transparent="1" font="Regular;26" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/green26.png" position="420,643" size="26,26" alphatest="on"/>
            <widget name="key_green" position="460,643" size="220,28" zPosition="1" transparent="1" font="Regular;26" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    titleNames = ["Belgie", "Nederland", "Europa"]

    def __init__(self, session, args=None):
        Screen.__init__(self, session)
        if shadowAdd():
            weatherStartMenu.skin = weatherStartMenu.skin.replace("""borderColor="black" borderWidth="1" ""","")
        self.skin = weatherStartMenu.skin
        self.session = session
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Ok"))
        dir = "/tmp/HetWeer/"
        if not os.path.exists(dir):
            os.makedirs(dir)

        self["list"] = MenuList([], True, eListboxPythonMultiContent)
        self.currentList = 'list'
        self.visible = 0
        self["actions"] = ActionMap(['OkCancelActions',
                                     'ShortcutActions',
                                     'WizardActions',
                                     'SetupActions',
                                     'NumberActions',
                                     'MenuActions',
                                     'HelpActions'],
                                    {"ok": self.go, "red": self.exit, "green": self.go, "cancel": self.close}, -1)
        self.fillmylist()
        self.onLayoutFinish.append(self.fillmylist)

    def fillmylist(self):
        scalingskins = {"itemheight": 44, "setFont": 34, "setsize": [620, 44]}
        sz_w = getDesktop(0).size().width()
        if sz_w > 1800:
            scalingskins = {"itemheight": 66, "setFont": 52, "setsize": [900, 66]}
        self["list"].l.setItemHeight(scalingskins["itemheight"])
        self['list'].l.setFont(0, gFont("Regular", scalingskins["setFont"]))
        events = []

        for x in weatherStartMenu.titleNames:
            res = []
            res.append(
                MultiContentEntryText(pos=(0, 8), size=(10, 25), font=0, flags=RT_HALIGN_LEFT))
            res.append(
                MultiContentEntryText(pos=(2, 0), size=(scalingskins["setsize"][0], scalingskins["setsize"][1]), font=0,
                                      flags=RT_HALIGN_LEFT, text=x, color=0x00D2D226, color_sel=0x00D2D226))
            events.append(res)

        self["list"].l.setList(events)
        self["list"].show()

    def go(self):
        global state
        index = self["list"].getSelectedIndex()
        state[0] = weatherStartMenu.titleNames[index]
        if state[0] == "WeerInfo":
            self.session.open(secweatherMenu)
        else:
            self.session.open(secweatherMenu)

    def exit(self):
        self.close()

    def cancel(self):
        self.close(None)


class secweatherMenu(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w > 1800:
        skin = """
        <screen name="secweatherMenu" position="center,center" size="1920,1080" title=" " flags="wfNoBorder">
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="30,120" size="720,405" backgroundColor="#ff000000" zPosition="1"/> 
            <widget source="session.CurrentService" render="Label" position="30,125" size="720,30" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28" borderColor="black" borderWidth="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
            <widget name="list" position="840,110" size="900,660" scrollbarMode="showOnDemand" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/list/list90066.png"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="on"/>
            <widget name="key_red" position="242,1030" size="370,42" zPosition="1" transparent="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/green34.png" position="628,1032" size="34,34" alphatest="on"/>
            <widget name="key_green" position="678,1030" size="370,42" zPosition="1" transparent="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    else:
        skin = """
        <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder" >
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="85,110" size="417,243" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="85,89" size="417,20" zPosition="1" foregroundColor="white" transparent="1" font="Regular;19" borderColor="black" borderWidth="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
            <widget name="list" position="560,106" size="650,440" scrollbarMode="showOnDemand" zPosition="1" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/list/list65044.png"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
            <widget name="key_red" position="185,643" size="220,28" zPosition="1" transparent="1" font="Regular;26" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/green26.png" position="420,643" size="26,26" alphatest="on"/>
            <widget name="key_green" position="460,643" size="220,28" zPosition="1" transparent="1" font="Regular;26" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    listNamesnl = ["Weerbericht", "Temperatuur", "Buienradar", "Motregenradar", "Onweerradar", "Wolkenradar",
                   "Mistradar", "Hagelradar", "Sneeuwradar", "Zonradar", "Zonkracht-UV", "Satelliet"]
    listNamesbe = ["Weerbericht", "Buienradar", "Motregenradar", "Onweerradar", "Wolkenradar", "Hagelradar",
                   "Sneeuwradar", "Zonradar", "Zonkracht-UV", "Satelliet"]
    listNameseu = ["Weerbericht", "Buienradar", "Onweerradar", "Zonkracht-UV", "Satelliet"]

    def __init__(self, session, args=None):
        Screen.__init__(self, session)
        if shadowAdd():
            secweatherMenu.skin = secweatherMenu.skin.replace("""borderColor="black" borderWidth="1" ""","")
        self.skin = secweatherMenu.skin
        self.session = session
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Ok"))
        self.countries = None
        if state[0] == "Belgie":
            self.countries = secweatherMenu.listNamesbe
        elif state[0] == "Nederland":
            self.countries = secweatherMenu.listNamesnl
        elif state[0] == "Europa":
            self.countries = secweatherMenu.listNameseu

        self["list"] = MenuList([], True, eListboxPythonMultiContent)
        self.currentList = 'list'
        self.visible = 0
        self["actions"] = ActionMap(['OkCancelActions',
                                     'ShortcutActions',
                                     'WizardActions',
                                     'SetupActions',
                                     'NumberActions',
                                     'MenuActions',
                                     'HelpActions'],
                                    {"ok": self.go, "red": self.exit, "back": self.close, "green": self.go,
                                     "cancel": self.close}, -1)
        self.fillmylist()
        self.onLayoutFinish.append(self.fillmylist)

    def fillmylist(self):
        scalingskins = {"itemheight": 44, "setFont": 34, "setsize": [620, 44]}
        sz_w = getDesktop(0).size().width()
        if sz_w > 1800:
            scalingskins = {"itemheight": 66, "setFont": 52, "setsize": [900, 66]}
        self["list"].l.setItemHeight(scalingskins["itemheight"])
        self['list'].l.setFont(0, gFont("Regular", scalingskins["setFont"]))
        events = []

        for x in self.countries:
            res = []
            res.append(
                MultiContentEntryText(pos=(0, 8), size=(10, 25), font=0, flags=RT_HALIGN_LEFT))
            res.append(
                MultiContentEntryText(pos=(2, 0), size=(scalingskins["setsize"][0], scalingskins["setsize"][1]), font=0,
                                      flags=RT_HALIGN_LEFT, text=x, color=0x00D2D226, color_sel=0x00D2D226))
            events.append(res)

        self["list"].l.setList(events)
        self["list"].show()

    def go(self):
        sz_w = getDesktop(0).size().width()
        isSD = sz_w <= 1800
        newView = isSD
        newView = True
        type = self.countries[self["list"].getSelectedIndex()]
        tt = time.time()
        tt = round(tt / (5 * 60))
        tt = tt * (5 * 60)
        tt -= (5 * 60)
        aantalfotos = 20
        tijdstap = 5
        locurl = ""
        picturedownloadurl = ""
        loctype = ""

        def openScreenRadar():
            if not type == 'Weerbericht':
                distro = 'unknown'
                try:
                    f = open('/etc/opkg/all-feed.conf', 'r') 
                    oeline = f.readline().strip().lower()
                    f.close()
                    distro = oeline.split()[1].replace('-all', '')
                except:
                    pass

                if distro == 'openpli' or distro == 'openpli' or distro == 'openrsi':
                    self.session.open(radarScreenop)
                else:
                    self.session.open(radarScreenoatv)

        global typename
        global wchat
        global legend
        typename = type
        legend = True
        try:
            if state[0] == "Belgie" and newView:
                if type == "Weerbericht":
                    wchat = weatherchat("be/Belgie/weerbericht")
                    self.session.open(weathertalk)
                elif type == "Buienradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/radarmapbe/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550',
                        '/tmp/HetWeer/00.png')
                elif type == "Motregenradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/drizzlemapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550',
                        '/tmp/HetWeer/00.png')
                elif type == "Wolkenradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/cloudmapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550',
                        '/tmp/HetWeer/00.png')
                elif type == "Zonradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/sunmapnl/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550',
                        '/tmp/HetWeer/00.png')
                    legend = False
                elif type == "Onweerradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/lightningnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550',
                        '/tmp/HetWeer/00.png')
                elif type == "Hagelradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/hailnl/?ext=png&l=2&hist=10&forc=1&step=0&w=550&h=512',
                        '/tmp/HetWeer/00.png')
                elif type == "Sneeuwradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/snowmapnl/?ext=png&l=2&hist=10&forc=1&step=0&w=550&h=512',
                        '/tmp/HetWeer/00.png')
                elif type == "Satelliet":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/satvisual2/?ext=png&l=2&hist=10&forc=0&step=0&w=550&h=512',
                        '/tmp/HetWeer/00.png')
                    legend = False
                elif type == "Zonkracht-UV":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/sunpowereu/?ext=png&l=2&hist=0&forc=30&step=0&w=550&h=512',
                        '/tmp/HetWeer/00.png')
                    legend = False
                if not type == "Weerbericht":
                    openScreenRadar()

            elif state[0] == "Nederland" and newView:
                if type == "Weerbericht":
                    wchat = weatherchat("nl/Nederland/weerbericht")
                    self.session.open(weathertalk)
                elif type == "Temperatuur":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/weathermapnl/?ext=png&l=2&hist=12&forc=1&step=0&type=temperatuur&w=550&h=512',
                        '/tmp/HetWeer/00.png')
                    legend = False
                elif type == "Buienradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/radarmapnl/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550',
                        '/tmp/HetWeer/00.png')
                elif type == "Motregenradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/drizzlemapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550',
                        '/tmp/HetWeer/00.png')
                elif type == "Wolkenradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/cloudmapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550',
                        '/tmp/HetWeer/00.png')
                elif type == "Sneeuwradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/snowmapnl/?ext=png&l=2&hist=10&forc=1&step=0&w=550&h=512',
                        '/tmp/HetWeer/00.png')
                elif type == "Mistradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/weathermapnl/?type=zicht&ext=png&l=2&hist=9&forc=1&step=0&w=550&h=512',
                        '/tmp/HetWeer/00.png')
                    legend = False
                elif type == "Zonradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/sunmapnl/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550',
                        '/tmp/HetWeer/00.png')
                    legend = False
                elif type == "Onweerradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/lightningnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550',
                        '/tmp/HetWeer/00.png')
                elif type == "Hagelradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/hailnl/?ext=png&l=2&hist=10&forc=1&step=0&w=550&h=512',
                        '/tmp/HetWeer/00.png')
                elif type == "Satelliet":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/satvisual2/?ext=png&l=2&hist=10&forc=0&step=0&w=550&h=512',
                        '/tmp/HetWeer/00.png')
                    legend = False
                elif type == "Zonkracht-UV":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/sunpowereu/?ext=png&l=2&hist=0&forc=30&step=0&w=550&h=512',
                        '/tmp/HetWeer/00.png')
                    legend = False
                if not type == "Weerbericht":
                    openScreenRadar()

            elif state[0] == "Europa" and newView:
                if type == "Weerbericht":
                    wchat = weatherchat("be/wereldwijd/europa")
                    self.session.open(weathertalk)
                elif type == "Buienradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/radarmapeu/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550',
                        '/tmp/HetWeer/00.png')
                elif type == "Onweerradar":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/radarcloudseu/?ext=png&l=2&hist=30&forc=0&step=0&h=512&w=550',
                        '/tmp/HetWeer/00.png')
                elif type == "Satelliet":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/satvisual2/?ext=png&l=2&hist=10&forc=1&step=0&type=eu&w=550&h=512',
                        '/tmp/HetWeer/00.png')
                    legend = False
                elif type == "Zonkracht-UV":
                    urllib.urlretrieve(
                        'http://api.buienradar.nl/image/1.0/sunpowereu/?ext=png&l=2&hist=0&forc=30&step=0&w=550&h=512',
                        '/tmp/HetWeer/00.png')
                    legend = False
                if not type == "Weerbericht":
                    openScreenRadar()

            if not newView:
                picturedownloadurl = "http://api.buienradar.nl/image/1.0/" + loctype
                for x in range(0, aantalfotos):
                    turl = time.strftime("20%y%m%d%H%M", time.localtime(tt))
                    dir = "/tmp/HetWeer/%02d.png" % (aantalfotos - (x + 1))
                    tt += tijdstap * 60
                    urllib.urlretrieve(picturedownloadurl + turl, dir)

                if os.path.exists('/tmp/HetWeer/00.png'):
                    try:
                        self.session.open(aantalfotos)
                    except:
                        return
                else:
                    print '00.png doenst exists, go back!'
                    return
        except:
            (None)

    def cancel(self):
        self.close(None)

    def exit(self):
        self.close(secweatherMenu)


class weathertalk(Screen):
    def __init__(self, session, args=None):
        self.session = session
        sz_w = getDesktop(0).size().width()
        if sz_w > 1800:
            skin = """
            <screen position="center,center" size="1920,1080" title=" " flags="wfNoBorder" >
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/backgroundhd.png" position="0,0" size="1920,1080"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                <widget name="PAG" position="1780,940" size="104,52" valign="top" halign="left" zPosition="11" font="Regular;46" borderColor="black" borderWidth="1" transparent="1"/>
                <widget name="weerchat" position="150,150" size="1620,782" zPosition="11" font="Regular;46" borderColor="black" borderWidth="1" transparent="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="on"/>
                <widget name="key_red" position="242,1030" size="370,42" zPosition="1" transparent="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
            </screen>"""

        else:
            skin = """
            <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder" >
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/background.png" position="0,0" size="1280,720"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                <widget name="PAG" position="1180,580" size="72,36" valign="top" halign="left" zPosition="11" font="Regular;32" borderColor="black" borderWidth="1" transparent="1"/>
                <widget name="weerchat" position="100,100" size="1100,500" valign="top" halign="left" zPosition="11" font="Regular;32" borderColor="black" borderWidth="1" transparent="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
                <widget name="key_red" position="185,643" size="220,28" zPosition="3" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
            </screen>"""

        Screen.__init__(self, session)
        if shadowAdd():
            skin = skin.replace("""borderColor="black" borderWidth="1" ""","")
        self.skin = skin
        global wchat
        self.indexpage = 0
        list = []
        regx = '''<p.*?>(.*?)</p>'''
        match = re.findall(regx, wchat, re.DOTALL)
        self.wchattext = match
        try:
            self["weerchat"] = Label(transhtml(match[self.indexpage]))
        except:
            self["weerchat"] = Label(_("regx aanpassen"))
        self["PAG"] = Label(("1/" + str(len(self.wchattext))))

        self["actions"] = ActionMap(["WizardActions"], {"left": self.left, "right": self.right, "back": self.close}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit}, -1)
        self["key_red"] = Label(_("Exit"))

    def left(self):
        if self.indexpage <= 0:
            self.indexpage = 0
        else:
            self.indexpage = self.indexpage - 1
        self["weerchat"].setText(transhtml(self.wchattext[self.indexpage]))
        self["PAG"].setText(str(self.indexpage + 1) + "/" + str(len(self.wchattext)))

    def right(self):
        if self.indexpage >= len(self.wchattext) - 1:
            self.indexpage = len(self.wchattext) - 1
        else:
            self.indexpage = self.indexpage + 1
        self["weerchat"].setText(transhtml(self.wchattext[self.indexpage]))
        self["PAG"].setText(str(self.indexpage + 1) + "/" + str(len(self.wchattext)))

    def exit(self):
        self.close(weathertalk)


class radarScreenoatv(Screen):
    def __init__(self, session):
        global pos
        self['radarname'] = Label(typename)
        self.weerpng = '/tmp/HetWeer/00.png'

        sz_w = getDesktop(0).size().width()
        legendinfo = ''
        if sz_w > 1800:
            if legend:
                legendinfo = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/legende.png" zPosition="6" position="705,545" size="270,333" alphatest="on"/>"""
            skin = """
            <screen position="center,center" size="1920,1080" title=" " flags="wfNoBorder" >
            <widget name="picd" position="685,284" size="39600,900" pixmap="/tmp/HetWeer/00.png" zPosition="1" alphatest="on"/>""" + legendinfo + """
            <widget name="radarname" position="center,290" size="550,64" zPosition="7" halign="center" transparent="1" font="Regular;30"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/framehdatv.png" zPosition="6" position="center,center" size="1920,1080" alphatest="on"/>
            </screen>"""

        else:
            if legend:
                legendinfo = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/legendehd.png" zPosition="6" position="370,222" size="270,333" alphatest="on"/>"""
            skin = """
            <screen position="center,center" size="1280,720" title=" " flags="wfNoBorder" >
            <widget name="picd" position="365,86" size="19800,512" pixmap="/tmp/HetWeer/00.png" zPosition="1" alphatest="on"/>""" + legendinfo + """
            <widget name="radarname" position="center,94" size="550,64" zPosition="6" halign="center" transparent="1" font="Regular;30"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/framesdatv.png" zPosition="6" position="0,80" size="1280,523" alphatest="on"/>
            </screen>"""

        self.session = session
        if shadowAdd():
            skin = skin.replace("""borderColor="black" borderWidth="1" ""","")
        self.skin = skin
        Screen.__init__(self, session)
        self.slidePicTimer = eTimer()
        self.slidePicTimer.callback.append(self.updatePic)
        self['picd'] = MovingPixmap()
        pos = 0
        self.slidePicTimer.start(750)
        self['actions'] = ActionMap(['WizardActions'], {'back': self.close}, -1)

    def updatePic(self):
        global pos
        if sz_w > 1800:
            self['picd'].moveTo((pos * -550) + 685, 284, 1)
        else:
            global picadjust
            postt = (pos * -550) + 365
            if postt < -8000:
                pos = 0
            self['picd'].moveTo((pos * -550) + 365, 86, 1)
        pos += 1
        try:
            if pos >= get_image_info('/tmp/HetWeer/00.png')[0] / 550:
                pos = 0
        except:
            None

        self['picd'].startMoving()


class radarScreenop(Screen):
    def __init__(self, session):
        global typename
        self["radarname"] = Label(typename)
        self.weerpng = "/tmp/HetWeer/00.png"
        picformat = None
        try:
            picformat = get_image_info("/tmp/HetWeer/00.png")
        except:
            None
        if not picformat:
            self.weerpng = "/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/busy.png"
            picformat = get_image_info(self.weerpng)
        self.scaler = 1.25
        sz_w = getDesktop(0).size().width()
        global legend
        legendinfo = ""
        if sz_w > 1800:
            self.scaler = 2.0
        if sz_w > 1800:
            if legend:
                legendinfo = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/legendehd.png" zPosition="6" position="460,630" size="270,333" alphatest="on"/>"""
            skin = """
            <screen position="fill" size=\"""" + str(int(550 * self.scaler - 16)) + """,""" + str(
                int(512 * self.scaler)) + """">
            <widget name="picd" position="400,28" size=\"""" + str(int(picformat[0] * self.scaler)) + """,""" + str(
                int(picformat[1] * self.scaler)) + """" zPosition="5" alphatest="on"/>""" + legendinfo + """
            <widget name="radarname" position="center,50" size="600,72" zPosition="6" halign="center" transparent="1" font="Regular;60" borderColor="black" borderWidth="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/borders/framehdop.png" zPosition="6" position="center,center" size="1920,1080" alphatest="on"/>
            </screen>"""

        else:
            if legend:
                legendinfo = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux/Images/main/legende.png" zPosition="6" position="326,390" size="180,222" alphatest="on"/>"""
            skin = """
            <screen position="fill" size=\"""" + str(int(370 * self.scaler - 16)) + """,""" + str(
                int(512 * self.scaler)) + """">
            <widget name="picd" position="305,36" size=\"""" + str(int(picformat[0] * self.scaler)) + """,""" + str(
                int(picformat[1] * self.scaler)) + """" zPosition="5" alphatest="on"/>""" + legendinfo + """
            <widget name="radarname" position="center,56" size="400,52" zPosition="6" halign="center" transparent="1" font="Regular;40" borderColor="black" borderWidth="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MenuLux//Extensions/MenuLux/Images/borders/framesdop.png" zPosition="6" position="center,center" size="1280,650" alphatest="on"/>
            </screen>"""

        self.session = session
        if shadowAdd():
            skin = skin.replace("""borderColor="black" borderWidth="1" ""","")
        self.skin = skin
        Screen.__init__(self, session)
        self.slidePicTimer = eTimer()
        self.slidePicTimer.callback.append(self.updatePic)
        self["picd"] = MovingPixmap()
        global pos
        pos = 0
        self.Scale = AVSwitch().getFramebufferScale()
        self.slidePicTimer.start(750)
        self["actions"] = ActionMap(["WizardActions"], {"back": self.close}, -1)
        self.PicLoad = ePicLoad()
        self.PicLoadPerformance = ePicLoad()
        self.picPath = self.weerpng
        self.PicLoad.PictureData.get().append(self.DecodePicture1)
        self.onLayoutFinish.append(self.ShowPicture1)
        self.PicLoad.startDecode(self.picPath)

    def DecodePicture1(self, PicInfo=""):
        if self.picPath is not None:
            ptr = self.PicLoad.getData()
            self["picd"].instance.setPixmap(ptr)

    def ShowPicture1(self):
        if self.picPath is not None:
            self.PicLoad.setPara([
                self["picd"].instance.size().width(),
                self["picd"].instance.size().height(),
                self.Scale[0],
                self.Scale[1],
                0,
                1,
                "#0x000000"])
            self.PicLoad.startDecode(self.picPath)

    def updatePic(self):
        global pos
        if sz_w > 1800:
            self["picd"].moveTo((pos * (-550 * self.scaler) - 15 + 415), 28, 1)

        else:
            global picadjust
            postt = (pos * -687.5)
            if postt < -8000:
                pos = 0
            self['picd'].moveTo((pos * (-550 * self.scaler)) + 300, 36, 1)
        pos += 1
        try:
            if pos >= get_image_info('/tmp/HetWeer/00.png')[0] / (550 * self.scaler):
                pos = 0
        except:
            None
        self['picd'].startMoving()


class errorScreen(Screen):
    skin = """
        <screen position="10,10" size="200,200" title="Weather Info" >
            <widget name="favor" position="1,1" size="1085,55" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="left"/>
        </screen>"""

    def __init__(self, session, args=None):
        self.session = session
        self.skin = errorScreen.skin
        global displayErrorMsg
        self["favor"] = Label((displayErrorMsg))
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['WizardActions'], {'back': self.close}, -1)


def main(session, **kwargs):
    try:
        response = urllib2.urlopen("http://claudck193.193.axc.nl/teller/index.php", None, 1.0)
        response.close()
    except urllib2.HTTPError as e:
        print
        'The server couldn\'t fulfill the request.'
    except urllib2.URLError as e:
        print
        'We failed to reach a server.'
    if checkInternet():
        session.open(buttonmenuscreen)
    else:
        session.open(MessageBox, _("Geen internet"), MessageBox.TYPE_INFO)


def Plugins(path, **kwargs):
    global plugin_path
    plugin_path = path
    return PluginDescriptor(name=_('LuxSat Utilities Menu'), description='Messages, Keys and other Utilities',
                            icon='Images/menu.png',
                            where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], fnc=main)