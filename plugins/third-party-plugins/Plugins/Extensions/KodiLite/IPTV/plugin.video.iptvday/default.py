#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, xpath, xbmc
libs = sys.argv[0].replace("default.py", "resources/lib")
if os.path.exists(libs):
   sys.path.append(libs)
print "Here in default-py sys.argv =", sys.argv
if ("?plugin%3A%2F%2F" in sys.argv[2]) or ("?plugin://" in sys.argv[2]):
       argtwo = sys.argv[2]
       n2 = argtwo.find("?", 0)
       n3 = argtwo.find("?", (n2+2))
       if n3<0: 
              sys.argv[0] = argtwo
              sys.argv[2] = ""
       else:
              sys.argv[0] = argtwo[:n3]
              sys.argv[2] = argtwo[n3:]
       sys.argv[0] = sys.argv[0].replace("?", "")

else:
       sys.argv[0] = sys.argv[0].replace('/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/IPTV/', 'plugin://') 
       sys.argv[0] = sys.argv[0].replace('default.py', '')
print "Here in default-py sys.argv B=", sys.argv



import xbmc,xbmcplugin
import xbmcgui
import sys
import urllib, urllib2
import time
import re
from htmlentitydefs import name2codepoint as n2cp
import httplib
import urlparse
from os import path, system
import socket
from urllib2 import Request, URLError, urlopen
from urlparse import parse_qs
from urllib import unquote_plus

from KW import KW
print "KW =", KW
from datetime import datetime
import base64

thisPlugin = int(sys.argv[1])
addonId = "plugin.video.iptvday"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)
       

def getUrl(url):
        print "Here in getUrl url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

	
def showContent():
                name = "Iptvday"
                url = "https://iptvday.blogspot.co.uk/"
                pic = " "
                addDirectoryItem(name, {"name":name, "url":url, "mode":1}, pic)
                """
                name = "Iptvfilmover"
                url = "http://iptv.filmover.com/"
                pic = " "
                addDirectoryItem(name, {"name":name, "url":url, "mode":5}, pic)
                """
                xbmcplugin.endOfDirectory(thisPlugin)

def checkstat(url):
                url = url.replace("get.php", "player_api.php")
                url = url.replace("&type=m3u", "")
                print "In status url =", url
                try:
                       content = getUrl(url)
                       print "In status content =", content 
                       if "Active" in content:
                              return "yes"
                       else:
                              return "no"
                except:
                       return "no"

                     
def fullepg(url):
                print "In Videos2 url =", url
                url = url.replace("get.php", "xmltv.php")
                url = url.replace("&type=m3u", "")
                lastchn = " "
                xn = 0
                if xn == 0:
#                try:
                       lines = []
                       content = getUrl(url)
                       print "In videos2 fullepg content =", content
                       regexcat = '<programme start="(.*?)" stop="(.*?)" channel="(.*?)".*?tle>(.*?)</title>'
                       match = re.compile(regexcat,re.DOTALL).findall(content)
                       print "In Videos2 match =", match
                       for start, stop, channel, title in match:
                               if channel == lastchn:
                                      channel = " "
                                      line1 = " "
                               else:       
                                      lastchn = channel
                                      line1 = "\tCh:" + channel
                               lines.append(line1)
                                                             
                               startst =  start[6:8] + "." + start[4:6] + "." + start[:4] + "-" + start[8:12]
                               stopst =  stop[6:8] + "." + stop[4:6] + "." + stop[:4] + "-" + stop[8:12]
                               line2 =startst + "->" + stopst
                               lines.append(line2)
                               line3 = title + "\n\n"
                               lines.append(line3)
                       epgtxt = ""
                       for line in lines:
                              epgtxt = epgtxt + "\n" + line 
                       return epgtxt
                               
#                except:
#                       return

                       
def epg(name):
                
                print "In epg name =", name
                items = name.split("___")
                chname = items[0].replace("+", " ") 
                print "In epg chname =", chname
                f1=open("/tmp/epgtxt","r")
                etxt = f1.read()
                lines = etxt.splitlines()
                epgtxt = []
                for line in lines:
                       epgtxt.append(line)
                print "In epg epgtxt =", epgtxt
                n1 = 0
#                print "epgtxt 2=", epgtxt
                for line in epgtxt:
                        print "In Videos2 epg n1 =", n1
                        print "In Videos2 epg line =", line
                        print "In Videos2 epg chname 2=", chname
                        if chname in line:
                                print "In Videos2 epg line 2=", line
                                print "In Videos2 epg chname 4=", chname
                                nstart = n1
                                break
                        n1 = n1+1 
                try:               
                   print "nstart =", nstart 
                   n1 = 0
                   nst = nstart+1
                   for line in epgtxt: 
                        print "In Videos2 epg n1 2=", n1
                        print "In Videos2 epg line 3=", line
                        if n1<nst:
                                n1 = n1+1
                                continue        
                        if "Ch:" in line:
                                nend = n1-1
                                break
                        n1 = n1+1        
                   print "In Videos2 epg nstart, nend =", nstart, nend
                   elines = []
                   n1 = 0
                   for line in self.epgtxt:
                        if n1<nstart:
                               n1 = n1+1
                               continue 
                        elif n1>nend:
                               n1 = n1+1
                               continue 
                        else:
                               n1 = n1+1
                               elines.append(line)
                   print "In Videos2 epg elines =", elines
                   return elines
                except:
                       lines = ["Sorry no epg available",]
                       return lines

def bouquet():
                """
#NAME Example
#SERVICE 1:0:1:0:0:0:0:0:0:0:http%3A//painel.iptvmove.com%3A25461/live/Jorge.jocelio/Jorge.jocelio/1116.ts
#DESCRIPTION BigBrotherBrasil 2018
#SERVICE 1:0:1:0:0:0:0:0:0:0:http%3A//painel.iptvmove.com%3A25461/live/Jorge.jocelio/Jorge.jocelio/1215.ts
#DESCRIPTION ALL Sports HD
#SERVICE 1:0:1:0:0:0:0:0:0:0:http%3A//painel.iptvmove.com%3A25461/live/Jorge.jocelio/Jorge.jocelio/1354.ts

                """
                name1 = self.name1.replace(".m3u", "")
                if "###" in name1:
                        name = name1.split("###")[1]
                else:
                        name = name1
                print "In Videos2 name =", name
                self.session.openWithCallback(self.doRename,InputBox,text=name, title = "Change bouquet name", windowTitle=_("Bouquet name"))

def doRename(newname):
           if newname is None:
                return
           else:
                bqname = "userbouquet." + newname + ".tv"
                path = "/etc/enigma2/" + bqname
                f = open(path, "w")
                line = "#NAME " + newname + "\n"
                f.write(line) 
                url = self.url1
                print "In Videos2 url =", url
                content = getUrl(url)
                print "In Videos2 content B =", content
                regexcat = '\#EXTINF\:(.*?)\\n(.*?)\\n'
                match = re.compile(regexcat,re.DOTALL).findall(content)
                print "In Videos2 match =", match
                for name, url in match:
                        url1 = url.replace("\r", "")
                        url1 = url1.replace("\n", "")
                        items = name.split(",")
                        name1 = items[1].replace("\r", "")
                        name1 = name1.replace("\n", "")
                        url1 = url1.replace(":", "%3a")
#                        line = "#SERVICE 1:0:1:0:0:0:0:0:0:0:" + url1 + ":" + name1 + "\n"
                        line = "#SERVICE 4097:0:1:0:0:0:0:0:0:0:" + url1 + "\n"
                        f.write(line)
                        line = "#DESCRIPTION " + name1 + "\n"
                        f.write(line)

                f.close()
                os.system("wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &")
                print "[IPTVbouquet] Bouquet installed in Channellist Favourite"
                txt = "Bouquet " + bqname + " installed in Channellist Favourite"
                lines = [txt,]
                self.session.open(statusinfo, lines)

def live():
                #player_api.php?username=X&password=X&action=get_live_streams 
                url = self.url1
                print "In Videos2 live url =", url
                url = url.replace("get.php", "player_api.php")
                url = url.replace("&type=m3u", "&action=get_live_streams")
                try:
                       content = getUrl(url)
                       print "In videos2 live content =", content
                       self.livelist = content
                except:
                       return

def status(url):
                url = url.replace("get.php", "player_api.php")
                url = url.replace("&type=m3u", "")
                print "In status url =", url
                try:
                       content = getUrl(url)
                       print "In status content =", content 
                       content = str(content).replace('{"user_info":{', '')
                       lines = content.split(",")
                       print "In status lines =", lines
                       data = ""
                       data = data + "     USER INFO"
                       data = data + "\n-------------------------"
                       for line in lines:
                             if "exp_date" in line:
                                    print "In status line =", line
                                    dates =  line.split(":")
                                    print "In status dates =", dates
                                    exp_date = dates[1]
                                    exp_date = exp_date.replace('"', '')
                                    tconv = datetime.fromtimestamp(float(exp_date)).strftime('%c')
                                    line = '"exp_date" : "' + str(tconv) + '"'
                                    print "In status line 3=", line
                                    data = data + "\n" + line
                             elif "status" in line:
                                    data = data + "\n" + line
                             elif "active_con" in line:
                                    data = data + "\n" + line
                             elif "max_connection" in line:
                                    data = data + "\n" + line
                             else:
                                    continue
                       data = data + "\n-------------------------"
                       print "In Videos1 status data =", data
                       return data

                except:
                       return "Sorry no status data"



def getVideos1(name, url):
                print "In getVideos1 name =", name
                print "In getVideos1 url =", url
                content = getUrl(url)

                print "getVideos1 content =", content
                regexcat = "rel='tag'>m3u playlist<.*?<a href='(.*?)'"
                match = re.compile(regexcat,re.DOTALL).findall(content)
                print "In Videos2 match =", match
                for url in match:
                     name = url
                     if not "free-iptv-links" in url:
                            continue
                     pic = " "
	             addDirectoryItem(name, {"name":name, "url":url, "mode":11}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)
#mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
def getVideos11(name1, url):
                content = getUrl(url)
                print "content A =", content
                start = 0
                i1 = 0
                while i1<20:
                     j1 = content.find("type=m3u", start)
                     if j1<0: 
                               break                       
                     j2 = content.rfind("http", 0, j1)
                     url = content[j2:(j1+8)]
                     print "In Videos1 url 2=", url
                     url = url.replace("&amp;", "&")
                     url1 = url.replace(" ", "")
                     if checkstat(url1) == "no":
                             i1 = i1+1
                             start = j1+7
                             continue
                     name = url1
                     n1 = name.find("http://", 0)
                     n2 = name.find("/", (n1+10))
                     n3 = name.find("usern", (n2+1))
                     n4 = name.find("=", (n3+1))
                     n5 = name.find("&", (n4+1))
                     nam1 = name[(n1+7):(n2)]
                     nam2 = name[(n4+1):n5]
                     name1 = nam1 + "###" + nam2
#                     pass#print "In Videos1 url1 =", url1
                     i1 = i1+1
                     start = j1+7
                     pic = " "
	             addDirectoryItem(name1, {"name":name1, "url":url1, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)	


def getVideos2(name1, url):
                name = "Status"
                pic = " "
                addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)

                name = "Channel names keywords"
                pic = " "
                addDirectoryItem(name, {"name":name, "url":url, "mode":9}, pic)

                name = "EPG"
                pic = " "
                addDirectoryItem(name, {"name":name, "url":url, "mode":7}, pic)

                name = "Channels"
                pic = " "
                addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)


def getVideos3(name1, url):
        if "Status" in name1:
                data = status(url)
                show = xbmcgui.ControlTextBox()
                show.setText(data)
        else:
                content = getUrl(url)
                print "In getVideos3 content B =", content
                regexcat = '\#EXTINF\:(.*?)\\n(.*?)\\n'
                match = re.compile(regexcat,re.DOTALL).findall(content)
                print "In getVideos3 match =", match
                print "In getVideos3 KW =", KW
                icount = 1
                for name, url in match:
                        if len(KW) > 0:
                            icount = 0
                            for key in KW:
                               if key in name.lower():
                                      icount = 1
                                      break
                            if icount == 0:
                               continue     
                        url1 = url.replace("\r", "")
                        url1 = url1.replace("\n", "")
                        items = name.split(",")
                        name1 = items[1].replace("\r", "")
                        name1 = name1.replace("\n", "")
 
                        pic = " "
	                addDirectoryItem(name1, {"name":name1, "url":url1, "mode":4}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def getVideos31(name1, url):
            if "daily-m3u-playlists" in name1:
                getVideos11(name1, url)
            else:    
                content = getUrl(url)
                print "In getVideos31 content B =", content
                n1 = content.find("data-url=", 0)
                content = content[n1:]

                regexcat = '\#EXTINF\:(.*?)<.*?ttp(.*?)<'
                match = re.compile(regexcat,re.DOTALL).findall(content)
                print "In getVideos31 match =", match
                print "In getVideos31 KW =", KW
                icount = 1
                for name, url in match:
                        print "In getVideos31 name =", name
                        print "In getVideos31 url =", url
                        if len(KW) > 0:
                            icount = 0
                            for key in KW:
                               print "In getVideos31 key =", key
                               print "In getVideos31 name.lower() =", name.lower()
                               if key in name.lower():
                                      print "In getVideos31 key in name"
                                      icount = 1
                                      break
                            print "In getVideos31 icount =", icount
                            if icount == 0:
                               continue
                        url1 = "http" + url
                        url1 = url1.replace("\r", "")
                        url1 = url1.replace("\n", "")
                        items = name.split(",")
                        name1 = items[1].replace("\r", "")
                        name1 = name1.replace("\n", "")

                        pic = " "
	                addDirectoryItem(name1, {"name":name1, "url":url1, "mode":4}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)
                
def getVideos4(name1, url):
                print "In getVideos4 url =", url
                content = getUrl(url)
                print "getVideos1 content =", content
                n1 = content.find('aside id="recent-posts', 0)
                n2 = content.find('</aside>', (n1+5))
                content2 = content[n1:n2]
                regexcat = '<a href="(.*?)">(.*?)<'
                match = re.compile(regexcat,re.DOTALL).findall(content2)
                print "In getVideos4 match =", match
                i1 = 0
                for url, name in match:
                     name = url
                     pic = " "
                     if i1 > 6:
                            break
                     i1 = i1+1
	             addDirectoryItem(name, {"name":name, "url":url, "mode":31}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def getVideos5(name1, url):
                        content = getUrl(url)
                        print "getVideos5 content A =", content
                        regexcat = "post-title entry-title.*?<a href='(.*?)'"
                        match = re.compile(regexcat,re.DOTALL).findall(content)
                        print "In getVideos5 match =", match
                        for url in match:
                                if "daily-m3u-playlist" in url:
                                        url1 = url
                                        pic = " "
                                        name = url
                                        addDirectoryItem(name, {"name":name, "url":url1, "mode":10}, pic)
                        xbmcplugin.endOfDirectory(thisPlugin)

def getVideos6(name1, url):
                content = getUrl(url)
                print "content A =", content
                start = 0
                i1 = 0
                while i1<20:
                     j1 = content.find("type=m3u", start)
                     if j1<0:
                               break
                     j2 = content.rfind("http", 0, j1)
                     url = content[j2:(j1+8)]
                     print "In Videos1 url 2=", url
                     url = url.replace("&amp;", "&")
                     url1 = url.replace(" ", "")
                     if checkstat(url1) == "no":
                             i1 = i1+1
                             start = j1+7
                             continue

                     name = url1
                     n1 = name.find("http://", 0)
                     n2 = name.find("/", (n1+10))
                     n3 = name.find("usern", (n2+1))
                     n4 = name.find("=", (n3+1))
                     n5 = name.find("&", (n4+1))
                     nam1 = name[(n1+7):(n2)]
                     nam2 = name[(n4+1):n5]
                     name1 = nam1 + "###" + nam2
#                     pass#print "In Videos1 url1 =", url1
                     i1 = i1+1
                     start = j1+7
                     pic = " "
	             addDirectoryItem(name1, {"name":name1, "url":url1, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)	

def getVideos7(name1, url):
                content = getUrl(url)
                print "getVideos7 content A =", content
                regexcat = "post-title entry-title.*?<a href='(.*?)'"
                match = re.compile(regexcat,re.DOTALL).findall(content)
                print "getVideos7 In match =", match
                url1 = match[0]
##############################################
                content = getUrl(url1)
                print "In getVideos7 content B =", content
                regexcat = '\#EXTINF\:(.*?)<.*?http(.*?)<'
                match = re.compile(regexcat,re.DOTALL).findall(content)
                print "In getVideos7  match 2=", match
                for name, url in match:
                        if len(KW) > 0:
                            icount = 0
                            for key in KW:
                               if key in name.lower():
                                      icount = 1
                                      break
                            if icount == 0:
                               continue     
                        url1 = "http" + url
                        items = name.split(",")
                        name1 = items[1].replace("\\r", "")
                        pic = " "
	                addDirectoryItem(name1, {"name":name1, "url":url1, "mode":4}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def playVideo(name, url):
           print "Here in playVideo url =", url
           pic = "DefaultFolder.png"
           print "Here in playVideo url B=", url
           li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
           player = xbmc.Player()
           player.play(url, li)

def epg1(name, url):
                print "In epg1 url =", url
                url = url.replace("get.php", "player_api.php")
                url = url.replace("&type=m3u", "&action=get_live_streams")
                try:
                       content = getUrl(url)
                       print "In epg1 content =", content
                       regexcat = ',"name"\:"(.*?)".*?stream_id"\:(.*?),'
                       match = re.compile(regexcat,re.DOTALL).findall(content)
                       print "In epg1 match =", match
                       icount = 1
                       for name, stream_id in match:
                            if len(KW) > 0:
                               icount = 0
                               for key in KW:
                                   if key in name.lower():
                                      icount = 1
                                      break
                            if icount == 0:
                               continue 
                            else:     
                               pic = " "
                               url1 = url.replace("get_live_streams", "get_short_epg&stream_id=")
                               url1 = url1 + stream_id
                               addDirectoryItem(name, {"name":name, "url":url1, "mode":8}, pic)
                       xbmcplugin.endOfDirectory(thisPlugin)
                except:
                       pass

def epg2(name, url):
                print "In epg1 url =", url
                try:
                       content = getUrl(url)
                       print "In epg2 content =", content
                       regexcat = '"title"\:"(.*?)".*?start"\:"(.*?)".*?end"\:"(.*?)"'
                       match = re.compile(regexcat,re.DOTALL).findall(content)
                       print "In epg2 match =", match
                       data = ""
                       for title, start, end in match:
                              title = base64.decodestring(title)
                              line = "\n-----------------------------------"
                              data = data + line 
                              line1 = "\n" + start + " -> " + end  
                              data = data + line1
                              line2 = "\n" + title
                              data = data + line2
                       show = xbmcgui.ControlTextBox()
                       show.setText(data)

                except:
                       pass

def keywords(name, url):
                ktext = "List your channel keywords in \n/plugin.video.IPTVupdater/KW.py\nCurrent keywords=" + str(KW)
                show = xbmcgui.ControlTextBox()
                show.setText(ktext)


std_headers = {
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'en-us,en;q=0.5',
}  

def addDirectoryItem(name, parameters={},pic=""):
    li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)


def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

params = parameters_string_to_dict(sys.argv[2])
name =  str(params.get("name", ""))
url =  str(params.get("url", ""))
url = urllib.unquote(url)
mode =  str(params.get("mode", ""))

if not sys.argv[2]:
	ok = showContent()
else:
        if mode == str(1):
		ok = getVideos1(name, url)
	elif mode == str(11):
		ok = getVideos11(name, url)

	elif mode == str(2):
		ok = getVideos2(name, url)
	elif mode == str(3):
	        ok = getVideos3(name, url)
	elif mode == str(31):
	        ok = getVideos31(name, url)
	        
	elif mode == str(4):
	        ok = playVideo(name, url)
	elif mode == str(5): 
                ok = getVideos4(name, url)
	elif mode == str(6):
        	ok = getVideos5(name, url)

	elif mode == str(7):
        	ok = epg1(name, url)
	elif mode == str(8):
        	ok = epg2(name, url)

 	elif mode == str(9):
        	ok = keywords(name, url)
	elif mode == str(10):
        	ok = getVideos6(name, url)
                """
	elif mode == str(11):
        	ok = getVideos7(name, url)
                """
                pass
