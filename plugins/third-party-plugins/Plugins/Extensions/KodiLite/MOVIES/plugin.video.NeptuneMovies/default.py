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
       sys.argv[0] = sys.argv[0].replace('/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/MOVIES/', 'plugin://') 
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
import datetime

#import universalscrapers

thisPlugin = int(sys.argv[1])
addonId = "plugin.video.NeptuneMovies"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
if not path.exists(dataPath):
       cmd = "mkdir -p " + dataPath
       system(cmd)

SOURCES = ["Watch32", "Movie25org", "Putlockerhd", "Watchfrees", "Seriesonline8", "Thewatchseries", "Coolmoviezone", "Darewatch", "Watchstream"]
HOSTS = ["openload", "vidtodo", "streamango", "bestream", "vidzi", "streamcloud", "estream"]

year_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&year=%s,%s&sort=moviemeter,asc&count=40&start=1'
genre_link = 'http://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=%s&sort=moviemeter,asc&count=40&start=1'



THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"

def getUrl(url):
        pass#print "Here in getUrl url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def years():
        selfdatetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        year = (selfdatetime.strftime('%Y'))
        ylist = []
        for i in range(int(year)-0, 1900, -1): ylist.append({'name': str(i), 'url': year_link % (str(i), str(i)), 'image': 'years.png', 'action': 'movies'})
        pass#print "ylist = ", ylist
        return ylist
        
def genres():
        glist = []
        genres = [
            ('Action', 'action', True),
            ('Adventure', 'adventure', True),
            ('Animation', 'animation', True),
            ('Anime', 'anime', False),
            ('Biography', 'biography', True),
            ('Comedy', 'comedy', True),
            ('Crime', 'crime', True),
            ('Documentary', 'documentary', True),
            ('Drama', 'drama', True),
            ('Family', 'family', True),
            ('Fantasy', 'fantasy', True),
            ('History', 'history', True),
            ('Horror', 'horror', True),
            ('Music ', 'music', True),
            ('Musical', 'musical', True),
            ('Mystery', 'mystery', True),
            ('Romance', 'romance', True),
            ('Science Fiction', 'sci_fi', True),
            ('Sport', 'sport', True),
            ('Thriller', 'thriller', True),
            ('War', 'war', True),
            ('Western', 'western', True)
        ]
        for i in genres: glist.append(
            {
                'name': i[0],
                'url': genre_link % i[1]
            })

#        self.addDirectory(self.list)
        return glist

def showContent():
                name = "Genres"
                url = "http://www.imdb.com"
                pic = " "
                addDirectoryItem(name, {"name":name, "url":url, "mode":11}, pic)
                name = "Years"
                url = "http://www.imdb.com"
                pic = " "
                addDirectoryItem(name, {"name":name, "url":url, "mode":22}, pic)
                
                xbmcplugin.endOfDirectory(thisPlugin)
        

def showContent1():
                glist = genres()
                pic = " "
                for item in glist:
                         url = item['url']
                         name = item['name']
                         addDirectoryItem(name, {"name":name, "url":url, "mode":1}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)
        
	
def showContent2():
                ylist = years()
                pic = " "
                for item in ylist:
                         url = item['url']
                         name = item['name']
                         addDirectoryItem(name, {"name":name, "url":url, "mode":1}, pic)
                xbmcplugin.endOfDirectory(thisPlugin)


def getVideos1(name1, url):
	    content = getUrl(url)
	    pass#print "content 1 =", content
	    
	    regexvideo = 'lister-item mode-advanced.*?<a href="(.*?)".*?img alt="(.*?)".*?loadlate="(.*?)".*?data-tconst="(.*?)".*?lister-item-year text-muted unbold">(.*?)<'

	    match = re.compile(regexvideo,re.DOTALL).findall(content)
	    pass#print "In getVideos9 match =", match
	    for url, name, pic, imdb, year in match:
	          poster = pic
                  pass#print "Here in movies.py poster = ", poster
                  if '/nopicture/' in poster: poster = '0'
                  poster = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
                  pass#print "Here in movies.py poster 2= ", poster
#                  poster = client.replaceHTMLCodes(poster)
#                  pass#print "Here in movies.py poster 3= ", poster
                  poster = poster.encode('utf-8')
                  pass#print "Here in movies.py poster 4= ", poster
                  pic = poster



                  url1 = "https://www.imdb.com" + url
                  year = year.replace("(I)", "")
                  year = year.replace("(", "")
                  year = year.replace(")", "")
                  year = year.replace(" ", "")
                   
	          name1 = name.replace(" ", "+")
	          url = name1 + "___" + year + "___" + imdb + "___"
	          name2 = name + "(" + year + ")"
                  addDirectoryItem(name2, {"name":name2, "url":url, "mode":2}, pic)
            xbmcplugin.endOfDirectory(thisPlugin)

def getVideos2(name1, url):
#            sources = ["Putlocker", "Movie4uch", "Solarmovie", "Seriesonline", "Watchfree"]

            for name in SOURCES:
	          pic = " " 
                  addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
            xbmcplugin.endOfDirectory(thisPlugin)	 


hostDict  = ['example.com', 'teramixer.com', 'waaw.tv', 'hqq.watch', 'netu.tv', 'hqq.tv', 'flixtor.to', 'videoraj.ec', 'videoraj.eu', 'videoraj.sx', 'videoraj.ch', 'videoraj.com', 'videoraj.to', 'videoraj.co', 'videowood.tv', 'movdivx.com', 'divxme.com', 'streamflv.com', 'cloudy.ec', 'cloudy.eu', 'cloudy.sx', 'cloudy.ch', 'cloudy.com', 'openload.io', 'openload.co', 'oload.tv', 'oload.stream', 'amazon.com', 'everplay.watchpass.net', 'filepup.net', 'daclips.in', 'daclips.com', 'vimeo.com', 'toltsd-fel.tk', 'toltsd-fel.xyz', 'thevideobee.to', 'thevideo.me', 'tvad.me', 'uptobox.com', 'uptostream.com', 'nosvideo.com', 'noslocker.com', 'lolzor.com', 'mycollection.net', 'adhqmedia.com', 'gagomatic.com', 'funblr.com', 'favour.me', 'vidbaba.com', 'likeafool.com', 'googlevideo.com', 'googleusercontent.com', 'get.google.com', 'plus.google.com', 'googledrive.com', 'drive.google.com', 'docs.google.com', 'youtube.googleapis.com', 'movshare.net', 'wholecloud.net', 'vidgg.to', 'cloud.mail.ru', 'kingvid.tv', 'vidup.me', 'watchers.to', 'datemule.co', 'datemule.com', 'grifthost.com', 'vivo.sx', 'tvlogy.to', 'anyfiles.pl', 'streamable.com', 'rutube.ru', 'indavideo.hu', 'gorillavid.in', 'gorillavid.com', 'fastplay.sx', 'fastplay.cc', 'fastplay.to', 'vidics.tv', 'stream.moe', 'videoget.me', 'dailymotion.com', 'bitvid.sx', 'videoweed.es', 'videoweed.com', 'watchonline.to', 'novamov.com', 'auroravid.to', 'vidzella.me', 'dl.vidzella.me', 'facebook.com', 'byzoo.org', 'playpanda.net', 'videozoo.me', 'videowing.me', 'easyvideo.me', 'play44.net', 'playbb.me', 'video44.net', 'upload.af', 'upload.mn', 'adultswim.com', 'streamplay.to', 'streamplay.club', 'fileweed.net', 'mersalaayitten.com', 'mersalaayitten.co', 'mersalaayitten.us', 'ok.ru', 'odnoklassniki.ru', 'speedvid.net', 'videohut.to', 'uploadx.link', 'uploadx.org', 'uploadz.org', 'uploadz.co', 'clicknupload.com', 'clicknupload.me', 'clicknupload.link', 'clicknupload.org', 'mp4stream.com', 'tune.pk', 'tune.video', 'vk.com', 'trollvid.net', 'trollvid.io', 'mp4edge.com', 'mail.ru', 'my.mail.ru', 'm.my.mail.ru', 'videoapi.my.mail.ru', 'api.video.mail.ru', 'vidmad.net', 'tamildrive.com', 'oneload.co', 'oneload.com', 'apnasave.club', 'videa.hu', 'videakid.hu', 'vidlox.tv', 'powvideo.net', 'streamin.to', 'flashx.tv', 'flashx.to', 'streamcloud.eu', 'vid.me', 'veoh.com', 'vidstore.me', 'videohost2.com', 'trt.pl', 'vidzi.tv', 'cda.pl', 'www.cda.pl', 'ebd.cda.pl', 'videos.sapo.pt', 'myvi.ru', 'thevid.net', 'yourupload.com', 'yucache.net', 'vodlock.co', 'anime-portal.org', 'goflicker.com', 'movpod.net', 'movpod.in', 'embed8.ocloud.stream', 'ocloud.stream', 'earnvideos.com', 'ecostream.tv', 'mehlizmovies.com', 'vidtodo.com', 'gamovideo.com', 'tubitv.com', 'hugefiles.net', 'hdvid.tv', 'ustream.tv', 'xvidstage.com', 'faststream.ws', 'kingfiles.net', 'tudou.com', 'vshare.eu', 'playwire.com', 'streamango.com', 'streamcherry.com', 'castamp.com', 'promptfile.com', 'syfy.com', 'vidabc.com', 'blazefile.co', 'usersfiles.com', 'mystream.la', 'stagevu.com', 'playhd.video', 'playhd.fo', 'aliez.me', 'vidbom.com', 'speedvideo.net', 'playedto.me', 'myvidstream.net', 'speedplay.xyz', 'speedplay.us', 'speedplay1.site', 'speedplay.pw', 'speedplay1.pw', 'speedplay3.pw', 'speedplayy.site', 'streame.net', 'thevideos.tv', 'weshare.me', 'nowvideo.eu', 'nowvideo.ch', 'nowvideo.sx', 'nowvideo.co', 'nowvideo.li', 'nowvideo.fo', 'nowvideo.at', 'nowvideo.ec', 'divxstage.eu', 'divxstage.net', 'divxstage.to', 'cloudtime.to', 'mycloud.to', 'mcloud.to', 'watchvideo.us', 'watchvideo2.us', 'watchvideo3.us', 'watchvideo4.us', 'watchvideo5.us', 'watchvideo6.us', 'watchvideo7.us', 'watchvideo8.us', 'watchvideo9.us', 'watchvideo10.us', 'watchvideo11.us', 'watchvideo12.us', 'watchvideo13.us', 'watchvideo14.us', 'watchvideo15.us', 'watchvideo16.us', 'watchvideo17.us', 'watchvideo18.us', 'watchvideo19.us', 'watchvideo20.us', 'watchvideo21.us', 'bestream.tv', 'vidwatch3.me', 'vidwatch.me', 'vidfile.net', 'jetload.tv', 'vidhos.com', 'rapidvideo.ws', 'putload.tv', 'shitmovie.com', 'filez.tv', 'tusfiles.net', 'dbmovies.xyz', 'ani-stream.com', 'mp4engine.com', 'megamp4.net', 'megamp4.us', 'h265.se', 'vidstreaming.io', 'vidup.org', 'mp4upload.com', 'spruto.tv', '9xplay.net', 'estream.to', 'vshare.io', 'vidto.me', 'speedwatch.us', 'downace.com', 'vidcrazy.net', 'uploadcrazy.net', 'rapidvideo.com', 'raptu.com', 'goodvideohost.com', 'vidoza.net', 'entervideo.net', 'videocloud.co', 'zstream.to', 'userscloud.com', 'clipwatching.com']
hostprDict  = ['1fichier.com', 'oboom.com', 'rapidgator.net', 'rg.to', 'uploaded.net', 'uploaded.to', 'ul.to', 'filefactory.com', 'nitroflare.com', 'turbobit.net', 'uploadrocket.net']


#import resources
def findUrl(s, imdb, title, localtitle, aliases, year):
#             from resources.lib.sources.en.putlocker import source
#             s = source()
             url = s.movie(imdb, title, localtitle, aliases, year)
             pass#print "Here in findUrl url =", url
             return url
             
def getVideos3(name1, url):
            pass#print "Here in getVideos3 name1 =", name1
            pass#print "Here in getVideos3 url =", url
            items = url.split("___")
            title = items[0]
            year = items[1]
            imdb = items[2]
#Here in getVideos3 year = %282017%29
#Here in getVideos3 title = Baby%24Driver
            year = year.replace("%28", "")
            year = year.replace("%29", "")
            title = title.replace("+", " ")
            
            pass#print "Here in getVideos3 year =", year
            pass#print "Here in getVideos3 title =", title
            pass#print "Here in getVideos3 imdb =", imdb
            localtitle = title
            aliases= []
            if "Putlockerhd" in name1:
                       from universalscrapers.scraperplugins.putlockerhd import putlockerhd
                       s = putlockerhd()
                       sources = s.scrape_movie(title, year, imdb, debrid = False)
                       pass#print "Here in getVideos3 Putlockerhd sources =", sources

            #watch32
            elif "Watch32" in name1:
                       from universalscrapers.scraperplugins.watch32 import watch32
                       s = watch32()
                       sources = s.scrape_movie(title, year, imdb, debrid = False)
                       pass#print "Here in getVideos3 watch32 sources =", sources
            #Movie25org
            elif "Movie25org" in name1:
                       from universalscrapers.scraperplugins.movie25org import movie25org
                       s = movie25org()
                       sources = s.scrape_movie(title, year, imdb, debrid = False)
                       pass#print "Here in getVideos3 watch32 sources =", sources
            #watchfrees   
            elif "Watchfrees" in name1:
                       from universalscrapers.scraperplugins.watchfrees import watchfrees
                       s = watchfrees()
                       sources = s.scrape_movie(title, year, imdb, debrid = False)
                       pass#print "Here in getVideos3 watchfrees sources =", sources
            #seriesonline8  
            elif "Seriesonline8" in name1:
                       from universalscrapers.scraperplugins.seriesonline8 import seriesonline8
                       s = seriesonline8()
                       sources = s.scrape_movie(title, year, imdb, debrid = False)
                       pass#print "Here in getVideos3 watch32 sources =", sources     
            #Darewatch
            elif "Darewatch" in name1:
                       from universalscrapers.scraperplugins.darewatch import darewatch
                       s = darewatch()
                       sources = s.scrape_movie(title, year, imdb, debrid = False)
                       pass#print "Here in getVideos3 watch32 sources =", sources     

            elif "Thewatchseries" in name1:
                       from universalscrapers.scraperplugins.thewatchseries import thewatchseries
                       s = thewatchseries()
                       sources = s.scrape_movie(title, year, imdb, debrid = False)
                       pass#print "Here in getVideos3 watch32 sources =", sources     
            #coolmoviezone           
            elif "Coolmoviezone" in name1:
                       from universalscrapers.scraperplugins.coolmoviezone import coolmoviezone
                       s = coolmoviezone()
                       sources = s.scrape_movie(title, year, imdb, debrid = False)
                       pass#print "Here in getVideos3 watch32 sources =", sources     
            #watchstream           
            elif "Watchstream" in name1:
                       from universalscrapers.scraperplugins.watchstream import watchstream
                       s = watchstream()
                       sources = s.scrape_movie(title, year, imdb, debrid = False)
                       pass#print "Here in getVideos3 watch32 sources =", sources     
                        
            elif "Divxcrawler" in name1:
                       from resources.lib.sources.en.divxcrawler import source
                       s = source()

                       sources = s.sources(findUrl(s, imdb, title, localtitle, aliases, year), hostDict, hostprDict)
                       pass#print "Here in getVideos3 Divxcrawler sources =", sources
            elif "Solarmovie" in name1:
                       from resources.lib.sources.en.solarmovie import source
                       s = source()

                       sources = s.sources(findUrl(s, imdb, title, localtitle, aliases, year), hostDict, hostprDict)
                       pass#print "Here in getVideos3 sources =", sources
            elif "Cmovies" in name1:
                       from resources.lib.sources.en.cmovies import source
                       s = source()

                       sources = s.sources(findUrl(s, imdb, title, localtitle, aliases, year), hostDict, hostprDict)
                       pass#print "Here in getVideos3 sources =", sources
            elif "Seriesonline" in name1:
                       from resources.lib.sources.en.seriesonline import source
                       s = source()

                       sources = s.sources(findUrl(s, imdb, title, localtitle, aliases, year), hostDict, hostprDict)
                       pass#print "Here in getVideos3 sources =", sources
            elif "Showbox" in name1:
                       from resources.lib.sources.en.showbox import source
                       s = source()

                       sources = s.sources(findUrl(s, imdb, title, localtitle, aliases, year), hostDict, hostprDict)
                       pass#print "Here in getVideos3 sources =", sources
            elif "Vodly" in name1:
                       from resources.lib.sources.en.vodly import source
                       s = source()

                       sources = s.sources(findUrl(s, imdb, title, localtitle, aliases, year), hostDict, hostprDict)
                       pass#print "Here in getVideos3 sources =", sources
                      
                      
                      
            for source in sources:
                         url = source['url']
                         
##                         url = s.resolve(url1)
                         pass#print "Here in getVideos3 url 3=", url
                         
                         
                         name = title + "_" + source['source']
                         if (not "googlelink" in name.lower()) and (not "dl" in name.lower()) and (not "cdn" in name.lower()) and(not "openload" in name.lower()) and (not "vidtodo" in name.lower()) and (not "streamango" in name.lower()) and (not "bestream" in name.lower()) and (not "vidzi" in name.lower()) and (not "streamcloud" in name.lower()):
                                continue
                         quality = source['quality']
                         name2 = name + "_" + quality
                         pic = " "
                         addDirectoryItem(name2, {"name":name2, "url":url, "mode":4}, pic)
            xbmcplugin.endOfDirectory(thisPlugin)
            
        
def playVideo(name, url):
           pass#print "Here in playVideo url =", url
           if ("googlelink" in name.lower()) or ("dl" in name.lower()) or ("cdn" in name.lower()) or ("gvideo" in name.lower()):
                    url = url
           else:      
#                    import resolveurl 
                    from resolveurl import HostedMediaFile 
#                    url = resolveurl.HostedMediaFile(url=url).resolve()
                    url = HostedMediaFile(url=url).resolve()
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
pic =  str(params.get("pic", ""))

if not sys.argv[2]:
	ok = showContent()
else:
        if mode == str(11):
                showContent1()
        elif mode == str(22):
                showContent2()

        elif mode == str(1):
		ok = getVideos1(name, url)
        elif mode == str(2):
		ok = getVideos2(name, url)	
                	
	elif mode == str(3):
		ok = getVideos3(name, url)	
	elif mode == str(4):
		ok = playVideo(name, url)	























































































