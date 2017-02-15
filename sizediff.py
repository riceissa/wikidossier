#!/usr/bin/python3

import argparse
import sys
import logging

import util

MAINSPACE = 0
TALKSPACE = 1
USERSPACE = 2
USERTALKSPACE = 3

def main():
    parser = argparse.ArgumentParser(description="Generate a TSV " +
            "about the given users' contributions.")
    parser.add_argument("usersfile", nargs="?", type=argparse.FileType("r"),
            default=sys.stdin, help="file containing list of usernames " +
            "for which to " +
            "print contributions, one username per line; reads " +
            "from stdin if not given")
    parser.add_argument("--debug", help="print debug statements",
            action="store_const", dest="loglevel", const=logging.DEBUG,
            default=logging.WARNING)
    parser.add_argument("-v", "--verbose", help="be verbose",
            action="store_const", dest="loglevel", const=logging.INFO)
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    for line in args.usersfile:
        u = line.strip()
        process_user(u)

def process_user(username):
    # For parameters, see https://www.mediawiki.org/wiki/API%3aUsercontribs
    ucpayload = {
            'list': 'usercontribs',
            'ucprop': 'sizediff|timestamp|ids|title',
            'ucuser': username,
            'uclimit': 100,
    }
    for result in util.query(ucpayload, sleep=0):
        for i in result['usercontribs']:
            try:
                print("\t".join(map(str, [
                    username,
                    i['ns'],
                    i['timestamp'],
                    i['sizediff'],
                ])))
            except Exception as e:
                logging.warning("Something went wrong for user %s; %s: %s",
                        username, e.__class__.__name__, e)
                logging.warning(str(i))

if __name__ == "__main__":
    main()
