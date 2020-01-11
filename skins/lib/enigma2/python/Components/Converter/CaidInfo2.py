#
#  CaidInfo2 - Converter
#
#  ver 0.8 04/07/2012
#
#  Coded by bigroma  & 2boom

from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService
from Tools.Directories import fileExists
from Components.Element import cached
from Poll import Poll
import os

info = {}
old_ecm_mtime = None

class CaidInfo2(Poll, Converter, object):
	CAID = 0
	PID = 1
	PROV = 2
	ALL = 3
	IS_NET = 4
	IS_EMU = 5
	CRYPT = 6
	BETA = 7
	CONAX = 8
	CRW = 9
	DRE = 10
	IRD = 11
	NAGRA = 12
	NDS = 13
	SECA = 14
	VIA = 15
	BETA_C = 16
	CONAX_C = 17
	CRW_C = 18
	DRE_C = 19
	IRD_C = 20
	NAGRA_C = 21
	NDS_C = 22
	SECA_C = 23
	VIA_C = 24
	BISS = 25
	BISS_C = 26
	HOST = 27
	DELAY = 28
	FORMAT = 29
	CRYPT2 = 30
	my_interval = 1000


	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		if type == "CAID":
			self.type = self.CAID
		elif type == "PID":
			self.type = self.PID
		elif type == "ProvID":
			self.type = self.PROV
		elif type == "Delay":
			self.type = self.DELAY
		elif type == "Host":
			self.type = self.HOST
		elif type == "Net":
			self.type = self.IS_NET
		elif type == "Emu":
			self.type = self.IS_EMU
		elif type == "CryptInfo":
			self.type = self.CRYPT
		elif type == "CryptInfo2":
			self.type = self.CRYPT2
		elif type == "BetaCrypt":
			self.type = self.BETA
		elif type == "ConaxCrypt":
			self.type = self.CONAX
		elif type == "CrwCrypt":
			self.type = self.CRW
		elif type == "DreamCrypt":
			self.type = self.DRE
		elif type == "IrdCrypt":
			self.type = self.IRD
		elif type == "NagraCrypt":
			self.type = self.NAGRA
		elif type == "NdsCrypt":
			self.type = self.NDS
		elif type == "SecaCrypt":
			self.type = self.SECA
		elif type == "ViaCrypt":
			self.type = self.VIA
		elif type == "BetaEcm":
			self.type = self.BETA_C
		elif type == "ConaxEcm":
			self.type = self.CONAX_C
		elif type == "CrwEcm":
			self.type = self.CRW_C
		elif type == "DreamEcm":
			self.type = self.DRE_C
		elif type == "IrdEcm":
			self.type = self.IRD_C
		elif type == "NagraEcm":
			self.type = self.NAGRA_C
		elif type == "NdsEcm":
			self.type = self.NDS_C
		elif type == "SecaEcm":
			self.type = self.SECA_C
		elif type == "ViaEcm":
			self.type = self.VIA_C
		elif type == "BisCrypt":
			self.type = self.BISS
		elif type == "BisEcm":
			self.type = self.BISS_C
		elif type == "Default" or type == "" or type == None or type == "%":
			self.type = self.ALL
		else:
			self.type = self.FORMAT
			self.sfmt = type[:]

		self.systemTxtCaids = {
			"26" : "BiSS",
			"01" : "Seca Mediaguard",
			"06" : "Irdeto",
			"17" : "BetaCrypt",
			"05" : "Viacces",
			"18" : "Nagravision",
			"09" : "NDS-Videoguard",
			"0B" : "Conax",
			"0D" : "Cryptoworks",
			"4A" : "DRE-Crypt",
			"0E" : "PowerVu",
			"22" : "Codicrypt",
			"07" : "DigiCipher",
			"56" : "Verimatrix",
			"A1" : "Rosscrypt"}

		self.systemCaids = {
			"26" : "BiSS",
			"01" : "SEC",
			"06" : "IRD",
			"17" : "BET",
			"05" : "VIA",
			"18" : "NAG",
			"09" : "NDS",
			"0B" : "CON",
			"0D" : "CRW",
			"4A" : "DRE" }


	@cached
	def getBoolean(self):

		service = self.source.service
		info = service and service.info()
		if not info:
			return False

		caids = info.getInfoObject(iServiceInformation.sCAIDs)
		if caids:
			if self.type == self.SECA:
				for caid in caids:
					if ("%0.4X" % int(caid))[:2] == "01":
						return True
				return False
			if self.type == self.BETA:
				for caid in caids:
					if ("%0.4X" % int(caid))[:2] == "17":
						return True
				return False
			if self.type == self.CONAX:
				for caid in caids:
					if ("%0.4X" % int(caid))[:2] == "0B":
						return True
				return False
			if self.type == self.CRW:
				for caid in caids:
					if ("%0.4X" % int(caid))[:2] == "0D":
						return True
				return False
			if self.type == self.DRE:
				for caid in caids:
					if ("%0.4X" % int(caid))[:2] == "4A":
						return True
				return False
			if self.type == self.NAGRA:
				for caid in caids:
					if ("%0.4X" % int(caid))[:2] == "18":
						return True
				return False
			if self.type == self.NDS:
				for caid in caids:
					if ("%0.4X" % int(caid))[:2] == "09":
						return True
				return False
			if self.type == self.IRD:
				for caid in caids:
					if ("%0.4X" % int(caid))[:2] == "06":
						return True
				return False
			if self.type == self.VIA:
				for caid in caids:
					if ("%0.4X" % int(caid))[:2] == "05":
						return True
				return False
			if self.type == self.BISS:
				for caid in caids:
					if ("%0.4X" % int(caid))[:2] == "26":
						return True
				return False
			self.poll_interval = self.my_interval
			self.poll_enabled = True
			ecm_info = self.ecmfile()
			if ecm_info:
				caid = ("%0.4X" % int(ecm_info.get("caid", ""),16))[:2]
				if self.type == self.SECA_C:
					if caid == "01":
						return True
					return False
				if self.type == self.BETA_C:
					if caid == "17":
						return True
					return False
				if self.type == self.CONAX_C:
					if caid == "0B":
						return True
					return False
				if self.type == self.CRW_C:
					if caid == "0D":
						return True
					return False
				if self.type == self.DRE_C:
					if caid == "4A":
						return True
					return False
				if self.type == self.NAGRA_C:
					if caid == "18":
						return True
					return False
				if self.type == self.NDS_C:
					if caid == "09":
						return True
					return False
				if self.type == self.IRD_C:
					if caid == "06":
						return True
					return False
				if self.type == self.VIA_C:
					if caid == "05":
						return True
					return False
				if self.type == self.BISS_C:
					if caid == "26":
						return True
					return False
				#oscam
				reader = ecm_info.get("reader", None)
				#cccam	
				using = ecm_info.get("using", "")
				#mgcamd
				source = ecm_info.get("source", None)
				if self.type == self.IS_EMU:
					return using == "emu" or source == "emu" or reader == "emu"
				if self.type == self.IS_NET:
					if using == "CCcam-s2s":
						return 1
					else:
						return  (source != None and source != "emu") or (reader != None and reader != "emu")
				else:
					return False

		return False

	boolean = property(getBoolean)

	@cached
	def getText(self):
		textvalue = ""
		server = ""
		service = self.source.service
		if service:
			info = service and service.info()
			if info:
				if info.getInfoObject(iServiceInformation.sCAIDs):
					self.poll_interval = self.my_interval
					self.poll_enabled = True
					ecm_info = self.ecmfile()
					# crypt2
					if self.type == self.CRYPT2:
						if fileExists("/tmp/ecm.info"):
							try:
								caid = "%0.4X" % int(ecm_info.get("caid", ""),16)
								return "%s" % self.systemTxtCaids.get(caid[:2])
							except:
								return 'nondecode'
						else:
							return 'nondecode'
					if ecm_info:
						# caid
						caid = "%0.4X" % int(ecm_info.get("caid", ""),16)
						if self.type == self.CAID:
							return caid
						# crypt
						if self.type == self.CRYPT:
							return "%s" % self.systemTxtCaids.get(caid[:2])
						#pid
						try:
							pid = "%0.4X" % int(ecm_info.get("pid", ""),16)
						except:
							pid = ""
						if self.type == self.PID:
							return pid
						# oscam
						try:
							prov = "%0.6X" % int(ecm_info.get("prov", ""),16)
						except:
							prov = ecm_info.get("prov", "")
						if self.type == self.PROV:
							return prov
						ecm_time = ecm_info.get("ecm time", "")
						if self.type == self.DELAY:
							return ecm_time
						#protocol
						protocol = ecm_info.get("protocol", "")
						#port
						port = ecm_info.get("port", "")
						# source	
						source = ecm_info.get("source", "")
						# server
						server = ecm_info.get("server", "")
						# reader
						reader = ecm_info.get("reader", "")
						if self.type == self.HOST:
							return server
						if self.type == self.FORMAT:
							textvalue = ""
							params = self.sfmt.split(" ")
							for param in params:
								if param != '':
									if param[0] != '%':
										textvalue+=param
									#server
									elif param == '%S':
										textvalue+=server
									#port
									elif param == "%SP":
										textvalue+=port
									#protocol
									elif param == "%PR":
										textvalue+=protocol
									#caid
									elif param == "%C":
										textvalue+=caid
									#Pid
									elif param == "%P":
										textvalue+=pid
									#prov
									elif param == "%p":
										textvalue+=prov
									#sOurce
									elif param == "%O":
										textvalue+=source
									#Reader
									elif param == "%R":
										textvalue+=reader
									#ECM Time
									elif param == "%T":
										textvalue+=ecm_time
									elif param == "%t":
										textvalue+="\t"
									elif param == "%n":
										textvalue+="\n"
									elif param[1:].isdigit():
										textvalue=textvalue.ljust(len(textvalue)+int(param[1:]))
									if len(textvalue) > 0:
										if textvalue[-1] != "\t" and textvalue[-1] != "\n":
											textvalue+=" "
							return textvalue[:-1]
						if self.type == self.ALL:
							if source == "emu":
								textvalue = "%s - %s (Caid: %s)" % (source, self.systemTxtCaids.get(caid[:2]), caid)
							elif reader != "" and source == "net": 
								textvalue = "%s - Prov: %s, Caid: %s, Reader: %s, %s (%s) - %ss" % (source, prov, caid, reader, protocol, server, ecm_time)
							elif reader != "" and source != "net": 
								textvalue = "%s - Prov: %s, Caid: %s, Reader: %s, %s (local) - %ss" % (source, prov, caid, reader, protocol, ecm_time)
							elif server == "" and port == "": 
								textvalue = "%s - Prov: %s, Caid: %s %s - %s" % (source, prov, caid, protocol, ecm_time)
							else:
								try:
									textvalue = "%s - Prov: %s, Caid: %s, %s (%s:%s) - %s" % (source, prov, caid, protocol, server, port, ecm_time)
								except:
									pass
					else:
						if self.type == self.ALL or (self.type == self.FORMAT and (self.sfmt.count("%") > 3 )):
							textvalue = "No parse cannot emu"
				else:
					if self.type == self.ALL or (self.type == self.FORMAT and (self.sfmt.count("%") > 3 )):
						textvalue = "Free-to-air"
		return textvalue

	text = property(getText)

	def ecmfile(self):
		global info
		global old_ecm_mtime
		ecm = None
		service = self.source.service
		if service:
			try:
				ecm_mtime = os.stat("/tmp/ecm.info").st_mtime
				if not os.stat("/tmp/ecm.info").st_size > 0:
					info = {}
				if ecm_mtime == old_ecm_mtime:
					return info
				old_ecm_mtime = ecm_mtime
				ecmf = open("/tmp/ecm.info", "rb")
				ecm = ecmf.readlines()
			except:
				old_ecm_mtime = None
				info = {}
				return info

			if ecm:
				for line in ecm:
					x = line.lower().find("msec")
					#ecm time for mgcamd and oscam
					if x != -1:
						info["ecm time"] = line[0:x+4]
					else:
						item = line.split(":", 1)
						if len(item) > 1:
							#wicard block
							if item[0] == "Provider":
								item[0] = "prov"
								item[1] = item[1].strip()[2:]
							elif item[0] == "ECM PID":
								item[0] = "pid"
							elif item[0] == "response time":
								info["source"] = "net"
								it_tmp = item[1].strip().split(" ")
								info["ecm time"] = "%s msec" % it_tmp[0]
								y = it_tmp[-1].find('[')
								if y !=-1:
									info["server"] = it_tmp[-1][:y]
									info["protocol"] = it_tmp[-1][y+1:-1]
								item[0]="port"
								item[1] = ""
							elif item[0][:2] == 'cw'or item[0] =='ChID' or item[0] == "Service" \
							     or item[0] == "system" or item[0] == "hops" or item[0] == "provider":
								pass
							#mgcamd new_oscam block
							elif item[0] == "source":
								if item[1].strip()[:3] == "net":
									it_tmp = item[1].strip().split(" ")
									info["protocol"] = it_tmp[1][1:]
									info["server"] = it_tmp[-1].split(":",1)[0]
									info["port"] = it_tmp[-1].split(':',1)[1][:-1]
									item[1] = "net"
							elif item[0] == "prov":
								y = item[1].find(",")
								if y != -1:
									item[1] = item[1][:y]
							#old oscam block
							elif item[0] == "reader":
								if item[1].strip() == "emu":
									item[0] = "source"
							elif item[0] == "from":
								if item[1].strip() == "local":
									item[1] = "sci"
									item[0] = "source"
								else:
									info["source"] = "net"
									item[0] = "server"
							#cccam block
							elif item[0] == "provid":
								item[0] = "prov"
							elif item[0] == "using":
								if item[1].strip() == "emu" or item[1].strip() == "sci":
									item[0] = "source"
								else:
									info["source"] = "net"
									item[0] = "protocol"
							elif item[0] == "address":
								tt = item[1].find(":")
								if tt != -1:
									info["server"] = item[1][:tt].strip()
									item[0] = "port"
									item[1] = item[1][tt+1:]
							info[item[0].strip().lower()] = item[1].strip()
						else:
							if not info.has_key("caid"):
								x = line.lower().find("caid")
								if x != -1:
									y = line.find(",")
									if y != -1:
										info["caid"] = line[x+5:y]
							if not info.has_key("pid"):
								x = line.lower().find("pid")
								if x != -1:
									y = line.find(" =")
									if y != -1:
										info["pid"] = line[x+4:y]
				ecmf.close()
		return info

	def changed(self, what):
		Converter.changed(self, (self.CHANGED_POLL,))


