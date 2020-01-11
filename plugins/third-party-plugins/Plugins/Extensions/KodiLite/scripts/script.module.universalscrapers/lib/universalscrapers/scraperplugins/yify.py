import re
import xbmcaddon,time
from ..scraper import Scraper
from ..common import clean_title,clean_search,send_log,error_log 
from universalscrapers.modules import cfscrape
dev_log = xbmcaddon.Addon('script.module.universalscrapers').getSetting("dev_log")

User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'


class yify(Scraper):
    domains = ['http://yifymovies.tv']
    name = "YifyMovies"
    sources = []

    def __init__(self):
        self.base_link = 'http://yifymovies.tv'
        self.sources = []

    def scrape_movie(self, title, year, imdb, debrid=False):
        try:
            start_time = time.time()
            search_id = clean_search(title.lower())
            start_url = '%s/?s=%s' %(self.base_link,search_id.replace(' ','+'))
            headers = {'User_Agent':User_Agent}
            scraper = cfscrape.create_scraper()
            html = scraper.get(start_url,headers=headers,timeout=5).content

            Regex = re.compile('class="result-item".+?href="(.+?)".+?alt="(.+?)"',re.DOTALL).findall(html)   
            for item_url,name in Regex:
                if not clean_title(title).lower() == clean_title(name).lower():
                    continue
                if not year in name:
                    continue
                movie_link = item_url
                print 'Grabbed movie url to pass > ' + movie_link 
                self.get_source(movie_link,title,year,'','',start_time)

            return self.sources
        except Exception, argument:
            if dev_log == 'true':
                error_log(self.name,argument)
            return self.sources

    def scrape_episode(self, title, show_year, year, season, episode, imdb, tvdb, debrid = False):
        try:
            start_time = time.time()
            search_id = clean_search(title.lower())
            start_url = '%s/?s=%s' %(self.base_link,search_id.replace(' ','+'))
            headers = {'User_Agent':User_Agent}
            scraper = cfscrape.create_scraper()
            html = scraper.get(start_url,headers=headers,timeout=5).content
            Regex = re.compile('class="result-item".+?href="(.+?)".+?alt="(.+?)"',re.DOTALL).findall(html)
            for item_url,name in Regex:
                if not clean_title(title).lower() == clean_title(name).lower():
                    continue
                if "/series/" in item_url:
                    movie_link = item_url[:-1].replace('/series/','/episodes/')+'-%sx%s/'%(season,episode)
                    #print 'Grabbed Showpass url to pass > ' + movie_link    
                    self.get_source(movie_link,title,year,season,episode,start_time)

            return self.sources
        except Exception, argument:
            if dev_log == 'true':
                error_log(self.name,argument)
            return self.sources

    def get_source(self,movie_link, title, year, season, episode, start_time):
        try:
            print 'passed show '+movie_link
            headers = {'User_Agent':User_Agent}
            scraper = cfscrape.create_scraper()
            html = scraper.get(movie_link,headers=headers,timeout=5).content
            # grab_id = re.compile('data-ids="(.+?)"',re.DOTALL).findall(html)[0]
            # nonce = re.compile('ajax_get_video_info":"(.+?)"',re.DOTALL).findall(html)[0]
            # print grab_id
            # print nonce
            # req_post = '%s/wp-admin/admin-ajax.php' %(self.base_link)
            # headers = {'User-Agent':User_Agent,'Referer':movie_link}

            # data = {'action':'ajax_get_video_info','ids':grab_id,
            #         'server':'1','nonce':nonce}

            # get_links = scraper.post(req_post,headers=headers,data=data,verify=False).content
            # print get_links
            links = re.compile('"file":"(.+?)","label":"(.+?)"',re.DOTALL).findall(html)
            count = 0
            for final_url,res in links: 
                final_url = final_url.replace('\\','')
                if '1080' in res:
                    rez = '1080p'
                elif '720' in res:
                    rez = '720p'
                else: rez = 'SD'
                count +=1
                self.sources.append({'source': 'DirectLink','quality': rez,'scraper': self.name,'url': final_url,'direct': True})
            if dev_log=='true':
                end_time = time.time() - start_time
                send_log(self.name,end_time,count,title,year, season=season,episode=episode)
        except:
            pass
