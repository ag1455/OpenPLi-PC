##to show e2 settings style
import os,sys
from Utils import *
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigText, ConfigYesNo
from Components.ConfigList import ConfigListScreen

from os import path, system
import xpath
import xbmcaddon
from Components.config import config,ConfigInteger,ConfigDirectory, ConfigSubsection, ConfigSubList, \
	ConfigEnableDisable, ConfigNumber, ConfigText, ConfigSelection, \
	ConfigYesNo, ConfigPassword, getConfigListEntry, configfile
from Components.ConfigList import ConfigListScreen
from Screens.Screen import Screen
from Components.Button import Button
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Label import Label
THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"
from Tools.Directories import fileExists, copyfile
from Tools.LoadPixmap import LoadPixmap
from enigma import  eTimer,RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont
##########################
import gettext
def _(txt):
	t = gettext.dgettext("KodiLite", txt)
	if t == txt:
		print "[KodoDirectA] fallback to default translation for", txt
		t = gettext.gettext(txt)
	return t

##########################
class RSList(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setItemHeight(40)
		textfont = int(config.plugins.kodiplug.textfont.value)
                self.l.setFont(0, gFont("Regular", textfont))

		       
def showlist(entry):
	return [entry,
			
		(eListboxPythonMultiContent.TYPE_TEXT,  55, 10, 320, 37, 0, RT_HALIGN_LEFT, str(entry[0])),
		(eListboxPythonMultiContent.TYPE_TEXT,  340, 10, 250, 37, 0, RT_HALIGN_LEFT, str(entry[1]))
		]		       

def getproxylinks(plugin_id):
  done=True
  links=[]
  try:
    f=open("/etc/XTkodi/proxy_links","r")
    data=f.readlines()
    print "23data",data
    
    f.close()
    for item in data:
       if not "$" in item:
          continue  
       plugin=item.split("$")[0].strip()
       proxy_name= item.split("$")[1].strip()
       proxy_link=item.split("$")[2].strip()
            
       if plugin==plugin_id: 
          if not proxy_link.endswith("/"):
                 proxy_link=proxy_link+"/"
          if not proxy_link.startswith("http://"):
                 proxy_link="http://"+proxy_link                  
          links.append((proxy_link,proxy_name))
           
    
  except:
    print "proxy links 36",'erro in proxy_links file'
    links=[]
    pass
    
  return links 

def get_logininfo(plugin_id=None):
    username=""
    password=""
    fname="/etc/XTkodi/XTkodi_login"
    if plugin_id is None:
       return username,passowrd
    try:
      f=open(fname,'r')
      lines=f.readlines()
      for line in lines:
         if line.strip().startswith(plugin_id):
            username=line.split(":")[1].strip()
            password=line.split(":")[2].strip()
            return username,password
      return username,password      
    except:
      return username,password   
class AddonsettScreen(Screen):
    def __init__(self, session, plug):
		Screen.__init__(self, session)
		self.skinName = "xbmc3"
       
                self["menu"] = RSList([])
		self["info"] = Label("Press ok to change value")
		self["pixmap"] = Pixmap()
		self["actions"] = NumberActionMap(["OkCancelActions"],{
                       "ok": self.okClicked,                                            
                       "cancel": self.close,}, -1)
                self.plug = plug

                sys.argv=[]
                sys.argv.append(THISPLUG+"/plugins/"+self.plug+"/default.py") 
                self.addon=xbmcaddon.Addon(self.plug)
                self.ids = []
                self.options = []
                self.types = []
                self.lnum = []
                self.ltxt = []
                self.lines = []
               
                self.list=[]
                self.onShown.append(self.setup)

            

    def selection_changed(self):
                try:
                  idx = self["menu"].getSelectionIndex()
                  list = self.list[idx]
                  default=list[1]
                except:
                  return  
                  
                if self.type=='text':
                   self["info"].setText(default+"\nPress ok to change value")
                else:
                   self["info"].setText(default+"\nSelect new value and save") 
    def setup(self):
          pic1 = THISPLUG + "/images/default.png"
          self["pixmap"].instance.setPixmapFromFile(pic1)
          
          self.list=[]
          print "71",self.addon.getSetting2("movreel-account")
          settings_list=self.addon.openSettings()    
          
          for item in settings_list:
                 settings=item[1]##dict
                 index=item[0]
                 id=str(settings.get("id",""))
                 type=str(settings.get("type",""))
                 label=str(settings.get("label",""))
                 default=str(settings.get("default",""))
                 values=str(settings.get("values",""))
                 if not values=='' and len(default)<2:
                    try:
                      parts=values.split("|")
                      default=parts[int(default)]
                    except:
                      pass  
                 if not id=='':
                    self.list.append((id,default,type,label,values,index))
          self["menu"].setList(map(showlist, self.list))       
         
           

    def okClicked(self):
          idx = self["menu"].getSelectionIndex()
          
          plug = self.plug
          list = self.list[idx]
          self.session.openWithCallback(self.callback,Addonsett2Screen, plug, list)
    def callback(self,result):
        if result==True:
           self.setup()
    
    
class Addonsett2Screen(Screen):
    def __init__(self, session, plug,list):
		Screen.__init__(self, session)
		self.skinName = "xbmc5"
		
                self['key_red'] = Button(_('Cancel'))
                self['key_green'] = Button(_('Save'))		
		
		
                self["menu"] = RSList([])
		self["info"] = Label("Press ok to change default value")
		self["pixmap"] = Pixmap()
                self["actions"] = NumberActionMap(['ColorActions',"OkCancelActions"],{
                       "ok": self.okClicked,
                       "green":self.save,
                       "red":self.exit,                                            
                       "cancel": self.exit,}, -1)
                self.plug = plug
                self.addon=xbmcaddon.Addon(self.plug)
                self.list=list
                self.type=list[2]
                self.setting_id=list[0]
                self.text=list[1]
                self.vals=[]
                
                self["menu"].onSelectionChanged.append(self.selection_changed)
                if self.type=='text' or self.type=='number':
                
                  self.timer = eTimer()
                  self.timer.callback.append(self.okClicked)
                  self.timer.start(50, 1)                
                
                   
                else:
                   self.onShown.append(self.sel)
                
              

    def sel(self):

          pic1 = THISPLUG + "/images/default.png"
          self["pixmap"].instance.setPixmapFromFile(pic1)
          ##list.append((id,default,type,label,values,index))
          
          vals=self.list[4]
          default=self.list[1]
          if self.type=='bool':
             if default=='true':
                self.vals.append(("true",'default'))
             else:
                self.vals.append(("true",''))
             if default=='false':
                self.vals.append(("false",'default'))
             else:
                self.vals.append(("false",''))                
                
             
             
          elif self.type=="enum": 
             self.vals = []
             self.vals = vals.split("|")
             nvals=[]
             try:
               idx=int(default)
             except:
               idx=default
             for i in range(0,len(self.vals)):
                 if len(str(idx))<2:
                 
                   if i==idx:
                     nvals.append((self.vals[i],"default"))
                   else:
                     nvals.append((self.vals[i],""))
                 else:
                  if self.vals[i]==default:
                    nvals.append((self.vals[i],"default"))
                  else:
                    nvals.append((self.vals[i],""))                   
             self.vals=nvals
             
             
          elif self.type=="labelenum": 
             self.vals = []
             self.vals = vals.split("|")
             nvals=[]
             
             for i in range(0,len(self.vals)):
                 if self.vals[i]==default:
                    nvals.append((self.vals[i],"default"))
                 else:
                    nvals.append((self.vals[i],""))
             self.vals=nvals
                         
             
          elif self.type=="text" or self.type=="number":
              self.vals=[]
              print "261",default
              self.vals.append((default,""))
              
              self["menu"].setList(map(showlist, self.vals))
              
              
          else :
              self.vals=[]
              self.vals.append((default,""))
                        
          self["menu"].setList(map(showlist, self.vals))
          
          
    def selection_changed(self):
                
                if self.type=='text':
                   self["info"].setText("Press ok to change value")
                else:
                   self["info"].setText("Select new value and save")             

    def okClicked(self):
                             
                             if  self.type=='bool' or self.type=='enum' or self.type=='labelenum':
                                return
                             #isel = self["menu"].getSelectionIndex()
                             txt=self.text
                             if "pass" in self.setting_id :
                                username,password=get_logininfo(self.plug)
                                txt=password
                             elif "user" in self.setting_id :
                                username,password=get_logininfo(self.plug)
                                txt=username                             
                             elif "website" in self.setting_id or "link" in self.setting_id or "source" in self.setting_id or "url" in self.setting_id:
                               links=getproxylinks(self.plug)
                               
                               try:txt=links[0][0]
                               except:pass 
                             
                                
                                
                             from  Screens.VirtualKeyBoard import VirtualKeyBoard
                             
                             self.session.openWithCallback(self.searchCallback, VirtualKeyBoard, title = (_("Enter new value")), text = txt)           
                
            ###mfaraj start                
    def searchCallback(self,text): 
                  if text:
             
                       self.vals=[]
                       self.vals.append((text,""))
                       self["info"].setText("Press ok to change value")
                       self["menu"].setList(map(showlist, self.vals)) 
                       
                  else:
                          
                       self.sel()  
    def exit(self):
        self.close(False)
    def settings_backup(self):
        settings_xml=THISPLUG+"/plugins/"+self.plug+"/resources/settings.xml"
        settings_xmlbackup=THISPLUG+"/plugins/"+self.plug+"/resources/settings_backup.xml"
        try:
          copyfile(settings_xml,settings_xmlbackup)
        except:
          cmd="cp -o "+ settings_xml+" "+ settings_xmlbackup
          os.system(cmd)
                   
    def settings_restore(self):
        settings_xml=THISPLUG+"/plugins/"+self.plug+"/resources/settings.xml"
        settings_xmlbackup=THISPLUG+"/plugins/"+self.plug+"/resources/settings_backup.xml"
        try:
          copyfile(settings_xmlbackup,settings_xml)
        except:
          cmd="cp -o "+ settings_xmlbackup+" "+ settings_xml
          os.system(cmd)    
    
    def save(self):
          isel = self["menu"].getSelectionIndex()

          if self.type=='enum':
                  selection = str(isel)

          else:
                  selection=str(self.vals[isel][0])
          self.settings_backup()        
#          result=self.addon.setSetting(setting_id=self.setting_id,value=selection)
          result=self.addon.setSetting(id=self.setting_id,value=selection)
          if result==False:
             self["info"].setText("New value not saved,add manually to settings.xml")
             self.settings_restore()
             return
          self.close(True)
