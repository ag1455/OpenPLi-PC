# Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/TSmedia/resources/VirtualKeyBoard.py
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_CENTER, RT_VALIGN_CENTER, getPrevAsciiCode
from Screens.Screen import Screen
from Components.Language import language
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from Components.MenuList import MenuList
import os
from Screens.ChoiceBox import ChoiceBox
from twisted.web.client import getPage
from twisted.internet import reactor
import os, socket, httplib
from urllib import quote, unquote_plus, unquote, urlencode
from urlparse import parse_qs, parse_qsl
fonts = {'Body': ('Regular',
          18,
          22,
          16),
 'ChoiceList': ('Regular',
                20,
                24,
                18)}
parameters = {}

class GoogleSuggestions():

    def __init__(self, callback = None, hl = 'en'):
        self.hl = hl
        self.conn = None
        self.callback = callback
        return

    def prepareQuery(self):
        self.prepQuerry = '/complete/search?output=chrome&client=chrome&'
        if self.hl is not None:
            self.prepQuerry = self.prepQuerry + 'hl=' + self.hl + '&'
        self.prepQuerry = self.prepQuerry + 'jsonp=self.gotSuggestions&q='
        return

    def dataError(self, error):
        print 'unable to get suggestion'
        self.callback([])

    def parseData(self, output):
        print 'output', output, self.hl
        if output:
            data = output
            charset = 'ISO-8859-1'
            if self.hl == 'ar':
                charset = 'windows-1256'
            elif self.hl == 'el':
                charset = 'windows-1253'
            try:
                data = data.decode(charset).encode('utf-8')
            except:
                pass

            list = data.split(',')
            data2 = []
            for item in list:
                if self.queryString in item:
                    item = item.replace('"', '').replace('[', '').replace(']', '').replace('self.gotSuggestions(', '')
                    data2.append(item)

            if self.callback is not None:
                self.callback(data2)
                return
        else:
            self.callback([])
        return

    def getSuggestions(self, queryString, hl = 'en'):
        self.hl = hl
        self.prepareQuery()
        self.queryString = queryString
        self.reactor = reactor
        if queryString is not '':
            query = self.prepQuerry + quote(queryString)
            url = 'http://www.google.com' + query
            getPage(url, headers={'Content-Type': 'application/x-www-form-urlencoded'}).addCallback(self.parseData).addErrback(self.dataError)
        else:
            return []
class VirtualKeyBoardList(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        font = fonts.get('VirtualKeyboard', ('Regular', 28, 45))
        self.l.setFont(0, gFont(font[0], font[1]))
        self.l.setItemHeight(font[2])


def VirtualKeyBoardEntryComponent(keys, selectedKey, shiftMode = False):
    key_backspace = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_backspace.png'))
    key_bg = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_bg.png'))
    key_clr = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_clr.png'))
    key_esc = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_esc.png'))
    key_ok = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_ok.png'))
    key_sel = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_sel.png'))
    key_shift = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_shift.png'))
    key_shift_sel = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_shift_sel.png'))
    key_space = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_space.png'))
    res = [keys]
    x = 0
    count = 0
    if shiftMode:
        shiftkey_png = key_shift_sel
    else:
        shiftkey_png = key_shift
    try:
        for key in keys:
            width = None
            if key == 'EXIT':
                width = key_esc.size().width()
                res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 45), png=key_esc))
            elif key == 'BACKSPACE':
                width = key_backspace.size().width()
                res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 45), png=key_backspace))
            elif key == 'CLEAR':
                width = key_clr.size().width()
                res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 45), png=key_clr))
            elif key == 'SHIFT':
                width = shiftkey_png.size().width()
                res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 45), png=shiftkey_png))
            elif key == 'SPACE':
                width = key_space.size().width()
                res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 45), png=key_space))
            elif key == 'OK':
                width = key_ok.size().width()
                res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 45), png=key_ok))
            else:
                width = key_bg.size().width()
                res.extend((MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 45), png=key_bg), MultiContentEntryText(pos=(x, 0), size=(width, 45), font=0, text=key.encode('utf-8'), flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER)))
            if selectedKey == count:
                width = key_sel.size().width()
                res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, 45), png=key_sel))
            if width is not None:
                x += width
            else:
                x += 45
            count += 1

    except:
        pass

    return res


class VirtualKeyBoard(Screen):
    skin='''<screen name="KodiLiteVKskin" position="center,center" size="1200,560" zPosition="99" title="Virtual keyboard">
		<ePixmap pixmap="skin_default/vkey_text.png" position="300,245" zPosition="-4" size="542,52" alphatest="on" />
		<widget source="country" render="Pixmap" position="40,400" size="60,40" alphatest="on" borderWidth="2" borderColor="yellow" >
			<convert type="ValueToPixmap">LanguageCode</convert>
		</widget>
		
		<eLabel text="language" position="40,350" size="100,35" font="Regular;21" foregroundColor="white" backgroundColor="yellow" />
		<widget name="header" position="10,10" size="500,20" font="Regular;20" transparent="1" noWrap="1" />
		<widget name="text" position="302,250" size="536,46" font="Regular;42" transparent="1" noWrap="1" halign="right" />
		<widget name="list" position="300,300" size="680,240" selectionDisabled="1" transparent="1" />
	        <eLabel text="Press blue for suggestion" position="900,10" size="300,35" font="Regular;21" foregroundColor="blue" backgroundColor="white" />
                <widget name="suggestlist" position="900,50" size="300,200" selectionDisabled="1" transparent="1" />
                <eLabel text="Press red for history" position="50,10" size="300,35" font="Regular;21" foregroundColor="red" backgroundColor="white" />
                <widget name="historylist" position="50,50" size="200,200" selectionDisabled="1" transparent="1" />
              
        </screen>'''
    def __init__(self, session, title = '', text = ''):
        Screen.__init__(self, session)
        self.skinName = 'KodiLiteVKskin'
        self.keys_list = []
        self.session = session
        self.shiftkeys_list = []
        self.lang = language.getLanguage()
        self.nextLang = None
        self.shiftMode = False
        self.text = text
        self.selectedKey = 0
        self['suggestlist'] = MenuList([])
        self['historylist'] = MenuList([])
        self.key_bg = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_bg.png'))
        self.key_sel = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_sel.png'))
        self.key_backspace = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_backspace.png'))
        self.key_all = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_all.png'))
        self.key_clr = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_clr.png'))
        self.key_esc = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_esc.png'))
        self.key_ok = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_ok.png'))
        self.key_shift = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_shift.png'))
        self.key_shift_sel = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_shift_sel.png'))
        self.key_space = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_space.png'))
        self.key_left = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_left.png'))
        self.key_right = LoadPixmap(path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/vkey_right.png'))
        self.keyImages = {'BACKSPACE': self.key_backspace,
         'ALL': self.key_all,
         'EXIT': self.key_esc,
         'OK': self.key_ok,
         'SHIFT': self.key_shift,
         'SPACE': self.key_space,
         'LEFT': self.key_left,
         'RIGHT': self.key_right}
        self.keyImagesShift = {'BACKSPACE': self.key_backspace,
         'CLEAR': self.key_clr,
         'EXIT': self.key_esc,
         'OK': self.key_ok,
         'SHIFT': self.key_shift_sel,
         'SPACE': self.key_space,
         'LEFT': self.key_left,
         'RIGHT': self.key_right}
        self['country'] = StaticText('')
        self['header'] = Label('')
        self['text'] = Label(self.text)
        self['list'] = VirtualKeyBoardList([])
        self['actions'] = ActionMap(['ColorActions',
         'OkCancelActions',
         'WizardActions',
         'KeyboardInputActions',
         'InputBoxActions',         
         'InputAsciiActions',"MenuActions"], {'gotAsciiCode': self.keyGotAscii,
         
         'ok': self.okClicked,
         'cancel': self.exit,
         'left': self.left,
         'right': self.right,
         'up': self.up,
         'down': self.down,
         'red': self.history,
         'green': self.ok,
         'blue': self.suggest,
         'menu': self.showmenu, 
         'yellow': self.switchLang,
         'deleteBackward': self.backClicked,
         '0': self.insertspace,
         'back': self.exit}, -2)
        self.setLang()
        self.displayhistory()
        self.onExecBegin.append(self.setKeyboardModeAscii)
        self.onLayoutFinish.append(self.buildVirtualKeyBoard)
        self.onLayoutFinish.append(self.getsuggestion)
        self.currentlist = 'list'
        return
    def showmenu(self):
         nlines=[]
         nlines.append((str("Clear search history"), str("Clear search history")))
         self.session.openWithCallback(self.choicesback, ChoiceBox, _('select action'), nlines)

    def choicesback(self, select):
        if select:
            if select[0] == 'Clear search history':
                self.historydel()
    def historydel(self):
        self.session.openWithCallback(self.delhx, MessageBox, _('All search history items will be deleted,are you sure?'), MessageBox.TYPE_YESNO)
    def delhx(self, answer):
        if answer:
            hfile = '/etc/history'
            try:
                os.remove(hfile)
                self['historylist'].setList([])
            except:
                print 'failed to delete history'
    def suggest(self):
        debug = True
        self['suggestlist'].selectionEnabled(1)
        self['historylist'].selectionEnabled(0)
        self['list'].selectionEnabled(0)
        self.currentlist = 'suggestlist'

    def history(self):
        self['suggestlist'].selectionEnabled(0)
        self['historylist'].selectionEnabled(1)
        self['list'].selectionEnabled(0)
        self.currentlist = 'historylist'

    def displayhistory(self):
        hfile = '/etc/history'
        if not os.path.exists(hfile):
            return
        lines = open(hfile).readlines()
        list1 = []
        for line in lines:
            list1.append(line.strip())

        self['historylist'].setList(list1)

    def getsuggestion(self):
        word = self['text'].getText()
        if word.strip() == '':
            return
        
        lang = self.lang.split('_')[0]
        self.suggestions = GoogleSuggestions(self.suggestcallback, lang)
        self.suggestions.getSuggestions(word, hl=lang)

    def suggestcallback(self, data):
        if data is None:
            return
        else:
            list1 = data
            print 'list1', list1
            self['suggestlist'].setList(list1)
            return
            return

    def suggestback(self, select):
        print '143', select
        if select:
            self['text'].setText(str(select))

    def switchLang(self):
        self.lang = self.nextLang
        self.setLang()
        self.buildVirtualKeyBoard()

    def setLang(self):
        if self.lang == 'de_DE':
            self.keys_list = [[u'EXIT',
              u'1',
              u'2',
              u'3',
              u'4',
              u'5',
              u'6',
              u'7',
              u'8',
              u'9',
              u'0',
              u'BACKSPACE'],
             [u'q',
              u'w',
              u'e',
              u'r',
              u't',
              u'z',
              u'u',
              u'i',
              u'o',
              u'p',
              u'\xfc',
              u'+'],
             [u'a',
              u's',
              u'd',
              u'f',
              u'g',
              u'h',
              u'j',
              u'k',
              u'l',
              u'\xf6',
              u'\xe4',
              u'#'],
             [u'<',
              u'y',
              u'x',
              u'c',
              u'v',
              u'b',
              u'n',
              u'm',
              u',',
              '.',
              u'-',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'@',
              u'\xdf',
              u'OK']]
            self.shiftkeys_list = [[u'EXIT',
              u'!',
              u'"',
              u'\xa7',
              u'$',
              u'%',
              u'&',
              u'/',
              u'(',
              u')',
              u'=',
              u'BACKSPACE'],
             [u'Q',
              u'W',
              u'E',
              u'R',
              u'T',
              u'Z',
              u'U',
              u'I',
              u'O',
              u'P',
              u'\xdc',
              u'*'],
             [u'A',
              u'S',
              u'D',
              u'F',
              u'G',
              u'H',
              u'J',
              u'K',
              u'L',
              u'\xd6',
              u'\xc4',
              u"'"],
             [u'>',
              u'Y',
              u'X',
              u'C',
              u'V',
              u'B',
              u'N',
              u'M',
              u';',
              u':',
              u'_',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'?',
              u'\\',
              u'OK']]
            self.nextLang = 'ar_AE'
        elif self.lang == 'ar_AE':
            self.keys_list = [[u'EXIT',
              u'1',
              u'2',
              u'3',
              u'4',
              u'5',
              u'6',
              u'7',
              u'8',
              u'9',
              u'0',
              u'BACKSPACE'],
             [u'\u0636',
              u'\u0635',
              u'\u062b',
              u'\u0642',
              u'\u0641',
              u'\u063a',
              u'\u0639',
              u'\u0647',
              u'\u062e',
              u'\u062d',
              u'\u062c',
              u'\u062f'],
             [u'\u0634',
              u'\u0633',
              u'\u064a',
              u'\u0628',
              u'\u0644',
              u'\u0627',
              u'\u062a',
              u'\u0646',
              u'\u0645',
              u'\u0643',
              u'\u0637',
              u'\u0630'],
             [u'\u0626',
              u'\u0621',
              u'\u0624',
              u'\u0631',
              u'\u0644\u0627',
              u'\u0649',
              u'\u0629',
              u'\u0648',
              u'\u0632',
              '\xd8\xb8',
              u'#',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'-',
              u'@',
              u'.',
              u'\u0644\u0622',
              u'\u0622',
              u'\u0644\u0623',
              u'\u0644\u0625',
              u'\u0625',
              u'\u0623',
              u'OK']]
            self.shiftkeys_list = [[u'EXIT',
              u'!',
              u'"',
              u'\xa7',
              u'$',
              u'^',
              u'<',
              u'>',
              u'(',
              u')',
              u'=',
              u'BACKSPACE'],
             [u'\u064e',
              u'\u064b',
              u'\u064f',
              u'\u064c',
              u'%',
              u'\u060c',
              u'\u2018',
              u'\xf7',
              u'\xd7',
              u'\u061b',
              u'<',
              u'>'],
             [u'\u0650',
              u'\u064d',
              u']',
              u'[',
              u'*',
              u'+',
              u'\u0640',
              u'\u060c',
              u'/',
              u':',
              u'~',
              u"'"],
             [u'\u0652',
              u'}',
              u'{',
              u'-',
              u'/',
              u'\u2019',
              u',',
              u'.',
              u'\u061f',
              u':',
              u'_',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'?',
              u'\\',
              u'=',
              u'\u0651',
              u'~',
              u'OK']]
            self.nextLang = 'es_ES'
        elif self.lang == 'es_ES':
            self.keys_list = [[u'EXIT',
              u'1',
              u'2',
              u'3',
              u'4',
              u'5',
              u'6',
              u'7',
              u'8',
              u'9',
              u'0',
              u'BACKSPACE'],
             [u'q',
              u'w',
              u'e',
              u'r',
              u't',
              u'z',
              u'u',
              u'i',
              u'o',
              u'p',
              u'\xfa',
              u'+'],
             [u'a',
              u's',
              u'd',
              u'f',
              u'g',
              u'h',
              u'j',
              u'k',
              u'l',
              u'\xf3',
              u'\xe1',
              u'#'],
             [u'<',
              u'y',
              u'x',
              u'c',
              u'v',
              u'b',
              u'n',
              u'm',
              u',',
              '.',
              u'-',
              u'ALL'],
             [u'SHIFT',
              u'SPACE',
              u'@',
              u'\u0141',
              u'\u0155',
              u'\xe9',
              u'\u010d',
              u'\xed',
              u'\u011b',
              u'\u0144',
              u'\u0148',
              u'OK']]
            self.shiftkeys_list = [[u'EXIT',
              u'!',
              u'"',
              u'\xa7',
              u'$',
              u'%',
              u'&',
              u'/',
              u'(',
              u')',
              u'=',
              u'BACKSPACE'],
             [u'Q',
              u'W',
              u'E',
              u'R',
              u'T',
              u'Z',
              u'U',
              u'I',
              u'O',
              u'P',
              u'\xda',
              u'*'],
             [u'A',
              u'S',
              u'D',
              u'F',
              u'G',
              u'H',
              u'J',
              u'K',
              u'L',
              u'\xd3',
              u'\xc1',
              u"'"],
             [u'>',
              u'Y',
              u'X',
              u'C',
              u'V',
              u'B',
              u'N',
              u'M',
              u';',
              u':',
              u'_',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'?',
              u'\\',
              u'\u0154',
              u'\xc9',
              u'\u010c',
              u'\xcd',
              u'\u011a',
              u'\u0143',
              u'\u0147',
              u'OK']]
            self.nextLang = 'fi_FI'
        elif self.lang == 'fi_FI':
            self.keys_list = [[u'EXIT',
              u'1',
              u'2',
              u'3',
              u'4',
              u'5',
              u'6',
              u'7',
              u'8',
              u'9',
              u'0',
              u'BACKSPACE'],
             [u'q',
              u'w',
              u'e',
              u'r',
              u't',
              u'z',
              u'u',
              u'i',
              u'o',
              u'p',
              u'\xe9',
              u'+'],
             [u'a',
              u's',
              u'd',
              u'f',
              u'g',
              u'h',
              u'j',
              u'k',
              u'l',
              u'\xf6',
              u'\xe4',
              u'#'],
             [u'<',
              u'y',
              u'x',
              u'c',
              u'v',
              u'b',
              u'n',
              u'm',
              u',',
              '.',
              u'-',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'@',
              u'\xdf',
              u'\u013a',
              u'OK']]
            self.shiftkeys_list = [[u'EXIT',
              u'!',
              u'"',
              u'\xa7',
              u'$',
              u'%',
              u'&',
              u'/',
              u'(',
              u')',
              u'=',
              u'BACKSPACE'],
             [u'Q',
              u'W',
              u'E',
              u'R',
              u'T',
              u'Z',
              u'U',
              u'I',
              u'O',
              u'P',
              u'\xc9',
              u'*'],
             [u'A',
              u'S',
              u'D',
              u'F',
              u'G',
              u'H',
              u'J',
              u'K',
              u'L',
              u'\xd6',
              u'\xc4',
              u"'"],
             [u'>',
              u'Y',
              u'X',
              u'C',
              u'V',
              u'B',
              u'N',
              u'M',
              u';',
              u':',
              u'_',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'?',
              u'\\',
              u'\u0139',
              u'OK']]
            self.nextLang = 'sv_SE'
        elif self.lang == 'sv_SE':
            self.keys_list = [[u'EXIT',
              u'1',
              u'2',
              u'3',
              u'4',
              u'5',
              u'6',
              u'7',
              u'8',
              u'9',
              u'0',
              u'BACKSPACE'],
             [u'q',
              u'w',
              u'e',
              u'r',
              u't',
              u'z',
              u'u',
              u'i',
              u'o',
              u'p',
              u'\xe9',
              u'+'],
             [u'a',
              u's',
              u'd',
              u'f',
              u'g',
              u'h',
              u'j',
              u'k',
              u'l',
              u'\xf6',
              u'\xe4',
              u'#'],
             [u'<',
              u'y',
              u'x',
              u'c',
              u'v',
              u'b',
              u'n',
              u'm',
              u',',
              '.',
              u'-',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'@',
              u'\xdf',
              u'\u013a',
              u'OK']]
            self.shiftkeys_list = [[u'EXIT',
              u'!',
              u'"',
              u'\xa7',
              u'$',
              u'%',
              u'&',
              u'/',
              u'(',
              u')',
              u'=',
              u'BACKSPACE'],
             [u'Q',
              u'W',
              u'E',
              u'R',
              u'T',
              u'Z',
              u'U',
              u'I',
              u'O',
              u'P',
              u'\xc9',
              u'*'],
             [u'A',
              u'S',
              u'D',
              u'F',
              u'G',
              u'H',
              u'J',
              u'K',
              u'L',
              u'\xd6',
              u'\xc4',
              u"'"],
             [u'>',
              u'Y',
              u'X',
              u'C',
              u'V',
              u'B',
              u'N',
              u'M',
              u';',
              u':',
              u'_',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'?',
              u'\\',
              u'\u0139',
              u'OK']]
            self.nextLang = 'sk_SK'
        elif self.lang == 'sk_SK':
            self.keys_list = [[u'EXIT',
              u'1',
              u'2',
              u'3',
              u'4',
              u'5',
              u'6',
              u'7',
              u'8',
              u'9',
              u'0',
              u'BACKSPACE'],
             [u'q',
              u'w',
              u'e',
              u'r',
              u't',
              u'z',
              u'u',
              u'i',
              u'o',
              u'p',
              u'\xfa',
              u'+'],
             [u'a',
              u's',
              u'd',
              u'f',
              u'g',
              u'h',
              u'j',
              u'k',
              u'l',
              u'\u013e',
              u'@',
              u'#'],
             [u'<',
              u'y',
              u'x',
              u'c',
              u'v',
              u'b',
              u'n',
              u'm',
              u',',
              '.',
              u'-',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'\u0161',
              u'\u010d',
              u'\u017e',
              u'\xfd',
              u'\xe1',
              u'\xed',
              u'\xe9',
              u'OK']]
            self.shiftkeys_list = [[u'EXIT',
              u'!',
              u'"',
              u'\xa7',
              u'$',
              u'%',
              u'&',
              u'/',
              u'(',
              u')',
              u'=',
              u'BACKSPACE'],
             [u'Q',
              u'W',
              u'E',
              u'R',
              u'T',
              u'Z',
              u'U',
              u'I',
              u'O',
              u'P',
              u'\u0165',
              u'*'],
             [u'A',
              u'S',
              u'D',
              u'F',
              u'G',
              u'H',
              u'J',
              u'K',
              u'L',
              u'\u0148',
              u'\u010f',
              u"'"],
             [u'\xc1',
              u'\xc9',
              u'\u010e',
              u'\xcd',
              u'\xdd',
              u'\xd3',
              u'\xda',
              u'\u017d',
              u'\u0160',
              u'\u010c',
              u'\u0164',
              u'\u0147'],
             [u'>',
              u'Y',
              u'X',
              u'C',
              u'V',
              u'B',
              u'N',
              u'M',
              u';',
              u':',
              u'_',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'?',
              u'\\',
              u'\xe4',
              u'\xf6',
              u'\xfc',
              u'\xf4',
              u'\u0155',
              u'\u013a',
              u'OK']]
            self.nextLang = 'cs_CZ'
        elif self.lang == 'cs_CZ':
            self.keys_list = [[u'EXIT',
              u'1',
              u'2',
              u'3',
              u'4',
              u'5',
              u'6',
              u'7',
              u'8',
              u'9',
              u'0',
              u'BACKSPACE'],
             [u'q',
              u'w',
              u'e',
              u'r',
              u't',
              u'z',
              u'u',
              u'i',
              u'o',
              u'p',
              u'\xfa',
              u'+'],
             [u'a',
              u's',
              u'd',
              u'f',
              u'g',
              u'h',
              u'j',
              u'k',
              u'l',
              u'\u016f',
              u'@',
              u'#'],
             [u'<',
              u'y',
              u'x',
              u'c',
              u'v',
              u'b',
              u'n',
              u'm',
              u',',
              '.',
              u'-',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'\u011b',
              u'\u0161',
              u'\u010d',
              u'\u0159',
              u'\u017e',
              u'\xfd',
              u'\xe1',
              u'\xed',
              u'\xe9',
              u'OK']]
            self.shiftkeys_list = [[u'EXIT',
              u'!',
              u'"',
              u'\xa7',
              u'$',
              u'%',
              u'&',
              u'/',
              u'(',
              u')',
              u'=',
              u'BACKSPACE'],
             [u'Q',
              u'W',
              u'E',
              u'R',
              u'T',
              u'Z',
              u'U',
              u'I',
              u'O',
              u'P',
              u'\u0165',
              u'*'],
             [u'A',
              u'S',
              u'D',
              u'F',
              u'G',
              u'H',
              u'J',
              u'K',
              u'L',
              u'\u0148',
              u'\u010f',
              u"'"],
             [u'>',
              u'Y',
              u'X',
              u'C',
              u'V',
              u'B',
              u'N',
              u'M',
              u';',
              u':',
              u'_',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'?',
              u'\\',
              u'\u010c',
              u'\u0158',
              u'\u0160',
              u'\u017d',
              u'\xda',
              u'\xc1',
              u'\xc9',
              u'OK']]
            self.nextLang = 'el_GR'
        elif self.lang == 'el_GR':
            self.keys_list = [[u'EXIT',
              u'1',
              u'2',
              u'3',
              u'4',
              u'5',
              u'6',
              u'7',
              u'8',
              u'9',
              u'0',
              u'BACKSPACE'],
             [u'=',
              u'\u03c2',
              u'\u03b5',
              u'\u03c1',
              u'\u03c4',
              u'\u03c5',
              u'\u03b8',
              u'\u03b9',
              u'\u03bf',
              u'\u03c0',
              u'[',
              u']'],
             [u'\u03b1',
              u'\u03c3',
              u'\u03b4',
              u'\u03c6',
              u'\u03b3',
              u'\u03b7',
              u'\u03be',
              u'\u03ba',
              u'\u03bb',
              u';',
              u"'",
              u'-'],
             [u'\\',
              u'\u03b6',
              u'\u03c7',
              u'\u03c8',
              u'\u03c9',
              u'\u03b2',
              u'\u03bd',
              u'\u03bc',
              u',',
              '.',
              u'/',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'\u03ac',
              u'\u03ad',
              u'\u03ae',
              u'\u03af',
              u'\u03cc',
              u'\u03cd',
              u'\u03ce',
              u'\u03ca',
              u'\u03cb',
              u'OK']]
            self.shiftkeys_list = [[u'EXIT',
              u'!',
              u'@',
              u'#',
              u'$',
              u'%',
              u'^',
              u'&',
              u'*',
              u'(',
              u')',
              u'BACKSPACE'],
             [u'+',
              u'\u20ac',
              u'\u0395',
              u'\u03a1',
              u'\u03a4',
              u'\u03a5',
              u'\u0398',
              u'\u0399',
              u'\u039f',
              u'\u03a0',
              u'{',
              u'}'],
             [u'\u0391',
              u'\u03a3',
              u'\u0394',
              u'\u03a6',
              u'\u0393',
              u'\u0397',
              u'\u039e',
              u'\u039a',
              u'\u039b',
              u':',
              u'"',
              u'_'],
             [u'|',
              u'\u0396',
              u'\u03a7',
              u'\u03a8',
              u'\u03a9',
              u'\u0392',
              u'\u039d',
              u'\u039c',
              u'<',
              u'>',
              u'?',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'\u0386',
              u'\u0388',
              u'\u0389',
              u'\u038a',
              u'\u038c',
              u'\u038e',
              u'\u038f',
              u'\u03aa',
              u'\u03ab',
              u'OK']]
            self.nextLang = 'pl_PL'
        elif self.lang == 'pl_PL':
            self.keys_list = [[u'EXIT',
              u'1',
              u'2',
              u'3',
              u'4',
              u'5',
              u'6',
              u'7',
              u'8',
              u'9',
              u'0',
              u'BACKSPACE'],
             [u'q',
              u'w',
              u'e',
              u'r',
              u't',
              u'y',
              u'u',
              u'i',
              u'o',
              u'p',
              u'-',
              u'['],
             [u'a',
              u's',
              u'd',
              u'f',
              u'g',
              u'h',
              u'j',
              u'k',
              u'l',
              u';',
              u"'",
              u'\\'],
             [u'<',
              u'z',
              u'x',
              u'c',
              u'v',
              u'b',
              u'n',
              u'm',
              u',',
              '.',
              u'/',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'\u0105',
              u'\u0107',
              u'\u0119',
              u'\u0142',
              u'\u0144',
              u'\xf3',
              u'\u015b',
              u'\u017a',
              u'\u017c',
              u'OK']]
            self.shiftkeys_list = [[u'EXIT',
              u'!',
              u'@',
              u'#',
              u'$',
              u'%',
              u'^',
              u'&',
              u'(',
              u')',
              u'=',
              u'BACKSPACE'],
             [u'Q',
              u'W',
              u'E',
              u'R',
              u'T',
              u'Y',
              u'U',
              u'I',
              u'O',
              u'P',
              u'*',
              u']'],
             [u'A',
              u'S',
              u'D',
              u'F',
              u'G',
              u'H',
              u'J',
              u'K',
              u'L',
              u'?',
              u'"',
              u'|'],
             [u'>',
              u'Z',
              u'X',
              u'C',
              u'V',
              u'B',
              u'N',
              u'M',
              u';',
              u':',
              u'_',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'\u0104',
              u'\u0106',
              u'\u0118',
              u'\u0141',
              u'\u0143',
              u'\xd3',
              u'\u015a',
              u'\u0179',
              u'\u017b',
              u'OK']]
            self.nextLang = 'en_EN'
        else:
            self.keys_list = [[u'EXIT',
              u'1',
              u'2',
              u'3',
              u'4',
              u'5',
              u'6',
              u'7',
              u'8',
              u'9',
              u'0',
              u'BACKSPACE'],
             [u'q',
              u'w',
              u'e',
              u'r',
              u't',
              u'y',
              u'u',
              u'i',
              u'o',
              u'p',
              u'-',
              u'['],
             [u'a',
              u's',
              u'd',
              u'f',
              u'g',
              u'h',
              u'j',
              u'k',
              u'l',
              u';',
              u"'",
              u'\\'],
             [u'<',
              u'z',
              u'x',
              u'c',
              u'v',
              u'b',
              u'n',
              u'm',
              u',',
              '.',
              u'/',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'OK',
              u'*']]
            self.shiftkeys_list = [[u'EXIT',
              u'!',
              u'@',
              u'#',
              u'$',
              u'%',
              u'^',
              u'&',
              u'(',
              u')',
              u'=',
              u'BACKSPACE'],
             [u'Q',
              u'W',
              u'E',
              u'R',
              u'T',
              u'Y',
              u'U',
              u'I',
              u'O',
              u'P',
              u'+',
              u']'],
             [u'A',
              u'S',
              u'D',
              u'F',
              u'G',
              u'H',
              u'J',
              u'K',
              u'L',
              u'?',
              u'"',
              u'|'],
             [u'>',
              u'Z',
              u'X',
              u'C',
              u'V',
              u'B',
              u'N',
              u'M',
              u';',
              u':',
              u'_',
              u'CLEAR'],
             [u'SHIFT',
              u'SPACE',
              u'OK',
              u'~']]
            self.lang = 'en_EN'
            self.nextLang = 'de_DE'
        self['country'].setText(self.lang)
        self.max_key = 47 + len(self.keys_list[4])

    def virtualKeyBoardEntryComponent(self, keys):
        w, h = parameters.get('VirtualKeyboard', (45, 45))
        key_bg_width = self.key_bg and self.key_bg.size().width() or w
        key_images = self.shiftMode and self.keyImagesShift or self.keyImages
        res = [keys]
        text = []
        x = 0
        for key in keys:
            png = key_images.get(key, None)
            if png:
                width = png.size().width()
                res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, h), png=png))
            else:
                width = key_bg_width
                res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, h), png=self.key_bg))
                text.append(MultiContentEntryText(pos=(x, 0), size=(width, h), font=0, text=key.encode('utf-8'), flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER))
            x += width

        return res + text

    def buildVirtualKeyBoard(self, selectedkey = None):
        self.previousSelectedKey = None
        self.list = []
        for keys in self.shiftMode and self.shiftkeys_list or self.keys_list:
            self.list.append(self.virtualKeyBoardEntryComponent(keys))

        self.markSelectedKey()
        return

    def markSelectedKey(self):
        w, h = parameters.get('VirtualKeyboard', (45, 45))
        if self.previousSelectedKey is not None:
            self.list[self.previousSelectedKey / 12] = self.list[self.previousSelectedKey / 12][:-1]
        width = self.key_sel.size().width()
        x = self.list[self.selectedKey / 12][self.selectedKey % 12 + 1][1]
        self.list[self.selectedKey / 12].append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, h), png=self.key_sel))
        self.previousSelectedKey = self.selectedKey
        self['list'].setList(self.list)
        return

    def backClicked(self):
        if self.currentlist == 'list':
            self.text = self['text'].getText()[:-1]
            self['text'].setText(self.text)
            self.getsuggestion()

    def insertspace(self):
        print 'self.currentlist', self.currentlist
        if self.currentlist == 'suggestlist':
            return
        elif self.currentlist == 'historylist':
            return
        else:
            if self.shiftMode:
                list = self.shiftkeys_list
            else:
                list = self.keys_list
            selectedKey = self.selectedKey
            text = None
            for x in list:
                if selectedKey < 12:
                    if selectedKey < len(x):
                        text = x[selectedKey]
                    break
                else:
                    selectedKey -= 12

            if text is None:
                return
            text = 'SPACE'
            if text == 'EXIT':
                self.close(None)
            elif text == 'BACKSPACE':
                self.text = self['text'].getText()[:-1]
                self['text'].setText(self.text)
            elif text == 'CLEAR':
                self.text = ''
                self['text'].setText(self.text)
            elif text == 'SHIFT':
                if self.shiftMode:
                    self.shiftMode = False
                else:
                    self.shiftMode = True
                self.buildVirtualKeyBoard(self.selectedKey)
            elif text == 'SPACE':
                self.text += ' '
                self['text'].setText(self.text)
            elif text == 'OK':
                self.close(self['text'].getText())
            else:
                self.text = self['text'].getText()
                self.text += text
                self['text'].setText(self.text)
            self.getsuggestion()
            return
            return

    def okClicked(self):
        print 'self.currentlist', self.currentlist
        if self.currentlist == 'suggestlist':
            txt = str(self['suggestlist'].l.getCurrentSelection())
            print 'txt', txt
            self['text'].setText(txt)
            self.exit()
            self.currentlist == 'list'
            return
        elif self.currentlist == 'historylist':
            txt = str(self['historylist'].l.getCurrentSelection())
            self['text'].setText(txt)
            self.exit()
            self.currentlist == 'list'
            return
        else:
            if self.shiftMode:
                list = self.shiftkeys_list
            else:
                list = self.keys_list
            selectedKey = self.selectedKey
            text = None
            for x in list:
                if selectedKey < 12:
                    if selectedKey < len(x):
                        text = x[selectedKey]
                    break
                else:
                    selectedKey -= 12

            if text is None:
                return
            text = text.encode('UTF-8')
            if text == 'EXIT':
                self.close(None)
            elif text == 'BACKSPACE':
                self.text = self['text'].getText()[:-1]
                self['text'].setText(self.text)
            elif text == 'CLEAR':
                self.text = ''
                self['text'].setText(self.text)
            elif text == 'SHIFT':
                if self.shiftMode:
                    self.shiftMode = False
                else:
                    self.shiftMode = True
                self.buildVirtualKeyBoard(self.selectedKey)
            elif text == 'SPACE':
                self.text += ' '
                self['text'].setText(self.text)
            elif text == 'OK':
                self.close(self['text'].getText())
            else:
                self.text = self['text'].getText()
                self.text += text
                self['text'].setText(self.text)
            self.getsuggestion()
            return
            return

    def ok(self):
        txt = str(self['text'].getText())
        writetohistory(txt)
        self.close(txt)

    def exit(self):
        debug = True
        if self.currentlist == 'suggestlist':
            self['suggestlist'].selectionEnabled(0)
            self['historylist'].selectionEnabled(0)
            self['list'].selectionEnabled(1)
            self.currentlist = 'list'
            return
        elif self.currentlist == 'historylist':
            self['suggestlist'].selectionEnabled(0)
            self['historylist'].selectionEnabled(0)
            self['list'].selectionEnabled(1)
            self.currentlist = 'list'
            return
        else:
            try:
                self.suggestions = None
                self.suggestcallback = None
            except:
                pass

            self.close(None)
            return
            return

    def left(self):
        self.selectedKey -= 1
        if self.selectedKey == -1:
            self.selectedKey = 11
        elif self.selectedKey == 11:
            self.selectedKey = 23
        elif self.selectedKey == 23:
            self.selectedKey = 35
        elif self.selectedKey == 35:
            self.selectedKey = 47
        elif self.selectedKey == 47:
            self.selectedKey = self.max_key
        self.showActiveKey()

    def right(self):
        self.selectedKey += 1
        if self.selectedKey == 12:
            self.selectedKey = 0
        elif self.selectedKey == 24:
            self.selectedKey = 12
        elif self.selectedKey == 36:
            self.selectedKey = 24
        elif self.selectedKey == 48:
            self.selectedKey = 36
        elif self.selectedKey > self.max_key:
            self.selectedKey = 48
        self.showActiveKey()

    def up(self):
        if self.currentlist == 'suggestlist':
            self['suggestlist'].up()
            print 'suggestlist'
            return
        if self.currentlist == 'historylist':
            self['historylist'].up()
            return
        self.selectedKey -= 12
        if self.selectedKey < 0 and self.selectedKey > self.max_key - 60:
            self.selectedKey += 48
        elif self.selectedKey < 0:
            self.selectedKey += 60
        self.showActiveKey()

    def down(self):
        if self.currentlist == 'suggestlist':
            self['suggestlist'].down()
            print 'suggestlist'
            return
        if self.currentlist == 'historylist':
            self['historylist'].down()
            return
        self.selectedKey += 12
        if self.selectedKey > self.max_key and self.selectedKey > 59:
            self.selectedKey -= 60
        elif self.selectedKey > self.max_key:
            self.selectedKey -= 48
        self.showActiveKey()

    def showActiveKey(self):
        self.buildVirtualKeyBoard(self.selectedKey)

    def inShiftKeyList(self, key):
        for KeyList in self.shiftkeys_list:
            for char in KeyList:
                if char == key:
                    return True

        return False

    def keyGotAscii(self):
        char = str(unichr(getPrevAsciiCode()).encode('utf-8'))
        if self.inShiftKeyList(char):
            self.shiftMode = True
            list = self.shiftkeys_list
        else:
            self.shiftMode = False
            list = self.keys_list
        if char == ' ':
            char = 'SPACE'
        selkey = 0
        for keylist in list:
            for key in keylist:
                if key == char:
                    self.selectedKey = selkey
                    self.okClicked()
                    self.showActiveKey()
                    return
                selkey += 1


def writetohistory(txt):
    hfile = '/etc/history'
    if not os.path.exists(hfile):
        afile = open(hfile, 'w')
        afile.write(txt)
        afile.close()
        return
    L = list()
    f = open(hfile, 'r')
    for line in f.readlines():
        if txt==line.strip():
           f.close()
           return
        L.append(line)


    L.insert(0, txt + '\n')
    f.close()
    fi = open(hfile, 'w')
    for line in xrange(len(L)):
        fi.write(L[line])

    fi.close()
