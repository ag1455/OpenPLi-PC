
import sys,os
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import ElementTree, dump,SubElement,Element
xmlfile="/etc/KodiLite/favorites.xml"


def addfavorite(addon_id,media_title,media_url):
        debug=True
        if debug:
                tree = ElementTree()
                tree.parse(xmlfile)
                
               

                root = tree.getroot()
                try:
                       for addon in root.iter('addon'):
                                            
                                            id = addon.get('id')
                                            print id
                                            if id==addon_id:##addon exist,add media entry
                                               media = SubElement(addon, "media")
                                               media.set("title", media_title)
                                               media.text = media_url
                                               
                                               tree = ET.ElementTree(root)
                                               tree.write(xmlfile)
                                               return True
                except:                               
                       for addon in root.getiterator('addon'):
                                            
                                            id = addon.get('id')
                                            print id
                                            if id==addon_id:##addon exist,add media entry
                                               media = SubElement(addon, "media")
                                               media.set("title", media_title)
                                               media.text = media_url
                                               
                                               tree = ET.ElementTree(root)
                                               tree.write(xmlfile)
                                               return True

                ###addon not exists,add new addon entry
                addon = SubElement(root, "addon")
                addon.set("id", addon_id)
                media = SubElement(addon, "media")
                media.set("title", media_title)
                media.text = media_url
                
                tree = ET.ElementTree(root)
                
                tree.write(xmlfile)
                return True
                        
                
        else:
                return False

        
print "***********************"
def getfavorites(addon_id):
        list1=[]
        debug=True
        if debug:
                tree = ElementTree()
                tree.parse(xmlfile)
                root = tree.getroot()
                
                i=0
                try:
                       for addon in root.iter('addon'):
                            id = addon.get('id')
                            print id
                            
                            if id==addon_id:
                              for media in addon.iter('media'):      
                                 title=str(media.attrib.get("title"))
                                 url=str(media.text)
                              
                                 list1.append((title,url))
                except:
                       for addon in root.getiterator('addon'):
                            id = addon.get('id')
                            print id
                            
                            if id==addon_id:
                              for media in addon.getiterator('media'):      
                                 title=str(media.attrib.get("title"))
                                 url=str(media.text)
                              
                                 list1.append((title,url))
                                 
                
                return list1
        else:
                 return list1

###test area
#addon_id="plugin.video.navixtreme"
#media_title="bbc1"
#media_url="http://bbc1.mp4"
#print addfavorite(addon_id,media_title,media_url)
#addon_id="plugin.video.navixtreme"

#print getfavorites(addon_id)

