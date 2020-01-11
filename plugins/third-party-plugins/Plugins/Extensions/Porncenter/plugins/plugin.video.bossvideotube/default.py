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

import XXXresolver
sources = XXXresolver.sources
from XXXresolver.resolver import getVideo

thisPlugin = int(sys.argv[1])
addonId = "plugin.video.bossvideotube"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)
       
Host = "http://www.bossvideotube.com/en/index.shtml"
def getUrl(url):
        print "Here in getUrl url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link
	
def getUrl2(url, referer):
        print "Here in getUrl2 url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        req.add_header('Referer', referer)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link	

	
def getUrl3(url):
        print "Here in getUrl3 url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.geturl()
	response.close()
	return link

	

#http://www.bossvideotube.com/en/boat.html	
def showContent():
        content = getUrl(Host)
        print "content A =", content
        icount = 0
	start = 0
        pic = " "
        addDirectoryItem("Search", {"name":"Search", "url":Host, "mode":4}, pic)          
        i1 = 0           
        if i1 == 0:
                regexcat = '<a class="th" href="(.*?)".*?<img src="(.*?)".*?alt="(.*?)"'
                match = re.compile(regexcat,re.DOTALL).findall(content)
                ##print "match =", match
                for url, pic, name in match:
                        url1 = "http://www.bossvideotube.com" + url
                        pic = pic
                        ##print "Here in Showcontent url1 =", url1
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":1}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def getVideos2(name, url):
                print "In getVideos2 name =", name
                print "In getVideos2 url =", url
                f = open("/tmp/xbmc_search.txt", "r")
                icount = 0
                for line in f.readlines(): 
                    sline = line
                    icount = icount+1
                    if icount > 0:
                           break

                name = sline.replace(" ", "+")
                #http://www.bossvideotube.com/en/search/?q=mom+anal
                url1 = "http://www.bossvideotube.com/en/search/?q=" + name
                getPage2(name, url1)


def getPage2(name, urlmain):
                pages = [1]
                for page in pages:
                        url = urlmain
                        name = "Page " + str(page)
                        pic = " "
                        addDirectoryItem(name, {"name":name, "url":url, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

#https://www.tubegals.com/category/hot-mom?page=4
def getPage(name, url):
#                pages = [1, 2, 3, 4, 5, 6]
                pages = [1]

                for page in pages:
                        url1 = url
                        name = "Page " + str(page)
                        pic = " "
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

#http://www.bossvideotube.com/go.php?u=bWF0dXJlLW9yZ3ktb24tYS1ib2F0LXB0MQ
def getVideos(name1, urlmain):
	content = getUrl(urlmain)
	print "content B =", content

	regexvideo = '<div class="th_box"><div class="holder"><a href="(.*?)".*?title="(.*?)".*?<img src="(.*?)".*?div class="sponsor">.*?>(.*?)<'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        print "getVideos match =", match
        for url, name, pic, source in match:
                 if not source.lower() in sources:
                         continue
                 name = source+ "-" + name
                 url = "http://www.bossvideotube.com" + url
                 pic = pic 
                 ##print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)	         
        
                
def playVideo(name, url):
           print "Here in playVideo url =", url
           fpage = getUrl(url)
           print "Here in playVideo fpage =", fpage
           surl = getUrl3(url)
           print "Here in playVideo surl =", surl
           name1, url1 = getVideo(name, surl)
           print "In playVideo name1 =", name1
           print "In playVideo url1 =", url1
           pic = "DefaultFolder.png"
           li = xbmcgui.ListItem(name1,iconImage="DefaultFolder.png", thumbnailImage=pic)
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
	ok = showContent()
else:
        if mode == str(1):
		ok = getPage(name, url)
	elif mode == str(2):
		ok = getVideos(name, url)	
	elif mode == str(3):
		ok = playVideo(name, url)	
	elif mode == str(4):
		ok = getVideos2(name, url)	
















