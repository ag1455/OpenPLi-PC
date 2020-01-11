# Test example by vlamo@ukr.net 06.06.2010 16:56 version 0.7
# Translate add by Michael Grigorev <sleuthhound@gmail.com> 16.07.2010 14:15 version 0.8
########################################################################################

import os,gettext

def _(txt):
	t = gettext.dgettext("xModem", txt)
	if t == txt:
		print "[xModem] fallback to default translation for", txt
		t = gettext.gettext(txt)
	return t

def getDefaultGateway():
	f = open("/proc/net/route", "r")
	if f:
		for line in f.readlines():
			tokens = line.split('\t')
			if tokens[1] == '00000000': #dest 0.0.0.0
				return int(tokens[2], 16)
	return None

def setOptionFile(file, txt):
	system("echo \"\" >%s" % file)
	system("chmod 644 %s" % file)
	f = open(file, "r+")
	if f:
		f.write(txt)

def setChatFile(file, txt):
	system("echo \"\" >%s" % file)
	system("chmod 755 %s" % file)
	f = open(file, "r+")
	if f:
		f.write(txt)


from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from enigma import eConsoleAppContainer, eTimer
from Components.Label import Label
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigSelection, getConfigListEntry, ConfigInteger, ConfigYesNo, ConfigText, ConfigPassword, ConfigIP, KEY_LEFT, KEY_RIGHT, KEY_0, KEY_DELETE, KEY_BACKSPACE
from Components.ActionMap import NumberActionMap, ActionMap
from Tools.Directories import copyfile, fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_SYSETC
from os import system
from time import time as getTime
#from Components.Network import iNetwork
from re import compile as re_compile, search as re_search
from Components.Sources.Boolean import Boolean

def setAltDNS():
	if not fileExists("/etc/ppp/resolv.conf.xmodem"):
		return
	system("grep -v '^nameserver' /etc/ppp/resolv.conf.xmodem >/etc/resolv.conf")
	dns1 = '.'.join(["%d" % d for d in config.plugins.xModem.dns1.value])
	dns2 = '.'.join(["%d" % d for d in config.plugins.xModem.dns2.value])
	dns = 'nameserver ' + dns1 + '\nnameserver ' + dns2 + '\n'
	f = open("/etc/resolv.conf", "r+")
	if f:
		f.seek(0,2)
		f.write(dns)

def restoreDNS():
	if fileExists("/etc/ppp/resolv.conf.xmodem"):
		system("mv /etc/ppp/resolv.conf.xmodem /etc/resolv.conf")


def setOptions():
	if config.plugins.xModem.altdns.value:
		usepeerdns = ''
	else:
		usepeerdns = 'usepeerdns\n'

	if config.plugins.xModem.standard.value == "0": # internal (builtin) modem
		username = config.plugins.xModem.imod.username.value
		password = config.plugins.xModem.imod.password.value
		options = config.plugins.xModem.imod.port.value + '\n'
		options += '%d\n' % config.plugins.xModem.imod.speed.value
		options += 'mtu %d\n' % config.plugins.xModem.imod.mtu.value
		options += 'mru %d\n' % config.plugins.xModem.imod.mru.value
		options += 'nocrtscts\nnocdtrcts\nlocal\nlock\ndefaultroute\nasyncmap 0\n'
		options += config.plugins.xModem.imod.pppopt.value + '\n'
		options += usepeerdns
		options += 'user \'' + username + '\'\n'
		options += 'password \'' + password + '\'\n'
		options += 'connect \'/etc/ppp/connect.chat.xmodem "' + config.plugins.xModem.imod.number.value + '"\'\n'
		options += 'disconnect /etc/ppp/disconnect.chat.xmodem\n'
	elif config.plugins.xModem.standard.value == "1": # gprs/edge/umts/hsdpa modem
		if config.plugins.xModem.gprs.numbersel.value == True:
			if config.plugins.xModem.gprs.numbers.value == "3":
				gprs_number = '#777'
			elif config.plugins.xModem.gprs.numbers.value == "2":
				gprs_number = '*99**1*1#'
			elif config.plugins.xModem.gprs.numbers.value == "1":
				gprs_number = '*99***1#'
			else:
				gprs_number = '*99#'
		else:
			gprs_number = config.plugins.xModem.gprs.number.value
		username = config.plugins.xModem.gprs.username.value
		password = config.plugins.xModem.gprs.password.value
		options = config.plugins.xModem.gprs.port.value + '\n'
		options += '%d\n' % config.plugins.xModem.gprs.speed.value
		options += 'mtu %d\n' % config.plugins.xModem.gprs.mtu.value
		options += 'mru %d\n' % config.plugins.xModem.gprs.mru.value
		options += 'debug\ncrtscts\nnoipdefault\nipcp-accept-local\nlcp-echo-interval 60\nlcp-echo-failure 5\ndefaultroute\nnoauth\nmaxfail 2\n'
		options += config.plugins.xModem.gprs.pppopt.value + '\n'
		options += usepeerdns
		options += 'user \'' + username + '\'\n'
		options += 'password \'' + password + '\'\n'
		options += 'connect \'/etc/ppp/connect.chat.xmodem "' + gprs_number + '"\'\n'
		options += 'disconnect /etc/ppp/disconnect.chat.xmodem\n'
	else: # cdma/evdo modem
		if config.plugins.xModem.cdma.numbersel.value == True:
			if config.plugins.xModem.cdma.numbers.value == "3":
				cdma_number = '#777'
			elif config.plugins.xModem.cdma.numbers.value == "2":
				cdma_number = '*99**1*1#'
			elif config.plugins.xModem.cdma.numbers.value == "1":
				cdma_number = '*99***1#'
			else:
				cdma_number = '*99#'
		else:
			cdma_number = config.plugins.xModem.cdma.number.value
		username = config.plugins.xModem.cdma.username.value
		password = config.plugins.xModem.cdma.password.value
		options = config.plugins.xModem.cdma.port.value + '\n'
		options += '%d\n' % config.plugins.xModem.cdma.speed.value
		options += 'mtu %d\n' % config.plugins.xModem.cdma.mtu.value
		options += 'mru %d\n' % config.plugins.xModem.cdma.mru.value
		options += 'debug\ncrtscts\nnoipdefault\nipcp-accept-local\nlcp-echo-interval 60\nlcp-echo-failure 5\ndefaultroute\nnoauth\nmaxfail 2\n'
		options += config.plugins.xModem.cdma.pppopt.value + '\n'
		options += usepeerdns
		options += 'user \'' + username + '\'\n'
		options += 'password \'' + password + '\'\n'
		options += 'connect \'/etc/ppp/connect.chat.xmodem "' + cdma_number + '"\'\n'
		options += 'disconnect /etc/ppp/disconnect.chat.xmodem\n'
	return options

def setChats(init = True):
	if init:
		chatstr = '#!/bin/sh\n\nif [ $# -lt 1 ]; then\n\techo "$0: no phone number given." >&2\n\texit -1\nfi\n\nPHONENUM=$1\n\nchat -v -e \\\n'
	else:
		chatstr = '#!/bin/sh\n\nchat "" "'
	if config.plugins.xModem.standard.value == "0": # internal (builtin) modem
		if init:
			chatstr += 'ABORT "N" \\\nABORT "n" \\\n'
			if config.plugins.xModem.imod.initstr.value:
				chatstr += '""\t"' + config.plugins.xModem.imod.initstr.value + '" \\\n'
			else:
				chatstr += '""\t"ATZ" \\\n'
			chatstr += '"O"\t"ATD${PHONENUM}" \\\n"c"\t\n'
		else:
			if config.plugins.xModem.imod.deinstr.value:
				chatstr += config.plugins.xModem.imod.deinstr.value + '"\n'
			else:
				chatstr += '\\d\\d+\\p+\\p+\\c" "" "\\d\\dATH0"\n'
	elif config.plugins.xModem.standard.value == "1": # gprs/edge/umts/hsdpa modem
		if init:
			if config.plugins.xModem.gprs.initstr.value:
				chatstr += '""\t"ATZ" \\\n'
				chatstr += '""\t"' + config.plugins.xModem.gprs.initstr.value + '" \\\n'
			else:
				chatstr += '""\t"ATZ" \\\n'
			if config.plugins.xModem.gprs.pincode.value:
				chatstr += '""\t\'AT+CPIN="' + config.plugins.xModem.gprs.pincode.value + '"\' \\\n'
			else:
				print("No PIN Code")
			chatstr += '"OK"\t\'AT+CGDCONT=1,"IP","' + config.plugins.xModem.gprs.apn.value + '"\' \\\n'
			chatstr += '"OK"\t"ATD${PHONENUM}" \\\n"CONNECT"\t""\n'
		else:
			if config.plugins.xModem.gprs.deinstr.value:
				chatstr += config.plugins.xModem.gprs.deinstr.value + '"\n'
			else:
				chatstr += '\\d\\d+\\p+\\p+\\c" "" "\\d\\dATH"\n'
	else: # cdma/evdo modem
		if init:
			if config.plugins.xModem.cdma.initstr.value:
				chatstr += '""\t"' + config.plugins.xModem.cdma.initstr.value + '"\\\n'
			else:
				chatstr += '""\t"ATZ" \\\n'
			chatstr += '"OK"\t"ATD${PHONENUM}" \\\n"CONNECT"\t""\n'
		else:
			if config.plugins.xModem.cdma.deinstr.value:
				chatstr += config.plugins.xModem.cdma.deinstr.value + '"\n'
			else:
				chatstr += '\\d\\d+\\p+\\p+\\c" "" "\\d\\dATH"\n'
		
	return chatstr

def doConnect():
	global gateway
	gateway = getDefaultGateway()
	system("route del default")
	system("modprobe ppp_async");

	if config.plugins.xModem.standard.value == "1": # gprs/edge/umts/hsdpa modem
		vendor = config.plugins.xModem.gprs.vendid.value
		product = config.plugins.xModem.gprs.prodid.value
		zerocdargs = config.plugins.xModem.gprs.zerocd.value
	elif config.plugins.xModem.standard.value == "2": # cdma/evdo modem
		vendor = config.plugins.xModem.cdma.vendid.value
		product = config.plugins.xModem.cdma.prodid.value
		zerocdargs = config.plugins.xModem.cdma.zerocd.value
	elif config.plugins.xModem.standard.value == "3": # use peers file
		vendor = config.plugins.xModem.peer.vendid.value
		product = config.plugins.xModem.peer.prodid.value
		zerocdargs = config.plugins.xModem.peer.zerocd.value
	else:
		vendor = ''
		product = ''
		zerocdargs = ''

	system("usb_modeswitch %s" % zerocdargs)

	if vendor and product:
		system("modprobe usbserial vendor=0x%s product=0x%s" % (vendor, product))
	else:
		system("modprobe usbserial")
	system("modprobe pl2303")
	system("modprobe cdc_acm")
	if config.plugins.xModem.altdns.value:
		system("rm -f /etc/ppp/resolv.conf.xmodem")
		system("cp /etc/resolv.conf /etc/ppp/resolv.conf.xmodem")

def pppdClosed(ret):
	global gateway
	print "modem disconnected", ret
	if gateway:
		#FIXMEEE... hardcoded for little endian!!
		system("route add default gw %d.%d.%d.%d" %(gateway&0xFF, (gateway>>8)&0xFF, (gateway>>16)&0xFF, (gateway>>24)&0xFF))
	if config.plugins.xModem.altdns.value:
		restoreDNS()
	if config.plugins.xModem.autorun.value:
		system("echo -e \"`date` : stop execute pppd [exit code = %d]\\n\" >>/tmp/autorun.tmp" % ret)

def dataAvail(text):
	global conn
	global connected
	global dialstate
	global starttime
	if text.find("Serial connection established") != -1:
		dialstate = LOGGING
	if text.find("AP authentication succeeded") != -1 or text.find("No auth is possible") != -1:
		dialstate = CONNECTING
	if text.find("ip-up finished") != -1:
		starttime = getTime()
		dialstate = CONNECTED
		connected = True
		system("echo \"`date` : pppd: ip-up finished\" >>/tmp/autorun.tmp")
		if config.plugins.xModem.altdns.value:
			setAltDNS()
	if text.find("Connect script failed") != -1:
		dialstate = NONE
		system("echo \"`date` : pppd: connect script failed\" >>/tmp/autorun.tmp")
		conn.sendCtrlC()
	#if text.find("Connection terminated") != -1:
	if text.find("ip-down finished") != -1:
		dialstate = NONE
		conn.sendCtrlC()
		connected = False
		starttime = None
		system("echo \"`date` : pppd: connection terminated\" >>/tmp/autorun.tmp")

def StartConnect(autorun=False):
	global conn
	global dialstate
	if autorun == True and config.plugins.xModem.autorun.value == False:
		return -1

	if autorun:
		print "starting xModem autorun pppd"
		system("echo \"`date` : start execute pppd\" >>/tmp/autorun.tmp")
	print "start execute pppd"
	doConnect()

	dialstate = DIALING
	if config.plugins.xModem.standard.value == "3": # use peers file
		ret = conn.execute("pppd", "pppd", "-d", "-detach", "call", config.plugins.xModem.peer.file.value)
	else:
		setOptionFile("/etc/ppp/options.xmodem", setOptions())
		setChatFile("/etc/ppp/connect.chat.xmodem", setChats(True))
		setChatFile("/etc/ppp/disconnect.chat.xmodem", setChats(False))
		ret = conn.execute("pppd", "pppd", "-d", "-detach", "file", "/etc/ppp/options.xmodem")

	if ret:
		print "execute pppd failed!"
		dialstate = NONE
		if autorun:
			pppdClosed(ret)
			system("echo \"`date` : pppd execute failed\" >>/tmp/autorun.tmp")
	if autorun:
		system("echo \"`date` : pppd return = %d\" >>/tmp/autorun.tmp" % ret)
	return ret

def StopConnect(autorun=False):
	global conn
	global connected
	global dialstate
	global starttime
	if autorun:
		print "stopping xModem autorun pppd"
	print "stop execute pppd"
	conn.sendCtrlC()
	connected = False
	dialstate = NONE
	starttime = None


NONE = 0

CONNECT = 1
ABORT = 2
DISCONNECT = 3

DIALING = 1
LOGGING = 2
CONNECTING = 3
CONNECTED = 4

gateway = None

connected = False
dialstate = NONE
starttime = None
conn = eConsoleAppContainer()
conn.appClosed.append(pppdClosed)
conn.dataAvail.append(dataAvail)

###########################################################################

config.plugins.xModem = ConfigSubsection()
config.plugins.xModem.standard = ConfigSelection([("0", "internal modem"),("1", "gprs/edge/umts/hsdpa"),("2", "cdma/evdo"),("3", "use peers file")], default = "0")
config.plugins.xModem.extlog = ConfigYesNo(default=False)
config.plugins.xModem.autorun = ConfigYesNo(default=False)
config.plugins.xModem.altdns = ConfigYesNo(default=False)
config.plugins.xModem.dns1 = ConfigIP(default=[208,67,222,222])
config.plugins.xModem.dns2 = ConfigIP(default=[208,67,220,220])

config.plugins.xModem.imod = ConfigSubsection()
config.plugins.xModem.imod.username = ConfigText("arcor", fixed_size=False)
config.plugins.xModem.imod.password = ConfigPassword("internet", fixed_size=False)
config.plugins.xModem.imod.number = ConfigText("01920793", fixed_size=False)
config.plugins.xModem.imod.number.setUseableChars(u"0123456789PTW,@")
config.plugins.xModem.imod.port = ConfigText("/dev/tts/2", fixed_size=False)
config.plugins.xModem.imod.port.setUseableChars(u"0123456789abcdemstuvyABCMSTU/")
config.plugins.xModem.imod.speed = ConfigInteger(default = 2400, limits=(1, 115200) )
config.plugins.xModem.imod.extopt = ConfigYesNo(default=False)
config.plugins.xModem.imod.mtu = ConfigInteger(default = 552, limits=(1, 65535) )
config.plugins.xModem.imod.mru = ConfigInteger(default = 552, limits=(1, 65535) )
config.plugins.xModem.imod.initstr = ConfigText("", fixed_size=False)
config.plugins.xModem.imod.deinstr = ConfigText("", fixed_size=False)
config.plugins.xModem.imod.pppopt = ConfigText("", fixed_size=False)

config.plugins.xModem.gprs = ConfigSubsection()
config.plugins.xModem.gprs.username = ConfigText("mts", fixed_size=False)
config.plugins.xModem.gprs.password = ConfigPassword("mts", fixed_size=False)
config.plugins.xModem.gprs.number = ConfigText("*99***1#", fixed_size=False)
config.plugins.xModem.gprs.numbers = ConfigSelection([("0", "*99#"),("1", "*99***1#"),("2", "*99**1*1#"),("3", "#777")], default = "1")
config.plugins.xModem.gprs.numbersel = ConfigYesNo(default=True)
config.plugins.xModem.gprs.apn = ConfigText("internet.mts.ru", fixed_size=False)
config.plugins.xModem.gprs.port = ConfigText("/dev/ttyUSB0", fixed_size=False)
config.plugins.xModem.gprs.port.setUseableChars(u"0123456789abcdemstuvyABCMSTU/")
config.plugins.xModem.gprs.speed = ConfigInteger(default = 115200, limits=(1, 921600) )
config.plugins.xModem.gprs.extopt = ConfigYesNo(default=False)
config.plugins.xModem.gprs.mtu = ConfigInteger(default = 1492, limits=(1, 65535) )
config.plugins.xModem.gprs.mru = ConfigInteger(default = 1492, limits=(1, 65535) )
config.plugins.xModem.gprs.initstr = ConfigText("", fixed_size=False)
config.plugins.xModem.gprs.deinstr = ConfigText("", fixed_size=False)
config.plugins.xModem.gprs.pppopt = ConfigText("persist", fixed_size=False)
config.plugins.xModem.gprs.vendid = ConfigText("", fixed_size=False)
config.plugins.xModem.gprs.vendid.setUseableChars(u"0123456789abcdef")
config.plugins.xModem.gprs.prodid = ConfigText("", fixed_size=False)
config.plugins.xModem.gprs.prodid.setUseableChars(u"0123456789abcdef")
config.plugins.xModem.gprs.zerocd = ConfigText("", fixed_size=False)
config.plugins.xModem.gprs.pincode = ConfigText("", fixed_size=False )
config.plugins.xModem.gprs.pincode.setUseableChars(u"0123456789")

config.plugins.xModem.cdma = ConfigSubsection()
config.plugins.xModem.cdma.username = ConfigText("01920793@free", fixed_size=False)
config.plugins.xModem.cdma.password = ConfigPassword("000000", fixed_size=False)
config.plugins.xModem.cdma.number = ConfigText("#777", fixed_size=False)
config.plugins.xModem.cdma.numbers = ConfigSelection([("0", "*99#"),("1", "*99***1#"),("2", "*99**1*1#"),("3", "#777")], default = "3")
config.plugins.xModem.cdma.numbersel = ConfigYesNo(default=True)
config.plugins.xModem.cdma.port = ConfigText("/dev/ttyUSB0", fixed_size=False)
config.plugins.xModem.cdma.port.setUseableChars(u"0123456789abcdemstuvyABCMSTU/")
config.plugins.xModem.cdma.speed = ConfigInteger(default = 460800, limits=(1, 921600) )
config.plugins.xModem.cdma.mtu = ConfigInteger(default = 1492, limits=(1, 65535) )
config.plugins.xModem.cdma.mru = ConfigInteger(default = 1492, limits=(1, 65535) )
config.plugins.xModem.cdma.initstr = ConfigText("", fixed_size=False)
config.plugins.xModem.cdma.deinstr = ConfigText("", fixed_size=False)
config.plugins.xModem.cdma.pppopt = ConfigText("persist", fixed_size=False)
config.plugins.xModem.cdma.vendid = ConfigText("", fixed_size=False)
config.plugins.xModem.cdma.vendid.setUseableChars(u"0123456789abcdef")
config.plugins.xModem.cdma.prodid = ConfigText("", fixed_size=False)
config.plugins.xModem.cdma.prodid.setUseableChars(u"0123456789abcdef")
config.plugins.xModem.cdma.zerocd = ConfigText("", fixed_size=False)

config.plugins.xModem.peer = ConfigSubsection()
config.plugins.xModem.peer.file = ConfigText("gprs-siem", fixed_size=False)
config.plugins.xModem.peer.vendid = ConfigText("", fixed_size=False)
config.plugins.xModem.peer.vendid.setUseableChars(u"0123456789abcdef")
config.plugins.xModem.peer.prodid = ConfigText("", fixed_size=False)
config.plugins.xModem.peer.prodid.setUseableChars(u"0123456789abcdef")
config.plugins.xModem.peer.zerocd = ConfigText("", fixed_size=False)

###########################################################################

class ConnectInfo(Screen):

	skin = """
	<screen position="140,100" size="440,310" title="Connect statistics" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="10,10" size="140,40" alphatest="on" />
		<widget name="key_red" position="10,10" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<!--widget name="curtimetxt" position="230,20" size="125,18" font="Regular;16" transparent="1" /-->
		<!--widget source="global.CurrentTime" render="Label" position="358,20" size="82,18" font="Regular;16" >
			<convert type="ClockToText">WithSeconds</convert>
		</widget-->
		<widget name="contimetxt" position="10,60" size="180,18" font="Regular;16" transparent="1" />
		<widget name="contimeval" position="200,60" size="235,18" font="Regular;16" />
		<widget name="ifacetxt" position="10,80" size="180,18" font="Regular;16" transparent="1" />
		<widget name="ifaceval" position="200,80" size="235,18" font="Regular;16" />
		<widget name="localIPtxt" position="10,100" size="180,18" font="Regular;16" transparent="1" />
		<widget name="localIPval" position="200,100" size="235,18" font="Regular;16" transparent="1" />
		<widget name="remoteIPtxt" position="10,120" size="180,18" font="Regular;16" transparent="1" />
		<widget name="remoteIPval" position="200,120" size="235,18" font="Regular;16" transparent="1" />
		<widget name="gatewaytxt" position="10,140" size="180,18" font="Regular;16" transparent="1" />
		<widget name="gatewayval" position="200,140" size="235,18" font="Regular;16" transparent="1" />
		<widget name="dnstxt" position="10,160" size="180,18" font="Regular;16" transparent="1" />
		<widget name="dnsval" position="200,160" size="235,18" font="Regular;16" transparent="1" />
		<ePixmap pixmap="skin_default/div-v.png" position="98,205" size="2,90" zPosition="1" />
		<ePixmap pixmap="skin_default/div-v.png" position="268,205" size="2,90" zPosition="1" />
		<widget name="receivetxt" position="100,205" size="165,18" font="Regular;16" halign="center" transparent="1" />
		<widget name="transmittxt" position="270,205" size="165,18" font="Regular;16" halign="center" transparent="1" />
		<ePixmap pixmap="skin_default/div-h.png" position="10,230" size="420,2" zPosition="1" />
		<widget name="bytestxt" position="10,240" size="85,18" font="Regular;16" transparent="1" />
		<widget name="bytesRXval" position="100,240" size="165,18" font="Regular;16" halign="center" transparent="1" />
		<widget name="bytesTXval" position="270,240" size="165,18" font="Regular;16" halign="center" transparent="1" />
		<widget name="packettxt" position="10,260" size="85,18" font="Regular;16" transparent="1" />
		<widget name="packetRXval" position="100,260" size="165,18" font="Regular;16" halign="center" transparent="1" />
		<widget name="packetTXval" position="270,260" size="165,18" font="Regular;16" halign="center" transparent="1" />
		<widget name="errortxt" position="10,280" size="85,18" font="Regular;16" transparent="1" />
		<widget name="errorRXval" position="100,280" size="165,18" font="Regular;16" halign="center" transparent="1" />
		<widget name="errorTXval" position="270,280" size="165,18" font="Regular;16" halign="center" transparent="1" />
	</screen>"""

	def __init__(self, session, constarttime = None, iface='ppp0'):
		Screen.__init__(self, session)

		self.starttime = constarttime
		if self.starttime is None:
			self.starttime = getTime()
		self.iface = iface
		if self.iface is None:
			self.iface = 'ppp0'
		self.Console = None
		#self.netmask = "255.255.255.255"
		self.getInterface(self.iface)
		#self.nameservers = (iNetwork.getNameserverList() + [[0,0,0,0]] * 2)[0:2]

		self["key_red"] = Button(_("Cancel"))
		self["ifacetxt"] = Label(_("Interface:"))
		self["ifaceval"] = Label(self.iface)
		self["curtimetxt"] = Label(_("Current Time:"))
		self["contimetxt"] = Label(_("Connection Time:"))
		self["contimeval"] = Label(self.getConnectTime())
		self["localIPtxt"] = Label(_("Local IP:"))
		self["localIPval"] = Label("-.-.-.-")
		self["remoteIPtxt"] = Label(_("Remote IP:"))
		self["remoteIPval"] = Label("-.-.-.-")
		self["gatewaytxt"] = Label(_("Gateway:"))
		self["gatewayval"] = Label(self.getGateway())
		self["dnstxt"] = Label(_("Name Servers:"))
		#self["dnsval"] = Label(self.ConvertIP(self.nameservers[0], na=True) + self.ConvertIP(self.nameservers[1], prefix="; "))
		self["dnsval"] = Label(self.getNameservers())
		self["receivetxt"] = Label(_("Received"))
		self["transmittxt"] = Label(_("Transmited"))
		self["bytestxt"] = Label(_("Bytes:"))
		self["bytesRXval"] = Label("0")
		self["bytesTXval"] = Label("0")
		self["packettxt"] = Label(_("Packets:"))
		self["packetRXval"] = Label("0")
		self["packetTXval"] = Label("0")
		self["errortxt"] = Label(_("Errors:"))
		self["errorRXval"] = Label("0")
		self["errorTXval"] = Label("0")
		
		self.getStatistics(self.iface)

		self["actions"] = ActionMap(["SetupActions"], 
			{
				"cancel": self.close,
				"ok": self.close
			})

		self.clock_timer = eTimer()
		self.clock_timer.callback.append(self.clockLoop)

		self.onClose.append(self.__closed)
		self.onLayoutFinish.append(self.__layoutFinished)

	def __layoutFinished(self):
		self.clock_timer.start(1000,False)

	def __closed(self):
		self.clock_timer.stop()
		self.clock_timer.callback.remove(self.clockLoop)

	def clockLoop(self):
		self["contimeval"].setText(self.getConnectTime())
		self.getStatistics(self.iface)

	def getConnectTime(self):
		time = int(getTime() - self.starttime)
		s = time % 60
		m = (time / 60) % 60
		h = (time / 3600) % 24
		d = time / 86400
		text = "%02d:%02d:%02d" % (h, m, s)
		if d > 0:
			text = "%dd %s" % (d, text)
		return text

	def getGateway(self):
		gw = getDefaultGateway()
		if gw:
			return "%d.%d.%d.%d" % (gw&0xFF, (gw>>8)&0xFF, (gw>>16)&0xFF, (gw>>24)&0xFF)
		return "0.0.0.0"

	#def ConvertIP(self, list, default=False, na=False, prefix=""):
	#	retstr = ""
	#	if list is not None:
	#		retstr = '.'.join(["%d" % d for d in list])
	#		if retstr == "0.0.0.0":
	#			if not default:
	#				retstr = ""
	#			if na:
	#				retstr = prefix + "N/A"
	#		else:
	#			retstr = prefix + retstr
	#	return retstr

	def regExpMatch(self, pattern, string):
		if string is None:
			return None
		try:
			return pattern.search(string).group()
		except AttributeError:
			None

	def getNameservers(self):
		ipRegexp = "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
		nameserverPattern = re_compile("^nameserver +" + ipRegexp)
		ipPattern = re_compile(ipRegexp)

		resolv = []
		try:
			fp = file('/etc/resolv.conf', 'r')
			resolv = fp.readlines()
			fp.close()
		except:
			print "[xModem] resolv.conf - opening failed"

		servers = ''
		for line in resolv:
			if self.regExpMatch(nameserverPattern, line) is not None:
				ip = self.regExpMatch(ipPattern, line)
				if ip is not None:
					if servers:
						servers += '; ' + ip
					else:
						servers = ip

		return servers

	def getStatistics(self, iface='ppp0'):
		digitalPattern = re_compile('[0-9]+')
		proclines = []
		try:
			fp = file('/proc/net/dev', 'r')
			proclines = fp.readlines()
			fp.close()
		except:
			print "[xModem] /proc/net/dev - opening failed"

		for line in proclines:
			if line.find(iface) != -1 :
				tokens = digitalPattern.findall(line[7:])
				if len(tokens) > 10:
					self["bytesRXval"].setText(self.strToSize(tokens[0]))
					self["packetRXval"].setText(tokens[1])
					self["errorRXval"].setText(tokens[2])
					self["bytesTXval"].setText(self.strToSize(tokens[8]))
					self["packetTXval"].setText(tokens[9])
					self["errorTXval"].setText(tokens[10])
				break

	def strToSize(self, strval="0"):
		ext = ['KB', 'KB', 'MB', 'GB', 'TB']
		X = int(strval)
		D = 0
		M = X
		i = 0
		while (X > 1023):
			D = X / 1024
			M = X % 1024
			X = D
			i += 1
			if i > 3:
				break
		return "%lu,%.3lu %s" % (D, M*1000/1024, ext[i])

	def getInterface(self, iface):
		from Components.Console import Console
		if not self.Console:
			self.Console = Console()
		cmd = "ip -o addr"
		self.Console.ePopen(cmd, self.IPaddrFinished, iface)

	def IPaddrFinished(self, result, retval, extra_args):
		#def calc_netmask(self,nmask):
		#	from struct import pack, unpack
		#	from socket import inet_ntoa, inet_aton
		#	mask = 1L<<31
		#	xnet = (1L<<32)-1
		#	cidr_range = range(0, 32)
		#	cidr = long(nmask)
		#	if cidr not in cidr_range:
		#		print 'cidr invalid: %d' % cidr
		#		return None
		#	else:
		#		nm = ((1L<<cidr)-1)<<(32-cidr)
		#		netmask = str(inet_ntoa(pack('>L', nm)))
		#		return netmask

		iface = extra_args
		globalIPpattern = re_compile("scope global")
		ipRegexp = '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
		#netRegexp = '[0-9]{1,2}'
		ipLinePattern = re_compile('inet ' + ipRegexp)
		peerLinePattern = re_compile('peer ' + ipRegexp + '/')
		ipPattern = re_compile(ipRegexp)
		#netmaskLinePattern = re_compile('/' + netRegexp)
		#netmaskPattern = re_compile(netRegexp)
		
		for line in result.splitlines():
			split = line.strip().split(' ',2)
			if (split[1] == iface):
				if re_search(globalIPpattern, split[2]):
					ip = self.regExpMatch(ipPattern, self.regExpMatch(ipLinePattern, split[2]))
					peer = self.regExpMatch(ipPattern, self.regExpMatch(peerLinePattern, split[2]))
					#netmask = calc_netmask(self.regExpMatch(netmaskPattern, self.regExpMatch(netmaskLinePattern, split[2])))
					if ip is not None:
						self["localIPval"].setText(ip)
					if peer is not None:
						self["remoteIPval"].setText(peer)
					#if netmask is not None:
					#	self.netmask = netmask
					#break




class ModemSetup(ConfigListScreen, Screen):

	skin = """
		<screen position="140,100" size="440,310" title="xModem v0.8" >
		<ePixmap pixmap="skin_default/buttons/green.png" position="10,10" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="290,10" size="140,40" alphatest="on" />
		<widget name="key_green" position="10,10" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_red" position="290,10" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="config" position="10,60" size="420,150" scrollbarMode="showOnDemand" />
		<widget name="state" position="10,220" size="420,90" font="Regular;20" />
		<widget source="InfoIcon" render="Pixmap" pixmap="skin_default/buttons/key_info.png" position="395,270" zPosition="10" size="35,25" transparent="1" alphatest="on" >
			<convert type="ConditionalShowHide" />
		</widget>
		</screen>"""

	def nothing(self):
		print "nothing!"

	def __init__(self, session, args = None):
		global conn
		global connected
		self.skin = ModemSetup.skin
		self.dot = 0
		self.dots = '........'
		self.connectiface = None

		Screen.__init__(self, session)

		ConfigListScreen.__init__(self, [])
		self.initConfig()
		
		self["key_green"] = Button("")
		self["key_red"] = Button("")
		self["state"] = Label("")
		self["InfoIcon"] = Boolean(False)
		self["actions"] = NumberActionMap(["ModemActions"],
		{
			"cancel": self.close,
			"left": self.keyLeft,
			"right": self.keyRight,
			"connect": self.connect,
			"disconnect": self.disconnect,
			"info": self.showInfo,
			"deleteForward": self.deleteForward,
			"deleteBackward": self.deleteBackward,
			"0": self.keyNumber,
			"1": self.keyNumber,
			"2": self.keyNumber,
			"3": self.keyNumber,
			"4": self.keyNumber,
			"5": self.keyNumber,
			"6": self.keyNumber,
			"7": self.keyNumber,
			"8": self.keyNumber,
			"9": self.keyNumber
		}, -1)

		self["ListActions"] = ActionMap(["ListboxDisableActions"],
		{
			"moveUp": self.nothing,
			"moveDown": self.nothing,
			"moveTop": self.nothing,
			"moveEnd": self.nothing,
			"pageUp": self.nothing,
			"pageDown": self.nothing
		}, -1)

		self.stateTimer = eTimer()
		self.stateTimer.callback.append(self.stateLoop)

		conn.appClosed.append(self.pppdClosed)
		conn.dataAvail.remove(dataAvail)
		conn.dataAvail.append(self.dataAvail)

		self.onClose.append(self.__closed)
		self.onLayoutFinish.append(self.__layoutFinished)

	def initConfig(self):
		list = []
		self.extopt = None
		self.numbers = None
		self.standard = getConfigListEntry(_("Standard"), config.plugins.xModem.standard)
		list.append(self.standard)

		if config.plugins.xModem.standard.value == "0":
			list.append(getConfigListEntry(_("Username"), config.plugins.xModem.imod.username))
			list.append(getConfigListEntry(_("Password"), config.plugins.xModem.imod.password))
			list.append(getConfigListEntry(_("Phone number"), config.plugins.xModem.imod.number))
			self.extopt = getConfigListEntry(_("Extended settings"), config.plugins.xModem.imod.extopt)
			list.append(self.extopt)

			if config.plugins.xModem.imod.extopt.value == True:
				sublist = [
					getConfigListEntry(_("Port"), config.plugins.xModem.imod.port),
					getConfigListEntry(_("Speed"), config.plugins.xModem.imod.speed),
					getConfigListEntry(_("MTU size"), config.plugins.xModem.imod.mtu),
					getConfigListEntry(_("MRU size"), config.plugins.xModem.imod.mru),
					getConfigListEntry(_("Init string"), config.plugins.xModem.imod.initstr),
					getConfigListEntry(_("Deinit string"), config.plugins.xModem.imod.deinstr),
					getConfigListEntry(_("Adv. pppd options"), config.plugins.xModem.imod.pppopt),
				]
				list.extend(sublist)
		elif config.plugins.xModem.standard.value == "1":
			list.append(getConfigListEntry(_("Username"), config.plugins.xModem.gprs.username))
			list.append(getConfigListEntry(_("Password"), config.plugins.xModem.gprs.password))
			if config.plugins.xModem.gprs.numbersel.value == True:
				self.numbers = getConfigListEntry(_("Phone number"), config.plugins.xModem.gprs.numbers)
				list.append(self.numbers)
			else:
				list.append(getConfigListEntry(_("Phone number"), config.plugins.xModem.gprs.number))
			list.append(getConfigListEntry(_("APN"), config.plugins.xModem.gprs.apn))
			list.append(getConfigListEntry(_("Port"), config.plugins.xModem.gprs.port))
			list.append(getConfigListEntry(_("Speed"), config.plugins.xModem.gprs.speed))
			self.extopt = getConfigListEntry(_("Extended settings"), config.plugins.xModem.gprs.extopt)
			list.append(self.extopt)

			if config.plugins.xModem.gprs.extopt.value == True:
				sublist = [
					getConfigListEntry(_("MTU size"), config.plugins.xModem.gprs.mtu),
					getConfigListEntry(_("MRU size"), config.plugins.xModem.gprs.mru),
					getConfigListEntry(_("Init string"), config.plugins.xModem.gprs.initstr),
					getConfigListEntry(_("Deinit string"), config.plugins.xModem.gprs.deinstr),
					getConfigListEntry(_("Adv. pppd options"), config.plugins.xModem.gprs.pppopt),
					getConfigListEntry(_("Vendor ID"), config.plugins.xModem.gprs.vendid),
					getConfigListEntry(_("Product ID"), config.plugins.xModem.gprs.prodid),
					getConfigListEntry(_("ZeroCD params"), config.plugins.xModem.gprs.zerocd),
					getConfigListEntry(_("Pincode"), config.plugins.xModem.gprs.pincode)
				]
				list.extend(sublist)
		elif config.plugins.xModem.standard.value == "2":
			list.append(getConfigListEntry(_("Username"), config.plugins.xModem.cdma.username))
			list.append(getConfigListEntry(_("Password"), config.plugins.xModem.cdma.password))
			if config.plugins.xModem.cdma.numbersel.value == True:
				self.numbers = getConfigListEntry(_("Phone number"), config.plugins.xModem.cdma.numbers)
				list.append(self.numbers)
			else:
				list.append(getConfigListEntry(_("Phone number"), config.plugins.xModem.cdma.number))
			list.append(getConfigListEntry(_("Port"), config.plugins.xModem.cdma.port))
			list.append(getConfigListEntry(_("Speed"), config.plugins.xModem.cdma.speed))
			list.append(getConfigListEntry(_("MTU size"), config.plugins.xModem.cdma.mtu))
			list.append(getConfigListEntry(_("MRU size"), config.plugins.xModem.cdma.mru))
			list.append(getConfigListEntry(_("Init string"), config.plugins.xModem.cdma.initstr))
			list.append(getConfigListEntry(_("Deinit string"), config.plugins.xModem.cdma.deinstr))
			list.append(getConfigListEntry(_("Pppd options"), config.plugins.xModem.cdma.pppopt))
			list.append(getConfigListEntry(_("Vendor ID"), config.plugins.xModem.cdma.vendid))
			list.append(getConfigListEntry(_("Product ID"), config.plugins.xModem.cdma.prodid))
			list.append(getConfigListEntry(_("ZeroCD params"), config.plugins.xModem.cdma.zerocd))
		else:
			list.append(getConfigListEntry(_("/etc/ppp/peers/"), config.plugins.xModem.peer.file))
			list.append(getConfigListEntry(_("Vendor ID"), config.plugins.xModem.peer.vendid))
			list.append(getConfigListEntry(_("Product ID"), config.plugins.xModem.peer.prodid))
			list.append(getConfigListEntry(_("ZeroCD params"), config.plugins.xModem.peer.zerocd))

		self.altdns = getConfigListEntry(_("Alternative DNS"), config.plugins.xModem.altdns)
		list.append(self.altdns)
		if config.plugins.xModem.altdns.value == True:
			sublist2 = [
				getConfigListEntry(_("DNS 1"), config.plugins.xModem.dns1),
				getConfigListEntry(_("DNS 2"), config.plugins.xModem.dns2),
			]
			list.extend(sublist2)
		#list.append(getConfigListEntry(_("Extended log"), config.plugins.xModem.extlog))
		list.append(getConfigListEntry(_("Autostart"), config.plugins.xModem.autorun))

		self["config"].list = list
		self["config"].l.setList(list)

	def newConfig(self):
		cur = self["config"].getCurrent()
		if cur == self.standard:
			self.initConfig()
		elif cur == self.extopt:
			self.initConfig()
		elif cur == self.numbers:
			self.initConfig()
		elif cur == self.altdns:
			self.initConfig()

	def keyLeft(self):
		if self.green_function == CONNECT:
			ConfigListScreen.keyLeft(self)
			self.newConfig()

	def keyRight(self):
		if self.green_function == CONNECT:
			ConfigListScreen.keyRight(self)
			self.newConfig()

	def keyNumber(self, number):
		if self.green_function == CONNECT:
			ConfigListScreen.keyNumberGlobal(number)

	def deleteForward(self):
		if self.green_function == CONNECT:
			ConfigListScreen.keyDelete(self)

	def deleteBackward(self):
		if self.green_function == CONNECT:
			ConfigListScreen.keyBackspace(self)

	def showInfo(self):
		if self.red_function == DISCONNECT:
			global starttime
			self.session.open(ConnectInfo, constarttime = starttime, iface = self.connectiface)

	def __layoutFinished(self):
		global conn
		global connected
		if conn.running():
			if  connected:
				self["state"].setText(_("\nConnected!"))
				self.green_function = NONE
				self.red_function = DISCONNECT
			else:
				global dialstate
				if dialstate == DIALING:
					tmp = "Dialing:"
				elif dialstate == LOGGING:
					tmp = "Dialing:" + self.dots + "OK\nLogin:"
				elif dialstate == CONNECTING:
					tmp = "Dialing:" + self.dots + "OK\nLogin:" + self.dots + "..OK\n"
				else:
					tmp = ""
				self.dot = 0
				self["state"].setText(tmp)
				self.stateTimer.start(1000,False)
				self.green_function = NONE
				self.red_function = ABORT
		else:
			self.green_function = CONNECT
			self.red_function = NONE
		self.updateGui()

	def __closed(self):
		global connected
		conn.appClosed.remove(self.pppdClosed)
		conn.dataAvail.remove(self.dataAvail)
		conn.dataAvail.append(dataAvail)
		if not connected:
			conn.sendCtrlC()
		for x in self["config"].list:
			x[1].save()

	def stateLoop(self):
		txt = self["state"].getText()
		if self.dot > 7:
			txt = txt[:-7]
			self.dot = 1
		else:
			txt += '.'
			self.dot += 1
		self["state"].setText(txt)

	def connect(self):
		if self.green_function == CONNECT:
			self.connectiface = None
			self.dot = 0
			self["state"].setText(_("Dialing:"))
			self.stateTimer.start(1000,False)

			ret = StartConnect()
			if ret:
				self.pppdClosed(ret)
				pppdClosed(ret)
			self.green_function = NONE
			self.red_function = ABORT
			self.updateGui()

	def disconnect(self):
		global conn
		conn.sendCtrlC()
		self.red_function = NONE
		self.updateGui()

	def pppdClosed(self, retval):
		global connected
		global starttime
		self.stateTimer.stop()
		self.red_function = NONE
		self.green_function = CONNECT
		if connected:
			self["state"].setText("\nConnection terminated.")
		self.updateGui()
		connected = False
		starttime = None

	def dataAvail(self, text):
		if text.find("unrecognized option") != -1:
			pos = text.find("unrecognized option")
			tmp1 = "pppd: " + text[pos:]
			tmp1 = tmp1[:tmp1.find("\n")+1]
			tmp = self["state"].getText()
			tmp += self.dots + "FAILED\n"
			tmp += tmp1
			self["state"].setText(tmp)
		if text.find("Serial connection established") != -1:
			tmp = self["state"].getText()
			dots = self.dots[:-self.dot]
			tmp += dots + "OK\nLogin:"
			self.dot = 0
			self["state"].setText(tmp)
		if text.find("Using interface") != -1:
			pos = text.find("Using interface")
			length = len("Using interface ")
			tmp = text[pos+length:]
			self.connectiface = tmp[:4]
		if text.find("AP authentication succeeded") != -1 or text.find("No auth is possible") != -1:
			tmp = self["state"].getText()
			dots = self.dots[:-self.dot]
			tmp += dots + "..OK\n";
			self.dot = 0
			self["state"].setText(tmp)
			self.stateTimer.stop()
		if text.find("ip-up finished") != -1:
			global connected
			global starttime
			self.stateTimer.stop()
			if starttime == None:
				starttime = getTime()
			if config.plugins.xModem.altdns.value:
				setAltDNS()
			tmp = self["state"].getText()
			tmp += "Connected :)\n"
			self["state"].setText(tmp)
			self.red_function = DISCONNECT
			connected=True
		if text.find("Connect script failed") != -1:
			tmp = self["state"].getText()
			dots = self.dots[:-self.dot]
			tmp += dots + "FAILED\n"
			self["state"].setText(tmp)
			self.stateTimer.stop()
			self.red_function = NONE
			self.green_function = CONNECT
			self.disconnect()
		self.updateGui()

	def updateGui(self):
		if self.red_function == NONE:
			self["key_red"].setText("")
			self["InfoIcon"].boolean = False
		elif self.red_function == DISCONNECT:
			self["key_red"].setText(_("Disconnect"))
			self["InfoIcon"].boolean = True
		elif self.red_function == ABORT:
			self["key_red"].setText(_("Abort"))
			self["InfoIcon"].boolean = False
		if self.green_function == NONE:
			self["key_green"].setText("")
		elif self.green_function == CONNECT:
			self["key_green"].setText(_("Connect"))
		focus_enabled = self.green_function == CONNECT
		self["config"].instance.setSelectionEnable(focus_enabled)
		self["ListActions"].setEnabled(not focus_enabled)


def autostart(reason, **kwargs):
	if reason == 0:
		StartConnect(True)
	elif reason == 1:
		StopConnect(True)

def main(session, **kwargs):
	session.open(ModemSetup)

def Plugins(**kwargs):
	return [PluginDescriptor(where = PluginDescriptor.WHERE_AUTOSTART, fnc = autostart),
		PluginDescriptor(name=_("xModem"), description=_("Plugin to configure modem and connect to the Internet"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="xmodem.png", fnc=main)]
