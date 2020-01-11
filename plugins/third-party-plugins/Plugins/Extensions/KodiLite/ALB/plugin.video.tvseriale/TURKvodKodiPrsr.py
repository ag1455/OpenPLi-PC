# -*- coding: utf-8 -*-
try:
    import ssl
    import socket
    timeout = 10
    socket.setdefaulttimeout(timeout)
except ImportError:
    pass

import re, urllib, urllib2, os, cookielib, base64, sys, random, math
from urlparse import parse_qs, urlparse, urljoin, urlsplit, urlunsplit
import time
from urllib2 import HTTPError, URLError
import htmlentitydefs
import string
import xbmc
import xbmcgui
import json
try:
    import httplib
except:
    pass

UA = 'Mozilla/5.0 TURKvod 8.0'
FF_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
IE_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko'
HEADERS = {"User-Agent":FF_USER_AGENT}

def mydebug():
    pass

def compat_ord(c):
    if type(c) is int:
        return c
    else:
        return ord(c)

try:
    compat_chr = unichr  # Python 2
except NameError:
    compat_chr = chr

try:
    import pafy
    pfy = True
except ImportError:
    pfy = False

def versiyon(parser_ver = '<h1>(.*?)</h1></td>\\W*</tr>\\W*<tr>\\W*<td align="right"><h3>(.*?)</h3></td>\\W*<td align="left"><h2>(.*?)</h2></td>\\W*</tr>\\W*<tr>\\W*<td align="right"><h3>(.*?)</h3></td>\\W*<td align="left"><h2>(.*?)</h2>'):
    return parser_ver

class cPacker():
    def detect(self, source):
        """Detects whether `source` is P.A.C.K.E.R. coded."""
        return source.replace(' ', '').startswith('eval(function(p,a,c,k,e,')

    def unpack(self, source):
        """Unpacks P.A.C.K.E.R. packed js code."""
        payload, symtab, radix, count = self._filterargs(source)

        if count != len(symtab):
            raise UnpackingError('Malformed p.a.c.k.e.r. symtab.')

        try:
            unbase = Unbaser(radix)
        except TypeError:
            raise UnpackingError('Unknown p.a.c.k.e.r. encoding.')

        def lookup(match):
            """Look up symbols in the synthetic symtab."""
            word  = match.group(0)
            return symtab[unbase(word)] or word

        source = re.sub(r'\b\w+\b', lookup, payload)
        return self._replacestrings(source)

    def _cleanstr(self, str):
        str = str.strip()
        if str.find("function") == 0:
            pattern = (r"=\"([^\"]+).*}\s*\((\d+)\)")
            args = re.search(pattern, str, re.DOTALL)
            if args:
                a = args.groups()
                def openload_re(match):
                    c = match.group(0)
                    b = ord(c) + int(a[1])
                    return chr(b if (90 if c <= "Z" else 122) >= b else b - 26)

                str = re.sub(r"[a-zA-Z]", openload_re, a[0]);
                str = urllib2.unquote(str)

        elif str.find("decodeURIComponent") == 0:
            str = re.sub(r"(^decodeURIComponent\s*\(\s*('|\"))|(('|\")\s*\)$)", "", str);
            str = urllib2.unquote(str)
        elif str.find("\"") == 0:
            str = re.sub(r"(^\")|(\"$)|(\".*?\")", "", str);
        elif str.find("'") == 0:
            str = re.sub(r"(^')|('$)|('.*?')", "", str);

        return str

    def _filterargs(self, source):
        """Juice from a source file the four args needed by decoder."""

        source = source.replace(',[],',',0,')

        juicer = (r"}\s*\(\s*(.*?)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*\((.*?)\).split\((.*?)\)")
        args = re.search(juicer, source, re.DOTALL)
        if args:
            a = args.groups()
            try:
                return self._cleanstr(a[0]), self._cleanstr(a[3]).split(self._cleanstr(a[4])), int(a[1]), int(a[2])
            except ValueError:
                raise UnpackingError('Corrupted p.a.c.k.e.r. data.')

        juicer = (r"}\('(.*)', *(\d+), *(\d+), *'(.*)'\.split\('(.*?)'\)")
        args = re.search(juicer, source, re.DOTALL)
        if args:
            a = args.groups()
            try:
                return a[0], a[3].split(a[4]), int(a[1]), int(a[2])
            except ValueError:
                raise UnpackingError('Corrupted p.a.c.k.e.r. data.')

        # could not find a satisfying regex
        raise UnpackingError('Could not make sense of p.a.c.k.e.r data (unexpected code structure)')



    def _replacestrings(self, source):
        """Strip string lookup table (list) and replace values in source."""
        match = re.search(r'var *(_\w+)\=\["(.*?)"\];', source, re.DOTALL)

        if match:
            varname, strings = match.groups()
            startpoint = len(match.group(0))
            lookup = strings.split('","')
            variable = '%s[%%d]' % varname
            for index, value in enumerate(lookup):
                source = source.replace(variable % index, '"%s"' % value)
            return source[startpoint:]
        return source

def UnpackingError(Exception):
    #Badly packed source or general error.#
    #xbmc.log(str(Exception))
    print Exception
    pass


class Unbaser(object):
    """Functor for a given base. Will efficiently convert
    strings to natural numbers."""
    ALPHABET = {
        62: '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        95: (' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ'
             '[\]^_`abcdefghijklmnopqrstuvwxyz{|}~')
    }

    def __init__(self, base):
        self.base = base

        #Error not possible, use 36 by defaut
        if base == 0 :
            base = 36

        # If base can be handled by int() builtin, let it do it for us
        if 2 <= base <= 36:
            self.unbase = lambda string: int(string, base)
        else:
            if base < 62:
                self.ALPHABET[base] = self.ALPHABET[62][0:base]
            elif 62 < base < 95:
                self.ALPHABET[base] = self.ALPHABET[95][0:base]
            # Build conversion dictionary cache
            try:
                self.dictionary = dict((cipher, index) for index, cipher in enumerate(self.ALPHABET[base]))
            except KeyError:
                raise TypeError('Unsupported base encoding.')

            self.unbase = self._dictunbaser

    def __call__(self, string):
        return self.unbase(string)

    def _dictunbaser(self, string):
        """Decodes a  value to an integer."""
        ret = 0

        for index, cipher in enumerate(string[::-1]):
            ret += (self.base ** index) * self.dictionary[cipher]
        return ret

def myrequest(url, postfields = {}, headers = {}, cookie = 'cookie.lpw', loc = None, useragent = ''):
    """
        url = 'http://www.diziizleyin.net/index.php?x=isyan'
        postfields = {'pid' : 'p2x29464a434'}
        txheaders = {'X-Requested-With':'XMLHttpRequest'}
        myrequest(url, postfields, txheaders, loc)
    """
    if not useragent:
        useragent = UA
    url = url if url.startswith('http://') else 'http://' + url
    req = urllib2.Request(url)
    cj = cookielib.LWPCookieJar()
    if os.path.isfile('cookie.lpw'):
        cj.load('cookie.lpw')
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    if postfields:
        postfields = urllib.urlencode(postfields)
        req = urllib2.Request(url, postfields)
    req.add_header('User-Agent', useragent)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)

    response = urllib2.urlopen(req)
    if loc:
        data = response.geturl()
        response.close()
    else:
        data = response.read()
        response.close()
        cookiepath = 'cookies.lwp'
        addonId = "plugin.video.turkvod"
        dataroot = xbmc.translatePath('special://profile/addon_data/%s' % (addonId)).decode('utf-8')
        cj.save( os.path.join( dataroot, cookiepath ) )		
    return data

class urlKap(object):
    """
        urlKap(url).result
        urlKap(url, output = 'geturl').result
        urlKap(url, output = 'cookie').result
        urlKap(url, timeout='30').result
        post = {'hash':media_id}
        urlKap(url, post = post).result
        url = 'http://www.diziizleyin.net/index.php?x=isyan'
        postfields = {'pid' : 'p2x29464a434'}
        txheaders = {'X-Requested-With':'XMLHttpRequest'}
        urlKap(url, postfields, headers, loc)
    """

    def __init__(self, url, close = True, proxy = None, post = None, mobile = False, referer = None, cookie = None, output = '', timeout = '10'):
        if not proxy == None:
            proxy_handler = urllib2.ProxyHandler({'http': '%s' % proxy})
            opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
            opener = urllib2.install_opener(opener)
        if output == 'cookie' or output == 'kukili' or not close == True:
            import cookielib
            cookie_handler = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
            opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
            opener = urllib2.install_opener(opener)
        if not post == None:
            post = urllib.urlencode(post)
            request = urllib2.Request(url, post)
        else:
            request = urllib2.Request(url, None)
        if mobile == True:
            request.add_header('User-Agent', 'Mozilla/5.0 (iPhone; CPU; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7')
        else:
            request.add_header('User-Agent', UA)
        if not referer == None:
            request.add_header('Referer', referer)
        if not cookie == None:
            request.add_header('cookie', cookie)
        response = urllib2.urlopen(request, timeout=int(timeout))
        if output == 'cookie':
            result = str(response.headers.get('Set-Cookie'))
        elif output == 'kukili':
            result = response.read() + 'kuki :' + str(response.headers.get('Set-Cookie'))
        elif output == 'geturl':
            result = response.geturl()
        elif output == 'lenght':
            result = str(response.headers.get('Content-Length'))
        else:
            result = response.read()
        if close == True:
            response.close()
        self.result = result


class turkvod_parsers:

    def __init__(self):
        self.quality = ''
        mydebug()

    def get_parsed_link(self, url):
        if url.startswith('//www.'):
            url = 'http:' + url
        elif url.startswith('www.'):
            url = 'http://' + url
        elif url.startswith('//'):
            url = 'http:' + url
        son_url = ''
        film_quality = []
        video_tulpe = []
        error = None
        try:

            if 'kodik' in url:
                try:
                    headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'}
                    req = urllib2.Request(url,None,headers)
                    response = urllib2.urlopen(req)
                    html = response.read()
                    response.close()
                    url_kodik = re.findall('(kodik.cc/go/[^"]+)"', html, re.IGNORECASE)[0]
                    url_kodik = 'http://' + url_kodik
                    req = urllib2.Request(url_kodik,None,headers)
                    response = urllib2.urlopen(req)
                    html_kodik = response.read()
                    response.close()
                    d_sign, pd, pd_sign, hash, id   = re.findall("d_sign: '([^']+)',\s+pd: '([^']+)',\s+pd_sign: '([^']+)',[\s+\S+]*?hash: '([^']+)',\s+id: '([^']+)'", html_kodik, re.IGNORECASE)[0]
                    data = urllib.urlencode({'d': 'kodik.cc', 'd_sign': d_sign, 'pd': 'kodik.cc', 'pd_sign': pd_sign, 'bad_user': 'false', 'type': 'video', 'hash': hash, 'id': id })
                    url = 'http://kodik.cc/get-video'
                    req = urllib2.Request(url, data, headers)
                    response = urllib2.urlopen(req)
                    link = response.read()
                    response.close()
                    for match in re.finditer('"([^"]+)":\[\{"src":"(.*?mp4)', link):
                        film_quality.append(match.group(1))
                        video_tulpe.append('http:' + match.group(2))
                except Exception as ex:
                    print ex

            if 'sosyalizle' in url:
                try:
                    headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'}
                    req = urllib2.Request(url,None,headers)
                    response = urllib2.urlopen(req)
                    html = response.read()
                    response.close()
                    embedlink = re.findall('(embedlive.flexmmp.com[^"]+)"', html, re.IGNORECASE)[0]
                    embedlink = 'http://'+embedlink.replace('&#038;','&')
                    headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.04',
                            'Referer': url }
                    req = urllib2.Request(embedlink,None,headers)
                    response = urllib2.urlopen(req)
                    html1 = response.read()
                    response.close()
                    videolink = re.findall("hls: ?'([^']+)'", html1, re.IGNORECASE)[0]
                    son_url = 'https:' + videolink
                except Exception as ex:
                    print ex

            if 'idtbox' in url:
                try:
                    url = url.replace('https', 'http')
                    html = myrequest(url)
                    for match in re.finditer('src="([^"]+)" type=".*?label="([^"]+)"', html):
                        film_quality.append(match.group(2))
                        video_tulpe.append(match.group(1) + '#User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0' + '&Referer=' + url)
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'canlitvplayer' in url:
                try:
                    headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'}
                    req = urllib2.Request(url,None,headers)
                    response = urllib2.urlopen(req)
                    html = response.read()
                    response.close()
                    embedlink = re.findall('src="(/tv/embed.php[^"]+)"', html, re.IGNORECASE)[0]
                    embedlink = 'http://www.canlitvplayer.com'+embedlink.replace('&#038;','&')
                    headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.04',
                            'Referer': url }
                    req = urllib2.Request(embedlink,None,headers)
                    response = urllib2.urlopen(req)
                    html1 = response.read()
                    response.close()
                    videolink = re.findall('source src="([^"]+)"', html1, re.IGNORECASE)[0]
                    son_url = videolink
                except Exception as ex:
                    print ex

            if 'vshare' in url:
                try:
                    html = urlKap(url).result
                    packed = re.findall("(eval\\(function.*?)\\n", html, re.IGNORECASE)[0]
                    js = cPacker().unpack(packed).split(';')
                    charcodes = [int(val) for val in js[1].split('=')[-1].replace('[', '').replace(']', '').split(',')]
                    sub = int(''.join(char for char in js[2].split('-')[1] if char.isdigit()))
                    charcodes = [val-sub for val in charcodes]
                    srcs = ''.join(map(unichr, charcodes))
                    for match in re.finditer(u'src="([^"]+)".*?label="([^"]+)"', srcs):
                        film_quality.append(match.group(2).encode('utf-8'))
                        video_tulpe.append(match.group(1).encode('utf-8'))
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'tvcatchup' in url:
                try:
                    html = myrequest(url)
                    son_url = re.findall('source src="(.*?)" type', html)[0]
                    son_url = son_url.replace('https', 'http')
                except Exception as ex:
                    print ex

            if 'vidlox' in url:
                try:
                    headers = {'User-Agent': FF_USER_AGENT, 'Referer': url}
                    url = url.replace('https', 'http')
                    html = urlKap(url, headers).result
                    for match in re.finditer('"(http[^"]+(m3u8|mp4))"', html):
                        film_quality.append(match.group(2))
                        video_tulpe.append(match.group(1) + '#Referer=' +url+ '&User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0')
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'strdef' in url:
                try:
                    def decode_base64(data):
                        missing_padding = len(data) % 4
                        if missing_padding != 0:
                            data += b'='* (4 - missing_padding)
                        return base64.decodestring(data)

                    headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.04',
                            'Referer': url }
                    req = urllib2.Request(url, None, headers)
                    response = urllib2.urlopen(req)
                    data = response.read()
                    link = re.findall('document.write\(dhYas638H\(dhYas638H\("([^"]+)"', data)[0]
                    dd = (decode_base64(link))
                    cc = (decode_base64(dd))
                    link2 = re.findall('document.write\(dhYas638H\(dhYas638H\("([^"]+)"', cc)[0]
                    ee = (decode_base64(link2))
                    ff = (decode_base64(ee))
                    url = re.search(r'iframe src="([^"]+)"', ff, re.IGNORECASE).group(1)
                    son_url = self.get_parsed_link(url)

                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'bspor' in url:
                try:
                    html = urlKap(url).result
                    url3 = re.findall('(http://whostreams.net/embed/[^"]+)"', html, re.IGNORECASE)[0]
                    html2 = urlKap(url3).result
                    packed = re.findall(">(eval\\(function.*?)\\n", html2, re.IGNORECASE)[0]
                    html4 = cPacker().unpack(packed)
                    son_url = re.findall('source:(?:| )"([^"]+)"', html4, re.IGNORECASE)[0] + '#User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0' + '&Referer=' + url3
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'swiftp' in url:
                try:
                    token = "http://163.172.181.152:8030/rbtv/token21.php"
                    html = urlKap(token).result
                    son_url = url + 'playlist.m3u8' + html
                except Exception as ex:
                    print ex

            if 'worldsport' in url:
                try:
                    try:
                        html = urlKap(url).result
                        urlmain = re.findall('(http://sport7.pw[^"]+)"', html, re.IGNORECASE)[0]
                        req = urllib2.Request(urlmain, None, {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0', 'Referer': urlmain})
                        response = urllib2.urlopen(req)
                        sHtmlContent = response.read()
                        Headers = response.headers
                        response.close()
                        c = Headers['Set-Cookie']
                        c2 = re.findall('(?:^|,) *([^;,]+?)=([^;,\/]+?);',c)
                        if c2:
                            cookies = ''
                            for cook in c2:
                                cookies = cookies + cook[0] + '=' + cook[1] + ';'
                        son_url = re.findall("videoLink = '([^']+)'", sHtmlContent, re.IGNORECASE)[0] + '#User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0' + '&Referer=' + url + '&Cookie=' + cookies
                    except:
                        html = urlKap(url).result
                        urlmain = re.findall('(https://hd24.watch/[^"]+)"', html, re.IGNORECASE)[0]
                        req = urllib2.Request(urlmain, None, {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0', 'Referer': urlmain})
                        response = urllib2.urlopen(req)
                        sHtmlContent = response.read()
                        Headers = response.headers
                        response.close()
                        c = Headers['Set-Cookie']
                        c2 = re.findall('(?:^|,) *([^;,]+?)=([^;,\/]+?);',c)
                        if c2:
                            cookies = ''
                            for cook in c2:
                                cookies = cookies + cook[0] + '=' + cook[1] + ';'
                        hostapi = "https://api.livesports24.online/gethost"
                        gethost = urlKap(hostapi).result
                        oynat = re.findall('data-channel="([^"]+)"', sHtmlContent, re.IGNORECASE)[0]
                        son_url = 'https://' + gethost + '/' + oynat + '.m3u8#User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0' + '&Referer=' + url + '&Cookie=' + cookies
                except Exception as ex:
                    print ex

            if 'anka.tv' in url:
                try:
                    urlmain = re.findall('(http://www.anka.tv/[^\/]+/)', url, re.IGNORECASE)[0]
                    urlframe = url.replace('channel', 'frame')
                    req = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0', 'Referer': urlmain})
                    response = urllib2.urlopen(req)
                    sHtmlContent = response.read()
                    Headers = response.headers
                    response.close()
                    c = Headers['Set-Cookie']
                    c2 = re.findall('(?:^|,) *([^;,]+?)=([^;,\/]+?);',c)
                    if c2:
                        cookies = ''
                        for cook in c2:
                            cookies = cookies + cook[0] + '=' + cook[1] + ';'
                    req = urllib2.Request(urlframe, None, {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0', 'Cookie': cookies, 'Referer': url})
                    response = urllib2.urlopen(req)
                    html = response.read()
                    Headers = response.headers
                    response.close()
                    son_url1 = re.findall('source src="([^"]+)"', html, re.IGNORECASE)[0] + '#User-Agent=Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0' + '&Referer=' + url + '&Cookie=' + cookies
                    if son_url1.startswith("/source"):
                        son_url1 = "http://www.anka.tv" + son_url1
                    son_url = son_url1.replace('&amp;','&')

                except Exception as ex:
                    print ex

            if 'izletv' in url or 'ozeltv' in url:
                try:
                    headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'}
                    req = urllib2.Request(url,None,headers)
                    response = urllib2.urlopen(req)
                    html = response.read()
                    response.close()
                    hash, id = re.findall('live\("([^"]+)","([^"]+)"\); }\);\s+</script>', html, re.IGNORECASE)[0]
                    data = urllib.urlencode({'hash': hash, 'id': id})
                    req = urllib2.Request(url, data, headers)
                    response = urllib2.urlopen(req)
                    link = response.read()
                    response.close()
                    link1 = link [::-1]
                    #link1 = link1.replace('_','=') + '=='
                    #first64, second64 = re.findall('(.*?=)(.*?==)', link1, re.IGNORECASE)[0]
                    def decode_base64(data):
                        missing_padding = len(data) % 4
                        if missing_padding != 0:
                            data += b'='* (4 - missing_padding)
                        return base64.decodestring(data)
                    #son_url1 = base64.b64decode(first64)+'?'+base64.b64decode(second64)
                    son_url1 = decode_base64(link1)
                    Header = '#User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
                    son_url = son_url1 + Header
                except Exception as ex:
                    print ex

            if '24video' in url:
                try:
                    media_id = re.findall('embedPlayer/([A-Za-z0-9]+)', url, re.IGNORECASE)[0]
                    weburl = 'http://24video.ws/video/xml/' + media_id + '?mode=play'
                    html = myrequest(weburl)
                    son_url = re.findall('video url=[\'|"](.*?)[\'|"]', html)[0]
                    url = 'http://24video.ws/embedPlayer' + media_id
                    son_url = son_url.replace('&amp;', '&') + '#Referer=' +url+ '&User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
                except Exception as ex:
                    print ex

            if 'bitporno' in url:
                try:
                    #url = url.replace('https', 'http')
                    html = urlKap(url).result
                    for match in re.finditer('"(http[^"]+)" type="[^"]+" data-res="([^"]+)"', html):
                        film_quality.append(match.group(2))
                        video_tulpe.append(match.group(1).replace('\\', ''))
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'canlitv.com' in url:
                try:
                    request = urllib2.Request(url, None, {'User-agent': 'User-Agent=Mozilla/5.0 (Linux; U; Android 2.2.1; en-us; Nexus One Build/FRG83) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                     'Connection': 'Close'})
                    response = urllib2.urlopen(request).read()
                    link = re.findall('file: "(.*?)"', response)
                    son_url1 = link[0]
                    if son_url1.startswith("//"):
                        son_url1 = "https:" + son_url1
                    son_url = son_url1

                except Exception as ex:
                    print ex

            if 'canlitvlive' in url:
                try:
                    url = url.replace('https', 'http')
                    html = myrequest(url)
                    stlink = re.findall('((?:web|www|tv).canlitvlive.(?:io|site)/tvizle.php\?t=[^"]+)"', html, re.IGNORECASE)[0]
                    stlink = 'http://' + stlink
                    request = urllib2.Request(stlink, None, {'User-agent': 'User-Agent=Mozilla/5.0 (Linux; U; Android 2.2.1; en-us; Nexus One Build/FRG83) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                     'Connection': 'Close'})
                    response = urllib2.urlopen(request).read()
                    link = re.findall('file(?: |):(?: |)"(.*?)"', response)
                    son_url1 = link[0]
                    if son_url1.startswith("//"):
                        son_url1 = "http:" + son_url1
                    Header = '#Referer='+url+'&User-Agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Mobile Safari/537.36'
                    son_url = son_url1 + Header
                except Exception as ex:
                    print ex

            if 'closeload' in url:
                try:
                    url = url.replace('https', 'http')
                    html = myrequest(url)
                    #packed = re.findall('(eval\\(function.*?)\\n', html, re.IGNORECASE)[0]
                    #html = cPacker().unpack(packed)
                    link = re.findall('<source src="([^"]+)" type="video/mp4">', html)
                    son_url = link[0] + "#Referer=%s" % url
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'daclips.in' in url:
                try:
                    request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                     'Connection': 'Close'})
                    response = urllib2.urlopen(request).read()
                    link = re.findall("(?:file|src): ['|\"](.*?)['|\"],", response)
                    son_url = link[0]
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'dailymotion.com' in url:
                url = url.replace('dailymotion.com/video/', 'dailymotion.com/embed/video/')
                try:
                    HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Referer': url}
                    page = urlKap(url, HTTP_HEADER).result
                    page = page.replace('\\', '')
                    v_tulpe1 = re.findall('"type":"video\/mp4","url":"(.*?x(\d+)\/video.*?mp4.*?)"', page)
                    if v_tulpe1:
                        for v, q in v_tulpe1:
                            video_tulpe.append(v)
                            film_quality.append(q + 'p mp4')
                    v_tulpe = re.findall('"(\d+)"\s*:.+?"url"\s*:\s*"([^"]+)', page)
                    if v_tulpe:
                        for q, v in v_tulpe:
                            video_tulpe.append(v)
                            film_quality.append(q + 'p m3u8')
                except Exception as ex:
                    print ex
                    error = True

            if 'datoporn' in url or 'dato.porn' in url:
                try:
                    url = url.replace('https', 'http')
                    html = myrequest(url)
                    packed = re.findall(">(eval\\(function.*?)\\n", html, re.IGNORECASE)[0]
                    html = cPacker().unpack(packed)
                    for match in re.finditer('file:"([^"]+(mp4|m3u8))"', html):
                        film_quality.append(match.group(2))
                        video_tulpe.append(match.group(1))
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'http://tiko' in url or 'https://tiko' in url or 'betit' in url:
                try:
                    def decode_base64(data):
                        missing_padding = len(data) % 4
                        if missing_padding != 0:
                            data += b'='* (4 - missing_padding)
                        return base64.decodestring(data)

                    headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.04',
                            'Referer': url }
                    try:
                        nurl = 'http://trvod.com/cf3/cf.php?search='+url
                        req = urllib2.Request(nurl, None, headers)
                        response = urllib2.urlopen(req)
                        data = response.read()
                        host = re.findall('//(.*?)/', url, re.IGNORECASE)[0]
                        link = re.findall('(canli-tv-bot/index.php[^"]+)"', data)[0]
                        url1 = 'http://trvod.com/cf3/cf.php?search=http://' + host + '/' + link
                        reff =  'http://' + host + '/' + link
                        req = urllib2.Request(url1, None, headers)
                        response = urllib2.urlopen(req)
                        data = response.read()
                        Header = 'Referer='+reff+'&User-Agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Mobile Safari/537.36'
                        try:
                            link = re.findall('atob\("([^"]+)"', data)[0]
                            dd = (decode_base64(link))
                            son_url = re.findall('source:"([^"]+)",watermark', dd)[0] + '#' + Header
                            son_url = son_url.replace('&amp;','&')
                        except:
                            son_url = re.findall('source:"([^"]+)",watermark', data)[0] + '#' + Header
                            son_url = son_url.replace('&amp;','&')
                    except:
                        req = urllib2.Request(nurl, None, headers)
                        response = urllib2.urlopen(req)
                        data = response.read()
                        link2 = re.findall('allowfullscreen class="embed-responsive-item" src="([^"]+)"', data)[0]
                        url2 = 'http://trvod.com/cf3/cf.php?search=http://' + host + '/' + link2
                        req = urllib2.Request(url2, None, headers)
                        response = urllib2.urlopen(req)
                        data = response.read()
                        Header = 'Referer='+reff+'&User-Agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Mobile Safari/537.36'
                        son_url = re.findall('source:"([^"]+)"', data)[0] + '#' + Header
                        son_url = son_url.replace('&amp;','&')
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'channel/watch/' in url:
                try:
                    headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.04',
                            'Referer': url }
                    req = urllib2.Request(url, None, headers)
                    response = urllib2.urlopen(req)
                    data = response.read()
                    Header = 'Referer='+url+'&User-Agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Mobile Safari/537.36'
                    try: 
                        link = re.findall("file: '(.*?m3u8[^']+)'", data)[0]
                        son_url = link + '#' + Header
                    except:
                        link = re.findall('atob\("([^"]+)"', data)[0]
                        dd = (base64.b64decode(link))
                        Header = 'Referer='+url+'&User-Agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Mobile Safari/537.36'
                        son_url = re.findall('source:"([^"]+)",watermark', dd)[0] + '#' + Header
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'marsb' in url:
                try:
                    headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.04',
                            'Referer': url }
                    req = urllib2.Request(url, None, headers)
                    response = urllib2.urlopen(req)
                    data = response.read()
                    link = re.findall("file: '([^']+)',\s+width", data)[0]
                    Header = 'Referer='+url+'&User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'
                    son_url = link + '#' + Header
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'docs.google.com' in url or 'drive.google.com' in url:
                try:
                    media_id = re.findall(r'https?://(?:(?:docs|drive)\.google\.com/(?:uc\?.*?id=|file/d/)|video\.google\.com/get_player\?.*?docid=)(?P<id>[a-zA-Z0-9_-]{20,40})', url, re.IGNORECASE)[0]
                    url = 'https://drive.google.com/file/d/%s/view' % media_id
                    req = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0', 'Referer': url})
                    response = urllib2.urlopen(req)
                    sHtmlContent = response.read()
                    Headers = response.headers
                    response.close()
                    c = Headers['Set-Cookie']
                    c2 = re.findall('(?:^|,) *([^;,]+?)=([^;,\/]+?);',c)
                    if c2:
                        cookies = ''
                        for cook in c2:
                            cookies = cookies + cook[0] + '=' + cook[1] + ';'
                    links_parts = re.findall('"fmt_stream_map","(.*?)"', sHtmlContent.decode('unicode-escape'))[0]
                    links_part = re.findall('\\|(.*?),', links_parts)
                    film_quality = []
                    for link_part in links_part:
                        if link_part.encode('utf_8').find('itag=18') > -1:
                            video_link = (link_part + "#User-Agent=" + FF_USER_AGENT + "&Referer=https://youtube.googleapis.com/" + "&Cookie=" + cookies).encode('utf_8')
                            video_tulpe.append(video_link)
                            film_quality.append('360p')
                        if link_part.encode('utf_8').find('itag=22') > -1:
                            video_link = (link_part + "#User-Agent=" + FF_USER_AGENT + "&Referer=https://youtube.googleapis.com/" + "&Cookie=" + cookies).encode('utf_8')
                            video_tulpe.append(video_link)
                            film_quality.append('720p')
                        if link_part.encode('utf_8').find('itag=37') > -1:
                            video_link = (link_part + "#User-Agent=" + FF_USER_AGENT + "&Referer=https://youtube.googleapis.com/" + "&Cookie=" + cookies).encode('utf_8')
                            video_tulpe.append(video_link)
                            film_quality.append('1080p')
                except Exception as ex:
                    print ex
                    error = True

            if 'easyvid' in url:
                try:
                    url = url.replace('https', 'http')
                    html = myrequest(url)
                    son_url = re.findall('"([^"]+mp4)"', html)[0]
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'estream' in url:
                try:
                    url = url.replace('https', 'http')
                    html = myrequest(url)
                    for match in re.finditer('"([^"]+)" type=\'video\/mp4\' label=\'\d+x(.*?)\'', html):
                        film_quality.append(match.group(2)+'p')
                        video_tulpe.append(match.group(1))
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'hqq.tv' in url or 'hqq.watch' in url or 'netu.tv' in url or 'waaw.tv' in url:
                try:

                    def tb(b_m3u8_2):
                        j = 0
                        s2 = ""
                        while j < len(b_m3u8_2):
                            s2 += "\\u0" + b_m3u8_2[j:(j + 3)]
                            j += 3

                        return s2.decode('unicode-escape').encode('ASCII', 'ignore')

                    ## loop2unobfuscated
                    def jswise(wise):
                        while True:
                            wise = re.search("var\s.+?\('([^']+)','([^']+)','([^']+)','([^']+)'\)", wise, re.DOTALL)
                            if not wise: break
                            ret = wise = js_wise(wise.groups())

                        return ret

                    ## js2python
                    def js_wise(wise):
                        w, i, s, e = wise

                        v0 = 0;
                        v1 = 0;
                        v2 = 0
                        v3 = [];
                        v4 = []

                        while True:
                            if v0 < 5:
                                v4.append(w[v0])
                            elif v0 < len(w):
                                v3.append(w[v0])
                            v0 += 1
                            if v1 < 5:
                                v4.append(i[v1])
                            elif v1 < len(i):
                                v3.append(i[v1])
                            v1 += 1
                            if v2 < 5:
                                v4.append(s[v2])
                            elif v2 < len(s):
                                v3.append(s[v2])
                            v2 += 1
                            if len(w) + len(i) + len(s) + len(e) == len(v3) + len(v4) + len(e): break

                        v5 = "".join(v3);
                        v6 = "".join(v4)
                        v1 = 0
                        v7 = []

                        for v0 in range(0, len(v3), 2):
                            v8 = -1
                            if ord(v6[v1]) % 2: v8 = 1
                            v7.append(chr(int(v5[v0:v0 + 2], 36) - v8))
                            v1 += 1
                            if v1 >= len(v4): v1 = 0

                        return "".join(v7)

                    media_id = re.findall('php\?vid=([0-9a-zA-Z/-]+)', url, re.IGNORECASE)[0]
                    headers = {'User-Agent': FF_USER_AGENT,
                               'Referer': 'https://waaw.tv/watch_video.php?v=%s&post=1' % media_id}
                    html = urlKap(url, headers).result

                    wise = re.search('''<script type=["']text/javascript["']>\s*;?(eval.*?)</script>''', html,
                                     re.DOTALL | re.I).groups()[0]
                    data_unwise = jswise(wise).replace("\\", "")
                    try:
                        at = re.search('at=(\w+)', data_unwise, re.I).groups()[0]
                    except:
                        at = ""
                    try:
                        http_referer = re.search('http_referer=(.*?)&', data_unwise, re.I).groups()[0]
                    except:
                        http_referer = ""
                    player_url = "http://hqq.watch/sec/player/embed_player.php?iss=&vid=%s&at=%s&autoplayed=yes&referer=on&http_referer=%s&pass=&embed_from=&need_captcha=0&hash_from=&secured=0" % (
                    media_id, at, http_referer)
                    headers.update({'Referer': url})
                    data_player = urlKap(player_url, headers).result
                    data_unescape = re.findall('document.write\(unescape\("([^"]+)"', data_player)
                    data = ""
                    for d in data_unescape:
                        data += urllib.unquote(d)

                    data_unwise_player = ""
                    wise = ""
                    wise = re.search('''<script type=["']text/javascript["']>\s*;?(eval.*?)</script>''', data_player,
                                     re.DOTALL | re.I)
                    if wise:
                        data_unwise_player = jswise(wise.group(1)).replace("\\", "")

                    try:
                        vars_data = re.search('/player/get_md5.php",\s*\{(.*?)\}', data, re.DOTALL | re.I).groups()[0]
                    except:
                        vars_data = ""
                    matches = re.findall('\s*([^:]+):\s*([^,]*)[,"]', vars_data)
                    params = {}
                    for key, value in matches:
                        if key == "adb":
                            params[key] = "0/"
                        elif '"' in value:
                            params[key] = value.replace('"', '')
                        else:
                            try:
                                value_var = re.search('var\s*%s\s*=\s*"([^"]+)"' % value, data, re.I).groups()[0]
                            except:
                                value_var = ""
                            if not value_var and data_unwise_player:
                                try:
                                    value_var = \
                                    re.search('var\s*%s\s*=\s*"([^"]+)"' % value, data_unwise_player, re.I).groups()[0]
                                except:
                                    value_var = ""
                            params[key] = value_var

                    data = urllib.urlencode(params)

                    headers.update({'X-Requested-With': 'XMLHttpRequest', 'Referer': player_url})
                    url = "http://hqq.watch/player/get_md5.php?"

                    req = urllib2.Request(url, data, headers)
                    response = urllib2.urlopen(req)
                    link = response.read()
                    response.close()

                    url_data = json.loads(link)

                    media_url = "https:" + tb(url_data["obf_link"].replace("#", "")) + ".mp4.m3u8"

                    if media_url:
                        del headers['X-Requested-With']
                        headers.update({'Origin': 'https://hqq.watch'})

                    def append_headers(headers):
                        return '|%s' % '&'.join(['%s=%s' % (key, urllib.quote_plus(headers[key])) for key in headers])

                    son_url = media_url + append_headers(headers)

                except:
                    print 'link alinamadi'
                    error = True

            if 'izlesene.com' in url:
                try:
                    request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                     'Connection': 'Close'})
                    response = urllib2.urlopen(request).read()
                    page = response.replace('\\', '').replace('%3A', ':').replace('%2F', '/').replace('%3F', '?').replace('%3D', '=').replace('%26', '&')
                    for match in re.finditer('value":"([^"]+)","source":"([^"]+)"', page):
					    video_tulpe.append(match.group(2))
					    film_quality.append(match.group(1))
                except Exception as ex:
                    print ex
                    error = True

            if 'liveonlinetv247' in url:
                try:
                    html = urlKap(url).result
                    ks = re.search('<script>(?:\s+|)(var [a-zA-Z]+ ?= ?"";[\s\S]*?)<\/script>', html, re.IGNORECASE).group(1)
                    js = ks.split(';')
                    charcodes = [int(val) for val in js[1].split('=')[-1].replace('[', '').replace(']', '').split(',')]
                    sub = int(''.join(char for char in js[2].split('-')[1] if char.isdigit()))
                    charcodes = [val-sub for val in charcodes]
                    srcs = ''.join(map(chr, charcodes))
                    video_url = re.search('"(http.*?m3u8[^"]+)"', srcs, re.IGNORECASE).group(1)
                    video_url = video_url + '#User-Agent=Mozilla/5.0 (Linux; Android 5.1.1; Nexus 5 Build/LMY48B; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/43.0.2357.65 Mobile Safari/537.36&Referer=' + url
                    son_url = video_url.replace('\\', '')
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'cricfree' in url:
                try:
                    html = urlKap(url).result
                    url2 = re.findall('src="(https?://cricfree.cc/watch/[^"]+)"', html, re.IGNORECASE)[0]
                    html2 = urlKap(url2).result
                    ks = re.search('<script>(var[\s\S]*?)<\/script>', html2, re.IGNORECASE).group(1)
                    js = ks.split(';')
                    js[1] = re.sub(',\s+]', ']', js[1])
                    js[1] = re.sub('\n', '', js[1])
                    charcodes = [int(re.sub('\D', '', base64.b64decode(val))) for val in js[1].split(' = ')[-1].replace('[', '').replace(']', '').split(',')]
                    sub = int(''.join(char for char in js[2].split('-')[1] if char.isdigit()))
                    charcodes = [val-sub for val in charcodes]
                    srcs = ''.join(map(chr, charcodes))
                    try: 
                        url3 = re.search("src='(https://whostreams.net/embed/[^']+)'", srcs, re.IGNORECASE).group(1)
                        headers = {'User-Agent': FF_USER_AGENT,
                                   'Referer': url2}
                        html3 = urlKap(url3, headers).result
                        packed = re.findall("(eval\\(function.*?)\\n", html3, re.IGNORECASE)[0]
                        html4 = cPacker().unpack(packed)
                        video_url = re.search('source:"(http.*?m3u8[^"]+)"', html4, re.IGNORECASE).group(1)
                        video_url = video_url + '#User-Agent=Mozilla/5.0 (Linux; Android 5.1.1; Nexus 5 Build/LMY48B; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/43.0.2357.65 Mobile Safari/537.36&Referer=' + url3
                        son_url = video_url.replace('\\', '')
                    except:
                        url3 = re.search("id='([^']+)'.*?embed.telerium.tv", srcs, re.IGNORECASE).group(1)
                        url3 = 'https://telerium.tv/embed/'+url3+'.html'
                        headers = {'User-Agent': FF_USER_AGENT,
                                   'Referer': url2}
                        html3 = urlKap(url3, headers).result
                        packed = re.findall("(eval\\(function.*?)\\n", html3, re.IGNORECASE)[0]
                        html4 = cPacker().unpack(packed)
                        atob_1, atob_2 = re.findall("url:.*?atob\(rSt\((.*?)\)\)(?:|\s)\+(?:|\s)atob\(rSt\((.*?)\)\)", html4, re.IGNORECASE)[0]
                        link_1 = re.findall(atob_1 + '="([^"]+)"', html4, re.IGNORECASE)[0][::-1]
                        link_2 = re.findall(atob_2 + '="([^"]+)"', html4, re.IGNORECASE)[0][::-1]
                        video_url = 'https:' + base64.b64decode(link_1) + base64.b64decode(link_2) + '#User-Agent=Mozilla/5.0 (Linux; Android 5.1.1; Nexus 5 Build/LMY48B; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/43.0.2357.65 Mobile Safari/537.36&Referer=' + url3
                        son_url = video_url.replace('\\', '')
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'tata.to' in url:
                try:
                    HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Referer': url}
                    html = urlKap(url, HTTP_HEADER).result
                    video_url = re.search('div class="tv-play" data-src="(https://.*?.skyfall.to/.*?)[\s|"]', html, re.IGNORECASE).group(1)
                    son_url = video_url.replace('embed.html?dvr=false&token', 'index.m3u8?token') + '#User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if '.m3u8' in url and not 'videotoken.tmgrup.com.tr' in url:
                error = None
                video_tulpe_tmp = []
                url_main = ''
                try:
                    page = urlKap(url).result
                    url_main = '/'.join(url.split('/')[:-1]) + '/'
                    film_quality = re.findall('BANDWIDTH=([0-9]+)', page)
                    if film_quality:
                        video_tulpe_tmp = re.findall('BANDWIDTH=.*\\s(.*)', page)
                        if len(video_tulpe_tmp) > 1:
                            if video_tulpe_tmp[0].find('http') > -1:
                                for tulpe in video_tulpe_tmp:
                                    video_tulpe.append(tulpe.replace('\r', ''))

                            else:
                                for tulpe in video_tulpe_tmp:
                                    video_tulpe.append(url_main + tulpe.replace('\r', ''))
                        else:
                            film_quality = []
                            son_url = url
                    else:
                        son_url = url
                except:
                    son_url = url

            if 'mail.ru' in url:
                try:
                    html = urlKap(url).result
                    metadataUrl = re.findall('(?:metadataUrl|metaUrl)":.*?(//my[^"]+)', html)
                    if metadataUrl:
                        nurl = 'https:%s?ver=0.2.123' % metadataUrl[0]
                        page = urlKap(nurl, output='kukili').result
                        video_key = re.findall('video_key[^;]+', page)
                        if video_key:
                            for match in re.finditer('url":"(//cdn[^"]+).+?(\\d+p)', page):
                                video_tulpe.append('http:' + match.group(1) + '#User-Agent=' + FF_USER_AGENT + '&Cookie=' + video_key[0])
                                film_quality.append(match.group(2))
                    else:
                        error = True
                except Exception as ex:
                    print ex
                    error = True

            if 'mystream' in url:
                try:
                    url = url.replace('https', 'http')
                    html = myrequest(url)
                    for match in re.finditer('src="([^"]+)" type="video/mp4" label="([^"]+)"', html):
                        film_quality.append(match.group(2))
                        video_tulpe.append(match.group(1))
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'ok.ru/videoembed' in url or 'odnoklassniki.ru' in url:
                try:
                    id1 = re.findall('https?://(?:www.)?(?:odnoklassniki|ok).ru/(?:videoembed/|dk\\?cmd=videoPlayerMetadata&mid=)(\\d+)', url)[0]
                    nurl = 'https://ok.ru/videoembed/' + id1
                    html = urlKap(nurl).result
                    data = re.findall('''data-options=['"]([^'^"]+?)['"]''', html)[0]
                    data = data.replace('\\', '').replace('&quot;', '').replace('u0026', '&')
                    hata = re.findall('error":"([^"]+)', data)
                    if hata:
                        error = True
                    else:
                        film_quality = re.findall('{name:(\\w+),url:.*?}', data)
                        video_tulpe = re.findall('{name:\\w+,url:(.*?),seekSchema', data)
                except:
                    error = True
                    print 'link alinamadi'

            if 'openload' in url or 'oload' in url:
                try:
                    def opendecode(code, parseInt, _0x59ce16, _1x4bfb36):

                        _0x1bf6e5 = ''
                        ke = []

                        for i in range(0, len(code[0:9*8]),8):
                            ke.append(int(code[i:i+8],16))

                        _0x439a49 = 0
                        _0x145894 = 0

                        while _0x439a49 < len(code[9*8:]):
                            _0x5eb93a = 64
                            _0x896767 = 0
                            _0x1a873b = 0
                            _0x3c9d8e = 0
                            while True:
                                if _0x439a49 + 1 >= len(code[9*8:]):
                                    _0x5eb93a = 143;

                                _0x3c9d8e = int(code[9*8+_0x439a49:9*8+_0x439a49+2], 16)
                                _0x439a49 +=2

                                if _0x1a873b < 6*5:
                                    _0x332549 = _0x3c9d8e & 63
                                    _0x896767 += _0x332549 << _0x1a873b
                                else:
                                    _0x332549 = _0x3c9d8e & 63
                                    _0x896767 += int(_0x332549 * math.pow(2, _0x1a873b))

                                _0x1a873b += 6
                                if not _0x3c9d8e >= _0x5eb93a: break

                            # _0x30725e = _0x896767 ^ ke[_0x145894 % 9] ^ _0x59ce16 ^ parseInt ^ _1x4bfb36
                            _0x30725e = _0x896767 ^ ke[_0x145894 % 9] ^ parseInt ^ _1x4bfb36
                            _0x2de433 = _0x5eb93a * 2 + 127

                            for i in range(4):
                                _0x3fa834 = chr(((_0x30725e & _0x2de433) >> (9*8/ 9)* i) - 1)
                                if _0x3fa834 != '$':
                                    _0x1bf6e5 += _0x3fa834
                                _0x2de433 = (_0x2de433 << (9*8/ 9))

                            _0x145894 += 1


                        videourl = "https://oload.tv/stream/%s?mime=true" % _0x1bf6e5
                        return videourl

                    url = url.replace("openload.co", "oload.tv").replace("openload.stream", "oload.tv")
                    HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Referer': url}
                    data = urlKap(url, HTTP_HEADER).result
                    try:
                         code = re.findall('<p style="" id="[^"]+">(.*?)</p>', data, re.DOTALL | re.MULTILINE)[0]
                         _0x59ce16 = eval(re.findall('_0x59ce16=([^;]+)', data, re.DOTALL | re.MULTILINE)[0].replace('parseInt', 'int'))
                         _1x4bfb36 = eval(re.findall('_1x4bfb36=([^;]+)', data, re.DOTALL | re.MULTILINE)[0].replace('parseInt', 'int'))
                         parseInt  = eval(re.findall('_0x30725e,(\(parseInt.*?)\),', data, re.DOTALL | re.MULTILINE)[0].replace('parseInt', 'int'))
                         videourl = opendecode(code, parseInt, _0x59ce16, _1x4bfb36)
                         dtext = videourl.replace('https', 'http')
                         headers = {'User-Agent': HTTP_HEADER['User-Agent']}
                         req = urllib2.Request(dtext, None, headers)
                         res = urllib2.urlopen(req)
                         videourl = res.geturl()
                         son_url = videourl + '?mime=true'

                    except :
                        try:
                            media_id = re.findall('(?:embed|f)/([0-9a-zA-Z-_]+)', url, re.IGNORECASE)[0]
                            API_BASE_URL = 'https://api.openload.co/1'
                            INFO_URL = API_BASE_URL + '/streaming/info'
                            GET_URL = API_BASE_URL + '/streaming/get?file={media_id}'

                            def get_json(url):
                                result = urlKap(url, None, {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36', 'Referer': url}).result
                                js_result = re.findall('"url":"(.*?)"', result, re.IGNORECASE)[0]
                                js_result = js_result.replace('\\', '')
                                return js_result

                            js_data = get_json(GET_URL.format(media_id=media_id))
                            son_url = js_data

                        except Exception as ex:
                            return ('Visit: https://openload.co/pair', [], [])

                except Exception as ex:
                    print ex
                    error = True

            if 'plus.google.com' in url:
                try:
                    request = urllib2.Request(url, None, HEADERS)
                    response = urllib2.urlopen(request).read()
                    response = response.replace('\\', '')
                    for match in re.finditer(r'\[\d+,(\d+),\d+,"([^"]+)"\]', response):
                        film_quality.append(match.group(1))
                        video_tulpe.append(match.group(2).replace('\\', '').replace('u003d', '='))
                except Exception as ex:
                    print ex
                    error = True

            if 'radio.de' in url:
                try:
                    page = myrequest(url)
                    if re.match('.*?"stream"', page, re.S):
                        pattern = re.compile('"stream":"(.*?)"')
                        stationStream = pattern.findall(page, re.S)
                        if stationStream:
                            film_quality = []
                            son_url = stationStream[0]
                except:
                    print 'link alinamadi'
                    error = True

            if 'rapidvideo' in url:
                try:
                    media_id = re.findall('rapidvideo.(?:org|com)/(?:\\?v=|e/|embed/)([A-z0-9]+)', url, re.IGNORECASE)[0]
                    web_url = 'https://www.rapidvideo.com/e/%s' % media_id
                    request = urllib2.Request(web_url, None, {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                     'Connection': 'Close'})
                    response = urllib2.urlopen(request).read()
                    if '&q=' in response:
                        for match in re.finditer(r'"(http.*?%s&q=([^"]+))"' % media_id, response):
					        request2 = urllib2.Request(match.group(1), None, {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3','Connection': 'Close'})
					        response2 = urllib2.urlopen(request2).read()
					        for match2 in re.finditer(r'source src="([^"]+)" type="video/mp4" title="([^"]+)"', response2):
					            film_quality.append(match2.group(2))
					            video_tulpe.append(match2.group(1).replace('\\', ''))
                    elif '"label":"' in response:
                        for match3 in re.finditer('"file":"(http[^"]+)","label":"([^"]+)"', response):
                            film_quality.append(match3.group(2))
                            video_tulpe.append(match3.group(1).replace('\\', ''))
                    else:
                        for match4 in re.finditer('src="(http[^"]+)" type="video/mp4"', response):
                            son_url = match4.group(1)

                except Exception as ex:
                    print ex
                    error = True

            if 'raptu' in url:
                try:
                    url = url.replace("raptu", "bitporno")
                    son_url = self.get_parsed_link(url)
                    #media_id = re.findall('raptu.com/(?:\?v\=|embed/|.+?\u=)?([0-9a-zA-Z]+)', url, re.IGNORECASE)[0]
                    #web_url = 'https://www.raptu.com/?v=%s' % media_id
                    #request = urllib2.Request(web_url, None, {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                    # 'Connection': 'Close'})
                    #gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars
                    #info = urllib2.urlopen(request, context=gcontext).read()
                    #response = urllib2.urlopen(request).read()
                    #response = response.replace('\\', '')
                    #for match in re.finditer(r'"file":"([^"]+)","label":"([^"]+)"', response):
                    #    film_quality.append(match.group(2))
                    #    video_tulpe.append(match.group(1).replace('\\', ''))

                except Exception as ex:
                    print ex
                    error = True

            if 'sonicstream' in url:
                try:
                    html = myrequest(url)
                    for match in re.finditer('secury=(.*?)&serverID=(.*?)&getChannel=(\d+)["|&]', html):
                        son_url = 'rtmp://'+ (match.group(2)) +'.futcast11.pro/edge/?' +(match.group(1)) +'/ch'+ (match.group(3))
                        #son_url = 'http://'+ (match.group(2)) +'.futcast11.pro:1935/edge/ch'+ (match.group(3))+'/playlist.m3u8'
                        #link = '"http://5.futcast11.pro:1935/edge/ch' + (match.group(3)) + '/playlist.m3u8":"Server 1", "http://6.futcast11.pro:1935/edge/ch' + (match.group(3)) + '/playlist.m3u8":"Server 2", "http://8.futcast11.pro:1935/edge/ch' + (match.group(3)) + '/playlist.m3u8":"Server 3",'
                    #for match in re.finditer('"(.*?)":"(.*?)",', link):
                        #film_quality.append(match.group(2))
                        #video_tulpe.append(match.group(1))
                except Exception as ex:
                    print ex

            if 'sportstream365' in url:
                try:
                    id = re.findall('http://sportstream365/(.*?)/', url, re.IGNORECASE)[0]
                    #tk = 'http://sportstream-365.com/LiveFeed/GetGame?id='+id+'&partner=24'####>>>>>>>http://sportstream365.com/js/iframe.js
                    #html = urlKap(tk, referer='http://www.sportstream-365.com/').result
                    #file = re.findall('true,"VI":"(.*?)"',html)[0]
                    #file = re.findall('.*?VI[\'"]*[:,]\s*[\'"]([^\'"]+)[\'"].*',html)[0]
                    #link = '"http://213.183.46.114/hls-live/xmlive/_definst_/' + id + '/' + id + '.m3u8":"Server 1", "http://93.189.62.10/edge0/xrecord/' + id + '/prog_index.m3u8":"Server 2", "http://93.189.57.254/edge0/xrecord/' + id + '/prog_index.m3u8":"Server 3", "http://91.192.80.210/edge0/xrecord/' + id + '/prog_index.m3u8":"Server 4",'
                    #for match in re.finditer('"(.*?)":"(.*?)",', link):
                    #    film_quality.append(match.group(2))
                    #    video_tulpe.append(match.group(1) + '#User-Agent=Mozilla/5.0 (Linux; Android 5.1.1; Nexus 5 Build/LMY48B; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/43.0.2357.65 Mobile Safari/537.36')
                    son_url = 'http://213.183.46.114/hls-live/xmlive/_definst_/' + id + '/' + id + '.m3u8?whence=1001' + '#User-Agent=Mozilla/5.0 (Linux; Android 5.1.1; Nexus 5 Build/LMY48B; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/43.0.2357.65 Mobile Safari/537.36'
                except Exception as ex:
                    print ex

            if 'startv.com' in url:
                try:
                    HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Referer': url}
                    html = urlKap(url, HTTP_HEADER).result
                    ol_id = re.search(r'"videoUrl": "([^"]+)"', html, re.IGNORECASE).group(1)
                    html1 = urlKap(ol_id, HTTP_HEADER).result
                    video_url = re.search(r'"hls":"([^"]+)"', html1, re.IGNORECASE).group(1)
                    son_url = video_url.replace('\\', '')
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'streamango' in url or 'streamcherry' in url:
                try:
                    def decode(encoded, code):

                        _0x59b81a = ""
                        k = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
                        k = k[::-1]

                        count = 0

                        for index in range(0, len(encoded) - 1):
                            while count <= len(encoded) - 1:
                                _0x4a2f3a = k.index(encoded[count])
                                count += 1
                                _0x29d5bf = k.index(encoded[count])
                                count += 1
                                _0x3b6833 = k.index(encoded[count])
                                count += 1
                                _0x426d70 = k.index(encoded[count])
                                count += 1

                                _0x2e4782 = ((_0x4a2f3a << 2) | (_0x29d5bf >> 4))
                                _0x2c0540 = (((_0x29d5bf & 15) << 4) | (_0x3b6833 >> 2))
                                _0x5a46ef = ((_0x3b6833 & 3) << 6) | _0x426d70
                                _0x2e4782 = _0x2e4782 ^ code

                                _0x59b81a = str(_0x59b81a) + chr(_0x2e4782)

                                if _0x3b6833 != 64:
                                    _0x59b81a = str(_0x59b81a) + chr(_0x2c0540)
                                if _0x3b6833 != 64:
                                    _0x59b81a = str(_0x59b81a) + chr(_0x5a46ef)

                        return _0x59b81a

                    HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Referer': url}
                    html = urlKap(url, HTTP_HEADER).result
                    video_urls = []

                    matches = re.findall("type:\"video/([^\"]+)\",src:d\('([^']+)',(.*?)\).+?height:(\d+)", html, re.DOTALL | re.MULTILINE)

                    for ext, encoded, code, quality in matches:

                        media_url = decode(encoded, int(code))

                        if not media_url.startswith("http"):
                            media_url = "http:" + media_url
                        video_urls.append(["%sp" % (quality), media_url])

                    video_urls.reverse()
                    for video_url in video_urls:

                        videourl = video_url[1].replace("@", "")
                        headers = HTTP_HEADER
                        req = urllib2.Request(videourl, None, headers)
                        res = urllib2.urlopen(req)
                        vid_url = res.geturl()
                        video_tulpe.append(vid_url)
                        film_quality.append(video_url[0])

                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'streamcloud' in url:
                try:
                    html = urlKap(url).result
                    postdata = {}
                    for i in re.finditer('<input.*?name="(.*?)".*?value="(.*?)">', html):
                        postdata[i.group(1)] = i.group(2).replace("download1", "download2")
                    keto = myrequest(url, postdata)
                    r = re.search('file: "(.+?)",', keto)
                    if r:
                        son_url = r.group(1)
                except Exception as ex:
                    print ex
                    error = True

            if 'thevideo.me' in url:
                try:
                    HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Referer': url}
                    media_id = re.findall('(?://|\.)thevideo\.me/(?:embed-|download/)?([0-9a-zA-Z]+)', url, re.IGNORECASE)[0]
                    web_url = 'https://thevideo.me/pair?file_code=%s&check' % media_id
                    html = urlKap(web_url, HTTP_HEADER).result
                    key = re.findall('"vt":"(.*?)"', html, re.IGNORECASE)[0]
                    html1 = urlKap(url, HTTP_HEADER).result
                    for match in re.finditer(r'"file":"(.*?)","label":"(\d+p)"', html1):
                        film_quality.append(match.group(2))
                        video_tulpe.append(match.group(1)+ '?direct=false&ua=1&vt=' + key)
                except Exception as ex:
                    return ('Visit: https://thevideo.me/pair', [], [])

            if 'trtarsiv' in url:
                try:
                    request = urllib2.Request(url, None, {'User-agent': 'User-Agent=Mozilla/5.0 (Linux; U; Android 2.2.1; en-us; Nexus One Build/FRG83) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                     'Connection': 'Close'})
                    response = urllib2.urlopen(request).read()
                    link = re.findall('"(.*?m3u8.*?)"', response)
                    son_url = link[0]
                except Exception as ex:
                    print ex

            if 'tune.pk' in url:
                try:
                    UAGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
                    url = url.replace('https', 'http').replace('http', 'https')
                    url = url.replace('https://tune.pk/player/embed_player.php?vid=', 'https://embed.tune.pk/play/')
                    request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                     'Connection': 'Close'})
                    page = urllib2.urlopen(request).read()
                    film_quality = re.findall('"label":(\\d+)', page)
                    vid_tulpe = re.findall('"file":"(.*?)","bitrate', page)
                    video_tulpe = [ vido.replace('\\/', '/')+ '#User-Agent=' + UAGENT for vido in vid_tulpe]
                except Exception as ex:
                    print ex

            if 'uptostream' in url:
                try:
                    html = urlKap(url).result
                    try:
                        for i in re.finditer('"src":"([^"]+)","type":"[^"]+","label":"([^"]+)"', html):
                            film_quality.append(i.group(2))
                            video_tulpe.append(i.group(1).replace('\\', ''))
                    except:
                        for i in re.finditer('source src=[\'|"](.*?)[\'|"].*?data-res=[\'|"](.*?)[\'|"]', html):
                            film_quality.append(i.group(2))
                            video_tulpe.append('http:' + i.group(1))
                except:
                    print 'link alinamadi'
                    error = True

            if 'userscloud' in url:
                try:
                    url = url.replace('https', 'http')
                    request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                     'Connection': 'Close'})
                    try:
					    page = urllib2.urlopen(request).read()
                    except httplib.IncompleteRead, e:
					    page = e.partial
                    video_url = re.findall('"(http[^"]+mp4)"', page)[0]
                    son_url = video_url
                except Exception as ex:
                    print ex

            if 'xsportv' in url or 'betestream' in url or 'queenbet' in url or 'betpark' in url:
                try:
                    html = urlKap(url).result
                    link = re.findall('(http(?:|s)://matchandbet.*?)"', html, re.IGNORECASE)[0]
                    url = url.replace('http://trvod.me/cf3/cf.php?search=','')
                    req = urllib2.Request(link, None, {'User-agent': 'Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) CriOS/30.0.1599.12 Mobile/11A465 Safari/8536.25 (3B92C18B-D9DE-4CB7-A02A-22FD2AF17C8F)', 'Referer': url})
                    response = urllib2.urlopen(req)
                    sHtmlContent = response.read()
                    Headers = response.headers
                    response.close()
                    son_url1 = re.findall("source = '(.*?)'", sHtmlContent, re.IGNORECASE)[0]
                    son_url = son_url1 + "#User-Agent=Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) CriOS/30.0.1599.12 Mobile/11A465 Safari/8536.25 (3B92C18B-D9DE-4CB7-A02A-22FD2AF17C8F)&Referer=" + link
                    if son_url.startswith("#"):
                        son_url = ''
                    else:
                        son_url = son_url
                except Exception as ex:
                    print ex

            if 'cccam' in url:
                try:
                    link1 = 'http://cccam-free.com/NEW/new0.php'
                    link2 = 'http://boss-cccam.com/Test.php'
                    link3 = 'http://cccam.ch/free/get.php'
                    link4 = 'http://cccamgenerators.com/generators/get.php'
                    link5 = 'http://www.cccam24.de/free24/get.php'

                    oscam_path = '/etc/tuxbox/config/oscam/oscam.server'
                    oscam_path2 = '/usr/keys/oscam.server'
                    cccam_path = '/etc/CCcam.cfg'
                    cccam_path2 = '/usr/keys/CCcam.cfg'

                    HTTP_HEADER1 = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Referer': link1}
                    HTTP_HEADER2 = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Referer': link2}
                    HTTP_HEADER3 = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Referer': link3}
                    HTTP_HEADER3 = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Referer': link4}
                    HTTP_HEADER3 = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Referer': link5}

                    try:
                        html = urlKap(link1, HTTP_HEADER1).result
                        server1, port1, user1, pasw1 = re.findall('>(?:\s+|)(?:c|C):\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)(?:\s+|)<', html, re.IGNORECASE)[0]
                    except:
                        server1 = ''
                        port1 = ''
                        user1 = ''
                        pasw1 = ''

                    try:
                        html = urlKap(link2, HTTP_HEADER2).result
                        server2, port2, user2, pasw2 = re.findall('>(?:c|C):\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)</strong>', html, re.IGNORECASE)[0]
                    except:
                        server2 = ''
                        port2 = ''
                        user2 = ''
                        pasw2 = ''
                    try:
                        html = urlKap(link3, HTTP_HEADER3).result
                        server3, port3, user3, pasw3 = re.findall('>(?:\s+|)(?:c|C):\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)(?:\s+|)<', html, re.IGNORECASE)[0]
                    except:
                        server3 = ''
                        port3 = ''
                        user3 = ''
                        pasw3 = ''
                    try:
                        html = urlKap(link4, HTTP_HEADER3).result
                        server4, port4, user4, pasw4 = re.findall('>(?:\s+|)(?:c|C):\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)(?:\s+|)<', html, re.IGNORECASE)[0]
                    except:
                        server4 = ''
                        port4 = ''
                        user4 = ''
                        pasw4 = ''
                    try:
                        html = urlKap(link5, HTTP_HEADER3).result
                        server5, port5, user5, pasw5 = re.findall('>(?:\s+|)(?:c|C):\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)(?:\s+|)<', html, re.IGNORECASE)[0]
                    except:
                        server5 = ''
                        port5 = ''
                        user5 = ''
                        pasw5 = ''

                    try:
                        oscam = open (oscam_path, 'w')
                        line = '[reader]\nlabel=TURKvod_server_1\nenable=1\nprotocol=cccam\ndevice=' + server1 + ',' + port1 + '\nuser=' + user1 + '\npassword=' + pasw1 +'\ncccversion=2.1.2\ngroup=1\ninactivitytimeout=1\nreconnecttimeout=30\nlb_weight=100\ncccmaxhops=10\nccckeepalive=1\ncccwantemu=0' + '\n\n[reader]\nlabel=TURKvod_server_2\nenable=1\nprotocol=cccam\ndevice=' + server2 + ',' + port2 + '\nuser=' + user2 + '\npassword=' + pasw2 +'\ncccversion=2.1.2\ngroup=1\ninactivitytimeout=1\nreconnecttimeout=30\nlb_weight=100\ncccmaxhops=10\nccckeepalive=1\ncccwantemu=0' + '\n\n[reader]\nlabel=TURKvod_server_3\nenable=1\nprotocol=cccam\ndevice=' + server3 + ',' + port3 + '\nuser=' + user3 + '\npassword=' + pasw3 +'\ncccversion=2.1.2\ngroup=1\ninactivitytimeout=1\nreconnecttimeout=30\nlb_weight=100\ncccmaxhops=10\nccckeepalive=1\ncccwantemu=0' + '\n\n[reader]\nlabel=TURKvod_server_4\nenable=1\nprotocol=cccam\ndevice=' + server4 + ',' + port4 + '\nuser=' + user4 + '\npassword=' + pasw4 +'\ncccversion=2.1.2\ngroup=1\ninactivitytimeout=1\nreconnecttimeout=30\nlb_weight=100\ncccmaxhops=10\nccckeepalive=1\ncccwantemu=0' + '\n\n[reader]\nlabel=TURKvod_server_5\nenable=1\nprotocol=cccam\ndevice=' + server5 + ',' + port5 + '\nuser=' + user5 + '\npassword=' + pasw5 +'\ncccversion=2.1.2\ngroup=1\ninactivitytimeout=1\nreconnecttimeout=30\nlb_weight=100\ncccmaxhops=10\nccckeepalive=1\ncccwantemu=0'
                        oscam.write(line)
                        oscam.close()
                    except:
                        pass
                    try:
                        oscam = open (oscam_path2, 'w')
                        line = '[reader]\nlabel=TURKvod_server_1\nenable=1\nprotocol=cccam\ndevice=' + server1 + ',' + port1 + '\nuser=' + user1 + '\npassword=' + pasw1 +'\ncccversion=2.1.2\ngroup=1\ninactivitytimeout=1\nreconnecttimeout=30\nlb_weight=100\ncccmaxhops=10\nccckeepalive=1\ncccwantemu=0' + '\n\n[reader]\nlabel=TURKvod_server_2\nenable=1\nprotocol=cccam\ndevice=' + server2 + ',' + port2 + '\nuser=' + user2 + '\npassword=' + pasw2 +'\ncccversion=2.1.2\ngroup=1\ninactivitytimeout=1\nreconnecttimeout=30\nlb_weight=100\ncccmaxhops=10\nccckeepalive=1\ncccwantemu=0' + '\n\n[reader]\nlabel=TURKvod_server_3\nenable=1\nprotocol=cccam\ndevice=' + server3 + ',' + port3 + '\nuser=' + user3 + '\npassword=' + pasw3 +'\ncccversion=2.1.2\ngroup=1\ninactivitytimeout=1\nreconnecttimeout=30\nlb_weight=100\ncccmaxhops=10\nccckeepalive=1\ncccwantemu=0' + '\n\n[reader]\nlabel=TURKvod_server_4\nenable=1\nprotocol=cccam\ndevice=' + server4 + ',' + port4 + '\nuser=' + user4 + '\npassword=' + pasw4 +'\ncccversion=2.1.2\ngroup=1\ninactivitytimeout=1\nreconnecttimeout=30\nlb_weight=100\ncccmaxhops=10\nccckeepalive=1\ncccwantemu=0' + '\n\n[reader]\nlabel=TURKvod_server_5\nenable=1\nprotocol=cccam\ndevice=' + server5 + ',' + port5 + '\nuser=' + user5 + '\npassword=' + pasw5 +'\ncccversion=2.1.2\ngroup=1\ninactivitytimeout=1\nreconnecttimeout=30\nlb_weight=100\ncccmaxhops=10\nccckeepalive=1\ncccwantemu=0'
                        oscam.write(line)
                        oscam.close()
                    except:
                        pass
                    try:
                        cccam = open (cccam_path, 'w')
                        line1 = 'C: ' + server1 + ' ' + port1 + ' ' + user1 + ' ' + pasw1 + '\nC: ' + server2 + ' ' + port2 + ' ' + user2 + ' ' + pasw2 + '\nC: ' + server3 + ' ' + port3 + ' ' + user3 + ' ' + pasw3 + '\nC: ' + server4 + ' ' + port4 + ' ' + user4 + ' ' + pasw4+ '\nC: ' + server5 + ' ' + port5 + ' ' + user5 + ' ' + pasw5 + '\n\n\nALLOW TELNETINFO: yes\nALLOW WEBINFO: yes\nWEBINFO LISTEN PORT : 16001\nSTATIC CW FILE : /usr/keys/constant.cw\nCAID PRIO FILE : /etc/CCcam.prio\nPROVIDERINFO FILE : /etc/CCcam.providers\nCHANNELINFO FILE : /etc/CCcam.channelinfo'
                        cccam.write(line1)
                        cccam.close()
                        son_url = line1
                    except:
                        pass
                    try:
                        cccam = open (cccam_path2, 'w')
                        line1 = 'C: ' + server1 + ' ' + port1 + ' ' + user1 + ' ' + pasw1 + '\nC: ' + server2 + ' ' + port2 + ' ' + user2 + ' ' + pasw2 + '\nC: ' + server3 + ' ' + port3 + ' ' + user3 + ' ' + pasw3 + '\nC: ' + server4 + ' ' + port4 + ' ' + user4 + ' ' + pasw4+ '\nC: ' + server5 + ' ' + port5 + ' ' + user5 + ' ' + pasw5 + '\n\n\nALLOW TELNETINFO: yes\nALLOW WEBINFO: yes\nWEBINFO LISTEN PORT : 16001\nSTATIC CW FILE : /usr/keys/constant.cw\nCAID PRIO FILE : /etc/CCcam.prio\nPROVIDERINFO FILE : /etc/CCcam.providers\nCHANNELINFO FILE : /etc/CCcam.channelinfo'
                        cccam.write(line1)
                        cccam.close()
                        son_url = line1
                    except:
                        pass
                except Exception as ex:
                    print ex

            if 'videotoken.tmgrup.com.tr' in url:
                try:
                    headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.04',
                            'Referer':'http://www.atv.com.tr/webtv/canli-yayin'}
                    req = urllib2.Request(url, None, headers)
                    response = urllib2.urlopen(req)
                    data = response.read()
                    match = re.findall('true,"Url":"(.+?)"', data, re.DOTALL | re.MULTILINE)
                    son_url = '**** '+match[0]
                    if match:
                    son_url = match[0]
                except:
                    print 'link alinamadi'
                    error = True

            if 'vidmoly' in url or 'venus/playm' in url or 'akar/playm' in url:
                try:
                    url = url.replace('https', 'http')
                    html = myrequest(url)
                    if re.search("type='text/javascript'>(eval\\(function.*?)\\n", html):
                        packed = re.findall("type='text/javascript'>(eval\\(function.*?)\\n", html, re.IGNORECASE)[0]
                        html = cPacker().unpack(packed)
                    for match in re.finditer('"(.*?(m3u8|mp4))"', html):
                        linko = match.group(1)
                        if linko.startswith("//"):
                            linko = "http:" + linko
                        film_quality.append(match.group(2))
                        video_tulpe.append(linko)

                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'vidoza' in url:
                try:
                    url = url.replace('https', 'http')
                    html = myrequest(url)
                    for match in re.finditer('src: ?["|\'](.*?)["|\'], type:.*?res:["|\'](.*?)["|\']', html):
                        film_quality.append(match.group(2))
                        video_tulpe.append(match.group(1))
                except Exception as ex:
                    print ex
                    error = True

            if 'vidto.me' in url:
                try:
                    link = myrequest(url)
                    ids = re.compile('<input type="hidden" name="id".*?value="(.*?)">').findall(link)[0]
                    fname = re.compile('<input type="hidden" name="fname".*?value="(.*?)">').findall(link)[0]
                    hash1 = re.compile('<input type="hidden" name="hash".*?value="(.*?)">').findall(link)[0]
                    postdata = {'op': 'download1',
                     'id': ids,
                     'fname': fname,
                     'hash': hash1,
                     'referer': '',
                     'imhuman': 'Proceed to video',
                     'usr_login': ''}
                    sleep_time = int(re.findall('>([0-9])</span> seconds<', link)[0])
                    time.sleep(sleep_time)
                    link = myrequest(url, postdata)
                    for match in re.finditer('file:"(.*?)",label:"(\d+p)"', link):
                        film_quality.append(match.group(2))
                        video_tulpe.append(match.group(1))
                except Exception as ex:
                    print ex
                    error = True

            if 'vidup' in url:
                try:
                    HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Referer': url}
                    html = urlKap(url, HTTP_HEADER).result
                    key = re.findall("var thief='(.*?)'", html, re.IGNORECASE)[0]
                    packed = urlKap('http://vidup.tv/jwv/' + key, HTTP_HEADER).result
                    authKey = re.findall(r"""\|([a-z0-9]{40}[a-z0-9]+?)\|""", packed, re.IGNORECASE)[0]
                    html1 = urlKap(url, HTTP_HEADER).result
                    for match in re.finditer(r'"file":"(.*?)","label":"(\d+p)"', html1):
                        film_quality.append(match.group(2))
                        video_tulpe.append(match.group(1)+ '?direct=false&ua=1&vt=' + authKey)
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'vidzi' in url:
                try:
                    html = myrequest(url)
                    if re.search("type='text/javascript'>(eval\\(function.*?)\\n", html):
                        packed = re.findall("type='text/javascript'>(eval\\(function.*?)\\n", html, re.IGNORECASE)[0]
                        html = cPacker().unpack(packed)
                    for match in re.finditer('file:?"([^"]+(m3u8|mp4))"', html):
                        film_quality.append(match.group(2).replace('v.mp', 'mp4'))
                        video_tulpe.append(match.group(1).replace('?embed=', ''))
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if 'vk.com' in url:
                url = url.replace('https', 'http').replace('http://www.', 'http://')
                query = url.split('?', 1)[-1]
                query = parse_qs(query)
                api_url = 'http://vk.com/al_video.php?act=show_inline&al=1&video=%s_%s' % (query['oid'][0], query['id'][0])
                html = myrequest(api_url)
                if 'mp4' in html :
                    html = re.sub('\\\\', '', html)
                    html = html.replace('https://', 'http://')
                    video_tulpe = re.findall('source src="(https?:[^"]+)" type="video/mp4"', html)
                    film_quality = re.findall('(\\d+).mp4\\?extra', html)
                if 'mp4' not in html :
                    vk_link = "http://trvod.me/vk_get.php?vk_link=https%3A%2F%2Fvk.com%2Fvideo"+query['oid'][0]+"_"+query['id'][0]
                    HTTP_HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Referer': vk_link}
                    html2 = urlKap(vk_link, HTTP_HEADER, timeout=40).result
                    for match in re.finditer('url=(http[^"]+)" class="[^"]+" data="([^"]+)"', html2):
                        film_quality.append(match.group(2))
                        video_tulpe.append(urllib2.unquote(match.group(1)))

            if 'vimeo.com' in url:
                try:
                    ids = re.findall('vimeo.com(?:/video)?/(\\d+)', url)[0]
                    url = 'http://player.vimeo.com/video/' + ids + '/config'
                    headers = {'Referer': 'https://vimeo.com/',
                               'Origin': 'https://vimeo.com'}
                    data = urlKap(url,headers).result
                    packed = re.findall('("progressive":\[{.+?}\]})', data, re.IGNORECASE)[0]
                    reg = re.findall(',"url":"(.+?)",.+?"quality":"(.+?)",', packed)
                    for src, quality in reg:
                        video_tulpe.append(src)
                        film_quality.append(quality)
                except:
                    error = True
                    print 'link alinamadi'

            if 'web.tv' in url:
                try:
                    request = urllib2.Request(url, None, {'User-agent': 'User-Agent=Mozilla/5.0 (Linux; U; Android 2.2.1; en-us; Nexus One Build/FRG83) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                     'Connection': 'Close'})
                    response = urllib2.urlopen(request).read()
                    link = re.findall('"src":"(.*?)"', response)
                    son_url = link[0]
                    son_url = son_url.replace('\\', '')
                except Exception as ex:
                    print ex

            if 'yourporn' in url:
                try:
                    request = urllib2.Request(url, None, {'User-agent': 'User-Agent=Mozilla/5.0 (Linux; U; Android 2.2.1; en-us; Nexus One Build/FRG83) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
                     'Connection': 'Close'})
                    response = urllib2.urlopen(request).read()
                    link = re.findall("src='([^']+mp4)'", response)
                    son_url1 = link[0]
                    if son_url1.startswith("//"):
                        son_url1 = "http:" + son_url1
                    son_url = son_url1
                except Exception as ex:
                    print ex

            if 'youtube' in url:
                gecerli_url = '^\n                 (\n                     (?:https?://)?                                       # http(s):// (optional)\n                     (?:youtu\\.be/|(?:\\w+\\.)?youtube(?:-nocookie)?\\.com/|\n                        tube\\.majestyc\\.net/)                             # the various hostnames, with wildcard subdomains\n                     (?:.*?\\#/)?                                          # handle anchor (#/) redirect urls\n                     (?!view_play_list|my_playlists|artist|playlist)      # ignore playlist URLs\n                     (?:                                                  # the various things that can precede the ID:\n                         (?:(?:v|embed|e)/)                               # v/ or embed/ or e/\n                         |(?:                                             # or the v= param in all its forms\n                             (?:watch(?:_popup)?(?:\\.php)?)?              # preceding watch(_popup|.php) or nothing (like /?v=xxxx)\n                             (?:\\?|\\#!?)                                  # the params delimiter ? or # or #!\n                             (?:.*?&)?                                    # any other preceding param (like /?s=tuff&v=xxxx)\n                             v=\n                         )\n                     )?                                                   # optional -> youtube.com/xxxx is OK\n                 )?                                                       # all until now is optional -> you can pass the naked ID\n                 ([0-9A-Za-z_-]+)                                         # here is it! the YouTube video ID\n                 (?(1).+)?                                                # if we found the ID, everything can follow\n                 $'
                mobj = re.match(gecerli_url, url, re.VERBOSE)
                video_id = mobj.group(2)
                try:
                    try:
                        html = urlKap(url).result
                        link = re.findall('"(http[^"]+m3u8)"', html, re.IGNORECASE)[0]
                        link = link.replace('\\','')
                        page = urlKap(link).result
                        url_main = '/'.join(link.split('/')[:-1]) + '/'
                        film_quality = re.findall('BANDWIDTH=([0-9]+)', page)
                        if film_quality:
                            video_tulpe_tmp = re.findall('BANDWIDTH=.*\\s(.*)', page)
                            if len(video_tulpe_tmp) > 1:
                                if video_tulpe_tmp[0].find('http') > -1:
                                    for tulpe in video_tulpe_tmp:
                                        video_tulpe.append(tulpe.replace('\r', ''))

                                else:
                                    for tulpe in video_tulpe_tmp:
                                        video_tulpe.append(url_main + tulpe.replace('\r', ''))
                            else:
                                film_quality = []
                                son_url = link
                        else:
                            son_url = link
                    except:
						pass
                    try:
                        answer = (urllib2.urlopen(urllib2.Request('http://www.saveitoffline.com/process/?url=https://www.youtube.com/watch?v=' + video_id +'&type=xml')).read())
                        for match in re.finditer('<label>((?:\s+|)\d+[^<]+)</label>\s+<url>([^<]+)</url>', answer):
                            film_quality.append(match.group(1))
                            video_tulpe.append(match.group(2))
                    except:
						pass
                    try:
                        if pfy:
                            url = 'https://www.youtube.com/watch?v=' + video_id
                            video = pafy.new(url).streams
                            for s in video:
                                video_tulpe.append(str(s.url))
                                film_quality.append(str(s.resolution + s.extension))
                        else:
                            found = False
                            for el in ['&el=embedded',
                             '&el=detailpage',
                             '&el=vevo',
                             '']:
                                info_url = 'http://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en' % (video_id, el)
                                try:
                                    infopage = myrequest(info_url)
                                    videoinfo = parse_qs(infopage)
                                    if ('url_encoded_fmt_stream_map' or 'fmt_url_map') in videoinfo:
                                        found = True
                                        break
                                except Exception as ex:
                                    print ex, 'YT ERROR 1'
                            if found:
                                fmt_value = {'18': '360p',
                                 '22': '720p',
                                 '37': '1080p',
                                 '84': '720p'}
                                if videoinfo.has_key('url_encoded_fmt_stream_map'):
                                    videos = videoinfo['url_encoded_fmt_stream_map'][0].split(',')
                                    for video in videos:
                                        if parse_qs(video)['itag'][0] in fmt_value.keys():
                                            film_quality.append('alternatif - ' + fmt_value[parse_qs(video)['itag'][0]])
                                            video_tulpe.append(parse_qs(video)['url'][0])
                    except Exception as ex:
                        print ex
                        error = True
                except Exception as ex:
                    print ex
                    error = True

            if 'youwatch' in url or 'chouhaa' in url:
                try:
                    headers = {'User-Agent': FF_USER_AGENT, 'Referer': url}
                    media_id = re.findall('(?://|\.)(?:youwatch.org|chouhaa.info|voodaith7e.com|youwatch.to)/(?:embed-|)([a-z0-9]+)', url, re.IGNORECASE)[0]
                    page_url = 'http://youwatch.org/embed-%s.html' % media_id
                    html = urlKap(page_url, headers).result
                    html1 = re.findall('<iframe\s+src\s*=\s*"([^"]+)', html, re.IGNORECASE)[0]
                    html2 = urlKap(html1, headers).result
                    for match in re.finditer('file:"([^"]+)",label:"(\d+)"', html2):
                        film_quality.append(match.group(2))
                        video_tulpe.append(match.group(1) + "#Referer=" + html1)
                except Exception as e:
                    print 'link alinamadi : ' + str(e)
                    error = True

            if error:
                return (error, video_tulpe, film_quality)
            elif film_quality:
                return (error, video_tulpe, film_quality)
            else:
                return son_url
        except Exception as ex:
            print ex
            print 'html_parser ERROR'