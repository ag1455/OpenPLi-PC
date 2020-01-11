# joergm6@IHAD V.05r0 28.01.2011
 
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Sensors import sensors
from time import strftime

class Sensors(Converter, object):
	RPM = 0
	RPMfull = 1
	RPM2000 = 2
	RPM3000 = 3
	RPM4000 = 4
	TEMPMAX = 5
	TEMPMAXfull = 6
	TEMPMAX55 = 7
	RPMTEMPMAX = 8
	RPMTEMPMAXfull = 9
	RPMTEMPMAXCfull = 10

	def __init__(self, type):
		Converter.__init__(self, type)
		self.wert = type.split(":")
		if self.wert[0] == "FanRPM":
			self.type = self.RPM
		elif self.wert[0] == "FanRPMfull":
			self.type = self.RPMfull
		elif self.wert[0] == "FanRPM2000":
			self.type = self.RPM2000
		elif self.wert[0] == "FanRPM3000":
			self.type = self.RPM3000
		elif self.wert[0] == "FanRPM4000":
			self.type = self.RPM4000
		elif self.wert[0] == "TempMAX":
			self.type = self.TEMPMAX
		elif self.wert[0] == "TempMAXfull":
			self.type = self.TEMPMAXfull
		elif self.wert[0] == "TempMAX55":
			self.type = self.TEMPMAX55
		elif self.wert[0] == "FanRPMTempMAX":
			self.type = self.RPMTEMPMAX
		elif self.wert[0] == "FanRPMTempMAXfull":
			self.type = self.RPMTEMPMAXfull
		elif self.wert[0] == "FanRPMTempMAXCfull":
			self.type = self.RPMTEMPMAXCfull
		else:
			self.type = self.RPM

	def getTempMax(self):
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
		return maxtemp

	def getFanRPM(self):
		tt = 0
		try:
			templist = sensors.getSensorsList(sensors.TYPE_FAN_RPM)
			id = templist[0]
			tt = sensors.getSensorValue(id)
		except:
			pass
		return tt/2

	@cached
	def getText(self):
		self.w1 = 2
		self.w2 = ""
		if len(self.wert)>1:
			if int(self.wert[1])>0:
				self.w1 = int(self.wert[1])
		if len(self.wert)>2:
			self.w2 = self.wert[2].replace(";",":").replace("_"," ")
		if self.type == self.RPMTEMPMAX:
			if (int(strftime("%S")) / self.w1) % 2 == 0:
				rpm = self.getFanRPM()
				return str(rpm)
			else:
				tmp = self.getTempMax()
				return str(tmp)
		elif self.type == self.RPMTEMPMAXfull:
			if (int(strftime("%S")) / self.w1) % 2 == 0:
				rpm = self.getFanRPM()
				return str(rpm) + " rpm"
			else:
				tmp = self.getTempMax()
				return str(tmp) + "°C"
		elif self.type == self.RPMTEMPMAXCfull:
			if (int(strftime("%S")) / self.w1) % 2 == 0:
				rpm = self.getFanRPM()
				return str(rpm)
			else:
				tmp = self.getTempMax()
				return str(tmp) + "°C"
		elif self.type == self.RPM:
			rpm = self.getFanRPM()
			return self.w2 + str(rpm)
		elif self.type == self.RPMfull:
			rpm = self.getFanRPM()
			return self.w2 + str(rpm) + " rpm"
		elif self.type == self.TEMPMAX:
			tmp = self.getTempMax()
			return self.w2 + str(tmp)
		elif self.type == self.TEMPMAXfull:
			tmp = self.getTempMax()
			return self.w2 + str(tmp) + "°C"
		else:
			return ""

	@cached
	def getValue(self):
		if self.wert[0][:6] == "FanRPM":
			self.w1 = 500
			self.w2 = 2000
			if len(self.wert)>1:
				if int(self.wert[1])>0 :
					self.w1 = int(self.wert[1])
			if len(self.wert)>2:
				if int(self.wert[2])>0 :
					self.w2 = int(self.wert[2])
			if self.type == self.RPM2000:
				self.w2 = 2000
			elif self.type == self.RPM3000:
				self.w2 = 3000
			elif self.type == self.RPM4000:
				self.w2 = 4000
			tmp = (self.getFanRPM()-self.w1)*100/(self.w2-self.w1)
		elif self.wert[0][:7] == "TempMAX":
			self.w1 = 30
			self.w2 = 55
			if len(self.wert)>1:
				if int(self.wert[1])>0 :
					self.w1 = int(self.wert[1])
			if len(self.wert)>2:
				if int(self.wert[2])>0 :
					self.w2 = int(self.wert[2])
			tmp = (self.getTempMax()-self.w1)*100/(self.w2-self.w1)
		else:
			tmp = 0
		if tmp < 0:
			tmp = 0
		if tmp > 100:
			tmp = 100
		return tmp

	range = 100
	text = property(getText)
	value = property(getValue)
