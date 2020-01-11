from Components.Language import language
from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import os, gettext
from skin import loadSkin
PluginLanguageDomain = 'xbmcaddons'
PluginLanguagePath = 'Extensions/XBMCAddons/locale'

def loadSkinReal(skinPath):
    if os.path.exists(skinPath):
        print '[XBMCAddons] Loading skin ', skinPath
        loadSkin(skinPath)


def loadPluginSkin(pluginPath):
#    loadSkinReal(pluginPath + '/' + config.skin.primary_skin.value)
    loadSkinReal(config.skin.primary_skin.value)
    loadSkinReal(pluginPath + '/skin.xml')


def localeInit():
#    lang = language.getLanguage()[:2]
#    os.environ['LANGUAGE'] = lang
#    print '[XBMCAddons] set language to ', lang
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


def _(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
        print '[XBMCAddons] fallback to default translation for', txt
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)

