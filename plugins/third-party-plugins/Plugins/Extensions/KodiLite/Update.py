import os, re
from urllib2 import urlopen
from twisted.web.client import getPage, downloadPage
#from enigma import addFont
############20180528##########################
THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"

latest = " "

pass#print "Starting Update-py"

#fontpath = THISPLUG
#addFont('%s/font_default.otf' % fontpath, 'TSmediaFont', 100, 1)


def updstart():

        #################
        pass#print "In upd_done"
        #################
        dest = "/tmp/updates2.zip"
        xfile = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/NONE.zip"
        pass#print "upd_done xfile =", xfile
        downloadPage(xfile, dest).addCallback(upd_last).addErrback(showError6)

def showError6(error):
        pass#print "ERROR :", error
        upd_last2()

def upd_last(fplug):
        fdest = "/usr"
        cmd = "unzip -o -q '/tmp/updates2.zip' -d " + fdest
        pass#print "cmd A =", cmd
        os.system(cmd)
        upd_last2()

def upd_last2(): 
        if not os.path.exists("/usr/lib/python2.7/site-packages/requests"):
               cmd = "opkg install python-requests"
               os.system(cmd)
        if not os.path.exists("/usr/lib/python2.7/site-packages/Crypto"):
               cmd = "opkg install python-pycrypto"
               os.system(cmd)
        if not os.path.exists("/usr/lib/python2.7/lib-dynload/mmap.so"):
               cmd = "opkg install python-mmap"
               os.system(cmd)
        if not os.path.exists("/usr/lib/python2.7/sqlite3"):
               cmd = "opkg install python-sqlite3"
               os.system(cmd)
        if not os.path.exists("/usr/lib/python2.7/cProfile.pyc"):  #needed by exodus
               cmd = "opkg install python-profile"
               os.system(cmd)
        if not os.path.exists("/usr/lib/python2.7/email"):  #needed by youtube
               cmd = "opkg install python-email"
               os.system(cmd)
        try:
               import Image
        except:
            try:
               from PIL import Image
            except:
               cmd = "opkg install python-image"
               os.system(cmd)
        try:
               import Image
        except:
            try:
               from PIL import Image
            except:
               cmd = "opkg install python-imaging"
               os.system(cmd)

        tf = THISPLUG + "/scripts/script.module.covenant/lib/resources/lib/sources/en/123netflix.py"
        tf2 = THISPLUG + "/scripts/script.module.covenant/lib/resources/lib/sources/en/netflix.py"
        pass#print "Renaming 123netflix.py"
        if os.path.exists(tf):
                cmd = "mv " + tf + " " + tf2 
                pass#print "Rename cmd =", cmd
                os.system(cmd)

        tf = THISPLUG + "/scripts/script.module.covenant/lib/resources/lib/sources/en/123hulu.py"
        tf2 = THISPLUG + "/scripts/script.module.covenant/lib/resources/lib/sources/en/hulu.py"
        pass#print "Renaming 123hulux.py"
        if os.path.exists(tf):
                cmd = "mv " + tf + " " + tf2 
                pass#print "Rename cmd =", cmd
                os.system(cmd)

        pass#print "In upd_done 2"
        ####################
