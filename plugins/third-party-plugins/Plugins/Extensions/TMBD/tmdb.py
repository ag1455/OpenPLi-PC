# -*- coding: UTF-8 -*-

#author:dbr/Ben
#contributors: by ccjensen/Chris
#project:themoviedb
#http://github.com/dbr/themoviedb

"""An interface to the themoviedb.org API
"""
#" + config.plugins.tmbd.locale.value + "
__author__ = "dbr/Ben"
__version__ = "0.2b"
from Plugins.Plugin import PluginDescriptor
from Components.config import config
import os
import struct
import urllib
import urllib2

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


class TmdBaseError(Exception):
    pass


class TmdNoResults(TmdBaseError):
    pass

class TmdHttpError(TmdBaseError):
    pass


class TmdXmlError(TmdBaseError):
    pass


def opensubtitleHashFile(name):
    """Hashes a file using OpenSubtitle's method.

    > In natural language it calculates: size + 64bit chksum of the first and
    > last 64k (even if they overlap because the file is smaller than 128k).

    A slightly more Pythonic version of the Python solution on..
    http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
    """
    longlongformat = 'q'
    bytesize = struct.calcsize(longlongformat)

    f = open(name, "rb")

    filesize = os.path.getsize(name)
    fhash = filesize

    if filesize < 65536 * 2:
       raise ValueError("File size must be larger than %s bytes (is %s)" % (65536*2, filesize))

    for x in range(65536/bytesize):
        buf = f.read(bytesize)
        (l_value,)= struct.unpack(longlongformat, buf)
        fhash += l_value
        fhash = fhash & 0xFFFFFFFFFFFFFFFF # to remain as 64bit number


    f.seek(max(0,filesize-65536),0)
    for x in range(65536/bytesize):
        buf = f.read(bytesize)
        (l_value,)= struct.unpack(longlongformat, buf)
        fhash += l_value
        fhash = fhash & 0xFFFFFFFFFFFFFFFF

    f.close()
    return  "%016x" % fhash


class XmlHandler:
    """Deals with retrieval of XML files from API
    """

    def __init__(self, url):
        self.url = url

    def _grabUrl(self, url):
        try:
            urlhandle = urllib2.urlopen(url)
        except IOError, errormsg:
            raise TmdHttpError(errormsg)
        if urlhandle.code >= 400:
            raise TmdHttpError("HTTP status code was %d" % urlhandle.code)
        return urlhandle.read()

    def getEt(self):
        xml = self._grabUrl(self.url)
        try:
            et = ElementTree.fromstring(xml)
        except SyntaxError, errormsg:
            raise TmdXmlError(errormsg)
        return et


class SearchResults(list):
    """Stores a list of Movie's that matched the search
    """

    def __repr__(self):
        return "<Search results: %s>" % (list.__repr__(self))


class MovieResult(dict):
    """A dict containing the information about a specific search result
    """

    def __repr__(self):
        return "<MovieResult: %s (%s)>" % (self.get("name"), self.get("released"))


class Movie(dict):
    """A dict containing the information about the film
    """

    def __repr__(self):
        return "<MovieResult: %s (%s)>" % (self.get("name"), self.get("released"))


class Categories(dict):

    def __init__(self, type, name, url):
        self['type'] = type
        self['name'] = name.encode("utf-8")
        self['url'] = url

    def __repr__(self):
        if self['type'] is None or self['type'] == "":
            return "%(name)s" % self
        else:
            return "%(name)s" % self

class StudiosList(list):
    def __str__(self):
        return "%s" % (repr(self).replace("[", "").replace("]", "").replace("{", "").replace("}", ""))

class StudiosAttribute(dict):
	def __str__(self):
		try:
			return "%s" % (repr(self).split(",")[0].split(":")[1].replace("[", "").replace("]", "").replace("{", "").replace("}", ""))
		except IndexError:
			return (_('Not available'))        

 


    
class Studios(dict):

    def __init__(self, id, name):
        self['id'] = id
        self['name'] = name.encode("utf-8")

    def __repr__(self):
        if self['id'] is None or self['id'] == "":
            return "%(name)s" % self
        else:
            return "%(name)s" % self 
        
class CountriesAttribute(dict):

    def __str__(self):
        return "%s" % (repr(self).replace("[", "").replace("]", "").replace("{", "").replace("}", "").replace(": None", "").replace("'", ""))

class Countries(CountriesAttribute):
    """Stores country information
    """

    def set(self, country_et):
        """Takes an elementtree Element ('country') and stores the url,
        using the name and code as the dict key.

        For example:
       <country url="http://www.themoviedb.org/encyclopedia/country/223" name="United States of America" code="US"/>

        ..becomes:
        countries['code']['name'] = 'http://www.themoviedb.org/encyclopedia/country/223'
        """

        name = country_et.get("name")
        url = country_et.get("url")
        self.setdefault(name)

        
class Image(dict):
    """Stores image information for a single poster/backdrop (includes
    multiple sizes)
    """

    def __init__(self, _id, _type, size, url):
        self['id'] = _id
        self['type'] = _type

    def largest(self):
        for csize in ["original", "mid", "cover", "thumb"]:
            if csize in self:
                return csize

    def __repr__(self):
        return "<Image (%s for ID %s)>" % (self['type'], self['id'])


class ImagesList(list):
    """Stores a list of Images, and functions to filter "only posters" etc
    """

    def set(self, image_et):
        """Takes an elementtree Element ('image') and stores the url,
        along with the type, id and size.

        Is a list containing each image as a dictionary (which includes the
        various sizes)

        For example:
        <image type="poster" size="original" url="http://images.themoviedb.org/posters/4181/67926_sin-city-02-color_122_207lo.jpg" id="4181"/>

        ..becomes:
        images[0] = {'id':4181', 'type': 'poster', 'original': 'http://images.themov...'}
        """
        _type = image_et.get("type")
        _id = image_et.get("id")
        size = image_et.get("size")
        url = image_et.get("url")

        cur = self.find_by('id', _id)
        if len(cur) == 0:
            nimg = Image(_id = _id, _type = _type, size = size, url = url)
            self.append(nimg)
        elif len(cur) == 1:
            cur[0][size] = url
        else:
            raise ValueError("Found more than one poster with id %s, this should never happen" % (_id))

    def find_by(self, key, value):
        ret = []
        for cur in self:
            if cur[key] == value:
                ret.append(cur)
        return ret

    @property
    def posters(self):
        return self.find_by('type', 'poster')

    @property
    def backdrops(self):
        return self.find_by('type', 'backdrop')

class CrewRoleList(dict):

    def __str__(self):
        return "%s" % (repr(self).replace("[", "").replace("]", "").replace("{", "").replace("}", ""))
  
                    
class CrewList(list):
    """Stores list of crew in specific role

    >>> import tmdb
    >>> tmdb.getMovieInfo(550)['cast']['author']
    [<author (id 7468): Chuck Palahniuk>, <author (id 7469): Jim Uhls>]
    """

    def __str__(self):
        return "%s" % (repr(self).replace("[", "").replace("]", "").replace("{", "").replace("}", ""))


class Person(dict):
    """Stores information about a specific member of cast
    """

    def __init__(self, job, _id, name, character, url):
        self['job'] = job
        self['id'] = _id
        self['name'] = name.encode("utf-8")
        self['character'] = character
        self['url'] = url

    def __repr__(self):
        if self['character'] is None or self['character'] == "":
            return "%(name)s" % self
        else:
            return "%(name)s" % self



class MovieDb:
    """Main interface to www.themoviedb.com

    The search() method searches for the film by title.
    The getMovieInfo() method retrieves information about a specific movie using themoviedb id.
    """

    def _parseSearchResults(self, movie_element):
        cur_movie = MovieResult()
        cur_images = ImagesList()
        for item in movie_element.getchildren():
                if item.tag.lower() == "images":
                    for subitem in item.getchildren():
                        cur_images.set(subitem)
                else:
                    cur_movie[item.tag] = item.text
        cur_movie['images'] = cur_images
        return cur_movie

    def _parseMovie(self, movie_element):
        cur_movie = Movie()
        cur_studios = StudiosAttribute()
        cur_countries = Countries()
        cur_images = ImagesList()
        cur_cast = CrewRoleList()
        for item in movie_element.getchildren():
            if item.tag.lower() == "categories":
                for subitem in item.getchildren():
                    type = subitem.get("type").lower()
                    p = Categories(
                        type = type,
                        url= subitem.get("url"),
                        name = subitem.get("name"),

                    )
                    cur_cast.setdefault(type, CrewList()).append(p)
            elif item.tag.lower() == "studios":
                for subitem in item.getchildren():
                    id = subitem.get("id").lower()
                    p = Studios(
                        id = id,
                        name = subitem.get("name"),

                    )
                    cur_studios.setdefault(id, StudiosList()).append(p)
            elif item.tag.lower() == "countries":
                for subitem in item.getchildren():
                    cur_countries.set(subitem)
            elif item.tag.lower() == "images":
                for subitem in item.getchildren():
                    cur_images.set(subitem)
            elif item.tag.lower() == "cast":
                for subitem in item.getchildren():
                    job = subitem.get("job").lower()
                    p = Person(
                        job = job,
                        _id = subitem.get("id"),
                        name = subitem.get("name"),
                        character = subitem.get("character"),
                        url = subitem.get("url"),
                    )
                    cur_cast.setdefault(job, CrewList()).append(p)
            else:
                 cur_movie[item.tag] = item.text
                

        cur_movie['categories'] = cur_cast
        cur_movie['studios'] = cur_studios
        cur_movie['countries'] = cur_countries
        cur_movie['images'] = cur_images
        cur_movie['cast'] = cur_cast
        return cur_movie

    def search(self, title):
        """Searches for a film by its title.
        Returns SearchResults (a list) containing all matches (Movie instances)
        """
        title = urllib.quote(title)
        url = "http://api.themoviedb.org/2.1/Movie.search/" + config.plugins.tmbd.locale.value + "/xml/a8b9f96dde091408a03cb4c78477bd14/%s"  % (title)
        etree = XmlHandler(url).getEt()
        search_results = SearchResults()
        for cur_result in etree.find("movies").findall("movie"):
            cur_movie = self._parseSearchResults(cur_result)
            search_results.append(cur_movie)
        return search_results

    def getMovieInfo(self, id):
        """Returns movie info by it's TheMovieDb ID.
        Returns a Movie instance
        """
        url = "http://api.themoviedb.org/2.1/Movie.getInfo/" + config.plugins.tmbd.locale.value + "/xml/a8b9f96dde091408a03cb4c78477bd14/%s" % (id)
        etree = XmlHandler(url).getEt()
        moviesTree = etree.find("movies").findall("movie")

        if len(moviesTree) == 0:
            raise TmdNoResults("No results for id %s" % id)

        return self._parseMovie(moviesTree[0])

    def hashGetInfo(self, hash):
        """Returns movie info by it's OpenSubtitle-format hash.
        http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes

        Example hash of "Willow (1988).avi": 00277ff46533b155
        """
        url = "http://api.themoviedb.org/2.1/Hash.getInfo/" + config.plugins.tmbd.locale.value + "/xml/a8b9f96dde091408a03cb4c78477bd14/%s" % (hash)
        etree = XmlHandler(url).getEt()
        moviesTree = etree.find("movies").findall("movie")

        if len(moviesTree) == 0:
            raise TmdNoResults("No results for hash %s" % hash)

        return self._parseMovie(moviesTree[0])


def search(name):
    """Convenience wrapper for MovieDb.search - so you can do..

    >>> import tmdb
    >>> tmdb.search("Fight Club")
    <Search results: [<MovieResult: Fight Club (1999-09-16)>]>
    """
    mdb = MovieDb()
    return mdb.search(name)


def getMovieInfo(id):
    """Convenience wrapper for MovieDb.search - so you can do..

    >>> import tmdb
    >>> tmdb.getMovieInfo(187)
    <MovieResult: Sin City (2005-04-01)>
    """
    mdb = MovieDb()
    return mdb.getMovieInfo(id)


def hashGetInfo(hash):
    """Convenience wrapper for MovieDb.hashGetInfo - so you can do..

    >>> import tmdb
    >>> tmdb.hashGetInfo('00277ff46533b155')
    <MovieResult: Willow (1988-05-20)>
    """
    mdb = MovieDb()
    return mdb.hashGetInfo(hash)


def searchByHashingFile(filename):
    """Searches for the specified file using the OpenSubtitle hashing method
    """
    return hashGetInfo(opensubtitleHashFile(filename))


def main():
    results = search("Fight Club")
    searchResult = results[0]
    movie = getMovieInfo(searchResult['id'])
    print movie['name']

    print "Producers:"
    for prodr in movie['cast']['producer']:
        print " " * 4, prodr['name']
    print movie['images']
    for genreName in movie['categories']['genre']:
        print "%s (%s)" % (genreName, movie['categories']['genre'][genreName])


if __name__ == '__main__':
    main()
