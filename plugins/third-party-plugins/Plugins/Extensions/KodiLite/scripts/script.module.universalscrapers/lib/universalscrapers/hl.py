# -*- coding: utf-8 -*-
import datetime
import json
import os
import re
from threading import Event

from universalscrapers.common import clean_title

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

import universalscrapers
import dialogs
import xbmc
import xbmcaddon
import xbmcvfs
import random

from executor import execute

scraper_cache = {}


class HostedLink:
    def __init__(self, title, year, imdb=None, tvdb=None, host=None, include_disabled=False, timeout=30, exclude=None, enable_debrid=False):
        self.title = title
        self.year = year
        self.imdb = imdb
        self.tvdb = tvdb
        self.host = host
        self.timeout = timeout
        self.debrid = enable_debrid
        self.__scrapers = self.__get_scrapers(include_disabled, exclude)
        random.shuffle(self.__scrapers)
        xbmcvfs.mkdir(xbmc.translatePath(xbmcaddon.Addon("script.module.universalscrapers").getAddonInfo('profile')))
        self.cache_location = os.path.join(
            xbmc.translatePath(xbmcaddon.Addon("script.module.universalscrapers").getAddonInfo('profile')).decode('utf-8'),
            'url_cache.db')

    def __get_scrapers(self, include_disabled, exclude):
        klasses = universalscrapers.relevant_scrapers(self.host, include_disabled, exclude=exclude)
        scrapers = []
        for klass in klasses:
            if klass in scraper_cache:
                scrapers.append(scraper_cache[klass])
            else:
                scraper_cache[klass] = klass()
                scrapers.append(scraper_cache[klass])
        return scrapers

    def get_scrapers(self):
        return self.__get_scrapers(True, None)

    def scrape_movie(self, maximum_age=60):
        scrape_f = lambda p: self.get_url(p, self.title, '', self.year, '', '', self.imdb, self.tvdb, "movie",
                                          self.cache_location, maximum_age, debrid = self.debrid)
        if len(self.__scrapers) > 0:
            pool_size = 10
            stop_flag = Event()
            populator = lambda: execute(scrape_f, self.__scrapers, stop_flag, pool_size, self.timeout)
            return populator
        else:
            return False

    def scrape_movie_with_dialog(self, maximum_age=60, sort_function=None, check_url=False, extended=False):
        scrape_f = lambda p: self.to_dialog_tuple(
            self.get_url(p, self.title, '', self.year, '', '', self.imdb, self.tvdb, "movie",
                         self.cache_location, maximum_age, check_url, debrid = self.debrid))
        if len(self.__scrapers) > 0:
            pool_size = 10
            stop_flag = Event()
            populator = lambda: execute(scrape_f, self.__scrapers, stop_flag, pool_size, self.timeout)
            if populator:
                selected, items = dialogs.select_ext("Select Link", populator, len(self.__scrapers), sort_function)
                stop_flag.set()
                if extended:
                    return selected, items
                return selected
            return False

    def scrape_episode(self, show_year, season, episode, maximum_age=60):
        scrape_f = lambda p: self.get_url(p, self.title, show_year, self.year, season, episode, self.imdb, self.tvdb,
                                          "episode",
                                          self.cache_location, maximum_age, debrid = self.debrid)
        if len(self.__scrapers) > 0:
            pool_size = 10
            stop_flag = Event()
            populator = lambda: execute(scrape_f, self.__scrapers, stop_flag, pool_size, self.timeout)
            return populator
        else:
            return False

    def scrape_episode_with_dialog(self, show_year, season, episode, maximum_age=60, sort_function=None, check_url=False, extended = False):
        scrape_f = lambda p: self.to_dialog_tuple(
            self.get_url(p, self.title, show_year, self.year, season, episode, self.imdb, self.tvdb, "episode",
                         self.cache_location, maximum_age, check_url, debrid = self.debrid))
        if len(self.__scrapers) > 0:
            pool_size = 10
            stop_flag = Event()
            populator = lambda: execute(scrape_f, self.__scrapers, stop_flag, pool_size, self.timeout)
            if populator:
                selected, items = dialogs.select_ext("Select Link", populator, len(self.__scrapers), sort_function)
                stop_flag.set()
                if extended:
                    return selected, items
                return selected
            return False

    def scrape_song(self, title, artist, maximum_age=60):
        scrape_f = lambda p: self.get_muscic_url(p, title, artist, self.cache_location, maximum_age, debrid = self.debrid)
        if len(self.__scrapers) > 0:
            pool_size = 10
            stop_flag = Event()
            populator = lambda: execute(scrape_f, self.__scrapers, stop_flag, pool_size, self.timeout)
            return populator
        else:
            return False

    def scrape_song_with_dialog(self, title, artist, maximum_age=60, sort_function=None, extended=False):
        scrape_f = lambda p: self.to_dialog_tuple(
            self.get_muscic_url(p, title, artist, self.cache_location, maximum_age, debrid = self.debrid))
        if len(self.__scrapers) > 0:
            pool_size = 10
            stop_flag = Event()
            populator = lambda: execute(scrape_f, self.__scrapers, stop_flag, pool_size, self.timeout)
            if populator:
                selected, items = dialogs.select_ext("Select Link", populator, len(self.__scrapers), sort_function)
                stop_flag.set()
                if extended:
                    return selected, items
                return selected
            return False

    @staticmethod
    def get_url(scraper, title, show_year, year, season, episode, imdb, tvdb, type, cache_location, maximum_age, check_url = False, debrid = False):
        cache_enabled = xbmcaddon.Addon('script.module.universalscrapers').getSetting("cache_enabled") == 'true'
        try:
            dbcon = database.connect(cache_location)
            dbcur = dbcon.cursor()
            try:
                dbcur.execute("SELECT * FROM version")
                match = dbcur.fetchone()
            except:
                universalscrapers.clear_cache()
                dbcur.execute("CREATE TABLE version (""version TEXT)")
                dbcur.execute("INSERT INTO version Values ('0.5.4')")
                dbcon.commit()

            dbcur.execute(
                "CREATE TABLE IF NOT EXISTS rel_src (""scraper TEXT, ""title Text, show_year TEXT, year TEXT, ""season TEXT, ""episode TEXT, ""imdb_id TEXT, ""urls TEXT, ""added TEXT, ""UNIQUE(scraper, title, year, season, episode)"");")
        except:
            pass

        if cache_enabled:
            try:
                sources = []
                dbcur.execute(
                    "SELECT * FROM rel_src WHERE scraper = '%s' AND title = '%s' AND show_year= '%s' AND year = '%s' AND season = '%s' AND episode = '%s'" % (
                        scraper.name, clean_title(title).upper(), show_year, year, season, episode))
                match = dbcur.fetchone()
                t1 = int(re.sub('[^0-9]', '', str(match[8])))
                t2 = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
                update = abs(t2 - t1) > maximum_age
                if update == False:
                    sources = json.loads(match[7])
                    return sources
            except:
                pass

        try:
            sources = []
            if type == "movie":
                sources = scraper.scrape_movie(title, year, imdb, debrid = debrid)
            elif type == "episode":
                sources = scraper.scrape_episode(title, show_year, year, season, episode, imdb, tvdb, debrid = debrid)
            if sources == None:
                sources = []
            else:
                if cache_enabled:
                    try:
                        dbcur.execute(
                            "DELETE FROM rel_src WHERE scraper = '%s' AND title = '%s' AND show_year= '%s' AND year = '%s' AND season = '%s' AND episode = '%s'" % (
                                scraper.name, clean_title(title).upper(), show_year, year, season, episode))
                        dbcur.execute("INSERT INTO rel_src Values (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                            scraper.name, clean_title(title).upper(), show_year, year, season, episode, imdb,
                            json.dumps(sources),
                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
                        dbcon.commit()
                    except:
                        pass

            if check_url:
                noresolver = False
                try:
                    import resolveurl as urlresolver
                except:
                    try:
                        import urlresolver as urlresolver
                    except:
                        noresolver = True
                new_sources = []
                from common import check_playable
                for source in sources:
                    if source["direct"]:
                        check = check_playable(source["url"])
                        if check:
                            new_sources.append(source)
                    elif not noresolver:
                        try:
                            hmf = urlresolver.HostedMediaFile(url=source['url'], include_disabled=False,
                                                         include_universal=False)
                            if hmf.valid_url():
                                resolved_url = hmf.resolve()
                                check = check_playable(resolved_url)
                                if check:
                                    new_sources.append(source)
                        except:
                            pass
                    else:
                        new_sources.append(source)
                sources = new_sources
            return sources
        except:
            pass

    @staticmethod
    def get_muscic_url(scraper, title, artist, cache_location, maximum_age, debrid = False):
        cache_enabled = xbmcaddon.Addon('script.module.universalscrapers').getSetting("cache_enabled") == 'true'
        try:
            dbcon = database.connect(cache_location)
            dbcur = dbcon.cursor()

            try:
                dbcur.execute("SELECT * FROM version")
                match = dbcur.fetchone()
            except:
                universalscrapers.clear_cache()
                dbcur.execute("CREATE TABLE version (""version TEXT)")
                dbcur.execute("INSERT INTO version Values ('0.5.4')")
                dbcon.commit()

            dbcur.execute(
                "CREATE TABLE IF NOT EXISTS rel_music_src (""scraper TEXT, ""title Text, ""artist TEXT, ""urls TEXT, ""added TEXT, ""UNIQUE(scraper, title, artist)"");")
        except:
            pass

        if cache_enabled:
            try:
                sources = []
                dbcur.execute(
                    "SELECT * FROM rel_music_src WHERE scraper = '%s' AND title = '%s' AND artist = '%s'" % (
                        scraper.name, clean_title(title).upper(), artist.upper()))
                match = dbcur.fetchone()
                t1 = int(re.sub('[^0-9]', '', str(match[4])))
                t2 = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
                update = abs(t2 - t1) > maximum_age
                if update == False:
                    sources = json.loads(match[3])
                    return sources
            except:
                pass

        try:
            sources = scraper.scrape_music(title, artist, debrid = debrid)
            if sources == None:
                sources = []
            else:
                if cache_enabled:
                    dbcur.execute(
                        "DELETE FROM rel_music_src WHERE scraper = '%s' AND title = '%s' AND artist = '%s'" % (
                            scraper.name, clean_title(title).upper(), artist.upper))
                    dbcur.execute("INSERT INTO rel_music_src Values (?, ?, ?, ?, ?)", (
                        scraper.name, clean_title(title).upper(), artist.upper(), json.dumps(sources),
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
                    dbcon.commit()

            return sources
        except:
            pass

    def to_dialog_tuple(self, scraper_array):
        results_array = []
        if scraper_array:
            labels = {}
            for link in scraper_array:
                quality = ""
                try:
                    quality = str(int(link['quality'])) + "p"
                except:
                    quality = link['quality']
                if not quality:
                    quality = "SD"
                label = link["scraper"] + " | " + link["source"] + " | " + " " + quality + ""
                if link.get("debridonly", ""):
                    label += "  | DEBRID"
                # grouping_label = link["source"] + " (" + quality + ")"
                # if not grouping_label in labels:
                #     labels[grouping_label] = []
                # labels[grouping_label].append(link)
                results_array.append((label, [link]))
            # for label, links in labels.iteritems():
            #     if len(links) > 1:
            #         result_links = []
            #         for link in links:
            #             label2 = label.replace("(", " - " + link["scraper"] + " (")
            #             result_links.append({'label': label2, 'path': link})
            #         results_array.append((label, result_links))
            #     else:
            #         label2 = label.replace("(", " - " + links[0]["scraper"] + " (")
            #         results_array.append((label2, links))
            return results_array
