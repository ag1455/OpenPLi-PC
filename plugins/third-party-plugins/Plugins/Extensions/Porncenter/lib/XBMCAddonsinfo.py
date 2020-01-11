##new file to show information and errors

from Screens.Screen import Screen

from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Tools.Directories import copyfile ,fileExists
from enigma import getDesktop

import os
from Screens.Standby import TryQuitMainloop
##########################
import gettext
def _(txt):
	t = gettext.dgettext("xbmcaddons", txt)
	if t == txt:
		print "[XBMCAddonsA] fallback to default translation for", txt
		t = gettext.gettext(txt)
	return t

##########################
class XBMCAddonsinfoScreen(Screen):
		
	def __init__(self, session,plugin_id=None,sender=None,data=None):
		Screen.__init__(self, session)
		self.skinName='XBMCAddonsinfoScreen'
                self.color="#00060606"
                title = "Information"
                self.sender=sender
                self.data=data
		self.finishedCallback = None
		self.closeOnSuccess = False
		cmdlist = None
                self.plugin_id=plugin_id
                
		self["text"] = ScrollLabel("")
		self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions"], 
		{       
			"ok": self.cancel,
			"back": self.cancel,
		        			
			"up": self["text"].pageUp,
			"down": self["text"].pageDown
		}, -1)
		
		self.cmdlist = cmdlist
		self.newtitle = title
		
		self.onShown.append(self.updateTitle)
		
		#self.container = eConsoleAppContainer()
		#self.run = 0
		#self.container.appClosed.append(self.runFinished)
		#self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun) # dont start before gui is finished


            
        def updateTitle(self):
		self.setTitle(self.newtitle)

	def startRun(self):
	        data=''          
	        if self.sender=='XBMCAddonsPlayer':
	           self["text"].setText(self.data)
	           return
	           
	        try:
	         if not self.plugin_id is None:
	            data=get_plugin_info(self.plugin_id)
                 else:
                    data=''
                except:
                    data=''
                debug=True            
		if debug:
		  import os
                  data='XBMCAddons addons error and logs' 
                  data=data+"\n"+"************Errors and logs**********************\n"       
                    
		        
                  if os.path.exists("/tmp/XBMCAddons_log"):    		
                     f=open("/tmp/XBMCAddons_log",'r')
		     lines=f.readlines()
		     
		  
		     for line in lines:
		         data=data+line	
                         
              
                  
                  
                         	        
		  
		else:
                      data="No info available" 
		
                data=data+"\n**********************************"+(_("\nPlease send the error log to the coder\nThe log file is available as /tmp/XBMCAddons_log,/tmp/xbmc_log,/tmp/TXBMCAddons_error"))+"\n**********************************"+(_("\nXBMXAddons support sites\nhttp://www.xtrend-alliance.com/"))+ (_("\n press OK or Cancel to exit"))
                
                self["text"].setText(data)

	def cancel(self):       
		self.close()


###################################
















