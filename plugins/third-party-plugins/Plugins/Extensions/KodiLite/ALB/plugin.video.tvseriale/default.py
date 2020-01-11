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



import sys, xbmc
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

hostDict = ['uptobox', 'allvid', 'exashare', 'filepup', 'filepup2', 'nosvideo', 'nowvideo', 'openload', 'vidlockers', 'streamcloud', 'streamin', 'vidspot', 'vidto', 'xvidstage', 'nosvideo', 'nowvideo', 'vidbull', 'vodlocker', 'vidto', 'youwatch', 'videomega']

thisPlugin = int(sys.argv[1])
addonId = "plugin.video.tvseriale"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)
       
#Host = "http://azfilma.al/zhanri/aventure/"
def getUrl(url):
        print "Here in getUrl url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def getUrl2(url, referer):
        print "Here in client2 getUrl url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        req.add_header('Referer', referer)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link
        		
def showContent():
        names = []
        urls = []
        #https://tvseriale.com/category/dhoma-309/
        names.append("Ruya")
        urls.append("https://tvseriale.com/ruya")
        names.append("nusja-nga-stambolli")
        urls.append("https://tvseriale.com/nusja-nga-stambolli")
        names.append("trumcaku")
        urls.append("https://tvseriale.com/trumcaku")
        names.append("gjithcka-per-tim-bir")
        urls.append("https://tvseriale.com/gjithcka-per-tim-bir")
        names.append("Nënë")
        urls.append("https://tvseriale.com/nene")
        names.append("flake-pasioni")
        urls.append("https://tvseriale.com/flake-pasioni")
        names.append("dhoma-309")
        urls.append("https://tvseriale.com/category/dhoma-309")
        names.append("deti-i-jetes-sime")
        urls.append("https://tvseriale.com/deti-i-jetes-sime")
        names.append("kosem")
        urls.append("https://tvseriale.com/kosem")
        names.append("dashuria-nuk-do-fjale")
        urls.append("https://tvseriale.com/dashuria-nuk-do-fjale")
        names.append("mos-u-dorezo")
        urls.append("https://tvseriale.com/mos-u-dorezo")
        names.append("kara-sevda")
        urls.append("https://tvseriale.com/kara-sevda")
        names.append("dashuri-me-qira")
        urls.append("https://tvseriale.com/dashuri-me-qira")
        names.append("mes-dy-dashurish")
        urls.append("https://tvseriale.com/mes-dy-dashurish")
        names.append("deti-i-jetes-sime")
        urls.append("https://tvseriale.com/deti-i-jetes-sime") 
        names.append("fate-te-kryqzuara")
        urls.append("https://tvseriale.com/fate-te-kryqzuara")
        names.append("nje-pjese-e-imja")
        urls.append("https://tvseriale.com/nje-pjese-e-imja")
        names.append("maral")
        urls.append("https://tvseriale.com/maral")
        names.append("guxim-dhe-bukuri")
        urls.append("https://tvseriale.com/guxim-dhe-bukuri")
        names.append("icerde")
        urls.append("https://tvseriale.com/icerde")
        names.append("zonja-e-vogel")
        urls.append("https://tvseriale.com/zonja-e-vogel")
        names.append("filinta")
        urls.append("https://tvseriale.com/filinta")
        names.append("ertugrul")
        urls.append("https://tvseriale.com/ertugrul")
        names.append("ambicie-e-verber")
        urls.append("https://tvseriale.com/ambicie-e-verber")
        names.append("qka-ka-shpija")
        urls.append("https://tvseriale.com/qka-ka-shpija")
        names.append("shoqeri-e-larte")
        urls.append("https://tvseriale.com/shoqeri-e-larte")
        names.append("o-sa-mire")
        urls.append("https://tvseriale.com/o-sa-mire")
        names.append("filma")
        urls.append("https://tvseriale.com/filma")
        names.append("ask-laftan-anlamaz")
        urls.append("https://tvseriale.com/ask-laftan-anlamaz")
        names.append("hakmarrja")
        urls.append("https://tvseriale.com/hakmarrja")
        names.append("me-fal")
        urls.append("https://tvseriale.com/me-fal")
    
        i = 0           
        for name in names:
                url = urls[i]
                i = i+1
                pic = " "
                addDirectoryItem(name, {"name":name, "url":url, "mode":1}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)
        
def getPage(name, url):
                pages = [1, 2, 3, 4, 5]
                #https://tvseriale.com/ruya/page/2/
                for page in pages:
                        url1 = url + "/page/" + str(page) + "/"
                        name = "Page " + str(page)
                        pic = " "
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)
        
        

        

def getVideos(name1, urlmain):
        url = urlmain
	content = getUrl(url)
#	print "content A =", content

	regexvideo = 'div class="td-module-thumb"><a href="(.*?)".*?title="(.*?)".*?src="(.*?)"'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        print "match =", match
        for url, name, pic in match:
                 ##print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)	         
        
def getVideos2(name, url):
    print "In getVideos2 url =", url
    content = getUrl(url)
    print "content B=", content
    regexvideo = '<iframe.*?src="(.+?)"'
    match = re.compile(regexvideo,re.DOTALL).findall(content) 
    print "match B=", match
    """
    for url, name in match:
           pic = " "
           print "name B=", name
           print "url B=", url
           addDirectoryItem(name, {"name":name, "url":url, "mode":4}, pic)
    
    xbmcplugin.endOfDirectory(thisPlugin)
    """
    vurl = match[0]
    playVideo(name, vurl)
    
def playVideo(name, url):
       print "In plaVideo url 1=", url
       if "hqq" in url:
           import TURKvodKodiPrsr
           TURKVOD_PARSER = TURKvodKodiPrsr.turkvod_parsers()
           stream_url = TURKVOD_PARSER.get_parsed_link(url)
           print "In VideoList stream_url =", stream_url
           pic = "DefaultFolder.png"
           li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
           player = xbmc.Player()
           player.play(stream_url, li)

       else:
           import resolveurl 
	   stream_url = resolveurl.HostedMediaFile(url=url).resolve()
           print "stream_url =", stream_url
           pic = "DefaultFolder.png"
           li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
           player = xbmc.Player()
           player.play(stream_url, li)
    
                
def playVideoX(name, url):
           import urlresolver 
           print "In plaVideo url 1=", url 
           content = getUrl2(url, "http://azfilma.al/filma/geostorm-2017-me-titra-shqip/")
           print "In playVideo content =", content
           regexvideo = "window.location.href='(.+?)'"
           match = re.compile(regexvideo,re.DOTALL).findall(content) 
           print "match =", match
           url = match[0]
           print "In plaVideo url 2=", url      
	   stream_url = urlresolver.HostedMediaFile(url=url).resolve()
           print "stream_url =", stream_url
           pic = "DefaultFolder.png"
           li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
           player = xbmc.Player()
           player.play(stream_url, li)

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
print "name =", name
print "url =", url

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



















