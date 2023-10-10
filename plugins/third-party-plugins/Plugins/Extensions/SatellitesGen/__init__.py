from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import os
import gettext

def localeInit():
    lang = language.getLanguage()
    os.environ['LANGUAGE'] = lang[:2]
    gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
    gettext.textdomain('enigma2')
    gettext.bindtextdomain('SatellitesGen', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/SatellitesGen/locale/'))


def _(txt):
    t = gettext.dgettext('SatellitesGen', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)
