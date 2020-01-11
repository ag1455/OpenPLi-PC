"""
XBMCLocalProxy 0.1
Copyright 2011 Torben Gerkensmeyer

Modified for Livestreamer by your mom 2k15

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.
"""

import xbmc
import base64
import urlparse,urllib
import sys, traceback
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

import struct
import streamlink
from streamlink.exceptions import StreamError
from urlparse import urljoin



##aes stuff
_android_ssl = False
_oscrypto = False
_dec = False

'''
disabled pycrypto because it breaks AES enc streams for some reason. script module has to
be installed though due to dependencies in streamlink
'''
# try:
#     from Crypto.Cipher import AES
#     _dec = True
# except ImportError:

try:
    from Cryptodome.Cipher import AES
    _dec = True
except ImportError:
    try:
        import androidsslPy
        enc = androidsslPy._load_crypto_libcrypto()
        _android_ssl = True
        _dec = True
    except:
        try:
            from oscrypto.symmetric import aes_cbc_no_padding_decrypt
            class AES(object):
                def __init__(self,key,iv):
                    self.key=key
                    self.iv=iv
                def decrypt(self, data):
                    return aes_cbc_no_padding_decrypt(self.key, data, self.iv)
            _oscrypto = True
            _dec = True
        except: pass


def num_to_iv(n):
    return struct.pack(">8xq", n)

def create_decryptor(self, key, sequence):
    #self.logger.debug('key.method, key.uri: %s, %s'%(key.method, key.uri))

    if key.method != "AES-128":
        raise StreamError("Unable to decrypt cipher {0}", key.method)

    if not key.uri:
        raise StreamError("Missing URI to decryption key")

    if self.key_uri != key.uri:
        zoom_key = self.reader.stream.session.options.get("zoom-key")
        zuom_key = self.reader.stream.session.options.get("zuom-key")
        livecam_key = self.reader.stream.session.options.get("livecam-key")
        saw_key = self.reader.stream.session.options.get("saw-key")
        your_key = self.reader.stream.session.options.get("your-key")
        mama_key = self.reader.stream.session.options.get("mama-key")
        if zoom_key:
            uri = 'http://www.zoomtv.me/k.php?q='+base64.urlsafe_b64encode(zoom_key+base64.urlsafe_b64encode(key.uri))
        elif zuom_key:
            uri = 'http://www.zuom.xyz/k.php?q='+base64.urlsafe_b64encode(zuom_key+base64.urlsafe_b64encode(key.uri))
        elif livecam_key:           
            h = urlparse.urlparse(urllib.unquote(livecam_key)).netloc
            q = urlparse.urlparse(urllib.unquote(livecam_key)).query            
            uri = 'http://%s/kaes?q='%h+base64.urlsafe_b64encode(q+base64.b64encode(key.uri))
        elif saw_key:
            if 'foxsportsgo' in key.uri:
                _tmp = key.uri.split('/')
                uri = urljoin(saw_key,'/m/fream?p='+_tmp[-4]+'&k='+_tmp[-1])
            elif 'nlsk.neulion' in key.uri:
                _tmp = key.uri.split('?')
                uri = urljoin(saw_key,'/m/stream?'+_tmp[-1])
            elif 'nlsk' in key.uri:
                _tmp = key.uri.split('?')
                uri = 'http://bile.level303.club/m/stream?'+_tmp[-1]
            elif 'nhl.com' in key.uri:
                _tmp = key.uri.split('/')
                uri = urljoin(saw_key,'/m/streams?ci='+_tmp[-3]+'&k='+_tmp[-1])
            else:
                uri = key.uri
        elif mama_key:
           if 'nlsk' in key.uri:
                _tmp = key.uri.split('&url=')
                uri = 'http://mamahd.in/nba?url=' + _tmp[-1]
        elif your_key:
            if 'mlb.com' in key.uri:
                _tmp = key.uri.split('?')
                uri = urljoin(your_key,'/mlb/get_key/'+_tmp[-1])
            elif 'espn3/auth' in key.uri:
                _tmp = key.uri.split('?')
                uri = urljoin(your_key,'/ncaa/get_key/'+_tmp[-1])
            elif 'nhl.com' in key.uri:
                _tmp = key.uri.split('nhl.com/')
                uri = urljoin(your_key,'/nhl/get_key/'+_tmp[-1])
            else:
                uri = key.uri
        else:
            uri = key.uri

        res = self.session.http.get(uri, exception=StreamError,
                                    retries=self.retries,
                                    **self.reader.request_params)

        self.key_data = res.content
        self.key_uri = key.uri

    iv = key.iv or num_to_iv(sequence)

    # Pad IV if needed
    iv = b"\x00" * (16 - len(iv)) + iv

    if _android_ssl:
        return enc(self.key_data, iv)
    elif _oscrypto:
        return AES(self.key_data, iv)
    else:
        return AES.new(self.key_data, AES.MODE_CBC, iv)


# unpad = lambda s : s[0:-ord(s[-1])]

# def write(self, sequence, res, chunk_size=8192):
#     if sequence.segment.key and sequence.segment.key.method != "NONE":
#         try:
#             decryptor = self.create_decryptor(sequence.segment.key,
#                                                 sequence.num)
#         except StreamError as err:
#             self.logger.error("Failed to create decryptor: {0}", err)
#             self.close()
#             return

#         data = res.content
#         # If the input data is not a multiple of 16, cut off any garbage
#         garbage_len = len(data) % 16
#         if garbage_len:
#             self.logger.debug("Cutting off {0} bytes of garbage "
#                                 "before decrypting", garbage_len)
#             decrypted_chunk = decryptor.decrypt(data[:-garbage_len])
#         else:
#             decrypted_chunk = decryptor.decrypt(data)

#         self.reader.buffer.write(unpad(decrypted_chunk))

#     else:
#         for chunk in res.iter_content(chunk_size):
#             self.reader.buffer.write(chunk)

#     self.logger.debug("Download of segment {0} complete", sequence.num)


def process_sequences(self, playlist, sequences):    
    first_sequence, last_sequence = sequences[0], sequences[-1]
    #self.logger.debug("process_sequences: %s"%len(sequences))

    if first_sequence.segment.key and first_sequence.segment.key.method != "NONE":
        self.logger.debug("Segments in this playlist are encrypted")

    self.playlist_changed = ([s.num for s in self.playlist_sequences] !=
                                [s.num for s in sequences])
    self.playlist_reload_time = (playlist.target_duration or
                                    last_sequence.segment.duration)
    self.playlist_sequences = sequences

    if not self.playlist_changed:
        self.playlist_reload_time = max(self.playlist_reload_time / 2, 1)

    if playlist.is_endlist:
        self.playlist_end = last_sequence.num

    if self.playlist_sequence < 0:
        if self.playlist_end is None and not self.hls_live_restart:
            edge_index = -(min(len(sequences), max(int(self.live_edge), 1)))
            edge_sequence = sequences[edge_index]
            self.playlist_sequence = edge_sequence.num
        else:
            self.playlist_sequence = first_sequence.num


class MyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    """
    Serves a HEAD request
    """
    def do_HEAD(self):
        self.answer_request(0)

    """
    Serves a GET request.
    """
    def do_GET(self):
        self.answer_request(1)

    def answer_request(self, sendData):
        try:

            request_path =  self.path[1:]
            parsed_path = urlparse.urlparse(self.path)
            path =  parsed_path.path[1:]
            try:
                params = dict(urlparse.parse_qsl(parsed_path.query))
            except:
                self.send_response(404)
                self.end_headers()
                self.wfile.write('URL malformed or stream not found!')
                return
            
            if request_path == "version":
                self.send_response(200)
                self.end_headers()
                self.wfile.write("StreamLink Proxy: Running\r\n")
                self.wfile.write("Version: 0.1\r\n")
            elif path == "streamlink/":
                #realpath = request_path[11:]
                fURL = params.get('url')
                fURL = base64.urlsafe_b64decode(fURL)
                q = params.get('q', None)
                if not q:
                    q = 'best'         
                self.serveFile(fURL, q, sendData)           
            else:
                self.send_response(404)
                self.end_headers()
        finally:
                return

    """
    Sends the requested file and add additional headers.
    """
    def serveFile(self, fURL, quality, sendData):        

        session = streamlink.session.Streamlink()
        #session.set_loglevel("debug")
        session.set_logoutput(sys.stdout)

        if _dec:
            streamlink.stream.hls.HLSStreamWriter.create_decryptor = create_decryptor
            #streamlink.stream.hls.HLSStreamWriter.write = write
            streamlink.stream.hls.HLSStreamWorker.process_sequences = process_sequences            

        if '|' in fURL:
            sp = fURL.split('|')
            fURL = sp[0]     
            headers = dict(urlparse.parse_qsl(sp[1]))

            session.set_option("http-ssl-verify", False)
            session.set_option("hls-segment-threads", 1)
            session.set_option("hls-segment-timeout", 10)

            try:
                if 'zoomtv' in headers['Referer']:
                    session.set_option("zoom-key", headers['Referer'].split('?')[1])                    
                elif 'zuom' in headers['Referer']:
                    session.set_option("zuom-key", headers['Referer'].split('?')[1])
                elif 'livecamtv' in headers['Referer'] or 'realtimetv' in headers['Referer']: # or 'emty.space' in headers['Referer']:
                    session.set_option("livecam-key", headers['Referer'])
                    headers.pop('Referer')               
                elif 'sawlive' in headers['Referer']:
                    session.set_option("saw-key", headers['Referer'])
                elif 'yoursportsinhd' in headers['Referer']:
                    session.set_option("your-key", headers['Referer'])
                elif 'mamahd' in headers['Referer']:
                    session.set_option("mama-key", headers['Referer'].split('&')[1])
            except:
                pass
            
            session.set_option("http-headers", headers)
            #xbmc.log('JAIROX1: '+str(session.get_option("http-headers"))) 
            


        try:
            streams = session.streams(fURL)            
            self.send_response(200)

        # except NoPluginError:
        #     self.send_response(403)
        #     xbmc.log("Streamlink is unable to handle the URL '{0}'".format(url))
        # except PluginError as err:
        #     xbmc.log('JAIROX: '+str(err)) 
        #     self.send_response(403)
        #     xbmc.log("Plugin error: {0}".format(err))
        except Exception as err:
            xbmc.log('Streamlink Proxy error: '+ str(err.message))
            traceback.print_exc(file=sys.stdout)
            self.send_response(403)
            
        finally:
            self.end_headers()
        
        # if not streams:
        #     self.send_response(404)
        #     self.end_headers()
            #exit("No streams found on URL '{0}'".format(url))

        # Look for specified stream
        # if quality not in streams:
        #     #streamlink.logger.debug("StreamLink Proxy: Unable to find '{0}' stream on URL '{1}'".format(quality, fURL))
        #     self.send_response(404)
        #     self.end_headers()            
            #exit("Unable to find '{0}' stream on URL '{1}'".format(quality, url))       

        if (sendData):
            #xbmc.log('[StreamLink_Proxy] Stream qualities found: %s'%str(streams.keys()))
            #xbmc.log('[StreamLink_Proxy] Stream quality selected: \'%s\''%quality)
            if not streams.get(quality, None):
                quality = 'best'                
                #self.send_response(404)
                #self.end_headers()
                #return
            try:
                with streams[quality].open() as stream:
                    #xbmc.log('[StreamLink_Proxy] Playing stream %s with quality \'%s\''%(streams[quality],quality))
                    buf = 'INIT'
                    while (len(buf) > 0):
                        buf = stream.read(1000 * 1024)
                        self.wfile.write(buf)
            except:
                traceback.print_exc(file=sys.stdout)


class Server(HTTPServer):
    timeout = 5

class ThreadedHTTPServer(ThreadingMixIn, Server):
    """Handle requests in a separate thread."""


HOST_NAME = '127.1.2.3'
PORT_NUMBER = 45678

if __name__ == '__main__':
    sys.stderr = sys.stdout
    server_class = ThreadedHTTPServer
    server_class.allow_reuse_address = True
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    while not xbmc.abortRequested:
        httpd.handle_request()
    httpd.server_close()
