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
       sys.argv[0] = sys.argv[0].replace('/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/TURK/', 'plugin://') 
       sys.argv[0] = sys.argv[0].replace('default.py', '')
print "Here in default-py sys.argv B=", sys.argv


import os
import xbmc, xbmcaddon, xbmcplugin
import xbmcgui
import sys
import urllib, urllib2
import time
import re
from htmlentitydefs import name2codepoint as n2cp
import httplib
import urlparse
import socket
from urllib2 import Request, URLError, urlopen
from urlparse import parse_qs
from urllib import unquote_plus
from resources import TURKvodKodiPrsr
	
thisPlugin = int(sys.argv[1])
addonId = "plugin.video.turkvod"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))

try:
    from os import path, system
    if not path.exists(dataPath):
        cmd = "mkdir -p " + dataPath
        system(cmd)
except:
    pass
	   
addon = xbmcaddon.Addon(id=addonId)
mac= ""
adultPIN = addon.getSetting("adultPIN")       
adultPINonoff = addon.getSetting( "adultPINonoff" )
serverId = addon.getSetting( "serverId" )	
TURKVOD_PARSER = TURKvodKodiPrsr.turkvod_parsers()

if addon.getSetting('serverId') == "true":
    server = 'me'
else:
    server = 'com'

Host = 'http://trvod.' + server + '/80/kodik.php'
		
def Url_Al(url, mac = None):
    sign = '?'
    url = url.strip(' \t\n\r')
    if url.find('?') > -1:
        sign = '&'
    if mac != None:
        security_key = ""
        security_param = ""
        url = url + sign + 'box_mac=' + mac + security_key + security_param
    if url.find('|') > -1:
        parts = url.split('|')
        url = parts[0]
        cookie = parts[1]
        req = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 TURKvod 8.0 Kodi',
        'Connection': 'Close',
        'Cookie': cookie})
    else:
        req = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 TURKvod 8.0 Kodi',
        'Connection': 'Close'})
    xmlstream = urllib2.urlopen(req).read()
    return xmlstream
	
def Anamenu():
    content = Url_Al(Host, mac)
    start = 0
    i = 0
    while i < 100:
        n1 = content.find("<channel>", start)
        if n1 < 0:
            break
        n2 = content.find("</channel>", start)
        if n2 < 0:
            break
        ch = content[n1:n2]
        regexvideo = '<title>(.*?)</title>.*?description>.*?>(.*?)</description>.*?<playlist_url>(.*?)</playlist_url>'
        match = re.compile(regexvideo,re.DOTALL).findall(ch)
        name = match[0][0]
        name = name.replace("<![CDATA[", "")
        name = name.replace("]]>", "")
        url = match[0][2]
        url = url.replace("<![CDATA[", "")
        url = url.replace("]]>", "")
        pic = ""
        description = match[0][1]
        description = description.replace("]]>", "")
        ListeyeEkle(name, {"name":name, "url":url, "mode":1}, pic, description)
        start = n2+5       
        i = i+1
    xbmcplugin.endOfDirectory(thisPlugin)

def Liste(name, url):
    if "/aramalar/" in url and 'aramalar_list.php' not in url:
        Ara(url)
    if "HAKKINDA" in name or "%2b18" in name or "erotik" in url or "yetiskin" in url or "Erotik" in url or "Yetiskin" in url:
        if adultPINonoff == "true":			
            if path.exists("/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"):
                pin = adultPIN
                if pin != "1234":
                    return
            else:            
                k = xbmc.Keyboard('', 'PIN i giriniz') ; k.doModal()
                pin = k.getText() if k.isConfirmed() else None
                if pin != adultPIN:
                    return
        if adultPINonoff == "false":
            pass
    else:
        pass

    if "LOKAL" in name:
        try:
            try:
                lokal = os.path.join(os.path.join("/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"), 'TURKvodLokal.xml' )
                url = lokal
                f = open(url,'r')
                data2 = f.read().replace("\n\n", "")
                f.close()
                content = data2
            except:
                lokal = os.path.join(os.path.join(dataPath), 'TURKvodLokal.xml' )
                url = lokal
                f = open(url,'r')
                data2 = f.read().replace("\n\n", "")
                f.close()
                content = data2
        except:
            url = 'http://trvod.me/80/TURKvodLokal.xml'
            content = Url_Al(url, mac)
    else:
        content = Url_Al(url, mac)
    if url.endswith(".m3u") or "type=m3u" in url or 'WORLD_IPTV' in name :
        content = Url_Al(url, mac)
        regexcat = 'EXTINF.*?,(.*?)\\n(.*?)\\n'
        match = re.compile(regexcat,re.DOTALL).findall(content)
        for name, url in match:
            name = name.replace("\n", "")
            name = name.replace("\r", "")
            url = url.replace(" ", "")
            url = url.replace("\n", "")
            url = url.replace("\r", "")
            pic = ""
            ListeyeEkle(name, {"name":name, "url":url, "mode":3}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)
    start = 0
    i = 0
    while i < 10000:
        n1 = content.find("<channel>", start)
        if n1 < 0:
            break
        n2 = content.find("</channel>", start)
        if n2 < 0:
            break
        ch = content[n1:n2]
		
        if "<stream_url>" in ch: 
            name = re.findall('<title>(.*?)</title>', ch, re.IGNORECASE)[0]
            url = re.findall('<stream_url>(.*?)</stream_url>', ch, re.IGNORECASE)[0]
            try:
                pic = re.findall('<description><\!\[CDATA\[<img src=[\'|"](.*?)[\'|"]', ch, re.IGNORECASE)[0]
            except:
                pic = ''
            try:
                description = re.findall('<description><\!\[CDATA\[<img src=[\'|"].*?[\'|"].*?>(.*?)</description>', ch, re.IGNORECASE)[0]
            except:
                description = ''
            name = name.replace("<![CDATA[", "")
            name = name.replace("]]>", "")
            name = name.replace("\n", "")
            name = name.replace("\r", "")
            url = url.replace("<![CDATA[", "")
            url = url.replace("]]>", "")
            url = url.replace("TURKvodModul@", "")
            url = url.replace("@m3u@TURKvod", "")
            description = description.replace("]]>", "")			
            ListeyeEkle(name, {"name":name, "url":url, "mode":2}, pic, description)
			
        elif "<playlist_url>" in ch: 
            name = re.findall('<title>(.*?)</title>', ch, re.IGNORECASE)[0]
            url = re.findall('<playlist_url>(.*?)</playlist_url>', ch, re.IGNORECASE)[0]
            try:
                pic = re.findall('<description><\!\[CDATA\[<img src=[\'|"](.*?)[\'|"]', ch, re.IGNORECASE)[0]
            except:
                pic = ''
            try:
                description = re.findall('<description><\!\[CDATA\[<img src=[\'|"].*?[\'|"].*?>(.*?)</description>', ch, re.IGNORECASE)[0]
            except:
                description = ''
            name = name.replace("<![CDATA[", "")
            name = name.replace("]]>", "")
            name = name.replace("\n", "")
            name = name.replace("\r", "")
            url = url.replace("<![CDATA[", "")
            url = url.replace("]]>", "")
            url = url.replace("TURKvodModul@", "")
            url = url.replace("@m3u@TURKvod", "")
            description = description.replace("]]>", "")			
            ListeyeEkle(name, {"name":name, "url":url, "mode":1}, pic, description)
        else:
            pass
        start = n2+5       
        i = i+1
    if "<next_page_url" in content:
        regexvideo = '<next_page_url.*?http(.*?)\]'
        match = re.compile(regexvideo,re.DOTALL).findall(content)
        name = "Next page..."
        url = "http" + match[0]
        pic = ""
        ListeyeEkle(name, {"name":name, "url":url, "mode":1}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)

def Ara(url):
    k = xbmc.Keyboard('', 'Search') ; k.doModal()
    query = k.getText() if k.isConfirmed() else None
    url = url + "?search=" + query
    name = query
    pic = ""
    ListeyeEkle(name, {"name":name, "url":url, "mode":4}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)
	
def Aramasonucu(name1, url):
    content = Url_Al(url, mac)
    start = 0
    i = 0
    while i < 1000:
        n1 = content.find("<channel>", start)
        if n1 < 0:
              break
        n2 = content.find("</channel>", start)
        if n2 < 0:
              break
        ch = content[n1:n2]
        if "<stream_url>" in ch: 
            name = re.findall('<title>(.*?)</title>', ch, re.IGNORECASE)[0]
            url = re.findall('<stream_url>(.*?)</stream_url>', ch, re.IGNORECASE)[0]
            try:
                pic = re.findall('<description><\!\[CDATA\[<img src=[\'|"](.*?)[\'|"]', ch, re.IGNORECASE)[0]
            except:
                pic = ''
            try:
                description = re.findall('<description><\!\[CDATA\[<img src=[\'|"].*?[\'|"].*?>(.*?)</description>', ch, re.IGNORECASE)[0]
            except:
                description = ''
            name = name.replace("<![CDATA[", "")
            name = name.replace("]]>", "")
            name = name.replace("\n", "")
            name = name.replace("\r", "")
            url = url.replace("<![CDATA[", "")
            url = url.replace("]]>", "")
            url = url.replace("TURKvodModul@", "")
            url = url.replace("@m3u@TURKvod", "")
            description = description.replace("]]>", "")			
            ListeyeEkle(name, {"name":name, "url":url, "mode":2}, pic, description)
			
        elif "<playlist_url>" in ch: 
            name = re.findall('<title>(.*?)</title>', ch, re.IGNORECASE)[0]
            url = re.findall('<playlist_url>(.*?)</playlist_url>', ch, re.IGNORECASE)[0]
            try:
                pic = re.findall('<description><\!\[CDATA\[<img src=[\'|"](.*?)[\'|"]', ch, re.IGNORECASE)[0]
            except:
                pic = ''
            try:
                description = re.findall('<description><\!\[CDATA\[<img src=[\'|"].*?[\'|"].*?>(.*?)</description>', ch, re.IGNORECASE)[0]
            except:
                description = ''
            name = name.replace("<![CDATA[", "")
            name = name.replace("]]>", "")
            name = name.replace("\n", "")
            name = name.replace("\r", "")
            url = url.replace("<![CDATA[", "")
            url = url.replace("]]>", "")
            url = url.replace("TURKvodModul@", "")
            url = url.replace("@m3u@TURKvod", "")
            description = description.replace("]]>", "")			
            ListeyeEkle(name, {"name":name, "url":url, "mode":1}, pic, description)
        else:
            pass				   
        start = n2+5       
        i = i+1
    if "<next_page_url" in content:
        regexvideo = '<next_page_url.*?http(.*?)\]'
        match = re.compile(regexvideo,re.DOTALL).findall(content)
        name = "Next page..."
        url = "http" + match[0]
        pic = ""
        ListeyeEkle(name, {"name":name, "url":url, "mode":4}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)

def VideoListe(name, url):
    if url.find('youtube.com') > -1:
        video_id = url.split('=')
        if len(video_id) > 1:
            xbmc.executebuiltin('PlayMedia(plugin://plugin.video.youtube/?action=play_video&videoid='+video_id[1]+')')
    else:
        print "In VideoList url =", url
        play_url = TURKVOD_PARSER.get_parsed_link(url)
        print "In VideoList play_url =", play_url
        if (play_url == []) or (play_url == ""):
            play_url = url
            Oynat(name, url)
        else:
            if type(play_url) == str:
                url = play_url
                Oynat(name, url)
            elif type(play_url) == tuple:
                names = []
                urls = []
                names = play_url[2]
                urls = play_url[1]
                if names == []:
                    pic = ""
                    url = url
                    name = name
                    Oynat(name, url)
                else:       
                    i = 0
                    for name in names:
                        pic = ""
                        url = urls[i]
                        i = i+1
                        ListeyeEkle(name, {"name":name, "url":url, "mode":3}, pic)
                    xbmcplugin.endOfDirectory(thisPlugin)  

def Oynat(name, url):
    url = url.replace('#', '|')
    if path.exists("/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"): # enigma2 Kodidirect
        pic = "DefaultFolder.png"
        li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
        player = xbmc.Player()
        player.play(url, li)
    else:
        if ".ts" in url and "VAVOO" not in url: 
            import F4mProxy
            from F4mProxy import f4mProxyHelper
            player=f4mProxyHelper()
            player.playF4mLink(url, name, streamtype='TSDOWNLOADER')
        else:
            pic = "DefaultFolder.png"
            li = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=pic)
            player = xbmc.Player()
            player.play(url, li)

def ListeyeEkle(name, parameters={},pic="", description = ""):
    li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
    li.setInfo(type = 'video', infoLabels={'plot': description})
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)

def Parametreler(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

params = Parametreler(sys.argv[2])
name =  str(params.get("name", ""))
url =  str(params.get("url", ""))
url = urllib.unquote(url)
mode =  str(params.get("mode", ""))

if not sys.argv[2]:
    ok = Anamenu()
else:
    if mode == str(1):
        ok = Liste(name, url)
    elif mode == str(2):
        ok = VideoListe(name, url)
    elif mode == str(3):
        ok = Oynat(name, url)
    elif mode == str(4):
        ok = Aramasonucu(name, url)




