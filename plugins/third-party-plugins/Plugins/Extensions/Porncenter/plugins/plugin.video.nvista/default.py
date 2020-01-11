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
#import resolvers, re
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
addonId = "plugin.video.nvista"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)
       
Host = "http://www.nudevista.com/directory/"

def getUrl(url):
        print "Here in getUrl url =", url
	req = urllib2.Request(url)
#	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	req.add_header('User-Agent', 'Mobile')

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
	
	
def showContent():
        pic = " "
        addDirectoryItem("Search", {"name":"Search", "url":Host, "mode":4}, pic)           
        i = 0   
        ref = "http://www.nudevista.com"        
        content = getUrl2(Host, ref)
	print "content A =", content
        n1 = content.find("<h3>NudeVista tags:</h3", 0)
        n2 = content.find('<div style="clear:both;', n1)
        content = content[n1:n2]
        
	regexvideo = '<a href="(.*?)">(.*?)<'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        print "match =", match
        for url, name in match:
                 name = name.replace('"', '')
                 pic = " "
                 url1 = "http://www.nudevista.com" + url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":1}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)	         
#http://www.nudevista.com/?q=amateur&s=t&start=25
def getPage(name, url):
                print "getPage name =", name
	        print "getPage url =", url
#               http://b44.com/s/Anal/page3
                page = 0
                while page < 25:
                        index = 25*page
                        text = "&start=" + str(index)
                        url1 = url + text
                        page1 = page + 1
                        name = "Page " + str(page1)
                        pic = " "
                        page = page+1
                        print "getPage name 2=", name
	                print "getPage url1 2=", url1
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def getVideos(name1, urlmain):
	content = getUrl(urlmain)
	print "getVideos content B =", content
	regexvideo = 'add"></div><a href="(.*?)".*?<img src="(.*?)".*?</a> <b>(.*?)</b>'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        print "match =", match
        for url, pic, name in match:
                 print "Here in getVideos url =", url
                 pic1 = "https:" + pic
                 indic = 0
                 for host in sources:
                       if host in url.lower():
                              name = host + "-" + name
                              indic = 1
                              break
                 print "Here in getVideos indic =", indic           
                 if indic == 0:
                       continue   
                 print "Here in getVideos indic 2=", indic            
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic1)
        xbmcplugin.endOfDirectory(thisPlugin)	         

def getVideos2(name, url):
                f = open("/tmp/xbmc_search.txt", "r")
                icount = 0
                for line in f.readlines(): 
                    sline = line
                    icount = icount+1
                    if icount > 0:
                           break

                name = sline.replace(" ", "+")
                url1 = "http://www.nudevista.com/?q=" + name + "/" 
                getPage(name, url1)



             
def playVideo(name, url):
     print "In playVideo name =", name
     print "In playVideo url =", url
     name1, url1 = getVideo(name, url)
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
	        print "name =", name
	        print "url =", url
		ok = getPage(name, url)
        elif mode == str(2):
		ok = getVideos(name, url)        	
	elif mode == str(3):
		ok = playVideo(name, url)		
	elif mode == str(4):
		ok = getVideos2(name, url)	
		
















