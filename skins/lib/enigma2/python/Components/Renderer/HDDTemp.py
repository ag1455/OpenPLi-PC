# -*- coding: utf-8 -*-
#    Temperature HDD Renderer for Enigma-2
#    Coded by Ligioner for VU+DUO (c)2011

from Components.VariableText import VariableText
from Components.Sensors import sensors
from Tools.HardwareInfo import HardwareInfo
from enigma import eLabel
from Renderer import Renderer
from os import popen

class HDDTemp(Renderer, VariableText):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		if "bm750" in HardwareInfo().get_device_name():
			self.ZeigeTemp = True
		else:
			self.ZeigeTemp = False
	GUI_WIDGET = eLabel
	def changed(self, what):
		if not self.suspended:
			if self.ZeigeTemp:
				maxtemp = 0
				try:
					templist = sensors.getSensorsList(sensors.TYPE_TEMPERATURE)
					tempcount = len(templist)
					for count in range(tempcount):
						id = templist[count]
						tt = sensors.getSensorValue(id)
						if tt > maxtemp:
							maxtemp = tt
				except:
					pass
				self.text = str(maxtemp) + " Temp. in °C"
			else:
				loada = 0
				try:
					out_line = popen("hddtemp -n -q /dev/sda").readline()
					loada = out_line[:4]	
				except:
					pass
				self.text = loada 

	def onShow(self):
		self.suspended = False
		self.changed(None)

	def onHide(self):
		self.suspended = True
