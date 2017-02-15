import re
import requests
import logging
import util

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

def get_page(title):
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
    return j.get('parse', {}).get('wikitext', "")

def votes(wikitext, normalize=True):
    '''
    Given the wikitext of an AfD page, return a list of tuples (vote, username)
    for votes in the AfD.
    '''
    # Modified from
    # https://github.com/APerson241/afdstats/blob/d1932ecf5447d2b621dce99c982da7cb877d3778/public_html/afdstats.py#L139-L140
    # Remove all parts tagged as strikeouts
    wikitext = re.sub("<(s|strike|del)>.*?</(s|strike|del)>", "", data,
            flags=re.IGNORECASE|re.DOTALL)
    votes = re.findall(
            "\*[ ]*'''(.*?)'''" # capture the vote
            + ".*?\[\[User.*?:(.*?)(?:\|.*?)?\]\]" # capture username
            + ".*?\(UTC\)", data, flags=re.IGNORECASE)
    if normalize:
        # Just some rudimentary normalization for now
        votes = [(v.lower(), u) for v, u in votes]
    return votes
