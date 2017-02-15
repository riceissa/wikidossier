import re
import requests
import logging
import util

'''
Sample usage:

>>> m = map(votes, map(get_page, get_afd_list()))
>>> all_votes = list(m)
'''

def get_afd_list(title="User:Cyberbot I/Current AfD's", lang="en"):
    '''
    Return a list of AfDs by parsing the wikitext of title.
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
        if t.startswith("Wikipedia:Articles for deletion/"):
            result.append(t)
    return result

def get_nominator(title, lang="en"):
    '''
    Return the username of the nominator of the AfD given by title. For the
    purposes of this function, we assume that "nominator of the AfD" is the
    same as the user that creates the AfD (i.e. the user that creates the
    page).
    '''
    payload = {
            'prop': 'revisions',
            'titles': title,
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
            assert title == v['title']
            assert len(v['revisions']) == 1
            return v['revisions'][0]['user']
        except Exception as e:
            logging.warning("Something went wrong for page %s; %s: %s",
                    title, e.__class__.__name__, e)
            logging.warning(str(result))

def get_page(title, lang="en"):
    '''
    Return the wikitext of title.
    '''
    payload = {
            'action': 'parse',
            'format': 'json',
            'contentmodel': 'wikitext',
            'prop': 'wikitext',
            'page': title,
    }
    r = requests.get('http://{}.wikipedia.org/w/api.php'.format(lang),
            params=payload, headers=util.HEADERS)
    j = r.json()
    return j.get('parse', {}).get('wikitext', {}).get('*', "")

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
        # Just some rudimentary normalization for now
        votes = [(v.lower(), u) for v, u in votes]
    return votes
