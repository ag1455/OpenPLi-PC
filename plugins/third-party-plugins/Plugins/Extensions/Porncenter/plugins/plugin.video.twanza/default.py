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

HOSTS = ['anysex', 'xhamster', 'drtuber', 'empflix', 'eporner', 'extremetube', '4tube', 'goshgay', 'hellporno', 'hornbunny', 'keezmovies', 'lovehomeporn', 'mofosex', 'motherless', '91porn', 'pornhd', 'pornhub', 'pornotube', 'pornovoisines', 'pornoxo', 'redtube', 'sexu', 'sexykarma', 'slutload', 'spankbang', 'spankwire', 'sunporno', 'tnaflix', 'tube8', 'vporn', 'xtube', 'xvideos', 'xxymovies', 'ah-me']
HOSTS2 = ['tubeq', 'txxx', 'upornia', 'katestube', 'hotmovs', 'theclassicporn','fantasy8','kinkytube', 'alphaporno', 'vid2c', 'hd21', 'winporn', 'drtube','anysex', 'xhamster', 'drtuber', 'empflix', 'eporner', 'extremetube', '4tube', 'goshgay', 'hellporno', 'hornbunny', 'keezmovies', 'lovehomeporn', 'mofosex', 'motherless', '91porn', 'pornhd', 'pornhub', 'pornotube', 'pornovoisines', 'pornoxo', 'redtube', 'sexu', 'sexykarma', 'slutload', 'spankbang', 'spankwire', 'sunporno', 'tnaflix', 'tube8', 'vporn', 'xtube', 'xvideos', 'xxymovies', 'ah-me']

thisPlugin = int(sys.argv[1])
addonId = "plugin.video.twanza"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)
       
Host = "http://twanza.com/index.php"

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
        addDirectoryItem("Twanza-Search", {"name":"Twanza-Search", "url":Host, "mode":4}, pic)           
        i = 0   
        ref = "http://twanza.com/index.php"        
        content = getUrl2(Host, ref)
	print "content A =", content
        #http://twanza.com/index.php?niche=3
	regexvideo = 'class="nicheBtn" onClick=".*?href=\'(.*?)\';">(.*?)<'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        print "match =", match
        for url, name in match:
                 name = "Twanza-" + name.replace('"', '')
                 pic = " "
                 url = "http://twanza.com/" + url
                 print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":1}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)	         
#http://twanza.com/index.php?niche=1
def getPage(name, url):
                print "In getPage name =", name
	        print "In getPage url =", url
#               http://twanza.com/index.php?p=10&niche=3
                page = 1
                while page < 11:
                        n1 = url.find("niche", 0)
                        url1 = url[:n1]
                        url2 = url[n1:]
                        urlf = url1 + "p=" + str(page) + "&" + url2
                        name = "Twanza-Page " + str(page)
                        pic = " "
                        page = page+1
                        addDirectoryItem(name, {"name":name, "url":urlf, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def getVideos(name1, urlmain):
	content = getUrl(urlmain)
	print "content B =", content
	#http://twanza.com/index.php?movieID=YUu7gNzg5iorUlp
	regexvideo = 'onClick="location.href=\'(.*?)\'.*?img src="(.*?)".*?"title">(.*?)<'
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        print "match =", match
        for url, pic, name in match:
                 name = "Twanza-" + name
                 url = "http://twanza.com/index.php" + url
                 print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)	         

def getVideos3(name, url):
                print "In Twanza getVideos3"
                f = open("/tmp/xbmc_search.txt", "r")
                icount = 0
                for line in f.readlines(): 
                    sline = line
                    icount = icount+1
                    if icount > 0:
                           break

                name = "Twanza-" + sline.replace(" ", "+")
                url1 = "http://twanza.com/index.php?fSearch=" + name + "/" 
                print "In Twanza getVideos3 going getVideos url1 = ", url1
                getVideos(name, url1)


#HOSTS2 = ['tubeq', 'txxx', 'katestube', "keezmovies", "upornia", 'hotmovs', 'theclassicporn','fantasy8','kinkytube', 'alphaporno', 'vid2c', 'hd21', 'winporn', 'drtube','anysex', 'xhamster', 'drtuber', 'empflix', 'eporner', 'extremetube', '4tube', 'goshgay', 'hellporno', 'hornbunny', 'keezmovies', 'lovehomeporn', 'mofosex', 'motherless', '91porn', 'pornhd', 'pornhub', 'pornotube', 'pornovoisines', 'pornoxo', 'redtube', 'sexu', 'sexykarma', 'slutload', 'spankbang', 'spankwire', 'sunporno', 'tnaflix', 'tube8', 'vporn', 'xtube', 'xvideos', 'xxymovies', 'ah-me']
        		
def getVideos2(name, url):
        print "Here in getVideos2 url =", url
        content = getUrl(url)
	print "content B2 =", content
	regexvideo = "file:'(.*?)'"

        match = re.compile(regexvideo,re.DOTALL).findall(content)
        print "match =", match
        vurl = match[0] 
#        vurl = vurl.replace("\\", "")       
        player = xbmc.Player()
        player.play(vurl) 
        

def playVideo(name, url):
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "fpage C =", fpage
           start = 0
           pos1 = fpage.find("file:", start)
           if (pos1 < 0):
                           return
  	   pos2 = fpage.find("'", pos1)
 	   if (pos2 < 0):
                           return
           pos3 = fpage.find("'", (pos2+10))
 	   if (pos3 < 0):
                           return                
           url = fpage[(pos2+1):pos3]
                    
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
print "url A=", url
url = urllib.unquote(url)
print "url B=", url
mode =  str(params.get("mode", ""))

if not sys.argv[2]:
       
        ok = showContent()
else:
	if mode == str(1):
	        print "name C=", name
	        print "url C=", url
		ok = getPage(name, url)
        elif mode == str(2):
		ok = getVideos(name, url)        	
	elif mode == str(3):
		ok = getVideos2(name, url)		
	elif mode == str(4):
		ok = getVideos3(name, url)		

	elif mode == str(5):
		ok = getVideos4(name, url)	




