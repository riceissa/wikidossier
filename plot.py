#!/usr/bin/python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import util

# df = pd.read_csv("big_contribs.tsv", sep="\t")
# df['timestamp'] = pd.to_datetime(df['timestamp'])
# ts_df = df.set_index('timestamp').sort_index()
# ts_df['ns_str'] = ts_df.ns.map(lambda x: util.NAMESPACES_INV_MAP[x])
# df = ts_df.set_index(ts_df.index.tz_localize('UTC').tz_convert('US/Pacific'))

def ns2color(ns):
    '''
    Take namespace as integer and return a string naming a fixed color for that
    namespace.
    '''
    # These colors are from https://tools.wmflabs.org/xtools-ec/ because I use
    # that tool a lot and it would be confusing to have different colors
    cs = {
        0: "#CC0000",
        1: "#F7B7B7",
        2: "#5C8D20",
        3: "#85ED82",
        4: "#2E97E0",
        5: "#B9E3F9",
        6: "#E1711D",
        7: "#FFC04C",
        8: "#FDFF98",
        9: "#5555FF",
        10: "#55FFFF",
        11: "#0000C0",
        12: "#008800",
        13: "#00C0C0",
        14: "#FFAFAF",
        15: "#808080",
        100: "#75A3D1",
        101: "#A679D2",
        108: "",
        109: "",
        118: "#99FFFF",
        119: "#99BBFF",
        446: "",
        447: "",
        710: "",
        711: "",
        828: "",
        829: "",
        2300: "",
        2301: "",
        2302: "",
        2303: "",
    }
    ret = cs.get(ns, "")
    if ret:
        return ret
    return "black"

def timeseries_df(df, pacific_timezone=False):
    '''
    Return a copy of the DataFrame where the "timestamp" column is used as a
    DatetimeIndex. If pacific_timezone is true, localize the times to the
    US/Pacific timezone.

    Side effect: the original df's "timestamp" column will be converted to
    datetime objects.
    '''
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    ret = df.set_index('timestamp').sort_index()
    if pacific_timezone:
        ret = ret.set_index(ret.index.tz_localize('UTC').tz_convert('US/Pacific'))
    return ret

def plot_from(path, user, limit=10000000, minlimit=0):
    lst = []
    with open(path, "r") as f:
        for line in f:
            lst.append(int(line.strip()))
    plot_lst = [i for i in lst if abs(i) < limit and abs(i) > minlimit]
    plt.hist(plot_lst, bins=50)
    plt.title(user + " sizediff histogram,\n" + "limit=" + str(limit) +
            ", minlimit=" + str(minlimit) +
            ", showing {} edits".format(len(plot_lst)))
    plt.show()

def plot_user_cumsum_sizediff(u):
    '''
    Plot the cumulative sum of sizediff as timeseries for user u.
    '''
    for i in ts_df[ts_df.username == u].ns.unique():
        if i < 20:
            ts = ts_df[(ts_df.username == u) & (ts_df.ns == i)]
            ts.sizediff.cumsum().plot(
                    label=util.NAMESPACES_INV_MAP[i],
                    legend=True,
                    color=ns2color(i),
                    title=u)
    plt.legend(bbox_to_anchor=(0.5, -0.08), loc='upper center', ncol=3)

def plot_all_users_cumsum_sizediff(ns):
    '''
    Plot the cumulative sum of sizediff as timeseries for namespace ns.
    '''
    for key, g in ts_df[ts_df.ns == ns].groupby('username').sizediff:
        gcs = g.cumsum()
        gcs.plot(legend=False, label=key)
        plt.text(g.index.values[-1], gcs[-1], key)

def plot_punchcard(df, normalize=None):
    '''
    Plot the punchcard (sometimes called "time card") for DataFrame df. If
    normalize is passed, the normalized area of the dots will be scaled by
    normalize.
    '''
    g = df.groupby([df.index.hour, df.index.dayofweek]).size()
    # Fill in sizes of the dots
    sizes = []
    for hour in range(24):
        for week in range(7):
            if hour in g and week in g[hour]:
                sizes.append(g[hour][week])
            else:
                sizes.append(0)
    if normalize:
        sizes = np.divide(sizes, g.max()) * normalize
    # The order of plotting the points is (h=0, w=0), (h=0, w=1), and so on
    plt.scatter(
        [h for h in range(24) for w in range(7)],
        list(range(7))*24,
        s=sizes
    )
    plt.yticks(list(range(7)), ['Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday', 'Sunday'])
    label_hrs = list(range(0, 24, 2))
    plt.xticks(label_hrs, label_hrs)
