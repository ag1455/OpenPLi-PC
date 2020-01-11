import requests,re,time
import urllib
import xbmcaddon
from ..scraper import Scraper
from ..common import clean_search,send_log,error_log
from ..modules.jsunpack import unpack

dev_log = xbmcaddon.Addon('script.module.universalscrapers').getSetting("dev_log")

User_Agent = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
session = requests.Session()

class watch32(Scraper):
    domains = ['watch32hd.co']
    name = "Watch32hd"
    sources = []

    def __init__(self):
        self.base_link = 'https://watch32hd.co'

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            start_time = time.time()
            search_id = clean_search(title.lower())
            start_url = '%s/watch?v=%s_%s' %(self.base_link,search_id.replace(' ','_'),year)
            headers={'User-Agent':User_Agent}
            html = session.get(start_url,headers=headers,timeout=5).content
            varid = re.compile('var frame_url = "(.+?)"',re.DOTALL).findall(html)[0]
            if varid.startswith('"'):
                pass
            else:
                res_chk = re.compile('class="title"><h1>(.+?)</h1>',re.DOTALL).findall(html)[0]
                varid = 'http:'+varid
                get_info_html = session.get(varid).content
                action = re.findall("'action': '(.+?)'",get_info_html)[0]
                print varid
                print varid.replace('http://vidlink.org/embed/','')
                headers={'User-Agent':User_Agent, 'referer':varid, 'X-Requested-With':'XMLHttpRequest','Host':'vidlink.org',
                         'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
                data = {'browserName':'Firefox','platform':'Win64','postID':varid.replace('http://vidlink.org/embed/',''),
                        'action':action}
                if not varid.startswith('https'):
                    varid = varid.replace('http','https')
                holder = session.post(varid.replace('/embed/','/streamdrive/info/'),headers=headers,data=data,timeout=5).content
                holder = unpack(holder)
                links = re.compile('"src":"(.+?)"',re.DOTALL).findall(holder)
                count = 0
                for link in links:
                    link = link.replace('\\','').replace('/redirect?url=','')
                    movie_link = urllib.unquote(link.decode("utf8"))
                    if '1080' in res_chk:
                        res= '1080p'
                    elif '720' in res_chk:
                        res='720p'
                    else:
                        res='DVD'
                    check = requests.head(urllib.unquote_plus(link),timeout=3).status_code
                    if str(check) == '200':
                        count +=1
                        self.sources.append({'source': 'Googlelink','quality': res,'scraper': self.name,'url': movie_link,'direct': True})
                if dev_log=='true':
                    end_time = time.time() - start_time
                    send_log(self.name,end_time,count,title,year)
            return self.sources
        except Exception, argument:
            print argument
            if dev_log == 'true':
                error_log(self.name,argument)
            return self.sources
