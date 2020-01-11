from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Button import Button

from bitrate import Bitrate

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
    lang = language.getLanguage()[:2] # getLanguage returns e.g. "fi_FI" for "language_country"
    os_environ["LANGUAGE"] = lang # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
    gettext.bindtextdomain("Bitrate", resolveFilename(SCOPE_PLUGINS, "Extensions/Bitrate/locale"))

def _(txt):
    t = gettext.dgettext("Bitrate", txt)
    if t == txt:
        print "[Bitrate] fallback to default translation for", txt
        t = gettext.gettext(txt)
    return t

localeInit()
language.addCallback(localeInit)

class BitrateViewer(Screen):
	skin = """
	<screen position="c-175,c-75" size="350,230" title="Bitrate viewer">
		<eLabel position="5,10" size="80,20" text="video" font="Regular;16" />
		<eLabel position="5,30" size="80,20" text="min" font="Regular;16" />
		<widget name="vmin" position="5,50" size="80,20" font="Regular;16" />
		<eLabel position="85,30" size="80,20" text="max" font="Regular;16" />
		<widget name="vmax" position="85,50" size="80,20" font="Regular;16" />
		<eLabel position="165,30" size="80,20" text="average" font="Regular;16" />
		<widget name="vavg" position="165,50" size="80,20" font="Regular;16" />
		<eLabel position="245,30" size="80,20" text="current" font="Regular;16" />
		<widget name="vcur" position="245,50" size="80,20" font="Regular;16" />
		<eLabel position="5,80" size="80,20" text="audio" font="Regular;16" />
		<eLabel position="5,100" size="80,20" text="min" font="Regular;16" />
		<widget name="amin" position="5,120" size="80,20" font="Regular;16" />
		<eLabel position="85,100" size="80,20" text="max" font="Regular;16" />
		<widget name="amax" position="85,120" size="80,20" font="Regular;16" />
		<eLabel position="165,100" size="80,20" text="average" font="Regular;16" />
		<widget name="aavg" position="165,120" size="80,20" font="Regular;16" />
		<eLabel position="245,100" size="80,20" text="current" font="Regular;16" />
		<widget name="acur" position="245,120" size="80,20" font="Regular;16" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="c-70,e-45" zPosition="0" size="140,40" alphatest="on" />
		<widget name="cancel" position="c-70,e-45" size="140,40" valign="center" halign="center" zPosition="1" font="Regular;20" transparent="1" backgroundColor="red" />
	</screen>"""

	def __init__(self, session):
		self.skin = BitrateViewer.skin
		Screen.__init__(self, session)
		self.bitrate = Bitrate(session, self.refreshEvent, self.bitrateStopped)

		self["cancel"] = Button(_("Exit"))
		self["vmin"] = Label("")
		self["vmax"] = Label("")
		self["vavg"] = Label("")
		self["vcur"] = Label("")
		self["amin"] = Label("")
		self["amax"] = Label("")
		self["aavg"] = Label("")
		self["acur"] = Label("")

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.keyCancel,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
		}, -2)

		self.onLayoutFinish.append(self.bitrate.start) # dont start before gui is finished

	def refreshEvent(self):
		self["vmin"].setText(self.bitrate.vmin)
		self["vmax"].setText(self.bitrate.vmax)
		self["vavg"].setText(self.bitrate.vavg)
		self["vcur"].setText(self.bitrate.vcur)
		self["amin"].setText(self.bitrate.amin)
		self["amax"].setText(self.bitrate.amax)
		self["aavg"].setText(self.bitrate.aavg)
		self["acur"].setText(self.bitrate.acur)

	def keyCancel(self):
		self.bitrate.stop()
		self.close()

	def bitrateStopped(self, retval):
		self.close()

def main(session, **kwargs):
	session.open(BitrateViewer)

def Plugins(**kwargs):
	return PluginDescriptor(name = _("Bitrate viewer"), description = _("Lets you view the bitrate"), where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc = main)