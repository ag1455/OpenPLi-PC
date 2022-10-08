# coding=utf-8
from Plugins.Plugin import PluginDescriptor
from Plugins.Extensions.SpinnerSelector.SpinnerSelectionBox import SpinnerSelectionBox
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.config import config
import os

import gettext
try:
	cat = gettext.translation('lang', '/usr/lib/enigma2/python/Plugins/Extensions/SpinnerSelector/po', [config.osd.language.getText()])
	_ = cat.gettext
except IOError:
	pass

class SpinnerSelector:
	def __init__(self,session):
		self.session = session
		path = "/usr/share/enigma2/Spinner/"
		dirs = os.listdir(path)
		dirs.sort()
		menu = []
		for dir in dirs:
			p = path + dir
			if os.path.isdir(p):
				menu.append((dir,dir))
		self.session.openWithCallback(self.menuCallback, SpinnerSelectionBox, title=_("Chose Spinner"), list=menu)

	def menuCallback(self,choice):
		if choice is None:
			return
		First = True
		for i in range(64):
			if (os.path.isfile("/usr/share/enigma2/skin_default/spinner/wait%d.png"%(i+1))):
				os.system("rm -f /usr/share/enigma2/skin_default/spinner/wait%d.png"%(i+1))
			if (os.path.isfile("/usr/share/enigma2/Spinner/%s/wait%d.png"%(choice,i+1))):
				os.system("ln -s /usr/share/enigma2/Spinner/%s/wait%d.png /usr/share/enigma2/skin_default/spinner/wait%d.png"%(choice,i+1,i+1))
				if First:
					First = False
					os.system("rm -f /usr/lib/enigma2/python/Plugins/Extensions/SpinnerSelektor/plugin.png; ln -s /usr/share/enigma2/Spinner/%s/wait%d.png /usr/lib/enigma2/python/Plugins/Extensions/SpinnerSelektor/plugin.png"%(choice,i+1));
		self.session.openWithCallback(self.restart,MessageBox,_("GUI needs a restart to apply a new spinner.\nDo you want to restart the GUI now ?"), MessageBox.TYPE_YESNO)

	def restart(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)

