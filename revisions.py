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
        process_page(p)

def process_page(pagename):
    payload = {
    }
    for result in util.query(ucpayload, sleep=0):
        pass

if __name__ == "__main__":
    main()
