#!/usr/bin/python
# -*- coding: utf-8 -*-
def youtube():
 import os, sys, xpath, xbmc
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
       sys.argv[0] = sys.argv[0].replace('/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/plugins/', 'plugin://') 
       sys.argv[0] = sys.argv[0].replace('default.py', '')
 print "Here in default-py sys.argv B=", sys.argv






 
 
 import xbmc,xbmcaddon, xbmcplugin
 import xbmcgui
 import os, sys
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
 import ssl
 
 import json
 import codecs
 from urlparse import urljoin
 
#Here in default-py sys.argv B= ['plugin://plugin.video.youtube/play/', '1', '?video_id=63dLq5GHUIc']
#Here in default-py sys.argv B= ['plugin://plugin.video.youtube/channel/UCFKE7WVJfvaHW5q283SxchA/', '4', '?page=0']
 thisPlugin = int(sys.argv[1])
 addonId = "plugin.video.youtube"
 adn = xbmcaddon.Addon('plugin.video.youtube')
#Hostmain = adn.getSetting('domain')
#pass#pass#print "Hostmain =", Hostmain
#Host = Hostmain + "/index.php?"
#Hostpop = Hostmain + "?sort=views"
#Hosttv = Hostmain + "/?tv"
 dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
 if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)
 
 def getUrl(url):
        print "Here in youtube getUrl url =", url
 	req = urllib2.Request(url)
 	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        try:
               response = urllib2.urlopen(req)
        except:
               ctx = ssl.create_default_context()
               ctx.check_hostname = False
               ctx.verify_mode = ssl.CERT_NONE
  	       response = urllib2.urlopen(req, context=ctx)
 	link=response.read()
 	response.close()
 	return link
 	
 def showContent():

        names = []
        urls = []
        modes = []
        
        names.append("Youtube-UK")
        urls.append("https://www.youtube.com/")
        modes.append("11")  
        names.append("Youtube-IT")
        urls.append("https://www.youtube.com/")
        modes.append("12")                            
        names.append("Sports")
        urls.append("https://www.youtube.com/channel/UCEgdi0XIXXZ-qJOFPf4JSKw")
        modes.append("3")
        names.append("Gaming")
        urls.append("https://www.youtube.com/channel/UCOpNcN46UbXVtpKMrmU4Abg")
        modes.append("3")
        names.append("Films")
        urls.append("https://www.youtube.com/user/YouTubeMoviesGB/videos?shelf_id=4&view=26&sort=dd")
        modes.append("6")
        names.append("TV Shows")
        urls.append("https://www.youtube.com/user/YouTubeShowsGB/videos?shelf_id=4&view=38&sort=dd")
        modes.append("6") 
        names.append("News")
        urls.append("https://www.youtube.com/channel/UCYfdidRxbB8Qhf0Nx7ioOYw")
        modes.append("3") 
        names.append("Spotlight")
        urls.append("https://www.youtube.com/channel/UCULkRHBdLC5ZcEQBaL0oYHQ")
        modes.append("3") 
        names.append("360deg Videos")
        urls.append("https://www.youtube.com/channel/UCzuqhhs6NWbgTzMuM09WKDQ")
        modes.append("3") 
        pass#print "names =", names
        i1 = 0
        for name in names:
                        pass#print "i1 =", i1
                        url = urls[i1]
                        mode = modes[i1]
                        pic = " "
                        ##pass#print "Here in Showcontent url1 =", url1
                        i1 = i1+1
                        addDirectoryItem(name, {"name":name, "url":url, "mode":mode}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)

 def showContent1():
        name = "Search"
        url = "https://www.youtube.com/"
        pic = " "
        addDirectoryItem(name, {"name":name, "url":url, "mode":1}, pic)
 
        names = []
        urls = []
        modes = []
        
        names.append("Trending")
        urls.append("https://www.youtube.com/feed/trending")
        modes.append("31")  
        names.append("Browse Channels")
        urls.append("https://www.youtube.com/feed/guide_builder?gl=GB")
        modes.append("3")  

        names.append("Music Videos")
        urls.append("https://www.youtube.com/channel/UC-9-kyTW8ZkZNDHQJ6FgpwQ")
        modes.append("3")  
        names.append("Popular")
        urls.append("https://www.youtube.com/channel/UCR44SO_mdyRq-aTJHO5QxAw")
        modes.append("3")                            
        names.append("Sports")
        urls.append("https://www.youtube.com/channel/UCEgdi0XIXXZ-qJOFPf4JSKw")
        modes.append("3")
        names.append("Gaming")
        urls.append("https://www.youtube.com/channel/UCOpNcN46UbXVtpKMrmU4Abg")
        modes.append("3")
        names.append("Films")
        urls.append("https://www.youtube.com/user/YouTubeMoviesGB/videos?shelf_id=4&view=26&sort=dd")
        modes.append("6")
        names.append("TV Shows")
        urls.append("https://www.youtube.com/user/YouTubeShowsGB/videos?shelf_id=4&view=38&sort=dd")
        modes.append("6") 
        names.append("News")
        urls.append("https://www.youtube.com/channel/UCYfdidRxbB8Qhf0Nx7ioOYw")
        modes.append("3") 
        names.append("Spotlight")
        urls.append("https://www.youtube.com/channel/UCULkRHBdLC5ZcEQBaL0oYHQ")
        modes.append("3") 
        names.append("360deg Videos")
        urls.append("https://www.youtube.com/channel/UCzuqhhs6NWbgTzMuM09WKDQ")
        modes.append("3") 
        print "names =", names
        i1 = 0
        for name in names:
                        print "i1 =", i1
                        url = urls[i1]
                        mode = modes[i1]
                        pic = " "
                        ##print "Here in Showcontent url1 =", url1
                        i1 = i1+1
                        addDirectoryItem(name, {"name":name, "url":url, "mode":mode}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)

 def showContent2():
        name = "Search"
        url = "https://www.youtube.com/"
        pic = " "
        addDirectoryItem(name, {"name":name, "url":url, "mode":1}, pic)
 
        names = []
        urls = []
        modes = []
        
        names.append("Trending")
        urls.append("https://www.youtube.com/feed/trending")
        modes.append("31")  
        names.append("Music Videos")
        urls.append("https://www.youtube.com/channel/UC-9-kyTW8ZkZNDHQJ6FgpwQ")
        modes.append("3")  
        names.append("Popular")
        urls.append("https://www.youtube.com/channel/UCR44SO_mdyRq-aTJHO5QxAw")
        modes.append("3")                            
        names.append("Sports")
        urls.append("https://www.youtube.com/channel/UCEgdi0XIXXZ-qJOFPf4JSKw")
        modes.append("3")
        names.append("Gaming")
        urls.append("https://www.youtube.com/channel/UCOpNcN46UbXVtpKMrmU4Abg")
        modes.append("3")
        names.append("Films")
        urls.append("https://www.youtube.com/user/YouTubeMoviesGB/videos?shelf_id=4&view=26&sort=dd")
        modes.append("6")
        names.append("TV Shows")
        urls.append("https://www.youtube.com/user/YouTubeShowsGB/videos?shelf_id=4&view=38&sort=dd")
        modes.append("6") 
        names.append("News")
        urls.append("https://www.youtube.com/channel/UCYfdidRxbB8Qhf0Nx7ioOYw")
        modes.append("3") 
        names.append("Spotlight")
        urls.append("https://www.youtube.com/channel/UCULkRHBdLC5ZcEQBaL0oYHQ")
        modes.append("3") 
        names.append("360deg Videos")
        urls.append("https://www.youtube.com/channel/UCzuqhhs6NWbgTzMuM09WKDQ")
        modes.append("3") 
        print "names =", names
        i1 = 0
        for name in names:
                        print "i1 =", i1
                        url = urls[i1]
                        mode = modes[i1]
                        pic = " "
                        ##print "Here in Showcontent url1 =", url1
                        i1 = i1+1
                        addDirectoryItem(name, {"name":name, "url":url, "mode":mode}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)
                            
 def getPage(name, url):
                pages = [1, 2, 3, 4, 5, 6]
                print "In getPage name A=", name
                print "In getPage url A=", url
                for page in pages:
                        url1 = url + "&page=" + str(page)
                        name1 = name + " - Page " + str(page)
                        if "TV-" in name:
                               url1 = url + "&page=" + str(page)
                        print "In getPage name B=", name1
                        print "In getPage url1 B=", url1
                        pic = " "
                        if "Popular" in name:
                               addDirectoryItem(name1, {"name":name1, "url":url1, "mode":3}, pic)
                        elif "All-Movies" in name:
                               addDirectoryItem(name1, {"name":name1, "url":url1, "mode":7}, pic)
                        elif "TV-" in name:
                               addDirectoryItem(name1, {"name":name1, "url":url1, "mode":9}, pic)       
                xbmcplugin.endOfDirectory(thisPlugin)
 
 def getVideos(name, url):
                f = open("/tmp/xbmc_search.txt", "r")
                icount = 0
                for line in f.readlines(): 
                    print "In getVideos line =", line
                    sline = line
                    icount = icount+1
                    if icount > 0:
                           break
 
                name = sline.replace(" ", "+")
                print "In getVideos name =", name
                url1 = "https://www.youtube.com/results?search_query=" + name
                pages = [1, 2, 3]
                for page in pages:
                        url = url1 + "&page=" + str(page)
                        print "Here in getVideos url =", url
                        name = "Page " + str(page)
                        pic = " "
                        addDirectoryItem(name, {"name":name, "url":url, "mode":21}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)
 
 def getVideos21(name1, urlmain):
        print "In getVideos21 urlmain =", urlmain
 	content = getUrl(urlmain)
 	print "In getVideos21 content =", content
 	n1 = content.find('class="section-list', 0)
 	n2 = content.find('div class="yt-uix-pager search-pager', n1)
 	content2 = content[n1:n2]
 	print "In getVideos21 content2 =", content2
                          
#	regexvideo = '/div><div class="yt-lockup-content"><h3 class="yt-lockup-title "><a href="/watch\?v=(.*?)".*?title="(.*?)".*?img src="(.*?)"'
##	regexvideo = '/div><div class="yt-lockup-content.*?<a href="/watch\?v=(.*?)".*?title="(.*?)".*?img src="(.*?)"'
 	regexvideo = '/div><div class="yt-lockup-content.*?<a href="/watch\?v=(.*?)".*?title="(.*?)"'
 
 	match = re.compile(regexvideo,re.DOTALL).findall(content2)
        print "In getVideos21 match =", match
        
        for url, name in match:
                 pic = " "
                 #print "Here in getVideos21 name, url =", name, url
 	         addDirectoryItem(name, {"name":name, "url":url, "mode":5}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)
        
        
 def getVideos2(name1, urlmain):
 	content = getUrl(urlmain)
	print "content B =", content
 	
 	regexvideo = 'class="yt-uix-sessionlink branded-page.*?span class="" >(.*?)<.*?a href.*?list=(.*?)"'
 	match = re.compile(regexvideo,re.DOTALL).findall(content)
        print "In youtube getVideos2 match =", match
        for name, url in match:
                 pic = ' '
                 url1 = 'https://www.youtube.com/playlist?list=' + url
 
                 print "Here in youtube getVideos2 url1 =", url1
 	         addDirectoryItem(name, {"name":name, "url":url1, "mode":4}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)
                
 def getVideos3(name1, urlmain):
 	content = getUrl(urlmain)
#	print "content B3 =", content
 	
 	regexvideo = 'tr class="pl-video yt-uix-.*?data-title="(.*?)".*?a href="/watch\?v=(.*?)&.*?data-thumb="(.*?)"'
 	match = re.compile(regexvideo,re.DOTALL).findall(content)
        print "In youtube getVideos3 match =", match
        for name, url, pic in match:
#                 pic = "http:" + pic
                 pic = " "
                 print "Here in youtube getVideos3 url =", url
 	         addDirectoryItem(name, {"name":name, "url":url, "mode":5}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)
 
 def getVideos4X(name, url):   
        args = '/usr/lib/enigma2/python/Plugins/Extensions/KodiDirect/plugins/plugin.video.youtube/default.py', '36', '?plugin://plugin.video.youtube/play/?video_id=BfiTt920nr8'
        cmd = "python '/usr/lib/enigma2/python/Plugins/Extensions/KodiDirect/plugins/plugin.video.youtube/default.py' '1' '?plugin://plugin.video.youtube/play/?video_id=" + url + "'" 
        os.system(cmd)
 
 def getVideos5XX(name, url):  
        url = "https://www.youtube.com/watch?v=" + url   
        print "In getVideos4 url =", url    
        cmd = "python '/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/scripts/script.module.youtube.dl/lib/youtube_dl/__main__.py' --skip-download --get-url '" + url + "' > /tmp/vid.txt"
#        cmd = "python '/usr/lib/enigma2/python/__main__.py' --skip-download --get-url '" + url + "' > /tmp/vid.txt"
        print "In getVideos4 cmd =", cmd
        os.system(cmd)
        url = "/tmp/vid.txt"
        player = xbmc.Player()
        player.play(url)
 
 
 def getVideos5(name, url):  
      
        import YDStreamExtractor
        YDStreamExtractor.disableDASHVideo(True) #Kodi (XBMC) only plays the video for DASH streams, so you don't want these normally. Of course these are the only 1080p streams on YouTube
        print "In youtube getVideos4 url =", url
        url = "https://www.youtube.com/watch?v=" + url #a youtube ID will work as well and of course you could pass the url of another site
        vid = YDStreamExtractor.getVideoInfo(url,quality=2) #quality is 0=SD, 1=720p, 2=1080p and is a maximum
        stream_url = vid.streamURL() #This is what Kodi (XBMC) will play
        print "youtube stream_url =", stream_url
#        img = " "
#        listitem = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
        playfile = xbmc.Player()
#        playfile.play(stream_url, listitem)
        playfile.play(stream_url)
 
 def getVideos4(name, url):
        print "youtube url =", url
        stream_url = getVideoUrl(url)
        print "youtube stream_url =", stream_url
        """
        if not "signature" in stream_url:
                getVideos5(name, url)
        else:        
                playfile = xbmc.Player()
                playfile.play(stream_url)
        """
        playVideo(name, stream_url)
 
 def getVideoUrl(vid):
       from YouTubeVideoUrl import YouTubeVideoUrl
       yt = YouTubeVideoUrl()
       vidurl = yt.extract(vid)
       return vidurl
 
        
 
 def playVideo(name, url):
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
    #print "In addDirectoryItem name, url =", name, url
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
#Here in default-py sys.argv B= ['plugin://plugin.video.youtube/', '4', '?path=/root/video&path=root/video&action=play_video&videoid=q3WIm2jrxSc']
 if "action=play_video" in sys.argv[2]:
            sys.argv[2] = sys.argv[2].replace("?", "?mode=5&")
            sys.argv[2] = sys.argv[2].replace("videoid", "url")
 
#Here in default-py sys.argv B= ['plugin://plugin.video.youtube/channel/UCFKE7WVJfvaHW5q283SxchA/', '4', '?page=0']
    
 if ("youtube/channel/" in sys.argv[0]) and (not "mode=" in sys.argv[2]):
            arg1 = sys.argv[0]  
            n1 = arg1.find("/channel", 0)
            n2 = arg1.find("/", (n1+3))
            ch = arg1[(n2+1):]
            ch = ch.replace("/", "")
            print "Here in youtube default-py ch =", ch
            name = "channel"
            url = "https://www.youtube.com/channel/" + ch
            pic = " "
#            addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
#            xbmcplugin.endOfDirectory(thisPlugin)
            getVideos2(name, url)
#Here in default-py sys.argv B= ['plugin://plugin.video.youtube/play/', '1', '?video_id=63dLq5GHUIc']
            
 if "youtube/play" in sys.argv[0]:
            arg1 = sys.argv[2]
            n1 = arg1.find("video_id", 0)
            n2 = arg1.find("=", n1)
            n3 = arg1.find("&", n2)
            if n3 < 0:
                   url = arg1[(n2+1):]
            else:       
                   url = arg1[(n2+1):n3]
            print "Here in default-py url =", url     
            pic = " "
            name = "videoName"
#            addDirectoryItem(name, {"name":name, "url":url, "mode":5}, pic)
#            xbmcplugin.endOfDirectory(thisPlugin)
            getVideos4(name, url)
            
 params = parameters_string_to_dict(sys.argv[2])
 name =  str(params.get("name", ""))
 url =  str(params.get("url", ""))
 url = urllib.unquote(url)
 mode =  str(params.get("mode", ""))
 
 if not sys.argv[2]:
 	ok = showContent()
 else:
        if mode == str(11):
 	        ok = showContent1()
        elif mode == str(12):
 	        ok = showContent2()

        elif mode == str(1):
 		ok = getVideos(name, url)
 	elif mode == str(21):
 		ok = getVideos21(name, url)	
 		
 	elif mode == str(2):
 		ok = getPage(name, url)	
        elif mode == str(3):
 		ok = getVideos2(name, url)
 	elif mode == str(31):
 		ok = getVideos21(name, url)	
        elif mode == str(4):
 		ok = getVideos3(name, url)	        	
        elif mode == str(5):
 		ok = getVideos4(name, url)
        elif mode == str(6):
 		ok = getVideos5(name, url)
        elif mode == str(7):
 		ok = getVideos6(name, url)
        elif mode == str(8):
 		ok = getVideos7(name, url)
        elif mode == str(9):
 		ok = getVideos8(name, url)
        elif mode == str(10):
 		ok = getVideos9(name, url)
        elif mode == str(11):
 		ok = getVideos10(name, url)
        elif mode == str(12):
 		ok = getVideos11(name, url)
        elif mode == str(13):
 		ok = getVideos12(name, url)
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 





