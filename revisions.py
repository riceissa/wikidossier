#!/usr/bin/python3

import argparse
import sys
import logging

import util

def main():
    parser = argparse.ArgumentParser(description="Generate a TSV " +
            "about page revisions.")
    parser.add_argument("pagesfile", nargs="?", type=argparse.FileType("r"),
            default=sys.stdin, help="file containing list of pages " +
            "for which to " +
            "print the revision information, one page per line; reads " +
            "from stdin if not given")
    parser.add_argument("--debug", help="print debug statements",
            action="store_const", dest="loglevel", const=logging.DEBUG,
            default=logging.WARNING)
    parser.add_argument("-v", "--verbose", help="be verbose",
            action="store_const", dest="loglevel", const=logging.INFO)
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    for line in args.pagesfile:
        p = line.strip()
        try:
            process_page(p)
        except Exception as e:
            logging.warning("Could not process %s", p)

def process_page(pagename):
    payload = {
            'prop': 'revisions',
            'titles': pagename,
            'rvprop': 'size|timestamp',
            'rvlimit': 100,
    }
    for result in util.query(payload, sleep=0):
        try:
            # There should only be one thing here, but it's the page id, so
            # let's iterate
            for _, v in result['pages'].items():
                assert pagename == v['title']
                for r in v['revisions']:
                    print("\t".join(map(str, [
                        pagename,
                        r['timestamp'],
                        r['size'],
                    ])))
        except Exception as e:
            logging.warning("Something went wrong for page %s; %s: %s",
                    pagename, e.__class__.__name__, e)
            logging.warning(str(result))

if __name__ == "__main__":
    main()
