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

from XXXresolver.resolver import getVideo


thisPlugin = int(sys.argv[1])
addonId = "plugin.video.search_porn"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)
       
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
	

def showContent():
        names = []
        urls = []
        names.append("Search-empflix.com")
        url = "https://www.empflix.com/search.php?what=searchText&sb=&su=&sd=&dir=&f=&p=&category=&page=iPage&tab=videos"
        urls.append(url)
        names.append("Search-tnaflix.com")
        url = "https://www.tnaflix.com/search.php?what=searchText&tab="
        urls.append(url)
        names.append("Search-pornhub.com")
        url = "https://www.pornhub.com/video/search?search=searchText&page=iPage"
        urls.append(url)

        names.append("Search-motherless.com")
        url = "http://motherless.com/term/videos/searchText?range=0&size=0&sort=relevance&page=iPage"
        urls.append(url)
        names.append("Search-sunporno.com")
        url = "https://www.sunporno.com/search/searchText/"
        urls.append(url)
        names.append("Search-shemaletubevideos.com")
        url = "http://www.shemaletubevideos.com/search/video/searchText/iPage/"
        urls.append(url)
        names.append("Search-xnxx.com")
        url = "http://www.xnxx.com/?k=searchText&p=iPage"
#               http://www.xnxx.com/?k=anal&p=6
        urls.append(url)
        names.append("Search-luxuretv.com")
        url = "http://en.luxuretv.com/search/videos/searchText/pageiPage.html"
        urls.append(url)

        names.append("Search-hotgoo.com")
        url = "http://www.hotgoo.com/search.php?page=iPage&query=searchText"
        urls.append(url)
        names.append("Search-heavy-r.com")
        url = "http://www.heavy-r.com/search/searchText_iPage.html"
        urls.append(url)
        names.append("Search-xhamster.com")
        url = "http://xhamster.com/search.php?q=searchText&qcat=video&page=iPage"
        urls.append(url)
#        names.append("Search-spicytranny.com")
#        url = "http://www.spicytranny.com/en/search/searchText/iPage/"
#        urls.append(url)
        names.append("Search-deviantclip.com")
        url = "http://www.deviantclip.com/s/searchText?p=iPage"
        urls.append(url)
#        names.append("Search-esmatube.com")
#        url = "http://esmatube.com/top/searchText"
#        urls.append(url)
        names.append("Search-jizzbunker.com")
        url = "http://jizzbunker.com/search?query=searchText&page=iPage"
        urls.append(url)
#        names.append("Search-tubeshemales.com")
#        url = "http://www.tubeshemales.com/search/?q=searchText&p=iPage"
#        urls.append(url)
        names.append("Search-xvideos.com")
        url = "http://www.xvideos.com/?k=searchText&p=iPage"
        urls.append(url)
        names.append("Search-pornoxo.com")
        url = "https://www.pornoxo.com/search/searchText/iPage/?sort=mw&so=y"
        urls.append(url)


        names.append("Search-youporn.com")
        url = "https://www.youporn.com/search/?query=searchText"
        urls.append(url)
        names.append("Search-vporn.com")
        url = "https://www.vporn.com/search/relevance/search?q=searchText&page=iPage"
        urls.append(url)
        names.append("Search-sheshaft.com")
        url = "https://www.sheshaft.com/search/iPage/?q=searchText"
        urls.append(url)

        names.append("Search-txxx.com")
        url = "https://www.txxx.com/search/iPage/?s=searchText"
        urls.append(url)

        names.append("Search-befuck.com")
        url = "https://befuck.com/search/searchText/iPage"
        urls.append(url)

        names.append("Search-pornxs.com")
        url = "http://pornxs.com/search.php?s=searchText&type=videos&or=&up=&page=iPage"
        urls.append(url)

        names.append("Search-ashemaletube.com")
        url = "https://www.ashemaletube.com/search/searchText/iPage/?sort=mw&so=y"
        urls.append(url)
#mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
        names.append("Search-tubemania.org")
        url = "https://tubemania.org/videos/searchText/?p=iPage"
        urls.append(url)

        names.append("Search-femdom-fetish-tube.com")
        url = "http://femdom-fetish-tube.com/search?query=searchText&page=iPage"
        urls.append(url)

        names.append("Search-tranny.one")
        url = "https://www.tranny.one/search/searchText/"
        urls.append(url)

        names.append("Search-flashtranny.com")
        url = "http://www.flashtranny.com/search/searchText"
        urls.append(url)


#  if ("txxx" in url) or ("sunporno" in url) or ("xhamster" in url) or ("befuck" in url) or ("xtube" in url) or ("nuvid" in url) or ("pornxs" in url) or ("sheshaft" in url) or ("freeshemaletube" in url) or ("ashemaletube" in url) or ("upornia" in url):


        
        i = 0
        for name in names:
                url = urls[i]
                pic = " "
                i = i+1
                addDirectoryItem(name, {"name":name, "url":url, "mode":1}, pic)
        xbmcplugin.endOfDirectory(thisPlugin)

        
def search(siteName, url):
                print "In Search siteName, url =", siteName, url
                f = open("/tmp/xbmc_search.txt", "r")
                icount = 0
                for line in f.readlines(): 
                    sline = line
                    icount = icount+1
                    if icount > 0:
                           break
                if "esmatube" in siteName:
                        name1 = sline.replace(" ", "_")
                elif "luxuretv" in siteName:
                        name1 = sline.replace(" ", "-")
                elif "pornoxo" in siteName:
                        name1 = sline.replace(" ", "_")        
                elif "ashemaletube" in siteName:
                        name1 = sline.replace(" ", "_")        

                elif "befuck" in siteName:
                        name1 = sline.replace(" ", "%20")        
                elif "pornxs" in siteName:
                        name1 = sline.replace(" ", "%20")        
                elif "empflix" in siteName:
                        name1 = sline.replace(" ", "%20")        
                elif "tnaflix" in siteName:
                        name1 = sline.replace(" ", "%20")        
                elif "tubemania" in siteName:
                        name1 = sline.replace(" ", "-")        
                elif "femdom" in siteName:
                        name1 = sline.replace(" ", "%20")        
                elif "flashtranny" in siteName:
                        name1 = sline.replace(" ", "%20")   
                else:        
                        name1 = sline.replace(" ", "+")
                print "name1 =", name1        
                pages = [1, 2, 3, 4, 5, 6]
                for page in pages:
                        page = str(page)
                        print "In Search url =", url
                        url1 = url.replace("searchText", name1)
                        print "Here in search url1 1=", url1
                        if "nudevista" in siteName:
                               n1 = (int(page)-1)*25
                               url1 = url1.replace("iPage", str(n1))
                        elif "xvideos" in siteName:
                               n1 = (int(page)-1)
                               url1 = url1.replace("iPage", str(n1))

                        else:       
                               url1 = url1.replace("iPage", page)
                        print "Here in search url1 2=", url1
                        name = siteName + "-Page" + str(page)
                        name = name.replace("Search-", "")
                        name = name.replace(".com", "")
                        pic = " "
                        addDirectoryItem(name, {"name":name, "url":url1, "mode":2}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

def getVideos(name1, urlmain):
	content = getUrl(urlmain)
	print "In getVideos name1 =", name1
	print "content B =", content
        if "motherless" in name1:
	       regexvideo = 'class="thumb video medium.*?<a href="(.*?)".*?img class="static" src="(.*?)".*?alt="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "getVideos match 1=", match
               for url, pic, name in match:
                 name = name1 + name.replace('"', '')
                 name = name.replace("Page", "")
                 url = url
                 pic = pic 
                 #print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
	       xbmcplugin.endOfDirectory(thisPlugin)  
        elif "shemaletubevideos" in name1:
	       regexvideo = 'div class="thumb"> <a href="(.*?)" class="ha">(.*?)<.*?img src="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "getVideos match 2=", match
               for url, name, pic in match:
                 name = name1 + name.replace('"', '')
                 name = name.replace("Page", "")
                 url = url
                 pic = pic 
                 #print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
	         
               xbmcplugin.endOfDirectory(thisPlugin)	         
        elif "xnxx" in name1:
	       regexvideo = 'class="thumb-block.*?a href="(.*?)".*?data-src="(.*?)".*?title="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "getVideos match 3=", match
               for url, pic, name in match:
                 #http://www.xnxx.com/video-8xolv4f/anal_wife
                 url1 = "http://www.xnxx.com" + url
                 name = name1 + name.replace('"', '')
                 name = name.replace("Page", "")
                 pic = pic 
                 #print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic)
	         
               xbmcplugin.endOfDirectory(thisPlugin)
               
        elif "luxuretv" in name1:
	       regexvideo = '<div class="content".*?a href="(.*?)"><img class="img" src="(.*?)" alt="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "getVideos match 3=", match
               for url, pic, name in match:
                 name = name1 + name.replace('"', '')
                 name = name.replace("Page", "")
                 pic = pic 
                 #print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)         
               xbmcplugin.endOfDirectory(thisPlugin)               	         

        elif "hotgoo" in name1:
	       regexvideo = '</td><td width=160><a href="(.*?)".*?img src="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "getVideos match 1=", match
               for url, pic in match:
                 n1 = url.rfind("/")
                 name = name1 + url[n1:]
                 url1 = "http://www.hotgoo.com" + url
                 pic = pic 
                 #print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic)
	       xbmcplugin.endOfDirectory(thisPlugin)  
        elif "heavy-r" in name1:
	       regexvideo = 'iv class="video-item compact.*?a href="(.*?)".*?img src="(.*?)".*?alt="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "getVideos match 2=", match
               for url, pic, name in match:
                 name = name1 + name.replace('"', '')
                 name = name.replace("Page", "")
                 url = "http://www.heavy-r.com" + url
                 pic = pic 
                 #print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
	         
               xbmcplugin.endOfDirectory(thisPlugin)	         

        elif "xhamster" in name1:
               	regexvideo = 'thumb-list__item video-thumb.*?href="(.*?)".*?<img class.*?src="(.*?)".*?alt="(.*?)"'
	        match = re.compile(regexvideo,re.DOTALL).findall(content)
                print "match =", match
                for url, pic, name in match:
                       name = name1 + name.replace('"', '')
                       name = name.replace("Page", "")
                       if "new-british" in url:
                               name = "British"
                       pic = pic 
                 #pass#print "Here in getVideos url =", url
	               addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)	  

               
        elif "spicytranny" in name1:
  	        n1 = content.find('<ul class="content">', 0)
                n2 = content.find('</ul>', n1)
                content = content[n1:n2]
	        regexvideo = '<li.*?ref="(.*?)".*?title="(.*?)"><img class'
	        match = re.compile(regexvideo,re.DOTALL).findall(content)
                print "In getVideos match =", match
                for url, name in match:
#                 if "xhamster" not in url:
#                        continue 
                       name = name1 + name.replace('"', '')
                       name = name.replace("Page", "")
                       pic = " " 
                       url = "http://www.spicytranny.com" + url
                       ##print "Here in getVideos url =", url
	               addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)

        elif "deviantclip" in name1:
	       regexvideo = 'thumb_container video.*?href="(.*?)" title="(.*?)">.*?src="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for url, name, pic in match:
                 name = name1 + name.replace('"', '')
                 url = "http://www.deviantclip.com" + url
                 pic = pic 
                 #print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "esmatube" in name1:
	       regexvideo = '<iframe class=iframeresdif src="(.*?)".*?data-title=\'(.*?)\'.*?src=\'(.*?)\''
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for url, name, pic in match:
                 name = name1 + name.replace('"', '')
                 name = name.replace("Page", "")
                 pic = pic 
                 print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)         
               xbmcplugin.endOfDirectory(thisPlugin)  
             	         
        elif "pornplaying" in name1:
	       regexvideo = '<a href="/video/(.*?)".*?<img src="(.*?)" title="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               #http://www.pornplaying.com/video/126567/Real_Amateur_Doggystyle_Sex/
               for url, pic, name in match:
                 name = name1 + name.replace('"', '')
                 name = name.replace("Page", "")
                 url1 = "http://www.pornplaying.com/video/" + url
                 pic1 = pic 
                 print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  
                
        elif "XXtubeshemalesXX" in name1:
               host = "http://www.tubeshemales.com"
               content = getUrl2(urlmain, host)
               print "content B2 =", content
	       regexvideo = 'data-title="(.*?)".*?data-thumbnail="(.*?)".*?u=(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for name, pic, url in match:
                 print "In tubeshemales url =", url
                 if ("txxx" in url) or ("sunporno" in url) or ("xhamster" in url) or ("befuck" in url) or ("xtube" in url) or ("nuvid" in url) or ("pornxs" in url) or ("sheshaft" in url) or ("freeshemaletube" in url) or ("ashemaletube" in url) or ("upornia" in url):
                     name = name1 + name.replace('"', '')
                     name = name.replace("Page", "")
                     url = url.replace("%3A", ":")
                     url = url.replace("%2F", "/")
                     url = url.replace("%3F", "?")
                     url = url.replace("%3D", "=")
                     url = url.replace("%26", "&")
                     print "Here in getVideos url =", url
	             addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic) 
                 else:    
                     continue        
               xbmcplugin.endOfDirectory(thisPlugin)  
        elif "tubeshemales" in name1:
               
	       regexvideo = 'data-title="(.*?)".*?data-thumbnail="(.*?)".*?data-item-url="(.*?)".*?data-source="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "tubeshemales match =", match
               sources = ["txxx", "sunporno", "xhamster", "befuck", "xtube", "nuvid", "pornxs", "sheshaft", "freeshemaletube", "ashemaletube", "upornia"]
               for name, pic, url, source in match:
                 if source.lower() in sources:
                     print "In tubeshemales source 2=", source
                     print "In tubeshemales name 2=", name
                     url1 = "https://www.tubeshemales.com" + url.replace("&amp;", "&")
                     host = "https://www.tubeshemales.com"
                     content2 = getUrl2(url1, urlmain)
#                 content2 = getUrl(url1)
                     print "tubeshemales content2 =", content2
                     regexvideo = 'link rel="canonical" href="(.*?)"'
	             match = re.compile(regexvideo,re.DOTALL).findall(content2)
                     url = match[0]
                     print "In tubeshemales url 2=", url
                     name = name1 + name.replace('"', '')
                     name = name.replace("Page", "")
                     print "Here in getVideos url =", url
	             addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic) 
                 else:    
                     continue        
               xbmcplugin.endOfDirectory(thisPlugin)  


        elif "nudevista" in name1:
 	       regexvideo = 'add"></div><a href="(.*?)".*?<img src="(.*?)".*?</a> <b>(.*?)</b>'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for url, pic, name in match:
                 name = name1 + name.replace('"', '')
                 name = name.replace("Page", "")
                 pic1 = pic 
                 print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "sunporno" in name1:
 	       regexvideo = 'data-type="movie".*?href="(.*?)".*?src="(.*?)".*?title="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               pic = " "
               for url, pic, name in match:
                 name = name1 + name.replace('"', '')
                 name = name.replace("Page", "")
                 pic1 = pic 
                 print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "jizzbunker" in name1:
 	       regexvideo = '<li><figure>.*?href="(.*?)".*?title="(.*?)".*?data-original="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               pic = " "
               for url, name, pic in match:
                 name = name1 + name.replace('"', '')
                 name = name.replace("Page", "")
                 pic1 = pic 
                 print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "pornoxo" in name1:
 	       regexvideo = 'data-video-id.*?a href="(.*?)".*?src="(.*?)".*?" alt="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for url, pic, name in match:
                 name = name1 + name.replace('"', '')
                 name = name.replace("Page", "")
                 pic1 = pic 
                 url1 = "https://www.pornoxo.com" + url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "youporn" in name1:
 	       regexvideo = 'a href="/watch/(.*?)".*?alt=\'(.*?)\'.*?data-thumbnail="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for url, name, pic in match:
                 name = name1 + name.replace('"', '')
                 name = name.replace("Page", "")
                 pic1 = pic 
                 url1 = "https://www.youporn.com/watch/" + url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "vporn" in name1:
 	       regexvideo = 'div  class="video">.*?<a  href="(.*?)".*?<img src="(.*?)" alt="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for url, pic, name in match:
                 name = name1 + name.replace('&plus;', ' ')
                 name = name.replace("Page", "")
                 pic1 = pic 
                 url1 = url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "sheshaft" in name1:
# 	       regexvideo = 'div class="item".*?href="(.*?)".*?title="(.*?)".*?"thumb" src="(.*?)"'
 	       regexvideo = 'itemtype="https://schema.org/ImageObject.*?a href="(.*?)".*?img src="(.*?)".*?alt="(.*?)"'

	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for url, pic, name in match:
                 name = name1 + name.replace('&plus;', ' ')
                 name = name.replace("Page", "")
                 pic1 = pic 
                 url1 = url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "xvideos" in name1:
 	       regexvideo = 'data-src="(.*?)".*?data-videoid.*?a href="(.*?)" title="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               pic = " "
               #https://www.xvideos.com/video31410981/morther_and_son_go_trip_and_together_on_bedroom
               for pic, url, name in match:
                 name = name1 + name.replace('&plus;', ' ')
                 name = name.replace("Page", "")
                 pic1 = pic 
                 url1 = "https://www.xvideos.com" + url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "txxx" in name1:
 	       regexvideo = '"un-grid--thumb--content"><a href="(.*?)".*?img src="(.*?)" alt="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for url, pic, name in match:
                 name = name.replace("Page", "")
                 pic1 = pic 
                 url1 = url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "befuck" in name1:
 	       regexvideo = '<div class="ic">.*?href="(.*?)" title="(.*?)".*?data-src="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               pic = " "
               for url, name, pic in match:
                 name = name.replace("Page", "")
                 pic1 = pic 
                 url1 = url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "pornxs" in name1:
               n1 = content.find('<div class="content', 0)
               content = content[n1:]
 	       regexvideo = '<a href="(.*?)".*?img src="(.*?)" alt="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for url, pic, name in match:
                 name = name.replace("Page", "")
                 pic1 = pic 
                 url1 = "http://pornxs.com" + url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "ashemaletube" in name1:
 	       regexvideo = '<div class="thumb-inner-wrapper.*?href="(.*?)".*?img src="(.*?)" alt="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               pic = " "
               for url, pic, name in match:
                 name = name1 + name.replace('&#039;', '')
                 name = name.replace("Page", "")
                 pic1 = pic 
                 url1 = "https://www.ashemaletube.com" + url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

#https://www.empflix.com/anal-porn/Nasty-Filipino-whore/video162209
        elif "empflix" in name1:
 	       regexvideo = "data-vid=.*?href='(.*?)'.*?data-original='(.*?)' alt=\"(.*?)\""
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for url, pic, name in match:
                 name = name1 + name.replace("Page", "")
                 pic1 = pic 
                 url1 = "https://www.empflix.com" + url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  
#https://www.tnaflix.com/amateur-porn/Awesome-BDSM-Hardcore/video757493
        elif "tnaflix" in name1:
 	       regexvideo = "data-vid=.*?data-name='(.*?)'.*?href='(.*?)'.*?data-original='(.*?)'"
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for name, url, pic in match:
                 name = name1 + name.replace('&plus;', ' ')
                 name = name.replace("Page", "")
                 pic1 = pic 
                 url1 = "https://www.tnaflix.com" + url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  
#https://www.pornhub.com/view_video.php?viewkey=ph595ab61fdbe65
        elif "pornhub" in name1:
             start = 0
             i = 0
             while i<40:
               n1 = content.find("/view_video.php", start)
               if n1 < 0: break
               n2 = content.find('"', n1)
               n3 = content.find('title="', n2)
               if n3 < 0: break
               n4 = content.find('"', (n3+8))
               n5 = content.find(".jpg", n4)
               if n5 < 0: break
               n6 = content.rfind('"', 0, n5)
               url = "https://www.pornhub.com" + content[n1:n2]
               name = content[(n3+8):n4]
               pic = content[(n6+1):n5] + ".jpg"
               print "name =", name
               print "url =", url
               print "pic =", pic
               addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
               start = n5
               i = i+1
             xbmcplugin.endOfDirectory(thisPlugin)  

        elif "tubemania" in name1:
	     regexvideo = 'div class="video".*?<a href="(.*?)" title="(.*?)"><img src="(.*?)"'
	     match = re.compile(regexvideo,re.DOTALL).findall(content)
             print "match =", match
             for url, name, pic in match:
                 #https://tubemania.org/mov/3290775/
                 name = "tubemania-" + name.replace('"', '')
                 url = "https://tubemania.org" + url
                 pic = pic 
                 ##print "Here in getVideos url =", url
	         addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
             xbmcplugin.endOfDirectory(thisPlugin)	         

        elif "femdom" in name1:
 	       regexvideo = '<div class="img".*?<a href="(.*?)".*?ata-original="(.*?)" title="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for url, pic, name in match:
                 name = name1 + name.replace('&plus;', ' ')
                 name = name.replace("Page", "")
                 pic1 = pic 
                 url1 = url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "tranny.one" in name1:
 	       regexvideo = '<a class="textIndent" href="(.*?)".*?<img src="(.*?)".*?video-title"><span>(.*?)<'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for url, pic, name in match:
                 name = name1 + name.replace('&plus;', ' ')
                 name = name.replace("Page", "")
                 pic1 = pic 
                 url1 = url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

        elif "flashtranny" in name1:
 	       regexvideo = '<div class="b-thumb-item">.*?title="(.*?)".*?ref="(.*?)".*?<img src="(.*?)"'
	       match = re.compile(regexvideo,re.DOTALL).findall(content)
               print "match =", match
               for name, url, pic in match:
                 #http://www.flashtranny.com/gallery/162366-lascivious-curious-daddy-pounding-wicked-latin-sheboy-pretty-anal-gap
                 name = name1 + name.replace('&plus;', ' ')
                 name = name.replace("Page", "")
                 pic1 = pic 
                 url1 = "http://www.flashtranny.com" + url
                 print "Here in getVideos url1 =", url1
	         addDirectoryItem(name, {"name":name, "url":url1, "mode":3}, pic1)         
               xbmcplugin.endOfDirectory(thisPlugin)  

#mmmmmmmmmmmmmmmmmmmmmmmmmmmm

def playVideo(name, url):
   if "tubemania" in name:
           print "Here in playVideo url =", url
           vid = url.replace("https://tubemania.org/mov/", "")
           vid = vid.replace("/", "")
           url1 = "https://borfos.com/kt_player/player.php?id=" + vid
           fpage = getUrl(url1)
	   print "fpage C =", fpage
	   regexvideo = 'video_url.*?"(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
	   
           url = match[0]

           pic = "DefaultFolder.png"
           print "Here in playVideo url B=", url
           li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
           player = xbmc.Player()
           player.play(url, li)

   elif "femdom" in name:
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "fpage C =", fpage
	   regexvideo = "var filepath = '(.*?)'"
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
	   
           url = match[0]

           pic = "DefaultFolder.png"
           print "Here in playVideo url B=", url
           li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
           player = xbmc.Player()
           player.play(url, li)

   elif "tranny.one" in name:
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "fpage C =", fpage
	   regexvideo = '<video src="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
	   
           url = match[0]

           pic = "DefaultFolder.png"
           print "Here in playVideo url B=", url
           li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
           player = xbmc.Player()
           player.play(url, li)

   elif "flashtranny" in name:
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "fpage C =", fpage
	   regexvideo = 'source src="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
	   
           url = match[0].replace("&amp;", "&")

           pic = "DefaultFolder.png"
           print "Here in playVideo url B=", url
           li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
           player = xbmc.Player()
           player.play(url, li)





   else:
     print "In playVideo name =", name
     print "In playVideo url =", url
     name1, url1 = getVideo(name, url)
     print "In playVideo name1 =", name1
     print "In playVideo url1 =", url1
     pic = "DefaultFolder.png"
     li = xbmcgui.ListItem(name1,iconImage="DefaultFolder.png", thumbnailImage=pic)
     player = xbmc.Player()
     player.play(url1, li)



#nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn     

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
    print "parameters=", parameters
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        print "paramPairs=", paramPairs
        for paramsPair in paramPairs:
            print "paramsPair=", paramsPair
            paramSplits = paramsPair.split('=')
            print "paramSplits=", paramSplits
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    print "paramDict=", paramDict           
    return paramDict

params = parameters_string_to_dict(sys.argv[2])
name =  str(params.get("name", ""))
url =  str(params.get("url", ""))
print "url A=", url
url = urllib.unquote(url)
mode =  str(params.get("mode", ""))

print "name =", name
print "url =", url
if not sys.argv[2]:
	ok = showContent()
else:
        if mode == str(1):
                ok = search(name, url)
	elif mode == str(2):
		ok = getVideos(name, url)	
	elif mode == str(3):
		ok = playVideo(name, url)	



























