from Screens.Screen import Screen
from Components.Button import Button
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_SKIN, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from Tools.BoundFunction import boundFunction
from enigma import eServiceReference, eServiceCenter
from Screens.ChannelSelection import BouquetSelector
from Screens.MessageBox import MessageBox

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
    lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
    os_environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
    gettext.bindtextdomain("BouquetHotkeys", resolveFilename(SCOPE_PLUGINS, "Extensions/BouquetHotkeys/locale"))

def _(txt):
    t = gettext.dgettext("BouquetHotkeys", txt)
    if t == txt:
        print "[BouquetHotkeys] fallback to default translation for", txt
        t = gettext.gettext(txt)
    return t

localeInit()
language.addCallback(localeInit)

class HotkeysSetupScreen(Screen):
	skin = """<screen position="center,center" size="520,400" title="Bouquet Hotkeys Setup" >
			<ePixmap pixmap="skin_default/buttons/red-big.png" position="10,10" size="200,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green-big.png" position="310,10" size="200,40" alphatest="on" />
			<widget name="key_red" position="10,10" zPosition="1" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_green" position="310,10" zPosition="1" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="entrylist" render="Listbox" position="10,70" size="500,250" scrollbarMode="showOnDemand" zPosition="1" >
				<convert type="TemplatedMultiContent">
					{"template": [
							MultiContentEntryText(pos = (60, 0), size = (420, 25), flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 1),
							MultiContentEntryPixmapAlphaTest(pos = (10, 0), size = (35, 25), png = 2), # index 2 is the pixmap (skin_default/icons/lock_o*.png - 25x24, skin_default/buttons/key_*.png - 35x25)
							MultiContentEntryText(pos = (10, 0), size = (35, 25), flags = RT_HALIGN_CENTER | RT_VALIGN_CENTER, text = 3),
						], "fonts": [gFont("Regular", 20)], "itemHeight": 25
					}
				</convert>
			</widget>
			<widget name="hint" position="10,350" size="500,50" font="Regular;19" halign="center" transparent="1" />
		</screen>"""
	def __init__(self, session, args = None):
		self.bouquet_root_tv = eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet')
		self.bouquet_root_radio = eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet')
		Screen.__init__(self, session)

		self["Title"].text= _("Bouquet Hotkeys Setup")
		self["key_green"] = Button(_("Save"))
		self["key_red"] = Button(_("Cancel"))
		self["hint"] = Label(_("Press OK button to change..."))
		self["actions"] = ActionMap(["SetupActions"],
		{
			"cancel": self.keyRed,	# KEY_RED, KEY_ESC
			"ok": self.keyOk,	# KEY_OK
			"save": self.keyGreen,	# KEY_GREEN
#			"left": self.keyLeft,	# KEY_LEFT
#			"right": self.keyRight,	# KEY_RIGHT
		}, -1)

		self.prev_list = [config.usage.bouquethotkeys.value]
		for x in range(1, 10):
			self.prev_list.append(eval("config.plugins.BouquetHotkeys.key"+str(x)).value)

		self.list = []
		self["entrylist"] = List(self.list)

		self.onClose.append(self.__closed)
		self.onLayoutFinish.append(self.__layoutFinished)

	def __closed(self):
		pass

	def __layoutFinished(self):
		self.updateEntryList()

	def setEntryComponent(self, file, name, index):
		png = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, file + ".png")) or \
			LoadPixmap(resolveFilename(SCOPE_SKIN, "skin_default/" + file + ".png"))
		hint = not png and index <> 0 and str(index) or ""
		return (index, name, png, hint)

	def updateEntryList(self):
		idx = 0
		if not config.usage.bouquethotkeys.value:
			list = [self.setEntryComponent("icons/lock_off", _("Enable bouquet hotkeys"), 0)]
		else:
			if len(self.list):
				idx = self["entrylist"].index
			serviceHandler = eServiceCenter.getInstance()
			list = [self.setEntryComponent("icons/lock_on", _("Disable bouquet hotkeys"), 0)]
			for x in range(1, 10):
				sx = str(x)
				name = eval("config.plugins.BouquetHotkeys.key"+sx).value
				if not name in ("", "none"):
					ref = eServiceReference(name)
					info = serviceHandler.info(ref)
					if info:
						name = info.getName(ref)
				list.append(self.setEntryComponent("buttons/key_" + sx, name, x))
		self.list = list
		self["entrylist"].setList(self.list)
		self["entrylist"].index = idx

	def getBouquetList(self, root):
		bouquets = [ ]
		serviceHandler = eServiceCenter.getInstance()
		bouquetlist = serviceHandler.list(root)
		if bouquetlist:
			while True:
				s = bouquetlist.getNext()
				if not s.valid(): break
				if s.flags & eServiceReference.isDirectory:
					info = serviceHandler.info(s)
					if info: bouquets.append((info.getName(s), s))
		return bouquets

	def keyOk(self):
		idx = self["entrylist"].index
		if idx == 0:
			config.usage.bouquethotkeys.value = not config.usage.bouquethotkeys.value
			#config.usage.bouquethotkeys.save()
			self.updateEntryList()
		elif 0 < idx < 10:
			bouquets = self.getBouquetList(self.bouquet_root_tv) + self.getBouquetList(self.bouquet_root_radio)
			if bouquets:
				bouquets.insert(0, ("none", -1))
				#self.session.openWithCallback(self.closed, BouquetSelector, bouquets, self.openBouquetEPG, enableWrapAround=True)
				self.selBouquet = self.session.open(BouquetSelector, bouquets, boundFunction(self.changeHotkey, idx), enableWrapAround=True)
			else:
				self.session.open(MessageBox, _("Sorry, but bouquets not found"))

	def changeHotkey(self, index, ref):
		if isinstance(ref, eServiceReference):
			val = ref.toString()
		else:
			val = "none"
		eval("config.plugins.BouquetHotkeys.key"+str(index)).value = val
		#eval("config.plugins.BouquetHotkeys.key"+str(index)).save()
		self.updateEntryList()
		self.selBouquet.close()
		self.selBouquet = None

	def keyRed(self):
		config.usage.bouquethotkeys.value = self.prev_list[0]
		for x in range(1, 10):
			eval("config.plugins.BouquetHotkeys.key"+str(x)).value = self.prev_list[x]
		self.keyGreen()

	def keyGreen(self):
		config.usage.bouquethotkeys.save()
		for x in range(1, 10):
			eval("config.plugins.BouquetHotkeys.key"+str(x)).save()
		self.close()

	def keyLeft(self):
		pass

	def keyRight(self):
		pass