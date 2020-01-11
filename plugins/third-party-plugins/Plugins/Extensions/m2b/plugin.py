# m2u converter config plugin
# Copyright (c) 2boom 2015-16
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
from Tools.Directories import fileExists
from GlobalActions import globalActionMap
from keymapparser import readKeymap, removeKeymap
from os import environ
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Console import Console as iConsole
from Components.Language import language
from Components.config import config, getConfigListEntry, ConfigText, ConfigInteger, ConfigSubsection, configfile, ConfigSelection, ConfigPassword, NoSave
from Components.ConfigList import ConfigListScreen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Components.Sources.StaticText import StaticText
import os
import gettext
from os import environ

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("m2b", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/m2b/locale/"))

def _(txt):
	t = gettext.dgettext("m2b", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t
	
def get_m3u_name():
	m3u_name = []
	#dirs = os.listdir("/tmp/")
	dirs = os.listdir(config.plugins.m2b.path.value)
	for m3u_file in dirs:
		if m3u_file.endswith(".m3u") or m3u_file.endswith(".xml"):
			if 'weather' not in m3u_file:
				m3u_name.append(m3u_file)
	return m3u_name

def remove_line(filename, what):
	if os.path.isfile(filename):
		file_read = open(filename).readlines()
		file_write = open(filename, 'w')
		for line in file_read:
			if what not in line:
				file_write.write(line)
		file_write.close()
		
def mountp():
	pathmp = []
	if os.path.isfile('/proc/mounts'):
		for line in open('/proc/mounts'):
			if '/dev/sd' in line or '/dev/disk/by-uuid/' in line or '/dev/mmc' in line or '/dev/mtdblock' in line:
				pathmp.append(line.split()[1].replace('\\040', ' ') + '/')
	pathmp.append('/tmp/')
	return pathmp

config.plugins.m2b = ConfigSubsection()
config.plugins.m2b.path = ConfigSelection(choices = mountp())
config.plugins.m2b.m3ufile = ConfigSelection(choices = get_m3u_name())
config.plugins.m2b.type = ConfigSelection(default = "LiveStreamerhls", choices = [
		("LiveStreamerhls", _("LiveStreamer/hls")),
		("LiveStreamerhlsvariant", _("LiveStreamer/hlsvariant")),
		("Gstreamer", _("Gstreamer")),
		("Multicast", _("Multicast")),
])
config.plugins.m2b.passw = ConfigPassword(default='', visible_width = 50, fixed_size = False)
##############################################################################
class m2b_setup(ConfigListScreen, Screen):
	skin = """
<screen name="m2b_setup" position="center,160" size="750,147" title="2boom's m3u/xml bouquet converter">
  <widget position="15,5" size="720,100" name="config" scrollbarMode="showOnDemand" />
   <ePixmap position="10,140" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/m2b/images/red.png" alphatest="blend" />
  <widget source="key_red" render="Label" position="10,110" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
  <ePixmap position="175,140" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/m2b/images/green.png" alphatest="blend" />
  <widget source="key_green" render="Label" position="175,110" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
  </screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("2boom's m3u/xml bouquet converter"))
		config.plugins.m2b.m3ufile = ConfigSelection(choices = get_m3u_name())
		self.list = []
		self.list.append(getConfigListEntry(_("Select path"), config.plugins.m2b.path))
		self.list.append(getConfigListEntry(_("Select m3u/xml file"), config.plugins.m2b.m3ufile))
		self.list.append(getConfigListEntry(_("Select type"), config.plugins.m2b.type))
		self.list.append(getConfigListEntry(_("Input password (if needed)"), config.plugins.m2b.passw))
		ConfigListScreen.__init__(self, self.list, session=session)
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Convert"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "EPGSelectActions"],
		{
			"red": self.cancel,
			"cancel": self.cancel,
			"green": self.convert,
			"ok": self.convert
		}, -2)

	def cancel(self):
		config.plugins.m2b.passw.save()
		config.plugins.m2b.path.save()
		config.save()
		self.session.openWithCallback(self.close, get_chlist)

	def convert(self):
		self.session.open(create_bouquet)

SKIN_DWN = """
<screen name="get_chlist" position="center,140" size="625,35" title="Please wait">
  <widget source="status" render="Label" position="10,5" size="605,22" zPosition="2" font="Regular; 20" halign="center" transparent="2" />
</screen>"""

class create_bouquet(Screen):
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self.skin = SKIN_DWN
		BFNAME = 'userbouquet.%s.tv' % config.plugins.m2b.m3ufile.value
		self.setTitle(_("Please wait"))
		self["status"] = StaticText()
		self.iConsole = iConsole()
		self["status"].text = _("Converting %s" % config.plugins.m2b.m3ufile.value)
		desk_tmp = hls_opt = ''
		in_bouquets = 0
		if os.path.isfile('/tmp/%s' % config.plugins.m2b.m3ufile.value):
			print config.plugins.m2b.type.value
			if os.path.isfile('/etc/enigma2/%s' % BFNAME):
				os.remove('/etc/enigma2/%s' % BFNAME)
			if config.plugins.m2b.type.value is 'LiveStreamerhls':
				hls_opt = 'hls'
			elif config.plugins.m2b.type.value is 'LiveStreamerhlsvariant':
				hls_opt = 'hlsvariant'
			with open('/etc/enigma2/%s' % BFNAME, 'w') as outfile:
				outfile.write('#NAME %s\r\n' % config.plugins.m2b.m3ufile.value.capitalize())
				for line in open('/tmp/%s' % config.plugins.m2b.m3ufile.value):
					if line.startswith('http://'):
						if config.plugins.m2b.type.value is 'LiveStreamerhls' or config.plugins.m2b.type.value is 'LiveStreamerhlsvariant':
							outfile.write('#SERVICE 1:0:1:0:0:0:0:0:0:0:http%%3a//127.0.0.1%%3a88/%s%%3a//%s' % (hls_opt, line.replace(':', '%3a')))
						elif config.plugins.m2b.type.value is 'Gstreamer':
							outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
						elif config.plugins.m2b.type.value is 'Multicast':
							outfile.write('#SERVICE 1:0:1:0:0:0:0:0:0:0:%s' % line.replace(':', '%3a'))
						outfile.write('#DESCRIPTION %s' % desk_tmp)
					elif line.startswith('#EXTINF'):
						desk_tmp = '%s' % line.split(',')[-1]
					elif '<stream_url><![CDATA' in line:
						if config.plugins.m2b.type.value is 'LiveStreamerhls' or config.plugins.m2b.type.value is 'LiveStreamerhlsvariant':
							outfile.write('#SERVICE 1:0:1:0:0:0:0:0:0:0:http%%3a//127.0.0.1%%3a88/%s%%3a//%s\r\n' % (hls_opt, line.split('[')[-1].split(']')[0].replace(':', '%3a')))
						elif config.plugins.m2b.type.value is 'Gstreamer':
							outfile.write('#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
						elif config.plugins.m2b.type.value is 'Multicast':
							outfile.write('#SERVICE 1:0:1:0:0:0:0:0:0:0:%s\r\n' % line.split('[')[-1].split(']')[0].replace(':', '%3a'))
						outfile.write('#DESCRIPTION %s\r\n' % desk_tmp)
					elif '<title>' in line:
						if '<![CDATA[' in line:
							desk_tmp = '%s\r\n' % line.split('[')[-1].split(']')[0]
						else:
							desk_tmp = '%s\r\n' % line.split('<')[1].split('>')[1]
				outfile.write('\r\n')			
				outfile.close()
			if os.path.isfile('/etc/enigma2/bouquets.tv'):
				for line in open('/etc/enigma2/bouquets.tv'):
					if BFNAME in line:
						in_bouquets = 1
				if in_bouquets is 0:
					if os.path.isfile('/etc/enigma2/%s' % BFNAME) and os.path.isfile('/etc/enigma2/bouquets.tv'):
						remove_line('/etc/enigma2/bouquets.tv', BFNAME)
						remove_line('/etc/enigma2/bouquets.tv', 'LastScanned')
						with open('/etc/enigma2/bouquets.tv', 'a') as outfile:
							outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\r\n' % BFNAME)
							outfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.LastScanned.tv" ORDER BY bouquet\r\n')
							outfile.close()
		else:
			self["status"].text = _("Not Found m3u file")
		self.iConsole.ePopen('sleep 3', self.cancel)

	def cancel(self, result, retval, extra_args):
		self.close()

class get_chlist(Screen):
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self.skin = SKIN_DWN
		self.setTitle(_("Please wait"))
		self["status"] = StaticText()
		self.iConsole = iConsole()
		self["status"].text = _("Reload servicelist")
		if config.plugins.m2b.passw.value is not '':
			config.plugins.m2b.passw.value = ':' + config.plugins.m2b.passw.value
		self.iConsole.ePopen('wget -q -O - http://root%s@127.0.0.1/web/servicelistreload?mode=0 && sleep 2' % config.plugins.m2b.passw.value, self.quit)
	
	def quit(self, result, retval, extra_args):
		config.plugins.m2b.passw.value = config.plugins.m2b.passw.value.lstrip(':')
		self.close(False)

def main(session, **kwargs):
	session.open(m2b_setup)

def Plugins(**kwargs):
	list = [PluginDescriptor(name=_("m3u2xml bouquet converter"), description=_("m3u to bouquet converter"), where = [PluginDescriptor.WHERE_PLUGINMENU], icon="m2b.png", fnc=main)]
	list.append(PluginDescriptor(name=_("m3u2xml bouquet converter"), description=_("m3u to bouquet converter"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main))
	return list
