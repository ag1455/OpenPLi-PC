#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import downloads
from . import globalfunctions as jfunc
from . import jediglobals as jglob
from collections import OrderedDict

from .plugin import cfg
from xml.dom import minidom

import os
import re
import sys
import xml.etree.cElementTree as ET

sys.setrecursionlimit(2000)


def categoryBouquetXml(streamtype, bouquetTitle, bouquetString):
    cleanTitle = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '_', bouquetTitle)
    cleanTitle = re.sub(r' ', '_', cleanTitle)
    cleanTitle = re.sub(r'_+', '_', cleanTitle)
    filepath = '/etc/enigma2/'

    if cfg.groups.value is True:
        cleanGroup = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '_', jglob.name)
        cleanGroup = re.sub(r' ', '_', cleanGroup)
        cleanGroup = re.sub(r'_+', '_', cleanGroup)
        filepath = '/etc/enigma2/'
        filename = 'subbouquet.jmx_' + str(streamtype) + '_' + str(cleanTitle) + '.tv'
        fullpath = filepath + filename
    else:
        filename = 'userbouquet.jmx_' + str(streamtype) + '_' + str(cleanTitle) + '.tv'
        fullpath = filepath + filename
    with open(fullpath, 'w+') as f:
        f.write(bouquetString)


def bouquetsTvXml(streamtype, bouquetTitle):
    cleanTitle = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '_', bouquetTitle)
    cleanTitle = re.sub(r' ', '_', cleanTitle)
    cleanTitle = re.sub(r'_+', '_', cleanTitle)

    if cfg.groups.value is True:
        cleanGroup = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '_', jglob.name)
        cleanGroup = re.sub(r' ', '_', cleanGroup)
        cleanGroup = re.sub(r'_+', '_', cleanGroup)

        groupname = 'userbouquet.jmx_' + str(cleanGroup) + '.tv'

        with open('/etc/enigma2/bouquets.tv', 'r') as f:
            content = f.read()

        with open('/etc/enigma2/bouquets.tv', 'a+') as f:
            bouquetTvString = '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + str(groupname) + '" ORDER BY bouquet\n'
            if str(bouquetTvString) not in content:
                f.write(str(bouquetTvString))

        filename = '/etc/enigma2/' + str(groupname)

        with open(filename, 'a+') as f:
            nameString = "#NAME " + str(jglob.name) + "\n"
            f.write(str(nameString))

            filename = 'subbouquet.jmx_' + str(streamtype) + '_' + str(cleanTitle) + '.tv'
            bouquetTvString = '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + str(filename) + '" ORDER BY bouquet\n'
            f.write(str(bouquetTvString))

    else:
        filename = 'userbouquet.jmx_' + str(streamtype) + '_' + str(cleanTitle) + '.tv'

        with open('/etc/enigma2/bouquets.tv', 'a+') as f:
            bouquetTvString = '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + str(filename) + '" ORDER BY bouquet\n'
            f.write(str(bouquetTvString))


def buildXMLTVChannelFile(epg_name_list):

    cleanName = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '_', str(jglob.name))
    cleanName = re.sub(r' ', '_', cleanName)
    cleanName = re.sub(r'_+', '_', cleanName)

    cleanNameOld = re.sub(r'[\<\>\:\"\/\\\|\?\* ]', '_', str(jglob.old_name))
    cleanNameOld = re.sub(r' ', '_', cleanNameOld)
    cleanNameOld = re.sub(r'_+', '_', cleanNameOld)

    # remove old files
    jfunc.purge('/etc/epgimport', 'jmx.' + str(cleanName) + '.channels.xml')
    jfunc.purge('/etc/epgimport', 'jmx.' + str(cleanNameOld) + '.channels.xml')

    jfunc.purge('/etc/epgimport', 'jmx.' + str(cleanName) + '.sources.xml')
    jfunc.purge('/etc/epgimport', 'jmx.' + str(cleanNameOld) + '.sources.xml')

    filepath = '/etc/epgimport/'
    epgfilename = 'jmx.' + str(cleanName) + '.channels.xml'
    channelpath = filepath + epgfilename

    root = ET.Element('channels')

    # if xmltv file doesn't already exist, create file and build.
    if not os.path.isfile(channelpath):
        open(channelpath, 'a').close()

        for i in range(len(epg_name_list)):
            newchannel = ET.SubElement(root, 'channel')
            newchannel.set('id', epg_name_list[i][0])
            newchannel.text = epg_name_list[i][1]

        xml_str = ET.tostring(root).decode('utf-8')
        doc = minidom.parseString(xml_str)
        xml_output = doc.toprettyxml(indent='')
        xml_output = os.linesep.join([s for s in xml_output.splitlines() if s.strip()])
        with open(channelpath, 'w') as f:
            f.write(xml_output)
    else:
        tree = ET.parse(channelpath)
        root = tree.getroot()

        for channel in root.findall('channel'):
            root.remove(channel)

        for i in range(len(epg_name_list)):
            newchannel = ET.SubElement(root, 'channel')
            newchannel.set('id', epg_name_list[i][0])
            newchannel.text = epg_name_list[i][1]

        xml_str = str(ET.tostring(root, 'utf-8'))
        doc = minidom.parseString(xml_str)
        xml_output = doc.toprettyxml(encoding='utf-8', indent='')
        xml_output = os.linesep.join([s for s in xml_output.splitlines() if s.strip()])
        with open(channelpath, 'w') as f:
            f.write(xml_output)


def buildXMLTVSourceFile():

    cleanName = re.sub(r'[\<\>\:\"\/\\\|\?\* ]', '_', str(jglob.name))
    cleanName = re.sub(r' ', '_', cleanName)
    cleanName = re.sub(r'_+', '_', cleanName)

    filepath = '/etc/epgimport/'
    epgfilename = 'jmx.' + str(cleanName) + '.channels.xml'
    channelpath = filepath + epgfilename

    filename = 'jmx.' + str(cleanName) + '.sources.xml'
    sourcepath = filepath + filename

    with open(sourcepath, 'w') as f:
        xml_str = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml_str += '<sources>\n'
        xml_str += '<sourcecat sourcecatname="IPTV ' + str(cleanName) + '">\n'
        xml_str += '<source type="gen_xmltv" nocheck="1" channels="' + channelpath + '">\n'
        xml_str += '<description>' + str(cleanName) + '</description>\n'
        if jglob.fixepg:
            xml_str += '<url><![CDATA[' + str(filepath + 'jmx.' + str(cleanName) + '.xmltv2.xml') + ']]></url>\n'
        else:
            if "xmltv.php" in str(jglob.xmltv_address):
                xml_str += '<url><![CDATA[' + str(jglob.xmltv_address) + '&next_days=7]]></url>\n'
            else:
                xml_str += '<url><![CDATA[' + str(jglob.xmltv_address) + ']]></url>\n'

        xml_str += '</source>\n'
        xml_str += '</sourcecat>\n'
        xml_str += '</sources>\n'
        f.write(xml_str)


def downloadXMLTV():

    cleanName = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '_', str(jglob.name))
    cleanName = re.sub(r' ', '_', cleanName)
    cleanName = re.sub(r'_+', '_', cleanName)

    cleanNameOld = re.sub(r'[\<\>\:\"\/\\\|\?\* ]', '_', str(jglob.old_name))
    cleanNameOld = re.sub(r' ', '_', cleanNameOld)
    cleanNameOld = re.sub(r'_+', '_', cleanNameOld)

    jfunc.purge('/etc/epgimport', 'jmx.' + str(cleanName) + '.xmltv.xml')
    jfunc.purge('/etc/epgimport', 'jmx.' + str(cleanNameOld) + '.xmltv.xml')
    jfunc.purge('/etc/epgimport', 'jmx.' + str(cleanName) + '.xmltv2.xml')
    jfunc.purge('/etc/epgimport', 'jmx.' + str(cleanNameOld) + '.xmltv2.xml')

    filepath = '/etc/epgimport/'
    epgfilename = 'jmx.' + str(cleanName) + '.xmltv.xml'
    epgpath = filepath + epgfilename
    response = downloads.checkGZIP(jglob.xmltv_address)

    if response is not None:

        with open(epgpath, 'w') as f:
            f.write(response)

        with open(epgpath, 'r') as f:
            # tree = ET.parse(f)
            tree = ET.parse(f, parser=ET.XMLParser(encoding='utf-8'))

        tree.write('/etc/epgimport/' + 'jmx.' + str(cleanName) + '.xmltv2.xml', encoding='utf-8', xml_declaration=True)
