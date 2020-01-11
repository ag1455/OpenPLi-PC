#!/usr/bin/python
# -*- coding: utf-8 -*-
##20180618 lines 1134 and 1380##################
##20180609###################
from urllib2 import urlopen
import httplib
import urllib
import urlparse
from Components.MenuList import MenuList
from Components.Label import Label

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Input import Input
from Components.Pixmap import Pixmap
from Components.FileList import FileList
from Screens.ChoiceBox import ChoiceBox
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Screens.InputBox import InputBox

import os
from Screens.InfoBar import MoviePlayer
from enigma import eServiceReference
from enigma import eServiceCenter
from ServiceReference import ServiceReference
from Components.Task import Task, Job, job_manager as JobManager, Condition
from Screens.TaskView import JobView
from Components.Button import Button

from enigma import eServiceReference
from enigma import eServiceCenter
from Screens.InfoBarGenerics import *
from Screens.InfoBar import MoviePlayer, InfoBar
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase

from Components.config import config

from Screens.Screen import Screen
from Tools.Directories import resolveFilename, pathExists, fileExists, SCOPE_SKIN_IMAGE, SCOPE_MEDIA
from Plugins.Plugin import PluginDescriptor

from Components.Pixmap import Pixmap, MovingPixmap
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch
from Components.Sources.List import List
from Components.ConfigList import ConfigList, ConfigListScreen

from Components.config import config, ConfigSubsection, ConfigInteger, ConfigSelection, ConfigText, ConfigEnableDisable, KEY_LEFT, KEY_RIGHT, KEY_0, getConfigListEntry
from Components.Task import Task, Job, job_manager as JobManager, Condition
##################
from twisted.web.client import getPage, downloadPage
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eTimer, quitMainloop, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, eListbox, gFont, getDesktop, ePicLoad
from Tools.LoadPixmap import LoadPixmap
########################
import socket
from urllib import quote, unquote_plus, unquote
from httplib import HTTPConnection, CannotSendRequest, BadStatusLine, HTTPException
from urlparse import parse_qs
from threading import Thread
HTTPConnection.debuglevel = 1
########################
from twisted.web import client
from twisted.internet import reactor
from urllib2 import Request, URLError, urlopen as urlopen2
from socket import gaierror, error
import os, socket
from urllib import quote, unquote_plus, unquote
from httplib import HTTPConnection, CannotSendRequest, BadStatusLine, HTTPException
from TaskView2 import JobViewNew
import re
##########################
import gettext
from skin import parseColor
#from Playlist import Playlist


import xpath
THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"
NOSS = 0
try:
      from SubsSupport import SubsSupport, initSubsSettings
except:
      NOSS = 1      

def _(txt):
	t = gettext.dgettext("xbmcaddons", txt)
	if t == txt:
		print "[XBMCAddonsA] fallback to default translation for", txt
		t = gettext.gettext(txt)
	return t

##########################

HTTPConnection.debuglevel = 1
from download import startdownload ##mfaraj2608 to for new download management
std_headers = {
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'en-us,en;q=0.5',
}  
##############################################################
#                                                            #
#   Mainly Coded by pcd, July 2013                 #
#                                                            #
##############################################################

SREF = " "

class Getvid(Screen):

    def __init__(self, session, name, url, desc):
		Screen.__init__(self, session)
#                self.skin = SkinA.skin
                self.skinName = "Showrtmp"
                title = "Play"
                self.setTitle(title)

#############################################
		self.list = []
                self["list"] = List(self.list)
                self["list"] = RSList([])
#############################################
		self["info"] = Label()
                self["key_red"] = Button(_("Exit"))
		self["key_green"] = Button(_("Download"))
		self["key_yellow"] = Button(_("Play"))
		self["key_blue"] = Button(_("Stop Download"))
                self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
		{
			"red": self.close,
			"green": self.okClicked,
			"yellow": self.play,
			"info":self.showinfo,
			"blue": self.stopdl,
			"cancel": self.cancel,
			"ok": self.okClicked,
		}, -2)
                self.icount = 0
                self.name = name
                self.url = url
                txt = _("Must do (1) Download  (2) Play.\n\n") + self.name + "\n\n" + desc
                self["info"].setText(txt)

                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                self.onLayoutFinish.append(self.getrtmp)
    def showinfo(self):
         return
    def getrtmp(self):
                fold = config.plugins.kodiplug.cachefold.value+"/"
                fname = "savedvid"
                svfile = fold + "/" + fname + ".mpg"
                self.svf = svfile
                if "rtmp" not in self.url:
                       self.urtmp = "wget -O '" + svfile +"' -c '" + self.url + "'"
                else:
                       params = self.url
                       print "params A=", params
                       params = params.replace(" swfVfy=", " --swfVfy ")
                       params = params.replace(" playpath=", " --playpath ")
                       params = params.replace(" app=", " --app ")
                       params = params.replace(" pageUrl=", " --pageUrl ")
                       params = params.replace(" tcUrl=", " --tcUrl ")
                       params = params.replace(" swfUrl=", " --swfUrl ") 
                       print "params B=", params
                       self.urtmp = "rtmpdump -r " + params + " -o '" + svfile + "'"

    def okClicked(self):
                self["info"].setText("Downloading ....")
                fold = config.plugins.kodiplug.cachefold.value+"/xbmc/vid"
                fname = "savedvid"
                svfile = fold + "/" + fname + ".mpg"
                self.svf = svfile
                cmd = "rm " + svfile
                os.system(cmd)
                JobManager.AddJob(downloadJob(self, self.urtmp, svfile, 'Title 1')) 

                self.LastJobView()

 
    def LastJobView(self):
		currentjob = None
		for job in JobManager.getPendingJobs():
			currentjob = job

		if currentjob is not None:
			self.session.open(JobView, currentjob)

    def play(self):
          if os.path.exists(self.svf):
                #print "Showrtmp here 2"
                svfile = self.svf
                desc = " "
                self.session.open(Playvid2, self.name, svfile, desc)
                #runKDplayer(self.session,name,svfile,desc)
          else:
                txt = _("Download Video first.")
                self["info"].setText(txt)

    def cancel(self):
	        self.session.nav.playService(self.srefOld)
                self.close()

    def stopdl(self):
                #svfile = self.svf
                #cmd = "rm " + svfile
                #os.system(cmd)
                self.session.nav.playService(self.srefOld)
                cmd1 = "killall -9 rtmpdump"
                cmd2 = "killall -9 wget"
                os.system(cmd1)
                os.system(cmd2)
                #self.close()


    def keyLeft(self):
		self["text"].left()

    def keyRight(self):
		self["text"].right()

    def keyNumberGlobal(self, number):
		#print "pressed", number
		self["text"].number(number)
def runKDplayerXX(session,name,url,desc):


                if "plugin://plugin.video.youtube" in url or "youtube.com/" in url :

                      from tube_resolver.plugin import getvideo
                      url,error = getvideo(url)
                      if error is not None or url is None:
                         print "failed to get valid youtube stream link"
                         return 

                elif "pcip" in url:
                       n1 = url.find("pcip")
                       urlA = self.url
                       url = url[:n1]
                       pcip = urlA[(n1+4):]



                print "Here in Playvid name A =", name
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                name = name.replace("›", "-")
                name = name.replace(",", "-") 
                print "Here in Playvid name B2 =", name

                if url is not None:
                       sref = eServiceReference(0x1001, 0, url)
		       sref.setName(name)


		else:
                       return

                session.open(Playvid2, name, url, desc) 


class Getvid2(Screen):

    def __init__(self, session, name, url, desc):
        global SREF
        Screen.__init__(self, session)
        self.skinName = "Showrtmp"
        self['list'] = MenuList([])
        self['info'] = Label()
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Download'))
        self['key_yellow'] = Button(_('Play'))
        self['key_blue'] = Button(_('Stop Download'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'TimerEditActions'], {'red': self.close,
         'green': self.okClicked,
         'yellow': self.play,
         'blue': self.stopDL,
         'cancel': self.cancel,
         'ok': self.openTest}, -2)
        self.icount = 0
        self.bLast = 0
        cachefold = config.plugins.kodiplug.cachefold.value
        self.svfile = cachefold + "/xbmc/vid/savedfile.mpg"
        txt = _("Play direct OR Download and Play")
        self['info'].setText(txt)
        ####################
##        self.updateTimer = eTimer()
##        self.updateTimer.callback.append(self.updateStatus)
##        self.updateTimer.start(2000)
##        self.updateStatus()
        ####################
        self.updateTimer = eTimer()
        try:
               self.updateTimer_conn = self.updateTimer.timeout.connect(self.updateStatus)
        except AttributeError:
               self.updateTimer.callback.append(self.updateStatus)
#       self.updateTimer.callback.append(self.updateStatus)
	self.updateTimer.start(2000)
	self.updateStatus()
        ####################
        self.name = name
        self.url = url
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        SREF = self.srefOld



    def openTest(self):
        vid = self.name
        infotxt = _('Video selected :-\n\n\n') + vid
        self['info'].setText(infotxt)

    def play(self):
        desc = " "
        if self.icount == 0:
               url = self.url
               name = self.name
        else:
               url = self.svfile
               name = "Video"
        self.session.open(Playvid2, name, url, desc)
        #runKDplayer(self.session,name,url,desc)

    def okClicked(self):
        cmd = 'rm ' + self.svfile
        os.system(cmd)
        self.icount = 1
        JobManager.AddJob(downloadJob(self, "wget -O '" + self.svfile + "' -c '" + self.url + "'", self.svfile, 'Title 1'))



    def updateStatus(self):
        if not os.path.exists(self.svfile):
            return 
        if self.icount == 0:
            return 
        b1 = os.path.getsize(self.svfile)
        b = b1 / 1000
        if b == self.bLast:
            infotxt = 'Download Complete....' + str(b)
            self['info'].setText(infotxt)
            return 
        self.bLast = b
        infotxt = (_('Downloading....')) + str(b) + ' kb'
        self['info'].setText(infotxt)



    def LastJobView(self):
        currentjob = None
        for job in JobManager.getPendingJobs():
            currentjob = job

        if currentjob is not None:
            self.session.open(JobView, currentjob)



    def cancel(self):
        self.session.nav.playService(SREF)
        self.close()



    def stopDL(self):
        cmd = 'killall -9 wget &'
        os.system(cmd)



    def keyLeft(self):
        self['text'].left()



    def keyRight(self):
        self['text'].right()



    def keyNumberGlobal(self, number):
        self['text'].number(number)


class Playoptions(Screen):

    def __init__(self, session, name, url, desc):
        global SREF
        Screen.__init__(self, session)
        self.name = name
        self.url = url  
        self.skinName = "Playoptions"
        self.hostaddr = ""
        self["list"] = List([])
        self["list"] = RSList([])
        self['info'] = Label()
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Download'))
        self['key_yellow'] = Button(_('Play'))
        self['key_blue'] = Button(_('Stop Download'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'TimerEditActions'], {'red': self.close,
         'green': self.okClicked,
         'yellow': self.start1,
         'blue': self.stopDL,
         'cancel': self.cancel,
         'ok': self.okClicked}, -2)
        self.icount = 0
        self.bLast = 0
        self.useragent = "QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1Service Pack 3)"
        cachefold = config.plugins.kodiplug.cachefold.value
        self.svfile = " "
        self.list=[]
########################
        i=0
        while i<9:
               self.list.append(i)
               i=i+1 
        self.list[0] =(_("Play"))
        self.list[1] =(_("Play with tsplayer"))
        self.list[2] =(_("Play with hlsplayer"))
        """
        self.list[3] =(_("Play with streamlink (needs streamlink installed)"))
        """
        self.list[3] =(_("Play with vlc (set vlc server ip in Config)"))
        self.list[4] =(_("Download"))
        self.list[5] =(_("Stop download"))
        self.list[6] =(_("Add to favorites"))
        self.list[7] =(_("Add to bouquets"))
        self.list[8] =(_("Current Downloads"))
########################
        self.name = name
        self.url = url
        print "Here in Playvid self.url =", self.url
        print "<<<Endurl"
        #############################
        if "/tmp/vid.txt" in self.url:
               file1 = "/tmp/vid.txt"
               f1=open(file1,"r+")
               txt1 = f1.read()
               print "In Playvid txt1 =", txt1
               self.url = txt1
        #############################
#        self.url = self.url.replace("|", "\|")
        self.urlmain = self.url
        n1 = self.url.find("|", 0)
        if n1 > -1:
                self.url = self.url[:n1]

        print "Here in Playvid self.url B=", self.url
        #self['info'].setText(txt)

        ####################
##        self.updateTimer = eTimer()
##        self.updateTimer.callback.append(self.updateStatus)
##        self.updateTimer.start(2000)
##        self.updateStatus()
        ####################
        self.updateTimer = eTimer()
        try:
               self.updateTimer_conn = self.updateTimer.timeout.connect(self.updateStatus)
        except AttributeError:
               self.updateTimer.callback.append(self.updateStatus)
#       self.updateTimer.callback.append(self.updateStatus)
##	self.updateTimer.start(2000)
##	self.updateStatus()
        ####################
        self['info'].setText(" ")
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        SREF = self.srefOld
        print "Here in Playvid SREF =", SREF
        if config.plugins.kodiplug.directpl.value is True:
                print "Here in directpl"
                self.onShown.append(self.start1)
        elif "hds://" in url: 
                self.onShown.append(self.start3)
        elif self.url.startswith("stack://"):
                self.onShown.append(self.start4)
#        elif "plugin://plugin.video.youtube" in self.url or "youtube.com/" in self.url :
#                self.onShown.append(self.start5)

        else:
                print "Here in no directpl"
                self.onLayoutFinish.append(self.start)
#                self.onShown.append(self.start1)

    def start1(self):
        desc = " "

        if "/tmp/vid.txt" in self.url or "plugin://plugin.video.youtube" in self.url or "youtube.com/" in self.url :
                 self.start5()
                 self.cancel()
        elif "f4m" in self.url:
                 print "In playVideo f4m url A=", self.url
                 from F4mProxy import f4mProxyHelper
                 player=f4mProxyHelper()
                 url = self.url
                 name = self.name
                 self.url = player.playF4mLink(url, name, streamtype='HDS', direct="no")
                 self.session.open(Playvid2, self.name, self.url, desc)
                 self.cancel()

        else:
                 self.session.open(Playvid2, self.name, self.url, desc)
                 self.cancel()


    def playts(self):
           desc = " "
           if ".ts" in self.url: 
                            url = self.url
                            print "shahid url A= ", url
                            try:os.remove("/tmp/hls.avi")
                            except:pass
#                            url=url.split("?hls")[0]
                            cmd = 'python "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/lib/tsclient.py" "' + url + '" "1" &'
#ok                            cmd = 'python "/usr/lib/enigma2/python/hlsclient.py" "' + url + '" "1" > /tmp/hls.txt 2>&1 &'
#                            cmd = 'python "/usr/lib/enigma2/python/hlsclient.py" "' + url + '" "1" &'
                            print "hls cmd = ", cmd
                            os.system(cmd)
                            os.system('sleep 3')
                            self.url = '/tmp/hls.avi'
                            self.session.open(Playvid2, self.name, self.url, desc)
           else:
                self.session.open(Playvid2, self.name, self.url, desc)

    def playtsX(self):
        desc = " "
        if ".ts" in self.url: 
                 print "In playVideo shahid url B=", self.url
                 from F4mProxy import f4mProxyHelper
                 player=f4mProxyHelper()
                 url = self.url
                 name = self.name
                 self.url = player.playF4mLink(url, name, streamtype='TSDOWNLOADER')
                 self.session.open(Playvid2, self.name, self.url, desc)

        else:
                 self.session.open(Playvid2, self.name, self.url, desc)
                 self.close()


    def start3(self):
        from stream import GreekStreamTVList
        self.session.open(GreekStreamTVList, streamFile = "/tmp/stream.xml")
        self.close()

    def start4(self):
                       from Playlist import Playlist
                       self.session.open(Playlist, self.url)
                       self.close()
    def start5X(self):
         self.pop = 1
         n1 = self.url.find("video_id", 0)
         n2 = self.url.find("=", n1)
         vid = self.url[(n2+1):]
         cmd = "python '/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/" + ADDONCAT + "/plugin.video.youtube/default.py' '6' '?plugin://plugin.video.youtube/play/?video_id=" + vid + "' &"
         self.p = os.popen(cmd)

    def start5(self):
         file1 = "/tmp/vid.txt"
         f1=open(file1,"r+")
         txt1 = f1.read()
         print "In Playvid txt1 =", txt1
         self.url = txt1
         self.session.open(Playvid2, self.name, self.url, desc=" ")
         self.close()



    def start(self):
#        infotxt=(_("Selected: ")) + self.name
        infotxt=(_("Selected video: ")) + self.name + (_("\n\nDownload as :"))+self.getlocal_filename()[0]
        self['info'].setText(infotxt)
        print "Going in showlist"
        showlist(self.list, self['list'])

    def openTest(self):
        pass

    def playsl(self):
                       print "Here in utils-py play with streamlink self.url =", self.url
                       url = str(self.url)
                       if ".ts" in url:
                            print "playsl url A= ", url
                            url = url.replace(".ts", ".m3u8")    

                       url = url.replace(":", "%3a")
                       url = url.replace("\\", "/")
                       print "url final= ", url
                       ref = "5002:0:1:1:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/" + url
                       print "ref= ", ref
                       self.session.open(Playvid2, self.name, ref, desc=" ")
		       self.close()

    def playhls(self):
        print "Here in utils-py play self.icount =", self.icount
        desc = " "
        if self.icount == 0:
               print "Here in utils-py play self.urlmain =", self.urlmain
               url1 = self.urlmain
               n1 = url1.find("|", 0)
               print "Here in hlsclient-py n1, url1 =", n1, url1
               if n1 > -1:
                     url = url1[:n1]
                     print "Here in hlsclient-py url =", url
                     header = url1[(n1+1):]
                     print "Here in hlsclient-py header = ", header
               else:
                     url = url1
                     header = ""
#               url = self.url
               name = self.name
               if ".ts" in url:
                            print "shahid url A= ", url
                            url = url.replace(".ts", ".m3u8")
               if "m3u8" in url:
#                      if "shahid.net" in url:
                            print "shahid url = ", url
                            try:os.remove("/tmp/hls.avi")
                            except:pass
#                            url=url.split("?hls")[0]
                            cmd = 'python "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/lib/hlsclient.py" "' + url + '" "1" "' + header + '" + &'
#ok                            cmd = 'python "/usr/lib/enigma2/python/hlsclient.py" "' + url + '" "1" > /tmp/hls.txt 2>&1 &'
#                            cmd = 'python "/usr/lib/enigma2/python/hlsclient.py" "' + url + '" "1" &'
                            print "hls cmd = ", cmd
                            os.system(cmd)
                            os.system('sleep 3')
                            url = '/tmp/hls.avi'
        else:
               url = self.svfile
               name = "Video"
        self.session.open(Playvid2, name, url, desc)

    def playXX(self):
        desc = " "
        if ".m3u8" in self.url:
                 print "In Playvid m3u8 going in f4mProxyHelper url A=", self.url
                 from F4mProxy import f4mProxyHelper
                 player=f4mProxyHelper()
                 url = self.url
                 name = self.name
                 self.url = player.playF4mLink(url, name, streamtype='HLS')
                 self.session.open(Playvid2, self.name, self.url, desc)

        else:
                 self.session.open(Playvid2, self.name, self.url, desc)
                 self.close()


    def getlocal_filename(self):
                       fold = config.plugins.kodiplug.cachefold.value + "/movies/"
                       name = self.name.replace("/media/hdd/movies/", "")
                       name = name.replace(" ", "-")
                       pattern = '[a-zA-Z0-9\-]'
                       input = name
                       output = ''.join(re.findall(pattern, input))
                       self.name = output
                       if self.url.endswith("mp4"):
                          svfile = fold + self.name+".mp4"
                       elif self.url.endswith("flv"):
                          svfile = fold + self.name+".flv"
                       elif self.url.endswith("avi"):
                          svfile = fold + self.name+".avi"
                       elif self.url.endswith("ts"):
                          svfile = fold + self.name+".ts"
                       else:  
                          svfile = fold + self.name+".mpg"
                       filetitle=os.path.split(svfile)[1]
                       return svfile,filetitle




    def play2(self):
	        print "We are in play2"
	        url = "http://192.168.1.65:8080/dream.ts"
	        url = url.replace(":", "%3a")
                ref = "4097:0:1:0:0:0:0:0:0:0:" + url
                sref = eServiceReference(ref)
                self.name = "Test"
		sref.setName(self.name)
		self.session.nav.stopService()
		self.session.nav.playService(sref)
	        self.close()

    def okClicked(self):

          idx=self["list"].getSelectionIndex()
          print "idx",idx
          if idx==0:
                self.start1()
          elif idx==1:
                self.playts()
          elif idx==2:
                self.playhls()
          elif idx==3:
                import urllib2
#                from urllib import urlencode
                from urllib import quote
                #transcode based on vlcplayerIHAD and vlc 2.0.5
                vlcip = config.plugins.kodiplug.vlcip.value

                self.hostaddr = "http://" + vlcip + ":8080"


                url = quote(self.url, safe='')
                print "In Playvid going in vlc url =", url
                cmd = self.hostaddr + "/requests/status.xml?command=in_play&input=" + url + "&option=%3Asout%3D%23transcode%7Bvcodec%3Dmp2v%2Cvb%3D2000%2Cvenc%3Dffmpeg%2Cfps%3D25%2Cvfilter%3Dcanvas%7Bwidth%3D352%2Cheight%3D288%2Caspect%3D4%3A3%7D%2Cacodec%3Dmp2a%2Cab%3D128%2Cchannels%3D2%2Csamplerate%3D0%7D%3Astd%7Baccess%3Dhttp%2Cmux%3Dts%7Bpid-video%3D68%2Cpid-audio%3D69%7D%2Cdst%3D%2Fdream.ts%7D&option=%3Asout-all&option=%3Asout-keep" 
##                cmd = self.hostaddr + "/requests/status.xml?command=in_play&input=" + url + "&option=%3Asout%3D%23transcode%7Bvcodec%3Dmp2v%2Cvb%3D2000%2Cvenc%3Dffmpeg%2Cfps%3D25%2Cvfilter%3Dcanvas%7Bwidth%3D1280%2Cheight%3D720%2Caspect%3D16%3A9%7D%2Cacodec%3Dmp2a%2Cab%3D128%2Cchannels%3D2%2Csamplerate%3D32000%7D%3Astd%7Baccess%3Dhttp%2Cmux%3Dts%7Bpid-video%3D68%2Cpid-audio%3D69%7D%2Cdst%3D%2Fdream.ts%7D&option=%3Asout-all&option=%3Asout-keep"
#                url = self.url.replace(":", "%3a")
	        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, self.hostaddr, '','Admin')
                handler = urllib2.HTTPBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(handler)
                f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_stop")
                f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_empty")
                f = opener.open(cmd)
                f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_play")
                vurl = self.hostaddr + "/dream.ts"
	        desc = " "
	        self.session.open(Playvid2, self.name, vurl, desc)

          elif idx==4: 
                print "In Playvid Download" 
                if "#header#" in self.url:
                       self.svfile,self.filetitle = self.getlocal_filename()
                       cmd1 = "rm " + self.svfile
                       os.system(cmd1)
                       n1 = self.url.find("#header#", 0)
                       header = self.url[(n1+8):]
                       self.url = self.url[:n1]
                       cmd = 'wget -O "' + self.svfile + '" --header="' + header + '" --user-agent="Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36" "' + self.url + '" &'
                       print "In Playvid cmd =", cmd
                       os.system(cmd)
                       self.icount = 1
                       return

                if "plugin://plugin.video.youtube" in self.url or "youtube.com/" in self.url :
                       file1 = "/tmp/vid.txt"
                       f1=open(file1,"r+")
                       txt1 = f1.read()
                       print "In Playvid download youtube txt1 =", txt1
                       self.url = txt1
                       print "In Playvid download youtube self.url =", self.url
                       self.svfile,self.filetitle = self.getlocal_filename()
                       downloadPage(self.url, self.svfile).addErrback(self.showError)
                       self.updateTimer.start(2000)

                elif ".m3u8" in self.url:
                       ###############################
                       print "In Playvid m3u8 download self.urlmain =", self.urlmain
                       url1 = self.urlmain
                       n1 = url1.find("|", 0)
                       print "Here in hlsclient-py n1, url1 =", n1, url1
                       if n1 > -1:
                               url = url1[:n1]
                               print "Here in hlsclient-py url =", url
                               header = url1[(n1+1):]
                               print "Here in hlsclient-py header = ", header
                       else:
                               url = url1
                               header = ""
                       ################################
                       self.svfile,self.filetitle = self.getlocal_filename()
#                       self.pop = 0
                       cmd = 'python "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/lib/hlsdownld.py" "' + self.url + '" "1" "' + self.svfile + '" "' + header + '" + &'
                       print "In Playvid m3u8 download cmd =", cmd
                       os.system(cmd)
                       self.icount = 1
#                       self.updateTimer.start(2000)

                elif self.url.startswith("https"):
                       print "In Playvid Download https url like youtube"
                       self.icount = 1
                       self.svfile,self.filetitle = self.getlocal_filename()
                       print "In Playvid Download https self.svfile,self.filetitle =", self.svfile, self.filetitle
                       print "In Playvid Download https self.url =", self.url
                       downloadPage(self.url, self.svfile).addErrback(self.showError)
                       self.updateTimer.start(2000)

                elif "rtmp" in self.url:
                       params = self.url
                       print "params A=", params
                       params = "'" + params + "'"
                       params = params.replace(" swfVfy=", "' --swfVfy '")
                       params = params.replace(" playpath=", "' --playpath '")
                       params = params.replace(" app=", "' --app '")
                       params = params.replace(" pageUrl=", "' --pageUrl '")
                       params = params.replace(" tcUrl=", "' --tcUrl '")
                       params = params.replace(" swfUrl=", "' --swfUrl '") 
                       print "params B=", params

                       self.svfile,self.filetitle = self.getlocal_filename()
                       self.urtmp = "rtmpdump -r " + params + " -o '" + self.svfile + "'"
                       self["info"].setText(_("Start downloading"))
                       self.icount = 1
                       cmd = "rm " + self.svfile
                       print "rtmp cmd =", cmd
                       os.system(cmd)
                       JobManager.AddJob(downloadJob(self, self.urtmp, self.svfile, 'Title 1'))
                       self.LastJobView()


                else:
                       self.svfile,self.filetitle = self.getlocal_filename()
                       startdownload(self.session,answer='download',myurl=self.url,filename=self.svfile,title=self.filetitle)

          elif idx==5:
                       self.stopDL()

          elif idx==6:
               print 'add to favorite'
               from favorites import addfavorite
               import sys

               try:
                  addon_id=os.path.split(os.path.split(sys.argv[0])[0])[1]
                  print "470add_id",addon_id
                  result=addfavorite(addon_id,self.name,self.url)
               except:
                   result=False
               if result==False:
                   print "failed to add to favorites"
                   self.session.open(MessageBox, _("Failed to add to favorites."), MessageBox.TYPE_ERROR, timeout = 4)
               else:
                   print "added to favorites"
                   self.session.open(MessageBox, _("Item added successfully to favorites."), MessageBox.TYPE_INFO, timeout = 4)
          elif idx==7:
            try:error=stream2bouquet(self.url,self.name,'XBMCAddons_streams')
            except:error=(_("Failed to add stream to bouquet"))
            if error=='none':
               self.session.open(MessageBox, _((_('Stream added to '))+'XBMCAddons_streams '+ (_('bouquet\nrestart enigma to refresh bouquets'))), MessageBox.TYPE_INFO, timeout = 10)
            else:
               self.session.open(MessageBox, _("Failed to add stream to bouquet."), MessageBox.TYPE_ERROR, timeout = 4)

          elif idx==8:
               from XBMCAddonsMediaExplorer import XBMCAddonsMediaExplorer
               self.session.open(XBMCAddonsMediaExplorer)

    def showError(self, error):
               print "DownloadPage error = ", error


    def updateStatus(self):
#        print "self.icount =", self.icount
#     print "In updateStatus self.pop =", self.pop
     if self.pop == 1:
            try:
               ptxt = self.p.read()
#               print "In updateStatus ptxt =", ptxt
               if "data B" in ptxt:
                      n1 = ptxt.find("data B", 0)
                      n2 = ptxt.find("&url", n1)
                      n3 = ptxt.find("\n", n2)
                      url = ptxt[(n2+5):n3]
                      url = url.replace("AxNxD", "&")
                      self.url = url.replace("ExQ", "=")
#                      print "In updateStatus url =", url
                      name = "Video"
                      desc = " "
                      self.session.open(Playvid, self.name, self.url, desc)
                      self.close()
                      self.updateTimer.stop()
#               else:
#                      self.openTest()
#                      return
            except:
               self.openTest()
#               return
     else:
        if not os.path.exists(self.svfile):
            print "No self.svfile =", self.svfile
            self.openTest()
            return

        if self.icount == 0:
            self.openTest()
            return 

#        print "Exists self.svfile =", self.svfile
        b1 = os.path.getsize(self.svfile)
        print "b1 =", b1
        b = b1 / 1000
        if b == self.bLast:
            infotxt = _('Download Complete....') + str(b)
            self['info'].setText(infotxt)
            return 
        self.bLast = b
        infotxt = _('Downloading....') + str(b) + ' kb'
        self['info'].setText(infotxt)

    def LastJobView(self):
        currentjob = None
        for job in JobManager.getPendingJobs():
            currentjob = job

        if currentjob is not None:
            self.session.open(JobViewNew, currentjob)


    def cancel(self):
            print "Here in cancel"
            try:
                vlcip = config.plugins.kodiplug.vlcip.value

                self.hostaddr = "http://" + vlcip + ":8080"
                password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, self.hostaddr, '','Admin')
                handler = urllib2.HTTPBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(handler)
                f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_stop")
                f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_empty")
#                self.session.nav.stopService()
#                self.session.nav.playService(self.srefOld)
            except:
                pass 
            if os.path.exists("/tmp/hls.avi"):
                   os.remove("/tmp/hls.avi")
            self.close()



    def stopDL(self):
                cmd = "rm -f " + self.svfile
                os.system(cmd)
                self.session.nav.playService(self.srefOld)
                cmd1 = "killall -9 rtmpdump"
                cmd2 = "killall -9 wget"
                os.system(cmd1)
                os.system(cmd2)
                self['info'].setText("Current download task stopped")
                self.close()

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def keyNumberGlobal(self, number):
        self['text'].number(number)

if NOSS == 0:
  class Playvid2(Screen, InfoBarMenu, InfoBarBase, SubsSupport, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):
    STATE_PLAYING = 1
    STATE_PAUSED = 2

    def __init__(self, session, name, url, desc):

		Screen.__init__(self, session)
		global SREF
                self.skinName = "Playvid2"
		title = "Play"
		self.sref=None
		self["title"] = Button(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
		self['key_yellow'] = Button(_('Subtitles'))
		InfoBarMenu.__init__(self)
		InfoBarNotifications.__init__(self)
		InfoBarBase.__init__(self)
		InfoBarShowHide.__init__(self)
		self.statusScreen = self.session.instantiateDialog(StatusScreen)
		##aspect ratio stuff
                try:
                    self.init_aspect = int(self.getAspect())
                except:
                    self.init_aspect = 0

                self.new_aspect = self.init_aspect
                ##end aspect ratio

		self["actions"] = ActionMap(["WizardActions", "MoviePlayerActions", "EPGSelectActions", "MediaPlayerSeekActions", "ColorActions", "InfobarShowHideActions", "InfobarSeekActions", "InfobarActions"],
		{
			"leavePlayer":		        self.cancel,
			"back":				self.cancel,
			"info":self.showinfo,
			"playpauseService":             self.playpauseService,
			"yellow":                          self.subtitles,
                        'down': self.av,##for aspect ratio
		}, -1)

		self.allowPiP = False
		initSubsSettings()
                SubsSupport.__init__(self, embeddedSupport=True, searchSupport=True)
                self.subs = True
		InfoBarSeek.__init__(self, actionmap = "MediaPlayerSeekActions")
                self.icount = 0
                self.name = name
                self.url = url
#ok                self.url = "rtmpe://fms-fra33.rtl.de/rtlnow/ swfVfy=1 playpath=mp4:2/V_398575_CEAT_E89903_93262_h264-mq_a535063e1a1fbf7249dbddf64452b6e6.f4v app=rtlnow/_definst_ pageUrl=http://rtl-now.rtl.de/p/ tcUrl=rtmpe://fms-fra33.rtl.de/rtlnow/ swfUrl=http://rtl-now.rtl.de/includes/vodplayer.swf"
#ok                self.url = "http://iphone.cdn.viasat.tv/iphone/008/00834/S83412_7dagemedsex_coasbb1elswjk4hj_Layer4_vod.m3u8"
#ok                self.url = "http://r8---sn-cu-cims.googlevideo.com/videoplayback?ratebypass=yes&id=c480126945309259&upn=cy2tR5f-Euc&expire=1394492898&ipbits=0&sparams=id%2Cip%2Cipbits%2Citag%2Cratebypass%2Csource%2Cupn%2Cexpire&fexp=917000%2C935501%2C914005%2C916611%2C936117%2C937417%2C913434%2C936910%2C936913%2C902907%2C934022&itag=22&sver=3&key=yt5&ip=86.129.227.24&ms=au&signature=248F501C2CC4F46437504012DDF0E517A936385C.713CC09A87E83950ACD42D60E12B68D467E107E7&mt=1394470293&mv=m&source=youtube"
#ok                self.url = "http://199.115.117.219//d/nbi6zz36qm752xrl7fzqr2llvh3gq2mynl3fitbewdtshbuk6rh3acul/A7r0n1nwb72G.mkv"
#                self.url = "http://2uscreativem3-vh.rai.it/i/podcastcdn/raiuno/sottovoce/Sottovoce_2014/4761193_1800.mp4/index_0_av.m3u8"
#                self.url = "https://openload.co/stream/bxQRLDZsSlg~1444840274~86.185.0.0~ooI8G6Rq?mime=true"
                print "Here in Playvid2 self.url = ", self.url
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                SREF = self.srefOld
                print "Here in Playvid2 SREF 2=", SREF
                self.desc = desc
                self.pcip = "None"
                self.state = self.STATE_PLAYING
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                self.onLayoutFinish.append(self.openTest)
    ##aspect ratio stuff
    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: _('4:3 Letterbox'),
         1: _('4:3 PanScan'),
         2: _('16:9'),
         3: _('16:9 always'),
         4: _('16:10 Letterbox'),
         5: _('16:10 PanScan'),
         6: _('16:9 Letterbox')}[aspectnum]

    def setAspect(self, aspect):
        map = {0: '4_3_letterbox',
         1: '4_3_panscan',
         2: '16_9',
         3: '16_9_always',
         4: '16_10_letterbox',
         5: '16_10_panscan',
         6: '16_9_letterbox'}
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        temp = int(self.getAspect())
        print self.getAspectString(temp)
        temp = temp + 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)
        print self.getAspectString(temp)
        self.statusScreen.setStatus(self.getAspectString(temp))



    def showinfo(self):
            debug=True
            try:

                 servicename,serviceurl=getserviceinfo(self.sref)
                 if servicename is not None:
                         sTitle=servicename
                 else:
                        sTitle=''

                 if serviceurl is not None:
                     sServiceref=serviceurl
                 else:
                   sServiceref=''

                 currPlay = self.session.nav.getCurrentService()

                 sTagCodec = currPlay.info().getInfoString(iServiceInformation.sTagCodec)
                 sTagVideoCodec = currPlay.info().getInfoString(iServiceInformation.sTagVideoCodec)
                 sTagAudioCodec = currPlay.info().getInfoString(iServiceInformation.sTagAudioCodec)

#return str(sTitle)
#message='remote keys help:\nmenu: subtitle player\nnumbers 1-6 seek back and forward\nleft and right:next and previous channel when playlist supported\ninfo:help\nup and cancel keys:exit to playlist'
                 message='stitle:'+str(sTitle)+"\n"+'sServiceref:'+str(sServiceref)+"\n"+'sTagCodec:'+str(sTagCodec)+"\n"+ 'sTagVideoCodec:'+str(sTagVideoCodec)+"\n"+'sTagAudioCodec :'+str(sTagAudioCodec)
                 from XBMCAddonsinfo import XBMCAddonsinfoScreen
                 self.session.open(XBMCAddonsinfoScreen,None,'XBMCAddonsPlayer',message)

            except:
                  pass

    def playpauseService(self):
		print "playpauseService"
		if self.state == self.STATE_PLAYING:
			self.pause()
			self.state = self.STATE_PAUSED
		elif self.state == self.STATE_PAUSED:
			self.unpause()
			self.state = self.STATE_PLAYING

    def pause(self):
                self.session.nav.pause(True)

    def unpause(self):
                self.session.nav.pause(False)

    def openTest(self):
            if "5002" in self.url:
                       print "In openTest streamlink self.url 2= ", self.url
                       ref = self.url
                       print "ref= ", ref
                       sref = eServiceReference(ref)
                       sref.setName(self.name)
		       self.session.nav.stopService()
		       self.session.nav.playService(sref)

            else:

                if "plugin://plugin.video.youtube" in self.url or "youtube.com/" in self.url :

                      from tube_resolver.plugin import getvideo
                      self.url,error = getvideo(self.url)
                      if error is not None or self.url is None:
                         print "failed to get valid youtube stream link"
                         return

                elif "pcip" in self.url:
                       n1 = self.url.find("pcip")
                       urlA = self.url
                       self.url = self.url[:n1]
                       self.pcip = urlA[(n1+4):]

                url = self.url
                name = self.name
                print "Here in Playvid name A =", name
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                name = name.replace("›", "-")
                name = name.replace(",", "-") 
                print "Here in Playvid name B2 =", name

                if url is not None:
                       url = str(url)
                       url = url.replace(":", "%3a")
                       url = url.replace("\\", "/")
                       print "url final= ", url
                       ref = "4097:0:1:0:0:0:0:0:0:0:" + url
                       print "ref= ", ref
                       sref = eServiceReference(ref)
                       sref.setName(self.name)
		       self.session.nav.stopService()
		       self.session.nav.playService(sref)

		else:
                       return

    def subtitles(self):
        try:
           self.subsMenu()
        except:
           self.session.open(MessageBox, _("Subtitle Player cannot be started."), MessageBox.TYPE_ERROR, timeout = 10)

    def subtitlesX(self):
			if not os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/DD_Subt/plugin.pyc"):
				self.session.open(MessageBox, _("Subtitle Player plugin is not installed\nPlease install it."), MessageBox.TYPE_ERROR, timeout = 10)
			else:
				found = 0
				pluginlist = []
				pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
				for plugin in pluginlist:
#					print "str(plugin.name) =", str(plugin.name)
                                        if "Subtitle player" in str(plugin.name):
						found = 1
						break
				if found == 0:
					self.session.open(MessageBox, _("Subtitle Player plugin Missing"), MessageBox.TYPE_ERROR, timeout = 5)
				else:
                                    try:
					plugin(session=self.session)	
                                    except:
                                        self.session.open(MessageBox, _("Subtitle Player not working"), MessageBox.TYPE_ERROR, timeout = 5)

    def cancel(self):
                if os.path.exists("/tmp/hls.avi"):
                        os.remove("/tmp/hls.avi")
                self.session.nav.stopService()
                print "Here in Playvid2 cancel SREF =", SREF
                self.session.nav.playService(SREF)
#                try:
                if self.pcip != "None":
                        url2 = "http://" + self.pcip + ":8080/requests/status.xml?command=pl_stop"
                        print "In Playvid2 url2 =", url2
                        resp = urlopen(url2)
#                except:
#                     pass
                ##aspect ratio
                if not self.new_aspect == self.init_aspect:
                    try:
                        self.setAspect(self.init_aspect)
                    except:
                        pass
                #aspect ratio
                self.close()

    def keyLeft(self):
		self["text"].left()

    def keyRight(self):
		self["text"].right()
	
    def keyNumberGlobal(self, number):
		self["text"].number(number)

if NOSS == 1:
  class Playvid2(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):
    STATE_PLAYING = 1
    STATE_PAUSED = 2

    def __init__(self, session, name, url, desc):

		global SREF
		Screen.__init__(self, session)
                self.skinName = "Playvid2"
		title = "Play"
		self.sref=None
		self["title"] = Button(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
		self['key_yellow'] = Button(_(' '))
		InfoBarMenu.__init__(self)
		InfoBarNotifications.__init__(self)
		InfoBarBase.__init__(self)
		InfoBarShowHide.__init__(self)
		self.statusScreen = self.session.instantiateDialog(StatusScreen)
		##aspect ratio stuff
                try:
                    self.init_aspect = int(self.getAspect())
                except:
                    self.init_aspect = 0

                self.new_aspect = self.init_aspect
                ##end aspect ratio

		self["actions"] = ActionMap(["WizardActions", "MoviePlayerActions", "EPGSelectActions", "MediaPlayerSeekActions", "ColorActions", "InfobarShowHideActions", "InfobarSeekActions", "InfobarActions"],
		{
			"leavePlayer":		        self.cancel,
			"back":				self.cancel,
			"info":self.showinfo,
			"playpauseService":             self.playpauseService,
			"yellow":                          self.subtitles,
                        'down': self.av,##for aspect ratio
		}, -1)

		self.allowPiP = False
		InfoBarSeek.__init__(self, actionmap = "MediaPlayerSeekActions")
                self.icount = 0
                self.name = name
                self.url = url
#ok                self.url = "rtmpe://fms-fra33.rtl.de/rtlnow/ swfVfy=1 playpath=mp4:2/V_398575_CEAT_E89903_93262_h264-mq_a535063e1a1fbf7249dbddf64452b6e6.f4v app=rtlnow/_definst_ pageUrl=http://rtl-now.rtl.de/p/ tcUrl=rtmpe://fms-fra33.rtl.de/rtlnow/ swfUrl=http://rtl-now.rtl.de/includes/vodplayer.swf"
#ok                self.url = "http://iphone.cdn.viasat.tv/iphone/008/00834/S83412_7dagemedsex_coasbb1elswjk4hj_Layer4_vod.m3u8"
#ok                self.url = "http://r8---sn-cu-cims.googlevideo.com/videoplayback?ratebypass=yes&id=c480126945309259&upn=cy2tR5f-Euc&expire=1394492898&ipbits=0&sparams=id%2Cip%2Cipbits%2Citag%2Cratebypass%2Csource%2Cupn%2Cexpire&fexp=917000%2C935501%2C914005%2C916611%2C936117%2C937417%2C913434%2C936910%2C936913%2C902907%2C934022&itag=22&sver=3&key=yt5&ip=86.129.227.24&ms=au&signature=248F501C2CC4F46437504012DDF0E517A936385C.713CC09A87E83950ACD42D60E12B68D467E107E7&mt=1394470293&mv=m&source=youtube"
#ok                self.url = "http://199.115.117.219//d/nbi6zz36qm752xrl7fzqr2llvh3gq2mynl3fitbewdtshbuk6rh3acul/A7r0n1nwb72G.mkv"
#                self.url = "http://2uscreativem3-vh.rai.it/i/podcastcdn/raiuno/sottovoce/Sottovoce_2014/4761193_1800.mp4/index_0_av.m3u8"
#                self.url = "https://openload.co/stream/bxQRLDZsSlg~1444840274~86.185.0.0~ooI8G6Rq?mime=true"
                print "Here in Playvid2 self.url = ", self.url
                self.desc = desc
                self.pcip = "None"
                self.state = self.STATE_PLAYING
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                SREF = self.srefOld
                print "Here in Playvid2 SREF 2=", SREF
                self.onLayoutFinish.append(self.openTest)
    ##aspect ratio stuff
    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: _('4:3 Letterbox'),
         1: _('4:3 PanScan'),
         2: _('16:9'),
         3: _('16:9 always'),
         4: _('16:10 Letterbox'),
         5: _('16:10 PanScan'),
         6: _('16:9 Letterbox')}[aspectnum]

    def setAspect(self, aspect):
        map = {0: '4_3_letterbox',
         1: '4_3_panscan',
         2: '16_9',
         3: '16_9_always',
         4: '16_10_letterbox',
         5: '16_10_panscan',
         6: '16_9_letterbox'}
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        temp = int(self.getAspect())
        print self.getAspectString(temp)
        temp = temp + 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)
        print self.getAspectString(temp)
        self.statusScreen.setStatus(self.getAspectString(temp))



    def showinfo(self):
            debug=True
            try:
 
                 servicename,serviceurl=getserviceinfo(self.sref)
                 if servicename is not None:
                         sTitle=servicename
                 else:
                        sTitle=''

                 if serviceurl is not None:
                     sServiceref=serviceurl
                 else:
                   sServiceref=''

                 currPlay = self.session.nav.getCurrentService()

                 sTagCodec = currPlay.info().getInfoString(iServiceInformation.sTagCodec)
                 sTagVideoCodec = currPlay.info().getInfoString(iServiceInformation.sTagVideoCodec)


#return str(sTitle)
#message='remote keys help:\nmenu: subtitle player\nnumbers 1-6 seek back and forward\nleft and right:next and previous channel when playlist supported\ninfo:help\nup and cancel keys:exit to playlist'
                 message='stitle:'+str(sTitle)+"\n"+'sServiceref:'+str(sServiceref)+"\n"+'sTagCodec:'+str(sTagCodec)+"\n"+ 'sTagVideoCodec:'+str(sTagVideoCodec)+"\n"+'sTagAudioCodec :'+str(sTagAudioCodec)
                 from XBMCAddonsinfo import XBMCAddonsinfoScreen
                 self.session.open(XBMCAddonsinfoScreen,None,'XBMCAddonsPlayer',message)

            except:
                  pass

    def playpauseService(self):
		print "playpauseService"
		if self.state == self.STATE_PLAYING:
			self.pause()
			self.state = self.STATE_PAUSED
		elif self.state == self.STATE_PAUSED:
			self.unpause()
			self.state = self.STATE_PLAYING

    def pause(self):
                self.session.nav.pause(True)

    def unpause(self):
                self.session.nav.pause(False)

    def openTest(self):
            if "5002" in self.url:
                       print "In openTest streamlink self.url 2= ", self.url
                       ref = self.url
                       print "ref= ", ref
                       sref = eServiceReference(ref)
                       sref.setName(self.name)
		       self.session.nav.stopService()
		       self.session.nav.playService(sref)

            else:

                if "plugin://plugin.video.youtube" in self.url or "youtube.com/" in self.url :

                      from tube_resolver.plugin import getvideo
                      self.url,error = getvideo(self.url)
                      if error is not None or self.url is None:
                         print "failed to get valid youtube stream link"
                         return 

                elif "pcip" in self.url:
                       n1 = self.url.find("pcip")
                       urlA = self.url
                       self.url = self.url[:n1]
                       self.pcip = urlA[(n1+4):]

                url = self.url
                name = self.name
                print "Here in Playvid name A =", name
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                name = name.replace("›", "-")
                name = name.replace(",", "-") 
                print "Here in Playvid name B2 =", name

                if url is not None:
                       url = str(url)
                       url = url.replace(":", "%3a")
                       url = url.replace("\\", "/")
                       print "url final= ", url

                       ref = "4097:0:1:0:0:0:0:0:0:0:" + url
                       print "ref= ", ref
                       sref = eServiceReference(ref)
                       sref.setName(self.name)
		       self.session.nav.stopService()
		       self.session.nav.playService(sref)

		else:
                       return

    def subtitles(self):
        self.session.open(MessageBox, _("Please install script.module.SubSupport."), MessageBox.TYPE_ERROR, timeout = 10)

    def cancel(self):
                if os.path.exists("/tmp/hls.avi"):
                        os.remove("/tmp/hls.avi")
                self.session.nav.stopService()
                print "Here in Playvid2 cancel SREF =", SREF
                self.session.nav.playService(SREF)
#                try:
                if self.pcip != "None":
                        url2 = "http://" + self.pcip + ":8080/requests/status.xml?command=pl_stop"
                        print "In Playvid2 url2 =", url2
                        resp = urlopen(url2)
#                except:
#                     pass
                ##aspect ratio
                if not self.new_aspect == self.init_aspect:
                    try:
                        self.setAspect(self.init_aspect)
                    except:
                        pass
                #aspect ratio
                self.close()

    def keyLeft(self):
		self["text"].left()
	
    def keyRight(self):
		self["text"].right()
	
    def keyNumberGlobal(self, number):
		self["text"].number(number)


class Showrtmp(Screen):

    def __init__(self, session, name, url, desc):
		Screen.__init__(self, session)
                self.skinName = "Showrtmp"
                title = "Play"
                self.setTitle(title)
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["key_red"] = Button(_("Exit"))
		self["key_green"] = Button(_("Download"))
		self["key_yellow"] = Button(_("Play"))
		self["key_blue"] = Button(_("Stop Download"))
                self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
		{
			"red": self.close,
			"green": self.okClicked,
			"yellow": self.play,
			"blue": self.stopdl,
			"cancel": self.cancel,
			"ok": self.okClicked,
		}, -2)
                self.icount = 0
                self.name = name
                self.url = url
                txt = "Video stream rtmp.\n\n\nMust do (1) Download  (2) Play.\n\n"
                self["info"].setText(txt)
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                self.onLayoutFinish.append(self.getrtmp)

    def getrtmp(self):
                       pic1 = THISPLUG + "/images/default.png"
                       self["pixmap"].instance.setPixmapFromFile(pic1)
                       params = self.url
                       print "params A=", params
                       params = params.replace("-swfVfy", " --swfVfy")
                       params = params.replace("-playpath", " --playpath")
                       params = params.replace("-app", " --app")
                       params = params.replace("-pageUrl", " --pageUrl")
                       params = params.replace("-tcUrl", " --tcUrl")
                       params = params.replace("-swfUrl", " --swfUrl")
                       print "params B=", params


                       fold = config.plugins.kodiplug.cachefold.value + "/movies"
                       name = self.name.replace("/media/hdd/movies/", "")
                       name = name.replace(":", "-")
                       name = name.replace("&", "-")
                       name = name.replace(" ", "-")
                       name = name.replace("/", "-")
                       name = name.replace(".", "-")
                       self.name = name
                       svfile = fold + "/xbmc/vid/savedfile.mpg"
                       self.svf = svfile
                       self.urtmp = "rtmpdump -r " + params + " -o '" + svfile + "'"

    def okClicked(self):
                self["info"].setText("Downloading ....")
                fold = config.plugins.kodiplug.cachefold.value + "/movies"
                name = self.name.replace("/media/hdd/movies/", "")
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                name = name.replace(".", "-")
                svfile = fold + "/xbmc/vid/savedfile.mpg"
                self.svf = svfile

                cmd = "rm " + svfile
                os.system(cmd)
                JobManager.AddJob(downloadJob(self, self.urtmp, svfile, 'Title 1')) 

                self.LastJobView()


    def LastJobView(self):
		currentjob = None
		for job in JobManager.getPendingJobs():
			currentjob = job

		if currentjob is not None:
			self.session.open(JobViewNew, currentjob)

    def play(self):
          if os.path.exists(self.svf):
                svfile = self.svf
                desc = " "
                self.session.open(Playvid2, self.name, svfile, desc)
                #runKDplayer(self.session,name,svfile,desc)
          else:
                txt = "Download Video first."
                self["info"].setText(txt)


    def cancel(self):
	        self.session.nav.playService(self.srefOld)
                self.close()

    def stopdl(self):
                svfile = self.svf
                cmd = "rm " + svfile
                os.system(cmd)
                self.session.nav.playService(self.srefOld)
                cmd1 = "killall -9 rtmpdump"
                cmd2 = "killall -9 wget"
                os.system(cmd1)
                os.system(cmd2)
                self.close()


    def keyLeft(self):
		self["text"].left()
	
    def keyRight(self):
		self["text"].right()

    def keyNumberGlobal(self, number):
		#print "pressed", number
		self["text"].number(number)

class Showrtmp2XX(Screen):
    skin = """
                <screen name="Showrtmp2" position="center,center" size="1280,720" title="  " >
                        <ePixmap position="0,0" zPosition="-2" size="1280,720" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/" + ADDONCAT + "Addons/images/panel3.png" />
                        <ePixmap position="942,372" size="200,200" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/" + ADDONCAT + "Addons/images/default.png" alphatest="on" />
                        <widget name="info" position="120,100" zPosition="4" size="500,240" font="Regular;25" foregroundColor="#ffffff" backgroundColor="#40000000" transparent="1" halign="center" valign="center" />
                        <eLabel position="150,660" zPosition="1" size="200,30" backgroundColor="#f23d21" /> 
                        <eLabel position="152,662" zPosition="1" size="196,26" backgroundColor="#40000000" /> 
                        <eLabel position="350,660" zPosition="1" size="200,30" backgroundColor="#389416" />
                        <eLabel position="352,662" zPosition="1" size="196,26" backgroundColor="#40000000" />
                        <eLabel position="550,660" zPosition="1" size="200,30" backgroundColor="#bab329" />
                        <eLabel position="552,662" zPosition="1" size="196,26" backgroundColor="#40000000" />
                        <eLabel position="750,660" zPosition="1" size="200,30" backgroundColor="#0064c7" />
                        <eLabel position="752,662" zPosition="1" size="196,26" backgroundColor="#40000000" />
                        <widget name="key_red" position="150,660" size="200,30" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> 
                        <widget name="key_green" position="350,660" size="200,30" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> 
                        <widget name="key_yellow" position="550,660" size="200,30" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />
                        <widget name="key_blue" position="750,660" size="200,30" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />
                        <ePixmap position="100,650" zPosition="1" size="50,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/" + ADDONCAT + "Addons/images/Exit2.png" />
                </screen>"""

    def __init__(self, session, name, url, desc):
		Screen.__init__(self, session)
                self.skinName = "Showrtmp2"
                title = "Play"
                self.setTitle(title)
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["key_red"] = Button(_("Exit"))
		self["key_green"] = Button(_("Play"))
		self["key_yellow"] = Button(_("Play"))
		self["key_blue"] = Button(_("Stop Download"))
                self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
		{
			"red": self.close,
			"green": self.okClicked,
			"yellow": self.play,
			"blue": self.stopdl,
			"cancel": self.cancel,
			"ok": self.okClicked,
		}, -2)
                self.icount = 0
                self.name = name
                self.url = url
                print "here in Showrtmp2"
                self.svf = " "
                self["info"].setText(str(name))
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                self.onLayoutFinish.append(self.getrtmp)

    def getrtmp(self):
                       pic1 = THISPLUG + "/images/default.png"
                       self["pixmap"].instance.setPixmapFromFile(pic1)
                       params = self.url
                       print "params A=", params
                       params = params.replace("swfVfy", "--swfVfy")
                       params = params.replace("playpath", "--playpath")
                       params = params.replace("app", "--app")
                       params = params.replace("pageUrl", "--pageUrl")
                       params = params.replace("tcUrl", "--tcUrl")
                       params = params.replace("swfUrl", "--swfUrl")
                       print "params B=", params

                       n1 = params.find(" ")
                       if n1<0:
                             params = "'" + params + "'"
                       else:
                             url = params[:n1]
                             url = "'" + url + "'"
                             prest = params[n1:]
                             params = url + prest

                       name = self.name
                       name = name.replace(":", "-")
                       name = name.replace("&", "-")
                       name = name.replace(" ", "-")
                       name = name.replace("/", "-")
                       name = name.replace(".", "-")
                       self.name = name

                       if not fileExists("/tmp/vid"):
			   os.system("/usr/bin/mkfifo /tmp/vid")

                       local_file = "/tmp/vid"

#                       self.urtmp = "rtmpdump -v -r " + params + " -o '" + local_file + "'"
                       self.urtmp = "rtmpdump -r rtmpe://fms-fra33.rtl.de/rtlnow/ --swfVfy=1 --playpath=mp4:2/V_398575_CEAT_E89903_93262_h264-mq_a535063e1a1fbf7249dbddf64452b6e6.f4v --app=rtlnow/_definst_ --pageUrl=http://rtl-now.rtl.de/p/ --tcUrl=rtmpe://fms-fra33.rtl.de/rtlnow/ --swfUrl=http://rtl-now.rtl.de/includes/vodplayer.swf -o /tmp/vid.mpg"

    def okClicked(self):
                self["info"].setText(" ")
                fold = config.plugins.kodiplug.cachefold.value + "/movies"
                name = self.name.replace("/media/hdd/movies/", "")
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                name = name.replace(".", "-")

                svfile = "/tmp/vid"
                self.svf = svfile
                print "self.urtmp =", self.urtmp
#                JobManager.AddJob(downloadJob(self, self.urtmp, svfile, 'Title 1'))
                os.system(self.urtmp)

#                self.play()


    def play(self):
#         try:
                print "Showrtmp here 2"
                svfile = self.svf
#                pvd = Playvid(self.session, self.name, svfile)
                desc = " "
                self.session.open(Playvid, self.name, svfile, desc)
#                pvd.openTest()

#         except:
#                return

    def cancel(self):
	        self.session.nav.playService(self.srefOld)
                svfile = self.svf
                cmd = "rm " + svfile + " &"
                os.system(cmd)
                self.session.nav.playService(self.srefOld)
                cmd1 = "killall -9 rtmpdump &"
                cmd2 = "killall -9 wget"
                os.system(cmd1)
                os.system(cmd2)
                self.close()


    def keyLeft(self):
		self["text"].left()

    def keyRight(self):
		self["text"].right()

    def keyNumberGlobal(self, number):
		#print "pressed", number
		self["text"].number(number)


class Showrtmp2X(Screen, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):

#Now same as class Playvid

    def __init__(self, session, name, url, desc):

		Screen.__init__(self, session)
                self.skinName = "MoviePlayer"
		title = "Play"
		self["title"] = Button(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
		InfoBarNotifications.__init__(self)
		InfoBarBase.__init__(self)
		InfoBarShowHide.__init__(self)
		self["actions"] = ActionMap(["WizardActions", "MoviePlayerActions", "EPGSelectActions", "MediaPlayerSeekActions", "ColorActions", "InfobarShowHideActions", "InfobarActions"],
		{
			"leavePlayer":		        self.cancel,
			"back":				self.cancel,
		}, -1)

		self.allowPiP = False
		InfoBarSeek.__init__(self, actionmap = "MediaPlayerSeekActions")
                self.icount = 0
                self.name = name
                self.url = url
                print "Here in Showrtmp2 self.url = ", self.url
                self.desc = desc
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                self.onLayoutFinish.append(self.openTest)

    def openTest(self):
                url = self.url
                name = self.name
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                ref = eServiceReference(0x1001, 0, url)
		ref.setName(name)
		self.session.nav.stopService()
		self.session.nav.playService(ref)


    def cancel(self):
                self.session.nav.stopService()
                self.session.nav.playService(self.srefOld)
                self.close()


    def keyLeft(self):
		self["text"].left()

    def keyRight(self):
		self["text"].right()
	
    def keyNumberGlobal(self, number):
		self["text"].number(number)



class downloadJob(Job):
	def __init__(self, toolbox, cmdline, filename, filetitle):
		Job.__init__(self, _("Saving Video"))
		self.toolbox = toolbox
		self.retrycount = 0
                downloadTask(self, cmdline, filename, filetitle)

	def retry(self):
		assert self.status == self.FAILED
		self.retrycount += 1
		self.restart()

class downloadTask(Task):
	ERROR_CORRUPT_FILE, ERROR_RTMP_ReadPacket, ERROR_SEGFAULT, ERROR_SERVER, ERROR_UNKNOWN = range(5)
	def __init__(self, job, cmdline, filename, filetitle):
		Task.__init__(self, job, filetitle)
                self.setCmdline(cmdline)
		self.filename = filename
		self.toolbox = job.toolbox
		self.error = None
		self.lasterrormsg = None

	def processOutput(self, data):
		try:
			if data.endswith('%)'):
				startpos = data.rfind("sec (")+5
				if startpos and startpos != -1:
					self.progress = int(float(data[startpos:-4]))
			elif data.find('%') != -1:
				tmpvalue = data[:data.find("%")]
				tmpvalue = tmpvalue[tmpvalue.rfind(" "):].strip()
				tmpvalue = tmpvalue[tmpvalue.rfind("(")+1:].strip()
				self.progress = int(float(tmpvalue))
			else:
				Task.processOutput(self, data)
		except Exception, errormsg:
			Task.processOutput(self, data)

	def processOutputLine(self, line):
			self.error = self.ERROR_SERVER
			
	def afterRun(self):
		pass

####################################

class RSList(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
#		self.l.setItemHeight(40)
#		self.l.setFont(0, gFont("Regular", 30))
		
		if config.plugins.kodiplug.skinres.value == "fullhd":
		       self.l.setItemHeight(100)
		       textfont = int(40)
		else:
		       self.l.setItemHeight(60)
		       textfont = int(25)
                self.l.setFont(0, gFont("Regular", textfont))

##############################################################################

def RSListEntry(download):
	res = [(download)]

        white = 0xffffff
        green = 0x389416
        black = 0x40000000
        yellow = 0xe5b243

        if config.plugins.kodiplug.skinres.value == "fullhd": 
               res.append(MultiContentEntryText(pos=(0, 0), size=(975, 60), text=download, color=white, color_sel = yellow, backcolor = black, backcolor_sel = black))
        else:
               res.append(MultiContentEntryText(pos=(0, 0), size=(650, 40), text=download, color=white, color_sel = yellow, backcolor = black, backcolor_sel = black))

	##print "res =", res
        return res

##############################################################################
def showlist(data, list):
#                       self.list1 = []
#                       list = List(list1)
#                       list = RSList([])

                       icount = 0
                       print "data here 1=", data
                       plist = []
                       for line in data:
                               name = data[icount]
                               print "icount, name =", icount, name
                               plist.append(RSListEntry(name))
                               icount = icount+1

		       list.setList(plist)
#######################################################

class RSListX(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, True, eListboxPythonMultiContent)
		if config.plugins.kodiplug.skinres.value == "fullhd":
		       self.l.setItemHeight(100)
		       textfont = int(35)
		else:
		       self.l.setItemHeight(100)
		       textfont = int(config.plugins.kodiplug.textfont.value)
                self.l.setFont(0, gFont("Regular", textfont))

def RSListEntryX(download):
	res = [(download)]

        white = 0xffffff
        grey = 0xb3b3b9
        green = 0x389416
        black = 0x000000
        yellow = 0xe5b243
        blue = 0x002d39
        red = 0xf07655
        col = int(config.plugins.kodiplug.textcol.value, 16)
        colsel = int(config.plugins.kodiplug.textsel.value, 16)
        backcol = int(config.plugins.kodiplug.listcol.value, 16)
        backsel = int(config.plugins.kodiplug.listcol.value, 16)
#        res.append(MultiContentEntryText(pos=(0, 0), size=(650, 40), text=download, color=col, color_sel = colsel, backcolor = backcol, backcolor_sel = backcol))
##        res.append(MultiContentEntryText(pos=(0, 0), size=(1000, 40), text=download, color=col, color_sel = colsel, backcolor = backcol, backcolor_sel = backcol))
        res.append(MultiContentEntryText(pos=(0, 0), size=(1700, 45), text=download, color=col, color_sel = colsel, backcolor = backcol, backcolor_sel = backcol))

        return res

def showlistX(data, list):
                       icount = 0
                       plist = []
                       for line in data:
#                               print "In showlist line =", line
                               name = data[icount]
                               plist.append(RSListEntry(name))
                               icount = icount+1

		       list.setList(plist)


#################

def getserviceinfo(sref):## this def returns the current playing service name and stream_url from give sref
              try:
	        p=ServiceReference(sref)
	        servicename=str(p.getServiceName())
	        serviceurl=str(p.getPath())
	        return servicename,serviceurl
	      except:
                return None,None

def getVideoUrl(vid):
		VIDEO_FMT_PRIORITY_MAP = {
			'38' : 1, #MP4 Original (HD)
			'37' : 2, #MP4 1080p (HD)
			'22' : 3, #MP4 720p (HD)
			'18' : 4, #MP4 360p
			'35' : 5, #FLV 480p
			'34' : 6, #FLV 360p
		}
		video_url = None
		video_id = vid

		# Getting video webpage
		#URLs for YouTube video pages will change from the format http://www.youtube.com/watch?v=ylLzyHk54Z0 to http://www.youtube.com/watch#!v=ylLzyHk54Z0.
		watch_url = 'http://www.youtube.com/watch?v=%s&gl=US&hl=en' % video_id
		watchrequest = Request(watch_url, None, std_headers)
		try:
			print "[MyTube] trying to find out if a HD Stream is available",watch_url
			watchvideopage = urlopen(watchrequest).read()
		except (URLError, HTTPException, socket.error), err:
			print "[MyTube] Error: Unable to retrieve watchpage - Error code: ", str(err)
			return None

		# Get video info
		for el in ['&el=embedded', '&el=detailpage', '&el=vevo', '']:
			info_url = ('http://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en' % (video_id, el))
			request = Request(info_url, None, std_headers)
			try:
				infopage = urlopen(request).read()
				videoinfo = parse_qs(infopage)
				if ('url_encoded_fmt_stream_map' or 'fmt_url_map') in videoinfo:
					break
			except (URLError, HTTPException, socket.error), err:
				print "[MyTube] Error: unable to download video infopage",str(err)
				return None

		if ('url_encoded_fmt_stream_map' or 'fmt_url_map') not in videoinfo:
			# Attempt to see if YouTube has issued an error message
			if 'reason' not in videoinfo:
				print '[MyTube] Error: unable to extract "fmt_url_map" or "url_encoded_fmt_stream_map" parameter for unknown reason'
			else:
				reason = unquote_plus(videoinfo['reason'][0])
				print '[MyTube] Error: YouTube said: %s' % reason.decode('utf-8')
			return None

		video_fmt_map = {}
		fmt_infomap = {}
		if videoinfo.has_key('url_encoded_fmt_stream_map'):
			tmp_fmtUrlDATA = videoinfo['url_encoded_fmt_stream_map'][0].split(',')
		else:
			tmp_fmtUrlDATA = videoinfo['fmt_url_map'][0].split(',')
		for fmtstring in tmp_fmtUrlDATA:
			fmturl = fmtid = ""
			if videoinfo.has_key('url_encoded_fmt_stream_map'):
				try:
					for arg in fmtstring.split('&'):
						if arg.find('=') >= 0:
							print arg.split('=')
							key, value = arg.split('=')
							if key == 'itag':
								if len(value) > 3:
									value = value[:2]
								fmtid = value
							elif key == 'url':
								fmturl = value

					if fmtid != "" and fmturl != "" and VIDEO_FMT_PRIORITY_MAP.has_key(fmtid):
						video_fmt_map[VIDEO_FMT_PRIORITY_MAP[fmtid]] = { 'fmtid': fmtid, 'fmturl': unquote_plus(fmturl)}
						fmt_infomap[int(fmtid)] = "%s" %(unquote_plus(fmturl))
					fmturl = fmtid = ""

				except:
					print "error parsing fmtstring:",fmtstring
					return None

			else:
				(fmtid,fmturl) = fmtstring.split('|')
			if VIDEO_FMT_PRIORITY_MAP.has_key(fmtid) and fmtid != "":
				video_fmt_map[VIDEO_FMT_PRIORITY_MAP[fmtid]] = { 'fmtid': fmtid, 'fmturl': unquote_plus(fmturl) }
				fmt_infomap[int(fmtid)] = unquote_plus(fmturl)
		print "[MyTube] got",sorted(fmt_infomap.iterkeys())
		if video_fmt_map and len(video_fmt_map):
			print "[MyTube] found best available video format:",video_fmt_map[sorted(video_fmt_map.iterkeys())[0]]['fmtid']
			best_video = video_fmt_map[sorted(video_fmt_map.iterkeys())[0]]
			video_url = "%s" %(best_video['fmturl'].split(';')[0])
			print "[MyTube] found best available video url:",video_url
		else:
                        return None
		return video_url



#######################################

def addstreamboq(bouquetname=None):
           boqfile="/etc/enigma2/bouquets.tv"
           if not os.path.exists(boqfile):
              pass
           else:
              fp=open(boqfile,"r")
              lines=fp.readlines()
              fp.close()
              add=True
              for line in lines:

                 if "userbouquet."+bouquetname+".tv" in line :

                    add=False
                    break
           if add==True:   
              fp=open(boqfile,"a")
              fp.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.%s.tv" ORDER BY bouquet\n'% bouquetname) 
              fp.close()
              add=True


def stream2bouquet(url=None,name=None,bouquetname=None):
          error='none' 
          bouquetname='XBMCAddons'
          fileName ="/etc/enigma2/userbouquet.%s.tv" % bouquetname
          out = '#SERVICE 4097:0:0:0:0:0:0:0:0:0:%s:%s\r\n' % (urllib.quote(url), urllib.quote(name))
          try:
              addstreamboq(bouquetname)

              if not os.path.exists(fileName):
                 fp = open(fileName, 'w')
                 fp.write("#NAME %s\n"%bouquetname) 
                 fp.close()
                 fp = open(fileName, 'a')
                 fp.write(out)
              else:
                 fp=open(fileName,'r')
                 lines=fp.readlines()
                 fp.close()
                 for line in lines:
                     if out in line:
                        error=(_('Stream already added to bouquet'))
                        return error



                 fp = open(fileName, 'a')
                 fp.write(out)
              fp.write("")
              fp.close()

	  except:

             error=(_('Adding to bouquet failed'))

	  return error

##added for need of aspect ratio
class StatusScreen(Screen):

    def __init__(self, session):
        desktop = getDesktop(0)
        size = desktop.size()
        self.sc_width = size.width()
        self.sc_height = size.height()
        statusPositionX = 50
        statusPositionY = 100
        self.delayTimer = eTimer()
        try:
               self.delayTimer_conn = self.delayTimer.timeout.connect(self.hideStatus)
        except AttributeError:
               self.delayTimer.callback.append(self.hideStatus)

        self.delayTimerDelay = 1500
        self.shown = True
        self.skin = '\n            <screen name="StatusScreen" position="%s,%s" size="%s,90" zPosition="0" backgroundColor="transparent" flags="wfNoBorder">\n                    <widget name="status" position="0,0" size="%s,70" valign="center" halign="left" font="Regular;22" transparent="1" foregroundColor="yellow" shadowColor="#40101010" shadowOffset="3,3" />\n            </screen>' % (str(statusPositionX),
         str(statusPositionY),
         str(self.sc_width),
         str(self.sc_width))
        Screen.__init__(self, session)
        self.stand_alone = True
        print 'initializing status display'
        self['status'] = Label('')
        self.onClose.append(self.__onClose)

    def setStatus(self, text, color = 'yellow'):
        self['status'].setText(text)
        self['status'].instance.setForegroundColor(parseColor(color))
        self.show()
        self.delayTimer.start(self.delayTimerDelay, True)

    def hideStatus(self):
        self.hide()
        self['status'].setText('')

    def __onClose(self):
        self.delayTimer.stop()
        del self.delayTimer
