import universalscrapers
import xbmcgui
import os,re
import xbmc
import xbmcaddon
import random
import sys
import urlparse
import xbmcvfs
import time
import urllib
import xbmc
import xbmcgui
import requests

dialog = xbmcgui.Dialog()
pDialog = xbmcgui.DialogProgress()
No_of_scrapers = []
scraper_paths = []

tmdb_test = str(xbmcaddon.Addon('script.module.universalscrapers').getSetting("tmdb_test"))

ADDON_PATH = xbmc.translatePath('special://home/addons/script.module.universalscrapers/')
ICON = ADDON_PATH + 'icon.png'
FANART = ADDON_PATH + 'fanart.jpg'

USERDATA_PATH = xbmc.translatePath('special://home/userdata/addon_data')
ADDON_DATA = os.path.join(USERDATA_PATH,'script.module.universalscrapers')
full_file = os.path.join(ADDON_DATA,'Log.txt')

scraper_results_path = xbmc.translatePath(full_file)
if not os.path.exists(scraper_results_path):
	Open = open(scraper_results_path,'w+')

scrapers_path = xbmc.translatePath('special://home/addons/script.module.universalscrapers/lib/universalscrapers/scraperplugins')
for Root, Dir, Files in os.walk(scrapers_path):
	for File in Files:
		if not 'pyc' in File and not '__' in File and 'py' in File and not 'broken' in Root and not 'slow' in Root and not 'ok' in Root and not 'unsure' in Root and not 'test' in Root:
			No_of_scrapers.append('1')
			scraper_paths.append(File)

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?', '')))
mode = params.get('mode')
if mode == "DisableAll":
    scrapers = sorted(
        universalscrapers.relevant_scrapers(include_disabled=True), key=lambda x: x.name.lower())
    for scraper in scrapers:
        key = "%s_enabled" % scraper.name
        xbmcaddon.Addon('script.module.universalscrapers').setSetting(key, "false")
    sys.exit()
elif mode == "EnableAll":
    scrapers = sorted(
        universalscrapers.relevant_scrapers(include_disabled=True), key=lambda x: x.name.lower())
    for scraper in scrapers:
        key = "%s_enabled" % scraper.name
        xbmcaddon.Addon('script.module.universalscrapers').setSetting(key, "true")
    sys.exit()
elif mode == "Deletelog":
    from universalscrapers.common import Del_LOG
    Del_LOG()
    sys.exit()

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

movies = [
    {
        'title': 'Deadpool',
        'year': '2016',
        'imdb': 'tt1431045'
    },
    {
        'title': 'Topper Returns',
        'year': '1941',
        'imdb': 'tt0034303'
    },
    {
        'title': 'Logan',
        'year': '2017',
        'imdb': 'tt3315342'
    },
    {
        'title': 'The Great Wall',
        'year': '2016',
        'imdb': 'tt2034800'
    },
    {
        'title': 'Why Him?',
        'year': '2016',
        'imdb': 'tt4501244'
    },
    {
        'title': 'Patriots Day',
        'year': '2016',
        'imdb': 'tt4572514'
    },
    {
        'title': 'Baywatch',
        'year': '2017',
        'imdb': ''
    },
    {
        'title': 'Sing',
        'year': '2016',
        'imdb': 'tt3470600'
    },
    {
        'title': 'Sonic The Hedgehog: The Movie',
        'year': '1996',
        'imdb': 'tt0237765'
    },
    {
        'title': 'Surf\'s Up',
        'year': '2007',
        'imdb': 'tt0423294'
    },
    {
        'title': 'Kim Possible A Sitch in Time',
        'year': '2004',
        'imdb': 'tt0389074'
    },
    {
        'title': 'Train to Busan',
        'year': '2016',
        'imdb': 'tt5700672'
    },
    {
        'title': 'Green Street',
        'year': '2005',
        'imdb': 'tt0385002'
    },
    {
        'title': 'A Turtle\'s Tale: Sammy\'s Adventures',
        'year': '2010',
        'imdb': 'tt1230204'
    },
]

shows = [
    {
        'title': "American Dad",
        'show_year': "2005",
        'year': "2017",
        'season': '15',
        'episode': '1',
        'imdb': 'tt0397306',
    },
    {
        'title': "The Flash",
        'show_year': "2014",
        'year': "2016",
        'season': '3',
        'episode': '8',
        'imdb': 'tt3107288',
    },
    {
        'title': "Breaking Bad",
        'show_year': "2008",
        'year': "2008",
        'season': '1',
        'episode': '1',
        'imdb': 'tt0903747',
    },
    {
        'title': "Breaking Bad",
        'show_year': "2008",
        'year': "2011",
        'season': '4',
        'episode': '6',
        'imdb': 'tt0903747',
    },
    {
        'title': "Game of Thrones",
        'show_year': "2011",
        'year': "2011",
        'season': '1',
        'episode': '1',
        'imdb': 'tt0944947',
    },
    {
        'title': "Game of Thrones",
        'show_year': "2011",
        'year': "2016",
        'season': '6',
        'episode': '5',
        'imdb': 'tt0944947',
    },
    {
        'title': "House M.D.",
        'show_year': "2004",
        'year': "2004",
        'season': '1',
        'episode': '1',
        'imdb': 'tt0412142',
    },

]

num_shows = len(shows) + len(movies)

def main():
    test_type = xbmcgui.Dialog().select("Choose type of test", ["Test Scrapers" , "Check Scraper Results" , "Wipe Scraper Results"])
    basepath = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo("profile"))
    if test_type == 0:
        test()
    elif test_type == 1:
        if os.path.exists(scraper_results_path):
            get_scraper_results()
        else:
            xbmcgui.Dialog().notification("Oopsie Daisy", "File not found")
    elif test_type == 2:
		clear_scraper_log()

def clear_scraper_log():
	if os.path.exists(scraper_results_path):
		Open = open(scraper_results_path,'w+')
	else:
		xbmcgui.Dialog().notification("Oopsie Doodles", "File not found")

def get_scraper_results():
	try:
		results_type = xbmcgui.Dialog().select("Choose type of results", ["Full" , "Slow Scrapers" , "No Results", "Errors"])
		slow_scraper_list = []
		no_results = []
		scraper_names = []
		scraper_results_check_name = []
		for item in scraper_paths:
			Scraper_path = os.path.join(scrapers_path,item)
			get_scraper_names = re.findall('name = "(.+?)"',open(Scraper_path).read())
			for name in get_scraper_names:
				scraper_names.append(name)
		if not os.path.exists(scraper_results_path):
			Open = open(scraper_results_path,'w+')
		else:
			Open = open(scraper_results_path).read()
			get_info = re.findall('<.+?Universalscraper: (.+?)\n.+?Tested with: (.+?)\n.+?Links returned: (.+?)\n.+?Time to Complete:(.+?)\n',str(Open),re.DOTALL)
			for scraper_name, info_tested, no_of_links, time_taken in get_info:
				if not 'NoLinks' in no_of_links:
					scraper_results_check_name.append(scraper_name)
				dict_string = {'scraper_name':scraper_name, 'info_tested':info_tested,'no_of_links':no_of_links,'time_taken':time_taken}
				if round(float(time_taken)) > 10:
					slow_scraper_list.append(dict_string)
		for name in scraper_names:
			if name not in str(scraper_results_check_name):
				no_results.append(name)
		if results_type == 0:
			Open = open(scraper_results_path).read()
			get_line = re.findall('(.+?)\n',Open,re.DOTALL)
			dialog.textviewer("Universalscrapers Testing Mode", '\n'.join(str(p) for p in get_line) )
		elif results_type == 1:
			if len(slow_scraper_list)==0:
				dialog.textviewer("Scrapers with slow times",'No Scrapers took over 10 seconds')
			else:
				dialog.textviewer("Scrapers with slow times", '\n'.join(str(scraper['scraper_name']+' : returned '+str(scraper['no_of_links']).replace('Check Scraper/NoLinks','0')+' links for '+scraper['info_tested']+' in '+scraper['time_taken']+' seconds') for scraper in slow_scraper_list) )

		elif results_type == 2:
			dialog.textviewer("Scrapers with no results", '\n'.join(str(p) for p in no_results) )
		elif results_type == 3:
			List = []
			Open = open(scraper_results_path).read()
			get_errors = re.findall(':>>>>(.+?)\n:>>>>(.+?)\n',Open,re.DOTALL)
			for line1, line2 in get_errors:
				List.append(line1.replace('  ',''))
				List.append(line2.replace('  ',''))
				List.append('\n')
				List.append('#######################')
			dialog.textviewer("Scraper Errors", '\n'.join(str(p) for p in List) )
	except Exception as e:
		xbmcgui.Dialog().notification("Oopsie Daisy", str(e))

def disable_working(scraper_id):
    key = "%s_enabled" % scraper_id
    xbmcaddon.Addon('script.module.universalscrapers').setSetting(key, "false")
    sys.exit()

def test():
	pDialog = xbmcgui.DialogProgress()
	if dialog.yesno("Universalscrapers Testing Mode", 'Clear Scraper Log?'):
		clear_scraper_log()
	if dialog.yesno("Universalscrapers Testing Mode", 'Clear cache?'):
		universalscrapers.clear_cache()
	if tmdb_test == '':
		test_type = xbmcgui.Dialog().select("Choose type of test", ["Single Scraper" , "Full Test" ])
	else:
		test_type = xbmcgui.Dialog().select("Choose type of test", ["Single Scraper" , "Full Test", "TMDB Test" ])
	if test_type == 0:
		single_test(0,0)
	elif test_type == 1:
		full_test()
	if tmdb_test != '':
		if test_type == 2:
			tmdb_test_menu()

def tmdb_test_menu():
	tmdb_list_url = 'https://www.themoviedb.org/list/' + tmdb_test
	html = requests.get(tmdb_list_url).content
	tmdb_movies(html)
#	test_type = xbmcgui.Dialog().select("Choose type of test", ["Movies" , "Tv Shows"]) #### Add these back in to allow choice of movie/tv show
#	if test_type == 0:
#		tmdb_movies(html)
#	if test_type == 1:
#		tmdb_tv_shows(html)


def tmdb_movies(html):
	count = 0
	pDialog.create('Universalscrapers Testing mode active', 'please wait')
	match = re.findall('<div class="info_wrapper">.+?href="(.+?)".+?alt="(.+?)"',html,re.DOTALL)
	index = len(match)
	for url, name in match:
		Scrapers_Run = 0
		count+= 1
		if pDialog.iscanceled():
			break
		html2 = requests.get('https://www.themoviedb.org'+url).content
		match2 = re.findall('<title>(.+?)\((.+?)\)',html2)
		for title,year in match2:
			title = title[:-1]
			movie_links_scraper = universalscrapers.scrape_movie(title, year, '')
			movie_links_scraper = movie_links_scraper()
			pDialog.update((index / count) * 100, "Scraping Movie {} of {}".format(count, index), title)
			for links in movie_links_scraper:
				Scrapers_Run += 1
				pDialog.update((index / count) * 100, "Scraping Movie {} of {}".format(count, index), title + ' | '+str(int(Scrapers_Run))+'/'+str(len(No_of_scrapers)))	
	get_scraper_results()

def tmdb_tv_shows(html):
	match = re.findall('<div class="info_wrapper">.+?href="(.+?)".+?alt="(.+?)"',html,re.DOTALL)
	
def single_test(count, index):
	if count==5:
		pass
	else:
		Scrapers_Run = 0
		Movies = movies[count]
		tv_shows = shows[count]
		pDialog.create('Universalscrapers Testing mode active', 'please wait')
		if dialog.yesno("Universalscrapers Testing Mode", 'Run next Movie?',Movies['title']+' ('+Movies['year']+')'):
			movie_links_scraper = universalscrapers.scrape_movie(Movies['title'], Movies['year'], Movies['imdb'])
			movie_links_scraper = movie_links_scraper()
			pDialog.update((index / num_shows) * 100, "Scraping Movie {} of {}".format(index, num_shows), Movies['title'])
			index += 1
			for links in movie_links_scraper:
				Scrapers_Run += 1
				pDialog.update((index / num_shows) * 100, "Scraping Movie {} of {}".format(index, num_shows), Movies['title'] + ' | '+str(int(Scrapers_Run))+'/'+str(len(No_of_scrapers)))	
		Scrapers_Run = 0
		if dialog.yesno("Universalscrapers Testing Mode", 'Would you like to run a tv show?',
		tv_shows['title']+' ('+tv_shows['year']+') S'+tv_shows['season']+'E'+tv_shows['episode']):
			episode_links_scraper = universalscrapers.scrape_episode(tv_shows['title'], tv_shows['show_year'], tv_shows['year'], tv_shows['season'], tv_shows['episode'], tv_shows['imdb'],'')
			episode_links_scraper = episode_links_scraper()
			pDialog.update((index / num_shows) * 100, "Scraping TV Show {} of {}".format(index, num_shows), tv_shows['title'])
			index += 1
			for links in episode_links_scraper:
				Scrapers_Run += 1
				pDialog.update((index / num_shows) * 100, "Scraping TV Show {} of {}".format(index, num_shows), tv_shows['title'] + ' | '+str(int(Scrapers_Run))+'/'+str(len(No_of_scrapers)))	
		else:
			get_scraper_results()
			return
		count += 1
		single_test(count, index)

def full_test():
	index = 0
	pDialog.create('Universalscrapers Testing mode active', 'please wait')
	for item in movies:
		Scrapers_Run = 0
		if pDialog.iscanceled():
			break
		movie_links_scraper = universalscrapers.scrape_movie(item['title'], item['year'], item['imdb'])
		movie_links_scraper = movie_links_scraper()
		pDialog.update((index / num_shows) * 100, "Scraping Movie {} of {}".format(index, num_shows), item['title'])
		index += 1
		for links in movie_links_scraper:
			Scrapers_Run += 1
			pDialog.update((index / num_shows) * 100, "Scraping Movie {} of {}".format(index, num_shows), item['title'] + ' | '+str(int(Scrapers_Run))+'/'+str(len(No_of_scrapers)))
	for item in shows:
		Scrapers_Run = 0
		if pDialog.iscanceled():
			break
		episode_links_scraper = universalscrapers.scrape_episode(item['title'], item['show_year'], item['year'], item['season'], item['episode'], item['imdb'],'')
		episode_links_scraper = episode_links_scraper()
		pDialog.update((index / num_shows) * 100, "Scraping TV Show {} of {}".format(index, num_shows), item['title'])
		index += 1
		for links in episode_links_scraper:
			Scrapers_Run += 1
			pDialog.update((index / num_shows) * 100, "Scraping TV Show {} of {}".format(index, num_shows), item['title'] + ' | '+str(int(Scrapers_Run))+'/'+str(len(No_of_scrapers)))
	get_scraper_results()
	
if __name__ == '__main__':
    main()
