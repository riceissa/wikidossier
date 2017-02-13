#!/usr/bin/python3

import time
import requests
import sys
import logging
from itertools import zip_longest

HEADERS = {
        'User-Agent': 'WikipediaArchive/0.1 ' +
            '(https://exp.issarice.com/wikipedia-archive.txt; ' +
            'riceissa@gmail.com) ' +
            'BasedOnpython-requests/' + str(requests.__version__),
}

NAMESPACES = [
    "Main",
    "Talk",
    "User",
    "User talk",
    "Wikipedia",
    "Wikipedia talk",
    "File",
    "File talk",
    "MediaWiki",
    "MediaWiki talk",
    "Template",
    "Template talk",
    "Help",
    "Help talk",
    "Category",
    "Category talk",
    "Portal",
    "Portal talk",
    "Book",
    "Book talk",
    "Draft",
    "Draft talk",
    "Education Program",
    "Education Program talk",
    "TimedText",
    "TimedText talk",
    "Module",
    "Module talk",
    "Gadget",
    "Gadget talk",
    "Gadget definition",
    "Gadget definition talk",
]

# Modified from https://www.mediawiki.org/wiki/API:Query#Continuing_queries
def query(request, lang="en", sleep=1):
    request['action'] = 'query'
    request['format'] = 'json'
    lastContinue = {'continue': ''}
    iteration = 0
    while True:
        # Clone original request
        req = request.copy()
        # Modify it with the values returned in the 'continue' section of the
        # last result.
        req.update(lastContinue)
        # Call API
        r = requests.get('http://{}.wikipedia.org/w/api.php'.format(lang),
                params=req, headers=HEADERS)
        result = r.json()
        logging.info("ON ITERATION %s, SLEEPING FOR %s", iteration, sleep)
        time.sleep(sleep)
        iteration += 1
        if 'error' in result:
            raise ValueError(r.url, result['error'])
        if 'warnings' in result:
            logging.warning(result['warnings'])
        if 'query' in result:
            yield result['query']
        if 'continue' not in result:
            break
        lastContinue = result['continue']

# From https://docs.python.org/3/library/itertools.html#itertools-recipes
def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)
