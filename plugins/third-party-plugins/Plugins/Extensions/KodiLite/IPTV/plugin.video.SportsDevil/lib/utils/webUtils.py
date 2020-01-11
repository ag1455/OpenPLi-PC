# -*- coding: utf-8 -*-

import os
import re
import urllib
import urlparse
import requests

import socket
import time
from cookielib import LWPCookieJar
from HTMLParser import HTMLParser
from fileUtils import fileExists, setFileContent, getFileContent

import lib.common

#------------------------------------------------------------------------------
socket.setdefaulttimeout(30)

#use ipv4 only
origGetAddrInfo = socket.getaddrinfo

def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
    return origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)

# replace the original socket.getaddrinfo by our version
socket.getaddrinfo = getAddrInfoWrapper


#------------------------------------------------------------------------------

'''
    REQUEST classes
'''

class BaseRequest(object):
    
    def __init__(self, cookie_file=None):
        self.cookie_file = cookie_file
        self.s = requests.Session()
        self.s.cookies = LWPCookieJar(self.cookie_file)
        if fileExists(self.cookie_file):
            self.s.cookies.load(ignore_discard=True)
        self.s.headers.update({'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'})
        self.s.headers.update({'Accept-Language' : 'en-US,en;q=0.8,de;q=0.6,es;q=0.4'})
        self.s.headers.update({'Upgrade-Insecure-Requests': '1'})
        

        self.url = ''
    
    # def save_cookies_lwp(self, cookiejar, filename):
    #     lwp_cookiejar = cookielib.LWPCookieJar()
    #     for c in cookiejar:
    #         args = dict(vars(c).items())
    #         args['rest'] = args['_rest']
    #         del args['_rest']
    #         c = cookielib.Cookie(**args)
    #         lwp_cookiejar.set_cookie(c)
    #     lwp_cookiejar.save(filename, ignore_discard=True)

    # def load_cookies_from_lwp(self, filename):
    #     lwp_cookiejar = cookielib.LWPCookieJar()
    #     try:
    #         lwp_cookiejar.load(filename, ignore_discard=True)
    #     except:
    #         pass
    #     return lwp_cookiejar
    
    def fixurl(self, url):
        #url is unicode (quoted or unquoted)
        try:
            #url is already quoted
            url = url.encode('ascii')
        except:
            #quote url if it is unicode
            parsed_link = urlparse.urlsplit(url)
            parsed_link = parsed_link._replace(netloc=parsed_link.netloc.encode('idna'),
                                               path=urllib.quote(parsed_link.path.encode('utf-8')),
                                               query=urllib.quote(parsed_link.query.encode('utf-8'),safe='+?=&'),
                                               fragment=urllib.quote(parsed_link.fragment.encode('utf-8')))
            url = parsed_link.geturl().encode('ascii')
        #url is str (quoted)
        return url
    
    #302 response redirect location
    def getLocation(self, url):
        r = self.s.get(url, allow_redirects=False, timeout=20)
        if 'Location' in r.headers:
             rloc = r.headers['Location']
        else:
            rloc = url        
        return rloc

    def getSource(self, url, form_data, referer, xml=False, mobile=False):
        url = self.fixurl(url)

        if not referer:
            referer = url
        else:
            referer = self.fixurl(referer.replace('wizhdsports.be','wizhdsports.is').replace('ibrod.tv','www.ibrod.tv').replace('livetv123.net','livetv.sx'))
        
        headers = {'Referer': referer}
        
        if 'liveonlinetv247' in urlparse.urlsplit(url).netloc: mobile = True

        if mobile:
            self.s.headers.update({'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1'})
            
        if xml:
            headers['X-Requested-With'] = 'XMLHttpRequest'
            
              
        if 'cndhlsstream.pw' in urlparse.urlsplit(url).netloc:
            del self.s.headers['Accept-Encoding']
        if 'skstream.tv' in urlparse.urlsplit(url).netloc:
            del self.s.headers['Accept-Encoding']
        if 'bstream.tech' in urlparse.urlsplit(url).netloc:
            del self.s.headers['Accept-Encoding']
        if 'bcast.site' in urlparse.urlsplit(url).netloc:
            del self.s.headers['Accept-Encoding']
        if 'bcast.pw' in urlparse.urlsplit(url).netloc:
            del self.s.headers['Accept-Encoding']
        if 'live247.online' in urlparse.urlsplit(url).netloc:
            del self.s.headers['Accept-Encoding']
        if 'indexstream.tv' in urlparse.urlsplit(url).netloc:
            del self.s.headers['Accept-Encoding']
        
        if 'streamlive.to' in urlparse.urlsplit(url).netloc:
            self.s.verify = False

        if 'vipleague' in url or 'strikeout' in url or 'homerun' or 'nbastreams' in url:
            self.s.verify = False
        
        if 'bypassed' in url or 'livecamtv' in url:
            self.s.verify = False

        if 'firstonetv' in url: 
            self.s.verify = False

        if 'vaughnlive.tv' in url:
            self.s.verify = False

        
        #if 'strikeout' in urlparse.urlsplit(url).netloc:
            #self.s.headers.update({'Upgrade-Insecure-Requests': '1'})
            #self.s.headers.update({'Host': 'zoomtv.me'})
            # self.s.headers.update({'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'})
            # self.s.headers.update({'Accept-Language' : 'en-US,en;q=0.8,de;q=0.6,es;q=0.4'})
            #self.s.headers.update({'Accept-Encoding': 'gzip, deflate'})
            #self.s.headers.update({'Connection' : 'keep-alive'})
            # self.s.headers.update({'Origin': 'http://www.strikeout.co'})
            # self.s.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
            
        

        if form_data:
            #zo**tv
            #if 'uagent' in form_data[0]:
               #form_data[0] = ('uagent',urllib.quote(self.s.headers['User-Agent']))
                #if len(form_data) > 4 and 'Cookie' in form_data[4]:
                    #headers['Cookie'] = form_data[4][1]
                    #del form_data[4]
                   
                #headers['Content-Type'] = 'application/x-www-form-urlencoded'
                #headers['User-Agent'] = self.s.headers['User-Agent']
                #lib.common.log("JairoX10:" + form_data[0][1])
            if 'firstonetv' in url and len(form_data) > 0:    
                # tmp_data = dict(form_data)
                # cookies = str(tmp_data['cookie'])
                # cookies = cookies.replace('___', ';')
                cookies = requests.utils.dict_from_cookiejar(self.s.cookies)
                evercookie = {'evercookie_cache': '', 'evercookie_etag': '', 'evercookie_png': '', 'f1tvuvid': ''}
                cookies.update(evercookie)
                cookiestr = "; ".join(["=".join([key, str(val)]) for key, val in cookies.items()])
                headers['cookie'] = cookiestr
                # tmp_data.pop('cookie')
                # form_data = tmp_data.items()

            r = self.s.post(url, headers=headers, data=form_data, timeout=20)
            
        else:
            try:
                r = self.s.get(url, headers=headers, timeout=20)
            except (requests.exceptions.MissingSchema):
                return 'pass'
        
        #many utf8 encodings are specified in HTTP body not headers and requests only checks headers, maybe use html5lib
        #https://github.com/kennethreitz/requests/issues/2086
        if 'streamlive.to' in urlparse.urlsplit(url).netloc \
        or 'sport365.live' in urlparse.urlsplit(url).netloc \
        or 'vipleague' in urlparse.urlsplit(url).netloc \
        or 'cinestrenostv.tv' in urlparse.urlsplit(url).netloc \
        or 'batmanstream.com' in urlparse.urlsplit(url).netloc \
        or 'sportcategory.com' in urlparse.urlsplit(url).netloc:
            r.encoding = 'utf-8'
        if 'lfootball.ws' in urlparse.urlsplit(url).netloc:
            r.encoding = 'windows-1251'
            
        response  = r.text

       

        if 'beget=begetok' in response: # av
            _cookie = requests.cookies.create_cookie('beget','begetok',domain=urlparse.urlsplit(url).netloc,path='/')
            self.s.cookies.set_cookie(_cookie)
            r = self.s.get(url, headers=headers, timeout=20)
            response  = r.text

        if 'fromCharCode,sucuri_cloudproxy_js' in response: # sebn
            from sucuri import sucuri_decode
            sucuri_name, sucuri_value = sucuri_decode(response)
            sucuri_cookie = requests.cookies.create_cookie(sucuri_name,sucuri_value,domain=urlparse.urlsplit(url).netloc,path='/',
                                                           discard=False,expires=(time.time() + 86400))
            self.s.cookies.set_cookie(sucuri_cookie)
            r = self.s.get(url, headers=headers, timeout=20)
            response  = r.text
        
        if len(response) > 10:
            self.s.cookies.save(ignore_discard=True)

        self.s.close()
        return HTMLParser().unescape(response)


#------------------------------------------------------------------------------

class DemystifiedWebRequest(BaseRequest):

    def __init__(self, cookiePath):
        super(DemystifiedWebRequest,self).__init__(cookiePath)

    def getSource(self, url, form_data, referer='', xml=False, mobile=False, demystify=False):
        data = super(DemystifiedWebRequest, self).getSource(url, form_data, referer, xml, mobile)
        if not data:
            return None

        if not demystify:
            # remove comments
            r = re.compile('<!--.*?(?!//)--!*>', re.IGNORECASE + re.DOTALL + re.MULTILINE)
            m = r.findall(data)
            if m:
                for comment in m:
                    data = data.replace(comment,'')
        else:
            import decryptionUtils as crypt
            data = crypt.doDemystify(data)

        return data

#------------------------------------------------------------------------------

class CachedWebRequest(DemystifiedWebRequest):

    def __init__(self, cookiePath, cachePath):
        super(CachedWebRequest,self).__init__(cookiePath)
        self.cachePath = cachePath
        self.cachedSourcePath = os.path.join(self.cachePath, 'page.html')
        self.currentUrlPath = os.path.join(self.cachePath, 'currenturl')
        self.lastUrlPath = os.path.join(self.cachePath, 'lasturl')

    def __setLastUrl(self, url):
        setFileContent(self.lastUrlPath, url)

    def __getCachedSource(self):
        try:
            data = getFileContent(self.cachedSourcePath)
        except:
            pass
        return data

    def getLastUrl(self):
        return getFileContent(self.lastUrlPath)
        

    def getSource(self, url, form_data, referer='', xml=False, mobile=False, ignoreCache=False, demystify=False):
        if 'tvone.xml' in url:
            self.cachedSourcePath = url
            data = self.__getCachedSource()
            return data
        if '.r.de.a2ip.ru' in url:
            parsed_link = urlparse.urlsplit(url)
            parsed_link = parsed_link._replace(netloc=parsed_link.netloc.replace('.r.de.a2ip.ru','').decode('rot13'))
            url = parsed_link.geturl()
        if 'calls/get/source' in url:
            ignoreCache = True
            
        if url == self.getLastUrl() and not ignoreCache:
            data = self.__getCachedSource()
        else:
            data = super(CachedWebRequest,self).getSource(url, form_data, referer, xml, mobile, demystify)
            if data:
                # Cache url
                self.__setLastUrl(url)
                # Cache page
                setFileContent(self.cachedSourcePath, data)
        return data
