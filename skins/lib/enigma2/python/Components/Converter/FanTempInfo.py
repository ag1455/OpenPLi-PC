# FanTempInfo Converter  v.0.3
# Copyright (c) 2boom 2012-14
# v.0.3-r0
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

from Poll import Poll
from Components.Converter.Converter import Converter
from Components.Element import cached
from Tools.Directories import fileExists

class FanTempInfo(Poll, Converter, object):
	FanInfo = 0
	TempInfo = 1

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		if type == "FanInfo":
			self.type = self.FanInfo
		elif type == "TempInfo":
			self.type = self.TempInfo
		self.poll_interval = 2000
		self.poll_enabled = True

	@cached

	def getText(self):
		info = 'N/A'
		if self.type == self.FanInfo:
			if fileExists("/usr/local/e2/etc/stb/fp/fan_speed"):
				info = open("/usr/local/e2/etc/stb/fp/fan_speed").read().strip('\n')
		elif self.type == self.TempInfo:
			if fileExists("/usr/local/e2/etc/stb/sensors/temp0/value") and fileExists("/usr/local/e2/etc/stb/sensors/temp0/unit"):
				info = "%s%s%s" % (open("/usr/local/e2/etc/stb/sensors/temp0/value").read().strip('\n'), unichr(176).encode("latin-1"), open("/usr/local/e2/etc/stb/sensors/temp0/unit").read().strip('\n'))
		return info

	text = property(getText)

	def changed(self, what):
		if what[0] == self.CHANGED_POLL:
			self.downstream_elements.changed(what)
