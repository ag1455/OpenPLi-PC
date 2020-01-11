#!/usr/bin/python

import sys, xpath, xbmc
print "Here in default-py sys.argv =", sys.argv
if ("plugin%3A%2F%2F" in sys.argv[2]) or ("plugin://" in sys.argv[2]):
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


import xbmc,xbmcaddon, xbmcplugin
import xbmcgui
import sys
import urllib, urllib2
import time
import re
from htmlentitydefs import name2codepoint as n2cp
import httplib
import urlparse
from os import path, system, walk
import socket
from urllib2 import Request, URLError, urlopen
from urlparse import parse_qs
from urllib import unquote_plus


thisPlugin = int(sys.argv[1])
addonId = "plugin.video.tivustream18"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)
       
Addon = xbmcaddon.Addon(addonId)
#AddonName = Addon.getAddonInfo("name")
#icon = Addon.getAddonInfo('icon')

addonDir = Addon.getAddonInfo('path').decode("utf-8")
      
# Host = "http://patbuweb.com/iptv/e2liste/userbouquet.kodi.iptv.tv"
Host = "https://patbuweb.com/iptv/e2liste/userbouquet.tivustream_adultxxx.tv"

def getUrl(url):
        pass#print "Here in getUrl url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link
	
def showContent():
        names = []
        urls = []
        names.append("Tivu Stream XXX")
        urls.append("https://patbuweb.com/iptv/e2liste/userbouquet.tivustream_adultxxx.tv") 
        i = 0
        for name in names:
                url = urls[i]
                pic = " "
                i = i+1
                addDirectoryItem(name, {"name":name, "url":url, "mode":"1"}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)


def showContentB1(): 
                content = getUrl(Host)
                pass#print "content A =", content
                regexcat = '#DESCRIPTION ---(.*?)---'
                match = re.compile(regexcat,re.DOTALL).findall(content)
                pass#print "match A=", match
                i = 0
                for name in match:
                        
                        if i < 3:
                              i = i+1
                              continue
                        i = i+1 
                        # if (not "ADULTI" in name) and (not "VINTAGE ITALIANO Film Completi" in name):
                              # continue     
                        url1 = Host
                        pic = " "
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":1}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def showContentB2(name, url):
	content = getUrl(url)
	pass#print "content B =", content
	name = name.replace("+", " ")
	name = name.replace("%20", " ")
	pass#print "name B =", name
	n1 = content.find(name, 0)
	n2 = content.find("---", (n1+100))
	if n2 > -1:
                 content2 = content[n1:n2]
        else:          
                 content2 = content[n1:]
        pass#print "content2 =", content2         
	regexvideo = '#SERVICE 4097\:.*?\:.*?\:.*?\:.*?\:.*?\:.*?\:.*?\:.*?\:.*?\:(.*?)\:(.*?)#'
	match = re.compile(regexvideo,re.DOTALL).findall(content2)
        pass#print "match B=", match
        for url, name in match:
                 pic = " "
                 name = name[:-1]
                 name = name.replace('"', '')
                 name = name.replace('\n', '')
                 url = url.replace("%3a", ":")
#                 url1 = "http" + url
                 url1 = url
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":2}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)	         
        

                
def playVideo(name, url):
           pass#print "Here in playVideo url =", url
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
	ok = showContentB1()
else:
        if mode == str(1):
		ok = showContentB2(name, url)

        elif mode == str(2):
		ok = playVideo(name, url)	




