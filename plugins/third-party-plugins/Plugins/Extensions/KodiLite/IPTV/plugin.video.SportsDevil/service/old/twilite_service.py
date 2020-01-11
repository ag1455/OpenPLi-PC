# -*- coding: utf-8 -*-

"""
    ---
    Modified for Streamlink
    https://github.com/Twilight0/service.streamlink.proxy
    ---

    Based on beardypig's local proxy service script
    https://github.com/beardypig/plugin.video.streamlink/blob/master/service.py

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

import SocketServer
import os, sys
import shutil
import threading
import urlparse
import streamlink
import xbmc
import xbmcaddon
from streamlink.stream import HTTPStream, HLSStream
from SimpleHTTPServer import SimpleHTTPRequestHandler

addon = xbmcaddon.Addon()
setting = addon.getSetting

port = '45678' #setting('listen_port')
host = '127.1.2.3'


try:
    streamlink_plugins = os.path.join('script.module.streamlink.plugins', 'plugins')
except:
    pass

path_streamlink_service = os.path.join('service.streamlink.proxy', 'resources', 'lib')

kodi_folder = os.path.dirname(os.path.realpath(__file__))

try:
    # noinspection PyUnboundLocalVariable
    custom_plugins = kodi_folder.replace(path_streamlink_service, streamlink_plugins)
except:
    pass


class ProxyHandler(SimpleHTTPRequestHandler):

    def do_GET(self):

        p = urlparse.urlparse(self.path)

        try:
            params = dict(urlparse.parse_qsl(p.query))
        except:
            params = {}

        xbmc.log(repr(params))

        if params == {}:

            xbmc.log("stream not found")
            self.send_error(404, "Invalid stream")
            return

        else:

            session = streamlink.Streamlink()
            #session.set_loglevel("debug")
            #session.set_logoutput(sys.stdout)

            try:
                session.load_plugins(custom_plugins)
            except:
                pass

            url = params.get('url')
            quality = params.get('q', None)
            if not quality:
                quality = 'best'

            streams = session.streams(url)
            stream = streams.get(quality)

            # ZATTOO:
            if url.startswith(('https://zattoo.com', 'https://tvonline.ewe.de', 'https://nettv.netcologne.de')):
                plugin_email = setting('zattoo_email')
                plugin_password = setting('zattoo_password')

                if plugin_email and plugin_password:
                    xbmc.log('Found Zattoo login')
                    session.set_plugin_option('zattoo', 'email', plugin_email)
                    session.set_plugin_option('zattoo', 'password', plugin_password)
                else:
                    xbmc.log('Missing Zattoo login')

            if not stream:

                xbmc.log("No stream resolved")
                self.send_error(404, "Stream not found")
                return

            elif isinstance(stream, HLSStream):

                res = session.http.get(stream.url)

                self.send_response(res.status_code, res.reason)
                self.send_header("content-type", res.headers.get('content-type', 'text'))
                self.end_headers()

                for line in res.text.splitlines(False):
                    if line and not line.startswith('#'):
                        self.wfile.write(urlparse.urljoin(stream.url, line) + '\n')
                    else:
                        self.wfile.write(line + '\n')
                return

            elif isinstance(stream, HTTPStream):
                res = session.http.get(stream.url, headers=self.headers)

                self.send_response(res.status_code, res.reason)
                for name, value in res.headers.items():
                    self.send_header(name, value)
                self.end_headers()
            else:
                self.send_response(200, "OK")
                self.end_headers()

            # return the stream
            fh = None
            try:
                fh = stream.open()
                shutil.copyfileobj(fh, self.wfile)
            finally:
                if fh:
                    fh.close()


if __name__ == "__main__":

    server = SocketServer.TCPServer((host, int(port)), ProxyHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

    monitor = xbmc.Monitor()

    while not monitor.waitForAbort(1):
        pass

    server.shutdown()
    server_thread.join()