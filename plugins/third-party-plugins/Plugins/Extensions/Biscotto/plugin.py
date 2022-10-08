# Edit By RAED to OE2.5 images 10-03-2019
# Edit By RAED Add IRDETO & PowerVU 14-03-2019
# Edit By RAED Fix PowerVU 18-03-2019
# Edit By RAED Edit keyboard 19-03-2019

from enigma import eConsoleAppContainer, eDVBDB, eServiceCenter, eServiceReference, iServiceInformation
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Tools.BoundFunction import boundFunction
from ServiceReference import ServiceReference
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.MessageBox import MessageBox
import os
import binascii
from array import array
from string import hexdigits
from datetime import datetime

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
    lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
    os_environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
    gettext.bindtextdomain("Biscotto", resolveFilename(SCOPE_PLUGINS, "Extensions/Biscotto/locale"))

def _(txt):
    t = gettext.dgettext("Biscotto", txt)
    if t == txt:
        print "[Biscotto] fallback to default translation for", txt
        t = gettext.gettext(txt)
    return t

localeInit()
language.addCallback(localeInit)

def findSoftCamKey():
	paths = ["/etc/tuxbox/config/oscam-emu", "/etc/tuxbox/config/oscam", "/etc/tuxbox/config/ncam", "/etc/tuxbox/config", "/etc", "/var/keys", "/usr/keys"]
	if os.path.exists("/tmp/.oscam/oscam.version"):
		data = open("/tmp/.oscam/oscam.version", "r").readlines()
	if os.path.exists("/tmp/.ncam/ncam.version"):
		data = open("/tmp/.ncam/ncam.version", "r").readlines()
		for line in data:
			if "configdir:" in line.lower():
				paths.insert(0, line.split(":")[1].strip())
	for path in paths:
		softcamkey = os.path.join(path, "SoftCam.Key")
		print "[key] the %s exists %d" % (softcamkey, os.path.exists(softcamkey))
		if os.path.exists(softcamkey):
			return softcamkey
	return "/usr/keys/SoftCam.Key"

class HexKeyBoard(VirtualKeyBoard):
	def __init__(self, session, title="", **kwargs):
		VirtualKeyBoard.__init__(self, session, title, **kwargs)
		self.skinName = "VirtualKeyBoard"
		self.keys_list = [[[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
					[u"OK", u"A", u"B", u"C", u"D", u"E", u"F", u"OK", u"LEFT", u"RIGHT", u"ALL", u"CLEAR"]]]
		self.locales = { "hex" : [_("HEX"), _("HEX"), self.keys_list] }
		self.lang = "hex"
		try:
		     self.setLocale()
		except:
                     self.max_key = all
		     self.setLang()
		self.buildVirtualKeyBoard()

	def setLang(self):
                self.keys_list = [[u"EXIT", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9", u"0", u"BACKSPACE"],
					[u"OK", u"A", u"B", u"C", u"D", u"E", u"F", u"OK", u"LEFT", u"RIGHT", u"ALL", u"CLEAR"]]

table = array('L')
for byte in range(256):
	crc = 0
	for bit in range(8):
		if (byte ^ crc) & 1:
			crc = (crc >> 1) ^ 0xEDB88320
		else:
			crc >>= 1
		byte >>= 1
	table.append(crc)

def crc32(string):
	value = 0x2600 ^ 0xffffffffL
	for ch in string:
		value = table[(ord(ch) ^ value) & 0xff] ^ (value >> 8)
	return value ^ 0xffffffffL

def crc323(string):
	value = 0xe00 ^ 0xffffffffL
	for ch in string:
		value = table[(ord(ch) ^ value) & 0xff] ^ (value >> 8)
	return value ^ 0xffffffffL

def hasCAID(session):
	service = session.nav.getCurrentService()
	info = service and service.info()
	caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
	if caids and 0xe00 in caids: return True
	if caids and 0x2600 in caids: return True
	if caids and 0x604 in caids: return True
	if caids and 0x1010 in caids: return True
	try:
		return eDVBDB.getInstance().hasCAID(ref, 0xe00)	# PowerVU
	except:
		pass
	try:
		return eDVBDB.getInstance().hasCAID(ref, 0x2600) # BISS
	except:
		pass
	try:
		return eDVBDB.getInstance().hasCAID(ref, 0x604) # IRDETO
	except:
		pass
	try:
		return eDVBDB.getInstance().hasCAID(ref, 0x1010) # Tandberg
	except:
		pass
	return False

def getCAIDS(session):
	service = session.nav.getCurrentService()
	info = service and service.info()
	caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
	caidstr = "None"
	if caids: caidstr = " ".join(["%04X (%d)" % (x,x) for x in sorted(caids)])
	return caidstr

def keymenu(session, service=None, *args, **kwargs):
	service = session.nav.getCurrentService()
	info = service and service.info()
	caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
	SoftCamKey = findSoftCamKey()
	ref = session.nav.getCurrentlyPlayingServiceReference()
	if not os.path.exists(SoftCamKey):
		session.open(MessageBox, _("Emu misses SoftCam.Key (%s)") % SoftCamKey, MessageBox.TYPE_ERROR)
	elif not hasCAID(session):
		session.open(MessageBox, _("CAID is missing for service (%s) CAIDS: %s") % (ref.toString(), getCAIDS(session)), MessageBox.TYPE_ERROR)
	else:
	     if caids and 0xe00 in caids:
		   session.openWithCallback(boundFunction(setKeyCallback, session, SoftCamKey), HexKeyBoard,
			title=_("Please enter new key:"), text=findKeyPowerVU(session, SoftCamKey))
	     elif caids and 0x2600 in caids:
		   session.openWithCallback(boundFunction(setKeyCallback, session, SoftCamKey), HexKeyBoard,
			title=_("Please enter new key:"), text=findKeyBISS(session, SoftCamKey))
	     elif caids and 0x604 in caids:
		   session.openWithCallback(boundFunction(setKeyCallback, session, SoftCamKey), HexKeyBoard,
			title=_("Please enter new key:"), text=findKeyIRDETO(session, SoftCamKey))
	     elif caids and 0x1010 in caids:
		   session.openWithCallback(boundFunction(setKeyCallback, session, SoftCamKey), HexKeyBoard,
			title=_("Please enter new key:"), text=findKeyTandberg(session, SoftCamKey))

def setKeyCallback(session, SoftCamKey, key):
	service = session.nav.getCurrentService()
	info = service and service.info()
	caids = info and info.getInfoObject(iServiceInformation.sCAIDs)
	SoftCamKey = findSoftCamKey()
	ref = session.nav.getCurrentlyPlayingServiceReference()
	if key: key = "".join(c for c in key if c in hexdigits).upper()
	if key and len(key) == 14:
		if key != findKeyPowerVU(session, SoftCamKey, ""): # no change was made ## PowerVU
			keystr = "P %s 00 %s" % (getonidsid(session), key)
			name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			datastr = _("\n%s ; Added on %s for %s at %s\n") % (keystr, datetime.now(), name, getOrb(session))
			restartmess = _("\n*** Need to Restart emu TO Active new key ***\n")
			open(SoftCamKey, "a").write(datastr)
			eConsoleAppContainer().execute("/etc/init.d/softcam restart")
			session.open(MessageBox, _("PowerVU key saved sucessfuly!%s %s") % (datastr, restartmess), MessageBox.TYPE_INFO, timeout=10)
	elif key and len(key) == 16:
             if 0x2600 in caids:
		if key != findKeyBISS(session, SoftCamKey, ""): # no change was made ## BISS
			keystr = "F %08X 00 %s" % (getHash(session), key)
			name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			datastr = _("\n%s ; Added on %s for %s at %s\n") % (keystr, datetime.now(), name, getOrb(session))
			restartmess = _("\n*** Need to Restart emu TO Active new key ***\n")
			open(SoftCamKey, "a").write(datastr)
			eConsoleAppContainer().execute("/etc/init.d/softcam restart")
			session.open(MessageBox, _("BISS key saved sucessfuly!%s %s") % (datastr, restartmess), MessageBox.TYPE_INFO, timeout=10)
             else:
		if key != findKeyTandberg(session, SoftCamKey, ""): # no change was made ## Tandberg
			keystr = "T 0001 01 %s" % key
			name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			datastr = _("\n%s ; Added on %s for %s at %s\n") % (keystr, datetime.now(), name, getOrb(session))
			restartmess = _("\n*** Need to Restart emu TO Active new key ***\n")
			open(SoftCamKey, "a").write(datastr)
			eConsoleAppContainer().execute("/etc/init.d/softcam restart")
			session.open(MessageBox, _("Tandberg key saved sucessfuly!%s %s") % (datastr, restartmess), MessageBox.TYPE_INFO, timeout=10)
	elif key and len(key) == 32:
		if key != findKeyIRDETO(session, SoftCamKey, ""): # no change was made ## IRDETO
			keystr = "I 0604 M1 %s" % key
			name = ServiceReference(session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			datastr = _("\n%s ; Added on %s for %s at %s\n") % (keystr, datetime.now(), name, getOrb(session))
			restartmess = _("\n*** Need to Restart emu TO Active new key ***\n")
			open(SoftCamKey, "a").write(datastr)
			eConsoleAppContainer().execute("/etc/init.d/softcam restart")
			session.open(MessageBox, _("IRDETO key saved sucessfuly!%s %s") % (datastr, restartmess), MessageBox.TYPE_INFO, timeout=10)
	elif key:
		   session.openWithCallback(boundFunction(setKeyCallback, session,SoftCamKey), HexKeyBoard,
			title=_("Invalid key, length is %d") % len(key), text=key.ljust(16,'*'))
			#title=_("Invalid key, length is %d expecting 16.") % len(key), text=key.ljust(16,'*'))

def getHash(session):
	ref = session.nav.getCurrentlyPlayingServiceReference()
	sid = ref.getUnsignedData(1)
	tsid = ref.getUnsignedData(2)
	onid = ref.getUnsignedData(3)
	namespace = ref.getUnsignedData(4) | 0xA0000000

	# check if we have stripped or full namespace
	if namespace & 0xFFFF == 0:
		# Namespace without frequency - Calculate hash with srvid, tsid, onid and namespace
		data = "%04X%04X%04X%08X" % (sid, tsid, onid, namespace)
	else:
		# Full namespace - Calculate hash with srvid and namespace only
		data = "%04X%08X" % (sid, namespace)
	return crc32(binascii.unhexlify(data))

def getonidsid(session):
	ref = session.nav.getCurrentlyPlayingServiceReference()
	sid = ref.getUnsignedData(1)
	onid = ref.getUnsignedData(3)
	return "%04X%04X" % (onid, sid)

def getOrb(session):
	ref = session.nav.getCurrentlyPlayingServiceReference()
	orbpos = ref.getUnsignedData(4) >> 16
	if orbpos == 0xFFFF:
		desc = "C"
	elif orbpos == 0xEEEE:
		desc = "T"
	else:
		if orbpos > 1800: # west
			orbpos = 3600 - orbpos
			h = "W"
		else:
			h = "E"
		desc = ("%d.%d%s") % (orbpos / 10, orbpos % 10, h)
	return desc

def findKeyPowerVU(session, SoftCamKey, key="00000000000000"):
	keystart = "P %s" % getonidsid(session)
	keyline = ""
	with open(SoftCamKey, 'rU') as f:
		for line in f:
			if line.startswith(keystart):
				keyline = line
	if keyline:
		return keyline.split()[3]
	else:
		return key

def findKeyBISS(session, SoftCamKey, key="0000000000000000"):
	keystart = "F %08X" % getHash(session)
	keyline = ""
	with open(SoftCamKey, 'rU') as f:
		for line in f:
			if line.startswith(keystart):
				keyline = line
	if keyline:
		return keyline.split()[3]
	else:
		return key

def findKeyTandberg(session, SoftCamKey, key="0000000000000000"):
	keystart = "T 0001 01"
	keyline = ""
	with open(SoftCamKey, 'rU') as f:
		for line in f:
			if line.startswith(keystart):
				keyline = line
	if keyline:
		return keyline.split()[3]
	else:
		return key

def findKeyIRDETO(session, SoftCamKey, key="00000000000000000000000000000000"):
	keystart = "I 0604"
	keyline = ""
	with open(SoftCamKey, 'rU') as f:
		for line in f:
			if line.startswith(keystart):
				keyline = line
	if keyline:
		return keyline.split()[3]
	else:
		return key

def Plugins(**kwargs):
	return [PluginDescriptor(name = "Biscotto" , description = _("Manually add Key to current service"), icon="plugin.png",
		where = [PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU],
		fnc = keymenu, needsRestart = False)]

