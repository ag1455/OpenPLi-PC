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
       sys.argv[0] = sys.argv[0].replace('/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/ALB/', 'plugin://') 
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



thisPlugin = int(sys.argv[1])
addonId = "plugin.video.filmi24"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)
       
Host = "http://www.filmi24.ga"

def getUrl(url):
        print "Here in getUrl url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

	
def showContent():
                content = getUrl(Host)
                print "content A =", content
                regexcat = '<a href="http://www.filmi24.ga/kategori(.*?)">(.*?)<'
                match = re.compile(regexcat,re.DOTALL).findall(content)
                print "match =", match
                for url, name in match:
                        pic = " "
                        url1 = "http://www.filmi24.ga/kategori" + url
                        ##print "Here in Showcontent url1 =", url1
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":1}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def getVideos2X(name, url):
                print "In xhamster name =", name
                print "In xhamster getVideos6 url =", url
                f = open("/tmp/xbmc_search.txt", "r")
                icount = 0
                for line in f.readlines(): 
                    sline = line
                    icount = icount+1
                    if icount > 0:
                           break

                name = sline.replace(" ", "-")
                url1 = "http://www.deviantclip.com/s/" + name
                getPage2(name, url1)

#http://www.deviantclip.com/s/mom-son?p=3

def getPage2X(name, urlmain):
                pages = [1, 2, 3, 4, 5, 6]
                for page in pages:
                        url = urlmain + "?p=" + str(page)
                        name = "Page " + str(page)
                        pic = " "
                        addDirectoryItem(name, {"name":name, "url":url, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

#http://www.filmi24.ga/kategori/aksion/page/2/
def getPage(name, url):
                pages = [1, 2, 3, 4, 5, 6]
                for page in pages:
                        url1 = url + "page/" + str(page) + "/"
                        name = "Page " + str(page)
                        pic = " "
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)


#<ins class="adsbygoogle" data-language="en"
def getVideos(name1, urlmain):
	content = getUrl(urlmain)
	print "content B =", content

	regexvideo = 'class="item movies">.*?img src="(.*?)" alt="(.*?)".*?<a href="(.*?)".*?<div class="data">.*?<span>(.*?)<'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        print "match =", match
        for pic, name, url, year in match:
                 name = name.replace('"', '')
                 name1 = name + " (" + year + ")"
                 ##print "Here in getVideos url =", url
	         addDirectoryItem(name1, {"name":name1, "url":url, "mode":3}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)	         
        
def getVideos2(name1, urlmain):
	content = getUrl(urlmain)
	print "content B =", content
        #https://www.dailymotion.com/embed/video/k1pF12HDofq71JqK0Ty
	regexvideo = '<iframe.*?src="(.*?)"'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        print "match =", match
        url = match[0].replace(" ", "")
        print "url =", url
        playVideo(name, url)
                
def playVideo(name, url):
           from resolveurl import HostedMediaFile 
           url = HostedMediaFile(url=url).resolve()
           pic = "DefaultFolder.png"
           print "Here in playVideo url B=", url
           li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
           player = xbmc.Player()
           player.play(url, li)


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
		ok = getPage(name, url)
	elif mode == str(2):
		ok = getVideos(name, url)	
	elif mode == str(3):
                ok = getVideos2(name, url)
        elif mode == str(4):
		ok = playVideo(name, url)	
#	elif mode == str(4):
#		ok = getVideos2(name, url)	

		


























































