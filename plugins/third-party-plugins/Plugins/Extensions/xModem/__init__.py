from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import os,gettext

def localeInit():
	lang = language.getLanguage()[:2]
	os.environ["LANGUAGE"] = lang
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain("xModem", resolveFilename(SCOPE_PLUGINS, "Extensions/xModem/locale"))

def _(txt):
	t = gettext.dgettext("xModem", txt)
	if t == txt:
		print "[xModem] fallback to default translation for", txt
		t = gettext.gettext(txt)
	return t

localeInit()
