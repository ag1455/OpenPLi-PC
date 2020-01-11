#!/usr/bin/python

import sys, xpath2, xbmc
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
       sys.argv[0] = sys.argv[0].replace('/usr/lib/enigma2/python/Plugins/Extensions/Porncenter/plugins/', 'plugin://') 
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

pass#print  "Here in default-py sys.argv =", sys.argv

thisPlugin = int(sys.argv[1])
addonId = "plugin.video.heavyr"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)
       
Host = "http://www.heavy-r.com/categories/"

def getUrl(url):
        pass#print  "Here in getUrl url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link
	

def showContent():
                content = getUrl(Host)
                pass#print  "content A =", content
                regexcat = 'div class="video-item category.*?a href="(.*?)".*?img src="(.*?)" alt="(.*?)"'
                match = re.compile(regexcat,re.DOTALL).findall(content)
                pass#print  "match =", match
                pic = " "
                addDirectoryItem("Heavyr-Search", {"name":"Heavyr-Search", "url":Host, "mode":4}, pic)
                for url, pic, name in match:
                        name = "Heavyr-" + name
                        n1 = url.rfind("/")
                        url = url[(n1+1):] 
                        url1 = "http://www.heavy-r.com/free_porn/" + url
                        pic = "http://www.heavy-r.com" + pic
                        #pass#print  "Here in Showcontent url1 =", url1
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":1}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)
# 4----http://www.heavy-r.com/free_porn/anal_3.html
def getPage(name, url):
                pages = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                for page in pages:
                        p = page-1
                        url1 = url + "_" + str(p) +".html"
                        name = "Heavyr-Page " + str(page)
                        pic = " "
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def getVideos(name1, urlmain):
	content = getUrl(urlmain)
	pass#print  "content B =", content
	regexvideo = 'iv class="video-item compact.*?a href="(.*?)".*?img src="(.*?)".*?alt="(.*?)"'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        pass#print  "match =", match
        for url, pic, name in match:
                 url1 = "http://www.heavy-r.com" + url
                 name = "Heavyr-" + name.replace('"', '')
                 #pass#print  "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)	         

def getVideos2(name1, urlmain):
	content = getUrl(urlmain)
	pass#print  "content C =", content
	regexvideo = 'type="video/mp4" src="(.*?)"'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        pass#print  "match =", match
        for url in match:
               pass#print  "Here in getvideos2 url =", url
               player = xbmc.Player()
               player.play(url)
               break	         

        
def getVideos3(name, url):
                      myfile = file(r"/tmp/xbmc_search.txt")       
                      icount = 0
                      for line in myfile.readlines(): 
                            stext = line
                            icount = icount+1
                            if icount > 0:
                                 break
                      stext = stext.replace(" ", "+")
                      pic = " "
                      name = stext
                      url = "http://m.hardsextube.com/results?search_query=" + stext
                      getPageS(name, url)        
                                 
def getPageS(name, url):
                myfile = file(r"/tmp/xbmc_search.txt")       
                icount = 0
                for line in myfile.readlines(): 
                            stext = line
                            icount = icount+1
                            if icount > 0:
                                 break
                stext = stext.replace(" ", "+")
                pages = [1, 2, 3, 4, 5, 6]
                for page in pages:
                        url1 = "http://www.heavy-r.com/search/" + stext + "_" + str(page) + ".html"
#                        url1 = url + "&page=" + str(page)
                        name = "Heavyr-Page " + str(page)
                        pic = " "
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

        
def playVideo(name, url):
           pass#print  "Here in playVideo Test url =", url
           content = getUrl(url)
	   pass#print  "content C =", content
	   regexvideo = 'div id="interstitialBtn.*?a href="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(content)
           pass#print  "match =", match[0]
           url1 = match[0] 
           pic = "DefaultFolder.png"
           pass#print  "Here in playVideo Test url1 B=", url1
           li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
           player = xbmc.Player()
           player.play(url1, li)

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
        pass#print  "Here in default-py going in showContent"
	ok = showContent()
else:
        if mode == str(1):
		ok = getPage(name, url)
	elif mode == str(2):
		ok = getVideos(name, url)
                	
	elif mode == str(3):
		ok = getVideos2(name, url)	
	elif mode == str(4):
		ok = getVideos3(name, url)	

	elif mode == str(5):
		ok = getVideos3(name, url)
	elif mode == str(6):
		ok = getVideos4(name, url)
	elif mode == str(7):
		ok = getVideos5(name, url)
	elif mode == str(8):
		ok = search(name, url)
	elif mode == str(9):
		ok = getPageS(name, url)	
































