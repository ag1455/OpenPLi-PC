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
    http://nneonneo.bpass#logspot.gr/2010/08/http-live-streaming-client.html

Depends on python-crypto (for secure stream)
Modified for OpenPli enigma2 usage by athoik
Modified for KodiDirect, KodiLite and IPTVworld by pcd 
"""
def log(msg):
        f1=open("/tmp/e.log","a")
        ms = "\n" + msg
        f1.write(ms)
        f1.close()

pass#log("Here in hlsclient-py 1")
import urlparse, urllib2, os , re
pass#print "Here in hlsclient-py 2"
import sys, threading, time, Queue
pass#print "Here in hlsclient-py 3"
import operator
pass#print "Here in hlsclient-py 4"

SUPPORTED_VERSION = 3
STREAM_PFILE      = '/tmp/hls.avi'
################################
import bitstring

defualtype=""
def getLastPTS(data,rpid,type="video"):
    ##pass#print 'inpcr'
    ret=None
    currentpost=len(data)
    ##pass#print 'currentpost',currentpost
    found=False
    packsize=188
    spoint=0
    while not found:
        ff=data.rfind('\x47',0,currentpost-1)
        ##pass#print 'ff',ff,data[ff-188]
        if ff==-1:
            #pass#print 'No sync data'
            found=True
        elif data[ff-packsize]=='\x47' and data[ff-packsize-packsize]=='\x47':
            spoint=ff
            found=True
        else:
            currentpost=ff-1
    ##pass#print 'spoint',spoint
    if spoint<=0: return None
    
    currentpost=   spoint 
    found=False
    while not found:
        ##pass#print len(data)-currentpost
        if len(data)-currentpost>=188:
            ##pass#print 'currentpost',currentpost
            bytes=data[currentpost:currentpost+188]
            
            bits=bitstring.ConstBitStream(bytes=bytes)
            sign=bits.read(8).uint
            tei = bits.read(1).uint
            pusi = bits.read(1).uint
            transportpri = bits.read(1).uint
            pid = bits.read(13).uint
            ##pass#print pid
            if pid==rpid or rpid==0:
                ##pass#print pid
                ##pass#print 1/0
             
                try:
                    packet = bits.read((packsize-3)*8)
                    scramblecontrol = packet.read(2).uint
                    adapt = packet.read(2).uint
                    concounter = packet.read(4).uint
                except:
                    #pass#print 'error'
                    return None##pass#print 'errpor'#adapt=-1
                decodedpts=None
                av=""
                ##pass#print 'adapt',adapt
                if adapt == 3:
                    adaptation_size = packet.read(8).uint
                    discontinuity = packet.read(1).uint
                    random = packet.read(1).uint
                    espriority = packet.read(1).uint
                    pcrpresent = packet.read(1).uint
                    opcrpresent = packet.read(1).uint
                    splicingpoint = packet.read(1).uint
                    transportprivate = packet.read(1).uint
                    adaptation_ext = packet.read(1).uint
                    restofadapt = (adaptation_size+3) - 1
                    if pcrpresent == 1:
                        pcr = packet.read(48)
                        restofadapt -=  6
                    if opcrpresent == 1:
                        opcr = packet.read(48)
                        restofadapt -=  6
                    packet.pos += (restofadapt-3) * 8
                    if ((packet.len - packet.pos)/8) > 5:
                        pesync = packet.read(24)#.hex
                        if pesync == ('0x000001'):
                            pestype = packet.read(8).uint
                            if pestype > 223 and pestype < 240:
                                av = 'video'
                            if pestype < 223 and pestype > 191:
                                av = 'audio'
                            packet.pos += (3*8)
                            ptspresent = packet.read(1).uint
                            dtspresent = packet.read(1).uint
                            if ptspresent:
                                packet.pos += (14)
                                pts = packet.read(40)
                                pts.pos = 4
                                firstpartpts = pts.read(3)
                                pts.pos += 1
                                secondpartpts = pts.read(15)
                                pts.pos += 1
                                thirdpartpts = pts.read(15)
                                #decodedpts = bitstring.ConstBitArray().join([firstpartpts.bin, secondpartpts.bin, thirdpartpts.bin]).uint
                                decodedpts =int(''.join([firstpartpts.bin, secondpartpts.bin, thirdpartpts.bin]),2)#
                            if dtspresent:
                                dts = packet.read(40)
                                dts.pos = 4
                                firstpartdts = dts.read(3)
                                dts.pos += 1
                                secondpartdts = dts.read(15)
                                dts.pos += 1
                                thirdpartdts = dts.read(15)
                                #decodeddts = bitstring.ConstBitArray().join([firstpartdts.bin, secondpartdts.bin, thirdpartdts.bin]).uint
                                decodeddts =int(''.join([firstpartdts.bin, secondpartdts.bin, thirdpartdts.bin]),2)#
                elif adapt == 2:
                    #if adapt is 2 the packet is only an adaptation field
                    adaptation_size = packet.read(8).uint
                    discontinuity = packet.read(1).uint
                    random = packet.read(1).uint
                    espriority = packet.read(1).uint
                    pcrpresent = packet.read(1).uint
                    opcrpresent = packet.read(1).uint
                    splicingpoint = packet.read(1).uint
                    transportprivate = packet.read(1).uint
                    adaptation_ext = packet.read(1).uint
                    restofadapt = (adaptation_size+3) - 1
                    if pcrpresent == 1:
                        pcr = packet.read(48)
                        restofadapt -=  6
                    if opcrpresent == 1:
                        opcr = packet.read(48)
                        restofadapt -=  6
                elif adapt == 1:
                    pesync = packet.read(24)#.hex
                    ##pass#print 'pesync',pesync
                    if pesync == ('0x000001'):
                        pestype = packet.read(8).uint
                        if pestype > 223 and pestype < 240:
                            av = 'video'
                        if pestype < 223 and pestype > 191:
                            av = 'audio'
                        packet.pos += 24
                        ptspresent = packet.read(1).uint
                        dtspresent = packet.read(1).uint
                        ##pass#print 'ptspresent',ptspresent
                        if ptspresent:
                            packet.pos += (14)
                            pts = packet.read(40)
                            pts.pos = 4
                            firstpartpts = pts.read(3)
                            pts.pos += 1
                            secondpartpts = pts.read(15)
                            pts.pos += 1
                            thirdpartpts = pts.read(15)
                            #decodedpts = bitstring.ConstBitArray().join([firstpartpts.bin, secondpartpts.bin, thirdpartpts.bin]).uint
                            decodedpts =int(''.join([firstpartpts.bin, secondpartpts.bin, thirdpartpts.bin]),2)#
                        if dtspresent:
                                dts = packet.read(40)
                                dts.pos = 4
                                firstpartdts = dts.read(3)
                                dts.pos += 1
                                secondpartdts = dts.read(15)
                                dts.pos += 1
                                thirdpartdts = dts.read(15)
                                #decodeddts = bitstring.ConstBitArray().join([firstpartdts.bin, secondpartdts.bin, thirdpartdts.bin]).uint
                                decodeddts =int(''.join([firstpartdts.bin, secondpartdts.bin, thirdpartdts.bin]),2)#
                if decodedpts and (type=="" or av==type) and len(av)>0:
                    ##pass#print 'currentpost',currentpost,decodedpts
                    return decodedpts
            
        currentpost=currentpost-packsize
        if currentpost<10:
            #pass#print 'came back to begin'
            found=True
    return ret


def getFirstPTSFrom(data,rpid, initpts,type="video" ):
    ##pass#pass#print 'xxxxxxxxxxxinpcr getFirstPTSFrom'
    ret=None
    currentpost=0#len(data)
    ##pass#pass#print 'currentpost',currentpost
    found=False
    packsize=188
    spoint=0
    ##pass#pass#print 'inwhile'
    while not found:
        ff=data.find('\x47',currentpost)
        if ff==-1:
            #pass#pass#print 'No sync data'
            found=True
        elif data[ff+packsize]=='\x47' and data[ff+packsize+packsize]=='\x47':
            spoint=ff
            found=True
        else:
            currentpost=ff+1
    ##pass#pass#print 'spoint',spoint
    if spoint>len(data)-packsize: return None
    
    currentpost=   spoint 
    found=False    

    while not found:
        ##pass#pass#print 'currentpost',currentpost
        if len(data)-currentpost>=188:
            bytes=data[currentpost:currentpost+188]
            
            bits=bitstring.ConstBitStream(bytes=bytes)
            sign=bits.read(8).uint
            tei = bits.read(1).uint
            pusi = bits.read(1).uint
            transportpri = bits.read(1).uint
            pid = bits.read(13).uint
            ##pass#pass#print pid
            ##pass#pass#print pid,rpid
                ##pass#pass#print 1/0
            if rpid==pid or rpid==0: 
                ##pass#pass#print 'here pid is same'
                try:
                    packet = bits.read((packsize-3)*8)
                    scramblecontrol = packet.read(2).uint
                    adapt = packet.read(2).uint
                    concounter = packet.read(4).uint
                except:
                    #pass#pass#print 'error'
                    return None##pass#pass#print 'errpor'#adapt=-1
                decodedpts=None
                av=""
                if adapt == 3:
                    adaptation_size = packet.read(8).uint
                    discontinuity = packet.read(1).uint
                    random = packet.read(1).uint
                    espriority = packet.read(1).uint
                    pcrpresent = packet.read(1).uint
                    opcrpresent = packet.read(1).uint
                    splicingpoint = packet.read(1).uint
                    transportprivate = packet.read(1).uint
                    adaptation_ext = packet.read(1).uint
                    restofadapt = (adaptation_size+3) - 1
                    if pcrpresent == 1:
                        pcr = packet.read(48)
                        restofadapt -=  6
                    if opcrpresent == 1:
                        opcr = packet.read(48)
                        restofadapt -=  6
                    packet.pos += (restofadapt-3) * 8
                    if ((packet.len - packet.pos)/8) > 5:
                        pesync = packet.read(24)#.hex
                        if pesync == ('0x000001'):
                            pestype = packet.read(8).uint
                            if pestype > 223 and pestype < 240:
                                av = 'video'
                            if pestype < 223 and pestype > 191:
                                av = 'audio'
                            packet.pos += (3*8)
                            ptspresent = packet.read(1).uint
                            dtspresent = packet.read(1).uint
                            if ptspresent:
                                packet.pos += (14)
                                pts = packet.read(40)
                                pts.pos = 4
                                firstpartpts = pts.read(3)
                                pts.pos += 1
                                secondpartpts = pts.read(15)
                                pts.pos += 1
                                thirdpartpts = pts.read(15)
                                #decodedpts = bitstring.ConstBitArray().join([firstpartpts.bin, secondpartpts.bin, thirdpartpts.bin]).uint
                                decodedpts =int(''.join([firstpartpts.bin, secondpartpts.bin, thirdpartpts.bin]),2)#
                            if dtspresent:
                                dts = packet.read(40)
                                dts.pos = 4
                                firstpartdts = dts.read(3)
                                dts.pos += 1
                                secondpartdts = dts.read(15)
                                dts.pos += 1
                                thirdpartdts = dts.read(15)
                                #decodeddts = bitstring.ConstBitArray().join([firstpartdts.bin, secondpartdts.bin, thirdpartdts.bin]).uint
                                decodeddts =int(''.join([firstpartdts.bin, secondpartdts.bin, thirdpartdts.bin]),2)#
                elif adapt == 2:
                    #if adapt is 2 the packet is only an adaptation field
                    adaptation_size = packet.read(8).uint
                    discontinuity = packet.read(1).uint
                    random = packet.read(1).uint
                    espriority = packet.read(1).uint
                    pcrpresent = packet.read(1).uint
                    opcrpresent = packet.read(1).uint
                    splicingpoint = packet.read(1).uint
                    transportprivate = packet.read(1).uint
                    adaptation_ext = packet.read(1).uint
                    restofadapt = (adaptation_size+3) - 1
                    if pcrpresent == 1:
                        pcr = packet.read(48)
                        restofadapt -=  6
                    if opcrpresent == 1:
                        opcr = packet.read(48)
                        restofadapt -=  6
                elif adapt == 1:
                    pesync = packet.read(24)#.hex
                    ##pass#pass#print 'pesync',pesync
                    if pesync == ('0x000001'):
                        pestype = packet.read(8).uint
                        if pestype > 223 and pestype < 240:
                            av = 'video'
                        if pestype < 223 and pestype > 191:
                            av = 'audio'
                        packet.pos += 24
                        ptspresent = packet.read(1).uint
                        dtspresent = packet.read(1).uint
                        ##pass#pass#print 'ptspresent',ptspresent
                        if ptspresent:
                            packet.pos += (14)
                            pts = packet.read(40)
                            pts.pos = 4
                            firstpartpts = pts.read(3)
                            pts.pos += 1
                            secondpartpts = pts.read(15)
                            pts.pos += 1
                            thirdpartpts = pts.read(15)
                            #decodedpts = bitstring.ConstBitArray().join([firstpartpts.bin, secondpartpts.bin, thirdpartpts.bin]).uint
                            decodedpts =int(''.join([firstpartpts.bin, secondpartpts.bin, thirdpartpts.bin]),2)#
                        if dtspresent:
                                dts = packet.read(40)
                                dts.pos = 4
                                firstpartdts = dts.read(3)
                                dts.pos += 1
                                secondpartdts = dts.read(15)
                                dts.pos += 1
                                thirdpartdts = dts.read(15)
                                #decodeddts = bitstring.ConstBitArray().join([firstpartdts.bin, secondpartdts.bin, thirdpartdts.bin]).uint
                                decodeddts =int(''.join([firstpartdts.bin, secondpartdts.bin, thirdpartdts.bin]),2)#
                if decodedpts and (type=="" or av==type) and len(av)>0:
                    ##pass#pass#print decodedpts
                    if decodedpts>initpts:
                        return decodedpts,currentpost
        else:
            found=True
        currentpost=currentpost+188
        if currentpost>=len(data):
            ##pass#pass#print 'came back to begin'
            found=True
    return ret
        
################################

class hlsclient(threading.Thread):
 
    def __init__(self):
        self._stop = False
        self.thread = None
        self._downLoading = False
        pass#print "Here in hlsclient-py 1 "
        threading.Thread.__init__(self)

    def setUrl(self, url):
        pass#print "Here in hlsclient-py url =", url
        self.url = url
        self._stop = False
        self.thread = None
        self._downLoading = False

    def isDownloading(self):
        return self._downLoading

    def run(self):
        self.play()
#    def download_chunks(self, downloadUrl, chunk_size=4096):
    def download_chunks(self, downloadUrl, chunk_size=192512):
        pass#print "Here in hlsclient-py downloadUrl =", downloadUrl
        conn=urllib2.urlopen(downloadUrl)
        pass#print "Here in hlsclient-py downloadUrl done"
        while 1:
            data=conn.read(chunk_size)
##            pass#print "Here in hlsclient-py data =", data
            if not data: return
            yield data

    def download_file(self, downloadUrl):
        pass#print "Here in hlsclient-py downloadUrl A=", downloadUrl
        return ''.join(self.download_chunks(downloadUrl))


    def player_pipe(self, queue, videopipe):
        while not self._stop:
            block = queue.get(block=True)
            if block is None: return
            videopipe.write(block)
            #videopipe.flush()
            if not self._downLoading:
                pass#print 'Connected...'
                self._downLoading = True

    def play(self):
        #check if pipe exists
##        if os.access(STREAM_PFILE, os.W_OK):
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
        """
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
        """
        queue = Queue.Queue(1024) # 1024 blocks of 4K each ~ 4MB buffer
        self.thread = threading.Thread(target=self.player_pipe, args=(queue, videopipe))
        self.thread.start()
#        try:
        fpts = 0
        while self.thread.isAlive():
                if self._stop:
                    pass#print '[hlsclient::play] Stopping Download Thread'
                    self.hread._Thread__stop()
                """    
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
                """    
                lastpts = 0
                fixpid=256
                lastchunk = ""
#                fpts = 0
                i = 0
                starttime = time.time()
                for chunk in self.download_chunks(self.url):
                   lastchunk = chunk
                   pass#log("Here in i A1="+str(i))
                   if len(chunk) >1:
#                      pass#log("Here in i A="+str(i))
                      if i == 0:
#                          try:
#                            if enc: chunk = enc.decrypt(chunk)
                            pass#log("Here in i B="+str(i))
                            try:
                                   firstpts,pos= getFirstPTSFrom(chunk,fixpid,lastpts)
                                   pass#log("Here in firstpts ="+str(firstpts))
                            except:       
                                   pass#log("Here in pts error")
                                   continue

                      i = i+1      
                      pass#log("Here in i A="+str(i))
                      pass#log("Here in firstpts queue="+str(firstpts))
                      queue.put(chunk, block=True)
                   else:
                         continue   
                      
                lc = len(lastchunk)
                pass#log("len(lastchunk) ="+str(lc))

#                firstpts,pos= getFirstPTSFrom(chunk,fixpid,lastpts)
                pass#log("Here in i C="+str(i))
                pass#log("Here in firstpts B="+str(firstpts)) 
                fpts = firstpts
                pass#log("Here in fpts B="+str(fpts))  
                
                lastpts=getLastPTS(lastchunk,fixpid,defualtype)
                if (lastpts is None) or (lastpts == "None"):
                       lastpts = 0
                pass#log("Here in lastpts ="+str(lastpts))
#                time.sleep(5)

                videotime = lastpts - firstpts
                pass#log("Here in videotime ="+str(videotime))
                videotime = videotime/90000
                pass#log("Here in videotime 2="+str(videotime))
                pass#log("Here in starttime ="+str(starttime))
                starttime = int(float(starttime))
                pass#log("Here in starttime 2="+str(starttime))
                endtime = time.time()
                pass#log("Here in endtime ="+str(endtime))
                endtime = int(float(endtime))
                pass#log("Here in endtime 2="+str(endtime))
                timetaken = endtime - starttime
                pass#log("Here in timetaken="+str(timetaken))
                if videotime > timetaken:
                       sleeptime = videotime - timetaken 
                else:
                       sleeptime = 10
                pass#log("Here in sleeptime="+str(sleeptime))
              
                pass#log("Here in time before sleep ="+str(time.time()))
#                if sleeptime > 2:
#                       sleeptime = sleeptime - 2
                time.sleep(sleeptime)
                pass#log("Here in time after sleep ="+str(time.time()))       
                           
                """
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
                """
                pass
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
            if (sys.argv[2]) == '1':
                pass#print "Here in going in play"
##                h.start()
                h.play()
                pass#print "Here in started"
        except:
#            if h:
#                h.stop()
             pass#print "In except"
             os.remove(STREAM_PFILE)
             h.stop()
