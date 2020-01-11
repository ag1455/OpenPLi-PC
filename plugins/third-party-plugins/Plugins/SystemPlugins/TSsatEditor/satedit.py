from . import _
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.config import config, ConfigBoolean, ConfigFloat, ConfigInteger, ConfigSelection, ConfigText, ConfigYesNo, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Tools.Directories import fileExists
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.NimManager import nimmanager, getConfigSatlist
from Components.Pixmap import Pixmap
from enigma import eListbox, gFont, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_WRAP, eRect, eTimer, getDesktop
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from time import strftime, time, localtime, mktime
import os
import time
import thread
import urllib2
import xml.etree.cElementTree

currversion = '2.6'

need_update = False

FHD_Res = False
HD_Res = False
sz_y = getDesktop(0).size().height()
if sz_y >= 1080:
    FHD_Res = True
elif sz_y >= 720 and sz_y <= 1079:
    HD_Res = True

class Transponder():
    essential = ['frequency', 'polarization', 'symbol_rate']
    niceToHave = ['system',
     'fec_inner',
     'is_id',
     'pls_code',
     'tsid',
     'onid']
    transSystem = {'0': 'DVB-S',
     '1': 'DVB-S2',
     'dvb-s': 'DVB-S',
     'dvb-s2': 'DVB-S2'}
    reTransSystem = {'DVB-S': '0',
     'DVB-S2': '1'}
    transPolarization = {'0': 'H',
     'h': 'H',
     '1': 'V',
     'v': 'V',
     '2': 'L',
     'cl': 'L',
     'l': 'L',
     '3': 'R',
     'cr': 'R',
     'r': 'R',
     'i': 'i'}
    reTransPolarization = {'H': '0',
     'V': '1',
     'L': '2',
     'R': '3'}
    transModulation = {'0': 'AUTO',
     '1': 'QPSK',
     '2': '8PSK',
     '3': 'QAM16',
     '4': '16APSK',
     '5': '32APSK'}
    reTransModulation = {'AUTO': '0',
     'QPSK': '1',
     '8PSK': '2',
     'QAM16': '3',
     '16APSK': '4',
     '32APSK': '5'}
    transRolloff = {'0': '0_35',
     '1': '0_25',
     '2': '0_20',
     '3': 'Auto'}
    reTransRolloff = {'0_35': '0',
     '0_25': '1',
     '0_20': '2',
     'Auto': '3'}
    transOnOff = {'0': 'OFF',
     '1': 'ON',
     '2': 'AUTO'}
    reTransOnOff = {'OFF': '0',
     'ON': '1',
     'AUTO': '2'}
    transFec = {'0': 'FEC_AUTO',
     '1': 'FEC_1_2',
     '2': 'FEC_2_3',
     '3': 'FEC_3_4',
     '4': 'FEC_5_6',
     '5': 'FEC_7_8',
     '6': 'FEC_8_9',
     '7': 'FEC_3_5',
     '8': 'FEC_4_5',
     '9': 'FEC_9_10',
     '10': 'FEC_6_7',
     '15': 'FEC_NONE',
     'Auto': 'FEC_AUTO',
     '1/2': 'FEC_1_2',
     '2/3': 'FEC_2_3',
     '3/4': 'FEC_3_4',
     '5/6': 'FEC_5_6',
     '6/7': 'FEC_6_7',
     '7/8': 'FEC_7_8',
     '8/9': 'FEC_8_9',
     '3/5': 'FEC_3_5',
     '4/5': 'FEC_4_5',
     '9/10': 'FEC_9_10',
     'none': 'FEC_NONE'}
    reTransFec = {'FEC_AUTO': '0',
     'FEC_1_2': '1',
     'FEC_2_3': '2',
     'FEC_3_4': '3',
     'FEC_5_6': '4',
     'FEC_7_8': '5',
     'FEC_8_9': '6',
     'FEC_3_5': '7',
     'FEC_4_5': '8',
     'FEC_9_10': '9',
     'FEC_6_7': '10',
     'FEC_NONE': '15'}
    onlyDVBS2Fec = ['FEC_8_9',
     'FEC_3_5',
     'FEC_4_5',
     'FEC_9_10']
    transBand = {'KU': ('10700000', '12750000'),
     'C': ('3400000', '4200000')}
    transPlsMode = {'0': 'Root',
     '1': 'Gold',
     '2': 'Combo',
     '3': 'Unknown'}
    reTransPlsMode = {'Root': '0',
     'Gold': '1',
     'Combo': '2',
     'Unknown': '3'}

    def __init__(self, transponder):
        self.rawData = transponder
        self.system = 'DVB-S'
        self.__frequency = '10700000'
        self.__symbolrate = '27500000'
        self.Polarization = 'H'
        self.modulation = 'QPSK'
        self.pilot = 'OFF'
        self.rolloff = '0_35'
        self.fec = 'FEC_AUTO'
        self.inversion = 'AUTO'
        self.__isid = "0"
        self.plsmode = 'Root'
        self.__plscode = '1'
        self.UseMultistream = False
        self.__tsid = '0'
        self.useTsid = False
        self.__onid = '0'
        self.useOnid = False
        self.band = 'KU'
        self.__importColor = None
        self.transponderDoctor(self.rawData)

    def transponderDoctor(self, transponder):
        if not isinstance(transponder, dict):
            print 'transponderDoctor: Transponderdaten muessen vom Type DICT sein'
            print transponder
            return
        param = transponder.keys()
        transParam = {}
        for x in param:
            transParam[x] = x.lower()

        if 'Polarization' in transParam:
            transParam.update({'polarization': transParam.get('Polarization').lower()})
            del transParam['Polarization']
        missing = []
        for x in self.essential:
            if x not in transParam:
                missing.append(x)

        if len(missing):
            print 'transponderDoctor: Folgende Parameter fehlen:', missing
            return
        self.Polarization = self.transPolarization.get(transponder.get(transParam.get('polarization'), 'i').lower())
        if self.Polarization == 'i':
            print 'transponderDoctor: unbekannter Wert fuer Polarization (%s)' % transParam.get('polarization')
            return
        self.__frequency = transponder.get(transParam.get('frequency'), 'i').lower()
        self.__symbolrate = transponder.get(transParam.get('symbol_rate'), 'i').lower()
        dvb_s_cnt = 0
        dvb_s2_cnt = 0
        self.__importColor = transponder.get('import', None)
        if 'system' in transParam:
            self.system = self.transSystem.get(transponder.get(transParam.get('system'), 'i').lower())
            if self.system == 'DVB-S':
                dvb_s_cnt += 1
            if self.system == 'DVB-S2':
                dvb_s2_cnt += 1
        if 'modulation' in transParam:
            self.modulation = self.transModulation.get(transponder.get(transParam.get('modulation'), 'i').lower())
            if self.modulation == '8PSK' or self.modulation == 'QAM16':
                dvb_s2_cnt += 1
        if 'pilot' in transParam:
            self.pilot = self.transOnOff.get(transponder.get(transParam.get('pilot'), 'i').lower())
            if self.pilot == 'ON' or self.pilot == 'AUTO':
                dvb_s2_cnt += 1
        if 'rolloff' in transParam:
            self.rolloff = self.transRolloff.get(transponder.get(transParam.get('rolloff'), 'i').lower())
            if self.rolloff == '0_25':
                dvb_s2_cnt += 1
        if 'fec_inner' in transParam:
            self.fec = self.transFec.get(transponder.get(transParam.get('fec_inner'), 'i').lower())
            if self.fec in self.onlyDVBS2Fec:
                dvb_s2_cnt += 1
        if dvb_s2_cnt:
            self.system = 'DVB-S2'
        else:
            self.system = 'DVB-S'
        if 'inversion' in transParam:
            self.inversion = self.transOnOff.get(transponder.get(transParam.get('inversion'), 'i').lower())
        if 'is_id' in transParam:
            self.__isid = transponder.get(transParam.get('is_id'), 'i').lower()
            self.UseMultistream = True
        if 'pls_mode' in transParam:
            self.plsmode = self.transPlsMode.get(transponder.get(transParam.get('pls_mode'), 'i').lower())
            self.UseMultistream = True
        if 'pls_code' in transParam:
            self.__plscode = transponder.get(transParam.get('pls_code'), 'i').lower()
            self.UseMultistream = True
        if 'tsid' in transParam:
            self.__tsid = transponder.get(transParam.get('tsid'), 'i').lower()
            self.useTsid = True
        if 'onid' in transParam:
            self.__onid = transponder.get(transParam.get('onid'), 'i').lower()
            self.useOnid = True

    def getFrequency(self):
        return self.__frequency

    def setFrequency(self, frequency):
        if isinstance(frequency, list):
            if len(frequency) == 2:
                if isinstance(frequency[0], int) and isinstance(frequency[1], int):
                    self.__frequency = str(frequency[0] * 1000 + frequency[1])
                    return
        else:
            self.__frequency = str(frequency)

    frequency = property(getFrequency, setFrequency)
    importColor = property(lambda self: self.__importColor)

    def getSymbolrate(self):
        return self.__symbolrate

    def setSymbolrate(self, symbolrate):
        self.__symbolrate = str(symbolrate)

    symbolrate = property(getSymbolrate, setSymbolrate)

    def setPlsCode(self, newPlsCode):
        self.__plscode = str(newPlsCode)

    plscode = property(lambda self: self.__plscode, setPlsCode)

    def setIsId(self, newIsId):
        self.__isid = str(newIsId)

    isid = property(lambda self: self.__isid, setIsId)

    def setTsid(self, newTsid):
        self.__tsid = str(newTsid)

    tsid = property(lambda self: self.__tsid, setTsid)

    def getOnid(self):
        return self.__onid

    def setOnid(self, newOnid):
        self.__onid = str(newOnid)

    onid = property(lambda self: self.__onid, setOnid)

    def exportImportColor(self):
        return {'import': self.__importColor}

    def exportSystem(self):
        return {'system': self.reTransSystem.get(self.system)}

    def exportFec(self):
        return {'fec_inner': self.reTransFec.get(self.fec)}

    def exportFrequency(self):
        return {'frequency': self.__frequency}

    def exportPolarization(self):
        return {'polarization': self.reTransPolarization.get(self.Polarization)}

    def exportSymbolrate(self):
        return {'symbol_rate': self.__symbolrate}

    def exportModulation(self):
        return {'modulation': self.reTransModulation.get(self.modulation)}

    def exportPlsMode(self):
        return {'pls_mode': self.reTransPlsMode.get(self.plsmode)}

    def exportPlsCode(self):
        return {'pls_code': self.__plscode}

    def exportIsId(self):
        return {'is_id': self.__isid}

    def exportOnid(self):
        return {'onid': self.__onid}

    def exportTsid(self):
        return {'tsid': self.__tsid}

    def exportInversion(self):
        return {'inversion': self.reTransOnOff.get(self.inversion)}

    def exportPilot(self):
        return {'pilot': self.reTransOnOff.get(self.pilot)}

    def exportRolloff(self):
        return {'rolloff': self.reTransRolloff.get(self.rolloff)}

    def exportClean(self):
        res = {}
        res.update(self.exportSystem())
        res.update(self.exportFec())
        res.update(self.exportFrequency())
        res.update(self.exportPolarization())
        res.update(self.exportSymbolrate())
        res.update(self.exportModulation())
        if self.UseMultistream:
           res.update(self.exportIsId())
           res.update(self.exportPlsMode())
           res.update(self.exportPlsCode())
        if self.useOnid:
            res.update(self.exportOnid())
        if self.useTsid:
            res.update(self.exportTsid())
        if self.inversion != 'AUTO':
            res.update(self.exportInversion())
        if self.system == 'DVB-S2':
            if self.pilot != 'OFF':
                res.update(self.exportPilot())
        if self.rolloff != '0_35':
            res.update(self.exportRolloff())
        return res

    def exportAll(self):
        res = self.exportClean()
        res.update(self.exportImportColor())
        return res

class TransponderList(MenuList):

    def __init__(self):
        MenuList.__init__(self, list=[], enableWrapAround=True, content=eListboxPythonMultiContent)
        if FHD_Res:
            self.rowHight = 40
            self.l.setItemHeight(40)
            self.l.setFont(0, gFont('Regular', 27))
            self.l.setFont(1, gFont('Regular', 23))
        else:
            self.rowHight = 20
            self.l.setItemHeight(24)
            self.l.setFont(0, gFont('Regular', 20))
            self.l.setFont(1, gFont('Regular', 15))
    def setEntries(self, transponderlist):
        transRolloff = {'0_35': '0.35',
         '0_25': '0.25',
         '0_20': '0.20',
         'Auto': 'Auto'}
        transFec = {'FEC_AUTO': 'Auto',
         'FEC_1_2': '1/2',
         'FEC_2_3': '2/3',
         'FEC_3_4': '3/4',
         'FEC_5_6': '5/6',
         'FEC_6_7': '6/7',
         'FEC_7_8': '7/8',
         'FEC_8_9': '8/9',
         'FEC_3_5': '3/5',
         'FEC_4_5': '4/5',
         'FEC_9_10': '9/10',
         'FEC_NONE': 'none'}
        res = []
        z = 0
        for x in transponderlist:
            transponder = Transponder(x)
            tp = []
            tp.append(z)
            z += 1
            calc_xpos = lambda a: a[len(a) - 1][1] + a[len(a) - 1][3]
            color = transponder.importColor
            if FHD_Res:
                tp.append(MultiContentEntryText(pos=(0, 0), size=(105, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.system, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(95, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=str(int(transponder.frequency) / 1000), color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(70, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.Polarization, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(85, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=str(int(transponder.symbolrate) / 1000), color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(80, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transFec.get(transponder.fec), color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(105, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.modulation, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(85, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transRolloff.get(transponder.rolloff), color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(85, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.inversion, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(80, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.pilot, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(75, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.isid, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(110, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.plsmode, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(110, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.plscode, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(80, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.tsid, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(80, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.onid, color=color, border_width=1, border_color=12092939))
            elif HD_Res:
                tp.append(MultiContentEntryText(pos=(0, 0), size=(75, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.system, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(65, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=str(int(transponder.frequency) / 1000), color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(45, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.Polarization, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(60, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=str(int(transponder.symbolrate) / 1000), color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(65, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transFec.get(transponder.fec), color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(85, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.modulation, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(60, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transRolloff.get(transponder.rolloff), color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(60, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.inversion, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(60, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.pilot, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(45, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.isid, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(70, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.plsmode, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(70, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.plscode, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(65, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.tsid, color=color, border_width=1, border_color=12092939))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(65, self.rowHight), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.onid, color=color, border_width=1, border_color=12092939))
            else:
                tp.append(MultiContentEntryText(pos=(0, 0), size=(55, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.system, color=color, border_width=1, border_color=806544))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(45, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=str(int(transponder.frequency) / 1000), color=color, border_width=1, border_color=806544))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(23, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.Polarization, color=color, border_width=1, border_color=806544))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(48, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=str(int(transponder.symbolrate) / 1000), color=color, border_width=1, border_color=806544))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(38, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transFec.get(transponder.fec), color=color, border_width=1, border_color=806544))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(48, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.modulation, color=color, border_width=1, border_color=806544))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(38, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transRolloff.get(transponder.rolloff), color=color, border_width=1, border_color=806544))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(38, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.inversion, color=color, border_width=1, border_color=806544))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(38, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.pilot, color=color, border_width=1, border_color=806544))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(33, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.isid, color=color, border_width=1, border_color=806544))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(46, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.plsmode, color=color, border_width=1, border_color=806544))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(38, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.plscode, color=color, border_width=1, border_color=806544))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(38, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.tsid, color=color, border_width=1, border_color=806544))
                tp.append(MultiContentEntryText(pos=(calc_xpos(tp), 0), size=(38, self.rowHight), font=1, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=transponder.onid, color=color, border_width=1, border_color=806544))
            res.append(tp)

        self.l.setList(res)

class TransponderEditor(Screen, ConfigListScreen, Transponder):

    if FHD_Res:
        skin = '\n\t\t<screen position="center,center" size="900,600" title="Edit" >\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/red.png" position="40,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/green.png" position="250,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/yellow.png" position="470,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/blue.png" position="690,0" size="140,40" alphatest="on" />\n\t\t<widget name="key_red" position="10,0" zPosition="1" size="200,40" font="Regular;25" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="220,0" zPosition="1" size="200,40" font="Regular;25" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="440,0" zPosition="1" size="200,40" font="Regular;25" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="660,0" zPosition="1" size="200,40" font="Regular;25" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="config" position="10,50" size="880,520" font="Regular;26" itemHeight="40" scrollbarMode="showOnDemand" />\n\t\t</screen>'
    else:
        skin = '\n\t\t<screen position="center,center" size="560,400" title="Edit" >\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/red.png" position="0,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/green.png" position="140,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/yellow.png" position="280,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/blue.png" position="420,0" size="140,40" alphatest="on" />\n\t\t<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="config" position="10,50" size="540,325" scrollbarMode="showOnDemand" />\n\t\t</screen>'

    def __init__(self, session, transponderData = None):
        self.skin = TransponderEditor.skin
        Screen.__init__(self, session)
        Transponder.__init__(self, transponderData)
        self.createConfig()
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'cancel': self.cancel,
         'ok': self.okExit,
         'red': self.cancel,
         'green': self.okExit}, -1)
        self['key_red'] = Button(_('Close'))
        self['key_green'] = Button(_('OK'))
        self['key_yellow'] = Button('')
        self['key_blue'] = Button('')
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self.transponderData = transponderData
        self.onLayoutFinish.append(self.layoutFinished)
        self.createSetup()

    def layoutFinished(self):
		if self.transponderData:
			self.setTitle(_('Edit transponder'))
		else:
			self.setTitle(_('Add transponder'))

    def createConfig(self):
        self.configTransponderSystem = ConfigSelection([('DVB-S', _('DVB-S')), ('DVB-S2', _('DVB-S2'))], self.system)
        self.configTransponderFrequency = ConfigFloat(default=[int(self.frequency) / 1000, int(self.frequency) % 1000], limits=[(0, 99999), (0, 999)])
        self.configTransponderPolarization = ConfigSelection([('H', _('horizontal')),
         ('V', _('vertical')),
         ('L', _('circular left')),
         ('R', _('circular right'))], self.Polarization)
        self.configTransponderSymbolrate = ConfigInteger(default=int(self.symbolrate) / 1000, limits=(0, 99999))
        self.configTransponderFec = ConfigSelection([('FEC_AUTO', 'Auto'),
         ('FEC_1_2', '1/2'),
         ('FEC_2_3', '2/3'),
         ('FEC_3_4', '3/4'),
         ('FEC_5_6', '5/6'),
         ('FEC_6_7', '6/7'),
         ('FEC_7_8', '7/8')], self.fec)
        self.configTransponderFec2 = ConfigSelection([('FEC_AUTO', 'Auto'),
         ('FEC_1_2', '1/2'),
         ('FEC_2_3', '2/3'),
         ('FEC_3_4', '3/4'),
         ('FEC_5_6', '5/6'),
         ('FEC_6_7', '6/7'),
         ('FEC_7_8', '7/8'),
         ('FEC_8_9', '8/9'),
         ('FEC_3_5', '3/5'),
         ('FEC_4_5', '4/5'),
         ('FEC_9_10', '9/10')], self.fec)
        self.configTransponderInversion = ConfigSelection([('OFF', 'off'), ('ON', 'on'), ('AUTO', 'auto')], self.inversion)
        self.configTransponderModulation = ConfigSelection([('AUTO', 'auto'),
         ('QPSK', 'QPSK'),
         ('8PSK', '8PSK'),
         ('QAM16', 'QAM16'),
         ('16APSK', '16APSK'),
         ('32APSK', '32APSK')], self.modulation)
        self.configTransponderRollOff = ConfigSelection([('0_35', '0.35'), ('0_25', '0.25'), ('0_20', '0.20'), ('Auto', 'Auto')], self.rolloff)
        self.configTransponderPilot = ConfigSelection([('OFF', 'off'), ('ON', 'on'), ('AUTO', 'auto')], self.pilot)
        self.configTransponderUseMultistream = ConfigYesNo(default=self.UseMultistream)
        self.configTransponderIsId = ConfigInteger(default=int(self.isid), limits=(0, 255))
        self.configTransponderPlsMode = ConfigSelection([('Root', 'Root'), ('Gold', 'Gold'), ('Combo', 'Combo')], self.plsmode)
        self.configTransponderPlsCode = ConfigInteger(default=int(self.plscode), limits=(0, 262142))
        self.configTransponderUseTsid = ConfigYesNo(default=self.useTsid)
        self.configTransponderUseOnid = ConfigYesNo(default=self.useOnid)
        self.configTransponderTsid = ConfigInteger(default=int(self.tsid), limits=(0, 65535))
        self.configTransponderOnid = ConfigInteger(default=int(self.onid), limits=(0, 65535))

    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_('System'), self.configTransponderSystem))
        if self.system == 'DVB-S' or self.system == 'DVB-S2':
            self.list.append(getConfigListEntry(_('Frequency'), self.configTransponderFrequency))
            self.list.append(getConfigListEntry(_('Polarization'), self.configTransponderPolarization))
            self.list.append(getConfigListEntry(_('Symbolrate'), self.configTransponderSymbolrate))
        if self.system == 'DVB-S':
            self.list.append(getConfigListEntry(_('FEC'), self.configTransponderFec))
        elif self.system == 'DVB-S2':
            self.list.append(getConfigListEntry(_('FEC'), self.configTransponderFec2))
        if self.system == 'DVB-S' or self.system == 'DVB-S2':
            self.list.append(getConfigListEntry(_('Inversion'), self.configTransponderInversion))
        if self.system == 'DVB-S2':
            self.list.append(getConfigListEntry(_('Modulation'), self.configTransponderModulation))
            self.list.append(getConfigListEntry(_('RollOff'), self.configTransponderRollOff))
            self.list.append(getConfigListEntry(_('Pilot'), self.configTransponderPilot))
        if self.system == 'DVB-S' or self.system == 'DVB-S2':
            if self.system == 'DVB-S2':
                self.list.append(getConfigListEntry(_('Use multistream'), self.configTransponderUseMultistream))
                if self.UseMultistream:
                    self.list.append(getConfigListEntry(_('Input Stream ID'), self.configTransponderIsId))
                    self.list.append(getConfigListEntry(_('PLS Mode'), self.configTransponderPlsMode))
                    self.list.append(getConfigListEntry(_('PLS Code'), self.configTransponderPlsCode))
            self.list.append(getConfigListEntry(_('Use tsid'), self.configTransponderUseTsid))
            if self.useTsid:
                self.list.append(getConfigListEntry(_('TSID'), self.configTransponderTsid))
            self.list.append(getConfigListEntry(_('Use onid'), self.configTransponderUseOnid))
            if self.useOnid:
                self.list.append(getConfigListEntry(_('ONID'), self.configTransponderOnid))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def cancel(self):
        self.close(None)

    def okExit(self):
        global need_update
        need_update = True
        self.system = self.configTransponderSystem.value
        self.frequency = self.configTransponderFrequency.value
        self.Polarization = self.configTransponderPolarization.value
        self.symbolrate = self.configTransponderSymbolrate.value * 1000
        if self.system == 'DVB-S':
            self.fec = self.configTransponderFec.value
        else:
            self.fec = self.configTransponderFec2.value
        self.inversion = self.configTransponderInversion.value
        self.modulation = self.configTransponderModulation.value
        self.rolloff = self.configTransponderRollOff.value
        self.pilot = self.configTransponderPilot.value
        self.isid = self.configTransponderIsId.value
        self.plsmode = self.configTransponderPlsMode.value
        self.plscode = self.configTransponderPlsCode.value
        self.tsid = self.configTransponderTsid.value
        self.onid = self.configTransponderOnid.value
        self.close(self.exportAll())

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.newConfig()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.newConfig()

    def newConfig(self):
        checkList = (self.configTransponderSystem, self.configTransponderUseTsid, self.configTransponderUseOnid, self.configTransponderUseMultistream)
        for x in checkList:
            if self['config'].getCurrent()[1] == x:
                if x == self.configTransponderSystem:
                    self.system = self.configTransponderSystem.value
                elif x == self.configTransponderUseMultistream:
                    self.UseMultistream = self.configTransponderUseMultistream.value
                elif x == self.configTransponderUseTsid:
                    self.useTsid = self.configTransponderUseTsid.value
                elif x == self.configTransponderUseOnid:
                    self.useOnid = self.configTransponderUseOnid.value
            self.createSetup()

class TranspondersEditor(Screen):
    if FHD_Res:
        skin = '\n\t\t<screen position="center,center" size="1320,800" title="Transponders Editor" >\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/red.png" position="40,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/green.png" position="250,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/yellow.png" position="470,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/blue.png" position="690,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/ok.png" position="1280,0" size="35,35" alphatest="on" />\n\t\t<widget name="key_red" position="10,0" zPosition="1" size="200,40" font="Regular;23" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="220,0" zPosition="1" size="200,40" font="Regular;23" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="440,0" zPosition="1" size="200,40" font="Regular;23" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="660,0" zPosition="1" size="200,40" font="Regular;23" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="list" position="10,100" size="1300,680" scrollbarMode="showOnDemand" />\n\t\t<widget name="head" position="10,45" size="1300,45" scrollbarMode="showNever" />\n\t\t</screen>'
    elif HD_Res:
        skin = '\n\t\t<screen position="center,center" size="920,460" title="Transponders Editor" >\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/red.png" position="0,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/green.png" position="140,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/yellow.png" position="280,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/blue.png" position="420,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/ok.png" position="880,0" size="35,35" alphatest="on" />\n\t\t<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="list" position="0,64" size="920,384" scrollbarMode="showOnDemand" />\n\t\t<widget name="head" position="0,30" size="920,34" scrollbarMode="showNever" />\n\t\t</screen>'
    else:
        skin = '\n\t\t<screen position="center,center" size="585,430" title="Transponders Editor" >\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/red.png" position="0,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/green.png" position="140,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/yellow.png" position="280,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/blue.png" position="420,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/ok.png" position="540,5" size="35,35" alphatest="on"  zPosition="2" />\n\t\t<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="list" position="0,64" size="585,335" scrollbarMode="showOnDemand" />\n\t\t<widget name="head" position="0,30" size="585,34" scrollbarMode="showNever" />\n\t\t</screen>'

    def __init__(self, session, satellite = None):
        self.skin = TranspondersEditor.skin
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['SatellitesEditorActions'], {'nextPage': self.nextPage,
         'prevPage': self.prevPage,
         'select': self.editTransponder,
         'exit': self.cancel,
         'left': self.left,
         'leftUp': self.doNothing,
         'leftRepeated': self.doNothing,
         'right': self.right,
         'rightUp': self.doNothing,
         'rightRepeated': self.doNothing,
         'up': self.up,
         'upUp': self.upUp,
         'upRepeated': self.upRepeated,
         'down': self.down,
         'downUp': self.downUp,
         'downRepeated': self.downRepeated,
         'red': self.removeTransponder,
         'green': self.editTransponder,
         'yellow': self.addTransponder,
         'blue': self.sortColumn}, -1)
        self.transponderslist = satellite[1]
        self.satelliteName = satellite[0].get('name')
        self['key_red'] = Button(_('Remove'))
        self['key_green'] = Button(_('Edit'))
        self['key_yellow'] = Button(_('Add'))
        self['key_blue'] = Button(_('Sort'))
        self['head'] = Head()
        self.currentSelectedColumn = 0
        self['list'] = TransponderList()
        self['list'].setEntries(self.transponderslist)
        self.onLayoutFinish.append(self.layoutFinished)

        self.row = [['System', '1', False],
         ['Freq.', '2', False],
         ['Pol.', '3', False],
         ['SR', '4', False],
         ['FEC', '5', False],
         ['Modul.', '6', False],
         ['Rolloff', '7', False],
         ['Invers.', '8', False],
         ['Pilot', '9', False],
         ['IS ID', '10', False],
         ['PLS Mode', '11', False],
         ['PLS Code', '12', False],
         ['TSID', '13', False],
         ['ONID', '14', False]]

    def layoutFinished(self):
        try:
            self.setTitle(_('Transponders Editor (%s)') % self.satelliteName)
            row = self['list'].getCurrent()
            if row is None:
                return
            head = []
            for x in range(1, len(row)):
                head.append((row[x][1], row[x][3], self.row[x - 1][0]))

            self['head'].setEntries(head)
            data = self['head'].l.getCurrentSelection()
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)
            self.updateSelection()
        except:
            self.close(None)

    def updateSelection(self):
        row = self['list'].l.getCurrentSelection()
        if row is None:
            return
        firstColumn = row[1]
        lastColumn = row[len(row) - 1]
        self['list'].l.setSelectionClip(eRect(firstColumn[1], firstColumn[0], lastColumn[1] + lastColumn[3], lastColumn[4]), True)

    def doNothing(self):
        pass

    def left(self):
        if self.currentSelectedColumn:
            self.currentSelectedColumn -= 1
            data = self['head'].l.getCurrentSelection()
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)

    def right(self):
        if self.currentSelectedColumn < len(self.row) - 1:
            self.currentSelectedColumn += 1
            data = self['head'].l.getCurrentSelection()
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)

    def upRepeated(self):
        self['list'].up()
        self.updateSelection()

    def downRepeated(self):
        self['list'].down()
        self.updateSelection()

    def nextPage(self):
        self['list'].pageUp()
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is not None:
            self.lastSelectedIndex = cur_idx
            self.updateSelection()

    def prevPage(self):
        self['list'].pageDown()
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is not None:
            self.lastSelectedIndex = cur_idx
            self.updateSelection()

    def up(self):
        self['list'].up()
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is not None:
            self.lastSelectedIndex = cur_idx
            self.updateSelection()

    def down(self):
        self['list'].down()
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is not None:
            self.lastSelectedIndex = cur_idx
            self.updateSelection()

    def upUp(self):
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is not None and self.lastSelectedIndex != cur_idx:
            self.lastSelectedIndex = cur_idx

    def downUp(self):
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is not None and self.lastSelectedIndex != cur_idx:
            self.lastSelectedIndex = cur_idx

    def addTransponder(self):
        self.session.openWithCallback(self.finishedTransponderAdd, TransponderEditor)

    def editTransponder(self):
        if not len(self.transponderslist):
            return
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is not None:
            self.session.openWithCallback(self.finishedTransponderEdit, TransponderEditor, self.transponderslist[cur_idx])

    def finishedTransponderEdit(self, result):
        if result is None:
            return
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is None: return
        global need_update
        need_update = True
        self.transponderslist[cur_idx] = result
        self['list'].setEntries(self.transponderslist)

    def finishedTransponderAdd(self, result):
        if result is None:
            return
        try:
            self.transponderslist.append(result)
        except:
            return
        global need_update
        need_update = True
        self['list'].setEntries(self.transponderslist)

    def removeTransponder(self):
        if len(self.transponderslist):
            cb_func = lambda ret: not ret or self.deleteTransponder()
            self.session.openWithCallback(cb_func, MessageBox, _('Remove transponder?'), MessageBox.TYPE_YESNO)

    def deleteTransponder(self):
        if len(self.transponderslist):
            cur_idx = self['list'].getSelectedIndex()
            if cur_idx is None: return
            global need_update
            need_update = True
            self.transponderslist.pop(cur_idx)
            self['list'].setEntries(self.transponderslist)

    def cancel(self):
        self.close(None)

    def compareColumn(self, a):
        map = {'System':'system', 'Freq.':'frequency', 'Pol.':'polarization', 'SR':'symbol_rate', 'FEC':'fec_inner', 'Modul.':'modulation', 'Rolloff':'rolloff', 'Invers.':'inversion', 'Pilot':'pilot', 'IS ID':'is_id', 'PLS Mode':'pls_mode', 'PLS Code':'pls_code', 'TSID':'tsid', 'ONID': 'onid'}
        cur = map[self.row[self.currentSelectedColumn][0]]
        return int(a.get(cur, '-1'))

    def sortColumn(self):
        rev = self.row[self.currentSelectedColumn][2]
        self.transponderslist.sort(key=self.compareColumn, reverse=rev)
        if rev:
            self.row[self.currentSelectedColumn][2] = False
        else:
            self.row[self.currentSelectedColumn][2] = True
        self['list'].setEntries(self.transponderslist)
        global need_update
        need_update = True

class SatelliteList(MenuList):

    def __init__(self):
        MenuList.__init__(self, list=[], enableWrapAround=True, content=eListboxPythonMultiContent)
        if FHD_Res:
            self.l.setItemHeight(40)
            self.l.setFont(0, gFont('Regular', 27))
        else:
            self.l.setItemHeight(24)
            self.l.setFont(0, gFont('Regular', 20))

    def setEntries(self, satelliteslist):
        res = []
        for x in satelliteslist:
            satparameter = x[0]
            satentry = []
            pos = int(satparameter.get('position'))
            if pos < 0:
                pos += 3600
            satentry.append(pos)
            color = None
            color_sel = None
            if satparameter.get('selected', False):
                color = 0
                color_sel = 65344
            backcolor = None
            backcolor_sel = None
            a = FHD_Res and 1050 or HD_Res and 700 or 430
            b = FHD_Res and 255 or HD_Res and 170 or 103
            if len(x) == 1:
                backcolor = 1644912
                backcolor_sel = 9466996
            if FHD_Res:
                satentry.append(MultiContentEntryText(pos=(0, 0), size=(a, 40), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_TOP, text=satparameter.get('name'), color=color, color_sel=color_sel, backcolor=backcolor, backcolor_sel=backcolor_sel, border_width=1, border_color=15792383))
            else:
                satentry.append(MultiContentEntryText(pos=(0, 0), size=(a, 24), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_TOP, text=satparameter.get('name'), color=color, color_sel=color_sel, backcolor=backcolor, backcolor_sel=backcolor_sel, border_width=1, border_color=15792383))
            pos = int(satparameter.get('position'))
            posStr = str(abs(pos) / 10) + '.' + str(abs(pos) % 10)
            if pos < 0:
                posStr = posStr + ' ' + 'West'
            if pos > 0:
                posStr = posStr + ' ' + 'East'
            if pos == 0:
                posStr = posStr + ' ' + 'Greenwich'
            if FHD_Res:
                satentry.append(MultiContentEntryText(pos=(a, 0), size=(b, 40), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=posStr, color=color, color_sel=color_sel, backcolor=backcolor, backcolor_sel=backcolor_sel, border_width=1, border_color=15792383))
            else:
                satentry.append(MultiContentEntryText(pos=(a, 0), size=(b, 24), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=posStr, color=color, color_sel=color_sel, backcolor=backcolor, backcolor_sel=backcolor_sel, border_width=1, border_color=15792383))
            res.append(satentry)

        self.l.setList(res)

class SatEditor(Screen, ConfigListScreen):
    flagNetworkScan = 1
    flagUseBAT = 2
    flagUseONIT = 4

    if FHD_Res:
        skin = '\n\t\t<screen position="center,center" size="900,540" title="Edit" >\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/red.png" position="40,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/green.png" position="250,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/yellow.png" position="470,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/blue.png" position="690,0" size="140,40" alphatest="on" />\n\t\t<widget name="key_red" position="10,0" zPosition="1" size="200,40" font="Regular;25" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="220,0" zPosition="1" size="200,40" font="Regular;25" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="440,0" zPosition="1" size="200,40" font="Regular;25" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="660,0" zPosition="1" size="200,40" font="Regular;25" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="config" position="10,50" size="880,480" font="Regular;26" itemHeight="40" scrollbarMode="showOnDemand" />\n\t\t</screen>'
    else:
        skin = '\n\t\t<screen position="center,center" size="560,330" title="Edit" >\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/red.png" position="0,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/green.png" position="140,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/yellow.png" position="280,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/blue.png" position="420,0" size="140,40" alphatest="on" />\n\t\t<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="config" position="10,50" size="540,200" scrollbarMode="showOnDemand" />\n\t\t</screen>'

    def __init__(self, session, satelliteslist=None, satelliteData=None, clone=False):
        self.skin = SatEditor.skin
        Screen.__init__(self, session)
        self.satelliteData = satelliteData
        self.satelliteslist = satelliteslist
        self.firstSatellitePosition = 0
        self.clone = clone
        self.satelliteOrientation = 'east'
        if self.satelliteData is not None:
            self.satelliteName = self.satelliteData.get('name', 'unknown satellite name')
            if self.clone:
                self.satelliteName += ' (copy)'
            satellitePosition = int(self.satelliteData.get('position', '0'))
            self.firstSatellitePosition = satellitePosition
            if satellitePosition < 0:
                self.satelliteOrientation = 'west'
            satellitePosition = abs(satellitePosition)
            self.satellitePosition = [satellitePosition / 10, satellitePosition % 10]
            self.satelliteFlags = int(self.satelliteData.get('flags', '1'))
        else:
            self.satelliteName = 'new satellite'
            self.satellitePosition = [0, 0]
            self.satelliteFlags = 1
        self.createConfig()
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'cancel': self.cancel,
         'ok': self.okExit,
         'red': self.cancel,
         'green': self.okExit}, -1)
        self['key_red'] = Button(_("Close"))
        self['key_green'] = Button(_('OK'))
        self['key_yellow'] = Button('')
        self['key_blue'] = Button('')
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self.onLayoutFinish.append(self.layoutFinished)
        self.createSetup()

    def layoutFinished(self):
        text = _('Edit ')
        if self.clone: text = _('Clone current ')
        if self.satelliteData is None: text = _('Add ')
        self.setTitle(text + self.satelliteName)

    def createConfig(self):
        self.configSatelliteName = ConfigText(default=self.satelliteName, visible_width=50, fixed_size=False)
        self.configSatelliteName.setUseableChars(u"0,?!&@=*'+\()$~% 1.:;/-_#abc2ABCdef3DEFghi4GHIjkl5JKLmno6MNOpqrs7PQRStuv8TUVwxyz9WXYZ")
        self.configSatellitePosition = ConfigFloat(default=self.satellitePosition, limits=[(0, 180), (0, 9)])
        self.configSatelliteOrientation = ConfigSelection([('east', 'East'), ('west', 'West')], self.satelliteOrientation)
        options = self.satelliteFlags in (1, 3, 5, 7) and True or False
        self.configSatelliteFlagNetworkScan = ConfigYesNo(default=options)
        options = self.satelliteFlags in (2, 3, 6, 7) and True or False
        self.configSatelliteFlagUseBAT = ConfigYesNo(default=options)
        options = self.satelliteFlags in (4, 5, 6, 7) and True or False
        self.configSatelliteFlagUseONIT = ConfigYesNo(default=options)

    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_('Name'), self.configSatelliteName))
        self.list.append(getConfigListEntry(_('Position'), self.configSatellitePosition))
        self.list.append(getConfigListEntry(_('Orientation'), self.configSatelliteOrientation))
        self.list.append(getConfigListEntry(_('Network scan'), self.configSatelliteFlagNetworkScan))
        self.list.append(getConfigListEntry(_('BAT'), self.configSatelliteFlagUseBAT))
        self.list.append(getConfigListEntry(_('ONIT'), self.configSatelliteFlagUseONIT))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def cancel(self):
        self.close(None)
 
    def okExit(self):
		satelliteFlags = 0
		if self.configSatelliteFlagNetworkScan.value:
			satelliteFlags += self.flagNetworkScan
		if self.configSatelliteFlagUseBAT.value:
			satelliteFlags += self.flagUseBAT
		if self.configSatelliteFlagUseONIT.value:
			satelliteFlags += self.flagUseONIT
		satellitePosition = self.configSatellitePosition.value[0] * 10 + self.configSatellitePosition.value[1]
		if self.configSatelliteOrientation.value == 'west':
			satellitePosition = -satellitePosition
		if satellitePosition == 0:
			self.session.open(MessageBox, _('Sorry, you can not use prime meridian.'), MessageBox.TYPE_ERROR)
			return
		if self.satelliteslist:
			exception = not self.clone and self.satelliteData
			for sat in self.satelliteslist:
				pos = int(sat[0].get('position', '0'))
				if satellitePosition == pos:
					if exception:
						if self.firstSatellitePosition != 0 and pos == self.firstSatellitePosition:
							continue
					self.session.open(MessageBox, _('This position number is busy.\nSelect another position.'), MessageBox.TYPE_ERROR)
					return
		satelliteData = {'name': self.configSatelliteName.value, 'flags': str(satelliteFlags), 'position': str(satellitePosition)}
		global need_update 
		need_update = True
		self.close(satelliteData)

class Head(HTMLComponent, GUIComponent):
    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setSelectionClip(eRect(0, 0, 0, 0))
        if FHD_Res:
            self.l.setItemHeight(40)
            self.l.setFont(0, gFont('Regular', 25))
        else:
            self.l.setItemHeight(34)
            self.l.setFont(0, gFont('Regular', 17))

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)

    def setEntries(self, data = None):
        res = [None]
        if data is not None:
            for x in data:
                if FHD_Res:
                    res.append(MultiContentEntryText(pos=(x[0], 0), size=(x[1], 40), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=x[2], color=12632256, backcolor=625428280, color_sel=16777215, backcolor_sel=627073024, border_width=1, border_color=15792383))
                else:
                    res.append(MultiContentEntryText(pos=(x[0], 0), size=(x[1], 20), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=x[2], color=12632256, backcolor=625428280, color_sel=16777215, backcolor_sel=627073024, border_width=1, border_color=15792383))

        self.l.setList([res])

class SatellitesEditor(Screen):
    if FHD_Res:
        skin = '\n\t\t<screen position="center,center" size="1320,800" title="TS-Satellites Editor" >\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/red.png" position="40,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/green.png" position="250,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/yellow.png" position="470,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/blue.png" position="690,0" size="140,40" alphatest="on" />\n\t\t<ePixmap  pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/yellow.png" position="470,0" size="140,40" alphatest="on" />\n\t\t<ePixmap  pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/ok.png" position="1280,0" size="35,35" alphatest="on" />\n\t\t<widget name="key_menu" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/key_menu.png" position="1000,0" size="35,25" alphatest="on" />\n\t\t<widget name="key_red" position="10,0" zPosition="1" size="200,40" font="Regular;25" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="220,0" zPosition="1" size="200,40" font="Regular;25" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="440,0" zPosition="1" size="200,40" font="Regular;25" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="660,0" zPosition="1" size="200,40" font="Regular;25" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="list" position="10,100" size="1300,520" scrollbarMode="showOnDemand" />\n\t\t<widget name="head" position="10,50" size="1300,40" scrollbarMode="showNever" />\n\t\t<widget name="polhead" position="100,630" size="1220,40" />\n\t\t<widget name="bandlist" position="10,670" size="90,120" />\n\t\t<widget name="infolist" position="100,670" zPosition="2" size="1220,120" />\n\t\t</screen>'
    elif HD_Res:
        skin = '\n\t\t<screen position="center,center" size="920,460" title="TS-Satellites Editor" >\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/red.png" position="0,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/green.png" position="140,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/yellow.png" position="280,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/blue.png" position="420,0" size="140,40" alphatest="on" />\n\t\t<ePixmap  pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/yellow.png" position="280,0" size="140,40" alphatest="on" />\n\t\t<ePixmap  pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/ok.png" position="880,0" size="35,35" alphatest="on" />\n\t\t<widget name="key_menu" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/key_menu.png" position="880,20" size="35,25" alphatest="on" />\n\t\t<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="list" position="0,64" size="920,240" scrollbarMode="showOnDemand" />\n\t\t<widget name="head" position="0,40" size="900,24" scrollbarMode="showNever" />\n\t\t<widget name="polhead" position="80,310" size="840,24" />\n\t\t<widget name="bandlist" position="0,334" size="80,72" />\n\t\t<widget name="infolist" position="80,334" zPosition="2" size="840,72" />\n\t\t</screen>'
    else:
        skin = '\n\t\t<screen position="center,center" size="560,430" title="TS-Satellites Editor" >\n\t\t<ePixmap  pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/red.png" position="0,0" size="140,40" alphatest="on" />\n\t\t<ePixmap  pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/green.png" position="140,0" size="140,40" alphatest="on" />\n\t\t<ePixmap  pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/yellow.png" position="280,0" size="140,40" alphatest="on" />\n\t\t<ePixmap  pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/blue.png" position="420,0" size="140,40" alphatest="on" />\n\t\t<ePixmap  pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/yellow.png" position="280,0" size="140,40" alphatest="on" />\n\t\t<ePixmap  pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/ok.png" position="530,40" size="35,25" alphatest="on"  zPosition="2" />\n\t\t<widget name="key_menu" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/TSsatEditor/ddbuttons/key_menu.png" position="530,20" size="35,25" alphatest="on"  />\n\t\t<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />\n\t\t<widget name="list" position="0,64" size="560,240" scrollbarMode="showOnDemand" />\n\t\t<widget name="head" position="0,40" size="560,24" scrollbarMode="showNever" />\n\t\t<widget name="polhead" position="55,310" size="500,24" />\n\t\t<widget name="bandlist" position="0,334" size="55,72" />\n\t\t<widget name="infolist" position="55,334"  zPosition="2" size="505,72" />\n\t\t</screen>'

    def __init__(self, session):
        self.skin = SatellitesEditor.skin
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['SatellitesEditorActions'], {'nextPage': self.nextPage,
         'prevPage': self.prevPage,
         'displayHelp': self.showHelp,
         'displayInfo': self.showSatelliteInfo,
         'select': self.editTransponders,
         'exit': self.Exit,
         'left': self.left,
         'leftUp': self.doNothing,
         'leftRepeated': self.doNothing,
         'displayMenu': self.blihdscanXML,
         'right': self.right,
         'rightUp': self.doNothing,
         'rightRepeated': self.doNothing,
         'upUp': self.upUp,
         'up': self.up,
         'upRepeated': self.upRepeated,
         'upUp': self.upUp,
         'down': self.down,
         'downUp': self.downUp,
         'downRepeated': self.downRepeated,
         'red': self.removeSatellite,
         'green': self.editSatellite,
         'yellow': self.addSatellite,
         'blue': self.sortColumn}, -1)
        self['key_menu'] = Pixmap()
        if self.isBlihdscanXML():
            self['key_menu'].show()
        else:
            self['key_menu'].hide()
        self.satelliteslist = self.readSatellites('/etc/enigma2/satellites.xml')
        self['key_red'] = Button(_('Remove'))
        self['key_green'] = Button(_('Edit'))
        self['key_yellow'] = Button(_('Add'))
        self['key_blue'] = Button(_('Sort'))
        self['infolist'] = MenuList([])
        self['infolist'].l = eListboxPythonMultiContent()
        self['infolist'].l.setSelectionClip(eRect(0, 0, 0, 0))
        if FHD_Res:
            self['infolist'].l.setItemHeight(40)
            self['infolist'].l.setFont(0, gFont('Regular', 27))
        else:
            self['infolist'].l.setItemHeight(24)
            self['infolist'].l.setFont(0, gFont('Regular', 20))
        self['polhead'] = MenuList([])
        self['polhead'].l = eListboxPythonMultiContent()
        self['polhead'].l.setSelectionClip(eRect(0, 0, 0, 0))
        if FHD_Res:
            self['polhead'].l.setItemHeight(40)
            self['polhead'].l.setFont(0, gFont('Regular', 27))
        else:
            self['polhead'].l.setItemHeight(24)
            self['polhead'].l.setFont(0, gFont('Regular', 20))
        self['bandlist'] = MenuList([])
        self['bandlist'].l = eListboxPythonMultiContent()
        self['bandlist'].l.setSelectionClip(eRect(0, 0, 0, 0))
        if FHD_Res:
            self['bandlist'].l.setItemHeight(40)
            self['bandlist'].l.setFont(0, gFont('Regular', 27))
        else:
            self['bandlist'].l.setItemHeight(24)
            self['bandlist'].l.setFont(0, gFont('Regular', 20))
        self['head'] = Head()
        self['list'] = SatelliteList()
        self['list'].setEntries(self.satelliteslist)
        self.onLayoutFinish.append(self.layoutFinished)
        self.currentSelectedColumn = 0
        self.addNewSat = None
        self.updateSatList = False
        self.row = [['name', _('Satellites'), False], ['position', _('Position'), False]]

    def layoutFinished(self):
        global need_update
        need_update = False
        self.cleansatellitesxml()
        self.setTitle(_("TS-Satellites Editor:%s") %  currversion)
        try:
            row = self['list'].getCurrent()
            head = []
            for x in range(1, len(row)):
                head.append([row[x][1], row[x][3], ''])

            head[0][2] = self.row[0][1]
            head[1][2] = self.row[1][1]
            self['head'].setEntries(head)
            data = self['head'].l.getCurrentSelection()
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)
            self.updateSelection()
        except:
            pass

    def updateSelection(self):
        row = self['list'].l.getCurrentSelection()
        if row is None:
            return
        firstColumn = row[1]
        lastColumn = row[len(row) - 1]
        self['list'].l.setSelectionClip(eRect(firstColumn[1], firstColumn[0], lastColumn[1] + lastColumn[3], lastColumn[4]), True)
        self.getInfo()

    def doNothing(self):
        pass

    def left(self):
        if self.currentSelectedColumn:
            self.currentSelectedColumn -= 1
            data = self['head'].l.getCurrentSelection()
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)

    def right(self):
        if self.currentSelectedColumn < len(self.row) - 1:
            self.currentSelectedColumn += 1
            data = self['head'].l.getCurrentSelection()
            data = data[self.currentSelectedColumn + 1]
            self['head'].l.setSelectionClip(eRect(data[1], data[0], data[3], data[4]), True)

    def nextPage(self):
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is None: return
        self['list'].pageUp()
        self.lastSelectedIndex = cur_idx
        self.updateSelection()

    def prevPage(self):
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is None: return
        self['list'].pageDown()
        self.lastSelectedIndex = cur_idx
        self.updateSelection()

    def up(self):
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is None: return
        self['list'].up()
        self.lastSelectedIndex = cur_idx
        self.updateSelection()

    def down(self):
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is None: return
        self['list'].down()
        self.lastSelectedIndex = cur_idx
        self.updateSelection()

    def upUp(self):
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is None: return
        if self.lastSelectedIndex != cur_idx:
            self.lastSelectedIndex = cur_idx

    def downUp(self):
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is None: return
        if self.lastSelectedIndex != cur_idx:
            self.lastSelectedIndex = cur_idx

    def upRepeated(self):
        self['list'].up()
        self.updateSelection()

    def downRepeated(self):
        self['list'].down()
        self.updateSelection()

    def getInfo(self):
        cur_idx = self['list'].getSelectedIndex()
        if cur_idx is None: return
        satellite = self.satelliteslist[cur_idx]
        self.name = satellite[0].get('name')
        self.position = satellite[0].get('position')
        self.tp_all = len(satellite[1])
        self.tp_ku = 0
        self.tp_c = 0
        self.tp_other = 0
        self.tp_ku_v = 0
        self.tp_ku_h = 0
        self.tp_ku_l = 0
        self.tp_ku_r = 0
        self.tp_ku_v2 = 0
        self.tp_ku_h2 = 0
        self.tp_ku_l2 = 0
        self.tp_ku_r2 = 0
        self.tp_c_v = 0
        self.tp_c_h = 0
        self.tp_c_l = 0
        self.tp_c_r = 0
        self.tp_c_v2 = 0
        self.tp_c_h2 = 0
        self.tp_c_l2 = 0
        self.tp_c_r2 = 0
        self.tp_ku_dvb_s = 0
        self.tp_ku_dvb_s2 = 0
        self.tp_c_dvb_s = 0
        ku_band = False
        ka_band = False
        self.tp_c_dvb_s2 = 0
        for tp in satellite[1]:
            freq = int(tp.get('frequency'))
            pol = tp.get('polarization')
            system = tp.get('system')
            if freq >= 10700000 and freq <= 26500000:
                if freq < 12751000:
                    ku_band = True
                else:
                    ka_band = True
                if system == '0':
                    if pol == '0':
                        self.tp_ku_h += 1
                    elif pol == '1':
                        self.tp_ku_v += 1
                    elif pol == '2':
                        self.tp_ku_l += 1
                    elif pol == '3':
                        self.tp_ku_r += 1
                elif system == '1':
                    if pol == '0':
                        self.tp_ku_h2 += 1
                    elif pol == '1':
                        self.tp_ku_v2 += 1
                    elif pol == '2':
                        self.tp_ku_l2 += 1
                    elif pol == '3':
                        self.tp_ku_r2 += 1
            elif freq >= 3400000 and freq <= 4200000:
                if system == '0':
                    if pol == '0':
                        self.tp_c_h += 1
                    elif pol == '1':
                        self.tp_c_v += 1
                    elif pol == '2':
                        self.tp_c_l += 1
                    elif pol == '3':
                        self.tp_c_r += 1
                elif system == '1':
                    if pol == '0':
                        self.tp_c_h2 += 1
                    elif pol == '1':
                        self.tp_c_v2 += 1
                    elif pol == '2':
                        self.tp_c_l2 += 1
                    elif pol == '3':
                        self.tp_c_r2 += 1
        text_band = 'Ku/Ka'
        if ku_band and not ka_band:
            text_band = 'Ku'
        if ka_band and not ku_band:
            text_band = 'Ka'
        entryList = ('Band', text_band, 'C')
        l = []
        for entry in entryList:
            bandList = [None]
            if FHD_Res:
                bandList.append(MultiContentEntryText(pos=(0, 0), size=(120, 40), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=entry, border_width=1, border_color=15792383))
            elif HD_Res:
                bandList.append(MultiContentEntryText(pos=(0, 0), size=(80, 24), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=entry, border_width=1, border_color=15792383))
            else:
                bandList.append(MultiContentEntryText(pos=(0, 0), size=(55, 24), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, text=entry, border_width=1, border_color=15792383))
            l.append(bandList)

        self['bandlist'].l.setList(l)
        calc_xpos = lambda a: a[len(a) - 1][1] + a[len(a) - 1][3]
        entryList = (_('horizontal'),
         _('vertical'),
         _('circular left'),
         _('circular right'))
        xpos = 0
        PolarizationList = [None]
        x = FHD_Res and 275 or HD_Res and 205 or 125
        for entry in entryList:
            if FHD_Res:
                PolarizationList.append(MultiContentEntryText(pos=(xpos, 0), size=(x, 40), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=entry, border_width=1, border_color=15792383))
            else:
                PolarizationList.append(MultiContentEntryText(pos=(xpos, 0), size=(x, 24), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=entry, border_width=1, border_color=15792383))
            xpos = calc_xpos(PolarizationList)

        self['polhead'].l.setList([PolarizationList])
        l = []
        infolist = [None]
        if FHD_Res:
            entryList = (('dvb-s', 130),
             ('dvb-s2', 145),
             ('dvb-s', 130),
             ('dvb-s2', 145),
             ('dvb-s', 130),
             ('dvb-s2', 145),
             ('dvb-s', 130),
             ('dvb-s2', 145))
        elif HD_Res:
            entryList = (('dvb-s', 100),
             ('dvb-s2', 105),
             ('dvb-s', 100),
             ('dvb-s2', 105),
             ('dvb-s', 100),
             ('dvb-s2', 105),
             ('dvb-s', 100),
             ('dvb-s2', 105))
        else:
            entryList = (('dvb-s', 60),
             ('dvb-s2', 65),
             ('dvb-s', 60),
             ('dvb-s2', 65),
             ('dvb-s', 60),
             ('dvb-s2', 65),
             ('dvb-s', 60),
             ('dvb-s2', 65))
        xpos = 0
        y = FHD_Res and 75 or HD_Res and 50 or 24
        for entry in entryList:
            infolist.append(MultiContentEntryText(pos=(xpos, 0), size=(entry[1], y), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=entry[0], border_width=1, border_color=15792383))
            xpos = calc_xpos(infolist)

        l.append(infolist)
        infolist = [None]
        if FHD_Res:
            entryList = ((self.tp_ku_h, 130),
             (self.tp_ku_h2, 145),
             (self.tp_ku_v, 130),
             (self.tp_ku_v2, 145),
             (self.tp_ku_l, 130),
             (self.tp_ku_l2, 145),
             (self.tp_ku_r, 130),
             (self.tp_ku_r2, 145))
        elif HD_Res:
            entryList = ((self.tp_ku_h, 100),
             (self.tp_ku_h2, 105),
             (self.tp_ku_v, 100),
             (self.tp_ku_v2, 105),
             (self.tp_ku_l, 100),
             (self.tp_ku_l2, 105),
             (self.tp_ku_r, 100),
             (self.tp_ku_r2, 105))
        else:
            entryList = ((self.tp_ku_h, 60),
             (self.tp_ku_h2, 65),
             (self.tp_ku_v, 60),
             (self.tp_ku_v2, 65),
             (self.tp_ku_l, 60),
             (self.tp_ku_l2, 65),
             (self.tp_ku_r, 60),
             (self.tp_ku_r2, 65))
        xpos = 0
        for entry in entryList:
            infolist.append(MultiContentEntryText(pos=(xpos, 0), size=(entry[1], y), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=str(entry[0]).lstrip('0'), border_width=1, border_color=15792383))
            xpos = calc_xpos(infolist)

        l.append(infolist)
        infolist = [None]
        if FHD_Res:
            entryList = ((self.tp_c_h, 130),
             (self.tp_c_h2, 145),
             (self.tp_c_v, 130),
             (self.tp_c_v2, 145),
             (self.tp_c_l, 130),
             (self.tp_c_l2, 145),
             (self.tp_c_r, 130),
             (self.tp_c_r2, 145))
        elif HD_Res:
            entryList = ((self.tp_c_h, 100),
             (self.tp_c_h2, 105),
             (self.tp_c_v, 100),
             (self.tp_c_v2, 105),
             (self.tp_c_l, 100),
             (self.tp_c_l2, 105),
             (self.tp_c_r, 100),
             (self.tp_c_r2, 105))
        else:
            entryList = ((self.tp_c_h, 60),
             (self.tp_c_h2, 65),
             (self.tp_c_v, 60),
             (self.tp_c_v2, 65),
             (self.tp_c_l, 60),
             (self.tp_c_l2, 65),
             (self.tp_c_r, 60),
             (self.tp_c_r2, 65))
        xpos = 0
        for entry in entryList:
            if FHD_Res:
                infolist.append(MultiContentEntryText(pos=(xpos, 0), size=(entry[1], 40), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=str(entry[0]).lstrip('0'), border_width=1, border_color=15792383))
            else:
                infolist.append(MultiContentEntryText(pos=(xpos, 0), size=(entry[1], 24), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_TOP, text=str(entry[0]).lstrip('0'), border_width=1, border_color=15792383))
            xpos = calc_xpos(infolist)

        l.append(infolist)
        self['infolist'].l.setList(l)

    def readSatellites(self, file, stop=True):
		if not fileExists(file):
			if stop:
				self.close()
			else:
				self['key_menu'].hide()
			return None
		try:
			satellitesXML = xml.etree.cElementTree.parse(file)
			satDict = satellitesXML.getroot()
			satelliteslist = []
			for sat in satDict.getiterator('sat'):
				transponderslist = []
				for transponder in sat.getiterator('transponder'):
					transponderslist.append(transponder.attrib)
				try:
					sat_name = sat.attrib.get('name', 'new Satellite').decode('utf-8').encode('utf-8')
				except:
					sat_name = 'new Satellite'
				sat.attrib.update({'name': sat_name})
				satelliteslist.append([sat.attrib, transponderslist])
			return satelliteslist
		except:
			try:
				os.remove(file)
			except:
				pass
			if stop:
				self.close()
			else:
				self['key_menu'].hide()
		return None

    def writeSatellites(self):
		try:
			root = xml.etree.cElementTree.Element('satellites')
			root.text = '\n\t'
			transponder = None
			satellite = None
			for x in self.satelliteslist:
				satellite = xml.etree.cElementTree.SubElement(root, 'sat', x[0])
				satellite.text = '\n\t\t'
				satellite.tail = '\n\t'
				for y in x[1]:
					y = Transponder(y).exportClean()
					transponder = xml.etree.cElementTree.SubElement(satellite, 'transponder', y)
					transponder.tail = '\n\t\t'

				if transponder is not None:
					transponder.tail = '\n\t'

			if transponder is not None:
				transponder.tail = '\n\t'
			if satellite is not None:
				satellite.tail = '\n'
			tree = xml.etree.cElementTree.ElementTree(root)
			os.rename('/etc/enigma2/satellites.xml', '/etc/enigma2/satellites.xml.' + str(int(time.time())))
			tree.write('/etc/enigma2/satellites.xml')
			if not self.updateSatList:
				nimmanager.satList = []
				nimmanager.cablesList = []
				nimmanager.terrestrialsList = []
				nimmanager.readTransponders()
		except:
			try:
				os.remove('/etc/enigma2/satellites.xml')
			except:
				pass

    def addSatellite(self):
		text = _("Select action:")
		menu = [(_("Add new"), "new")]
		cur_idx = self['list'].getSelectedIndex()
		if cur_idx is not None:
			menu.append((_("Clone current"), "clone"))
		def addAction(choice):
			if choice:
				self.addNewSat = None
				if choice[1] == "new":
					self.session.openWithCallback(self.finishedSatAdd, SatEditor, self.satelliteslist)
				elif choice[1] == "clone":
					self.addNewSat = self.satelliteslist[cur_idx][1]
					self.session.openWithCallback(self.finishedSatAdd, SatEditor, self.satelliteslist, self.satelliteslist[cur_idx][0], clone=True)
		self.session.openWithCallback(addAction, ChoiceBox, title=text, list=menu)

    def finishedSatAdd(self, result):
		if result is None:
			return
		if self.addNewSat is None:
			self.satelliteslist.append([result, {}])
		else:
			self.satelliteslist.append([result, self.addNewSat])
		self.updateSatList = True
		self['list'].setEntries(self.satelliteslist)
		global need_update
		need_update = True

    def editTransponders(self):
		if not len(self.satelliteslist):
			return
		cur_idx = self['list'].getSelectedIndex()
		if cur_idx is None: return
		self.session.openWithCallback(self.finishedTranspondersEdit, TranspondersEditor, self.satelliteslist[cur_idx])

    def finishedTranspondersEdit(self, result):
		if result is None:
			return
		cur_idx = self['list'].getSelectedIndex()
		if cur_idx is None: return
		self.satelliteslist[cur_idx][1] = result
		global need_update
		need_update = True

    def editSatellite(self):
		if not len(self.satelliteslist):
			return
		cur_idx = self['list'].getSelectedIndex()
		if cur_idx is None: return
		self.session.openWithCallback(self.finishedSatEdit, SatEditor, self.satelliteslist, self.satelliteslist[cur_idx][0])

    def finishedSatEdit(self, result):
		if result is None:
			return
		cur_idx = self['list'].getSelectedIndex()
		if cur_idx is None: return
		pos = int(self.satelliteslist[cur_idx][0].get('position', '0'))
		now_pos = int(result.get('position', '0'))
		if pos != now_pos:
			self.updateSatList = True
		self.satelliteslist[cur_idx][0] = result
		self['list'].setEntries(self.satelliteslist)
		global need_update
		need_update = True

    def deleteSatellite(self):
		if len(self.satelliteslist):
			cur_idx = self['list'].getSelectedIndex()
			if cur_idx is None: return
			self.satelliteslist.pop(self['list'].getSelectedIndex())
			self['list'].setEntries(self.satelliteslist)
			global need_update
			self.updateSatList = True
			need_update = True

    def removeSatellite(self):
		if len(self.satelliteslist):
			cur_idx = self['list'].getSelectedIndex()
			if cur_idx is None: return
			satellite = self.satelliteslist[cur_idx][0].get('name')
			cb_func = lambda ret: not ret or self.deleteSatellite()
			self.session.openWithCallback(cb_func, MessageBox, _('Remove satellite %s?' % satellite), MessageBox.TYPE_YESNO)

    def compareColumn(self, a):
		if self.row[self.currentSelectedColumn][0] == 'name':
			return a[0].get('name')
		if self.row[self.currentSelectedColumn][0] == 'position':
			return int(a[0].get('position'))

    def sortColumn(self):
        if len(self.satelliteslist) <= 2:
            return
        rev = self.row[self.currentSelectedColumn][2]
        self.satelliteslist.sort(key=self.compareColumn, reverse=rev)
        if rev:
            self.row[self.currentSelectedColumn][2] = False
        else:
            self.row[self.currentSelectedColumn][2] = True
        self['list'].setEntries(self.satelliteslist)
        self.updateSelection()
        global need_update
        need_update = True

    def Exit(self):
		if need_update == False:
			pass
		else:
			cb_func = lambda ret: not ret or self.writeSatellites()
			self.session.openWithCallback(cb_func, MessageBox, _('Save new /etc/enigma2/satellites.xml? \n(This take some seconds.)'), MessageBox.TYPE_YESNO, default = False)
		self.cleansatellitesxml()
		global need_update
		need_update = False
		if self.updateSatList:
			self.close(self.session)
		else:
			self.close()

    def cleansatellitesxml(self):
		top = '/etc/enigma2/'
		for root, dirs, files in os.walk(top, topdown=False):
			for name in files:
				if 'satellites.xml.' in name:
					os.remove(os.path.join(root, name))

    def isBlihdscanXML(self):
		top = '/tmp/'
		for root, dirs, files in os.walk(top, topdown=False):
			for name in files:
				if 'blindscan' in name and '.xml' in name:
					return '/tmp/' + name
		return None

    def showSatelliteInfo(self):
		self.session.open(MessageBox, _('Autor original code mfaraj57\nFurther development Dimitrij openPLi'), MessageBox.TYPE_INFO)

    def blihdscanXML(self):
		self.addNewSat = None
		xml = self.isBlihdscanXML()
		if not xml: return
		text = _("Select action for blindscan.xml:")
		menu = [(_("Show blindscan.xml"), "show"),(_("Add in user satellites.xml"), "add")]
		def addAction(choice):
			if choice:
				if choice[1] == "show":
					self.session.open(Console,_('Show blindscan.xml'),["cat %s" % xml])
				elif choice[1] == "add":
					blindscan_satelliteslist = self.readSatellites(xml, stop=False)
					if blindscan_satelliteslist:
						self.addNewSat = blindscan_satelliteslist[0][1]
						self.session.openWithCallback(self.finishedSatAdd, SatEditor, self.satelliteslist, blindscan_satelliteslist[0][0], clone=True)
		self.session.openWithCallback(addAction, ChoiceBox, title=text, list=menu)

    def showHelp(self):
		pass
