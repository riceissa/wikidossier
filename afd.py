import re
import requests
import logging
import util
import datetime

'''
Sample usage:

>>> import afd
>>> lst = afd.get_afd_list()
>>> a = afd.AfD(lst[0])
>>> a.title
'Wikipedia:Articles for deletion/1998 Piruetten'
>>> a.get_nominator()
'Sportsfan 1234'
>>> a.get_votes()
[(None, 'Gab4gab'), ('keep', 'Hergilei'), ('keep', 'Smartyllama')]
'''

def title_generator(start=datetime.datetime(2004, 12, 25),
        end=datetime.datetime.today()):
    '''
    Yield a generator that returns all Wikipedia "Articles for deletion" daily
    log pages in order between start and end (inclusive).

    >>> g = title_generator()
    >>> next(g)
    'Wikipedia:Articles for deletion/Log/2004 December 25'
    '''
    curr = start
    while curr <= end:
        title_prefix = "Wikipedia:Articles for deletion/Log/"
        yield title_prefix + curr.strftime("%Y %B %-d")
        curr += datetime.timedelta(days=1) # go on to the next day

def print_afd_votes(start=datetime.datetime(2004, 12, 25)):
    '''
    TODO write docstring
    '''
    for title in title_generator():

def get_afd_list(title="User:Cyberbot I/Current AfD's", exclude_logs=False,
        lang="en"):
    '''
    Return a list of AfDs by parsing the wikitext of title.

    The default title string, "User:Cyberbot I/Current AfD's", is just a page
    that lists all the currently-running AfDs. Another page that is useful as a
    starting point is "Wikipedia:Articles for deletion/Log", which links out to
    all the daily logs, so run once with exclude_logs=False to get all the
    daily log pages, then loop over each of the resulting titles and run with
    exclude_logs=True to get a list of all the actual discussion pages.
    '''
    payload = {
            'action': 'parse',
            'format': 'json',
            'contentmodel': 'wikitext',
            'prop': 'links',
            'page': title,
    }
    r = requests.get('http://{}.wikipedia.org/w/api.php'.format(lang),
            params=payload, headers=util.HEADERS)
    j = r.json()
    result = []
    for link in j.get('parse', {}).get('links', {}):
        t = link.get('*', "")
        if exclude_logs:
            if (t.startswith("Wikipedia:Articles for deletion/") and
                    not t.startswith("Wikipedia:Articles for deletion/Log/")):
                result.append(t)
        else:
            if t.startswith("Wikipedia:Articles for deletion/"):
                result.append(t)
    return result

class AfD(object):
    '''
    Represents an "Articles for deletion" page on Wikipedia.
    '''
    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return self.title

    def get_nominator(self, lang="en"):
        '''
        Return the username of the nominator of the AfD given by title. For the
        purposes of this function, we assume that "nominator of the AfD" is the
        same as the user that creates the AfD (i.e. the user that creates the
        page).
        '''
        payload = {
                'prop': 'revisions',
                'titles': self.title,
                'rvprop': 'user',
                'rvlimit': 1,       # We only care about the first edit
                'rvdir': 'newer',   #   to the page
        }
        for result in util.query(payload, sleep=0):
            try:
                # We only requested one page, so just retrieve that from the mess
                # of JSON
                assert len(result['pages']) == 1
                v = list(result['pages'].values())[0]

                # Again, we only requested one revision, so just get the username
                # from that
                assert self.title == v['title']
                assert len(v['revisions']) == 1
                return v['revisions'][0]['user']
            except Exception as e:
                logging.warning("Something went wrong for page %s; %s: %s",
                        self.title, e.__class__.__name__, e)
                logging.warning(str(result))

    def get_page(self, lang="en"):
        '''
        Return the wikitext of title.
        '''
        payload = {
                'action': 'parse',
                'format': 'json',
                'contentmodel': 'wikitext',
                'prop': 'wikitext',
                'page': self.title,
        }
        r = requests.get('http://{}.wikipedia.org/w/api.php'.format(lang),
                params=payload, headers=util.HEADERS)
        j = r.json()
        return j.get('parse', {}).get('wikitext', {}).get('*', "")

    def get_votes(self, normalize=True, lang="en"):
        return votes(self.get_page(lang), normalize=normalize)

def votes(wikitext, normalize=True):
    '''
    Given the wikitext of an AfD page, return a list of tuples (vote, username)
    for votes in the AfD.
    '''
    # Modified from
    # https://github.com/APerson241/afdstats/blob/d1932ecf5447d2b621dce99c982da7cb877d3778/public_html/afdstats.py#L139-L140
    # Remove all parts tagged as strikeouts
    wikitext = re.sub("<(s|strike|del)>.*?</(s|strike|del)>", "", wikitext,
            flags=re.IGNORECASE|re.DOTALL)
    votes = re.findall(r"""
            ^\*?[ ]*'''(.*?)''' # capture the vote
            .*?\[\[User[^[\]]*?:([^[\]]*?)(?:\|[^[\]]*?)?\]\] # capture username
            [^[\]]*?\(UTC\)""", wikitext,
            flags=re.VERBOSE|re.IGNORECASE|re.MULTILINE)
    if normalize:
        votes = [(normalized_vote(v), u) for v, u in votes]
    return votes

def normalized_vote(vote):
    '''
    Take an AfD vote as a string. Return one of "keep", "delete", "merge",
    "redirect", or None (for everything else, including comments), in that
    order of precedence.
    '''
    vote = vote.lower()
    if "keep" in vote:
        return "keep"
    if "delete" in vote:
        return "delete"
    if "merge" in vote:
        return "merge"
    if "redirect" in vote:
        return "redirect"
    else:
        return None
