# CalendarToText
# Coded by Sirius

from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config, getConfigListEntry, configfile
from Poll import Poll
from time import localtime
import os

class CalendarToText(Poll, Converter, object):

	FORMAT = 0
	FULL = 1
	DATE = 2
	DATEPEOPLE = 3
	SIGN = 4
	HOLIDAY = 5
	DESCRIPTION = 6
	PICON = 7

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_interval = 2000
		self.poll_enabled = True

		if type == "Format":
			self.type = self.FORMAT
		elif type == "Full":
			self.type = self.FULL
		elif type == "Date":
			self.type = self.DATE
		elif type == "Datepeople":
			self.type = self.DATEPEOPLE
		elif type == "Sign":
			self.type = self.SIGN
		elif type == "Holiday":
			self.type = self.HOLIDAY
		elif type == "Description":
			self.type = self.DESCRIPTION
		elif type == "Picon":
			self.type = self.PICON

	@cached

	def getText(self):
		self.year = localtime()[0]
		self.month = localtime()[1]
		self.day = localtime()[2]
		self.language = config.osd.language.value.split("_")[0].strip()

		text = ""
		if self.type == self.FORMAT:
			text = "%s %s %s" % (self.txtdate(), self.txtpeople(), self.txtholiday())
		elif self.type == self.FULL:
			text = "%s \n %s \n %s \n %s" % (self.datepeople(), self.holiday(), self.sign(), self.description())
		elif self.type == self.DATE:
			text = self.date()
		elif self.type == self.DATEPEOPLE:
			text = self.datepeople()
		elif self.type == self.SIGN:
			text = self.sign()
		elif self.type == self.HOLIDAY:
			text = self.holiday()
		elif self.type == self.DESCRIPTION:
			text = self.description()
		elif self.type == self.PICON:
			text = "%s (%s)" % (self.month, self.day)
		return text

	def txtdate(self):
		date = "no info"
		info = ""
		try:
			line = open("/usr/lib/enigma2/python/Plugins/Extensions/Calendar/base/%s/day/m%sd%s.txt" % (self.language, self.month, self.day), "r").readlines()[0]
			info += line.split(":")[1].strip()
			date = info
		except:
			pass
		return date

	def txtpeople(self):
		datepeople = "no info"
		info = ""
		try:
			line = open("/usr/lib/enigma2/python/Plugins/Extensions/Calendar/base/%s/day/m%sd%s.txt" % (self.language, self.month, self.day), "r").readlines()[1]
			info += line.split(":")[1].strip()
			datepeople = info
		except:
			pass
		return datepeople

	def txtholiday(self):
		holiday = "no info"
		info = ""
		try:
			line = open("/usr/lib/enigma2/python/Plugins/Extensions/Calendar/base/%s/day/m%sd%s.txt" % (self.language, self.month, self.day), "r").readlines()[3]
			info += line.split(":")[1].strip()
			holiday = info
		except:
			pass
		return holiday

	def date(self):
		date = "no info"
		info = ""
		try:
			line = open("/usr/lib/enigma2/python/Plugins/Extensions/Calendar/base/%s/day/m%sd%s.txt" % (self.language, self.month, self.day), "r").readlines()[0]
			info += line.strip()
			date = info
		except:
			pass
		return date

	def datepeople(self):
		datepeople = "no info"
		info = ""
		try:
			line = open("/usr/lib/enigma2/python/Plugins/Extensions/Calendar/base/%s/day/m%sd%s.txt" % (self.language, self.month, self.day), "r").readlines()[1]
			info += line.strip()
			datepeople = info
		except:
			pass
		return datepeople

	def sign(self):
		sign = "no info"
		info = ""
		try:
			line = open("/usr/lib/enigma2/python/Plugins/Extensions/Calendar/base/%s/day/m%sd%s.txt" % (self.language, self.month, self.day), "r").readlines()[2]
			info += line.strip()
			sign = info
		except:
			pass
		return sign

	def holiday(self):
		holiday = "no info"
		info = ""
		try:
			line = open("/usr/lib/enigma2/python/Plugins/Extensions/Calendar/base/%s/day/m%sd%s.txt" % (self.language, self.month, self.day), "r").readlines()[3]
			info += line.strip()
			holiday = info
		except:
			pass
		return holiday

	def description(self):
		description = "no info"
		info = ""
		try:
			line = open("/usr/lib/enigma2/python/Plugins/Extensions/Calendar/base/%s/day/m%sd%s.txt" % (self.language, self.month, self.day), "r").readlines()[4]
			info += line.strip()
			description = info
		except:
			pass
		return description

	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)