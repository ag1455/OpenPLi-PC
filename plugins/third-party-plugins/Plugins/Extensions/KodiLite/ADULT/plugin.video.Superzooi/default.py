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
       sys.argv[0] = sys.argv[0].replace('/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/ADULT/', 'plugin://') 
       sys.argv[0] = sys.argv[0].replace('default.py', '')
print "Here in default-py sys.argv B=", sys.argv



HOSTS = ['xhamster', 'drtuber', 'empflix', 'eporner', 'extremetube', '4tube', 'goshgay', 'hellporno', 'hornbunny', 'keezmovies', 'lovehomeporn', 'mofosex', 'motherless', '91porn', 'pornhd', 'pornhub', 'pornotube', 'pornovoisines', 'pornoxo', 'redtube', 'sexu', 'sexykarma', 'slutload', 'spankbang', 'spankwire', 'sunporno', 'tnaflix', 'tube8', 'vporn', 'xtube', 'xvideos', 'xxymovies', 'ah-me']

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
addonId = "plugin.video.superzooi"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)
       
Host = "http://www.superzooi.com/categories/"

def getUrl(url):
        pass#print "Here in getUrl url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link
	
def getUrl2(url, referer):
        pass#print "Here in getUrl2 url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        req.add_header('Referer', referer)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link		
	
def showContent():
        content = getUrl(Host)
        pass#print "content A =", content
        icount = 0
	
        pic = " "
        addDirectoryItem("Superzooi-Search", {"name":"Superzooi-Search", "url":Host, "mode":4}, pic)           
        i1 = 0           
        #http://www.superzooi.com/anime/
        if i1 == 0:
                regexcat = '<li class="category span3">.*?<a href="(.*?)"><img src="(.*?)".*?a href=.*?">(.*?)<'
                match = re.compile(regexcat,re.DOTALL).findall(content)
                pass#print "match =", match
                for url, pic, name in match:
                        if name == "": 
                               continue
                        name = "Superzooi-" + name       
                        url1 = "http://www.superzooi.com" + url
                        #pass#print "Here in Showcontent url1 =", url1
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":1}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def getPage(name, urlmain):
                page = 1
                
                #http://www.superzooi.com/anime/recent/3/
                while page < 50:
                        url = urlmain + 'recent/' + str(page) + "/"
                        p = page
                        name = "Superzooi-Page " + str(p)
                        pic = " "
                        page = page+1
                        addDirectoryItem(name, {"name":name, "url":url, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def getVideos(name1, urlmain):
	content = getUrl(urlmain)
	pass#print "content B =", content

	regexvideo = '<li class="span3">.*?a href="(.*?)" title="(.*?)"><img src="(.*?)"'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        pass#print "getVideos match =", match
        for url, name, pic in match:
                 name = "Superzooi-" + name.replace('"', '')
                 #http://www.superzooi.com/media/videos/tmb/000/008/904/21.jpg
                 #http://www.superzooi.com/19926/russian-gangster-pussy/
                 url = "http://www.superzooi.com" + url
                 #pass#print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)	         

def getVideos3(name, url):
                f = open("/tmp/xbmc_search.txt", "r")
                icount = 0
                for line in f.readlines(): 
                    sline = line
                    icount = icount+1
                    if icount > 0:
                           break
                #http://www.superzooi.com/search/video/mom-son/
                #http://www.superzooi.com/search/video/anal/3/
                name = sline.replace(" ", "-")
                url1 = "http://www.superzooi.com/search/video/" + name + "/" 
                page = 1
                while page < 50:
                        if page > 1:
                                url = url1 + str(page) + "/"
                        else:        
                                url = url1
                        pass#print "Here in getVideos2 url =", url
                        p = page
                        name = "Superzooi-Page " + str(p)
                        pic = " "
                        page = page+1
                        addDirectoryItem(name, {"name":name, "url":url, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)


        		
def getVideos2(name, url):
        pass#print "Here in getVideos3 url =", url
        content = getUrl(url)
	pass#print "content B2 =", content
#	regexvideo = "<iframe allowfullscreen src='(.*?)'"
        #http://www.superzooi.com/modules/video/player/config.php?id=10234
	regexvideo = 'text/javasc.*?src="/modules(.*?)"'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
	pass#print "match =", match
        url1 = 'http://www.superzooi.com/modules' + match[0]
        pass#print "url1 =", url1
        content2 = getUrl2(url1, url)
        pass#print "content B3 =", content2
	regexvideo = "'url'.*?'(.*?)'"
	match2 = re.compile(regexvideo,re.DOTALL).findall(content2)
	vurl = match2[0]
	playVideo(name, vurl)
        
           
def playVideo(name, url):
           pass#print "Here in playVideo url =", url
                   
           pic = "DefaultFolder.png"
           pass#print "Here in playVideo url B=", url
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
#		ok = playVideo(name, url)
                ok = getVideos2(name, url)	
	elif mode == str(4):
		ok = getVideos3(name, url)
	elif mode == str(6):
		ok = getVideos4(name, url)
	elif mode == str(7):
		ok = getVideos5(name, url)
		









