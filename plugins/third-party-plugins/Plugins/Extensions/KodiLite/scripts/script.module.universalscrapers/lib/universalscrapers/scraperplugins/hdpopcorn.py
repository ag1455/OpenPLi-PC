import requests
import re
import xbmc,xbmcaddon,time
from ..scraper import Scraper
from ..common import clean_title,clean_search,send_log,error_log

dev_log = xbmcaddon.Addon('script.module.universalscrapers').getSetting("dev_log")

s = requests.session()
User_Agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
                                           
class hdpopcorn(Scraper):
    domains = ['hdpopcorns.com']
    name = "HD Popcorns"
    sources = []

    def __init__(self):
        self.base_link = 'http://hdpopcorns.co'
        self.sources = []

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            start_time = time.time() 
            search_id = clean_search(title.lower())
            start_url ='%s/?s=%s' %(self.base_link,search_id.replace(' ','+'))
            #print 'starturl > '+start_url
            headers={'User-Agent':User_Agent}
            html = requests.get(start_url,headers=headers,timeout=5).content
           
            links = re.compile('<header>.+?href="(.+?)" title="(.+?)"',re.DOTALL).findall(html)
            for m_url,m_title in links:
                movie_name, movie_year = re.findall("(.*?)(\d+)", m_title)[0]
                if not clean_title(title).lower() == clean_title(movie_name).lower():
                    continue
                if not year in movie_year:
                    continue
                url = m_url
                #error_log(self.name + ' Pass',url)
                self.get_source(url, title, year, '', '', start_time)
            return self.sources
        except Exception, argument:        
            if dev_log == 'true':
                error_log(self.name,argument)
            return self.sources

    def get_source(self,url, title, year, season, episode, start_time):
        try:
            headers={'User-Agent':User_Agent}
            OPEN = requests.get(url,headers=headers,timeout=5).content
            headers = {'Origin':'http://hdpopcorns.com', 'Referer':url,
                       'X-Requested-With':'XMLHttpRequest', 'User-Agent':User_Agent}
            count = 0
            try:
                params = re.compile('FileName1080p.+?value="(.+?)".+?FileSize1080p.+?value="(.+?)".+?value="(.+?)"',re.DOTALL).findall(OPEN)
                for param1, param2,param3 in params:
                    request_url = '%s/select-movie-quality.php' %(self.base_link)
                    form_data = {'FileName1080p':param1,'FileSize1080p':param2,'FSID1080p':param3}
                link = requests.post(request_url, data=form_data, headers=headers,timeout=3).content
                final_url = re.compile('<strong>1080p</strong>.+?href="(.+?)"',re.DOTALL).findall(link)[0]
                
                res = '1080p'
                count +=1
                self.sources.append({'source': 'DirectLink', 'quality': res, 'scraper': self.name, 'url': final_url,'direct': True})
            except:pass
            try:
                params = re.compile('FileName720p.+?value="(.+?)".+?FileSize720p".+?value="(.+?)".+?value="(.+?)"',re.DOTALL).findall(OPEN)
                for param1, param2,param3 in params:
                    request_url = '%s/select-movie-quality.php' %(self.base_link)
                    form_data = {'FileName720p':param1,'FileSize720p':param2,'FSID720p':param3}
                link = requests.post(request_url, data=form_data, headers=headers,timeout=3).content
                final_url = re.compile('<strong>720p</strong>.+?href="(.+?)"',re.DOTALL).findall(link)[0]

                res = '720p'
                count +=1
                self.sources.append({'source': 'DirectLink', 'quality': res, 'scraper': self.name, 'url': final_url,'direct': True})
  
            except:pass 
            if dev_log=='true':
                end_time = time.time() - start_time
                send_log(self.name,end_time,count,title,year, season=season,episode=episode)              
        except:
            pass

