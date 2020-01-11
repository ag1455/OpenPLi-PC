import requests
import urlparse
import re
import resolveurl as urlresolver
import xbmc,xbmcaddon,time
from ..scraper import Scraper
from ..common import clean_title,clean_search,random_agent,send_log,error_log
dev_log = xbmcaddon.Addon('script.module.universalscrapers').getSetting("dev_log")


class pandamovies(Scraper):
    domains = ['https://pandamovie.pw']
    name = "Panda Movies"
    sources = []

    def __init__(self):
        self.base_link = 'https://pandamovie.pw'


    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            start_time = time.time()
            search_id = clean_search(title.lower())


            start_url = '%s/?s=%s' %(self.base_link,search_id.replace(' ','+'))
            #print 'scrapercheck - scrape_movie - start_url:  ' + start_url

            headers={'User-Agent':random_agent()}
            html = requests.get(start_url,headers=headers,timeout=5).content
            #print html
            match = re.compile('class="title".+?href="(.+?)".+?title="(.+?)"',re.DOTALL).findall(html)
            for item_url, name in match:
                if year in name:
                    #print 'scrapertest - scrape_movie - name: '+name
                    #print 'scrapertest - scrape_movie - item_url: '+item_url
                    if clean_title(search_id).lower() == clean_title(name).lower():

                        #print 'scrapertest - scrape_movie - Send this URL: ' + item_url
                        self.get_source(item_url,title,year,start_time)
            return self.sources
        except Exception, argument:
            if dev_log=='true':
                error_log(self.name,argument)


    def get_source(self,item_url,title,year,start_time):
        try:
            count = 0
            headers={'User-Agent':random_agent()}
            OPEN = requests.get(item_url,headers=headers,timeout=5).content
            #print 'scrapercheck- scrape_movie - OPEN: '+OPEN
            Endlinks = re.compile('<li><span.+?href="(.+?)"',re.DOTALL).findall(OPEN)
            #print 'scrapercheck- scrape_movie - EndLinks: '+str(Endlinks)
            for link in Endlinks:
                #print 'scrapercheck-- scrape_movie - link: '+str(link)
                if '1080' in link:
                    qual = '1080p'
                elif '720' in link:
                    qual = '720p'
                else:
                    qual = 'DVD'
                count+=1
                host = link.split('//')[1].replace('www.','')
                host = host.split('/')[0].split('.')[0].title()
                self.sources.append({'source':host, 'quality':qual, 'scraper':self.name, 'url':link, 'direct':True})
            if dev_log=='true':
                end_time = time.time() - start_time
                send_log(self.name,end_time,count,title,year)
        except Exception, argument:
            if dev_log=='true':
                error_log(self.name,argument)
            return[]
