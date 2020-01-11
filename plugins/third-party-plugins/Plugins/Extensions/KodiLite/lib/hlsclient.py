"""
Simple HTTP Live Streaming client.

References:
    http://tools.ietf.org/html/draft-pantos-http-live-streaming-08

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.

Last updated: July 22, 2012

Original Code From:
    http://nneonneo.blogspot.gr/2010/08/http-live-streaming-client.html

Depends on python-crypto (for secure stream)
Modified for OpenPli enigma2 usage by athoik
Modified for KodiDirect and IPTVworld by pcd 
"""
##updated by pcd@xtrend-alliance 20140906##
pass#print "Here in hlsclient-py 1"
import urlparse, urllib2, os , re
pass#print "Here in hlsclient-py 2"
import sys, threading, time, Queue
pass#print "Here in hlsclient-py 3"
import operator
pass#print "Here in hlsclient-py 4"

SUPPORTED_VERSION = 3
STREAM_PFILE      = '/tmp/hls.avi'

def getUrl2(url, referer):
        pass#print "Here in client2 getUrl url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        req.add_header('Referer', referer)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link	

class hlsclient(threading.Thread):
 
    def __init__(self):
        self._stop = False
        self.thread = None
        self._downLoading = False
        pass#print "Here in hlsclient-py 1 "
        threading.Thread.__init__(self)

    def setUrl(self, url):
        pass#print "Here in hlsclient-py url 2=", url
        self.url = url
        self._stop = False
        self.thread = None
        self._downLoading = False

    def isDownloading(self):
        return self._downLoading

    def run(self):
        self.play()

    def download_chunks(self, downloadUrl, chunk_size=4096):
        pass#print "Here in hlsclient-py downloadUrl =", downloadUrl
#        conn=urllib2.urlopen(downloadUrl)
        req = urllib2.Request(downloadUrl)
        pass#print "Here in hlsclient-py self.header =", self.header
#        if self.header != "":
        hdr = 'User-Agent=ONLINETVCLIENT_X60000_X25000_X4000MEGA_V1770'
	req.add_header('User-Agent', 'User-Agent=ONLINETVCLIENT_X60000_X25000_X4000MEGA_V1770')
        conn = urllib2.urlopen(req)
        pass#print "Here in hlsclient-py downloadUrl done"
        while 1:
            data=conn.read(chunk_size)
            #pass#print "Here in hlsclient-py data =", data
            if not data: return
            yield data

    def download_file(self, downloadUrl):
        pass#print "Here in hlsclient-py downloadUrl A=", downloadUrl
        return ''.join(self.download_chunks(downloadUrl))

    def validate_m3u(self, conn):
        ''' make sure file is an m3u, and returns the encoding to use. '''
        mime = conn.headers.get('Content-Type', '').split(';')[0].lower()
        if mime == 'application/vnd.apple.mpegurl':
            enc = 'utf8'
        elif mime == 'audio/mpegurl':
            enc = 'iso-8859-1'
        elif conn.url.endswith('.m3u8'):
            enc = 'utf8'
        elif conn.url.endswith('.m3u'):
            enc = 'iso-8859-1'
        else:
#            raise Exception('[hlsclient::validate_m3u] Stream MIME type or file extension not recognized')
            pass#print "Here in hls-py into stop 8"
            os.remove(STREAM_PFILE)
            self.stop()
        if conn.readline().rstrip('\r\n') != '#EXTM3U':
#            raise Exception('[hlsclient::validate_m3u] Stream is not in M3U format')
            pass#print "Here in hls-py into stop 7"
            os.remove(STREAM_PFILE)
            self.stop()
        return enc

    def gen_m3u(self, url, skip_comments=True):
        pass#print "Here in hlsclient-py in gen_m3u url =", url
        pass#print "Here in hlsclient-py in gen_m3u self.header =", self.header
#        conn = urllib2.urlopen(url)
        req = urllib2.Request(url)
        if self.header != "":
	       req.add_header('User-Agent', str(self.header))
        conn = urllib2.urlopen(req)
        pass#print "Here in hlsclient-py in gen_m3u conn =", conn
#        enc = self.validate_m3u(conn)
        enc = 'utf8'
        for line in conn:
            pass#print "Here in hlsclient-py line 2 =", line
            line = line.rstrip('\r\n').decode(enc)
            pass#print "Here in hlsclient-py line 3 =", line
            if not line:
                # blank line
                continue
            elif line.startswith('#EXT'):
                # tag
                yield line
            elif line.startswith('#'):
                # comment
                if skip_comments:
                    continue
                else:
                    yield line
            else:
                # media file
                yield line
 
    def parse_m3u_tag(self, line):
        if ':' not in line:
            return line, []
        tag, attribstr = line.split(':', 1)
        attribs = []
        last = 0
        quote = False
        for i,c in enumerate(attribstr+','):
            if c == '"':
                quote = not quote
            if quote:
                continue
            if c == ',':
                attribs.append(attribstr[last:i])
                last = i+1
        return tag, attribs

    def parse_kv(self, attribs, known_keys=None):
        d = {}
        for item in attribs:
            k, v = item.split('=', 1)
            k=k.strip()
            v=v.strip().strip('"')
            if known_keys is not None and k not in known_keys:
#                raise ValueError('[hlsclient::parse_kv] unknown attribute %s' % k)
                  pass#print "Here in hls-py into stop 6"
                  os.remove(STREAM_PFILE)
                  self.stop()
            d[k] = v
        return d

    def handle_basic_m3uX(self, hlsUrl):
#http://l3md.shahid.net/media/l3/2fda1d3fd7ab453cad983544e8ed70e4/3be7afa11f5a4037bb0b1163d378c444/4df816395413420488af72856246b027/kormebra_s01_e27.mpegts/playlist-f01309a9eaa9e824e1b65430ddecf7f592cdfd76.m3u8
#line = re.sub('foo','bar', line.rstrip())
        base_key_url = 	re.sub('playlist-.*?.m3u8','',hlsUrl)
        seq = 1
        enc = None
        nextlen = 5
        duration = 5
        for line in self.gen_m3u(hlsUrl):
            if line.startswith('#EXT'):
                tag, attribs = self.parse_m3u_tag(line)
                if tag == '#EXTINF':
                    duration = float(attribs[0])
                elif tag == '#EXT-X-TARGETDURATION':
                    assert len(attribs) == 1, '[hlsclient::handle_basic_m3u] too many attribs in EXT-X-TARGETDURATION'
                    targetduration = int(attribs[0])
                    pass
                elif tag == '#EXT-X-MEDIA-SEQUENCE':
                    assert len(attribs) == 1, '[hlsclient::handle_basic_m3u] too many attribs in EXT-X-MEDIA-SEQUENCE'
                    seq = int(attribs[0])
                elif tag == '#EXT-X-KEY':
                    attribs = self.parse_kv(attribs, ('METHOD', 'URI', 'IV'))
                    assert 'METHOD' in attribs, '[hlsclient::handle_basic_m3u] expected METHOD in EXT-X-KEY'
                    if attribs['METHOD'] == 'NONE':
                        assert 'URI' not in attribs, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=NONE, but URI found'
                        assert 'IV' not in attribs, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=NONE, but IV found'
                        enc = None
                    elif attribs['METHOD'] == 'AES-128':
                        from Crypto.Cipher import AES
                        assert 'URI' in attribs, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=AES-128, but no URI found'
                        if 'https://' in attribs['URI']:
                            key = self.download_file(attribs['URI'].strip('"')) #key = self.download_file(base_key_url+attribs['URI'].strip('"'))
                            print(attribs['URI'].strip('"')) 
                        else:
#                            key = self.download_file(base_key_url+attribs['URI'].strip('"'))
                            key = self.download_file('m3u8http://hls.fra.rtlnow.de/hls-vod-enc-key/vodkey.bin')

#                            print(base_key_url+attribs['URI'].strip('"'))
                        assert len(key) == 16, '[hlsclient::handle_basic_m3u] EXT-X-KEY: downloaded key file has bad length'
                        if 'IV' in attribs:
                            assert attribs['IV'].lower().startswith('0x'), '[hlsclient::handle_basic_m3u] EXT-X-KEY: IV attribute has bad format'
                            iv = attribs['IV'][2:].zfill(32).decode('hex')
                            assert len(iv) == 16, '[hlsclient::handle_basic_m3u] EXT-X-KEY: IV attribute has bad length'
                        else:
                            iv = '\0'*8 + struct.pack('>Q', seq)
                        enc = AES.new(key, AES.MODE_CBC, iv)
                    else:
                        assert False, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=%s unknown' % attribs['METHOD']
                elif tag == '#EXT-X-PROGRAM-DATE-TIME':
                    assert len(attribs) == 1, '[hlsclient::handle_basic_m3u] too many attribs in EXT-X-PROGRAM-DATE-TIME'
                    # TODO parse attribs[0] as ISO8601 date/time
                    pass
                elif tag == '#EXT-X-ALLOW-CACHE':
                    # XXX deliberately ignore
                    pass
                elif tag == '#EXT-X-ENDLIST':
                    assert not attribs
                    yield None
                    return
                elif tag == '#EXT-X-STREAM-INF':
#                    raise ValueError('[hlsclient::handle_basic_m3u] dont know how to handle EXT-X-STREAM-INF in basic playlist')
                    pass#print "Here in hls-py into stop 5"
                    os.remove(STREAM_PFILE)
                    self.stop()
                elif tag == '#EXT-X-DISCONTINUITY':
                    assert not attribs
                    pass#print '[hlsclient::handle_basic_m3u] discontinuity in stream'
                elif tag == '#EXT-X-VERSION':
                    assert len(attribs) == 1
                    if int(attribs[0]) > SUPPORTED_VERSION:
                        pass#print '[hlsclient::handle_basic_m3u] file version %s exceeds supported version %d; some things might be broken' % (attribs[0], SUPPORTED_VERSION)
                else:
#                    raise ValueError('[hlsclient::handle_basic_m3u] tag %s not known' % tag)
                    pass#print "Here in hls-py into stop 4"
                    os.remove(STREAM_PFILE)
                    self.stop()
            else:
                yield (seq, enc, duration, targetduration, line)
                seq += 1
    def handle_basic_m3u(self, hlsUrl):
        seq = 1
        enc = None
        nextlen = 5
        duration = 5
        for line in self.gen_m3u(hlsUrl):
            if "#EXT-X-PLAYLIST-TYPE:VOD" in line:
                line.replace("#EXT-X-PLAYLIST-TYPE:VOD", "")
                continue
            if line.startswith('#EXT'):
                tag, attribs = self.parse_m3u_tag(line)
                pass#print "Here in hlsclient-py line =", line
                pass#print "Here in hlsclient-py tag =", tag
                pass#print "Here in hlsclient-py attribs =", attribs
                if tag == '#EXTINF':
                    duration = float(attribs[0])
                elif tag == '#EXT-X-TARGETDURATION':
                    assert len(attribs) == 1, '[hlsclient::handle_basic_m3u] too many attribs in EXT-X-TARGETDURATION'
                    targetduration = int(attribs[0])
                    pass
                elif tag == '#EXT-X-MEDIA-SEQUENCE':
                    assert len(attribs) == 1, '[hlsclient::handle_basic_m3u] too many attribs in EXT-X-MEDIA-SEQUENCE'
                    seq = int(attribs[0])
                elif tag == '#EXT-X-KEY':
                    attribs = self.parse_kv(attribs, ('METHOD', 'URI', 'IV'))
                    assert 'METHOD' in attribs, '[hlsclient::handle_basic_m3u] expected METHOD in EXT-X-KEY'
                    if attribs['METHOD'] == 'NONE':
                        assert 'URI' not in attribs, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=NONE, but URI found'
                        assert 'IV' not in attribs, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=NONE, but IV found'
                        enc = None
                    elif attribs['METHOD'] == 'AES-128':
                        from Crypto.Cipher import AES
                        assert 'URI' in attribs, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=AES-128, but no URI found'
                        pass#print "Here in hlsclient-py attribs['URI'] =", attribs['URI']
                        key = self.download_file(attribs['URI'].strip('"'))
                        assert len(key) == 16, '[hlsclient::handle_basic_m3u] EXT-X-KEY: downloaded key file has bad length'
                        if 'IV' in attribs:
                            assert attribs['IV'].lower().startswith('0x'), '[hlsclient::handle_basic_m3u] EXT-X-KEY: IV attribute has bad format'
                            iv = attribs['IV'][2:].zfill(32).decode('hex')
                            assert len(iv) == 16, '[hlsclient::handle_basic_m3u] EXT-X-KEY: IV attribute has bad length'
                        else:
                            iv = '\0'*8 + struct.pack('>Q', seq)
                        enc = AES.new(key, AES.MODE_CBC, iv)
                    else:
                        assert False, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=%s unknown' % attribs['METHOD']
                elif tag == '#EXT-X-PROGRAM-DATE-TIME':
                    assert len(attribs) == 1, '[hlsclient::handle_basic_m3u] too many attribs in EXT-X-PROGRAM-DATE-TIME'
                    # TODO parse attribs[0] as ISO8601 date/time
                    pass
                elif tag == '#EXT-X-ALLOW-CACHE':
                    # XXX deliberately ignore
                    pass
                elif tag == '#EXT-X-ENDLIST':
                    assert not attribs
                    yield None
                    return
                elif tag == '#EXT-X-STREAM-INF':
                    pass#print "Here in hls-py into stop 3"
                    os.remove(STREAM_PFILE)
                    self.stop()
#                    raise ValueError('[hlsclient::handle_basic_m3u] dont know how to handle EXT-X-STREAM-INF in basic playlist')
                elif tag == '#EXT-X-DISCONTINUITY':
                    assert not attribs
                    pass#print '[hlsclient::handle_basic_m3u] discontinuity in stream'
                elif tag == '#EXT-X-VERSION':
                    assert len(attribs) == 1
                    if int(attribs[0]) > SUPPORTED_VERSION:
                        pass#print '[hlsclient::handle_basic_m3u] file version %s exceeds supported version %d; some things might be broken' % (attribs[0], SUPPORTED_VERSION)
                else:
#                    raise ValueError('[hlsclient::handle_basic_m3u] tag %s not known' % tag)
                    pass#print "Here in hls-py into stop 2"
                    pass
##                    os.remove(STREAM_PFILE)
##                    self.stop()
            else:
                pass#print "Here in hls-py line final=", line
                yield (seq, enc, duration, targetduration, line)
                seq += 1

    def player_pipe(self, queue, videopipe):
        while not self._stop:
            block = queue.get(block=True)
            if block is None: return
            videopipe.write(block)
            #videopipe.flush()
            if not self._downLoading:
                pass#print 'Connected...'
                self._downLoading = True

    def play(self, header):
        #check if pipe exists
##        if os.access(STREAM_PFILE, os.W_OK):
        self.header = header
        if os.path.exists(STREAM_PFILE):
               os.remove(STREAM_PFILE)
#        os.mkfifo(STREAM_PFILE)
        cmd = "/usr/bin/mkfifo " + STREAM_PFILE
        pass#print "Here in hlsclient-py cmd =" , cmd
        os.system(cmd)
        pass#print "Here in hlsclient-py cmd done"
        videopipe = open(STREAM_PFILE, "w+b")
        pass#print "Here in hlsclient-py play"
        variants = []
        variant = None
        
        for line in self.gen_m3u(self.url):
            if line.startswith('#EXT'):
                tag, attribs = self.parse_m3u_tag(line)
                if tag == '#EXT-X-STREAM-INF':
                    variant = attribs
            elif variant:
                variants.append((line, variant))
                variant = None
        pass#print "Here in hlsclient-py variants =", variants        
        if len(variants) == 1:
            self.url = urlparse.urljoin(self.url, variants[0][0])
        elif len(variants) >= 2:
            pass#print '[hlsclient::play] More than one variant of the stream was provided.'
            autoChoice = {}
            for i, (vurl, vattrs) in enumerate(variants):
                pass#print "i, vurl =", i, vurl
                pass#print "i, vattrs =", i, vattrs
                for attr in vattrs:
                    key, value = attr.split('=')
                    key = key.strip()
                    value = value.strip().strip('"')
                    if key == 'BANDWIDTH':
                        #Limit bandwidth?
                        #if int(value) < 1000000:
                        #    autoChoice[i] = int(value)
                        autoChoice[i] = int(value)
                        pass#print 'bitrate %.2f kbps' % (int(value)/1024.0)
                    elif key == 'PROGRAM-ID':
                        pass#print 'program %s' % value,
                    elif key == 'CODECS':
                        pass#print 'codec %s' % value,
                    elif key == 'RESOLUTION':
                        pass#print 'resolution %s' % value,
                    else:
                        pass
#                        raise ValueError('[hlsclient::play] unknown STREAM-INF attribute %s' % key)
##                        pass#print "Here in hls-py into stop 1"
##                        os.remove(STREAM_PFILE)
##                        self.stop()
#                print
            choice = max(autoChoice.iteritems(), key=operator.itemgetter(1))[0]
            pass#print '[hlsclient::play] Autoselecting %s' % choice
            #Use the first choice for testing
##            choice = 0
            self.url = urlparse.urljoin(self.url, variants[choice][0])

        queue = Queue.Queue(1024) # 1024 blocks of 4K each ~ 4MB buffer
        self.thread = threading.Thread(target=self.player_pipe, args=(queue, videopipe))
        self.thread.start()
        last_seq = -1
        targetduration = 5
        changed = 0
#        try:
        while self.thread.isAlive():
                if self._stop:
                    pass#print '[hlsclient::play] Stopping Download Thread'
                    self.hread._Thread__stop()
                medialist = list(self.handle_basic_m3u(self.url))
                pass#print 'Here in [hlsclient::play] medialist A=', medialist
                if None in medialist:
                    # choose to start playback at the start, since this is a VOD stream
                    pass
                else:
                    # choose to start playback three files from the end, since this is a live stream
                    medialist = medialist[-3:]
                    pass#print 'Here in [hlsclient::play] medialist =', medialist
                for media in medialist:
                  try:
                    if media is None:
                        queue.put(None, block=True)
                        return
                    seq, enc, duration, targetduration, media_url = media
                    pass#print 'Here in [hlsclient::play] media_url =', media_url
                    if seq > last_seq:
                        for chunk in self.download_chunks(urlparse.urljoin(self.url, media_url)):
                            if enc: chunk = enc.decrypt(chunk)
                            queue.put(chunk, block=True)
                        last_seq = seq
                        changed = 1
                  except:
                        pass        
                        
                self._sleeping = True
                if changed == 1:
                    # initial minimum reload delay
                    time.sleep(duration)
                elif changed == 0:
                    # first attempt
                    time.sleep(targetduration*0.5)
                elif changed == -1:
                    # second attempt
                    time.sleep(targetduration*1.5)
                else:
                    # third attempt and beyond
                    time.sleep(targetduration*3.0)
                self._sleeping = False
                changed -= 1
#        except Exception as ex:
#            pass#print '[hlsclient::play] Exception %s; Stopping threads' % ex 
#            self._stop = True
#            self_downLoading = False
#            self.thread._Thread__stop()
#            self._Thread__stop()
        
    def stop(self):
        self._stop = True
        self._downLoading = False
        if self.thread:
            self.thread._Thread__stop()
        pass#print '[hlsclient::stop] Stopping Main hlsclient thread'
        self._Thread__stop()


pass#print "Here in sys.argv =", sys.argv
if __name__ == '__main__':
        pass#print "Here in sys.argv =", sys.argv
#    if len(sys.argv) <> 3:
#        pass#print "Here in usage", sys.argv[0], "<stream URL> L%s" % len(sys.argv)
#        sys.exit(1)
#    else:
        try:
            pass#print "Here in sys.argv B=", sys.argv
            h = hlsclient()
            h.setUrl(sys.argv[1])
            pass#print "(sys.argv[2]) =", sys.argv[2]
            header = sys.argv[3]
            pass#print "header =", header
            if (sys.argv[2]) == '1':
                pass#print "Here in going in play"
##                h.start()
                h.play(header)
                pass#print "Here in started"
#                while 1:
#                    time.sleep(10)
#            else:
#                h.stop()
        except:
#            if h:
#                h.stop()
             pass#print "In except"
             os.remove(STREAM_PFILE)
             h.stop()
