# -*- coding: utf-8 -*-
# Universal Scrapers
import re,requests,base64,time
import xbmcaddon
from ..scraper import Scraper
from ..common import clean_title,clean_search,random_agent,filter_host,send_log,error_log 

dev_log = xbmcaddon.Addon('script.module.universalscrapers').getSetting("dev_log")

class darewatch(Scraper):
    domains = ['ondarewatch.com/']
    name = "DareWatch"
    sources = []

    def __init__(self):
        self.base_link = 'http://www.ondarewatch.com/'
        self.search_url = self.base_link + '/index.php'
        self.sources = []
        if dev_log=='true':
            self.start_time = time.time()

    def scrape_movie(self, title, year, imdb, debrid=False):
        try:
            start_time = time.time()
            search_id = clean_search(title.lower())
            
            #print 'darewatch ID> ' + search_id
            headers = {'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                       'accept-encoding':'gzip, deflate, br','accept-language':'en-US,en;q=0.8','content-type':'application/x-www-form-urlencoded',
                       'User-Agent':random_agent(),'origin':self.base_link,'referer':self.base_link+'/search'}
            
            data = {'menu': 'search','query': search_id}
            
            html = requests.post(self.search_url,headers=headers,data=data,timeout=5).content
            #print 'DAREWARCH > post: '+html
            page = html.split('Movie results for:')[1]
            Regex = re.compile('<h4>.+?class="link" href="(.+?)" title="(.+?)"',re.DOTALL).findall(page)
            for item_url,name in Regex:
                #print '(grabbed url) %s  (title) %s' %(item_url,name)
                if not clean_title(title).lower() == clean_title(name).lower():
                    continue
                if not year in name:
                    continue
                #print 'Darewatch URL check> ' + item_url
                self.get_source(item_url,title,year,'','',start_time)
                
            return self.sources
        except Exception, argument:        
            if dev_log == 'true':
                error_log(self.name,argument)
            return self.sources

    def scrape_episode(self,title, show_year, year, season, episode, imdb, tvdb, debrid = False):
        try:    
            start_time = time.time()
            search_id = clean_search(title.lower())
            
            #print 'darewatch ID> ' + search_id
            headers = {'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                       'accept-encoding':'gzip, deflate, br','accept-language':'en-US,en;q=0.8','content-type':'application/x-www-form-urlencoded',
                       'User-Agent':random_agent(),'origin':self.base_link,'referer':self.base_link+'/search'}
            
            data = {'menu': 'search','query': search_id}
            
            html = requests.post(self.search_url,headers=headers,data=data,timeout=5).content
            #print 'DAREWARCH > post: '+html
            page = html.split('TV show results for:')[1]
            Regex = re.compile('<h4>.+?class="link" href="(.+?)" title="(.+?)"',re.DOTALL).findall(page)
            for item_url,name in Regex:
                #print '(grabbed url) %s  (title) %s' %(item_url,name)
                if not clean_title(title).lower() == clean_title(name).lower():
                    continue
                if '/watchm/' not in item_url:
                    item_url = item_url + '/season/%s/episode/%s' %(season, episode)
                    #print 'Darewatch URL check> ' + item_url
                    self.get_source(item_url,title,year,season,episode,start_time)
                
            return self.sources
        except Exception, argument:        
            if dev_log == 'true':
                error_log(self.name,argument)
            return self.sources


    def get_source(self,item_url,title,year,season,episode,start_time):
        try:
            headers = {'User-Agent':random_agent()}

            html = requests.get(item_url,headers=headers,timeout=10).content

            match = re.compile("] = '(.+?)'",re.DOTALL).findall(html)
            count = 0
            for vid in match:
                host = base64.b64decode(vid)
                link=re.compile('.+?="(.+?)"',re.DOTALL).findall(host)[0]
                if 'openload' in link:
                    try:
                        get_res=requests.get(link,headers=headers,timeout=5).content
                        rez = re.compile('description" content="(.+?)"',re.DOTALL).findall(get_res)[0]
                        if '1080' in rez:
                            qual = '1080p'
                        elif '720' in rez:
                            qual='720p'
                        else:
                            qual='SD'
                    except:qual='SD'
                    count +=1
                    self.sources.append({'source': 'Openload','quality': qual,'scraper': self.name,'url': link,'direct': False})
                else: 
                    hoster = link.split('//')[1].replace('www.','')
                    hoster = hoster.split('/')[0].lower()
                    if not filter_host(hoster):
                        continue
                    count +=1    
                    self.sources.append({'source': hoster,'quality': 'DVD','scraper': self.name,'url': link,'direct': False})
            if dev_log=='true':
                end_time = time.time() - start_time
                send_log(self.name,end_time,count,title,year, season=season,episode=episode)        
        except:
            pass
