#
# Softcam setup mod for openPLi
# Coded by vlamo (c) 2012
# Version: 3.0-rc2
# Support: http://dream.altmaster.net/
#
# Modified by Dima73 (c) 2012
# Support: Dima-73@inbox.lv
#

from . import _
from Components.config import config
from Screens.Screen import Screen
from Screens.ChannelSelection import service_types_radio, service_types_tv, ChannelSelection, ChannelSelectionBase
from RecordTimer import RecordTimer
from camcontrol import CamControl

def getProviderName(ref):
	typestr = ref.getData(0) in (2,10) and service_types_radio or service_types_tv
	pos = typestr.rfind(':')
	rootstr = '%s (channelID == %08x%04x%04x) && %s FROM PROVIDERS ORDER BY name'%(typestr[:pos+1],ref.getUnsignedData(4),ref.getUnsignedData(2),ref.getUnsignedData(3),typestr[pos+1:])
	from enigma import eServiceReference, eServiceCenter
	provider_root = eServiceReference(rootstr)
	serviceHandler = eServiceCenter.getInstance()
	providerlist = serviceHandler.list(provider_root)
	if not providerlist is None:
		while True:
			provider = providerlist.getNext()
			if not provider.valid(): break
			if provider.flags & eServiceReference.isDirectory:
				servicelist = serviceHandler.list(provider)
				if not servicelist is None:
					while True:
						service = servicelist.getNext()
						if not service.valid(): break
						if service == ref:
							info = serviceHandler.info(provider)
							return info and info.getName(provider) or "Unknown"
	return ''

def getAutoCamForService(service, provname=None):
	refstring = service.toString()
	if not provname:
		provname = getProviderName(service)
	for cam,list in autoCamList.items():
		if refstring in list or \
		  (provname and provname in list):
			return cam
	return None

class AutoCamList(dict):
	def __init__(self):
		dict.__init__(self)
		self.load()
	
	def loadFrom(self, filename):
		try:
			cfg = open(filename, 'r')
		except:
			return { }
		camname = 'default'
		from re import compile
		re_section = compile(r'\[(?P<camname>[^]]+)\]')
		while True:
			line = cfg.readline()
			if not line: break
			if line[0] in '#;\n': continue
			mo = re_section.match(line)
			if mo:
				camname = mo.group('camname')
				if not camname in self:
					self[camname] = [ ]
			else:
				self[camname].append(line.strip())
		cfg.close()
		return self
	
	def saveTo(self, filename):
		try:
			cfg = open(filename, 'w')
		except:
			return { }
		first = True
		for cam, val in self.items():
			if first:
				first = False
			else:
				cfg.write('\n')
			cfg.write('[%s]\n'%(cam))
			for v in val:
				cfg.write('%s\n'%(v))
		cfg.close()
		return self
	
	def load(self):
		self.loadFrom('/usr/local/e2/etc/autocam.conf')
	
	def save(self):
		self.saveTo('/usr/local/e2/etc/autocam.conf')
	
	def dict(self):
		return self
	
	def addCam(self, cam):
		if not self.has_key(cam):
			self[cam] = [ ]
	
	def delCam(self, cam):
		if self.has_key(cam):
			del self[cam]
	
	def addService(self, cam, service):
		self.addCam(cam)
		if isinstance(service, str):
			service = [service]
		for s in service:
			if not s in self[cam]:
				self[cam].append(s)
	
	def delService(self, cam, service):
		if self.has_key(cam):
			if isinstance(service, str):
				service = [service]
			for s in service:
				if s in self[cam]:
					self[cam].remove(s)

autoCamList = AutoCamList()

class AutoCamListSetup(Screen):
	skin = """
	<screen name="AutoCamListSetup" position="center,center" size="680,400" title="Auto-Camd List Setup">
		<ePixmap position="0,390" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/red.png" transparent="1" alphatest="on" />
		<ePixmap position="170,390" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/green.png" transparent="1" alphatest="on" />
		<ePixmap position="340,390" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/yellow.png" transparent="1" alphatest="on" />
		<ePixmap position="510,390" zPosition="1" size="170,2" pixmap="/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/images/blue.png" transparent="1" alphatest="on" />
		<widget name="key_red" position="0,348" zPosition="1" size="170,42" font="Regular;18" halign="center" valign="bottom" transparent="1" />
		<widget name="key_green" position="170,348" zPosition="1" size="170,42" font="Regular;18" halign="center" valign="bottom" transparent="1"  />
		<widget name="key_yellow" position="340,348" zPosition="1" size="170,42" font="Regular;18" halign="center" valign="bottom" transparent="1" />
		<widget name="key_blue" position="510,348" zPosition="1" size="170,42" font="Regular;18" halign="center" valign="bottom" transparent="1" />
		<widget source="list" render="Listbox" position="10,10" size="660,310" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
				{"template": [
						MultiContentEntryText(pos = (10, 5), size = (420, 25), font = 0, flags = RT_HALIGN_LEFT, text = 0),
						MultiContentEntryText(pos = (50, 30), size = (380, 20), font = 1, flags = RT_HALIGN_LEFT, text = 1),
						MultiContentEntryText(pos = (430, 13), size = (140, 24), font = 0, flags = RT_HALIGN_LEFT, text = 2),
					],
				 "fonts": [gFont("Regular", 21), gFont("Regular", 16)],
				 "itemHeight": 50
				}
			</convert>
		</widget>
	</screen>"""
	def __init__(self, session, camcontrol):
		Screen.__init__(self, session)
		
		self.camctrl = camcontrol
		self.ACL = autoCamList
		
		from Components.Sources.List import List
		self["list"] = List([])
		self.updateList()
		
		from Components.Label import Label
		self["key_red"] = Label(" ")
		self["key_green"] = Label(_("Add Provider"))
		self["key_yellow"] = Label(_("Add Channel"))
		self["key_blue"] = Label(" ")
		self.updateButtons()
		
		from Components.ActionMap import ActionMap
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.exit,
				"ok": self.keyOk,
				"red": self.keyRed,
				"green": self.keyGreen,
				"yellow": self.keyYellow,
				"blue": self.keyBlue,
			},-1)
			
		self.setTitle(_("Auto-Camd List Setup"))
		self.onClose.append(self.__onClose)

	def __onClose(self):
		self.ACL.save()

	def keyRed(self):
		cur = self["list"].getCurrent()
		if cur:
			self.ACL.delService(cur[1], cur[3])
			self.updateList()
			self.updateButtons()

	def keyGreen(self):
		self.session.openWithCallback(self.addServiceCallback, AutoCamServiceSetup, True)

	def keyYellow(self):
		self.session.openWithCallback(self.addServiceCallback, AutoCamServiceSetup)

	def addServiceCallback(self, *ref):
		if ref:
			ref = ref[0]
			if (ref.flags & 7) == 7:
				from ServiceReference import ServiceReference
				provname = ServiceReference(ref).getServiceName()
				self.ACL.addService(config.plugins.SoftcamSetup.autocam.defcam.value, provname)
			else:
				self.ACL.addService(config.plugins.SoftcamSetup.autocam.defcam.value, ref.toString())
			self.updateList()
			self.updateButtons()

	def keyBlue(self):
		cur = self["list"].getCurrent()
		if cur:
			sel, x = 0, -1
			camlist = [ ]
			for cam in self.camctrl.getList():
				#if cam == 'None': continue
				x += 1
				camlist.append((cam,))
				if not sel and cam == cur[1]:
					sel = x
			from Screens.ChoiceBox import ChoiceBox
			dlg = self.session.openWithCallback(self.choiceCamCallback, ChoiceBox, list=camlist, selection=sel)
			dlg.setTitle(_("Select Cam for %s")%(cur[0]))

	def choiceCamCallback(self, choice):
		if choice:
			cur = self["list"].getCurrent()
			if choice[0] != cur[1]:
				self.ACL.delService(cur[1], cur[3])
				self.ACL.addService(choice[0], cur[3])
				self.updateList()

	def keyOk(self):
		self.keyBlue()

	def exit(self):
		self.close()

	def updateList(self):
		from ServiceReference import ServiceReference
		self.list = [ ]
		for cam,list in self.ACL.items():
			for service in list:
				if '1:0:' in service:
					s = _('Channel')
					servname = ServiceReference(service).getServiceName()
				else:
					s = _('Provider')
					servname = service
				self.list.append((servname, cam, s, service))
		self["list"].setList(self.list)
		self["list"].updateList(self.list)

	def updateButtons(self):
		if len(self.list):
			self["key_red"].setText(_("Delete"))
			self["key_blue"].setText(_("Change Camd"))
		else:
			self["key_red"].setText(" ")
			self["key_blue"].setText(" ")

class AutoCamServiceSetup(ChannelSelectionBase):
	skin = """
	<screen position="center,center" size="560,430" title="Channel Selection">
		<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
		<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		<widget name="list" position="00,45" size="560,364" scrollbarMode="showOnDemand" />
	</screen>
	"""
	def __init__(self, session, providers=False):
		self.providers = providers
		ChannelSelectionBase.__init__(self, session)
		OFF = 0
		EDIT_BOUQUET = 1
		EDIT_ALTERNATIVES = 2
		self.bouquet_mark_edit = OFF
		from Components.ActionMap import ActionMap
		self["actions"] = ActionMap(["OkCancelActions", "TvRadioActions"], {"cancel": self.close, "ok": self.channelSelected, "keyRadio": self.setModeRadio, "keyTV": self.setModeTv})
		self.onLayoutFinish.append(self.setModeTv)

	def channelSelected(self):
		ref = self.getCurrentSelection()
		if self.providers and (ref.flags & 7) == 7:
			if 'provider' in ref.toString():
				self.close(ref)
			else:
				self.enterPath(ref)
		elif (ref.flags & 7) == 7:
			self.enterPath(ref)
		elif not (ref.flags & 64):
			self.close(ref)

	def setModeTv(self):
		self.setTvMode()
		if self.providers:
			self.showProviders()
		else:
			self.showFavourites()

	def setModeRadio(self):
		self.setRadioMode()
		if self.providers:
			self.showProviders()
		else:
			self.showFavourites()

def restartAutocam(self, cam, pip=False):
	def doStop():
		timer.stop()
		self.camCtrl.command('stop')
		timer.callback.remove(doStop)
		timer.callback.append(doStart)
		timer.start(100, True)

	def doStart():
		timer.stop()
		self.camCtrl.select(cam)
		self.camCtrl.command('start')
		if config.plugins.SoftcamSetup.autocam.switchinfo.value:
                        if msgbox:
			        msgbox.close()
		if pip:
			if not self.session.pip.playService(oldref):
				self.session.pip.playService(None)
		else:
			self.session.nav.playService(oldref)
	
	if pip:
		oldref = self.session.pip.getCurrentService()
	else:
		oldref = self.session.nav.getCurrentlyPlayingServiceReference()
	self.session.nav.stopService()
	
	self.hide()
	if config.plugins.SoftcamSetup.autocam.switchinfo.value:
                from Screens.MessageBox import MessageBox
	        msgbox = self.session.open(MessageBox, _("Switch camd:\n '%s' to '%s'")%(self.camCtrl.current(), cam), MessageBox.TYPE_INFO)
	        msgbox.setTitle(_("Auto-Camd"))
	
	from enigma import eTimer
	timer = eTimer()
	timer.callback.append(doStop)
	timer.start(100, True)

# ChannelSelection setHistoryPath
defHistoryPath = None
def hew_setHistoryPath(self, doZap=True):
	if not config.plugins.SoftcamSetup.autocam.enabled.value:
		defHistoryPath(self, doZap)
	else:
		ref = self.session.nav.getCurrentlyPlayingServiceReference()
		defHistoryPath(self, doZap)
		nref = self.session.nav.getCurrentlyPlayingServiceReference()
		if nref and self.session.pipshown == False:
		#if nref:
			if ref is None or ref != nref:
				if not hasattr(self, 'camCtrl'):
					from camcontrol import CamControl
					self.camCtrl = CamControl('softcam')
				try:
					from enigma import iServiceInformation
					provname = self.session.nav.getCurrentService().info().getInfoString(iServiceInformation.sProvider)
				except:
					provname = None
				camname = getAutoCamForService(nref, provname)
				camcurrent = self.camCtrl.current()
				if camname and camname != camcurrent:
					if not config.plugins.SoftcamSetup.autocam.checkrec.value:
						self.restartAutocam(camname)
					else:
						if not self.session.nav.RecordTimer.isRecording():
							self.restartAutocam(camname)
				elif not camname and camcurrent != config.plugins.SoftcamSetup.autocam.defcam.value:
					if not config.plugins.SoftcamSetup.autocam.checkrec.value:
						self.restartAutocam(config.plugins.SoftcamSetup.autocam.defcam.value)
					else:
						if not self.session.nav.RecordTimer.isRecording():
							self.restartAutocam(config.plugins.SoftcamSetup.autocam.defcam.value)

# ChannelSelection zap
defZap = None
def newZap(self, enable_pipzap = False, preview_zap = False, checkParentalControl=True, ref=None):
	if not config.plugins.SoftcamSetup.autocam.enabled.value:
		defZap(self, enable_pipzap, preview_zap, checkParentalControl, ref)
	else:
		nref = self.getCurrentSelection()
		isPip = enable_pipzap and self.dopipzap
		if isPip:
			r = self.session.pip.getCurrentService()
		else:
			r = self.session.nav.getCurrentlyPlayingServiceReference()
		defZap(self, enable_pipzap, preview_zap, checkParentalControl, ref)
		if not preview_zap and self.session.pipshown == False: #not self.dopipzap:
			if r is None or r != nref:
				if not hasattr(self, 'camCtrl'):
					from camcontrol import CamControl
					self.camCtrl = CamControl('softcam')
				try:
					from enigma import iServiceInformation
					provname = self.session.nav.getCurrentService().info().getInfoString(iServiceInformation.sProvider)
				except:
					provname = None
				camname = getAutoCamForService(nref, provname)
				camcurrent = self.camCtrl.current()
				if camname and camname != camcurrent:
					if not config.plugins.SoftcamSetup.autocam.checkrec.value:
						self.restartAutocam(camname, isPip)
					else:
						if not self.session.nav.RecordTimer.isRecording():
							self.restartAutocam(camname, isPip)
				elif not camname and camcurrent != config.plugins.SoftcamSetup.autocam.defcam.value:
					if not config.plugins.SoftcamSetup.autocam.checkrec.value:
						self.restartAutocam(config.plugins.SoftcamSetup.autocam.defcam.value, isPip)
					else:
						if not self.session.nav.RecordTimer.isRecording():
							self.restartAutocam(config.plugins.SoftcamSetup.autocam.defcam.value, isPip)

def StartMainSession(session):
	global defZap
	global defHistoryPath
	if defZap is None:
		defZap = ChannelSelection.zap
	ChannelSelection.zap = newZap
	if defHistoryPath is None:
		defHistoryPath = ChannelSelection.setHistoryPath
	ChannelSelection.setHistoryPath = hew_setHistoryPath
	ChannelSelection.restartAutocam = restartAutocam
