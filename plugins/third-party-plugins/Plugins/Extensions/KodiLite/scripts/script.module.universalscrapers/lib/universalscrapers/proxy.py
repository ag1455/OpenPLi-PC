import random
import urllib
import urllib2
import urlparse

from universalscrapers.common import random_agent


def get(url, check, headers=None, data=None):
    if headers is None:
        headers = {
            'User-Agent': random_agent(),
        }
        try:
            request = urllib2.Request(url, headers=headers, data=data)
            html = urllib2.urlopen(request, timeout=10).read()
            if check in str(html): return html
        except:
            pass

    try:
        new_url = get_proxy_url() % urllib.quote_plus(url)
        headers['Referer'] = 'http://%s/' % urlparse.urlparse(new_url).netloc
        request = urllib2.Request(new_url, headers=headers)
        response = urllib2.urlopen(request, timeout=10)
        html = response.read()
        response.close()
        if check in html: return html
    except:
        pass

    try:
        new_url = get_proxy_url() % urllib.quote_plus(url)
        headers['Referer'] = 'http://%s/' % urlparse.urlparse(new_url).netloc
        request = urllib2.Request(new_url, headers=headers)
        html = urllib2.urlopen(request, timeout=10).read()
        if check in html: return html
    except:
        pass

    return


def get_raw(url, headers=None, data=None):
    if headers is None:
        headers = {
            'User-Agent': random_agent(),
        }

    try:
        new_url = get_proxy_url() % urllib.quote_plus(url)
        headers['Referer'] = 'http://%s/' % urlparse.urlparse(new_url).netloc
        request = urllib2.Request(new_url, headers=headers)
        response = urllib2.urlopen(request, timeout=10)
        return response
    except:
        pass


def get_proxy_url():
    return random.choice([
        'http://www.ultrabestproxy.com/index.php?q=%s&hl=3ed'
        'http://proxite.net/browse.php?u=%s&b=5&f=norefer',   
        'http://unblockthatsite.net/browse.php?u=%s&b=0&f=norefer',
        'http://ocaspro.com/browse.php?u=%s&b=13&f=norefer',
        'http://coolbits.org/browse.php?u=%s&b=0&f=norefer',
        'http://www.agorafunfa.com/browse.php?u=%s&b=29&f=norefer',
        'http://www.ultrabestproxy.com/index.php?q=%s&hl=3ed',
        'http://www.englandproxy.co.uk/%s',
         
    ])
