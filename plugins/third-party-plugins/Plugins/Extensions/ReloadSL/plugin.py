# -*- coding: utf-8 -*-
# Reload Servicelist (ReloadSL)
# Copyright (c) 2boom 2016-17
# v.0.1-r1
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

from Plugins.Plugin import PluginDescriptor
from Components.Language import language
from Components.Console import Console as iConsole
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import os, sys, os.path
import gettext

lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("reloadsl", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/ReloadSL/locale/"))

def _(txt):
	t = gettext.dgettext("reloadsl", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t
	
SKIN_DWN = """
<screen name="reloadsl" position="center,140" size="625,35" title="Please wait">
  <widget source="status" render="Label" position="10,5" size="605,22" zPosition="2" font="Regular; 20" halign="center" transparent="2" />
</screen>"""

class reloadsl(Screen):
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self.skin = SKIN_DWN
		password = ''
		self.setTitle(_("Please wait"))
		self["status"] = StaticText()
		self.iConsole = iConsole()
		self["status"].text = _("Reload ServiceList")
		if os.path.isfile('%sExtensions/ReloadSL/password' % resolveFilename(SCOPE_PLUGINS)):
			password = open('%sExtensions/ReloadSL/password' % resolveFilename(SCOPE_PLUGINS)).read().strip().rstrip('\r').rstrip('\n')
		self.iConsole.ePopen('wget -q -O - http://root:%s@127.0.0.1/web/servicelistreload?mode=0 && sleep 2' % password, self.cancel)
		
	def cancel(self, result, retval, extra_args):
		self.close()

def main(session, **kwargs):
	session.open(reloadsl)

def Plugins(**kwargs):
	return PluginDescriptor(name=_("Reload ServiceList"), description=_("Reload ServiceList"), where = [PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main)
	#return result
