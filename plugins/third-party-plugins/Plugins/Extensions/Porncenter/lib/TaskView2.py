from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.config import ConfigSubsection, ConfigSelection, getConfigListEntry
from Components.SystemInfo import SystemInfo
from Components.Task import job_manager
from Screens.InfoBarGenerics import InfoBarNotifications
import Screens.Standby
from Tools import Notifications
from Components.Pixmap import Pixmap

THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiDirect"

class JobViewNew(InfoBarNotifications, Screen, ConfigListScreen):
        skin = """
    <screen position="center,center" size="1280,720" title="  " >
    <!--ePixmap position="0,0" zPosition="-2" size="1280,720" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/skin/images/panel3.png" /-->
    <widget name="pixmap" position="942,372" size="200,200" zPosition="1" alphatest="on" />

		<widget source="job_name" render="Label" position="100,100" size="480,100" font="Regular;28" backgroundColor="#40000000" />
		<!--widget source="job_task" render="Label" position="100,150" size="480,50" font="Regular;23" backgroundColor="#40000000" /-->
		<widget source="job_progress" render="Progress" position="140,250" size="480,36" borderWidth="2" backgroundColor="#40000000" />
		<widget source="job_progress" render="Label" position="100,350" size="280,32" font="Regular;28" backgroundColor="#40000000" zPosition="2" halign="center" transparent="1"  >
			<convert type="ProgressToText" />
		</widget>
		<widget source="job_status" render="Label" position="100,400" size="480,30" font="Regular;23" backgroundColor="#40000000" />
		<widget name="config" position="100,500" size="550,40" foregroundColor="#cccccc" backgroundColor="#40000000" />
	
        
    <eLabel position="150,660" zPosition="1" size="200,30" backgroundColor="#f23d21" /> 
    <eLabel position="152,662" zPosition="1" size="196,26" backgroundColor="#40000000" /> 
    <eLabel position="350,660" zPosition="1" size="200,30" backgroundColor="#389416" />
    <eLabel position="352,662" zPosition="1" size="196,26" backgroundColor="#40000000" />
    <eLabel position="550,660" zPosition="1" size="400,30" backgroundColor="#0064c7" />
    <eLabel position="552,662" zPosition="1" size="396,26" backgroundColor="#40000000" />

    	<widget source="cancelable" render="FixedLabel" text="Cancel" position="150,660" size="200,30" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" > 
			<convert type="ConditionalShowHide" />
	</widget>
	<widget source="finished" render="FixedLabel" text="OK" position="350,660" size="200,30" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" > 
			<convert type="ConditionalShowHide" />
	</widget>
	<widget source="backgroundable" render="FixedLabel" text="Continue in background" position="550,660" size="400,30" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" >
			<convert type="ConditionalShowHide" />
	</widget>    
        
	</screen>"""        
	def __init__(self, session, job, parent=None, cancelable = True, backgroundable = True, afterEventChangeable = True):
		from Components.Sources.StaticText import StaticText
		from Components.Sources.Progress import Progress
		from Components.Sources.Boolean import Boolean
		from Components.ActionMap import ActionMap
		Screen.__init__(self, session, parent)
		InfoBarNotifications.__init__(self)
		ConfigListScreen.__init__(self, [])
		self.parent = parent
		self.job = job
                self["pixmap"] = Pixmap()
		self["job_name"] = StaticText(job.name)
		self["job_progress"] = Progress()
		self["job_task"] = StaticText()
		self["summary_job_name"] = StaticText(job.name)
		self["summary_job_progress"] = Progress()
		self["summary_job_task"] = StaticText()
		self["job_status"] = StaticText()
		self["finished"] = Boolean()
		self["cancelable"] = Boolean(cancelable)
		self["backgroundable"] = Boolean(backgroundable)

		self["key_blue"] = StaticText(_("Background"))

		self.onShow.append(self.windowShow)
		self.onHide.append(self.windowHide)

		self["setupActions"] = ActionMap(["ColorActions", "SetupActions"],
		{
		    "green": self.ok,
		    "red": self.abort,
		    "blue": self.background,
		    "cancel": self.ok,
		    "ok": self.ok,
		}, -2)

		self.settings = ConfigSubsection()
		if SystemInfo["DeepstandbySupport"]:
			shutdownString = _("go to standby")
		else:
			shutdownString = _("shut down")
		self.settings.afterEvent = ConfigSelection(choices = [("nothing", _("do nothing")), ("close", _("Close")), ("standby", _("go to idle mode")), ("deepstandby", shutdownString)], default = self.job.afterEvent or "nothing")
		self.job.afterEvent = self.settings.afterEvent.getValue()
		self.afterEventChangeable = afterEventChangeable
		self.setupList()
		self.state_changed()

	def setupList(self):
                if self.afterEventChangeable:
			self["config"].setList( [ getConfigListEntry(_("After event"), self.settings.afterEvent) ])
		else:
			self["config"].hide()
		self.job.afterEvent = self.settings.afterEvent.getValue()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.setupList()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.setupList()

	def windowShow(self):
	        pic1 = THISPLUG + "/skin/images/default.png"
                self["pixmap"].instance.setPixmapFromFile(pic1)
		self.job.state_changed.append(self.state_changed)

	def windowHide(self):
		if len(self.job.state_changed) > 0:
		    self.job.state_changed.remove(self.state_changed)

	def state_changed(self):
		j = self.job
		self["job_progress"].range = j.end
		self["summary_job_progress"].range = j.end
		self["job_progress"].value = j.progress
		self["summary_job_progress"].value = j.progress
		#print "JobView::state_changed:", j.end, j.progress
		self["job_status"].text = j.getStatustext()
		if j.status == j.IN_PROGRESS:
			self["job_task"].text = j.tasks[j.current_task].name
			self["summary_job_task"].text = j.tasks[j.current_task].name
		else:
			self["job_task"].text = ""
			self["summary_job_task"].text = j.getStatustext()
		if j.status in (j.FINISHED, j.FAILED):
			self.performAfterEvent()
			self["backgroundable"].boolean = False
			if j.status == j.FINISHED:
				self["finished"].boolean = True
				self["cancelable"].boolean = False
			elif j.status == j.FAILED:
				self["cancelable"].boolean = True

	def background(self):
		if self["backgroundable"].boolean == True:
			self.close(True)

	def ok(self):
		if self.job.status in (self.job.FINISHED, self.job.FAILED):
			self.close(False)

	def abort(self):
		if self.job.status == self.job.NOT_STARTED:
			job_manager.active_jobs.remove(self.job)
			self.close(False)
		elif self.job.status == self.job.IN_PROGRESS and self["cancelable"].boolean == True:
#			self.job.cancel()
                        self.close(False)
		else:
			self.close(False)

	def performAfterEvent(self):
		self["config"].hide()
		if self.settings.afterEvent.getValue() == "nothing":
			return
		elif self.settings.afterEvent.getValue() == "close" and self.job.status == self.job.FINISHED:
			self.close(False)
		from Screens.MessageBox import MessageBox
		if self.settings.afterEvent.getValue() == "deepstandby":
			if not Screens.Standby.inTryQuitMainloop:
				Notifications.AddNotificationWithCallback(self.sendTryQuitMainloopNotification, MessageBox, _("A sleep timer wants to shut down\nyour Dreambox. Shutdown now?"), timeout = 20, domain = "JobManager")
		elif self.settings.afterEvent.getValue() == "standby":
			if not Screens.Standby.inStandby:
				Notifications.AddNotificationWithCallback(self.sendStandbyNotification, MessageBox, _("A sleep timer wants to set your\nDreambox to standby. Do that now?"), timeout = 20, domain = "JobManager")

	def checkNotifications(self):
			self.close(False)

	def sendStandbyNotification(self, answer):
		if answer:
			Notifications.AddNotification(Screens.Standby.Standby, domain = "JobManager")

	def sendTryQuitMainloopNotification(self, answer):
		if answer:
			Notifications.AddNotification(Screens.Standby.TryQuitMainloop, 1, domain = "JobManager")























