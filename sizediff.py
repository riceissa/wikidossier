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
    parser = argparse.ArgumentParser(description="Print Wikipedia pages " +
            "that are related to users.")
    parser.add_argument("--created", action="store_true",
            help="print pages created by the users")
    parser.add_argument("--user_prefix", action="store_true",
            help="print pages with users' prefix")
    parser.add_argument("usersfile", nargs="?", type=argparse.FileType("r"),
            default=sys.stdin, help="file containing list of usernames " +
            "for which to " +
            "print the requested pages, one username per line; reads " +
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
            # 'ucnamespace': MAINSPACE,
            # 'ucdir': 'older',
            # 'ucshow': 'new',
    }
    for result in util.query(ucpayload, sleep=0):
        for i in result['usercontribs']:
            print("\t".join(map(str, [
                username,
                i['ns'],
                i['timestamp'],
                i['sizediff'],
            ])))

    # if user_prefix:
    #     appayload = {
    #             'list': 'allpages',
    #             'aplimit': 100,
    #             'apprefix': username + '/',
    #             'apnamespace': USERSPACE,
    #     }
    #     for result in util.query(appayload):
    #         for i in result['allpages']:
    #             print(i['title'])

def plot_from(path, user, limit=10000000, minlimit=0):
    lst = []
    with open(path, "r") as f:
        for line in f:
            lst.append(int(line.strip()))
    plot_lst = [i for i in lst if abs(i) < limit and abs(i) > minlimit]
    plt.hist(plot_lst, bins=50)
    plt.title(user + " sizediff histogram,\n" + "limit=" + str(limit) + ", minlimit=" + str(minlimit) + ", showing {} edits".format(len(plot_lst)))
    plt.show()

if __name__ == "__main__":
    main()
