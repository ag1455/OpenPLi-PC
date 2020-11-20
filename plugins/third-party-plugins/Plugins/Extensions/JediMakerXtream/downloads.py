#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict
import os
import re
from Components.config import *
from plugin import cfg, hdr, rytec_url, rytec_file, sat28_file, alias_file
import urllib2
import json
import socket
import jediglobals as jglob

def transferChunked(url):
    streamdata = []
    try:
        import requests
    except ImportError:
        return streamdata

    response = requests.get(url, stream=True)
    for data in response.iter_lines():
        if data:
            try:
                streamdata = json.loads(data, object_pairs_hook=OrderedDict)
            except:
                pass

    return streamdata


def downloadlivecategories(liveurl):
    jglob.livecategories = []
    jglob.haslive = False

    response = ''

    req = urllib2.Request(liveurl, headers=hdr)
    try:
        response = urllib2.urlopen(req)

    except urllib2.URLError as e:
        print e
        pass

    except socket.timeout as e:
        print e
        pass

    except SocketError as e:
        print e
        pass

    try:
        jglob.livecategories = json.load(response)
    except ValueError as e:
        print "\n ***** download live error - trying transferChunked method ***** "
        print e
        jglob.livecategories = transferChunked(liveurl)


    print jglob.livecategories
    if jglob.livecategories != []:
        jglob.livecategories.append({'category_id':'0','category_name':'Live Not Categorised','parent_id':0})

    if jglob.livecategories != [] and 'user_info' not in jglob.livecategories and 'category_id' in jglob.livecategories[0]:
        jglob.haslive = True

    if jglob.haslive == False:
        jglob.livecategories = []


def downloadvodcategories(vodurl):
    jglob.vodcategories = []
    jglob.hasvod = False
    response = ''
    req = urllib2.Request(vodurl, headers=hdr)
    try:
        response = urllib2.urlopen(req)

    except urllib2.URLError as e:
        print e
        pass

    except socket.timeout as e:
        print e
        pass

    except SocketError as e:
        print e
        pass

    try:
        jglob.vodcategories = json.load(response)
    except:
        print "\n ***** download vod error - trying transferChunked method ***** "
        jglob.vodcategories = transferChunked(vodurl)

    if jglob.vodcategories != []:
        jglob.vodcategories.append({'category_id':'0','category_name':'Vod Not Categorised','parent_id':0})

    if jglob.vodcategories != [] and 'user_info' not in jglob.vodcategories and 'category_id' in jglob.vodcategories[0]:
        jglob.hasvod = True

    if jglob.hasvod == False:
        jglob.vodcategories = [] 


def downloadseriescategories(seriesurl):
    jglob.seriescategories = []
    jglob.hasseries = False

    response = ''
    req = urllib2.Request(seriesurl, headers=hdr)
    try:
        response = urllib2.urlopen(req)

    except urllib2.URLError as e:
        print e
        pass

    except socket.timeout as e:
        print e
        pass

    except SocketError as e:
        print e
        pass

    try:
        jglob.seriescategories = json.load(response)

    except:
        print "\n ***** download vseries error - trying transferChunked method ***** "
        jglob.seriescategories = transferChunked(seriesurl)

    if jglob.seriescategories != [] and 'user_info' not in jglob.seriescategories and 'category_id' in jglob.seriescategories[0]:
        jglob.hasseries = True

    if jglob.hasseries == False:
        jglob.seriescategories = []


def downloadlivestreams(liveurl):
    jglob.livestreams = []

    req = urllib2.Request(liveurl, headers=hdr)
    try:
        response = urllib2.urlopen(req)

    except urllib2.URLError as e:
        jglob.haslive = False
        print e
        pass

    except socket.timeout as e:
        jglob.haslive = False
        print e
        pass

    except SocketError as e:
        print e
        pass

    try:
        jglob.livestreams = json.load(response)
    except:
        jglob.livestreams = transferChunked(liveurl)

    if jglob.livestreams == [] or 'user_info' in jglob.livestreams or 'category_id' not in jglob.livestreams[0]:
        jglob.haslive = False

    if jglob.haslive == False:
        jglob.livestreams = []


def downloadvodstreams(vodurl):
    jglob.vodstreams = []

    req = urllib2.Request(vodurl, headers=hdr)
    try:
        response = urllib2.urlopen(req)

    except urllib2.URLError as e:
        jglob.hasvod = False
        print e
        pass

    except socket.timeout as e:
        jglob.hasvod = False
        print e
        pass

    except SocketError as e:
        print e
        pass

    try:
        jglob.vodstreams = json.load(response)
    except:
        jglob.vodstreams = transferChunked(vodurl)

    if jglob.vodstreams == [] or 'user_info' in jglob.vodstreams or 'category_id' not in jglob.vodstreams[0]:
        jglob.hasvod = False

    if jglob.hasvod == False:
        jglob.vodstreams = []


def downloadseriesstreams(seriesurl):
    jglob.seriesstreams = []

    req = urllib2.Request(seriesurl, headers=hdr)
    try:
        response = urllib2.urlopen(req)

    except urllib2.URLError as e:
        jglob.hasseries = False
        print e
        pass
    except socket.timeout as e:
        jglob.hasseries = False
        print e
        pass

    except SocketError as e:
        print e
        pass

    try:
        jglob.seriesstreams = json.load(response)
    except:
        jglob.seriesstreams = transferChunked(seriesurl) 

    if jglob.seriesstreams == [] or 'user_info' in jglob.seriesstreams or 'category_id' not in jglob.seriesstreams[0]:
        jglob.hasseries = False

    if jglob.hasseries == False:
        jglob.seriersstreams = []


def getM3uCategories(live,vod):

    lines = []
    myfile = []

    address = jglob.current_playlist['playlist_info']['address']

    if jglob.current_playlist['playlist_info']['playlisttype'] == 'external':

        req = urllib2.Request(address, headers=hdr)
        try:
            response = urllib2.urlopen(req, timeout=cfg.timeout.value)
            #myfile = response.read()
            lines = response.read().splitlines(True)
        except urllib2.URLError as e:
            print e
            pass
        except socket.timeout as e:
            print e
            pass

        except SocketError as e:
            print e
            pass

    elif jglob.current_playlist['playlist_info']['playlisttype'] == 'local':
        with open(cfg.m3ulocation.value + address) as f:
            lines = f.readlines()

    prevline = ''
    channelnum = 0
    jglob.getm3ustreams = []

    for line in lines:

        if line == '':
            continue

        group_title = ''
        epg_name = ''
        name = ''
        source = ''

        if prevline != '':
            if prevline.upper().startswith('#EXTINF') and line.startswith('http'):

                if re.search('(?<=group-title=")[^"]+', prevline) is not None:
                    group_title = re.search('(?<=group-title=")[^"]+', prevline).group()

                if re.search('(?<=tvg-id=")[^"]+', prevline) is not None:
                    epg_name = re.search('(?<=tvg-id=")[^"]+', prevline).group()

                if re.search('((?<=",).*$|(?<=1,).*$|(?<=0,).*$)', prevline) is not None:
                    name = re.search('((?<=",).*$|(?<=1,).*$|(?<=0,).*$)', prevline).group().strip()

                if name == '':
                    channelnum += 1
                    name = 'Channel ' + str(channelnum)
                source = line.rstrip()

                if live:
                    if source.endswith('.ts') or source.endswith('.m3u8') or source[-1].isdigit():
                        if group_title == '':
                            group_title = 'Uncategorised Live'
                        jglob.getm3ustreams.append([group_title, epg_name, name, source, 'live'])

                if vod:
                    if not source.endswith('.ts') and not source.endswith('.m3u8') and not source[-1].isdigit():
                        if group_title == '':
                            group_title = 'Uncategorised VOD'
                        jglob.getm3ustreams.append([group_title, epg_name, name, source, 'vod'])
        prevline = line


def downloadrytec():

    haslzma = False

    try:
        import lzma
        print '\nlzma success'
        haslzma = True

    except ImportError:

        try:
            from backports import lzma
            print '\nbackports lzma success'
            haslzma = True

        except ImportError:
            print '\nlzma failed'
            pass


    req = urllib2.Request(rytec_url, headers=hdr)
    try:
        response = urllib2.urlopen(req)
        with open(rytec_file,'wb') as output:
            output.write(response.read())

    except urllib2.URLError as e:
        print e
        pass

    except socket.timeout as e:
        print e
        pass

    except SocketError as e:
        print e
        pass

    if os.path.isfile(rytec_file) and os.stat(rytec_file).st_size > 0 and haslzma:
        with lzma.open(rytec_file, 'rb') as fd:
            with open(sat28_file, 'w') as outfile:
                for line in fd:
                    # get all 28.2e but ignore bad epg importer refs 
                    if '28.2E' in line \
                    and '1:0:1:2F12:7EF:2:11A0000:0:0:0:' not in line \
                    and '1:0:1:1262:7EA:2:11A0000:0:0:0:' not in line \
                    and '1:0:19:F79:7E9:2:11A0000:0:0:0:' not in line \
                    and '1:0:19:C472:837:2:11A0000:0:0:0:' not in line \
                    and '1:0:19:CCC:7D2:2:11A0000:0:0:0:' not in line \
                    and '1:0:1:2EEF:7EF:2:11A0000:0:0:0:' not in line :
                        outfile.write(line)

        ###################################################################################################
        # read rytec 28.2e file

        with open(sat28_file, 'r') as outfile:
            rytec_sat28 = outfile.readlines();
        rytec_ref = {}

        for line in rytec_sat28:

            serviceref = ''
            epg_channel_id = ''
            channelname = ''

            if re.search('(?<=<\/channel><!-- ).*(?= --)', line) is not None:
                channelname = re.search('(?<=<\/channel><!-- ).*(?= --)', line).group()

            if re.search('(?<=\">1).*(?=<\/)', line) is not None:
                serviceref = re.search('(?<=\">1).*(?=<\/)', line).group()

            if re.search('(?<=id=\")[a-zA-Z0-9\.]+', line) is not None:
                epg_channel_id = re.search('(?<=id=\")[a-zA-Z0-9\.]+', line).group() 

            rytec_ref[channelname.lower()] = [serviceref, epg_channel_id, channelname]


        ###################################################################################################
        # read iptv name file

        epg_alias_names = []

        if os.path.isfile(alias_file) and os.stat(alias_file).st_size > 0:
            with open(alias_file) as f:
                try:
                    epg_alias_names = json.load(f)
                except ValueError as e:
                    print str(e) + '\n******** broken alias.txt file ***********'
                    print '\n******** check alias.txt file with https://jsonlint.com ********'

        ###################################################################################################

        return rytec_ref, epg_alias_names


def downloadgetfile(get_api):

    download = False

    req = urllib2.Request(get_api, headers=hdr)
    try:
        response = urllib2.urlopen(req)
        download = True
    except urllib2.URLError as e:
        print e
        pass

    except socket.timeout as e:
        print e
        pass

    except SocketError as e:
        print e
        pass


    channelnum = 0
    m3uValues = {}
    if download:
        for line in response:
            series_group_title = 'Uncategorised'
            series_name = ''
            series_container_extension = ''
            series_url = ''
            if not line.startswith('#EXTINF') and not line.startswith('http'):
                continue
            if line.startswith('#EXTINF'):

                if re.search('(?<=group-title=")[^"]+', line) is not None:
                    series_group_title = re.search('(?<=group-title=")[^"]+', line).group()

                if re.search('((?<=",).*$|(?<=1,).*$|(?<=0,).*$)', line) is not None:
                    series_name = re.search('((?<=",).*$|(?<=1,).*$|(?<=0,).*$)', line).group().strip()

                if series_name == '':
                    channelnum += 1
                    series_name = 'Channel ' + str(channelnum)


                nextline = response.next()
                if nextline.startswith('http'):
                    series_url = nextline.strip()

            if series_url != '' and '/series/' in series_url:
                if series_group_title not in m3uValues:
                    m3uValues[series_group_title] = [{'name': series_name, 'url': series_url}]
                else:
                    m3uValues[series_group_title].append({'name': series_name, 'url': series_url})

    return m3uValues
