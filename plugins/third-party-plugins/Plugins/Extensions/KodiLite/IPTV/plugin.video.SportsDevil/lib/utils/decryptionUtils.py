# -*- coding: utf-8 -*-
import pyDes
import urllib
import re
from regexUtils import parseTextToGroups
from javascriptUtils import JsFunctions, JsUnpacker, JsUnpackerV2, JsUnpacker95High, JsUnwiser, JsUnIonCube, JsUnFunc, JsUnPP, JsUnPush, JSUnfuck
from hivelogic import hivelogic
try: import json
except ImportError: import simplejson as json
try: from Crypto.Cipher import AES
except ImportError: import pyaes as AES
import lib.common

def encryptDES_ECB(data, key):
    data = data.encode()
    k = pyDes.des(key, pyDes.ECB, IV=None, pad=None, padmode=pyDes.PAD_PKCS5)
    d = k.encrypt(data)
    assert k.decrypt(d, padmode=pyDes.PAD_PKCS5) == data
    return d

def decryptDES_ECB(data, key):
    data = data.decode('base-64')
    k = pyDes.des(key, pyDes.ECB, IV=None, pad=None, padmode=pyDes.PAD_PKCS5)
    return k.decrypt(data, padmode=pyDes.PAD_PKCS5)

def gAesDec(data, key):
    from mycrypt import decrypt
    return decrypt(key,data)

def cjsAesDec(data, key):
    from mycrypt import decrypt
    enc_data = json.loads(data.decode('base-64'))
    ciphertext = 'Salted__' + enc_data['s'].decode('hex') + enc_data['ct'].decode('base-64')
    return json.loads(decrypt(key,ciphertext.encode('base-64')))

def m3u8AesDec(data, key):
    try:
        _in = data.split('.')
        unpad = lambda s : s[0:-ord(s[-1])]
        aes = AES.new(key.decode('hex'), AES.MODE_CBC, _in[1].decode('hex'))
        return unpad(aes.decrypt(_in[0].decode('hex')))
    except: return data
		
def drenchDec(data, key):
    from drench import blowfish
    return blowfish(key).decrypt(data)

def zadd(data):
    if re.search(".*\w+\s*=\s*eval\(\"\(\"\+\w+\+", data):
        
        jsvar = re.findall(".*\w+\s*=\s*eval\(\"\(\"\+(\w+)\+", data)[0]
        matches = re.findall(jsvar+'\s+\+=\s*(\w+)',data)
        jsall = ''
        try:
            firstword = matches[0]
            for match in matches:
                tmp = re.findall(match+'\s*=\s*[\'\"](.*?)[\"\'];',data)
                if len(tmp)>0:
                    jsall += tmp[0]
            #lib.common.log("JairoXZADD:" + data)
            tmp_ = re.sub(firstword+r".*eval\(\"\(\"\+\w+\+\"\)\"\);", jsall, data, count=1, flags=re.DOTALL)
            data = tmp_
        except:
            data = data
            pass

    return data

# def zadd2(data):
#     if re.search(".*\w+\s*=\s*eval\(\"\(\"\s*\+\s*\w+",data):
#         #jsvar = re.findall(".*\w+\s*=\s*eval\(\"\(\"\+(\w+)\+", data)[0]
#         matches = re.findall('\w+\s*=\s*\w+\s*\+\s*(\w+)',data)
#         jsall = ''
#         try:
#             firstword = matches[0]
#             for match in matches:
#                 tmp = re.findall(match+'\s*=\s*[\'\"](.*?)[\"\'];',data)
#                 if len(tmp)>0:
#                     jsall += tmp[0]
#             if re.compile(r"jwplayer\(\'\w+.*eval\(\"\(\"\s*\+\s*\w+\s*\+\s*\"\)\"\);", flags=re.DOTALL).findall(data):
#                  tmp_ = re.sub(r"jwplayer\(\'\w+.*eval\(\"\(\"\s*\+\s*\w+\s*\+\s*\"\)\"\);", jsall, data, count=1, flags=re.DOTALL)
#             if re.compile(r"\w+\.\w+\({.*}\s+</script>(.*)</script>", flags=re.DOTALL).findall(data):
#                 tmp_ = re.sub(r"\w+.\w+\({.*}\s+</script>(.*)</script>", jsall, data, count=1, flags=re.DOTALL)
#             data = tmp_
#         except:
#             data = data
#             pass

#     return data

def zadd2(data):
    #lib.common.log("JairoXZADD2:" + data)
    if re.search(r".*\w+\s*=\s*eval\(\"\(\"\s*\+\s*\w+",data):
        #jsvar = re.findall(".*\w+\s*=\s*eval\(\"\(\"\+(\w+)\+", data)[0]
        matches = re.findall(r'\w+\s*=\s*\w+\s*\+\s*(\w+)',data)
        if len(matches)==0:
            matches = re.findall(r'\w+\s*=\s*\w+\s*\+\s*\'\'\s*\+\s*(\w+);',data)
        jsall = ''
        try:
            firstword = matches[0]
            for match in matches:
                tmp = re.findall(r"[;,]\s*(\w+)\s*=\s*'(.*?)'\s*[;,]\s*%s\s*=\s*(\1)"%match,data)
                if len(tmp)==0:
                    tmp = re.findall(r";(%s)\s*=\s*'(.*?)';"%match,data)
                if len(tmp)>0:
                    jsall += tmp[0][1]
            
            if re.compile(r"(jwplayer\(['\"]\w+.*?\}\);).*?eval\(\"\(\"", flags=re.DOTALL).findall(data):
                tmp_ = re.sub(r"(jwplayer\(['\"]\w+.*?\}\);).*?eval\(\"\(\"", '\\1'+jsall, data, count=1, flags=re.DOTALL)
            elif re.compile(r"\w+\.\w+\({.*}\s+</script>(.*)</script>", flags=re.DOTALL).findall(data):
                tmp_ = re.sub(r"\w+.\w+\({.*}\s+</script>(.*)</script>", jsall, data, count=1, flags=re.DOTALL)
            elif re.search(r'player.attach.*?<\/script>', data, re.DOTALL) != None:
                tmp_ = re.sub(r'player.attach.*?<\/script>', jsall, data, count=1, flags=re.DOTALL)
            else: tmp_ = None
            
            if not tmp_ is None: data = tmp_
        except:
            data = data
            pass

    return data


def zdecode(data):
    import csv

    csv.register_dialect('js', delimiter=',', quotechar="'", escapechar='\\')

    keys_regex = r'''eval\(.*?function\(([^\)]+)\){'''
    keys = [re.search(keys_regex, data).groups()[0]]

    values_regex = r'''.*(\w+)\s*=\s*\w+\((.*?)\);\s*eval\(\1'''
    values = [re.search(values_regex, data, re.DOTALL).groups()[1].replace('\n','')]

    key_list = [l for l in csv.reader(keys, dialect='js')][0]
    value_list = [l for l in csv.reader(values, dialect='js')][0]

    dictionary = dict(zip(key_list, value_list))

    symtab_regex = r'''\w+\[\w+\]=(\w+)\[\w+\]\|\|\w+'''
    sym_key = re.search(symtab_regex, data).groups()[0]
    symtab = dictionary[sym_key]

    split_regex = r'''(.*)\.split\('(.*)'\)'''
    _symtab, _splitter = re.search(split_regex, symtab).groups()
    splitter = re.sub(r"""'\s*\+\s*'""", '', _splitter)
    symtab = _symtab.split(splitter)

    tab_regex = r'''(\w+)=\1\.replace'''
    tab_key = re.search(tab_regex, data).groups()[0]
    tab = dictionary[tab_key]

    def lookup(match):
        return symtab[int(match.group(0))] or str(match.group(0))

    return re.sub(ur'\w+', lookup, tab)
    
def wdecode(data):
    from itertools import chain
    
    in_data = re.split('\W+',data)
    pos = in_data.index(max(in_data,key=len))
    codec = "".join(chain(*zip(in_data[pos][:5], in_data[pos+1][:5], in_data[pos+2][:5])))
    data = "".join(chain(*zip(in_data[pos][5:], in_data[pos+1][5:], in_data[pos+2][5:])))
    
    ring = 0
    res = []
    for i in xrange(0,len(data),2):
        modifier = -1
        if (ord(codec[ring]) % 2):
            modifier = 1
        res.append( chr( int(data[i:i+2],36) - modifier ) )
        
        ring = ring + 1
        if ring >= len(codec):
            ring = 0
    return ''.join(res)

def onetv(playpath):
    import random,time,md5
    from base64 import b64encode
    user_agent = 'Mozilla%2F5.0%20%28Linux%3B%20Android%205.1.1%3B%20Nexus%205%20Build%2FLMY48B%3B%20wv%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Version%2F4.0%20Chrome%2F43.0.2357.65%20Mobile%20Safari%2F537.36'
    token = "65rSw"+"UzRad"
    servers = ['185.152.66.39', '185.102.219.72', '185.59.221.109', '185.152.64.236', '185.59.222.232', '185.102.219.67', '185.102.218.56']
    time_stamp = str(int(time.time()) + 14400)
    to_hash = "{0}{1}/hls/{2}".format(token,time_stamp,playpath)
    out_hash = b64encode(md5.new(to_hash).digest()).replace("+", "-").replace("/", "_").replace("=", "")
    server = random.choice(servers)
    
    url = "hls://http://{0}/p2p/{1}?st={2}&e={3}".format(server,playpath,out_hash,time_stamp)
    return '{url}|User-Agent={user_agent}&referer={referer}'.format(url=url,user_agent=user_agent,referer='6d6f6264726f2e6d65'.decode('hex'))
    

def encryptJimey(data):
    result = encryptDES_ECB(data,"PASSWORD").encode('base64').replace('/','').strip()
    return result

# used by 24cast
def destreamer(s):
    #remove all but[0-9A-Z]
    string = re.sub("[^0-9A-Z]", "", s.upper())
    result = ""
    nextchar = ""
    for i in range(0,len(string)-1):
        nextchar += string[i]
        if len(nextchar) == 2:
            result += ntos(int(nextchar,16))
            nextchar = ""
    return result

def ntos(n):
    n = hex(n)[2:]
    if len(n) == 1:
        n = "0" + n
    n = "%" + n
    return urllib.unquote(n)


def decryptSaurus(data):
    #lib.common.log("JairoX3:" + data)
    aeskeys = [ '5e4542404f4c757e4431675f373837385649313133356f3152693935366e4361',
                    '5e5858405046757e4631775f33414141514e3133393973315775336c34695a5a',
                    '5e4d58405044757e73314a5f39373837514e313335396a3144793833366e527a'
              ]
    r = re.compile(r":(\"(?!http)\w+\.\w+\.m3u8\")")
    r2 = re.compile(r"((?!http)\w+\.\w+\.m3u8)")
    gs = r.findall(data) or r2.findall(data)
    if gs:
        for g in gs:
            for aeskey in aeskeys:
                if re.match(r"{.*:.*}", g):
                   _in = json.loads(g).split('.')
                else:
                   _in = g.split('.')
                aes = AES.new(aeskey.decode('hex'), AES.MODE_CBC, _in[1].decode('hex'))            
                unpad = lambda s : s[0:-ord(s[-1])]
                try:
                    _url = unpad(aes.decrypt(_in[0].decode('hex')))
                except:
                    _url = None
                if _url and re.match(r'http://.*m3u8', _url):
                    try:
                        if re.match(r"{.*:.*}", data):
                           data = data.replace(g,json.dumps( _url ))
                        else:
                           data = _url
                        break
                    except:
                        continue
    else:            
        r = re.compile(r":(\"(?!http)[\w=\\/\+]+\.m3u8\")")
        gs = r.findall(data)
        if gs:
            for g in gs:
                data = data.replace(g,json.dumps(decryptDES_ECB(json.loads(g)[:-5], '5333637233742600'.decode('hex'))))

    return data

def unFuckFirst(data):
    try:
        #lib.common.log("JairoDemyst: " + data)
        p = 186
        hiro = re.findall(r'"hiro":"(.*?)"', data)[0]
        parts = re.findall('([^;]+)', hiro)
        for part in parts:
            if '(' in part:
                f = re.findall('(.*?)\((.+)\)',part)[0]
                exec(f[0] + JSUnfuck(f[1]).decode())
            else:
                exec(part)
        if isinstance(n, long):
            data = re.sub(r'"hiro":"(.*?)"', '"hiro":%s'%str(n), data, count=1)

        return data
    except:
        return data

def doDemystify(data):
    from base64 import b64decode
    escape_again=False
    #lib.common.log("JairoDemyst:" + data)
    #init jsFunctions and jsUnpacker
    jsF = JsFunctions()
    jsU = JsUnpacker()
    jsU2 = JsUnpackerV2()
    jsUW = JsUnwiser()
    jsUI = JsUnIonCube()
    jsUF = JsUnFunc()
    jsUP = JsUnPP()
    jsU95 = JsUnpacker95High()
    JsPush = JsUnPush()
    JsHive = hivelogic()

    # replace NUL
    #data = data.replace('\0','')


    # unescape
    r = re.compile('a1=["\'](%3C(?=[^\'"]*%\w\w)[^\'"]+)["\']')
    while r.findall(data):
        for g in r.findall(data):
            quoted=g
            data = data.replace(quoted, urllib.unquote_plus(quoted))
    
    
    r = re.compile('unescape\(\s*["\']((?=[^\'"]*%\w\w)[^\'"]+)["\']')
    while r.findall(data):
        for g in r.findall(data):
            quoted=g
            data = data.replace(quoted, urllib.unquote_plus(quoted))
            
    r = re.compile("""('%[\w%]{100,130}')""")
    while r.findall(data):
        for g in r.findall(data):
            quoted=g
            data = data.replace(quoted, "unescape({0})".format(urllib.unquote_plus(quoted)))
    
    r = re.compile('unescape\(\s*["\']((?=[^\'"]*\\u00)[^\'"]+)["\']')
    while r.findall(data):
        for g in r.findall(data):
            quoted=g
            data = data.replace(quoted, quoted.decode('unicode-escape'))

    r = re.compile('(\'\+dec\("\w+"\)\+\')')
    while r.findall(data):
        for g in r.findall(data):
            r2 = re.compile('dec\("(\w+)"\)')
            for dec_data in r2.findall(g):
                res = ''
                for i in dec_data:
                    res = res + chr(ord(i) ^ 123)
            data = data.replace(g, res)

    #sebn
    #(?:file\s*:|source\s*:|src\s*:|\w+=)\s*(window\.atob\(['"][^'"]+['"]\))
    #"""(?:file:|source:|\w+=)\s*(window\.atob\(['"][^'"]+['"]\))"""
    r = re.compile('(?:file\s*:|source\s*:|src\s*:|\w+\s*=)\s*(window\.atob\([\'"][^\'"]+[\'"]\))')
    #lib.common.log("JairoXDecrypt: " + data)
    if r.findall(data):
        for g in r.findall(data):
            #r"""window\.atob\(['"]([^'"]+)['"]\)"""
            r2 = re.compile('window\.atob\([\'"]([^\'"]+)[\'"]\)')
            for base64_data in r2.findall(g):
                data = data.replace(g, '"'+urllib.unquote(base64_data.decode('base-64')+'"'))

    #r = re.compile('((?:eval\(decodeURIComponent\(|window\.)atob\([\'"][^\'"]+[\'"]\)+)')
    #while r.findall(data):
        #for g in r.findall(data):
            #r2 = re.compile('(?:eval\(decodeURIComponent\(|window\.)atob\([\'"]([^\'"]+)[\'"]\)+')
            #for base64_data in r2.findall(g):
                #data = data.replace(g, urllib.unquote(base64_data.decode('base-64')))
                
    #jairox: ustreamix -- Obfuscator HTML : https://github.com/BlueEyesHF/Obfuscator-HTML
    r = re.compile(r"var\s*(\w+)\s*=\s*\[([A-Za-z0-9+=\/\",\s]+)\];\s*\1\.forEach.*-\s*(\d+)")
    if r.findall(data):
        try:
            matches = re.compile(r"var\s*(\w+)\s*=\s*\[([A-Za-z0-9+=\/\",\s]+)\];\s*\1\.forEach.*-\s*(\d+)").findall(data)
            chunks = matches[0][1].split(',')
            op = int(matches[0][2])
            dec_data = r""
            for chunk in chunks:
                try:
                    tmp = chunk.replace('"','')
                    tmp = str(b64decode(tmp))
                    dig = int(re.sub('[\D\s\n]','',tmp))
                    dig = dig - op
                    dec_data += chr(dig)
                except:
                    pass
            data = re.sub(r"(?s)<script>\s*var\s*\w+\s*=.*?var\s*(\w+)\s*=\s*\[.*<\/script>[\"']?", dec_data, data)

        except:
            pass
    
    r = re.compile('(<script.*?str=\'@.*?str.replace)')
    while r.findall(data):
        for g in r.findall(data):
            r2 = re.compile('.*?str=\'([^\']+)')
            for escape_data in r2.findall(g):
                data = data.replace(g, urllib.unquote(escape_data.replace('@','%')))
       
    r = re.compile('(base\([\'"]*[^\'"\)]+[\'"]*\))')
    while r.findall(data):
        for g in r.findall(data):
            r2 = re.compile('base\([\'"]*([^\'"\)]+)[\'"]*\)')
            for base64_data in r2.findall(g):
                data = data.replace(g, urllib.unquote(base64_data.decode('base-64')))
                escape_again=True
    
    if not 'sawlive' in data:
        r = re.compile('\?i=([^&]+)&r=([^&\'"]+)')
        for g in r.findall(data):
            print g
            try:
                _a, _b =  g[0].split('%2F')
                _res = (_a+'=').decode('base-64')+'?'+_b.decode('base-64')
                data = data.replace(g[0], _res)
                data = data.replace(g[1], urllib.unquote(g[1]).decode('base-64'))
            except:
                pass

    if 'var enkripsi' in data:
        r = re.compile(r"""enkripsi="([^"]+)""")
        gs = r.findall(data)
        if gs:
            for g in gs:
                s=''
                for i in g:
                    s+= chr(ord(i)^2)
                data = data.replace("""enkripsi=\""""+g, urllib.unquote(s))

    if """.replace(""" in data:
        r = re.compile(r""".replace\(["'](...[^"']+)["'],\s*["']([^"']*)["']\)""")
        gs = r.findall(data)
        if gs:
            for g in gs:
                if '\\' in g[0]:
                    data = data.replace(g[0].lower(),g[1])
                data = data.replace(g[0],g[1])
        r = re.compile(r""".replace\(["'](...[^"']+)["'],\s*["']([^"']*)["']\)""")
        gs = r.findall(data)
        if gs:
            for g in gs:
                if '\\' in g[0]:
                    data = data.replace(g[0].lower(),g[1])
                data = data.replace(g[0],g[1])

    # 24cast
    if 'destreamer(' in data:
        r = re.compile("destreamer\(\"(.+?)\"\)")
        gs = r.findall(data)
        if gs:
            for g in gs:
                data = data.replace(g, destreamer(g))

    # JS P,A,C,K,E,D
    if jsU95.containsPacked(data):
        data = jsU95.unpackAll(data)
        escape_again=True
        
    if jsU2.containsPacked(data):
        data = jsU2.unpackAll(data)
        escape_again=True
    
    if jsU.containsPacked(data):
        data = jsU.unpackAll(data)
        escape_again=True

    # JS W,I,S,E
    if jsUW.containsWise(data):
        data = jsUW.unwiseAll(data)
        escape_again=True

    # JS IonCube
    if jsUI.containsIon(data):
        data = jsUI.unIonALL(data)
        escape_again=True
        
    # Js unFunc
    if jsUF.cointainUnFunc(data):
        data = jsUF.unFuncALL(data)
        escape_again=True
    
    if jsUP.containUnPP(data):
        data = jsUP.UnPPAll(data)
        escape_again=True
        
    if JsPush.containUnPush(data):
        data = JsPush.UnPush(data)

    if JsHive.contains_hivelogic(data):
        data = JsHive.unpack_hivelogic(data)
    
    if re.search(r'hiro":".*?[\(\)\[\]\!\+]+', data) != None:
        data = unFuckFirst(data)
        #lib.common.log("JairoDemyst: " + data)
    
    if re.search(r"zoomtv", data, re.IGNORECASE) != None:
        #lib.common.log("JairoZoom:" + data)
        data = zadd(data)
        data = zadd2(data)
        try: 
            data = zdecode(data)
            escape_again=True
        except: pass
    # unescape again
    if escape_again:
        data = doDemystify(data)
    return data

#def doDemystify(data):
#    escape_again=False
    
#    #init jsFunctions and jsUnpacker
#    jsF = JsFunctions()
#    jsU = JsUnpacker()
#    jsU2 = JsUnpackerV2()
#    jsUW = JsUnwiser()
#    jsUI = JsUnIonCube()
#    jsUF = JsUnFunc()
#    jsUP = JsUnPP()
#    jsU95 = JsUnpacker95High()
#    JsPush = JsUnPush()
#    JsHive = hivelogic()

#    # replace NUL
#    #data = data.replace('\0','')


#    # unescape
#    r = re.compile('a1=["\'](%3C(?=[^\'"]*%\w\w)[^\'"]+)["\']')
#    while r.findall(data):
#        for g in r.findall(data):
#            quoted=g
#            data = data.replace(quoted, urllib.unquote_plus(quoted))
    
    
#    r = re.compile('unescape\(\s*["\']((?=[^\'"]*%\w\w)[^\'"]+)["\']')
#    while r.findall(data):
#        for g in r.findall(data):
#            quoted=g
#            data = data.replace(quoted, urllib.unquote_plus(quoted))
            
#    r = re.compile("""('%[\w%]{100,130}')""")
#    while r.findall(data):
#        for g in r.findall(data):
#            quoted=g
#            data = data.replace(quoted, "unescape({0})".format(urllib.unquote_plus(quoted)))
    
#    r = re.compile('unescape\(\s*["\']((?=[^\'"]*\\u00)[^\'"]+)["\']')
#    while r.findall(data):
#        for g in r.findall(data):
#            quoted=g
#            data = data.replace(quoted, quoted.decode('unicode-escape'))

#    r = re.compile('(\'\+dec\("\w+"\)\+\')')
#    while r.findall(data):
#        for g in r.findall(data):
#            r2 = re.compile('dec\("(\w+)"\)')
#            for dec_data in r2.findall(g):
#                res = ''
#                for i in dec_data:
#                    res = res + chr(ord(i) ^ 123)
#            data = data.replace(g, res)
            
#    r = re.compile('((?:eval\(decodeURIComponent\(|window\.)atob\([\'"][^\'"]+[\'"]\)+)')
#    while r.findall(data):
#        for g in r.findall(data):
#            r2 = re.compile('(?:eval\(decodeURIComponent\(|window\.)atob\([\'"]([^\'"]+)[\'"]\)+')
#            for base64_data in r2.findall(g):
#                data = data.replace(g, urllib.unquote(base64_data.decode('base-64')))
                
#    r = re.compile('(<script.*?str=\'@.*?str.replace)')
#    while r.findall(data):
#        for g in r.findall(data):
#            r2 = re.compile('.*?str=\'([^\']+)')
#            for escape_data in r2.findall(g):
#                data = data.replace(g, urllib.unquote(escape_data.replace('@','%')))
       
#    r = re.compile('(base\([\'"]*[^\'"\)]+[\'"]*\))')
#    while r.findall(data):
#        for g in r.findall(data):
#            r2 = re.compile('base\([\'"]*([^\'"\)]+)[\'"]*\)')
#            for base64_data in r2.findall(g):
#                data = data.replace(g, urllib.unquote(base64_data.decode('base-64')))
#                escape_again=True
    
#    r = re.compile('(eval\(function\((?!w)\w+,\w+,\w+,\w+\),\w+,\w+.*?\{\}\)\);)', flags=re.DOTALL)
#    for g in r.findall(data):
#        try:
#            data = data.replace(g, wdecode(g))
#            escape_again=True
#        except:
#            pass

    
#    # n98c4d2c
#    if 'function n98c4d2c(' in data:
#        gs = parseTextToGroups(data, ".*n98c4d2c\(''\).*?'(%[^']+)'.*")
#        if gs != None and gs != []:
#            data = data.replace(gs[0], jsF.n98c4d2c(gs[0]))
            
#    if 'var enkripsi' in data:
#        r = re.compile(r"""enkripsi="([^"]+)""")
#        gs = r.findall(data)
#        if gs:
#            for g in gs:
#                s=''
#                for i in g:
#                    s+= chr(ord(i)^2)
#                data = data.replace("""enkripsi=\""""+g, urllib.unquote(s))
#    # o61a2a8f
#    if 'function o61a2a8f(' in data:
#        gs = parseTextToGroups(data, ".*o61a2a8f\(''\).*?'(%[^']+)'.*")
#        if gs != None and gs != []:
#            data = data.replace(gs[0], jsF.o61a2a8f(gs[0]))

#    # RrRrRrRr
#    if 'function RrRrRrRr(' in data:
#        r = re.compile("(RrRrRrRr\(\"(.*?)\"\);)</SCRIPT>", re.IGNORECASE + re.DOTALL)
#        gs = r.findall(data)
#        if gs != None and gs != []:
#            for g in gs:
#                data = data.replace(g[0], jsF.RrRrRrRr(g[1].replace('\\','')))

#    # hp_d01
#    if 'function hp_d01(' in data:
#        r = re.compile("hp_d01\(unescape\(\"(.+?)\"\)\);//-->")
#        gs = r.findall(data)
#        if gs:
#            for g in gs:
#                data = data.replace(g, jsF.hp_d01(g))

#    # ew_dc
#    if 'function ew_dc(' in data:
#        r = re.compile("ew_dc\(unescape\(\"(.+?)\"\)\);</SCRIPT>")
#        gs = r.findall(data)
#        if gs:
#            for g in gs:
#                data = data.replace(g, jsF.ew_dc(g))
                
#     # pbbfa0
#    if 'function pbbfa0(' in data:
#        r = re.compile("pbbfa0\(''\).*?'(.+?)'.\+.unescape")
#        gs = r.findall(data)
#        if gs:
#            for g in gs:
#                data = data.replace(g, jsF.pbbfa0(g))
    
#    if 'eval(function(' in data:
#        #lib.common.log("JairoX3:" + data)
#        data = re.sub(r"""function\(\w\w\w\w,\w\w\w\w,\w\w\w\w,\w\w\w\w""",'function(p,a,c,k)',data.replace('#','|'))
#        data = re.sub(r"""\(\w\w\w\w\)%\w\w\w\w""",'e%a',data)
#        data = re.sub(r"""RegExp\(\w\w\w\w\(\w\w\w\w\)""",'RegExp(e(c)',data)
#        r = re.compile(r"""\.split\('([^']+)'\)""")
#        gs = r.findall(data)
#        if gs:
#            for g in gs:
#                data = data.replace(g,'|')

#    if """.replace(""" in data:
#        r = re.compile(r""".replace\(["']([^"']+)["'],\s*["']([^"']*)["']\)""")
#        gs = r.findall(data)
#        if gs:
#            for g in gs:
#                data = data.replace(g[0],g[1])

#    # util.de
#    if 'Util.de' in data:
#        r = re.compile("Util.de\(unescape\(['\"](.+?)['\"]\)\)")
#        gs = r.findall(data)
#        if gs:
#            for g in gs:
#                data = data.replace(g,g.decode('base64'))

#    # 24cast
#    if 'destreamer(' in data:
#        r = re.compile("destreamer\(\"(.+?)\"\)")
#        gs = r.findall(data)
#        if gs:
#            for g in gs:
#                data = data.replace(g, destreamer(g))
                
#    # JS P,A,C,K,E,D
#    if jsU95.containsPacked(data):
#        data = jsU95.unpackAll(data)
#        escape_again=True
        
#    if jsU2.containsPacked(data):
#        data = jsU2.unpackAll(data)
#        escape_again=True
    
#    if jsU.containsPacked(data):
#        data = jsU.unpackAll(data)
#        escape_again=True

#    # JS W,I,S,E
#    if jsUW.containsWise(data):
#        data = jsUW.unwiseAll(data)
#        escape_again=True

#    # JS IonCube
#    if jsUI.containsIon(data):
#        data = jsUI.unIonALL(data)
#        escape_again=True
        
#    # Js unFunc
#    if jsUF.cointainUnFunc(data):
#        data = jsUF.unFuncALL(data)
#        escape_again=True
    
#    if jsUP.containUnPP(data):
#        data = jsUP.UnPPAll(data)
#        escape_again=True
        
#    if JsPush.containUnPush(data):
#        data = JsPush.UnPush(data)

#    if JsHive.contains_hivelogic(data):
#        data = JsHive.unpack_hivelogic(data)

#    try: data = zdecode(data)
#    except: pass
#    # unescape again
#    if escape_again:
#        data = doDemystify(data)
#    return data
