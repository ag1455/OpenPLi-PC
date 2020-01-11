
'''
Created on 9/05/2014

@author: pybquillast

This module has been ported from xbmcstubs:

__author__ = 'Team XBMC <http://xbmc.org>'
__credits__ = 'Team XBMC'
__date__ = 'Thu Apr 17 08:03:38 BST 2014'
__platform__ = 'ALL'
__version__ = '2.14.0'


'''
__version__ = '2.25.0'

import os.path, traceback
from os import system
from urlparse import urlparse
from cStringIO import StringIO

import xbmcaddon, xbmcplugin, xbmcgui
import sys
##########20171111############################
pass#pass#print "Here in xbmc-py"
# xbmc/PlayListPlayer.h
PLAYLIST_NONE = -1
PLAYLIST_MUSIC = 0
PLAYLIST_VIDEO = 1
PLAYLIST_PICTURE = 2

# xbmc/cores/playercorefactory/PlayerCoreFactory.h
PLAYER_CORE_AUTO = 0 # EPC_NONE
PLAYER_CORE_DVDPLAYER = 1 # EPC_DVDPLAYER
PLAYER_CORE_MPLAYER = 2 # EPC_MPLAYER
PLAYER_CORE_PAPLAYER = 3 # EPC_PAPLAYER

# xbmc/storage/IoSupport.h
TRAY_OPEN = 16
DRIVE_NOT_READY = 1
TRAY_CLOSED_NO_MEDIA = 64
TRAY_CLOSED_MEDIA_PRESENT = 96

# xbmc/utils/log.h
LOGDEBUG = 0
LOGINFO = 1
LOGNOTICE = 2
LOGWARNING = 3
LOGERROR = 4
LOGSEVERE = 5
LOGFATAL = 6
LOGNONE = 7

# xbmc/cores/VideoRenderers/RenderCapture.h
CAPTURE_STATE_WORKING = 0 # CAPTURESTATE_WORKING
CAPTURE_STATE_DONE = 3 # CAPTURESTATE_DONE
CAPTURE_STATE_FAILED = 4 # CAPTURESTATE_FAILED
CAPTURE_FLAG_CONTINUOUS = 1 # CAPTUREFLAG_CONTINUOUS
CAPTURE_FLAG_IMMEDIATELY = 2 # CAPTUREFLAG_IMMEDIATELY

SERVER_AIRPLAYSERVER = 2
SERVER_EVENTSERVER = 6
SERVER_JSONRPCSERVER = 3
SERVER_UPNPRENDERER = 4
SERVER_UPNPSERVER = 5
SERVER_WEBSERVER = 1
SERVER_ZEROCONF = 7

abortRequested = False

xbmclog_file="/tmp/e.log"
def write_log(msg):
    if os.path.exists( xbmclog_file):
       afile=open(xbmclog_file,"a")
    else:
       afile=open(xbmclog_file,"w")
    afile.write("\n"+msg)
       
def log(msg, level=None):
	"""Write a string to XBMC's log file."""
        write_log(msg)
        pass#pass#print msg
	if os.path.exists("/etc/debugxb"):
	       pass#pass#print "Here in xmbc.py log =", msg
	pass       

output = log # alias for backward compatility

def shutdown():
	"""Shutdown the xbox."""
	pass

def restart():
	"""Restart the xbox."""
	pass

def executescript(script):
	"""Execute a python script."""
	runScript(script)

def executebuiltinX(function):
	"""Execute a built in XBMC function."""
#	pass#print "**** executebuiltin ****",function
        pass

#plugin://plugin.video.covenant/?action=moviePage&url=http%3A%2F%2Fapi.trakt.tv%2Fsearch%2Fmovie%3Flimit%3D20%26page%3D1%26query%3Dwonder%2Bwoman
def executebuiltin(function):
    """Execute a built in XBMC function."""
    pass#print "**** executebuiltin ****",function
    if not "Container.Update" in function:
        pass
    else:    
        n1 = function.find("(", 0)
        n2 = function.find(")", n1)
        url = function[(n1+1):n2]
        n3 = url.find("?", 0)
        arg3 = url[n3:]
        arg1 = sys.argv[0].replace("plugin://","/usr/lib/enigma2/python/Plugins/Extensions/Porncenter/plugins/") + "default.py"
        arg2 = sys.argv[1]  
        cmd = "python " + arg1 + " " + arg2 + " '" + arg3 + "' &"
        pass#print "In xbmc.py cmd =", cmd 
        os.system(cmd)
        
def executehttpapi(httpcommand):
	"""Execute an HTTP API command."""
	return ""

def executeJSONRPC(jsonrpccommand):
	"""Execute an JSONRPC command."""
	return '{"error":{"code":-32602,"message":"Invalid params."},"id":1,"jsonrpc":"2.0"}'
#	return ""

#def sleep(time):
#	"""Sleeps for 'time' msec."""
#	system("sleep 0")
def sleep(ctime):
	"""Sleeps for 'time' msec."""
        import time
        print "Going to sleep 2 time =", ctime/1000
#        time.sleep(ctime/1000) ##time passed by milliseconds 
	

def getLocalizedString(id):
	"""Returns a localized 'unicode string'."""
	return u""

def getSkinDir():
	"""Returns the active skin directory as a string."""
	return ""

def getLanguage():
	"""Returns the active language as a string."""
	return _settings['xbmc']['language']

def getIPAddress():
	"""Returns the current ip address as a string."""
	return ""

def getDVDState():
	"""Returns the dvd state as an integer."""
	return 0

def getFreeMem():
	"""Returns the amount of free memory in MB as an integer."""
	return 0

def getCpuTemp():
	"""Returns the current cpu temperature as an integer."""
	return 0

# xbmc/GUIInfoManager.cpp
def getInfoLabel(infotag):
	"""Returns an InfoLabel as a string."""
	if infotag == 'System.BuildVersion':
		return "12.0"
	# string/number
	return ""

def getInfoImage(infotag):
	"""Returns a filename including path to the InfoImage's"""
	return ""

def playSFX(filename):
	"""Plays a wav file by filename"""
	pass

def enableNavSounds(yesNo):
	"""Enables/Disables nav sounds"""
	pass

def getCondVisibility(condition):
	"""Returns True (1) or False (0) as a bool."""
	return False;

def getGlobalIdleTime():
	"""Returns the elapsed idle time in seconds as an integer."""
	return 0

def getCacheThumbName(path):
	"""Returns a thumb cache filename."""
	return ""

def makeLegalFilename(filename, fatX=None):
	"""Returns a legal filename or path as a string."""
	return filename

#def translatePath(text):
#        pass#print "translatePath text =", text
#        pass
#xbmc.translatePath(os.path.join('special://home/addons/plugin.video.itv', 'lib'))
def translatePath(url, asURL=False):
	"""Returns the translated path."""
	pass#print "In xbmc url A=", url
	xurl = url
        pass#print "translatePath xurl 0 =", xurl
        try:
            myfile = file(r"/etc/xbmc.txt")       
            icount = 0
            for line in myfile.readlines():
                 cachefold = line
        except:
            cachefold = "/media/hdd"        
               
        if "special://home/addons/" in url:
            url = url.replace("special://home/addons/", "/usr/lib/enigma2/python/Plugins/Extensions/Porncenter/plugins/")
            pass#print "In xbmc url B=", url
            return url
        
        if "special://" in url:
               pass#print "translatePath url =", url
               n1 = url.find("//", 0)
#               n2 = len(url)
#               n3 = url.rfind("/", 0, n2)
               xurl = cachefold + "/xbmc" + url[(n1+1):]
               pass#print "translatePath xurl =", xurl
#        if not xurl.endswith("/"):
        n2 = len(xurl)
        n3 = xurl.rfind("/", 0, n2)
        xpath = xurl[:n3]
        pass#print "translatePath xpath =", xpath
        cmd = "mkdir -p " + xpath
        system(cmd)
        return xurl

def getCleanMovieTitle(path, usefoldername=None):
	"""Returns a clean movie title and year string if available."""
	return ""


#play_m3u8 = xbmc.validatePath(xbmc.translatePath('special://home')+'/userdata/addon_data/plugin.video.laola1live/play.m3u8')

def validatePath(path):
	"""Returns the validated path."""
#	return path
        pass#print "In validatePath path =", path
        return path


        

def getRegion(id):
	"""Returns your regions setting as a string for the specified id."""
	return "%I:%M %p"

def getSupportedMedia(media):
	"""Returns the supported file types for the specific media as a string."""
	return ""

def skinHasImage(image):
	"""Returns True if the image file exists in the skin."""
	return False;

def subHashAndFileSize(file):
	"""Calculate subtitle hash and size."""
	return ("0", "0")

# xbmc/interfaces/python/xbmcmodule/player.cpp
pass#pass#print "Here in xbmc-py B"
###mfaraj-start
class Keyboard:##activate the object to read the search term-mfaraj
    def __init__(self, default=None, heading=None, hidden=False):

        """Creates a new Keyboard object with default text heading and hidden input flag if supplied.

        default: string - default text entry.
        heading: string - keyboard heading.
        hidden: boolean - True for hidden text entry.

        Example:
            kb = xbmc.Keyboard('default', 'heading', True)
            kb.setDefault('password') # optional
            kb.setHeading('Enter password') # optional
            kb.setHiddenInput(True) # optional
            kb.doModal()
            if (kb.isConfirmed()):
                text = kb.getText()
        """
        pass#pass#print "In xbmc-py default =", default
#        pass

    def doModal(self, autoclose=0):
        """Show keyboard and wait for user action.

        autoclose: integer - milliseconds to autoclose dialog.

        Note:
            autoclose = 0 - This disables autoclose

        Example:
            kb.doModal(30000)
        """
        pass

    def setDefault(self, default):
        """Set the default text entry.

        default: string - default text entry.

        Example:
            kb.setDefault('password')
        """
        pass

    def setHiddenInput(self, hidden):
        """Allows hidden text entry.

        hidden: boolean - True for hidden text entry.

        Example:
            kb.setHiddenInput(True)
        """
        pass

    def setHeading(self, heading):
        """Set the keyboard heading.

        heading: string - keyboard heading.

        Example:
            kb.setHeading('Enter password')
        """
        pass

    def getText(self):
        """Returns the user input as a string.

        Note:
            This will always return the text entry even if you cancel the keyboard.
            Use the isConfirmed() method to check if user cancelled the keyboard.
        """
        ###mfaraj-start
        import os
        if os.path.exists('/tmp/xbmc_search.txt'): 
           file=open('/tmp/xbmc_search.txt',"r")
           str=file.read()
           file.close()
        else:
           str=None   
        ###mfaraj-end
        pass#pass#print "In xbmc-py str =", str
        return str

    def isConfirmed(self):
        """Returns False if the user cancelled the input."""
        return True

###mfaraj-end

class Player:

        def __init__(self, core=None):
		"""Creates a new Player with as default the xbmc music playlist."""
		self.playlist = None
		self.playing = True;

        #dataA = listitem.data
        def play(self, url=None, listitem=None, playlist=None, windowed=None):
#           url = item
           name = "video"
           url = str(url)
           print "xmbc url =", url
           if listitem is not None:
              dataA = listitem.data
              name = dataA['label'] 
           if (name == 'None') or (name is None) or (name == ""):
              name = "video"  
           try:
              print "xmbc url 2=", url
              url = url.replace("&", "AxNxD")
              print "xmbc url 3=", url
              url = url.replace("=", "ExQ")
              print "xmbc url 4=", url
              data = "&url=" + url + "&name=" + name + "\n"
              print "xmbc url 5=", url
#              if os.path.exists("/etc/debugxb"):
              print "xmbc data B=", data
              print "xmbc url 6=", url

           except:
              url = url.items[0].getfilename()  
              url = url.replace("&", "AxNxD")
              url = url.replace("=", "ExQ")
              data = "&url=" + url + "&name=" + name + "\n"
#              if os.path.exists("/etc/debugxb"):
              print "xmbc data B=", data
#              file = open("//tmp/data.txt", "a")
#              if "plugin:/" not in data:
#                     file.write(data)
 #             file.close()
	def stop(self):
		"""Stop playing."""
		pass

	def pause(self):
		"""Pause playing."""
		pass

	def playnext(self):
		"""Play next item in playlist."""
		pass

	def playprevious(self):
		"""Play previous item in playlist."""
		pass

	def playselected(self):
		"""Play a certain item from the current playlist."""
		pass

	def onPlayBackStarted(self):
		"""onPlayBackStarted method."""
		pass

	def onPlayBackEnded(self):
		"""onPlayBackEnded method."""
		pass

	def onPlayBackStopped(self):
		"""onPlayBackStopped method."""
		pass

	def onPlayBackPaused(self):
		"""onPlayBackPaused method."""
		pass

	def onPlayBackResumed(self):
		"""onPlayBackResumed method."""
		pass

	def isPlaying(self):
		"""returns True is xbmc is playing a file."""
		return self.playing

	def isPlayingAudio(self):
		"""returns True is xbmc is playing an audio file."""
		return True

	def isPlayingVideo(self):
		"""returns True if xbmc is playing a video."""
		return False

	def getPlayingFile(self):
		"""returns the current playing file as a string."""
		pass

	def getVideoInfoTag(self):
		"""returns the VideoInfoTag of the current playing Movie."""
		pass

	def getMusicInfoTag(self):
		"""returns the MusicInfoTag of the current playing 'Song'."""
		pass

	def getTotalTime(self):
		"""Returns the total time of the current playing media in"""
		return 0

	def getTime(self):
		"""Returns the current time of the current playing media as fractional seconds."""
		# pretend to have played for 1 second
		if self.playing:
			self.playing = False
			return 1
		else:
			self.playing = True
			raise Exception("fake playback ended!")

	def seekTime(self):
		"""Seeks the specified amount of time as fractional seconds."""
		pass

	def setSubtitles(self, path):
		"""set subtitle file and enable subtitles"""
		pms.setSubtitles(path)

	def getSubtitles(self):
		"""get subtitle stream name."""
		pass

	def showSubtitles(self, visible):
		"""enable/disable subtitles"""
		pass

	def DisableSubtitles(self):
		"""disable subtitles."""
		pass

	def getAvailableAudioStreams(self):
		"""get Audio stream names."""
		pass

	def setAudioStream(self, stream):
		"""set Audio Stream."""
		pass

	def getAvailableSubtitleStreams(self):
		"""get Subtitle stream names."""
		pass

	def setSubtitleStream(self, stream):
		"""set Subtitle Stream."""
		pass

# xbmc/interfaces/python/xbmcmodule/playlist.cpp
class PlayListItem(xbmcgui.ListItem):

	def __init__(self, url=None, listitem=None):
		"""Creates a new PlaylistItem which can be added to a PlayList."""
		xbmcgui.ListItem.__init__(self)
		if listitem is not None:
			self.__dict__.update(listitem.__dict__)
		# url is sometimes 'False'
#                pass#print "Here in xbmc-py PlayListItem url =", url
		if url is not None and url:
			self.__dict__['path'] = url

	def getdescription(self):
		"""Returns the description of this PlayListItem."""
		return getLabel()

	def getduration(self):
		"""Returns the duration of this PlayListItem."""
		return 0

	def getfilename(self):
		"""Returns the filename of this PlayListItem."""
		return self.__dict__['path']

class PlayList:

	def __init__(self, type):
		self.items = []
		self.type = type

	def PlayList(self, playlist):
		"""retrieve a reference from a valid xbmc playlist."""
		pass

        def add(self, url, listitem=None, index=None):
		"""Adds a new file to the playlist."""
#		pass#print "**** PlayList.add ****", url, '' if listitem is None else listitem.__dict__
		player = Player()
		player.play(url)



	def addXX(self, url, listitem=None, index=None):
		"""Adds a new file to the playlist."""
#		pass#print "**** PlayList.add ****", url, '' if listitem is None else listitem.__dict__
		if not isinstance(url, list):
			url = [url]
		for u in url:
#                        pass#print "Here in xbmc-py u =", u
			item = PlayListItem(u, listitem)
#			pass#print "Here in xbmc-py item =", item
			if index is not None:
				self.items.insert(index, item)
				index += 1
			else:
				self.items.append(PlayListItem(u, item))
			xbmcplugin.setResolvedUrl(0, True, item)
#                pass#print "Here in xbmc-py self.items[0].getfilename() =", self.items[0].getfilename()

        def addX(self, url, listitem=None, index=None):
		"""Adds a new file to the playlist."""
#		pass#print "**** PlayList.add ****", url, '' if listitem is None else listitem.__dict__
		if not isinstance(url, list):
			url = [url]
		for u in url:
#                        pass#print "Here in xbmc-py u =", u
                        u = u.replace("&", "AxNxD")
                        u = u.replace("=", "ExQ")
#                        data = "&url=" + u + "\n"
                        data = "url=" + u + "\n"
                        if os.path.exists("/etc/debugxb"):
                               pass#pass#print "xmbc data B=", data
                        file = open("/tmp/data.txt", "a")
                        file.write(data)
                        file.close()

	def load(self, filename):
		"""Load a playlist."""
		pass

	def remove(self, filename):
		"""remove an item with this filename from the playlist."""
#		pass#print "**** PlayList.remove ****"
		self.items.remove(filename)

	def clear(self):
		"""clear all items in the playlist."""
		self.items = []

	def shuffle(self):
		"""shuffle the playlist."""
		pass

	def unshuffle(self):
		"""unshuffle the playlist."""
		pass

	def size(self):
		"""returns the total number of PlayListItems in this playlist."""
		return len(self.items)

	def getposition(self):
		"""returns the position of the current song in this playlist."""
		pass


# mock everything else

#from xbmcinit import mock

InfoTagMusic = None
InfoTagVideo = None
####Keyboard = None
Monitor = None

RenderCapture = None



# xbmc/interfaces/Builtins.cpp
# http://wiki.xbmc.org/index.php?title=List_of_Built_In_Functions

def PlayMedia(media, isdir=False, preview=1, playoffset=0):
	"""Play the specified media file (or playlist)"""
	#TODO: implement this properly
	Player().play(media)

def RunScript(script, *args):
	"""Run the specified script"""
	cmd = [translatePath(script)]
	cmd.extend(args)
	cmd.append('&')
	pms.run(cmd)

#def StopScript(*args):
#	"""Stop the script by ID or path, if running"""
#	pass

##if defined(TARGET_DARWIN)
#def RunAppleScript(*args):
#	"""Run the specified AppleScript command"""
#	pass
##endif

#def RunPlugin(*args):
#	"""Run the specified plugin"""
#	pass

#def RunAddon(*args):
#	"""Run the specified plugin/script"""
#	pass

#def Extract(*args):
#	"""Extracts the specified archive"""
#	pass


#def System_Exec(*args):
#	"""Execute shell commands"""
#	pass

#def System_ExecWait(*args):
#	"""Execute shell commands and freezes XBMC until shell is closed"""
#	pass

#System = mock()
#System.Exec = System_Exec
#System.ExecWait = System_ExecWait

#def Help():
#	"""This help message"""
#	pass

#def Reboot():
#	"""Reboot the system"""
#	pass

#def Restart():
#	"""Restart the system (same as reboot)"""
#	pass

#def ShutDown():
#	"""Shutdown the system"""
#	pass

#def Powerdown():
#	"""Powerdown system"""
#	pass

#def Quit():
#	"""Quit XBMC"""
#	pass

#def Hibernate():
#	"""Hibernates the system"""
#	pass

#def Suspend():
#	"""Suspends the system"""
#	pass

#def InhibitIdleShutdown():
#	"""Inhibit idle shutdown"""
#	pass

#def AllowIdleShutdown():
#	"""Allow idle shutdown"""
#	pass

#def RestartApp():
#	"""Restart XBMC"""
#	pass

#def Minimize():
#	"""Minimize XBMC"""
#	pass

#def Reset():
#	"""Reset the system (same as reboot)"""
#	pass

#def Mastermode():
#	"""Control master mode"""
#	pass

#def ActivateWindow(*args):
#	"""Activate the specified window"""
#	pass

#def ActivateWindowAndFocus(*args):
#	"""Activate the specified window and sets focus to the specified id"""
#	pass

#def ReplaceWindow(*args):
#	"""Replaces the current window with the new one"""
#	pass

#def TakeScreenshot():
#	"""Takes a Screenshot"""
#	pass

#def SlideShow(*args):
#	"""Run a slideshow from the specified directory"""
#	pass

#def RecursiveSlideShow(*args):
#	"""Run a slideshow from the specified directory, including all subdirs"""
#	pass

#def ReloadSkin():
#	"""Reload XBMC's skin"""
#	pass

#def UnloadSkin():
#	"""Unload XBMC's skin"""
#	pass

#def RefreshRSS():
#	"""Reload RSS feeds from RSSFeeds.xml"""
#	pass

#def PlayerControl(*args):
#	"""Control the music or video player"""
#	pass

#def Playlist.PlayOffset(*args):
#	"""Start playing from a particular offset in the playlist"""
#	pass

#def Playlist.Clear():
#	"""Clear the current playlist"""
#	pass

#def EjectTray():
#	"""Close or open the DVD tray"""
#	pass

#def AlarmClock(*args):
#	"""Prompt for a length of time and start an alarm clock"""
#	pass

#def CancelAlarm(*args):
#	"""Cancels an alarm"""
#	pass

#def Action(*args):
#	"""Executes an action for the active window (same as in keymap)"""
#	pass

#def Notification(*args):
#	"""Shows a notification on screen, specify header, then message, and optionally time in milliseconds and a icon."""
#	pass

#def PlayDVD():
#	"""Plays the inserted CD or DVD media from the DVD-ROM Drive!"""
#	pass

#def RipCD():
#	"""Rip the currently inserted audio CD"""
#	pass

#def Skin.ToggleSetting(*args):
#	"""Toggles a skin setting on or off"""
#	pass

#def Skin.SetString(*args):
#	"""Prompts and sets skin string"""
#	pass

#def Skin.SetNumeric(*args):
#	"""Prompts and sets numeric input"""
#	pass

#def Skin.SetPath(*args):
#	"""Prompts and sets a skin path"""
#	pass

#def Skin.Theme(*args):
#	"""Control skin theme"""
#	pass

#def Skin.SetImage(*args):
#	"""Prompts and sets a skin image"""
#	pass

#def Skin.SetLargeImage(*args):
#	"""Prompts and sets a large skin images"""
#	pass

#def Skin.SetFile(*args):
#	"""Prompts and sets a file"""
#	pass

#def Skin.SetAddon(*args):
#	"""Prompts and set an addon"""
#	pass

#def Skin.SetBool(*args):
#	"""Sets a skin setting on"""
#	pass

#def Skin.Reset(*args):
#	"""Resets a skin setting to default"""
#	pass

#def Skin.ResetSettings():
#	"""Resets all skin settings"""
#	pass

#def Mute():
#	"""Mute the player"""
#	pass

#def SetVolume(*args):
#	"""Set the current volume"""
#	pass

#def Dialog.Close(*args):
#	"""Close a dialog"""
#	pass

#def System.LogOff():
#	"""Log off current user"""
#	pass

#def Resolution(*args):
#	"""Change XBMC's Resolution"""
#	pass

#def SetFocus(*args):
#	"""Change current focus to a different control id"""
#	pass

#def UpdateLibrary(*args):
#	"""Update the selected library (music or video)"""
#	pass

#def CleanLibrary(*args):
#	"""Clean the video/music library"""
#	pass

#def ExportLibrary(*args):
#	"""Export the video/music library"""
#	pass

#def PageDown(*args):
#	"""Send a page down event to the pagecontrol with given id"""
#	pass

#def PageUp(*args):
#	"""Send a page up event to the pagecontrol with given id"""
#	pass

#def LastFM.Love():
#	"""Add the current playing last.fm radio track to the last.fm loved tracks"""
#	pass

#def LastFM.Ban():
#	"""Ban the current playing last.fm radio track"""
#	pass

#def Container.Refresh():
#	"""Refresh current listing"""
#	pass

#def Container.Update():
#	"""Update current listing. Send Container.Update(path,replace) to reset the path history"""
#	pass

#def Container.NextViewMode():
#	"""Move to the next view type (and refresh the listing)"""
#	pass

#def Container.PreviousViewMode():
#	"""Move to the previous view type (and refresh the listing)"""
#	pass

#def Container.SetViewMode(*args):
#	"""Move to the view with the given id"""
#	pass

#def Container.NextSortMethod():
#	"""Change to the next sort method"""
#	pass

#def Container.PreviousSortMethod():
#	"""Change to the previous sort method"""
#	pass

#def Container.SetSortMethod(*args):
#	"""Change to the specified sort method"""
#	pass

#def Container.SortDirection():
#	"""Toggle the sort direction"""
#	pass

#def Control.Move(*args):
#	"""Tells the specified control to 'move' to another entry specified by offset"""
#	pass

#def Control.SetFocus(*args):
#	"""Change current focus to a different control id"""
#	pass

#def Control.Message(*args):
#	"""Send a given message to a control within a given window"""
#	pass

#def SendClick(*args):
#	"""Send a click message from the given control to the given window"""
#	pass

#def LoadProfile(*args):
#	"""Load the specified profile (note; if locks are active it won't work)"""
#	pass

#def SetProperty(*args):
#	"""Sets a window property for the current focused window/dialog (key,value)"""
#	pass

#def ClearProperty(*args):
#	"""Clears a window property for the current focused window/dialog (key,value)"""
#	pass

#def PlayWith(*args):
#	"""Play the selected item with the specified core"""
#	pass

#def WakeOnLan(*args):
#	"""Sends the wake-up packet to the broadcast address for the specified MAC address"""
#	pass

#def Addon.Default.OpenSettings(*args):
#	"""Open a settings dialog for the default addon of the given type"""
#	pass

#def Addon.Default.Set(*args):
#	"""Open a select dialog to allow choosing the default addon of the given type"""
#	pass

#def Addon.OpenSettings(*args):
#	"""Open a settings dialog for the addon of the given id"""
#	pass

#def UpdateAddonRepos():
#	"""Check add-on repositories for updates"""
#	pass

#def UpdateLocalAddons():
#	"""Check for local add-on changes"""
#	pass

#def ToggleDPMS():
#	"""Toggle DPMS mode manually"""
#	pass

#def Weather.Refresh():
#	"""Force weather data refresh"""
#	pass

#def Weather.LocationNext():
#	"""Switch to next weather location"""
#	pass

#def Weather.LocationPrevious():
#	"""Switch to previous weather location"""
#	pass

#def Weather.LocationSet(*args):
#	"""Switch to given weather location (parameter can be 1-3)"""
#	pass

##if defined(HAS_LIRC) || defined(HAS_IRSERVERSUITE)
#def LIRC.Stop():
#	"""Removes XBMC as LIRC client"""
#	pass

#def LIRC.Start():
#	"""Adds XBMC as LIRC client"""
#	pass

#def LIRC.Send(*args):
#	"""Sends a command to LIRC"""
#	pass
##endif

##ifdef HAS_LCD
#def LCD.Suspend():
#	"""Suspends LCDproc"""
#	pass

#def LCD.Resume():
#	"""Resumes LCDproc"""
#	pass
##endif

#def VideoLibrary.Search():
#	"""Brings up a search dialog which will search the library"""
#	pass

#def ToggleDebug():
#	"""Enables/disables debug mode"""
#	pass

#def StartPVRManager():
#	"""(Re)Starts the PVR manager"""
#	pass

#def StopPVRManager():
#	"""Stops the PVR manager"""
#	pass


class Monitor(object):
    """
   	Monitor class.
    Monitor() -- Creates a new Monitor to notify addon about changes.
    """
    def onAbortRequested(self):
        """
        Deprecated!
        """
        pass

    def waitForAbort(self):
        """
        waitForAbort() -- onAbortRequested method.
        Will be called when XBMC requests Abort
        """
        pass

    def onDatabaseUpdated(self, database):
        """
        Deprecated!
        """
        pass

    def onScreensaverActivated(self):
        """
        onScreensaverActivated() -- onScreensaverActivated method.
        Will be called when screensaver kicks in
        """
        pass

    def onScreensaverDeactivated(self):
        """
        onScreensaverDeactivated() -- onScreensaverDeactivated method.
        Will be called when screensaver goes off
        """
        pass

    def onSettingsChanged(self):
        """
        onSettingsChanged() -- onSettingsChanged method.
        Will be called when addon settings are changed
        """
        pass

    def onDatabaseScanStarted(self, database):
        """
        Deprecated!
        """
        pass

    def onNotification(self, sender, method, data):
        """
        onNotification(sender, method, data)--onNotification method.

        sender : sender of the notification
        method : name of the notification
        data : JSON-encoded data of the notification

        Will be called when XBMC receives or sends a notification
        """
        pass

    def onCleanStarted(self, library=''):
        """
        onCleanStarted(library)--onCleanStarted method.

        library : video/music as string

        Will be called when library clean has started
        and return video or music to indicate which library is being cleaned
        """
        pass

    def onCleanFinished(self, library=''):
        """
        onCleanFinished(library)--onCleanFinished method.

        library : video/music as string

        Will be called when library clean has ended
        and return video or music to indicate which library has been cleaned
        """
        pass

    def onDPMSActivated(self):
        """
        onDPMSActivated() --onDPMSActivated method.

        Will be called when energysaving/DPMS gets active
        """
        pass

    def onDPMSDeactivated(self):
        """
        onDPMSDeactivated() --onDPMSDeactivated method.

        Will be called when energysaving/DPMS is turned off
        """
        pass

    def onScanFinished(self, library=''):
        """
        onScanFinished(library)--onScanFinished method.

        library : video/music as string

        Will be called when library scan has ended
        and return video or music to indicate which library has been scanned
        """
        pass

    def onScanStarted(self, library=''):
        """
        onScanStarted(library)--onScanStarted method.

        library : video/music as string

        Will be called when library scan has started
        and return video or music to indicate which library is being scanned
        """
        pass

    def waitForAbort(self, timeout):
        """
        waitForAbort([timeout]) -- Block until abort is requested, or until timeout occurs. If an
        abort requested have already been made, return immediately.
        Returns True when abort have been requested, False if a timeout is given and the operation times out.

        :param timeout: float - (optional) timeout in seconds. Default: no timeout.
        :return: bool
        """
        return bool





















































































