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
addonId = "plugin.video.wildfire2"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)
       
#Host = "http://www.wildfireporn.com/cat/19.html"
Host = "http://www.wildfireporn.com/cat/18.html"

def getUrl(url):
        pass#print"Here in getUrl url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def showContent():
               pic = " "
               name = "JAVHD"
               url = "19"
               addDirectoryItem(name, {"name":name, "url":url, "mode":1}, pic)
               """
               name = "Streamcloud"
               url = "1"
               addDirectoryItem(name, {"name":name, "url":url, "mode":1}, pic)
               """
               xbmcplugin.endOfDirectory(thisPlugin)

#http://www.wildfireporn.com/cat/1-p4.html
def getPage(name, url):
        if "Dropvideo" in name:
               np = 22
        elif "JAVHD" in name:
               np = 4
        elif "Streamcloud" in name:
               np = 100
        i1 = 0
        while i1< np:
               i1 = i1+1
               name1 = name + "-Page-" + str(i1)
               url1 = "http://www.wildfireporn.com/cat/" + url + "-p" + str(i1) + ".html"
               pic = " "
               addDirectoryItem(name1, {"name":name1, "url":url1, "mode":3}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)

def getVideos(name1, urlmain):
	content = getUrl(urlmain)
	pass#print"content A =", content
	n1 = content.find("<!-- main content -->", 0)
	content = content[n1:]
	regexvideo = 'align="left"><a href="(.*?)"><img src="(.*?)".*?class="movie">(.*?)<'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        pass#print"match =", match
        pass#print"name1 =", name1
        if "Dropvideo" in name1:
               mode = 4
        elif "JAVHD" in name1:
               mode = 5
        else:
               mode = 6       
        for url, pic, name in match:
               addDirectoryItem(name, {"name":name, "url":url, "mode":mode}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)


def getVideos2(name1, urlmain):
	content = getUrl(urlmain)
	pass#print"content B =", content

	regexvideo = '"></iframe><b.*?<BR><B.*?a href="(.*?)"'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        pass#print"match =", match
        surl = match[0]
        
        pass#print"Here in default-py surl =", surl
        player = xbmc.Player()
        player.play(surl)	
        
def getVideos1(name1, urlmain):
	content = getUrl(urlmain)
	pass#print"In getVideos1 content B =", content
	regexvideo = '<iframe src="(.*?)"'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        pass#print"In getVideos1 match =", match
        content2 = getUrl(match[0])
        pass#print"In getVideos1 content2 =", content2
        regexvideo = ';backgrou.*?url\((.*?)screenshots/(.*?)\.jpg'
	match2 = re.compile(regexvideo,re.DOTALL).findall(content2)
        pass#print"In getVideos1 match2 =", match2
        url1 = match2[0][0].replace("videos", "v")
        url2 = match2[0][1]
        url3 = " "
        n1 = content2.find("simulateiDevice")
        n2 = content2.find("scrubberBarHeightRatio")
        content3 = content2[n1:n2]
        items = content3.split("|")
        pass#print"In getVideos1 items =", items
        for item in items:
              nlen = len(item)
              pass#print"In getVideos1 nlen, item =", nlen, item
              if nlen == 22:
                     url3 = item
                     break
        
        surl = url1 + url2 + ".mp4?st=" + url3
        
        pass#print"Here in default-py surl =", surl
        player = xbmc.Player()
        player.play(surl)	        

def getVideos3(name, urlmain):
        import urlresolver
	content = getUrl(urlmain)
	pass#print"content B =", content

	regexvideo = '<iframe.*?<a href="(.*?)"'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        pass#print"match =", match
        url = match[0]
        playVideo(name, url)
#        stream_url = urlresolver.HostedMediaFile(url=url).resolve()
#        got_link(stream_url)

def got_link(stream_url):
        pass#print"got_link stream_url =", stream_url
        if stream_url:
                    xbmc.executebuiltin("XBMC.Notification(Please Wait!,Resolving Link,3000)")
                    img = " "
                    name = " "
                    listitem = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
#                    stream_url = source.resolve()
                    pass#print"movie25-py stream_url =", stream_url
                    listitem.setPath(stream_url)
                    playfile = xbmc.Player()
#                    stream_url = "*download*" + stream_url
                    pass#print"movie25-py stream_url B=", stream_url
                    playfile.play(stream_url, listitem)
        else:
                  stream_url = False
                  return
        
    



        
def playVideo(name, url):
        pass#print"In playVideo url =", url
        import YDStreamExtractor
        YDStreamExtractor.disableDASHVideo(True) #Kodi (XBMC) only plays the video for DASH streams, so you don't want these normally. Of course these are the only 1080p streams on YouTube
#        url = "https://www.youtube.com/watch?v=" + url #a youtube ID will work as well and of course you could pass the url of another site
        vid = YDStreamExtractor.getVideoInfo(url,quality=1) #quality is 0=SD, 1=720p, 2=1080p and is a maximum
        stream_url = vid.streamURL() #This is what Kodi (XBMC) will play
        pass#print"stream_url =", stream_url
        n1 = stream_url.find("|", 0)
        stream_url = stream_url[:n1]
        pass#print"stream_url 2=", stream_url
        img = " "
        playfile = xbmc.Player()
        playfile.play(stream_url)        
                        

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
	elif mode == str(3):
		ok = getVideos(name, url)	
        elif mode == str(4):
#                import urlresolver
		ok = getVideos1(name, url)
	elif mode == str(5):
		ok = getVideos2(name, url)	
	elif mode == str(6):
		ok = getVideos3(name, url)	

		







































