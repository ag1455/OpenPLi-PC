# uncompyle6 version 2.9.8
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.6 (default, Oct 26 2016, 20:32:47) 
# [GCC 4.8.4]
# Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/piconload/__init__.py
# Compiled at: 2013-11-02 23:18:57
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import os
import gettext

def localeInit():
    lang = language.getLanguage()
    os.environ['LANGUAGE'] = lang[:2]
    gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
    gettext.textdomain('enigma2')
    gettext.bindtextdomain('piconload', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/piconload/locale/'))


def _(txt):
    t = gettext.dgettext('piconload', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)