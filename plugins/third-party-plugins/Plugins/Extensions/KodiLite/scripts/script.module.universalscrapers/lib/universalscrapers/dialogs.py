# -*- coding: utf-8 -*-
from threading import Thread, RLock

import xbmc
import xbmcaddon
import xbmcgui


def select_ext(title, populator, tasks_count, sort_function = None):
    addonPath = xbmcaddon.Addon().getAddonInfo('path').decode('utf-8')
    dlg = SelectorDialog("DialogSelect.xml", addonPath, title=title,
                         populator=populator, steps=tasks_count, sort_function=sort_function)

    with ExtendedDialogHacks():
        dlg.doModal()
        selection = dlg.get_selection()
        items = dlg.items
        del dlg

    return (selection, items)


class FanArtWindow(xbmcgui.WindowDialog):
    def __init__(self):
        control_background = xbmcgui.ControlImage(0, 0, 1280, 720, xbmcaddon.Addon().getAddonInfo('fanart'))
        self.addControl(control_background)

        fanart = xbmc.getInfoLabel('ListItem.Property(Fanart_Image)')
        if fanart and fanart != "Fanart_Image":
            control_fanart = xbmcgui.ControlImage(0, 0, 1280, 720, fanart)
            self.addControl(control_fanart)


class ExtendedDialogHacks(object):
    def __init__(self):
        self.active = False

        self.hide_progress = False
        self.hide_info = False

        self.autohidedialogs = False
        if self.autohidedialogs:
            self.hide_progress = False
            self.hide_info = False

        if not self.hide_progress and not self.hide_info:
            self.autohidedialogs = False

    def __enter__(self):
        self.active = True

        #        self.numeric_keyboard = None
        self.fanart_window = FanArtWindow()

        ## Keyboard hack
        #        if plugin.get_setting(SETTING_ADVANCED_KEYBOARD_HACKS, converter=bool):
        #            self.numeric_keyboard = xbmcgui.Window(10109)
        #            Thread(target = lambda: self.numeric_keyboard.show()).start()
        #            wait_for_dialog('numericinput', interval=50)

        # Show fanart background
        self.fanart_window.show()

        # Run background task
        if self.autohidedialogs:
            Thread(target=self.background_task).start()

    def background_task(self):
        xbmc.sleep(1000)
        while not xbmc.abortRequested and self.active:
            if self.hide_progress:
                active_window = xbmcgui.getCurrentWindowDialogId()
                if active_window in [10101, 10151]:
                    xbmc.executebuiltin("Dialog.Close(%d, true)" % active_window)
            if self.hide_info:
                if xbmc.getCondVisibility("Window.IsActive(infodialog)"):
                    xbmc.executebuiltin('Dialog.Close(infodialog, true)')
            xbmc.sleep(100)

    def __exit__(self, exc_type, exc_value, traceback):
        self.active = False

        #        if self.numeric_keyboard is not None:
        #            self.numeric_keyboard.close()
        #            del self.numeric_keyboard
        #            xbmc.executebuiltin("Dialog.Close(numericinput, true)")

        self.fanart_window.close()
        del self.fanart_window


class SelectorDialog(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.title = kwargs['title']
        self.populator = kwargs['populator']
        self.steps = kwargs['steps']
        self.sort_function = kwargs['sort_function']

        self.items = []
        self.selection = None
        self.insideIndex = -1
        self.completed_steps = 0

        self.thread = None
        self.lock = RLock()

    def get_selection(self):
        """ get final selection """
        return self.selection

    def onInit(self):
        # set title
        self.label = self.getControl(1)
        self.label.setLabel(self.title)

        # Hide ok button
        self.getControl(5).setVisible(False)

        # Get active list
        try:
            self.list = self.getControl(6)
            self.list.controlLeft(self.list)
            self.list.controlRight(self.list)
            self.getControl(3).setVisible(False)
        except:
            self.list = self.getControl(3)
        self.setFocus(self.list)

        # populate list
        self.thread = Thread(target=self._populate)
        self.thread.start()

    def onAction(self, action):
        if action.getId() in (9, 10, 92, 216, 247, 257, 275, 61467, 61448,):
            if self.insideIndex == -1:
                self.close()
            else:
                self._inside_root(select=self.insideIndex)

    def onClick(self, controlID):
        if controlID == 6 or controlID == 3:
            num = self.list.getSelectedPosition()
            if num >= 0:
                if self.insideIndex == -1:
                    self._inside(num)
                else:
                    self.selection = self.items[self.insideIndex][1][num]
                    self.close()

    def onFocus(self, controlID):
        if controlID in (3, 61):
            self.setFocus(self.list)

    def _inside_root(self, select=-1):
        with self.lock:
            self.list.reset()

            for source, links in self.items:
                if len(links) > 1:
                    source += " >>"
                listitem = xbmcgui.ListItem(source)
                try:
                    #icon = xbmcaddon.Addon(id=links[0]['path'].split("/")[2]).getAddonInfo('icon')
                    icon = xbmcaddon.Addon().getAddonInfo('icon')
                    listitem.setIconImage(icon)
                except:
                    pass
                self.list.addItem(listitem)

            if select >= 0:
                self.list.selectItem(select)
            self.insideIndex = -1

    def _inside(self, num):
        if num == -1:
            self._inside_root(select=self.insideIndex)
            return

        with self.lock:
            source, links = self.items[num]

            if len(links) == 1:
                self.selection = links[0]
                self.close()
                return

            self.list.reset()
            for item in links:
                listitem = xbmcgui.ListItem(item['label'])
                #listitem.setProperty("Path", item['path'])

                try:
                    #pluginid = item['path'].split("/")[2]
                    icon = xbmcaddon.Addon().getAddonInfo('icon')
                    listitem.setIconImage(icon)
                except:
                    pass

                self.list.addItem(listitem)

            self.insideIndex = num

    def step(self):
        self.completed_steps += 1
        progress = self.completed_steps * 100 / self.steps
        self.label.setLabel(u"{0} - {1:d}% ({2}/{3})".format(self.title, progress,
                                                             self.completed_steps, self.steps))

    def _populate(self):
        xbmc.sleep(500)  # Delay population to let ui settle
        self.label.setLabel(self.title)
        try:
            for result in self.populator():
                self.step()

                if not result:
                    continue

                with self.lock:
                    # Remember selected item
                    selectedItem = None
                    if self.insideIndex == -1:
                        selectedIndex = self.list.getSelectedPosition()
                    else:
                        selectedIndex = self.insideIndex
                    if selectedIndex >= 0:
                        selectedItem = self.items[selectedIndex]

                    # Add new item
                    self.items.extend(result)
                    if self.sort_function:
                        self.items = sorted(self.items, key = self.sort_function)
                    #self.items.sort()

                    # Retrived new selection-index
                    if selectedItem is not None:
                        selectedIndex = self.items.index(selectedItem)
                        if self.insideIndex != -1:
                            self.insideIndex = selectedIndex

                    # Update only if in root
                    if self.insideIndex == -1:
                        self._inside_root(select=selectedIndex)
                        self.setFocus(self.list)
        except:
            self.label.setLabel(
                u"{0} - {1:d}% ({2}/{3})".format(self.title, 100,
                                                 self.steps, self.steps))
        pass
