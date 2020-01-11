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
addonId = "plugin.video.avelip"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)
       
Host = " "

def getUrl(url):
        pass#print "Here in getUrl url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link


                     
#http://avelip.com/vidc/abused
def showContent():
                url = "http://avelip.com"
                content = getUrl(url)
                pass#print "content A =", content
                name = "#"
                pic = " "
                addDirectoryItem(name, {"name":name, "url":url, "mode":1}, pic)
                regexcat = 'class=textbigbig><br>(.*?)<'
                match = re.compile(regexcat,re.DOTALL).findall(content)
                pass#print "showContent match =", match
                for name in match:
                        pic = " "
                        addDirectoryItem(name, {"name":name, "url":url, "mode":1}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def showContent1(name, url):
                pass#print "showContent1 name =", name
                url = "http://avelip.com"
                content = getUrl(url)
                pass#print "showContent1 content A =", content
                if "%23" in name:
                       txt1 = "class=textbigbig>"
                else:
                       txt1 = "class=textbigbig><br>" + name + "<"
                pass#print "showContent1 txt1 =", txt1      
                n1 = content.find(txt1, 0)
                n2 = content.find("class=textbigbig>", (n1+2))
                content2 = content[n1:n2]

                regexcat = 'href=\'(.*?)\'>(.*?)<'
                match = re.compile(regexcat,re.DOTALL).findall(content2)
                ##pass#print "match =", match
                for url, name  in match:
                        pic = " "
                        url1 = "http://avelip.com" + url
                        ##pass#print "Here in Showcontent url1 =", url1
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)



def getVideos2(name, url):
                pass#print "In xhamster name =", name
                pass#print "In xhamster getVideos6 url =", url

                k = xbmc.Keyboard('', 'Search') ; k.doModal()
                sline = k.getText() if k.isConfirmed() else None
                pass#print "Here in search query sline =", sline
                
                name = sline.replace(" ", "-")
                url1 = "http://www.deviantclip.com/s/" + name
                getPage2(name, url1)

#http://www.deviantclip.com/s/mom-son?p=3

def getPage2(name, urlmain):
                pages = [1, 2, 3, 4, 5, 6]
                for page in pages:
                        url = urlmain + "?p=" + str(page)
                        name = "Page " + str(page)
                        pic = " "
                        addDirectoryItem(name, {"name":name, "url":url, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

#"http://avelip.com/vidc/sleeping?p=2
def getPage(name, url):
                pages = [1, 2, 3, 4, 5, 6]
                for page in pages:
                        url1 = url + "?p=" + str(page)
                        name = "Page " + str(page)
                        pic = " "
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def getVideos(name1, urlmain):
	content = getUrl(urlmain)
	pass#print "getVideos content B =", content

	regexvideo = '<a href=\'http\://avelip\.com/vida/(.*?)\'.*?data-original=\'(.*?)\'.*?alt=\'(.*?)\''
	match = re.compile(regexvideo,re.DOTALL).findall(content)
        pass#print "match =", match
        for url, pic, name in match:
                 name = name.replace('"', '')
                 url = "http://avelip.com/vida/" + url
                 pic = pic 
                 ##pass#print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":4}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)	         
        
                
def playVideo(name, url):
#        content = getUrl("http://avelip.com/vidb/985-extemly_petite_tiny_little_anal_granny.html")
#        content = getUrl("http://avelip.com/vidb/431035-fucking_his_sleeping_mom.html")
#        pass#print "content A =", content
                content = getUrl(url)
                pass#print "content A =", content
                regexcat = "class='iframeclass' src=\"(.*?)\""
                match = re.compile(regexcat,re.DOTALL).findall(content)
                pass#print "match =", match
                web_url = match[0]

#                html = self.net.http_GET(web_url, headers=self.headers).content
                html = getUrl(web_url)
                pass#print "html =", html
                js_link = re.compile("src='(/kt_player/.*?)'", re.DOTALL | re.IGNORECASE).search(html).group(1)
                pass#print "js_link =", js_link
#                js_path = 'https://' + self.domains[0] + js_link + '&ver=x'
                js_path = 'https://vartuc.com' + js_link
                pass#print "js_path =", js_path
                js = getUrl(js_path)
                pass#print "js =", js
                js = js.split(";")
                pass#print "js 2=", js
                js = [line for line in js if (line.startswith("gh") or line.startswith("irue842")) and '=' in line and '(' not in line and ')' not in line]
                pass#print "js 3=", js
                js = "\n".join(js)
                pass#print "js 4=", js
                exec js
#        try:
                vid = re.compile('src="([^"]+)"', re.DOTALL | re.IGNORECASE).search(irue842).group(1)
#            return vid
                pass#print "vid =", vid
                url = vid
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
                ok = showContent1(name, url)
        elif mode == str(2):
		ok = getPage(name, url)
	elif mode == str(3):
		ok = getVideos(name, url)	
	elif mode == str(4):
		ok = playVideo(name, url)	
	elif mode == str(5):
		ok = getVideos2(name, url)	










