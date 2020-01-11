# -*- coding: utf-8 -*-

import abc
import xbmcaddon

abstractstaticmethod = abc.abstractmethod
class abstractclassmethod(classmethod):
    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)

class Scraper:
    __metaclass__ = abc.ABCMeta
    domains = ['localdomain']
    name = "Scraper"

    @classmethod
    def get_setting(cals, key):
        return xbmcaddon.Addon('script.module.universalscrapers').getSetting(key)

    @classmethod
    def _is_enabled(clas):
        return clas.get_setting(clas.name + '_enabled') == 'true'

    @classmethod
    def get_settings_xml(clas):
        xml = [
            '<setting id="%s_enabled" ''type="bool" label="Enabled" default="true"/>' % (clas.name)
        ]
        return xml

    def scrape_movie(self, title, year, imdb, debrid = False):
        """
    scrapes scraper site for movie links
    Args:
        title: movie title -> str
        year: year the movie came out -> str
        imdb: imdb identifier -> str
        debrid: boolean indicating whether to use debrid links if available -> bool
    Returns:
        a list of video sources represented by dicts with format:
          {'source': video source (str), 'quality': quality (str), 'scraper': scraper name (str) , 'url': url (str), 'direct': bool}
        """
        pass

    def scrape_episode(self,title, show_year, year, season, episode, imdb, tvdb, debrid = False):
        """
    scrapes scraper site for episode links
    Args:
        title: title of the tv show -> str
        show_year: year tv show started -> str
        year: year episode premiered -> str
        season: season number of the episode -> str
        episode: episode number -> str
        imdb: imdb identifier -> str
        tvdb: tvdb identifier -> str
        debrid: boolean indicating whether to use debrid links if available -> bool
    Returns:
        a list of video sources represented by dicts with format:
          {'source': video source (str), 'quality': quality (str), 'scraper': scraper name (str) , 'url': url (str), 'direct': bool}
        """
        pass

    def scrape_music(self, title, artist, debrid = False):
        """
    scrapes scraper site for song links
    Args:
        title: song title -> str
        artist: song artist -> str
        debrid: boolean indicating whether to use debrid links if available -> bool
    Returns:
        a list of music sources represented by dicts with format:
          {'source': music source (str), 'quality': quality (str), 'scraper': scraper name (str) , 'url': url (str), 'direct': bool}
        """
        pass
