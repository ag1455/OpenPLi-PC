# YWeather Converter
# xml from http://weather.yahooapis.com/forecastrss
# Copyright (c) 2boom 2013-14 (02.03.2014)
# v.1.5-r0
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Console import Console as iConsole
from Tools.Directories import fileExists
from Poll import Poll
import time
import os

# 924938 - Kiev
# 2122265 - Moscow
weather_city = '926934'
time_update = 20
time_update_ms = 3000
#time_update_ms = 30000

class YWeather(Poll, Converter, object):
	city = 0
	country = 1
	direction = 2
	speed = 3
	speed_ms = 4
	humidity = 5
	visibility = 6
	pressure = 7
	pressurenm = 8
	wtext = 9
	temp = 10
	sunrise = 11
	sunset = 12
	geolat = 13
	geolong = 14
	picon = 15
	fdate0 = 16
	fdate1 = 17
	fdate2 = 18
	fdate3 = 19
	fdate4 = 20
	fweekday0 = 21
	fweekday1 = 22
	fweekday2 = 23
	fweekday3 = 24
	fweekday4 = 25
	ftemp0 = 26
	ftemp1 = 27
	ftemp2 = 28
	ftemp3 = 29
	ftemp4 = 30
	ftext0 = 31
	ftext1 = 32
	ftext2 = 33
	ftext3 = 34
	ftext4 = 35
	fpicon0 = 36
	fpicon1 = 37
	fpicon2 = 38
	fpicon3 = 39
	fpicon4 = 40
	ffulldate0 = 41
	ffulldate1 = 42
	ffulldate2 = 43
	ffulldate3 = 44
	ffulldate4 = 45
	fshortdate0 = 46
	fshortdate1 = 47
	fshortdate2 = 48
	fshortdate3 = 49
	fshortdate4 = 50
	city_title = 51
	feels = 52

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		if type == "city":
			self.type = self.city
		elif type == "city_title":
			self.type = self.city_title
		elif type == "country":
			self.type = self.country
		elif type == "direction":
			self.type = self.direction
		elif type == "speed":
			self.type = self.speed
		elif type == "speed_ms":
			self.type = self.speed_ms
		elif type == "humidity":
			self.type = self.humidity
		elif type == "feels":
			self.type = self.feels
		elif type == "visibility":
			self.type = self.visibility
		elif type == "pressure":
			self.type = self.pressure
		elif type == "pressurenm":
			self.type = self.pressurenm
		elif type == "text":
			self.type = self.wtext
		elif type == "temp":
			self.type = self.temp
		elif type == "sunrise":
			self.type = self.sunrise
		elif type == "sunset":
			self.type = self.sunset
		elif type == "geolat":
			self.type = self.geolat
		elif type == "geolong":
			self.type = self.geolong
		elif type == "picon":
			self.type = self.picon
		elif type == "fdate0":
			self.type = self.fdate0
		elif type == "fdate1":
			self.type = self.fdate1
		elif type == "fdate2":
			self.type = self.fdate2
		elif type == "fdate3":
			self.type = self.fdate3
		elif type == "fdate4":
			self.type = self.fdate4
		elif type == "fweekday0":
			self.type = self.fweekday0
		elif type == "fweekday1":
			self.type = self.fweekday1
		elif type == "fweekday2":
			self.type = self.fweekday2
		elif type == "fweekday3":
			self.type = self.fweekday3
		elif type == "fweekday4":
			self.type = self.fweekday4
		elif type == "ffulldate0":
			self.type = self.ffulldate0
		elif type == "ffulldate1":
			self.type = self.ffulldate1
		elif type == "ffulldate2":
			self.type = self.ffulldate2
		elif type == "ffulldate3":
			self.type = self.ffulldate3
		elif type == "ffulldate4":
			self.type = self.ffulldate4
		elif type == "ftemp0":
			self.type = self.ftemp0
		elif type == "ftemp1":
			self.type = self.ftemp1
		elif type == "ftemp2":
			self.type = self.ftemp2
		elif type == "ftemp3":
			self.type = self.ftemp3
		elif type == "ftemp4":
			self.type = self.ftemp4
		elif type == "ftext0":
			self.type = self.ftext0
		elif type == "ftext1":
			self.type = self.ftext1
		elif type == "ftext2":
			self.type = self.ftext2
		elif type == "ftext3":
			self.type = self.ftext3
		elif type == "ftext4":
			self.type = self.ftext4
		elif type == "fpicon0":
			self.type = self.fpicon0
		elif type == "fpicon1":
			self.type = self.fpicon1
		elif type == "fpicon2":
			self.type = self.fpicon2
		elif type == "fpicon3":
			self.type = self.fpicon3
		elif type == "fpicon4":
			self.type = self.fpicon4
		elif type == "fshortdate0":
			self.type = self.fshortdate0
		elif type == "fshortdate1":
			self.type = self.fshortdate1
		elif type == "fshortdate2":
			self.type = self.fshortdate2
		elif type == "fshortdate3":
			self.type = self.fshortdate3
		elif type == "fshortdate4":
			self.type = self.fshortdate4
		self.iConsole = iConsole()
		self.poll_interval = time_update_ms
		self.poll_enabled = True

	def write_none(self):
		self.iConsole.ePopen("echo -e 'None' >> /tmp/yweather.xml")

	def get_xmlfile(self):
		self.iConsole.ePopen("wget -P /tmp -T2 'http://weather.yahooapis.com/forecastrss?w=%s&u=c' -O /tmp/yweather.xml" % weather_city, self.control_xml)

	def control_xml(self, result, retval, extra_args):
		if retval is not 0:
			self.write_none()

	@cached
	def getText(self):
		fweather, tweather = [], []
		xweather = {'ycity':"N/A", 'feels':"N/A", 'ycountry':"N/A", 'ydirection':"N/A", 'yspeed':"N/A", 'yhumidity':"N/A", 'yvisibility':"N/A", 'ypressure':"N/A", 'ytext':"N/A",\
			'ytemp':"N/A", 'ysunrise':"N/A", 'ysunset':"N/A", 'ypicon':"3200", 'ylat':"N/A", 'ylong':"N/A", 'ymetric':"N/A"}
		direct = 0
		info, finfo1, finfo2 = '', '', ''
		if fileExists("/tmp/yweather.xml"):
			if int((time.time() - os.stat("/tmp/yweather.xml").st_mtime)/60) >= time_update:
				self.get_xmlfile()
		else:
			self.get_xmlfile()
			if not fileExists("/tmp/yweather.xml"):
				self.write_none()
				return 'N/A'
		if not fileExists("/tmp/yweather.xml"):
			self.write_none()
			return 'N/A'
		for line in open("/tmp/yweather.xml"):
			if "<yweather:location" in line:
				xweather['ycity'] = line.split('city')[1].split('"')[1]
				xweather['ycountry'] = line.split('country')[1].split('"')[1]
			elif "</title>" in line:
				tweather.append(line)
			elif "<yweather:units" in line:
				xweather['ymetric'] = line.split('temperature')[1].split('"')[1]
			elif "<yweather:wind" in line:
				xweather['feels'] = line.split('chill')[1].split('"')[1]
				xweather['ydirection'] = line.split('direction')[1].split('"')[1]
				xweather['yspeed'] = line.split('speed')[1].split('"')[1]
			elif "<yweather:atmosphere" in line:
				xweather['yhumidity'] = line.split('humidity')[1].split('"')[1]
				xweather['yvisibility'] = line.split('visibility')[1].split('"')[1]
				xweather['ypressure'] = line.split('pressure')[1].split('"')[1]
			elif "<yweather:condition" in line:
				xweather['ytext'] = line.split('text')[1].split('"')[1]
				xweather['ypicon'] = line.split('code')[1].split('"')[1]
				xweather['ytemp'] = line.split('temp')[1].split('"')[1]
			elif "<yweather:astronomy" in line:
				xweather['ysunrise'] = line.split('"')[1].split()[0]
				xweather['ysunset'] = line.split('"')[-2].split()[0]
			elif "<geo:lat" in line:
				xweather['ylat'] = line.split('<')[1].split('>')[1]
			elif "<geo:long" in line:
				xweather['ylong'] = line.split('<')[1].split('>')[1]
			elif "<yweather:forecast" in line:
				fweather.append(line.split('<yweather:forecast')[-1].split('/>')[0].strip())

		if self.type == self.city:
			info = xweather['ycity']
		elif self.type == self.city_title:
			if len(tweather) > 0:
				info = tweather[0].split('<')[-2].split(' - ')[-1]
			else:
				info = "N/A"
		elif self.type == self.country:
			info = xweather['ycountry']
		elif self.type == self.direction:
			if not xweather['ydirection'] is 'N/A':
				direct = int(xweather['ydirection'])
				if direct >= 0 and direct <= 20:
					info = _('N')
				elif direct >= 21 and direct <= 35:
					info = _('NNE')
				elif direct >= 36 and direct <= 55:
					info = _('NE')
				elif direct >= 56 and direct <= 70:
					info = _('ENE')
				elif direct >= 71 and direct <= 110:
					info = _('E')
				elif direct >= 111 and direct <= 125:
					info = _('ESE')
				elif direct >= 126 and direct <= 145:
					info = _('SE')
				elif direct >= 146 and direct <= 160:
					info = _('SSE')
				elif direct >= 161 and direct <= 200:
					info = _('S')
				elif direct >= 201 and direct <= 215:
					info = _('SSW')
				elif direct >= 216 and direct <= 235:
					info = _('SW')
				elif direct >= 236 and direct <= 250:
					info = _('WSW')
				elif direct >= 251 and direct <= 290:
					info = _('W')
				elif direct >= 291 and direct <= 305:
					info = _('WNW')
				elif direct >= 306 and direct <= 325:
					info = _('NW')
				elif direct >= 326 and direct <= 340:
					info = _('NNW')
				elif direct >= 341 and direct <= 360:
					info = _('N')
				else:
					info = _('N/A')
		elif self.type == self.speed:
			info = xweather['yspeed'] + _(' km/h')
		elif self.type == self.geolat:
			info = xweather['ylat']
		elif self.type == self.geolong:
			info = xweather['ylong']
		elif self.type == self.sunrise:
			if not xweather['ysunrise'] is 'N/A':
				info = '%.02d:%s' % (int(xweather['ysunrise'].split(':')[0]), xweather['ysunrise'].split(':')[-1])
			else:
				info = "N/A"
		elif self.type == self.sunset:
			if not xweather['ysunset'] is 'N/A':
				info = '%s:%s' % (int(xweather['ysunset'].split(':')[0]) + 12, xweather['ysunset'].split(':')[1])
			else:
				info = "N/A"
		elif self.type == self.speed_ms:
			if not xweather['yspeed'] is 'N/A':
				speed = (float(xweather['yspeed']) * 1000)/3600
				info = _('%3.02f m/s') % speed
			else:
				info = "N/A"
		elif self.type == self.humidity:
			info = xweather['yhumidity'] + '%'
		elif self.type == self.visibility:
			info = _('%s km') % xweather['yvisibility']
		elif self.type == self.pressure:
			info = _('%s mb') % xweather['ypressure']
		elif self.type == self.pressurenm:
			if not xweather['ypressure'] is "N/A":
				tmp_round = round(float(xweather['ypressure']) * 0.75)
				info = _("%d mmHg") % tmp_round
			else:
				info = "N/A"
		elif self.type == self.wtext:
			info = xweather['ytext']
		elif self.type == self.feels:
			if not info is "N/A":
				if not xweather['feels'][0] is '-' and not xweather['feels'][0] is '0':
					info = '+' + xweather['feels'] + '%s' % unichr(176).encode("latin-1") + xweather['ymetric']
				else:
					info = xweather['feels'] + '%s' % unichr(176).encode("latin-1") + xweather['ymetric']
			else:
				info = xweather['feels']
		elif self.type == self.temp:
			if not info is "N/A":
				if not xweather['ytemp'][0] is '-' and not xweather['ytemp'][0] is '0':
					info = '+' + xweather['ytemp'] + '%s' % unichr(176).encode("latin-1") + xweather['ymetric']
				else:
					info = xweather['ytemp'] + '%s' % unichr(176).encode("latin-1") + xweather['ymetric']
			else:
				info = xweather['ytemp']
		elif self.type == self.picon:
			info = xweather['ypicon']
#####################################################
		elif self.type == self.fdate0:
			if len(fweather) >= 1:
				info = fweather[0].split('"')[3].split()[0]
			else:
				info = "N/A"
		elif self.type == self.fweekday0:
			if len(fweather) >= 1:
				info = _('%s') % fweather[0].split('"')[1]
			else:
				info = "N/A"
######################################################
		elif self.type == self.fdate1:
			if len(fweather) >= 2:
				info = fweather[1].split('"')[3].split()[0]
			else:
				info = "N/A"
		elif self.type == self.fweekday1:
			if len(fweather) >= 2:
				info = _('%s') % fweather[1].split('"')[1]
			else:
				info = "N/A"
#########################################################
		elif self.type == self.fdate2:
			if len(fweather) >= 3:
				info = fweather[2].split('"')[3].split()[0]
			else:
				info = "N/A"
		elif self.type == self.fweekday2:
			if len(fweather) >= 3:
				info = _('%s') % fweather[2].split('"')[1]
			else:
				info = "N/A"
#########################################################
		elif self.type == self.fdate3:
			if len(fweather) >= 4:
				info = fweather[3].split('"')[3].split()[0]
			else:
				info = "N/A"
		elif self.type == self.fweekday3:
			if len(fweather) >= 4:
				info = _('%s') % fweather[3].split('"')[1]
			else:
				info = "N/A"
#########################################################
		elif self.type == self.fdate4:
			if len(fweather) >= 5:
				info = fweather[4].split('"')[3].split()[0]
			else:
				info = "N/A"
		elif self.type == self.fweekday4:
			if len(fweather) >= 5:
				info = _('%s') % fweather[4].split('"')[1]
			else:
				info = "N/A"
#########################################################
		elif self.type == self.ftemp0:
			if len(fweather) >= 1:
				if not fweather[0].split('"')[5][0] is '-' and not fweather[0].split('"')[5][0] is '0':
					finfo1 = '+' + fweather[0].split('"')[5] + '%s' % unichr(176).encode("latin-1")
				else:
					finfo1 = fweather[0].split('"')[5] + '%s' % unichr(176).encode("latin-1")
				if not fweather[0].split('"')[7][0] is '-' and not fweather[0].split('"')[7][0] is '0':
					finfo2 = '+' + fweather[0].split('"')[7] + '%s' % unichr(176).encode("latin-1")
				else:
					finfo2 = fweather[0].split('"')[7] + '%s' % unichr(176).encode("latin-1")
				info = '%s / %s' % (finfo1,finfo2)
			else:
				info = "N/A"
		elif self.type == self.ftemp1:
			if len(fweather) >= 2:
				if not fweather[1].split('"')[5][0] is '-' and not fweather[1].split('"')[5][0] is '0':
					finfo1 = '+' + fweather[1].split('"')[5] + '%s' % unichr(176).encode("latin-1")
				else:
					finfo1 = fweather[1].split('"')[5] + '%s' % unichr(176).encode("latin-1")
				if not fweather[1].split('"')[7][0] is '-' and not fweather[1].split('"')[7][0] is '0':
					finfo2 = '+' + fweather[1].split('"')[7] + '%s' % unichr(176).encode("latin-1")
				else:
					finfo2 = fweather[1].split('"')[7] + '%s' % unichr(176).encode("latin-1")
				info = '%s / %s' % (finfo1,finfo2)
			else:
				info = "N/A"
		elif self.type == self.ftemp2:
			if len(fweather) >= 3:
				if not fweather[2].split('"')[5][0] is '-' and not fweather[2].split('"')[5][0] is '0':
					finfo1 = '+' + fweather[2].split('"')[5] + '%s' % unichr(176).encode("latin-1")
				else:
					finfo1 = fweather[2].split('"')[5] + '%s' % unichr(176).encode("latin-1")
				if not fweather[2].split('"')[7][0] is '-' and not fweather[2].split('"')[7][0] is '0':
					finfo2 = '+' + fweather[2].split('"')[7] + '%s' % unichr(176).encode("latin-1")
				else:
					finfo2 = fweather[2].split('"')[7] + '%s' % unichr(176).encode("latin-1")
				info = '%s / %s' % (finfo1,finfo2)
			else:
				info = "N/A"
		elif self.type == self.ftemp3:
			if len(fweather) >= 4:
				if not fweather[3].split('"')[5][0] is '-' and not fweather[3].split('"')[5][0] is '0':
					finfo1 = '+' + fweather[3].split('"')[5] + '%s' % unichr(176).encode("latin-1")
				else:
					finfo1 = fweather[3].split('"')[5] + '%s' % unichr(176).encode("latin-1")
				if not fweather[3].split('"')[7][0] is '-' and not fweather[3].split('"')[7][0] is '0':
					finfo2 = '+' + fweather[3].split('"')[7] + '%s' % unichr(176).encode("latin-1")
				else:
					finfo2 = fweather[3].split('"')[7] + '%s' % unichr(176).encode("latin-1")
				info = '%s / %s' % (finfo1,finfo2)
			else:
				info = "N/A"
		elif self.type == self.ftemp4:
			if len(fweather) >= 5:
				if not fweather[4].split('"')[5][0] is '-' and not fweather[4].split('"')[5][0] is '0':
					finfo1 = '+' + fweather[4].split('"')[5] + '%s' % unichr(176).encode("latin-1")
				else:
					finfo1 = fweather[4].split('"')[5] + '%s' % unichr(176).encode("latin-1")
				if not fweather[4].split('"')[7][0] is '-' and not fweather[4].split('"')[7][0] is '0':
					finfo2 = '+' + fweather[4].split('"')[7] + '%s' % unichr(176).encode("latin-1")
				else:
					finfo2 = fweather[4].split('"')[7] + '%s' % unichr(176).encode("latin-1")
				info = '%s / %s' % (finfo1,finfo2)
			else:
				info = "N/A"
		elif self.type == self.ftext0:
			if len(fweather) >= 1:
				info = _('%s') % fweather[0].split('"')[9]
			else:
				info = "N/A"
		elif self.type == self.ftext1:
			if len(fweather) >= 2:
				info = _('%s') % fweather[1].split('"')[9]
			else:
				info = "N/A"
		elif self.type == self.ftext2:
			if len(fweather) >= 3:
				info = _('%s') % fweather[2].split('"')[9]
			else:
				info = "N/A"
		elif self.type == self.ftext3:
			if len(fweather) >= 4:
				info = _('%s') % fweather[3].split('"')[9]
			else:
				info = "N/A"
		elif self.type == self.ftext4:
			if len(fweather) >= 5:
				info = _('%s') % fweather[4].split('"')[9]
			else:
				info = "N/A"
		elif self.type == self.fpicon0:
			if len(fweather) >= 1:
				info = fweather[0].split('"')[-2]
			else:
				info = "3200"
		elif self.type == self.fpicon1:
			if len(fweather) >= 2:
				info = fweather[1].split('"')[-2]
			else:
				info = "3200"
		elif self.type == self.fpicon2:
			if len(fweather) >= 3:
				info = fweather[2].split('"')[-2]
			else:
				info = "3200"
		elif self.type == self.fpicon3:
			if len(fweather) >= 4:
				info = fweather[3].split('"')[-2]
			else:
				info = "3200"
		elif self.type == self.fpicon4:
			if len(fweather) >= 5:
				info = fweather[4].split('"')[-2]
			else:
				info = "3200"
		elif self.type == self.ffulldate0:
			if len(fweather) >= 1:
				finfo1 = fweather[0].split('"')[3].replace('Jan','.01.').replace('Feb','.02.').replace('Mar','.03.')\
					.replace('Apr','.04.').replace('May','.05.').replace('Jun','.06.').replace('Jul','.07.')\
					.replace('Aug','.08.').replace('Sep','.09.').replace('Oct','.10.').replace('Nov','.11.')\
					.replace('Dec','.12.').replace(' ','')
				if len(finfo1) == 10:
					info = finfo1
				else:
					info = '0%s' % finfo1
			else:
				info = "N/A"
		elif self.type == self.ffulldate1:
			if len(fweather) >= 2:
				finfo1 = fweather[1].split('"')[3].replace('Jan','.01.').replace('Feb','.02.').replace('Mar','.03.')\
					.replace('Apr','.04.').replace('May','.05.').replace('Jun','.06.').replace('Jul','.07.')\
					.replace('Aug','.08.').replace('Sep','.09.').replace('Oct','.10.').replace('Nov','.11.')\
					.replace('Dec','.12.').replace(' ','')
				if len(finfo1) == 10:
					info = finfo1
				else:
					info = '0%s' % finfo1
			else:
				info = "N/A"
		elif self.type == self.ffulldate2:
			if len(fweather) >= 3:
				finfo1 = fweather[2].split('"')[3].replace('Jan','.01.').replace('Feb','.02.').replace('Mar','.03.')\
					.replace('Apr','.04.').replace('May','.05.').replace('Jun','.06.').replace('Jul','.07.')\
					.replace('Aug','.08.').replace('Sep','.09.').replace('Oct','.10.').replace('Nov','.11.')\
					.replace('Dec','.12.').replace(' ','')
				if len(finfo1) == 10:
					info = finfo1
				else:
					info = '0%s' % finfo1
			else:
				info = "N/A"
		elif self.type == self.ffulldate3:
			if len(fweather) >= 4:
				finfo1 = fweather[3].split('"')[3].replace('Jan','.01.').replace('Feb','.02.').replace('Mar','.03.')\
					.replace('Apr','.04.').replace('May','.05.').replace('Jun','.06.').replace('Jul','.07.')\
					.replace('Aug','.08.').replace('Sep','.09.').replace('Oct','.10.').replace('Nov','.11.')\
					.replace('Dec','.12.').replace(' ','')
				if len(finfo1) == 10:
					info = finfo1
				else:
					info = '0%s' % finfo1
			else:
				info = "N/A"
		elif self.type == self.ffulldate4:
			if len(fweather) >= 5:
				finfo1 = fweather[4].split('"')[3].replace('Jan','.01.').replace('Feb','.02.').replace('Mar','.03.')\
					.replace('Apr','.04.').replace('May','.05.').replace('Jun','.06.').replace('Jul','.07.')\
					.replace('Aug','.08.').replace('Sep','.09.').replace('Oct','.10.').replace('Nov','.11.')\
					.replace('Dec','.12.').replace(' ','')
				if len(finfo1) == 10:
					info = finfo1
				else:
					info = '0%s' % finfo1
			else:
				info = "N/A"

#####################################################
		elif self.type == self.fshortdate0:
			if len(fweather) >= 1:
				info = fweather[0].split('"')[1] + ' ' + fweather[0].split('"')[3].split()[0]
			else:
				info = "N/A"
		elif self.type == self.fshortdate1:
			if len(fweather) >= 2:
				info = fweather[1].split('"')[1] + ' ' + fweather[1].split('"')[3].split()[0]
			else:
				info = "N/A"
		elif self.type == self.fshortdate2:
			if len(fweather) >= 3:
				info = fweather[2].split('"')[1] + ' ' + fweather[2].split('"')[3].split()[0]
			else:
				info = "N/A"
		elif self.type == self.fshortdate3:
			if len(fweather) >= 4:
				info = fweather[3].split('"')[1] + ' ' + fweather[3].split('"')[3].split()[0]
			else:
				info = "N/A"
		elif self.type == self.fshortdate4:
			if len(fweather) >= 5:
				info = fweather[4].split('"')[1] + ' ' + fweather[4].split('"')[3].split()[0]
			else:
				info = "N/A"
		return info
######################################################
	text = property(getText)

	def changed(self, what):
		Converter.changed(self, (self.CHANGED_POLL,))
