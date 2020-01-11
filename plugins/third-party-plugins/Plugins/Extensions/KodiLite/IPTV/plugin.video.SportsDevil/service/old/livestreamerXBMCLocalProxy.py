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
import urlparse
import sys
import socket
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

import struct
import livestreamer
from livestreamer.exceptions import StreamError
from urlparse import urljoin

##aes stuff
_android_ssl = False
_oscrypto = False
CAN_DECRYPT = True
try:
    from Crypto.Cipher import AES
except ImportError:
    try:
        from Cryptodome.Cipher import AES
    except ImportError:
        try:
            import androidsslPy
            enc = androidsslPy._load_crypto_libcrypto()
            _android_ssl = True
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
            except:
                CAN_DECRYPT = False

def num_to_iv(n):
    return struct.pack(">8xq", n)

def create_decryptor(self, key, sequence):
    if key.method != "AES-128":
        raise StreamError("Unable to decrypt cipher {0}", key.method)

    if not key.uri:
        raise StreamError("Missing URI to decryption key")

    if self.key_uri != key.uri:
        zoom_key = self.reader.stream.session.options.get("zoom-key")
        saw_key = self.reader.stream.session.options.get("saw-key")
        your_key = self.reader.stream.session.options.get("your-key")

        if zoom_key:
            uri = 'http://www.zoomtv.me/k.php?q='+base64.urlsafe_b64encode(zoom_key+base64.urlsafe_b64encode(key.uri))
        elif saw_key:
            if 'foxsportsgo' in key.uri:
                _tmp = key.uri.split('/')
                uri = urljoin(saw_key,'/m/fream?p='+_tmp[-4]+'&k='+_tmp[-1])
            elif 'nlsk.neulion' in key.uri:
                _tmp = key.uri.split('?')
                uri = urljoin(saw_key,'/m/stream?'+_tmp[-1])
            elif 'nhl.com' in key.uri:
                _tmp = key.uri.split('/')
                uri = urljoin(saw_key,'/m/streams?ci='+_tmp[-3]+'&k='+_tmp[-1])
        
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
                                    **self.reader.request_params)
        self.key_data = res.content
        self.key_uri = key.uri

    iv = key.iv or num_to_iv(sequence)
    if _android_ssl:
        return enc(self.key_data, iv)
    elif _oscrypto:
        return AES(self.key_data, iv)
    else:
        return AES.new(self.key_data, AES.MODE_CBC, iv)

def process_sequences(self, playlist, sequences):
    first_sequence, last_sequence = sequences[0], sequences[-1]

    if first_sequence.segment.key and first_sequence.segment.key.method != "NONE":
        self.logger.debug("Segments in this playlist are encrypted")
    
        if not CAN_DECRYPT:
            raise StreamError("No crypto lib installed to decrypt this stream")

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
        if self.playlist_end is None:
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
            request_path = self.path[1:]
            if request_path == "stop":
                sys.exit()
            elif request_path == "version":
                self.send_response(200)
                self.end_headers()
                self.wfile.write("Proxy: Running\r\n")
                self.wfile.write("Version: 0.1\r\n")
            elif request_path[0:13] == "livestreamer/":
                realpath = request_path[13:]
                fURL = base64.urlsafe_b64decode(realpath)
                self.serveFile(fURL, sendData)
            else:
                self.send_response(403)
                self.end_headers()
        finally:
                return

    """
    Sends the requested file and add additional headers.
    """
    def serveFile(self, fURL, sendData):
        session = livestreamer.session.Livestreamer()
        #session.set_loglevel('debug')
        livestreamer.stream.hls.HLSStreamWriter.create_decryptor = create_decryptor
        livestreamer.stream.hls.HLSStreamWorker.process_sequences = process_sequences

        if '|' in fURL:
                sp = fURL.split('|')
                fURL = sp[0]
                headers = dict(urlparse.parse_qsl(sp[1]))                
                session.set_option("http-headers", headers)
                session.set_option("http-ssl-verify", False)
                session.set_option("hls-segment-threads", 1)
                if 'zoomtv' in headers['Referer']:
                    session.set_option("zoom-key", headers['Referer'].split('?')[1])
                elif 'sawlive' in headers['Referer']:
                    session.set_option("saw-key", headers['Referer'])
                elif 'yoursportsinhd' in headers['Referer']:
                    session.set_option("your-key", headers['Referer'])
                
        try:
            streams = session.streams(fURL)
            self.send_response(200)
        except:
            self.send_response(403)
        finally:
            self.end_headers()

        if (sendData):
            with streams["best"].open() as stream:
                buf = 'INIT'
                while (len(buf) > 0):
                    buf = stream.read(1000 * 1024)
                    self.wfile.write(buf)


class Server(HTTPServer):
    """HTTPServer class with timeout."""
    timeout = 5
    # def get_request(self):
    #     """Get the request and client address from the socket."""
    #     self.socket.settimeout(2.0)
    #     result = None
    #     while result is None:
    #         try:
    #             result = self.socket.accept()
    #         except socket.timeout:
    #             pass
    #     result[0].settimeout(1000)
    #     return result


class ThreadedHTTPServer(ThreadingMixIn, Server):
    """Handle requests in a separate thread."""


#HOST_NAME = '127.1.2.3'
#PORT_NUMBER = 45678
HOST_NAME = '127.0.0.1'
PORT_NUMBER = 19000
if __name__ == '__main__':
    sys.stderr = sys.stdout
    server_class = ThreadedHTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    while not xbmc.abortRequested:
        httpd.handle_request()
    httpd.server_close()
    httpd.stopped = True