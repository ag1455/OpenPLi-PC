from Converter import Converter
from time import localtime, strftime
from Components.Element import cached

MONTHS = (_("January"),
          _("February"),
          _("March"),
          _("April"),
          _("May"),
          _("June"),
          _("July"),
          _("August"),
          _("September"),
          _("October"),
          _("November"),
          _("December"))

shortMONTHS = (_("Jan"),
               _("Feb"),
               _("Mar"),
               _("Apr"),
               _("May"),
               _("Jun"),
               _("Jul"),
               _("Aug"),
               _("Sep"),
               _("Oct"),
               _("Nov"),
               _("Dec"))

DAYWEEK = (_("Monday"),
           _("Tuesday"),
           _("Wednesday"),
           _("Thursday"),
           _("Friday"),
           _("Saturday"),
           _("Sunday"))

shortDAYWEEK = (_("Mon"),
                _("Tue"),
                _("Wed"),
                _("Thu"),
                _("Fri"),
                _("Sat"),
                _("Sun"))

class TuxClockToText(Converter, object):
	DEFAULT = 0
	WITH_SECONDS = 1
	IN_MINUTES = 2
	DATE = 3
	FORMAT = 4
	AS_LENGTH = 5
	TIMESTAMP = 6


	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "WithSeconds":
			self.type = self.WITH_SECONDS
		elif type == "InMinutes":
			self.type = self.IN_MINUTES
		elif type == "Date":
			self.type = self.DATE
		elif type == "AsLength":
			self.type = self.AS_LENGTH
		elif type == "Timestamp":
			self.type = self.TIMESTAMP
		elif str(type).find("Format") != -1:
			self.type = self.FORMAT
			self.fmt_string = type[7:]
		else:
			self.type = self.DEFAULT

	@cached
	def getText(self):
		time = self.source.time
		if time is None:
			return ""

		if self.type == self.IN_MINUTES:
			return "%d min" % (time / 60)
		elif self.type == self.AS_LENGTH:
			return "%d:%02d" % (time / 60, time % 60)
		elif self.type == self.TIMESTAMP:
			return str(time)

		t = localtime(time)

		if self.type == self.WITH_SECONDS:
			return "%2d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)
		elif self.type == self.DEFAULT:
			return "%2d:%02d" % (t.tm_hour, t.tm_min)
		elif self.type == self.DATE:
			return _(strftime("%A",t)) + " " + str(t[2]) + " " + MONTHS[t[1]-1] + " " + str(t[0])
		elif self.type == self.FORMAT:
			spos = self.fmt_string.find('%')
			self.fmt_string = self.fmt_string.replace('%A',_(DAYWEEK[t.tm_wday]))
		        self.fmt_string = self.fmt_string.replace('%B',_(MONTHS[t.tm_mon-1]))
		        self.fmt_string = self.fmt_string.replace('%a',_(shortDAYWEEK[t.tm_wday]))
		        self.fmt_string = self.fmt_string.replace('%b',_(shortMONTHS[t.tm_mon-1]))
			if spos > 0:
				s1 = self.fmt_string[:spos]
				s2 = strftime(self.fmt_string[spos:], t)
				return str(s1+s2)
			else:
				return strftime(self.fmt_string, t)

		else:
			return "???"

	text = property(getText)
