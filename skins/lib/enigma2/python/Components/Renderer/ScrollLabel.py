# uncompyle6 version 3.3.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.16 (default, Apr  6 2019, 01:42:57) 
# [GCC 8.3.0]
# Embedded file name: /usr/lib/enigma2/python/Components/Renderer/ScrollLabel.py
# Compiled at: 2012-08-26 05:13:07
import skin
from Components.VariableText import VariableText
from Renderer import Renderer
from enigma import eLabel, eWidget, ePoint, eSize, gFont, fontRenderClass, eTimer

class ScrollLabel(VariableText, Renderer):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.step = 1
        self.steptime = 100
        self.startdelay = 2000
        self.long_text = None
        self.text_height = 0
        self.page_height = 0
        self.updateTimer = eTimer()
        self.updateTimer.callback.append(self.lineScroll)
        return

    def postWidgetCreate(self, instance):
        self.long_text = eLabel(instance)

    def applySkin(self, desktop, parent):
        attribs = []
        longtext_attribs = []
        for attrib, value in self.skinAttributes:
            if attrib.find('step') != -1:
                self.step = int(value)
            if attrib.find('steptime') != -1:
                self.steptime = int(value)
            if attrib.find('startdelay') != -1:
                self.startdelay = int(value)
            if attrib.find('font') != -1 or attrib.find('size') != -1 or attrib.find('zPosition') != -1 or attrib.find('transparent') != -1 or attrib.find('backgroundColor') != -1 or attrib.find('foregroundColor') != -1 or attrib.find('valign') != -1 or attrib.find('halign') != -1:
                longtext_attribs.append((attrib, value))
            if attrib != 'font' and attrib != 'valign' and attrib != 'halign' and attrib != 'foregroundColor' and attrib != 'step' and attrib != 'steptime' and attrib != 'startdelay' and attrib != 'css':
                attribs.append((attrib, value))
            if attrib.find('css') != -1:
                from skin import cascadingStyleSheets
                styles = value.split(',')
                for style in styles:
                    for _attrib in cascadingStyleSheets[style].keys():
                        _value = cascadingStyleSheets[style][_attrib]
                        if _attrib.find('step') != -1:
                            self.step = int(_value)
                        if _attrib.find('steptime') != -1:
                            self.steptime = int(_value)
                        if _attrib.find('startdelay') != -1:
                            self.startdelay = int(_value)
                        if _attrib.find('font') != -1 or _attrib.find('size') != -1 or _attrib.find('zPosition') != -1 or _attrib.find('transparent') != -1 or _attrib.find('backgroundColor') != -1 or _attrib.find('foregroundColor') != -1 or _attrib.find('valign') != -1 or _attrib.find('halign') != -1:
                            longtext_attribs.append((_attrib, _value))
                        if _attrib != 'font' and _attrib != 'valign' and _attrib != 'halign' and _attrib != 'foregroundColor' and _attrib != 'step' and _attrib != 'steptime' and _attrib != 'startdelay':
                            attribs.append((_attrib, _value))

        skin.applyAllAttributes(self.long_text, desktop, longtext_attribs, parent.scale)
        self.long_text.move(ePoint(0, 0))
        self.skinAttributes = attribs
        ret = Renderer.applySkin(self, desktop, parent)
        self.changed((self.CHANGED_DEFAULT,))
        return ret

    GUI_WIDGET = eWidget

    def connect(self, source):
        Renderer.connect(self, source)
        self.changed((self.CHANGED_DEFAULT,))

    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            if self.long_text is not None:
                self.long_text.move(ePoint(0, 0))
                self.long_text.setText('')
                self.long_text.resize(self.instance.size())
                self.updateTimer.stop()
        else:
            if self.long_text is not None:
                self.long_text.move(ePoint(0, 0))
                if self.source.text is None:
                    self.long_text.setText('')
                else:
                    self.long_text.setText(self.source.text)
                self.page_height = int(self.instance.size().height())
                self.text_height = int(self.long_text.calculateSize().height() + fontRenderClass.getInstance().getLineHeight(self.long_text.getFont()))
                self.long_text.resize(eSize(self.instance.size().width(), self.text_height))
                if self.text_height > self.page_height:
                    self.updateTimer.start(self.startdelay)
                else:
                    self.updateTimer.stop()
        return

    def lineScroll(self):
        if self.long_text is not None:
            if self.text_height > self.page_height:
                curPos = self.long_text.position()
                if self.text_height - self.step >= abs(curPos.y() - self.step):
                    self.long_text.move(ePoint(curPos.x(), curPos.y() - self.step))
                else:
                    self.long_text.move(ePoint(curPos.x(), self.page_height))
                self.updateTimer.start(self.steptime)
            else:
                self.updateTimer.stop()
        return