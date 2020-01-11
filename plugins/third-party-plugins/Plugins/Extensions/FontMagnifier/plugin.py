#
# Font magnifier-Plugin
# by BigReaper
#
fm_version="0.5.2"
# (0.5.2b)

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Components.config import config, ConfigSubsection, ConfigEnableDisable, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.config import config, getConfigListEntry, ConfigText
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.Label import Label
from Components.MenuList import MenuList
from Screens.MessageBox import MessageBox
from enigma import eTimer
from __init__ import _
import Screens.Standby
import gettext
import os
import xml.etree.cElementTree

fm_plugindir="/usr/lib/enigma2/python/Plugins/Extensions/FontMagnifier"
fm_pypath="/usr/lib/enigma2/python"
standard_pypath="/usr/lib/python2.5"

config.plugins.fm = ConfigSubsection()
config.plugins.fm.display_manipulation_active = ConfigEnableDisable(default = False)
config.plugins.fm.active = ConfigEnableDisable(default = False)
config.plugins.fm.display_subtitles = ConfigEnableDisable(default = False)
config.plugins.fm.fontsize = ConfigInteger(default = 80, limits = (40,90))
config.plugins.fm.evv_fontsize = ConfigInteger(default = 22, limits = (10,50))                      #1
config.plugins.fm.show_only_clock = ConfigEnableDisable(default = False)
config.plugins.fm.single_epg_description_fontsize = ConfigInteger(default = 20, limits = (10,40))   #2
config.plugins.fm.single_epg_list_fontsize = ConfigInteger(default = 25, limits = (10,40))          #3
config.plugins.fm.single_epg_list_fontsize2 = ConfigInteger(default = 25, limits = (10,40))         #3.1
config.plugins.fm.channel_list_epg_description_fontsize = ConfigInteger(default = 20, limits = (10,40))    #4
config.plugins.fm.channel_list_fontsize = ConfigInteger(default = 20, limits = (10,40))             #5
config.plugins.fm.Subtitle_TTX = ConfigInteger(default = 40, limits = (20,80))                      #6
config.plugins.fm.Subtitle_Regular = ConfigInteger(default = 40, limits = (20,80))                  #7
config.plugins.fm.Subtitle_Bold = ConfigInteger(default = 40, limits = (20,80))                     #8
config.plugins.fm.Subtitle_Italic = ConfigInteger(default = 40, limits = (20,80))                   #9
config.plugins.fm.movie_list_fontsize = ConfigInteger(default = 20, limits = (10,40))               #10
config.plugins.fm.infobar_fontsize_event_now = ConfigInteger(default = 22, limits = (10,30))        #11
config.plugins.fm.infobar_fontsize_event_next = ConfigInteger(default = 22, limits = (10,30))       #12

def Plugins(**kwargs):
    return [PluginDescriptor(name=_("FontMagnifier"), description=_("Tool to change easily font sizes."), where = PluginDescriptor.WHERE_PLUGINMENU, icon="fm.png", fnc=main)]

def main(session, **kwargs):
        # print "[fm] Open Config Screen"
        session.open(fmConfiguration)

class fmConfiguration(Screen, ConfigListScreen):
    skin = """
        <screen name="FontMagnifierConfigScreen" position="center,center" size="560,425" title="Font Magnifier V%s">
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/key_info.png" position="520,0" size="140,40" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/key_menu.png" position="470,0" size="140,40" alphatest="on" />
            <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
            <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
            <widget name="config" position="5,50" size="550,385" scrollbarMode="showOnDemand" zPosition="1"/>
        </screen>""" % fm_version

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)

        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))
        self["setupActions"] = ActionMap(["EPGSelectActions", "SetupActions", "ColorActions", "MenuActions", "DirectionActions"],
        {
            "green": self.save,
            "red": self.cancel,
            "save": self.save,
            "cancel": self.cancel,
            "ok": self.save,
            "info": self.info,
            "menu": self.handle_menukey,
        })

        self.list = []
        ConfigListScreen.__init__(self, self.list, session=session)
        self.tree = xml.etree.cElementTree.parse("/usr/share/enigma2/%s" % (config.skin.primary_skin.value))
        self.root = self.tree.getroot()
        self.list_of_screens = self.root.findall("screen")
        self.list_of_subtitles = self.root.findall("subtitles")

        self.getcurrent_font_epg_description()                  # 1
        self.getcurrent_font_single_epg_description()           #2
        self.getcurrent_font_single_epg_service_list()          #3
        self.getcurrent_font_epg_descr_channel_list()           #4
        self.getcurrent_font_channel_list()                     #5
        self.getcurrent_font_subtitles()                        #6, 7, 8, 9
        self.getcurrent_font_movie_list()                       #10
        self.getcurrent_font_infobar_event_now ()               #11
        self.getcurrent_font_infobar_event_next ()              #12
        self.createSetup()

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.createSetup()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.createSetup()

    # Einfache Sendungsinfo (#1)
    def getcurrent_font_epg_description(self):
        tag_gefunden=0
        for element in self.list_of_screens: # Schleife 1
            if element.keys():
                for name, value in element.items(): # Schleife 2
                    if name == "name" and value == "EventView":
                        if element.getchildren():
                            for child in element: # Schleife 3
                                if child.get("name") == "epg_description":
                                    epg_description_font = child.get("font")
                                    font_elements = epg_description_font.split(";")
                                    if len(font_elements)==2:
                                        config.plugins.fm.evv_fontsize.value = int(font_elements[1])
                                        tag_gefunden=1
                                        break # Schleife 3
                            if tag_gefunden==1:
                                break; # Schleife 2
                if tag_gefunden==1:
                    break;  # Schleife 1

    #  Einfach-EPG Sendungsinfo (#2)
    def getcurrent_font_single_epg_description(self):
        tag_gefunden=0
        for element in self.list_of_screens: # Schleife 1
            if element.keys():
                for name, value in element.items(): # Schleife 2
                    if name == "name" and value == "EPGSelection":
                        if element.getchildren():
                            for child in element: # Schleife 3
                                if child.getchildren():
                                    for sub_child in child: # Schleife 4
                                        if sub_child.tag == "convert":
                                            if sub_child.text == "ExtendedDescription":
                                                tag_gefunden=1
                                                break # Schleife 4
                                    if tag_gefunden == 1:
                                        epg_description_font = child.get("font")
                                        font_elements = epg_description_font.split(";")
                                        if len(font_elements)==2:
                                            config.plugins.fm.single_epg_description_fontsize.value = int(font_elements[1])
                                        break # Schleife 3
                            if tag_gefunden==1:
                                break # Schleife 2
                if tag_gefunden==1:
                    break # Schleife 1

    # Einfach-EPG Tagesprogrammliste (#3, #3.1)
    def getcurrent_font_single_epg_service_list(self):
        try:
            config.plugins.fm.single_epg_list_fontsize.value = 0
            config.plugins.fm.single_epg_list_fontsize2.value = 0
            EpgList_file = open("/usr/lib/enigma2/python/Components/EpgList.py", "r")
            anzahl_der_gefundenen_schriften = 0
            for zeile in EpgList_file:
                if zeile.find("\t\tself.l.setFont(0") is not -1:
                    function_arguments = zeile.split(",")
                    if len(function_arguments) == 3:
                        font_size_argument = function_arguments[2]
                        font_size = font_size_argument.split(")")
                        if len(font_size) == 3:
                            config.plugins.fm.single_epg_list_fontsize.value = int(font_size[0])
                            anzahl_der_gefundenen_schriften += 1
                elif zeile.find("\t\tself.l.setFont(1") is not -1:
                    function_arguments = zeile.split(",")
                    if len(function_arguments) == 3:
                        font_size_argument = function_arguments[2]
                        font_size = font_size_argument.split(")")
                        if len(font_size) == 3:
                            config.plugins.fm.single_epg_list_fontsize2.value = int(font_size[0])
                            anzahl_der_gefundenen_schriften += 1
                if anzahl_der_gefundenen_schriften == 2:
                    break;
            EpgList_file.close()
        except:
            config.plugins.fm.single_epg_list_fontsize.value = 0
            config.plugins.fm.single_epg_list_fontsize2.value = 0

    # Kanalliste, Sendungsinfo (#4)
    def getcurrent_font_epg_descr_channel_list(self):
        try:
            tag_gefunden=0
            config.plugins.fm.channel_list_epg_description_fontsize.value=0
            for element in self.list_of_screens: # Schleife 1
                if element.keys():
                    for name, value in element.items(): # Schleife 2
                        if name == "name" and value == "ChannelSelection":
                            if element.getchildren():
                                for child in element: # Schleife 3
                                    if child.getchildren():
                                        for sub_child in child: # Schleife 4
                                            if sub_child.tag == "convert":
                                                if sub_child.text == "ExtendedDescription":
                                                    tag_gefunden=1
                                                    break # Schleife 4
                                        if tag_gefunden == 1:
                                            epg_description_font = child.get("font")
                                            font_elements = epg_description_font.split(";")
                                            if len(font_elements) == 2:
                                                config.plugins.fm.channel_list_epg_description_fontsize.value = int(font_elements[1])
                                            break # Schleife 3
                                if tag_gefunden == 1:
                                    break # Schleife 2
                    if tag_gefunden == 1:
                        break # Schleife 1
        except:
            config.plugins.fm.channel_list_epg_description_fontsize.value = 0

    #  Kanalliste (#5)
    def getcurrent_font_channel_list(self):
        try:
            tag_gefunden=0
            for element in self.list_of_screens: # Schleife 1
                if element.keys():
                    for name, value in element.items(): # Schleife 2
                        if name == "name" and value == "ChannelSelection":
                            if element.getchildren():
                                for child in element: # Schleife 3
                                    if child.get("name") == "list":
                                        epg_description_font = child.get("serviceNameFont")
                                        font_elements = epg_description_font.split(";")
                                        if len(font_elements)==2:
                                            config.plugins.fm.channel_list_fontsize.value = int(font_elements[1])
                                            tag_gefunden=1
                                            break # Schleife 3
                                if tag_gefunden==1:
                                    break # Schleife 2
                    if tag_gefunden==1:
                        break # Schleife 1
        except:
            config.plugins.fm.channel_list_fontsize.value = 0

    # subtitles (#6,7,8,9)
    def getcurrent_font_subtitles(self):
        config.plugins.fm.Subtitle_TTX.value = 0
        config.plugins.fm.Subtitle_Regular.value = 0
        config.plugins.fm.Subtitle_Bold.value = 0
        config.plugins.fm.Subtitle_Italic.value = 0
        if len (self.list_of_subtitles) != 0:
            for element in self.list_of_subtitles: # Schleife 1
                if element.getchildren():
                    for child in element: # Schleife 2
                        if child.get("name") == "Subtitle_TTX":
                            font = child.get("font")
                            font_elements = font.split(";")
                            if len(font_elements)==2:
                                config.plugins.fm.Subtitle_TTX.value = int(font_elements[1])
                        elif child.get("name") == "Subtitle_Regular":
                            font = child.get("font")
                            font_elements = font.split(";")
                            if len(font_elements)==2:
                                config.plugins.fm.Subtitle_Regular.value = int(font_elements[1])
                        elif child.get("name") == "Subtitle_Bold":
                            font = child.get("font")
                            font_elements = font.split(";")
                            if len(font_elements)==2:
                                config.plugins.fm.Subtitle_Bold.value = int(font_elements[1])
                        elif child.get("name") == "Subtitle_Italic":
                            font = child.get("font")
                            font_elements = font.split(";")
                            if len(font_elements)==2:
                                config.plugins.fm.Subtitle_Italic.value = int(font_elements[1])

    # movielist (#10)
    def getcurrent_font_movie_list(self):
        try:
            config.plugins.fm.movie_list_fontsize.value = 0
            MovieList_file = open("/usr/lib/enigma2/python/Components/MovieList.py", "r")
            for zeile in MovieList_file:
                if zeile.find("\t\t\tself.l.setFont(0") is not -1:
                    function_arguments = zeile.split(",")
                    if len(function_arguments) == 3:
                        font_size_argument = function_arguments[2]
                        font_size = font_size_argument.split(")")
                        if len(font_size) == 3:
                            config.plugins.fm.movie_list_fontsize.value = int(font_size[0])
                            break
            MovieList_file.close()
        except:
            config.plugins.fm.movie_list_fontsize.value = 0

    # infobar event now (#11)
    def getcurrent_font_infobar_event_now(self):
        config.plugins.fm.infobar_fontsize_event_now.value=0
        tag_gefunden=0
        for element in self.list_of_screens: # Schleife 1
            if element.keys():
                for name, value in element.items(): # Schleife 2
                    if name == "name" and value == "InfoBar":
                        if element.getchildren():
                            for child in element: # Schleife 3
                                if child.get("source") == "session.Event_Now":
                                    if child.getchildren():
                                        for sub_child in child: # Schleife 4
                                            if sub_child.tag == "convert":
                                                if sub_child.text == "Name":
                                                    tag_gefunden=1
                                                    break # Schleife 4
                                        if tag_gefunden == 1:
                                            infobar_font = child.get("font")
                                            font_elements = infobar_font.split(";")
                                            if len(font_elements) == 2:
                                                config.plugins.fm.infobar_fontsize_event_now.value = int(font_elements[1])
                                            break # Schleife 3
                                if tag_gefunden == 1:
                                    break # Schleife 2
                    if tag_gefunden == 1:
                        break # Schleife 1

    # infobar event next (#12)
    def getcurrent_font_infobar_event_next(self):
        config.plugins.fm.infobar_fontsize_event_next.value=0
        tag_gefunden=0
        for element in self.list_of_screens: # Schleife 1
            if element.keys():
                for name, value in element.items(): # Schleife 2
                    if name == "name" and value == "InfoBar":
                        if element.getchildren():
                            for child in element: # Schleife 3
                                if child.get("source") == "session.Event_Next":
                                    if child.getchildren():
                                        for sub_child in child: # Schleife 4
                                            if sub_child.tag == "convert":
                                                if sub_child.text == "Name":
                                                    tag_gefunden=1
                                                    break # Schleife 4
                                        if tag_gefunden == 1:
                                            infobar_font = child.get("font")
                                            font_elements = infobar_font.split(";")
                                            if len(font_elements) == 2:
                                                config.plugins.fm.infobar_fontsize_event_next.value = int(font_elements[1])
                                            break # Schleife 3
                                if tag_gefunden == 1:
                                    break # Schleife 2
                    if tag_gefunden == 1:
                        break # Schleife 1

    def createSetup(self):
        self.list = []
        # display manipulation
        self.list.append(getConfigListEntry(_("Enable display options"), config.plugins.fm.display_manipulation_active))
        if config.plugins.fm.display_manipulation_active.value:
            if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/ExtendedServiceInfo"):
                self.list.append(getConfigListEntry(_("Enable service number in display"), config.plugins.fm.active))
            if config.plugins.fm.active.value:
                self.list.append(getConfigListEntry(_("Enter service number font size in pixel"), config.plugins.fm.fontsize))
            self.list.append(getConfigListEntry(_("Show only time in display when box is in standby"), config.plugins.fm.show_only_clock))

        self.list.append(getConfigListEntry(_("Enter font size for epg description in pixel"), config.plugins.fm.evv_fontsize))
        self.list.append(getConfigListEntry(_("Enter font size for epg description in single epg"), config.plugins.fm.single_epg_description_fontsize))
        if config.plugins.fm.single_epg_list_fontsize.value != 0:
            self.list.append(getConfigListEntry(_("Enter font size for channel list in single epg"), config.plugins.fm.single_epg_list_fontsize))
        if config.plugins.fm.single_epg_list_fontsize2.value != 0:
            self.list.append(getConfigListEntry(_("Enter font size for date/time in multi epg"), config.plugins.fm.single_epg_list_fontsize2))
        if config.plugins.fm.channel_list_epg_description_fontsize.value != 0:
            self.list.append(getConfigListEntry(_("Font size for epg description in channel list"), config.plugins.fm.channel_list_epg_description_fontsize))
        if config.plugins.fm.channel_list_fontsize.value != 0:
            self.list.append(getConfigListEntry(_("Font size for channel list"), config.plugins.fm.channel_list_fontsize))
        if config.plugins.fm.movie_list_fontsize.value != 0:
            self.list.append(getConfigListEntry(_("Font size for movie list"), config.plugins.fm.movie_list_fontsize))
        if config.plugins.fm.infobar_fontsize_event_now.value != 0:
            self.list.append(getConfigListEntry(_("Font size for infobar event now"), config.plugins.fm.infobar_fontsize_event_now))
        if config.plugins.fm.infobar_fontsize_event_next.value != 0:
            self.list.append(getConfigListEntry(_("Font size for infobar event next"), config.plugins.fm.infobar_fontsize_event_next))

        # Untertitel
        self.list.append(getConfigListEntry(_("show subtitle options"), config.plugins.fm.display_subtitles))
        if config.plugins.fm.display_subtitles.value:
            if config.plugins.fm.Subtitle_TTX.value != 0:
                self.list.append(getConfigListEntry(_("Font size for subtitles (Teletext)"), config.plugins.fm.Subtitle_TTX))
            if config.plugins.fm.Subtitle_Regular.value != 0:
                self.list.append(getConfigListEntry(_("Font size for subtitles (Regular)"), config.plugins.fm.Subtitle_Regular))
            if config.plugins.fm.Subtitle_Bold.value != 0:
                self.list.append(getConfigListEntry(_("Font size for subtitles (Bold)"), config.plugins.fm.Subtitle_Bold))
            if config.plugins.fm.Subtitle_Italic.value != 0:
                self.list.append(getConfigListEntry(_("Font size for subtitles (Italic)"), config.plugins.fm.Subtitle_Italic))

        self["config"].list = self.list
        self["config"].l.setList(self.list)

    def save(self):
        for x in self["config"].list:
           x[1].save()

        self.session.open(fmWaitScreen, self.tree)
        self.close ()

    def cancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close (False)

    def info(self):
        aboutbox = self.session.open(MessageBox,_("Font magnifier plugin\n\nThis plugin helps you to\nset up different font sizes.\n\n(c) 2010 - BigReaper"), MessageBox.TYPE_INFO)
        aboutbox.setTitle(_("Info...")) 

    def handle_menukey(self):
        self.session.open(fmOptions)

class fmOptions(Screen):
    skin = """
        <screen name="fmOptionsScreen" position="center,center" size="450,130" zPosition="6" title="Options">
            <widget name="optionslist" position="10,5" zPosition="7" size="450,130" scrollbarMode="showOnDemand" transparent="1" />
        </screen>"""

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)

        self["setupActions"] = ActionMap(["SetupActions", "MenuActions"],
        {
            "cancel": self.cancel,
            "ok": self.ok,
        })

        self.list = []
        if os.path.exists("/usr/share/enigma2/%s.bak" % (config.skin.primary_skin.value)):
            self.list.append(_("restore skin.xml"))
        if os.path.exists("/usr/lib/enigma2/python/Components/EpgList.py.bak"):
            self.list.append(_("restore EpgList.py"))
        if os.path.exists("/usr/lib/enigma2/python/Components/MovieList.py.bak"):
            self.list.append(_("restore MovieList.py"))
        if os.path.exists("/usr/lib/enigma2/python/Components/ServiceList.py.bak"):
            self.list.append(_("restore ServiceList.py"))
        if os.path.exists("/etc/enigma2/skin_user.xml.bak"):
            self.list.append(_("restore skin_user.xml"))

        self.selection = ""

        if len(self.list) == 0:
            self.list.append(_("No files to restore!"))
            self["optionslist"] = MenuList(self.list)
            self.setTitle(_("Info..."))
        else:
            self["optionslist"] = MenuList(self.list)
            self.setTitle(_("restore options"))
 
    def cancel(self):
        self.close(False)

    def ok(self):
        self.selection = self["optionslist"].getCurrent()

        if self.selection == _("No files to restore!"):
            self.close(False)
            return
        else:
            self.session.openWithCallback(self.restoringConfirmed, MessageBox, "%s ?" % self.selection)

    def restoringConfirmed(self, confirmed):
        if self.selection == _("restore skin.xml"):
            self.selection = "skin.xml"
        elif self.selection == _("restore EpgList.py"):
            self.selection = "EpgList.py"
        elif self.selection == _("restore MovieList.py"):
            self.selection = "MovieList.py"
        elif self.selection == _("restore ServiceList.py"):
            self.selection = "ServiceList.py"
        elif self.selection == _("restore skin_user.xml"):
            self.selection = "skin_user.xml"

        if not confirmed:
            messagebox_text = self.selection + _(" not restored.")
            confirmbox = self.session.open(MessageBox, messagebox_text, MessageBox.TYPE_INFO)
            confirmbox.setTitle(_("Info..."))
            self.close(False)
            return

        try:
            if self.selection == "skin.xml":
                os.system("mv -f /usr/share/enigma2/%s.bak /usr/share/enigma2/%s" % (config.skin.primary_skin.value, config.skin.primary_skin.value))            
            elif self.selection == "EpgList.py":
                os.system("mv -f /usr/lib/enigma2/python/Components/EpgList.py.bak /usr/lib/enigma2/python/Components/EpgList.py")            
            elif self.selection == "MovieList.py":
                os.system("mv -f /usr/lib/enigma2/python/Components/MovieList.py.bak /usr/lib/enigma2/python/Components/MovieList.py")            
            elif self.selection == "ServiceList.py":
                os.system("mv -f /usr/lib/enigma2/python/Components/ServiceList.py.bak /usr/lib/enigma2/python/Components/ServiceList.py")            
            elif self.selection == "skin_user.xml":
                os.system("mv -f /etc/enigma2/skin_user.xml.bak /etc/enigma2/skin_user.xml")            

            messagebox_text = self.selection + _(" restored.")
            confirmbox = self.session.open(MessageBox, messagebox_text, MessageBox.TYPE_INFO)
        except:
            messagebox_text = self.selection + _(" not restored.")
            confirmbox = self.session.open(MessageBox, messagebox_text, MessageBox.TYPE_INFO)

        confirmbox.setTitle(_("Info..."))
        self.close(False)

class fmWaitScreen(Screen):
    skin = """
        <screen name="fmWaitScreen" position="center,center" size="450,110" zPosition="1" title=" ">
            <ePixmap position="30,10" size="64,64" pixmap="%s" transparent="1" alphatest="blend" />
            <widget source="label" render="Label" position="130,25" size="350,50" font="Regular;32" transparent="1"  />
        </screen>""" % resolveFilename(SCOPE_PLUGINS, "Extensions/FontMagnifier/wait-icon.png")

    def __init__(self, session, skin_tree = None):
        Screen.__init__(self, session)

        self["label"] = StaticText("")
        self["label"].setText(_("Please wait..."))
        self.tree = skin_tree
        self.root = self.tree.getroot()
        self.list_of_screens = self.root.findall("screen")
        self.list_of_subtitles = self.root.findall("subtitles")
        self.timer = eTimer()
        self.timer.callback.append(self.writeXml)
        self.timer.start(500, 1)

    def writeXml(self):
        try: # skin_user.xml
            # if no skin_user.xml exists, create an "empty" file
            if not os.path.exists("/etc/enigma2/skin_user.xml"):
                skin_user_xml_file = open("/etc/enigma2/skin_user.xml", "w")
                skin_user_xml_text = "<skin>\n"
                skin_user_xml_text = skin_user_xml_text + "</skin>\n"
                skin_user_xml_file.write(skin_user_xml_text)
                skin_user_xml_file.close()

            # perform backup before overwriting skin_user.xml:
            if not os.path.exists("/etc/enigma2/skin_user.xml.bak"):
                os.system("cp /etc/enigma2/skin_user.xml /etc/enigma2/skin_user.xml.bak")

            # display manipulation is activated
            if config.plugins.fm.display_manipulation_active.value:
                # but both options are disabled
                if (not config.plugins.fm.active.value) and (not config.plugins.fm.show_only_clock.value):
                    # if a backup exists, restore it
                    if os.path.exists("/etc/enigma2/skin_user.xml.bak"):
                        os.system("mv /etc/enigma2/skin_user.xml.bak /etc/enigma2/skin_user.xml")
                    # if no backup exists, delete skin_user.xml to disable display manipulation
                    elif os.path.exists("/etc/enigma2/skin_user.xml"):
                        os.system("rm /etc/enigma2/skin_user.xml")
                else:   # at least one option is activated
                    skin_user_xml_file = open("/etc/enigma2/skin_user.xml", "w")
                    skin_user_xml_text = "<skin>\n"
                    if config.plugins.fm.active.value:
                        skin_user_xml_text = skin_user_xml_text + "\t<screen name=\"InfoBarSummary\" position=\"0,0\" size=\"132,64\">\n"
                        skin_user_xml_text = skin_user_xml_text + "\t\t<widget font=\"Regular;%s\" halign=\"center\" position=\"1,1\" render=\"Label\" size=\"128,64\" source=\"session.CurrentService\" valign=\"center\">\n" % (config.plugins.fm.fontsize.value)
                        skin_user_xml_text = skin_user_xml_text + "\t\t\t<convert type=\"ExtendedServiceInfo\">ServiceNumber</convert>\n"
                        skin_user_xml_text = skin_user_xml_text + "\t\t</widget>\n"
                        skin_user_xml_text = skin_user_xml_text + "\t</screen>\n"
                    if config.plugins.fm.show_only_clock.value:
                        skin_user_xml_text = skin_user_xml_text + "\t<screen name=\"StandbySummary\" position=\"0,0\" size=\"132,64\">\n"
                        skin_user_xml_text = skin_user_xml_text + "\t\t<widget font=\"Regular;44\" halign=\"center\" position=\"0,0\" render=\"Label\" size=\"132,64\" source=\"global.CurrentTime\" valign=\"center\">\n"
                        skin_user_xml_text = skin_user_xml_text + "\t\t\t<convert type=\"ClockToText\">Format:%H:%M</convert>\n"
                        skin_user_xml_text = skin_user_xml_text + "\t\t</widget>\n"
                        skin_user_xml_text = skin_user_xml_text + "\t\t<widget position=\"6,0\" render=\"FixedLabel\" size=\"120,64\" source=\"session.RecordState\" text=\" \" zPosition=\"1\">\n"
                        skin_user_xml_text = skin_user_xml_text + "\t\t\t<convert type=\"ConfigEntryTest\">config.usage.blinking_display_clock_during_recording,True,CheckSourceBoolean</convert>\n"
                        skin_user_xml_text = skin_user_xml_text + "\t\t\t<convert type=\"ConditionalShowHide\">Blink</convert>\n"
                        skin_user_xml_text = skin_user_xml_text + "\t\t</widget>\n"
                        skin_user_xml_text = skin_user_xml_text + "\t</screen>\n"

                    skin_user_xml_text = skin_user_xml_text + "</skin>\n"
                    skin_user_xml_file.write(skin_user_xml_text)
                    skin_user_xml_file.close()
            else:
                if os.path.exists("/etc/enigma2/skin_user.xml.bak"):
                    os.system("mv /etc/enigma2/skin_user.xml.bak /etc/enigma2/skin_user.xml")
        except:
            self.session.openWithCallback(self.close, MessageBox,_("Sorry, unable modify skin_user.xml"), type = MessageBox.TYPE_INFO)

        # perform backup of skin.xml before changing stuff:
        if not os.path.exists("/usr/share/enigma2/%s.bak" % (config.skin.primary_skin.value)):
            os.system("cp /usr/share/enigma2/%s /usr/share/enigma2/%s.bak" % (config.skin.primary_skin.value, config.skin.primary_skin.value))

        # screens in skin.xml
        try:
            for element in self.list_of_screens:
                if element.keys():
                    for name, value in element.items():
                        if name == "name" and value == "EventView":
                            if element.getchildren():
                                for child in element:
                                    if child.get("name") == "epg_description":
                                        epg_description_font = child.get("font")
                                        font_elements = epg_description_font.split(";")
                                        if len(font_elements) == 2:
                                            new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.evv_fontsize.value)
                                            child.set("font", new_font)
                                            break
                        elif name == "name" and value == "EPGSelection":
                            tag_gefunden=0
                            if element.getchildren():
                                for child in element: # Schleife 1
                                    if child.getchildren():
                                        for sub_child in child: # Schleife 2
                                            if sub_child.tag == "convert":
                                                if sub_child.text == "ExtendedDescription":
                                                    tag_gefunden=1
                                                    break # Schleife 2
                                        if tag_gefunden == 1:
                                            epg_description_font = child.get("font")
                                            font_elements = epg_description_font.split(";")
                                            if len(font_elements) == 2:
                                                new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.single_epg_description_fontsize.value)
                                                child.set("font", new_font)
                                                break # Schleife 1
                        elif name == "name" and value == "ChannelSelection":
                            tag_gefunden=0
                            if element.getchildren():
                                for child in element: # Schleife 1
                                    #if (child.get("name") == "list") and (config.skin.primary_skin.value != "Vali-KingSize/skin.xml"):
                                    if (child.get("name") == "list"):
                                        service_name_font = child.get("serviceNameFont", "")
                                        service_info_font = child.get("serviceInfoFont", "")
                                        service_number_font = child.get("serviceNumberFont", "")

                                        font_elements = service_name_font.split(";")
                                        if len(font_elements) == 2:
                                            new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.channel_list_fontsize.value)
                                            if (config.plugins.fm.channel_list_fontsize.value != 0):
                                                child.set("serviceNameFont", new_font)

                                        font_elements = service_info_font.split(";")
                                        if len(font_elements) == 2:
                                            new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.channel_list_fontsize.value-2)
                                            if (config.plugins.fm.channel_list_fontsize.value != 0):
                                                child.set("serviceInfoFont", new_font)

                                        new_font = "%s" % (config.plugins.fm.channel_list_fontsize.value+6)
                                        if (config.plugins.fm.channel_list_fontsize.value != 0):
                                            child.set("serviceItemHeight", new_font)

                                        font_elements = service_number_font.split(";")
                                        if len(font_elements) == 2:
                                            new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.channel_list_fontsize.value)
                                            if (config.plugins.fm.channel_list_fontsize.value != 0):
                                                child.set("serviceNumberFont", new_font)

                                    if child.getchildren():
                                        for sub_child in child: # Schleife 2
                                            if sub_child.tag == "convert":
                                                if sub_child.text == "ExtendedDescription":
                                                    tag_gefunden=1
                                                    break # Schleife 2
                                        if tag_gefunden == 1:
                                            epg_description_font = child.get("font")
                                            font_elements = epg_description_font.split(";")
                                            if len(font_elements) == 2:
                                                new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.channel_list_epg_description_fontsize.value)
                                                if (config.plugins.fm.channel_list_epg_description_fontsize.value != 0):
                                                    child.set("font", new_font)
                        elif name == "name" and value == "InfoBar":
                            if element.getchildren():
                                children_modified=0
                                for child in element: # Schleife x
                                    if child.get("source") == "session.Event_Now":
                                        if child.getchildren():
                                            tag_gefunden=0
                                            for sub_child in child: # Schleife y
                                                if sub_child.tag == "convert":
                                                    if sub_child.text == "Name":
                                                        tag_gefunden=1
                                                        break # Schleife y
                                            if tag_gefunden == 1:
                                                infobar_event_next_font = child.get("font")
                                                font_elements = infobar_event_next_font.split(";")
                                                if len(font_elements) == 2:
                                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.infobar_fontsize_event_now.value)
                                                    if (config.plugins.fm.infobar_fontsize_event_now.value != 0):
                                                        child.set("font", new_font)
                                                        children_modified=children_modified+1 # 1
                                            tag_gefunden=0
                                            for sub_child in child: # Schleife y
                                                if sub_child.tag == "convert":
                                                    if sub_child.text == "StartTime":
                                                        tag_gefunden=1
                                                        break # Schleife y
                                            if tag_gefunden == 1:
                                                infobar_event_next_font = child.get("font")
                                                font_elements = infobar_event_next_font.split(";")
                                                if len(font_elements) == 2:
                                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.infobar_fontsize_event_now.value)
                                                    if (config.plugins.fm.infobar_fontsize_event_now.value != 0):
                                                        child.set("font", new_font)
                                                        children_modified=children_modified+1 # 2
                                            tag_gefunden=0
                                            for sub_child in child: # Schleife y
                                                if sub_child.tag == "convert":
                                                    if sub_child.text == "Remaining":
                                                        tag_gefunden=1
                                                        break # Schleife y
                                            if tag_gefunden == 1:
                                                infobar_event_next_font = child.get("font")
                                                font_elements = infobar_event_next_font.split(";")
                                                if len(font_elements) == 2:
                                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.infobar_fontsize_event_now.value)
                                                    if (config.plugins.fm.infobar_fontsize_event_now.value != 0):
                                                        child.set("font", new_font)
                                                        children_modified=children_modified+1 # 3
                                    elif child.get("source") == "session.Event_Next":
                                        if child.getchildren():
                                            tag2_gefunden=0
                                            for sub_child in child: # Schleife y
                                                if sub_child.tag == "convert":
                                                    if sub_child.text == "Name":
                                                        tag2_gefunden=1
                                                        break # Schleife y
                                            if tag2_gefunden == 1:
                                                infobar_event_next_font = child.get("font")
                                                font_elements = infobar_event_next_font.split(";")
                                                if len(font_elements) == 2:
                                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.infobar_fontsize_event_next.value)
                                                    if (config.plugins.fm.infobar_fontsize_event_next.value != 0):
                                                        child.set("font", new_font)
                                                        children_modified=children_modified+1 # 4
                                            tag2_gefunden=0
                                            for sub_child in child: # Schleife y
                                                if sub_child.tag == "convert":
                                                    if sub_child.text == "StartTime":
                                                        tag2_gefunden=1
                                                        break # Schleife y
                                            if tag2_gefunden == 1:
                                                infobar_event_next_font = child.get("font")
                                                font_elements = infobar_event_next_font.split(";")
                                                if len(font_elements) == 2:
                                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.infobar_fontsize_event_next.value)
                                                    if (config.plugins.fm.infobar_fontsize_event_next.value != 0):
                                                        child.set("font", new_font)
                                                        children_modified=children_modified+1 # 5
                                            tag2_gefunden=0
                                            for sub_child in child: # Schleife y
                                                if sub_child.tag == "convert":
                                                    if sub_child.text == "Duration":
                                                        tag2_gefunden=1
                                                        break # Schleife y
                                            if tag2_gefunden == 1:
                                                infobar_event_next_font = child.get("font")
                                                font_elements = infobar_event_next_font.split(";")
                                                if len(font_elements) == 2:
                                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.infobar_fontsize_event_next.value)
                                                    if (config.plugins.fm.infobar_fontsize_event_next.value != 0):
                                                        child.set("font", new_font)
                                                        children_modified=children_modified+1 # 6
                                    if children_modified==6:
                                        break; # Schleife x

            # subtitles
            if len (self.list_of_subtitles) != 0:
                for element in self.list_of_subtitles: # Schleife 1
                    if element.getchildren():
                        for child in element: # Schleife 2
                            if child.get("name") == "Subtitle_TTX":
                                font = child.get("font")
                                font_elements = font.split(";")
                                if len(font_elements)==2:
                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.Subtitle_TTX.value)
                                    if config.plugins.fm.Subtitle_TTX.value != 0:
                                        child.set("font", new_font)
                            elif child.get("name") == "Subtitle_Regular":
                                font = child.get("font")
                                font_elements = font.split(";")
                                if len(font_elements)==2:
                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.Subtitle_Regular.value)
                                    if config.plugins.fm.Subtitle_Regular.value != 0:
                                        child.set("font", new_font)
                            elif child.get("name") == "Subtitle_Bold":
                                font = child.get("font")
                                font_elements = font.split(";")
                                if len(font_elements)==2:
                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.Subtitle_Bold.value)
                                    if config.plugins.fm.Subtitle_Bold.value != 0:
                                        child.set("font", new_font)
                            elif child.get("name") == "Subtitle_Italic":
                                font = child.get("font")
                                font_elements = font.split(";")
                                if len(font_elements)==2:
                                    new_font = font_elements[0] + ";" + "%s" % (config.plugins.fm.Subtitle_Italic.value)
                                    if config.plugins.fm.Subtitle_Italic.value != 0:
                                        child.set("font", new_font)

            self.tree.write("/usr/share/enigma2/%s" % (config.skin.primary_skin.value))
        except:
            self.session.openWithCallback(self.close, MessageBox,_("Sorry, unable to parse /usr/share/enigma2/%s." % (config.skin.primary_skin.value)), type = MessageBox.TYPE_INFO)

        # single epg modification start:
        try:
            if config.plugins.fm.single_epg_list_fontsize.value != 0:
                EpgList_file = open("/usr/lib/enigma2/python/Components/EpgList.py", "r")
                EpgList_text=EpgList_file.read()
                if EpgList_text.find("\t\tself.l.setItemHeight") is not -1:
                    item_height_gefunden = 1
                else:
                    item_height_gefunden = 0
                EpgList_file.close()

                EpgList_text_neu = ""
                EpgList_file = open("/usr/lib/enigma2/python/Components/EpgList.py", "r")
                for zeile in EpgList_file:
                    if zeile.find("\t\tself.l.setFont(0") is not -1:
                        if item_height_gefunden == 0:
                            EpgList_text_neu = EpgList_text_neu + "\t\tself.l.setItemHeight(%d)\n" % (config.plugins.fm.single_epg_list_fontsize.value+5)
                        EpgList_text_neu = EpgList_text_neu + "\t\tself.l.setFont(0, gFont(\"Regular\", %d))\n" % (config.plugins.fm.single_epg_list_fontsize.value)
                    elif zeile.find("\t\tself.l.setFont(1") is not -1:
                        EpgList_text_neu = EpgList_text_neu + "\t\tself.l.setFont(1, gFont(\"Regular\", %d))\n" % (config.plugins.fm.single_epg_list_fontsize2.value)
                    elif zeile.find("\t\tself.l.setItemHeight") is not -1:
                        EpgList_text_neu = EpgList_text_neu + "\t\tself.l.setItemHeight(%d)\n" % (config.plugins.fm.single_epg_list_fontsize.value+5)
                    else:
                        EpgList_text_neu = EpgList_text_neu + zeile

                EpgList_file.close()

                if not os.path.exists("/usr/lib/enigma2/python/Components/EpgList.py.bak"):
                    os.system("cp /usr/lib/enigma2/python/Components/EpgList.py /usr/lib/enigma2/python/Components/EpgList.py.bak")

                EpgList_file = open("/usr/lib/enigma2/python/Components/EpgList.py", "w")
                EpgList_file.write(EpgList_text_neu)
                EpgList_file.close()
        # single epg modification end
        except:
            self.session.openWithCallback(self.close, MessageBox,_("Sorry, unable to parse /usr/lib/enigma2/python/Components/EpgList.py"), type = MessageBox.TYPE_INFO)

        # movie list modification start
        try:
            if config.plugins.fm.movie_list_fontsize.value != 0:
                MovieList_text_neu = ""
                MovieList_file = open("/usr/lib/enigma2/python/Components/MovieList.py", "r")
                for zeile in MovieList_file:
                    if zeile.find("\t\tself.l.setFont(0") is not -1:
                        MovieList_text_neu = MovieList_text_neu + "\t\t\tself.l.setFont(0, gFont(\"Regular\", %d))\n" % (config.plugins.fm.movie_list_fontsize.value)
                    else:
                        MovieList_text_neu = MovieList_text_neu + zeile

                MovieList_file.close()

                if not os.path.exists("/usr/lib/enigma2/python/Components/MovieList.py.bak"):
                    os.system("cp /usr/lib/enigma2/python/Components/MovieList.py /usr/lib/enigma2/python/Components/MovieList.py.bak")

                MovieList_file = open("/usr/lib/enigma2/python/Components/MovieList.py", "w")
                MovieList_file.write(MovieList_text_neu)
                MovieList_file.close()
        # movie list modification end
        except:
            self.session.openWithCallback(self.close, MessageBox,_("Sorry, unable to parse /usr/lib/enigma2/python/Components/MovieList.py"), type = MessageBox.TYPE_INFO)

        restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to apply a new settings\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
        restartbox.setTitle(_("Restart GUI now?"))

    def restartGUI(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()
