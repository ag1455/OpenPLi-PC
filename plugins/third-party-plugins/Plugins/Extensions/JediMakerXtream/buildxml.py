#!/usr/bin/python
# -*- coding: utf-8 -*-

from xml.dom import minidom
from xml.dom.minidom import parse, parseString
import xml.etree.cElementTree as ET
import re
import os
import jediglobals as jglob
import globalfunctions as jfunc


def categoryBouquetXml(streamtype, bouquetTitle, bouquetString):
    cleanTitle = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '_', bouquetTitle)
    cleanTitle = re.sub(r' ', '_', cleanTitle)
    cleanTitle = re.sub(r'_+', '_', cleanTitle)

    filepath = '/etc/enigma2/'
    filename = 'userbouquet.jmx_' + str(streamtype) + '_' + str(cleanTitle) + '.tv'
    fullpath = filepath + filename
    with open(fullpath, 'w+') as f:
        f.write(bouquetString)


def bouquetsTvXml(streamtype, bouquetTitle):
    cleanTitle = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '_', bouquetTitle)
    cleanTitle = re.sub(r' ', '_', cleanTitle)
    cleanTitle = re.sub(r'_+', '_', cleanTitle)

    filename = 'userbouquet.jmx_' + str(streamtype) + '_' + str(cleanTitle) + '.tv'
    with open('/etc/enigma2/bouquets.tv', 'a+') as f:
        bouquetTvString = '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + filename + '" ORDER BY bouquet\r\n'
        if bouquetTvString not in f:
            f.write(bouquetTvString)


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

    bouquetfilepath = '/etc/enigma2/'
    root = ET.Element('channels')

    # if xmltv file doesn't already exist, create file and build.
    if not os.path.isfile(channelpath):
        open(channelpath, 'a').close()

        for i in range(len(epg_name_list)):
            newchannel = ET.SubElement(root, 'channel')
            newchannel.set('id', epg_name_list[i][0])
            newchannel.text = epg_name_list[i][1]

        xml_str = str(ET.tostring(root, 'utf-8'))
        doc = minidom.parseString(xml_str)
        xml_output = doc.toprettyxml(encoding='utf-8', indent='')
        xml_output = os.linesep.join([ s for s in xml_output.splitlines() if s.strip() ])
        with open(channelpath, 'w') as f:
            f.write(xml_output)
    else:
        tree = ET.parse(channelpath)
        root = tree.getroot()
        e = str(ET.tostring(root, 'utf-8'))

        for channel in root.findall('channel'):
            root.remove(channel)

        for i in range(len(epg_name_list)):
            newchannel = ET.SubElement(root, 'channel')
            newchannel.set('id', epg_name_list[i][0])
            newchannel.text = epg_name_list[i][1]

        xml_str = str(ET.tostring(root, 'utf-8'))
        doc = minidom.parseString(xml_str)
        xml_output = doc.toprettyxml(encoding='utf-8', indent='')
        xml_output = os.linesep.join([ s for s in xml_output.splitlines() if s.strip() ])
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
        xml_str += '<url><![CDATA[' + str(jglob.xmltv_address) + ']]></url>\n'
        xml_str += '</source>\n'
        xml_str += '</sourcecat>\n'
        xml_str += '</sources>\n'
        f.write(xml_str)
