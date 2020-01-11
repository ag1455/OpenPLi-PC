# -*- coding: utf-8 -*-

"""
    Universal Scrapers Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import re

def get_release_quality(release_name, release_link=None):

    if release_name is None: return

    try: release_name = release_name.encode('utf-8')
    except: pass

    try:
        quality = None

        fmt = re.sub('(.+)(\.|\(|\[|\s)(\d{4}|S\d+E\d+|S\d+)(\.|\)|\]|\s)', '', release_name)
        fmt = re.split('\.|\(|\)|\[|\]|\s|-|_', fmt)
        fmt = [i.lower() for i in fmt]

        p_qual = re.search("(?:\s|%20|\.|\_|\-|\(|\{|\/|\[|^)(\d{3,4})(?:p|$)(?:\s|\.|\_|\-|\)|\}|\/|\]|%20)", release_name.lower())
        if p_qual: quality = label_to_quality(p_qual.groups()[0])
        elif '.4k.' in fmt: quality = '4K'
        elif '.uhd' in fmt: quality = '4K'
        elif 'brrip' in fmt: quality = '720p'
        elif 'hdrip' in fmt: quality = '720p'
        elif 'hdtv' in fmt: quality = '720p'
        elif 'cam' in fmt: quality = 'CAM'
        elif any(i in ['dvdscr', 'r5', 'r6'] for i in fmt): quality = 'SCR'
        elif any(i in ['camrip', 'tsrip', 'hdcam', 'hdts', 'dvdcam', 'dvdts', 'cam', 'telesync', 'ts'] for i in fmt): quality = 'CAM'

        if not quality:
            if release_link:
                release_link = release_link.lower()
                try: release_link = release_link.encode('utf-8')
                except: pass
                p_qual = re.search("(?:\s|%20|\.|\_|\-|\(|\{|\/|\[|^)(\d{3,4})(?:p|$)(?:\s|\.|\_|\-|\)|\}|\/|\]|%20)", release_link)
                if p_qual: quality = label_to_quality(p_qual.groups()[0])
                elif '.4k.' in release_link: quality = '4K'
                elif '.uhd' in release_link: quality = '4K'
                elif '.hd' in release_link: quality = 'SD'
                elif 'hdrip' in release_link: quality = '720p'
                elif 'hdtv' in release_link: quality = '720p'
                elif 'cam' in release_link: quality = 'CAM'
                else:
                    if any(i in ['dvdscr', 'r5', 'r6'] for i in release_link): quality = 'SCR'
                    elif any(i in ['camrip', 'tsrip', 'hdcam', 'hdts', 'dvdcam', 'dvdts', 'cam', 'telesync', 'ts'] for i in release_link): quality = 'CAM'
                    else: quality = 'SD'
            else: quality = 'SD'
        info = []
        if '3d' in fmt or '.3D.' in release_name: info.append('3D')
        if any(i in ['hevc', 'h265', 'x265'] for i in fmt): info.append('HEVC')

        return quality, info
    except:
        return 'SD', ''

def check_sd_url(release_link):

    try:
        release_link = release_link.lower()
        if '2160' in release_link:
            quality = '4K'
        elif '1080' in release_link:
            quality = '1080p'
        elif '720' in release_link:
            quality = '720p'
        elif '.hd.' in release_link:
            quality = '720p'
        elif any(i in ['dvdscr', 'r5', 'r6'] for i in release_link):
            quality = 'SCR'
        elif any(i in ['camrip', 'tsrip', 'hdcam', 'hdts', 'dvdcam', 'dvdts', 'cam', 'telesync', 'ts'] for i in release_link):
            quality = 'CAM'
        else: quality = 'SD'

        return quality
    except:
        return 'SD'


def label_to_quality(label):
    try:
        try: label = int(re.search('(\d+)', label).group(1))
        except: label = 0

        if label >= 2160:
            return '4K'
        elif label >= 1440:
            return '1080p'
        elif label >= 1080:
            return '1080p'
        elif 720 <= label < 1080:
            return '720p'
        elif label < 720:
            return 'SD'
    except:
        return 'SD'

def _give_host(url):
    import urlparse
    elements = urlparse.urlparse(url)
    domain = elements.netloc or elements.path
    domain = domain.split('@')[-1].split(':')[0]
    regex = "(?:www\.)?([\w\-]*\.[\w\-]{2,3}(?:\.[\w\-]{2,3})?)$"
    res = re.search(regex, domain)
    if res: domain = res.group(1)
    host = domain.lower()
    return host