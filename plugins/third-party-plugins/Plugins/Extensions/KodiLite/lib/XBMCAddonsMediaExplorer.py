import os,sys  
from enigma import  loadPNG,eTimer,eListbox,  RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont
from Components.ActionMap import ActionMap, NumberActionMap
from Screens.MessageBox import MessageBox


#from Screens.InfoBarGenerics import InfoBarShowHide, NumberZap, InfoBarAudioSelection, InfoBarSubtitleSupport,InfoBarSeek, InfoBarNotifications

from Screens.Screen import Screen

from Components.MenuList import MenuList
from Components.Label import Label   


from Components.Button import Button


from Components.config import config,ConfigInteger,ConfigDirectory, ConfigSubsection, ConfigSubList, \
	ConfigEnableDisable, ConfigNumber, ConfigText, ConfigSelection, \
	ConfigYesNo, ConfigPassword, getConfigListEntry, configfile
from Components.ConfigList import ConfigListScreen
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmap, MultiContentEntryPixmapAlphaTest


from Tools.Directories import resolveFilename, pathExists, SCOPE_MEDIA,copyfile,fileExists,createDir,removeDir,SCOPE_PLUGINS,SCOPE_CURRENT_SKIN
THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"
PLUGIN_PATH=THISPLUG
##########################
import gettext
def _(txt):
	t = gettext.dgettext("xbmcaddons", txt)
	if t == txt:
		print "[XBMCAddonsA] fallback to default translation for", txt
		t = gettext.gettext(txt)
	return t

##########################

def XBMCAddonsScreen1_channels(entry):
	return [entry,
		(eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 1, 35, 35, loadPNG(PLUGIN_PATH+'/skin/images/movie.png')),
		(eListboxPythonMultiContent.TYPE_TEXT, 45, 10, 860, 37, 0, RT_HALIGN_LEFT, str(entry[0].strip()))
	       ]

def mkdir(backuppath):

        try:
            if (os.path.exists(backuppath) == False):
                os.makedirs(backuppath)
        except:
            pass
def getDownloadPath():
    Downloadpath = str(config.plugins.kodiplug.cachefold.value)
    mkdir(Downloadpath)

    if Downloadpath.endswith('/'):
        return Downloadpath
    else:
        return Downloadpath + '/'
def get_filedate(file):
    import os.path, time
    try:
      mdate= time.ctime(os.path.getmtime(file))
      return mdate
    except:
      return ""
    #print "created: %s" % time.ctime(os.path.getctime(file))


def freespace():
         downloadlocation=getDownloadPath()
         try:
            diskSpace = os.statvfs(downloadlocation)
            #tspace=os.stat('/')
            capacity = float(diskSpace.f_bsize * diskSpace.f_blocks)
            available = float(diskSpace.f_bsize * diskSpace.f_bavail)
            #used = diskSpace.f_bsize * (diskSpace.f_blocks -diskSpace.f_bavail)

            fspace=round(float((available) / (1024.0*1024.0)),2)
	    tspace=round(float((capacity) / (1024.0 * 1024.0)),1)
            #self.freespace=nspace
            spacestr='Free space(' +str(fspace)+'MB) Total space(' + str(tspace)+'MB)'
	    #self["info1"].setText('Free space available:' +str(fspace)+'MB Total space:' + str(tspace)+' MB')
            return fspace
         except:
            return 0



class XBMCAddonsMediaExplorer(Screen):

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
                self.skinName = "XBMCAddonsdownloadsscreen"

                #self["list"] = RSList([])
                self['info'] = Label()
                self['key_red'] = Button(_('Exit'))
                self["key_green"]=Label(_("Play"))
                self['key_yellow'] = Button(_("Rename "))
                self['key_blue'] = Button(_("Delete"))


                downloadlocation=  config.plugins.kodiplug.cachefold.value

		self["info"] = Label(_("Download Path: ")+downloadlocation)
		self.streamMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self.streamMenuList.l.setFont(0, gFont('Regular', 20))
		self.streamMenuList.l.setFont(1, gFont('Regular', 18)) 
		self.streamMenuList.l.setFont(2, gFont('Regular', 12)) 
		self.streamMenuList.l.setFont(3, gFont('Regular', 10))
		self.streamMenuList.l.setItemHeight(37)
		self["list"] = self.streamMenuList 
		############

                self.movie_list=[]
                self.searchstr=None
                self.searchagain="titanic"
                self.filmliste=[]
		#self.mlist.setList(map(channelEntryIPTVplaylist, self.channel_list))



	        self.page=1
		#self.glist.onSelectionChanged.append(self.groupselectionchanged)
		self.streamMenuList.onSelectionChanged.append(self.moviesselectionchanged)
		self.onShown.append(self.getlocalmedia)
		self["actions"] = ActionMap([ "ColorActions","SetupActions","DirectionActions","PiPSetupActions","WizardActions","NumberActions","EPGSelectActions"],
			{
			"red":self.deletefile ,
			"green":self.keyOK ,
			"blue":self.deletefile,
			"yellow":self.renamefile,#self.addfavorite,
			"ok": self.keyOK,
			#"info"	: self.viewdownloads,
			"cancel": self.exit,
			"up":self["list"].up ,
			"down":self["list"].down,
			"left"	:self["list"].pageUp ,
			"right"	: self["list"].pageDown,

			},-1)

		self.pages=[]
		cat_movies=[]
	        self.movies=[]
		self.pagemovies=[]
		self.desc=""
		self.keyLocked = False
		self.page=1
		self.download=False
		#self.onLayoutFinish.append(self.loadPage)
		self.searchstr=None
		self.page=1
		#self.timer = eTimer()
                #self.timer.callback.append(self.getlocalmedia)
                #self.timer.start(100, 1)


        def renamefile(self):
            from Screens.VirtualKeyBoard import VirtualKeyBoard
            try:

              filename=self["list"].getCurrent()[0][0]
            except:
              self["info"].setText("Failed to rename file")
              return

            self.session.openWithCallback(self.renameCallback, VirtualKeyBoard, title = (_("Enter new file name")), text = filename)
        def renameCallback(self,newfilename):
            if not newfilename:
               return
            try:
              filepath=self["list"].getCurrent()[0][2]
              filename=self["list"].getCurrent()[0][0]
            except:
             self["info"].setText(_("Failed to rename file")) 
             return
            newfilepath=filepath.replace(filename,newfilename)
            if newfilename:
               try:
                 os.rename(filepath,newfilepath)
                 self["info"].setText(_("file renamed successfuly"))
                 self.getlocalmedia()
               except:
                 self["info"].setText(_("Failed to rename file"))

        def getlocalmedia(self,result=None):

	    folder= getDownloadPath()
	    if freespace()==0:
	            self["info"].setText(folder+(_(" Free space: zero or invalid location")))
                    return
	    else:

                   fspace=str(freespace())
	           self["info"].setText(folder+(_(" Free space: "))+fspace+"MB")
                
	    if folder.endswith("/"):
	           self.folder=folder

            else:
                   self.folder=folder+"/"
            try:
                self.mediafiles=[]



                for x in os.listdir(self.folder):
                    fullpath=self.folder+ x
                    if os.path.isfile(fullpath):


                       msize=os.path.getsize(fullpath)
                       localimagesize=str(round(float((msize) / (1024.0*1024.0)),2))+'MB'
                       x=x.strip()
                       if x.endswith(".mpg") or x.endswith(".ts") or x.endswith(".mp3") or x.endswith(".mp4") or x.endswith(".avi") or x.endswith(".flv") or x.endswith(".wmv"):
                          try:title=x.split(".")[0]
                          except:pass
                          self.mediafiles.append((title,localimagesize,fullpath,))

                    else:
                       pass

                self.streamMenuList.setList(map(XBMCAddonsScreen1_channels, self.mediafiles))
                #self["infoload"].setText(" ")
            except:
                self.mediafiles.append(((_('Invalid download path')),""))
                self.streamMenuList.setList(map(XBMCAddonsScreen1_channels, self.mediafiles))
                #self["infoload"].setText(" ")


        def changepath(self):
            return
            from DownloadLocation import TStvdownloadLocation
            try:
               self.session.openWithCallback(self.backuplocation_choosen, TStvdownloadLocation)
            except:
               return


        def deletefile(self):
                        try:
                          downloadlocation=  getDownloadPath()
                          self.filename=self["list"].getCurrent()[0][2]
                          print "In deletefile self.filename =", self.filename
	                  #self.filename=downloadlocation+self.fname
  	                  self.session.openWithCallback(self.removefile, MessageBox, _(self.filename+ " will be removed,are you sure?"), MessageBox.TYPE_YESNO)
                          return
                        except:
                          self["info"].setText("No files deleted ")

	def removefile(self,result):
	 if result:
            print "324",self.filename
            try:
               os.remove(self.filename)
               self.getlocalmedia()
               self["info"].setText(self.filename +" deleted!")

            except:
               self["info"].setText(_("sorry unable to delete file! "))


	def keyOK(self):
	
                          downloadlocation=  getDownloadPath()
                          try:self.filename=self["list"].getCurrent()[0][2]
                          except:return
                          
                          try:title=self["list"].getCurrent()[0][0]
                          except:return	                  
                          from Utils import Playvid2
                          self.session.open(Playvid2,title,self.filename,"")


#################################################################################################

        def refreshlists(self,result=False):

             if result==True:
                self.close

               # self.showpage()

        def moviesselectionchanged(self):

            folder=getDownloadPath()
	    if freespace()==0:
	            self["info"].setText(folder+" Free space: zero or invalid location")
                    return
	    else:
                   try:filesize=self["list"].getCurrent()[0][1]
                   except:filesize=''
                   try:title=self["list"].getCurrent()[0][0]
                   except:title=''

                   fspace=str(freespace())
                   fdate=get_filedate(self["list"].getCurrent()[0][2])
                   info=title+"\nsize "+filesize+" MB"+" "+fdate+"\n"+folder+" Free space: "+fspace+"MB"

	           self["info"].setText(info)


        def exit(self):

               self.close()

        def exitplugin(self):

			  self.close()

