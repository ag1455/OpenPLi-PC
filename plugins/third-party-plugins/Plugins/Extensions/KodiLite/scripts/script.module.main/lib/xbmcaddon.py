# coding: utf-8
import os, os.path, sys
import xml.etree.cElementTree 

myfile = file(r"/tmp/addoncat.txt")
icount = 0
for line in myfile.readlines():
       ADDONCAT = line
myfile.close()

# xbmc/interfaces/python/xbmcmodule/PythonAddon.cpp
# (with a little help from xbmcswift)
#####################20171210#########################################
def getaddonpath_params(item=None):
    #module_path=sys.argv[0]
    ##module_path="/usr/lib/enigma2/python/Plugins/Extensions/TSmedia/addons/movies/plugin.video.glomovies/default.py"
    ##addon_path="/usr/lib/enigma2/python/Plugins/Extensions/TSmedia/addons/movies/plugin.video.glomovies" or "/usr/lib/enigma2/python/Plugins/Extensions/TSmedia/" + ADDONCAT + "/plugin.video.glomovies" for XBMCAddons
    ##section_path="/usr/lib/enigma2/python/Plugins/Extensions/TSmedia/addons/movies"  only for TSmedia
    ##addons_path="/usr/lib/enigma2/python/Plugins/Extensions/TSmedia/addons"  or .../XBMC for xbmcaddons or ..../" + ADDONCAT + " for XBMCAddons
    ##plugin_path="/usr/lib/enigma2/python/Plugins/Extensions/TSmedia or "/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/ or "/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/
    module_path =sys.argv[0] #"/usr/lib/enigma2/python/Plugins/Extensions/TSmedia/addons/movies/plugin.video.glomovies/default.py"

    count=module_path.count("/") ##10 for xbmcaddons and XBMCAddons and 11 for TSmedia
    addon_path,module_name=os.path.split(module_path)
    pass#print "Here in xbmcaddons-py  addon_path =", addon_path
    if count==11: ##for tsmedia
       section_path,addon_id=os.path.split(addon_path)
       main_addons_path,section_name=os.path.split(section_path)
       plugin_path,addons_name=os.path.split(main_addons_path)
       scripts_path=plugin_path+"/scripts" ##for tsmedia
       addons_path=section_path
    else:##for XBMCAddons and xbmcaddons
       n1 = addon_path.find("://", 0)
       if n1 < 0:
               addon_path = addon_path
       else:
               n2 = addon_path.find("/", (n1+4))
               if (n2 < 0):
                      addon_path = addon_path
               else:
#                      addon_path = addon_path[:(n2+1)]
                      addon_path = addon_path[:(n2)]

       addon_path = addon_path.replace("plugin://", "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/" + ADDONCAT + "/")
       addons_path,addon_id=os.path.split(addon_path)
       plugin_path,addons_name=os.path.split(addons_path)
       if addons_name=="XBMC":

          scripts_path=plugin_path+"/XBMC" ###for XBMcaddons


       else:##may be for future
          scripts_path=plugin_path+"/scripts"###may be used for other similar addons in future

#    pass#print "addon path params:plugin_path,addons_path,scripts_path,addon_id",plugin_path,addons_path,scripts_path,addon_id
    if item=='plugin_path':
       return plugin_path #/usr/lib/enigma2/python/Plugins/Extensions/XTkoodi,/usr/lib/enigma2/python/Plugins/Extensions/TSmedia,/usr/lib/enigma2/python/Plugins/Extensions/XBMCaddons
    if item=='addons_path':
       return addons_path  ##/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/" + ADDONCAT + ",/usr/lib/enigma2/python/Plugins/Extensions/TSmedia/addons/movies,/usr/lib/enigma2/python/Plugins/Extensions/XBMC

    if item=='scripts_path':
       return scripts_path ##/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/scripts,/usr/lib/enigma2/python/Plugins/Extensions/TSmedia/scripts,/usr/lib/enigma2/python/Plugins/Extensions/XBMC

    if item=="addon_id":
       return addon_id #example plugin.video.glowmovies

    if item is None:
       return plugin_path,addons_path,scripts_path,addon_id


class Addon:

	def __init__(self, id=None):

                       pass#print "Here in xbmcaddon-py id =", id
                       if id is not None:## requested from addons or scripts
                             if id.startswith("script"):
                                self.id=id
                                self.path=getaddonpath_params("scripts_path")+"/"+str(self.id)
                             elif id.startswith("plugin"):   
                                 self.id=getaddonpath_params("addon_id")##get addon_id from sys.argv[0] for tsmedia reason we do not use self.id=id
                                 self.path=getaddonpath_params("addons_path")+"/"+str(self.id)
                             else:
                                 self.id=getaddonpath_params("addon_id")##get addon_id from sys.argv[0] for tsmedia reason we do not use self.id=id
                                 self.path=getaddonpath_params("addons_path")+"/"+str(self.id)

                       else: #either requested from addons not scripts 
                             self.id=getaddonpath_params("addon_id")##we extract addon path params from sys.argv[0]
                             self.path=getaddonpath_params("addons_path")+"/"+str(self.id)



	def getLocalizedString(self, idx=" "):
	     pass#print "In xbmcaddon idx =", idx
             xfile = self.path + "/resources/language/English/strings.xml"
             if not os.path.exists(xfile):
                   xfile = self.path + "/resources/language/english/strings.xml"
                   if not os.path.exists(xfile):
                         xfile = self.path + "/resources/language/English/strings.po"
                         if not os.path.exists(xfile):
                                xfile = self.path + "/resources/language/english/strings.po"
                         if not os.path.exists(xfile):
                                xfile = self.path + "/resources/language/resource.language.en_gb/strings.po" #krypton cheddar
                         f = open(xfile, "r")
                         fpo = f.read()
                         n1 = fpo.find(str(idx), 0)
                         if n1 < 0:
                                xtxt = str(idx)
                                return xtxt
                         n2 = fpo.find('msgid', n1)
                         n3 = fpo.find('"', n2)
                         n4 = fpo.find('"', (n3+1))
                         xtxt = fpo[(n3+1):n4]
                         pass#print "In xbmcaddon xtxt A=", xtxt
                         return xtxt
             ftxt = open(xfile, "r").read()
             n1 = ftxt.find(str(idx), 0)
             if n1 < 0:
                     xtxt = str(idx)
                     return xtxt
             n2 = ftxt.find(">", n1)
             n3 = ftxt.find("<", n2)
             xtxt = ftxt[(n2+1):n3]
             pass#print "In xbmcaddon xtxt B=", xtxt
             return str(xtxt)

	def getSetting(self,id=None):
	   item = '"' + str(id) + '"'
           pass#print "In xbmcaddon-py id =", item
           pass#print "In xbmcaddon-py self.path =", self.path
           xfile = self.path + "/resources/settings.xml" 
           if not os.path.exists(xfile):
                    return ""
           else:
             f = open(xfile, 'r').read()
             if item not in f:
                    return ""

             lines = []
             lines = f.splitlines()
             for line in lines:
                    pass#print "In xbmcaddon-py line =", line
                    if str(item) in line:
                            pass#print "In xbmcaddon-py line B=", line
                            n2 = line.find(" default", 0)
                            if n2 < 0:
                                   return ""
                            n3 = line.find('"', n2)
                            n4 = line.find('"', (n3+1))
                            xtxt = line[(n3+1):n4]
                            break

             pass#print "In xbmcaddon xtxt B=", xtxt
             return str(xtxt)

	def getSetting2(self,id=None):
	     item = id
             pass#print "In xbmcaddon id =", id
             pass#print "In xbmcaddon self.path =", self.path
             xfile = self.path + "/resources/settings.xml" 
             f = open(xfile, 'r').read()
             if item not in f:
                    return ""

             lines = []
             lines = f.splitlines()
             for line in lines:
                    if str(id) in line:
                            n2 = line.find("default", 0)
                            n3 = line.find('"', n2)
                            n4 = line.find('"', (n3+1))
                            xtxt = line[(n3+1):n4]
                            break

             pass#print "In xbmcaddon xtxt B=", xtxt
             return xtxt



	def setSetting(self, id = " ", value = " "):
           if value is None:
                     return False

#	   item = id
	   item = '"' + str(id) + '"'
           pass#print "In xbmcaddon setSetting id =", id 
           pass#print "In xbmcaddon setSetting value =", value
           pass#print "In xbmcaddon setSetting self.path =", self.path
           xfile = self.path + "/resources/settings.xml" 
           f = open(xfile, 'r').read()
           if item not in f:
                    nline = '<setting id="' + item + '" type="text" default="' + str(value) + '" visible="false" />\n'
                    n1 = f.find("<setting id", 0)
                    s1 = f[:n1]
                    s2 = f[n1:]
                    fnew = s1 + nline + s2
                    f2 = open('/tmp/temp.xml', 'w')
                    f2.write(fnew)
                    f2.close()
           else:
             f2 = open('/tmp/temp.xml', 'w')
             lines = []
             lines = f.splitlines()
             for line in lines:
                    if str(id) in line:
                            n2 = line.find("default", 0)
                            n3 = line.find('"', n2)
                            n4 = line.find('"', (n3+1))
                            s = line[n2:(n4+1)]
                            s2 = 'default="' + str(value) + '"'
                            line = line.replace(s, s2)

                    line = line + "\n"
                    f2.write(line)
           f2.close()
           cmd = "mv -f '/tmp/temp.xml' " + xfile
           os.system(cmd)
           return True

	# sometimes called with an arg, e.g veehd
	def openSettings(self, arg=None):
	      """get all settings."""
	      try:
                settings_xml=self.path + "/resources/settings.xml"
                pass#print "283",settings_xml
                tree = xml.etree.cElementTree.parse(settings_xml)
                root = tree.getroot()

                i=0
                list=[]
                for setting in root.iter('setting'):

                            list.append((i,setting.attrib))##add dict for all settings in the line,i=line number
                            i=i+1
                pass#print "In openSettings list =",list
                return list
		#pass#print "*** openSettings ***"
              except:
                list=[]
                return list

	def getAddonInfo(self, item):
	        pass#print "In xbmcaddon item =", item
                cachefold=None
                try:
                  myfile = file(r"/etc/xbmc.txt")
                  icount = 0
                  for line in myfile.readlines():
                       cachefold = line
                       break
                except:
                      pass
                if  cachefold is None:
                   try:cachefold=sys.argv[3]
                   except:cachefold="/media/hdd"


                profile = cachefold + '/xbmc/profile/addon_data/' + str(self.id)
                cmd = "mkdir -p " + profile
                os.system(cmd)

                xfile = self.path + "/addon.xml"
#                pass#print "get_version xfile =", xfile
                if not os.path.exists(xfile):
                    pass#print "addon has no addon.xml or path wrong",xfile
                    pass#print "self.id",self.id
                    pass#print "addon path",self.path
                    return None
                tree = xml.etree.cElementTree.parse(xfile)
                root = tree.getroot()
                version = str(root.get('version'))
#                pass#print "get_version version =", version
                author = str(root.get('provider-name'))
                name = str(root.get('name'))
                id = str(root.get('id'))
                if item == "path":
                        return self.path
                elif item == "Path":
                        return self.path
                elif item == "version":
                        return version
                elif item == "author":
                        return author
                elif item == "name":
                        return name
                elif item == "id":
                        return id
                elif item == "profile":
                        return profile
                elif item == "Profile":
                        return profile
                else:
                        return "xxx"
