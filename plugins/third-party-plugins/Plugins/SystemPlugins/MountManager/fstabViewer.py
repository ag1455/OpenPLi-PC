#
#  fstabeditor
#
from . import _
from Components.config import config, ConfigText, ConfigNumber, ConfigSelection, NoSave, getConfigListEntry
from Components.ActionMap import *
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.Pixmap import Pixmap
#from Plugins.Plugin import PluginDescriptor
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import fileExists
from dirSelect import dirSelectDlg
from enigma import RT_HALIGN_LEFT, RT_HALIGN_RIGHT, eListboxPythonMultiContent, gFont
import os

entryList = []
lengthList = [0,0,0,0]

class fstabMenuList(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setFont(0, gFont("Regular", 22))
		self.l.setFont(1, gFont("Regular", 18))
		self.l.setItemHeight(220)

def fstabMenuListEntry(devicename, mountpoint,fstype, options, dumpfreq, passnum):
	res = [ (devicename, mountpoint,fstype, options, dumpfreq, passnum) ]
	res.append(MultiContentEntryText(pos=(230,15),size=(370,25), font=0, text=devicename))
	res.append(MultiContentEntryText(pos=(230,60),size=(370,25), font=0, text=mountpoint))
	res.append(MultiContentEntryText(pos=(230,90),size=(370,25), font=0, text=fstype))
	res.append(MultiContentEntryText(pos=(230,120),size=(370,25), font=0, text=options))
	res.append(MultiContentEntryText(pos=(230,150),size=(370,25), font=0, text=dumpfreq))
	res.append(MultiContentEntryText(pos=(230,180),size=(370,25), font=0, text=passnum))
	res.append(MultiContentEntryText(pos=(0,17),size=(200,25), font=1, flags=RT_HALIGN_RIGHT, text= _("Device name:")))
	res.append(MultiContentEntryText(pos=(0,62),size=(200,25), font=1, flags=RT_HALIGN_RIGHT, text= _("Mount point:")))
	res.append(MultiContentEntryText(pos=(0,92),size=(200,25), font=1, flags=RT_HALIGN_RIGHT, text= _("File system type:")))
	res.append(MultiContentEntryText(pos=(0,122),size=(200,25), font=1, flags=RT_HALIGN_RIGHT, text= _("Options:")))
	res.append(MultiContentEntryText(pos=(0,152),size=(200,25), font=1, flags=RT_HALIGN_RIGHT, text= _("Dump frequency:")))
	res.append(MultiContentEntryText(pos=(0,182),size=(200,25), font=1, flags=RT_HALIGN_RIGHT, text= _("Pass number:")))
	return res


class fstabViewerScreen(Screen,HelpableScreen):
	skin = """
		<screen position="center,center" size="600,430" title="fstab-Editor" >
			<widget name="entryinfo" position="0,10" size="580,20" halign="right" font="Regular;17" transparent="1" />
			<widget name="menulist" position="0,40" size="600,220" scrollbarMode="showNever" />
			<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/MountManager/icons/fstabEditor.png" position="70,304" size="100,40"/>
			<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/MountManager/icons/ok.png" position="230,300" size="35,25"/>
			<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/MountManager/icons/exit.png" position="230,325" size="35,25"/>
			<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/MountManager/icons/green.png" position="230,350" size="35,25"/>
			<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/MountManager/icons/blue.png" position="230,375" size="35,25"/>
			<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/MountManager/icons/yellow.png" position="230,400" size="35,25"/>
			<widget name="edit" font="Regular;18" position="275,301" size="200,25" transparent="1"/>
			<widget name="cancelist" font="Regular;18" position="275,326" size="200,25" transparent="1"/>
			<widget name="addentry" font="Regular;18" position="275,351" size="200,25" transparent="1"/>
			<widget name="run" font="Regular;18" position="275,376" size="200,25"  transparent="1"/>
			<widget name="restore" font="Regular;18" position="275,401" size="200,25" transparent="1"/>
		</screen>"""

	def __init__(self, session, args = 0):
		self.skin = fstabViewerScreen.skin
		self.session = session
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)

		self["entryinfo"] = Label()
		self["edit"] = Label(_("Edit"))
		self["cancelist"] = Label(_("Cancel"))
		self["addentry"] = Label(_("Add entry"))
		self["run"] = Label(_("Run mount -a"))
		self["restore"] = Label("")
		self["menulist"] = fstabMenuList([])
		self.fstabEntryList = []

		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
		{
			"green": (self.addEntry, _("Add entry")),
			"yellow": (self.restoreBackUp, _("Restore back up of fstab")),
			"blue":	(self.mountall, _("Run mount -a")),
		}, -1)

		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
		{
			"cancel":	(self.close, _("Close plugin")),
			"ok":		(self.openEditScreen, _("Open editor")),
		}, -1)

		self.setTitle(_("fstab-Editor"))
		self.builderror = False
		if fileExists("/etc/fstab"):
			self.buildScreen()

		self["menulist"].onSelectionChanged.append(self.selectionChanged)

	def openEditScreen(self):
		if not self.builderror:
			self.selectedEntry = self["menulist"].getSelectedIndex()
			self.session.openWithCallback(self.writeFile, fstabEditorScreen, self.selectedEntry)

	def buildScreen(self):
		self.fstabEntryList = []
		if fileExists("/etc/fstab.backup"):
			self["restore"].setText(_("Restore fstab.backup"))
		if fileExists("/etc/fstab"):
			fstabFile = open("/etc/fstab" ,"r")
			global entryList
			entryList = []
			self.counter = 0
			for line in fstabFile:
				if line[0] != "\n" and line[0] != "#":
					try:
						entry = line.split()
						entryList.append(entry)
						global lenghtList
						if len(entry[0]) > lengthList[0]:
							lengthList[0] = len(entry[0])
						if len(entry[1]) > lengthList[1]:
							lengthList[1] = len(entry[1])
						if len(entry[2]) > lengthList[2]:
							lengthList[2] = len(entry[2])
						if len(entry[3]) > lengthList[3]:
							lengthList[3] = len(entry[3])
						self.fstabEntryList.append(fstabMenuListEntry(entry[0],entry[1],entry[2],entry[3],entry[4],entry[5]))
						self.counter = self.counter+1
					except:
						fstabFile.close()
						self.fstabEntryList = []
						self["menulist"].l.setList(self.fstabEntryList)
						self["entryinfo"].setText(_('Failed to read /etc/fstab! Restore fstab.backup or edit the file manually.'))
						self.builderror = True
						return -1
			fstabFile.close()
		self["menulist"].l.setList(self.fstabEntryList)
		self["entryinfo"].setText("%d / %d" %(self["menulist"].getSelectedIndex()+1, self.counter))

	def writeFile(self, returnvalue):
		if returnvalue != 0 and not self.builderror:
			os.system("cp /etc/fstab /etc/fstab.backup")
			configFile = open('/etc/fstab', 'w')
			for i in range(len(entryList)):
				try:
					line = "%*s %*s %*s %*s %s %s\n" %(int(lengthList[0])*-1, entryList[i][0], int(lengthList[1])*-1, entryList[i][1], int(lengthList[2])*-1, entryList[i][2], int(lengthList[3])*-1, entryList[i][3],str(entryList[i][4]), str(entryList[i][5]))
					configFile.write(line)
				except:
					return -1
			configFile.close()
			self.buildScreen()

	def selectionChanged(self):
		if not self.builderror:
			self["entryinfo"].setText("%d / %d" %(self["menulist"].getSelectedIndex()+1, self.counter))

	def mountall(self):
		if not self.builderror:
			os.system("mount -a")

	def addEntry(self):
		if not self.builderror:
			self.session.openWithCallback(self.writeFile, fstabEditorScreen, None, addEntry=True)
		
	def restoreBackUp(self):
		if fileExists("/etc/fstab.backup"):
			os.system("rm -f /etc/fstab")
			os.system("cp /etc/fstab.backup /etc/fstab")
			self.session.open(MessageBox, _("Backup restored!"), MessageBox.TYPE_INFO, timeout=5)
			self.builderror = False
			self.buildScreen()
		else:
			self.session.open(MessageBox, _("Not found /etc/fstab.backup!"), MessageBox.TYPE_ERROR, timeout=5)


class fstabEditorScreen(Screen,ConfigListScreen,HelpableScreen):
	skin = """
		<screen position="center,center" size="600,380" title="fstab-Editor" >
			<widget itemHeight="28" name="config" position="0,40" size="600,224" scrollbarMode="showOnDemand"/>
			<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/MountManager/icons/fstabEditor.png" position="70,304" size="100,40"/>
			<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/MountManager/icons/green.png" position="230,300" size="35,25"/>
			<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/MountManager/icons/exit.png" position="230,325" size="35,25"/>
			<widget name="ButtonRed" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/MountManager/icons/red.png" position="230,350" zPosition="10" size="35,25" transparent="1" alphatest="on" />
			<widget name="save" font="Regular;18" position="275,301" size="200,25" transparent="1"/>
			<widget name="cansel" font="Regular;18" position="275,326" size="200,25" transparent="1"/>
			<widget name="ButtonRedText" position="275,351" size="200,25" zPosition="10" font="Regular;18" foregroundColor="#f0f0f0" transparent="1" />
		</screen>"""

	def __init__(self, session, selectedEntry, addEntry=False):
		self.skin = fstabEditorScreen.skin
		self.session = session
		self.selectedEntry = selectedEntry
		self.addEntry = addEntry
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)

		self["ButtonRed"] = Pixmap()
		self["ButtonRedText"] = Label(_("Remove entry"))
		self["save"] = Label(_("Save"))
		self["cansel"] = Label(_("Cancel"))
		
		if self.addEntry:
			self["ButtonRed"].hide()
			self["ButtonRedText"].hide()

		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
		{
			"green":	(self.checkEntry, _("Return with saving")),
			"red":		(self.removeEntry, _("Remove entry")),
		}, -1)

		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
		{
			"cancel":	(self.cancelEntry, _("Return without saving")),
			"ok":		(self.ok, _("Open selector")),
		}, -1)

		self.setTitle(_("fstab-Editor"))
		self.list = []
		ConfigListScreen.__init__(self, self.list)

		if 	self.addEntry:
			self.devicename = NoSave(ConfigText(default = ""))
			self.mountpoint = NoSave(ConfigText(default = ""))
			self.fstype = NoSave(ConfigSelection([("auto","auto"),("ext2","ext2"),("ext3","ext3"),("ext4","ext4"),("swap","swap"),("tmpfs","tmpfs"),("proc","proc"),("cifs","cifs"),("nfs","nfs"),("jffs2","jffs2"),("usbfs","usbfs"),("devpts","devpts"),("vfat","vfat"),("fat","fat"),("ntfs","ntfs"),("noauto", "no auto"), ("xfs", "xfs")], default = "auto"))
			self.options = NoSave(ConfigText(default = "defaults"))
			self.dumpfreq = NoSave(ConfigNumber(default = 0))
			self.passnum = NoSave(ConfigSelection([("0","0"),("1","1"),("2","2")], default = "0"))
		else:
			self.devicename = NoSave(ConfigText(default = entryList[self.selectedEntry][0]))
			self.mountpoint = NoSave(ConfigText(default = entryList[self.selectedEntry][1]))
			self.fstype = NoSave(ConfigSelection([("auto","auto"),("ext2","ext2"),("ext3","ext3"),("ext4","ext4"),("swap","swap"),("tmpfs","tmpfs"),("proc","proc"),("cifs","cifs"),("nfs","nfs"),("jffs2","jffs2"),("usbfs","usbfs"),("devpts","devpts"),("vfat","vfat"),("fat","fat"),("ntfs","ntfs"),("noauto", "no auto"), ("xfs", "xfs")], default = entryList[self.selectedEntry][2]))
			self.options = NoSave(ConfigText(default = entryList[self.selectedEntry][3]))
			self.dumpfreq = NoSave(ConfigNumber(default = int(entryList[self.selectedEntry][4])))
			self.passnum = NoSave(ConfigSelection([("0","0"),("1","1"),("2","2")], default = entryList[self.selectedEntry][5]))
		
		self.list.append(getConfigListEntry(_("device name: "), self.devicename))
		self.list.append(getConfigListEntry(_("mount point: "), self.mountpoint))
		self.list.append(getConfigListEntry(_("file system type: "), self.fstype))
		self.list.append(getConfigListEntry(_("options: "), self.options))
		self.list.append(getConfigListEntry(_("dump frequency (in days): "), self.dumpfreq))
		self.list.append(getConfigListEntry(_("pass num: "), self.passnum))

		self["config"].setList(self.list)
	
	def checkEntry(self):
		if self.devicename.value == "" or self.mountpoint.value == "":
			error = self.session.open(MessageBox, _("Please enter a value for every input field!"), MessageBox.TYPE_ERROR, timeout=6)
		else:
			self.saveEntry()

	def saveEntry(self):
		global entryList, lengthList
		#check if new entry is longer than the currently longest
		if len(self.devicename.value) > lengthList[0]:
			lengthList[0] = len(self.devicename.value)
		if len(self.mountpoint.value) > lengthList[1]:
			lengthList[1] = len(self.mountpoint.value)
		if len(self.fstype.value) > lengthList[2]:
			lengthList[2] = len(self.fstype.value)
		if len(self.options.value) > lengthList[3]:
			lengthList[3] = len(self.options.value)
		if self.addEntry:
			entryList.append([self.devicename.value, self.mountpoint.value, self.fstype.value, self.options.value, str(self.dumpfreq.value), self.passnum.value])
		else:
			entryList[self.selectedEntry] = [self.devicename.value, self.mountpoint.value, self.fstype.value, self.options.value, str(self.dumpfreq.value), self.passnum.value]
		self.close(1)

	def removeEntry(self):
		if not self.addEntry:
			global entryList
			del entryList[self.selectedEntry]
			self.close(1)

	def cancelEntry(self):
		self.close(0)
	
	def ok(self):
		self.selectedEntry = self["config"].getCurrentIndex()
		if self.selectedEntry == 1:
			self.session.openWithCallback(self.dirSelectDlgClosed, dirSelectDlg, "/media/dummy/", False)  # just add any (not even existing) subdir to start in /media
		elif self.selectedEntry == 0:
			self.session.openWithCallback(self.dirSelectDlgClosed, dirSelectDlg, "/dev/dummy/", True) # just add any (not even existing) subdir to start in /dev
	
	def dirSelectDlgClosed(self, mountpoint):
		print "mountpoint: ", mountpoint
		if mountpoint != False:
			if self.selectedEntry == 1:
				self.mountpoint.value = mountpoint
			elif self.selectedEntry == 0:
				self.devicename.value = mountpoint