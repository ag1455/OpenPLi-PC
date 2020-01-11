# 2boom 2011-13
#  CamdInfo3 - Converter
# <widget source="session.CurrentService" render="Label" position="189,397" zPosition="4" size="350,20" noWrap="1" valign="center" halign="center" font="Regular;14" foregroundColor="clText" transparent="1"  backgroundColor="#20002450">
#	<convert type="CamdInfo">Camd</convert>
# </widget>			

from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigText, ConfigPassword, ConfigClock, ConfigSelection, ConfigSubsection, ConfigYesNo, configfile, NoSave
from Components.Element import cached
from Tools.Directories import fileExists
from Poll import Poll
import os


class CamdInfo3(Poll, Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_interval = 2000
		self.poll_enabled = True
		
	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		camd = ""
		serlist = None
		camdlist = None
		nameemu = []
		nameser = []
		if not info:
			return ""
		# TS-Panel
		if fileExists("/etc/startcam.sh"):
			try:
				for line in open("/etc/startcam.sh"):
					if line.find("script") > -1:
						return "%s" % line.split("/")[-1].split()[0][:-3]
			except:
				camdlist = None
		# domica 8120
		elif fileExists("/etc/init.d/cam"):
			for line in open("/etc/enigma2/settings"):
				if line.find("config.plugins.emuman.cam") > -1:
					return line.split("=")[-1].strip('\n')
		#PKT
		elif fileExists("//usr/lib/enigma2/python/Plugins/Extensions/PKT/plugin.pyo"):
			for line in open("/etc/enigma2/settings"):
				if line.find("config.plugins.emuman.cam=") > -1:
					return line.split("=")[-1].strip('\n')
		#HDMU
		elif fileExists("/etc/.emustart") and fileExists("/etc/image-version"):
			try:
				for line in open("/etc/.emustart"):
					return line.split()[0].split('/')[-1]
			except:
				return None
		
		# AAF & ATV & VTI 
		elif fileExists("/etc/image-version") and not fileExists("/etc/.emustart"):
			emu = ""
			server = ""
			for line in open("/etc/image-version"):
				if line.find("=AAF") > -1 or line.find("=openATV") > -1:
					for line in open("/etc/enigma2/settings"):
						if line.find("config.softcam.actCam=") > -1:
							emu = line.split("=")[-1].strip('\n')
						if line.find("config.softcam.actCam2=") > -1:
							server = line.split("=")[-1].strip('\n')
							if server.find("no CAM 2 active") > -1:
								server = ""
				elif line.find("=vuplus") > -1:
					if fileExists("/tmp/.emu.info"):
						for line in open("/tmp/.emu.info"):
							emu = line.strip('\n')
			return "%s %s" % (emu, server)
		# BlackHole	
		elif fileExists("/etc/CurrentBhCamName"):
			try:
				camdlist = open("/etc/CurrentBhCamName", "r")
			except:
				return None
		# Domica	
		elif fileExists("/etc/active_emu.list"):
			try:
				camdlist = open("/etc/active_emu.list", "r")
			except:
				return None
		# Egami	
		elif fileExists("/tmp/egami.inf","r"):
			lines = open("/tmp/egami.inf", "r").readlines()
			for line in lines:
				item = line.split(":",1)
				if item[0] == "Current emulator":
					return item[1].strip()
		#Pli
		elif fileExists("/etc/init.d/softcam") or fileExists("/etc/init.d/cardserver"):
			try:
				for line in open("/etc/init.d/softcam"):
					if line.find("echo") > -1:
						nameemu.append(line)
				camdlist = "%s" % nameemu[1].split('"')[1]
			except:
				pass
			try:
				for line in open("/etc/init.d/cardserver"):
					if line.find("echo") > -1:
						nameser.append(line)
				serlist = "%s" % nameser[1].split('"')[1]
			except:
				pass
			if serlist is None:
				serlist = ""
			elif camdlist is None:
				camdlist = ""
			elif serlist is None and camdlist is None:
				serlist = ""
				camdlist = ""
			return ("%s %s" % (serlist, camdlist))
		# OoZooN
		elif fileExists("/tmp/cam.info"):
			try:
				camdlist = open("/tmp/cam.info", "r")
			except:
				return None
		# Merlin2	
		elif fileExists("/etc/clist.list"):
			try:
				camdlist = open("/etc/clist.list", "r")
			except:
				return None
		# GP3
		elif fileExists("/usr/lib/enigma2/python/Plugins/Bp/geminimain/lib/libgeminimain.so"):
			try:
				from Plugins.Bp.geminimain.plugin import GETCAMDLIST
				from Plugins.Bp.geminimain.lib import libgeminimain
				camdl = libgeminimain.getPyList(GETCAMDLIST)
				cam = None
				for x in camdl:
					if x[1] == 1:
						cam = x[2] 
				return cam
		   	except:
				return None
		else:
			return None
			
		if serlist is not None:
			try:
				cardserver = ""
				for current in serlist.readlines():
					cardserver = current
				serlist.close()
			except:
				pass
		else:
			cardserver = " "

		if camdlist is not None:
			try:
				emu = ""
				for current in camdlist.readlines():
					emu = current
				camdlist.close()
			except:
				pass
		else:
			emu = " "
			
		return "%s %s" % (cardserver.split('\n')[0], emu.split('\n')[0])
		
	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)
