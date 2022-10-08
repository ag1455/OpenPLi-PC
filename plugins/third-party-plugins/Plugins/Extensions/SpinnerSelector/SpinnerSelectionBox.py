from Screens.Screen import Screen
from Components.ActionMap import NumberActionMap
from Components.Label import Label
#from Components.ChoiceList import ChoiceEntryComponent, ChoiceList
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Plugins.Extensions.SpinnerSelector.Spinner import Spinner
import os

class SpinnerSelectionBox(Screen):
	skin = """
	<screen name="SpinnerSelectionBox" position="150,100" size="550,400" title="Input" backgroundColor="transparent">
		<widget name="text" position="10,160" size="550,25" font="Regular;20" backgroundColor="transparent" />
		<widget name="list" position="0,30" size="550,335" scrollbarMode="showOnDemand" />
		<widget name="bild" position="200,10" zPosition="1" size="300,200" transparent="1" />
		<applet type="onLayoutFinish">
# this should be factored out into some helper code, but currently demonstrates applets.
from enigma import eSize, ePoint

orgwidth = self.instance.size().width()
orgpos = self.instance.position()
textsize = self[&quot;text&quot;].getSize()

# y size still must be fixed in font stuff...
textsize = (textsize[0] + 50, textsize[1] + 200)
count = len(self.list)
if count &gt; 8:
	count = 8
offset = 25 * count
wsizex = textsize[0] + 60
wsizey = textsize[1] + offset

if (520 &gt; wsizex):
	wsizex = 520
wsize = (wsizex, wsizey)

# resize
self.instance.resize(eSize(*wsize))

# resize label
self[&quot;text&quot;].instance.resize(eSize(*textsize))

# move list
listsize = (wsizex, 25 * count)
self[&quot;list&quot;].instance.move(ePoint(0, textsize[1]))
self[&quot;list&quot;].instance.resize(eSize(*listsize))

# center window
newwidth = wsize[0]
self.instance.move(ePoint((720-wsizex)/2, (576-wsizey)/(count &gt; 7 and 2 or 3)))
		</applet>
	</screen>"""
	def __init__(self, session, title = "", list = []):
		Screen.__init__(self, session)

		self["text"] = Label(title)
		self.list = list #[]
		self.summarylist = []
		cursel = self.list[0]
		self.Bilder = []
		if cursel:
			for i in range(64):
				if (os.path.isfile("/usr/share/enigma2/Spinner/%s/wait%d.png"%(cursel[0],i+1))):
					self.Bilder.append("/usr/share/enigma2/Spinner/%s/wait%d.png"%(cursel[0],i+1))
		self["bild"] = Spinner(self.Bilder);
		self["list"] = MenuList(list = self.list) #, selection = selection)
		self["list"].onSelectionChanged.append(self.Changed)
		self["summary_list"] = StaticText()
		self.updateSummary()
				
		self["actions"] = NumberActionMap(["WizardActions","DirectionActions"], 
		{
			"ok": self.go,
			"back": self.cancel,
			"up": self.up,
			"down": self.down
		}, -1)

	def Changed(self):
		cursel = self["list"].l.getCurrentSelection()
		if cursel:
			self.Bilder = []
			for i in range(64):
				if (os.path.isfile("/usr/share/enigma2/Spinner/%s/wait%d.png"%(cursel[0],i+1))):
					self.Bilder.append("/usr/share/enigma2/Spinner/%s/wait%d.png"%(cursel[0],i+1))
			self["bild"].SetBilder(self.Bilder)
			
		
	def keyLeft(self):
		pass
	
	def keyRight(self):
		pass
	
	def up(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.moveUp)
				self.updateSummary(self["list"].l.getCurrentSelectionIndex())
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == 0:
					break

	def down(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.moveDown)
				self.updateSummary(self["list"].l.getCurrentSelectionIndex())
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == len(self["list"].list) - 1:
					break

	# runs the current selected entry
	def go(self):
		cursel = self["list"].l.getCurrentSelection()
		if cursel:
			self.goEntry(cursel[0])
		else:
			self.cancel()

	# runs a specific entry
	def goEntry(self, entry):
		if len(entry) > 2 and isinstance(entry[1], str) and entry[1] == "CALLFUNC":
			# CALLFUNC wants to have the current selection as argument
			arg = self["list"].l.getCurrentSelection()[0]
			entry[2](arg)
		else:
			self.close(entry)

	def updateSummary(self, curpos=0):
		pos = 0
		summarytext = ""
		for entry in self.summarylist:
			if pos > curpos-2 and pos < curpos+5:
				if pos == curpos:
					summarytext += ">"
				else:
					summarytext += entry[0]
				summarytext += ' ' + entry[1] + '\n'
			pos += 1
		self["summary_list"].setText(summarytext)

	def cancel(self):
		self.close(None)

