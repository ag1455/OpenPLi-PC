##########20171210###################
import os, sys
import urllib, re
from urlparse import urlparse
#from ast import literal_eval

import xbmc
import xbmcaddon

# some plugins seem to expect these to be preloaded
# sys is already preloaded by jumpy
import __builtin__
__builtin__.os = os
__builtin__.xbmc = xbmc

# xbmc/SortFileItem.h
SORT_METHOD_NONE = 0
SORT_METHOD_ALBUM = 13  
SORT_METHOD_ALBUM_IGNORE_THE = 14 
SORT_METHOD_ARTIST = 11 
SORT_METHOD_ARTIST_IGNORE_THE = 12 
SORT_METHOD_BITRATE = 39 
SORT_METHOD_CHANNEL = 38 
SORT_METHOD_COUNTRY = 16 
SORT_METHOD_DATE = 3 
SORT_METHOD_DATEADDED = 19 
SORT_METHOD_DATE_TAKEN = 40 
SORT_METHOD_DRIVE_TYPE = 6 
SORT_METHOD_DURATION = 8 
SORT_METHOD_EPISODE = 22 
SORT_METHOD_FILE = 5 
SORT_METHOD_FULLPATH = 32 
SORT_METHOD_GENRE = 15 
SORT_METHOD_LABEL = 1 
SORT_METHOD_LABEL_IGNORE_FOLDERS = 33 
SORT_METHOD_LABEL_IGNORE_THE = 2 
SORT_METHOD_LASTPLAYED = 34 
SORT_METHOD_LISTENERS = 36 
SORT_METHOD_MPAA_RATING = 28 
SORT_METHOD_NONE = 0 
SORT_METHOD_PLAYCOUNT = 35 
SORT_METHOD_PLAYLIST_ORDER = 21 
SORT_METHOD_PRODUCTIONCODE = 26 
SORT_METHOD_PROGRAM_COUNT = 20 
SORT_METHOD_SIZE = 4 
SORT_METHOD_SONG_RATING = 27 
SORT_METHOD_STUDIO = 30 
SORT_METHOD_STUDIO_IGNORE_THE = 31 
SORT_METHOD_TITLE = 9 
SORT_METHOD_TITLE_IGNORE_THE = 10 
SORT_METHOD_TRACKNUM = 7 
SORT_METHOD_UNSORTED = 37 
SORT_METHOD_VIDEO_RATING = 18 
SORT_METHOD_VIDEO_RUNTIME = 29 
SORT_METHOD_VIDEO_SORT_TITLE = 24 
SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE = 25 
SORT_METHOD_VIDEO_TITLE = 23 
SORT_METHOD_VIDEO_YEAR = 17 


SORT_ORDER_NONE = 0
SORT_ORDER_ASC = 1
SORT_ORDER_DESC = 2

SORT_NORMALLY = 0
SORT_ON_TOP = 1
SORT_ON_BOTTOM = 2

librtmp_checked = False
librtmp = False

#argv0 = sys.argv[0]

# added functions

def log(txt):
#        f = open("/usr/lib/enigma2/python/Plugins/Extensions/Porncenter/kodi_log.txt", "a")
        f = open("/tmp/kodi_log.txt", "a")
        f.write(txt)
        f.close()

def setargv(argv):
	pass

#setargv(sys.argv)

def using_librtmp():
	return None

def getMediaType(listitem):
	itemtype = listitem.getProperty('type').strip().upper()
#	pass#print 'mediatype=%s' % itemtype
	if itemtype == "VIDEO":
		return PMS_VIDEO
	elif itemtype == "AUDIO":
		return PMS_AUDIO
	else:
		return PMS_UNKNOWN

def fullPath(base, path):
#	pass#print 'fullPath %s' % [base, path]
	if path == None:
		return None
	if urlparse(path).scheme == "" and not os.path.isabs(path):
		url = urlparse(base)
		path = '%s://%s/%s' % (url.scheme, url.netloc, path) if url.scheme != ""  \
			else os.path.join(os.path.dirname(base), path)
	return xbmc.translatePath(path, False)

# see xbmc/guilib/GUITextLayout.cpp::ParseText

ltags = re.compile(r'\[/?(COLOR.*?|B|I)\]')

def striptags(label):
	global ltags
	if label is not None:
		return ltags.sub('', label)
	return label

def rtmpsplit(url, listitem):
	sargs = []
	args = []
	tups = re.findall(r' ([-\w]+)=(".*?"|\S+)', ' -r=' + url)
	# see xbmc/cores/dvdplayer/DVDInputStreams/DVDInputStreamRTMP.cpp:120
	for key,tag in [
			( "SWFPlayer", "swfUrl"),
			( "PageURL",   "pageUrl"),
			( "PlayPath",  "playpath"),
			( "TcUrl",     "tcUrl"),
			( "IsLive",    "live")
		]:
			try:
				tups.append((tag, listitem.getProperty(key)))
			except KeyError:
				pass
	swfVfy = True if url.lower().replace('=1', '=true').find(" swfvfy=true") > -1 else False
	opts = {
		'swfurl'    : '-W' if swfVfy else '-s',
		'playpath'  : '-y',
		'app'       : '-a',
		'pageurl'   : '-p',
		'tcurl'     : '-t',
		'subscribe' : '-d',
		'live'      : '-v',
		'playlist'  : '-Y',
		'socks'     : '-S',
		'flashver'  : '-f',
		'conn'      : '-C',
		'jtv'       : '-j',
		'token'     : '-T',
		'swfage'    : '-X',
		'start'     : '-A',
		'stop'      : '-B',
		'buffer'    : '-b',
		'timeout'   : '-m',
		'auth'      : '-u'
	}
	for key,val in tups:
		if val is None:
			continue
#		# convert some '\hh' hex escapes
#		val = val.replace('\\5c','\\').replace('\\20',' ') \
#			.replace('\\22','\\"' if sys.platform.startswith('win32') else '"')
		# convert all '\hh' hex escapes
##		val = literal_eval("'%s'" % val.replace('\\','\\x'))
                val = " "
		if sys.platform.startswith('win32'):
			val = val.replace('"', '\\"')
		if key.lower() in opts:
			key = opts[key.lower()]
		if val == '1' or val.lower() == 'true':
			if key.lower() != 'swfvfy':
				sargs.append(key)
		else:
			args.append((key, val))
	cmd = "rtmpdump " + ' '.join('%s "%s"' % arg for arg in args) + ' ' + ' '.join(sargs)
        if os.path.exists("/etc/debugxb"):
	       pass#print "test cmd: %s\n" %  cmd
	return (args, sargs)

def librtmpify(url, listitem):
	newurl = [url]
	# see xbmc/cores/dvdplayer/DVDInputStreams/DVDInputStreamRTMP.cpp:120
	for key,tag in [
			( "SWFPlayer", "swfUrl"),
			( "PageURL",   "pageUrl"),
			( "PlayPath",  "playpath"),
			( "TcUrl",     "tcUrl"),
			( "IsLive",    "live")
		]:
			try:
				val = listitem.getProperty(key)
				if val:
					newurl.append('%s=%s' % (tag, val))
			except KeyError:
				pass
	newurl = ' '.join(newurl)
        if os.path.exists("/etc/debugxb"):
	       pass#print 'test cmd: ffmpeg -y -i "%s" -target ntsc-dvd - \n' %  newurl
	return newurl

# native xbmc functions

def addDirectoryItem(handle, url, listitem, totalItems=40, isFolder=True):
       plug = xbmcaddon.getaddonpath_params("addon_id")
       if os.path.exists("/etc/debugxb"):
           try:
               pass#print "xbmcplugin addDirectoryItem plug =", plug
               pass#print "xbmcplugin addDirectoryItem url =", url
           except:
               pass   
       if "plugin://plugin.video.youtube" in url:
               plug = "plugin.video.youtube"
       if plug in url:
               print "xbmcplugin addDirectoryItem plug in url"
               url = "/usr/lib/enigma2/python/Plugins/Extensions/Porncenter/plugins/" + plug + "/default.py?" + url
       pass#print "xbmcplugin addDirectoryItem url B =", url
       url = url.replace("&", "AxNxD")
       url = url.replace("=", "ExQ")
       data = "&url=" + url

       if os.path.exists("/etc/debugxb"):
          try:
             pass#print "xbmcplugin addDirectoryItem data =", data
          except:
             pass   
       file = open("/tmp/data.txt", "a")
       data1 = getdata(listitem)
       pass#print "xbmcplugin addDirectoryItem data1 =", data1
       data = "&" + data1 + data
       data = data.replace("\n", "")
       data = data.replace("\r", "")
       data = data + "\n"
       print "xbmcplugin addDirectoryItem 1"
       print "xbmcplugin addDirectoryItem data B =", data

def getdata(listitem):
              pass#print "Here in getdata 1"
              dataA = listitem.data
              thumbnailImage = dataA['thumbnailImage']
              label = dataA['label']
              try:
                  if (label is None) or (label=="0") or (label=="") or (label==" "):
                     label = dataA['Title']
              except:       
                  pass  
              pass#print "Here in getdata label =", label
              path = dataA['path']
              label2 = dataA['label2']
              iconImage = dataA['iconImage']
              
              if label is None:
                      label = " "
              if thumbnailImage is None:
                      thumbnailImage = "DefaultFolder.png"
              if path is None:
                      path= " "
              if label2 is None:
                      label2 = " "
              if iconImage is None:
                      iconImage = " "

              if (".jpg" not in thumbnailImage) and (".png" not in thumbnailImage):
                      thumbnailImage = "DefaultFolder.png"
              
              if thumbnailImage is not None:
                      thumbnailImage = thumbnailImage.replace(" ", "%20")
                      thumbnailImage = thumbnailImage.replace("&", "AxNxD")
                      thumbnailImage = thumbnailImage.replace("=", "ExQ")
              if label is None:
                      label = label2        
              if label is not None:
                      label = label.replace(" ", "-")
                      label = label.replace("&", "AxNxD")
                      label = label.replace("=", "ExQ")
              if path is not None:
                      if '|' in path:
		              path,headers = path.split('|')
#                      path = path.replace(" ", "-")
                      path = path.replace("&", "AxNxD")
                      path = path.replace("=", "ExQ")
#              pass#print "path =", path
#              pass#print "label =", label
              i = 0
              col = ""
              while i < 4:
                     n1 = path.find("[COLOR", 0)
                     if n1 > -1:
                            n2 = path.find("]", n1)
                            col = path[n1:(n2+1)]
                            path = path.replace(col, "")
                            i = i+1
                     else:
                            i = i+1
                            continue 
              path = path.replace("[/COLOR]", "")
              path = path.replace("[B]", "")                
              path = path.replace("[/B]", "")
              path = path.replace(">", "")
                                                    
              i = 0
              col = ""
              while i < 4:
                     n1 = label.find("[COLOR", 0)
                     if n1 > -1:
                            n2 = label.find("]", n1)
                            col = label[n1:(n2+1)]
                            label = label.replace(col, "")
                            i = i+1
                     else:
                            i = i+1
                            continue 
              label = label.replace("[/COLOR]", "")
              label = label.replace("[B]", "")                
              label = label.replace("[/B]", "")
              label = label.replace(">", "") 
              label = label.replace("\n", "")               
#              pass#print "path B=", path
#              pass#print "label B=", label
#              if "plugin://" in path:
              path = path.replace("plugin://", "/usr/lib/enigma2/python/Plugins/Extensions/Porncenter/plugins/")
              path = path.replace("?", "default.py?")  
              if label is None:
                      label = "Video"                                          
              if (path != "path"):
                      data = "name=" + str(label) + "&url=" + str(path) + "&thumbnailImage=" + str(thumbnailImage) + "&iconlImage=" + str(iconImage)
              else:
                      data = "name=" + str(label) + "&thumbnailImage=" + str(thumbnailImage) + "&iconImage=" + str(iconImage)
              i = 0
              col = ""

              data = data.replace("[/COLOR]", "")
              data = data.replace("[B]", "")                
              data = data.replace("[/B]", "")
              data = data.replace("\n", "")
              if os.path.exists("/etc/debugxb"):
                  try:
                      pass#print "In xbmcgui Kodi data =", data
                      pass#print "<<<"
                  except:        
                      pass
#              file = open("/tmp/data.txt", "a")
#              file.write(data)
#              file.close()
#              self.data = data
              return data
              

def addDirectoryItems(handle, items, totalItems = 0):
    """
    Callback function to pass directory contents back to XBMC as a list.

    Returns a bool for successful completion.

    handle: integer - handle the plugin was started with.
    items: List - list of (url, listitem[, isFolder]) as a tuple to add.
    totalItems: integer - total number of items that will be passed. (used for progressbar)

    Note:
        Large lists benefit over using the standard addDirectoryItem().
        You may call this more than once to add items in chunks.

    Example:
        if not xbmcplugin.addDirectoryItems(int(sys.argv[1]), [(url, listitem, False,)]:
            raise
    """
    for url, listItem, isFolder in items:
        addDirectoryItem(handle, url, listItem, isFolder, totalItems)


def addDirectoryItemsX(handle, items, totalItems=40):
       """Callback function to pass directory contents back to XBMC as a list."""
#       plug = xbmcaddon.getaddonpath_params("addon_id")
       pass#print "xbmcplugin addDirectoryItems items A=", items
       pass#print "xbmcplugin addDirectoryItems totalItems=", totalItems
       f = open("/tmp/kodiplug.txt", "r")
       icount = 0
       for line in f.readlines(): 
               plug = line[:-1]
               if icount == 0:
                       break
       
       
       if os.path.exists("/etc/debugxb"):
           try:
               pass#print "xbmcplugin addDirectoryItem plug =", plug
               pass#print "xbmcplugin addDirectoryItems handle =", handle
               pass#print "xbmcplugin addDirectoryItems items =", items
               pass#print "xbmcplugin addDirectoryItems totalItems =", totalItems
           except:
               psss    
       file = open("/tmp/data.txt", "w")
       i = 0
       while i < totalItems:
               plug = xbmcaddon.getaddonpath_params("addon_id")
               pass#print "xbmcplugin addDirectoryItems plug =", plug
               url = items[i][0]
               url = url.replace("&", "AxNxD")
               url = url.replace("=", "ExQ")
               url = "/usr/lib/enigma2/python/Plugins/Extensions/Porncenter/plugins/" + plug + "/default.py?" + url
#               log("\nxbmcplugin addDirectoryItems url =%s" %url)
               pass#print "xbmcplugin addDirectoryItems url =", url
               name = items[i][1].getLabel()
               pass#print "xbmcplugin addDirectoryItems name =", name
               data = "&name=" + name + "&url=" + url + "\n"
               try:
                             print "xbmcplugin addDirectoryItems 1"
                             print "In xbmcplugin addDirectoryItems data B=", data
               except:        
                             pass
#               file.write(data)
#               listitem = items[i][1]
               i = i+1
#               addDirectoryItem(handle, url, listitem, totalItems=40, isFolder=True)        

       file.close()
       return True

def setResolvedUrl(handle, succeeded, listitem, stack=-1):
	   """Callback function to tell XBMC that the file plugin has been resolved to a url"""
	
           pass#print "Here in setResolvedUrl 1"
           dataA = listitem.data
           pass#print "Here in setResolvedUrl dataA =", dataA
           thumbnailImage = dataA['thumbnailImage']
           label = dataA['label']
           pass#print "Here in setResolvedUrl label =", label
           path = dataA['path']
           label2 = dataA['label2']
           iconImage = dataA['iconImage']




           url=dataA['path']
           pass#print "In setResolvedUrl url = ",url
           import xbmc
           player=xbmc.Player()
           player.play(url=url, listitem=listitem)
           pass#print "setResolvedUrl done"
           return	
	
 
def setResolvedUrlX(handle, succeeded, listitem, stack=-1):
	"""Callback function to tell XBMC that the file plugin has been resolved to a url"""
        if os.path.exists("/etc/debugxb"):
               pass#print "setResolvedUrl done"


def endOfDirectory(handle, succeeded=None, updateListing=None, cacheToDisc=None):
	"""Callback function to tell XBMC that the end of the directory listing in a virtualPythonFolder is reached."""
        if os.path.exists("/etc/debugxb"):
	       pass#print "*** endOfDirectory ***"

def addSortMethod(handle, sortMethod, label2Mask=None):
	"""Adds a sorting method for the media list."""
	pass

# some plugins e.g Nickolodeon call getSetting(handle, id) instead of getSetting(id)
def getSettingX(item1, item2):
             if item2 == "quality":
                    return "2"
             elif item2 == "preferedStreamType":
                    return "1"  
def getSetting(handle, settingID):
    """
    Returns the value of a setting as a string.

    handle: integer - handle the plugin was started with.
    settingID: string - id of the setting that the module needs to access.

    Example:
        apikey = xbmcplugin.getSetting(int(sys.argv[1]), 'apikey')
    """
    pluginId = sys.argv[0]
    return xbmcaddon.Addon(pluginId).getSetting(settingID)
    pass

def iPlayer(url):
       if os.path.exists("/etc/debugxb"):
              pass#print "xbmcplugin iPlayer url =", url
       
       url = url.replace("&", "AxNxD")
       url = url.replace("=", "ExQ")
       data = "&url=" + url + "\n"
       file = open("/tmp/data.txt", "a")
       file.write(data)
       file.close()


def setSetting(handle, id, value):
	"""Sets a plugin setting for the current running plugin."""
	pass

def setContent(handle, content):
	"""Sets the plugins content."""
	pass

def setPluginCategory(handle, category):
	"""Sets the plugins name for skins to display."""
	pass

def setPluginFanart(handle, image, color1=None, color2=None, color3=None):
	"""Sets the plugins fanart and color for skins to display."""
	pass

def setProperty(handle, key, value):
	"""Sets a container property for this plugin."""
	pass

# protocols:
#	ftp
#	ftps
#	dav
#	davs
#	http
#	https
#	rtp
#	udp
#	rtmp
#	rtsp

#	filereader
#	shout
#	mms
#	musicdb
#	videodb
#	zip
#	file
#	playlistmusic
#	playlistvideo
#	special
#	upnp
#	plugin
#	musicsearch
#	lastfm
#	rss
#	smb
#	daap
#	hdhomerun
#	sling
#	rtv
#	htsp
#	vtp
#	myth
#	sap
#	sources
#	stack
#	tuxbox
#	multipath
#	rar
#	script
#	addons































