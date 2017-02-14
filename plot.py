#!/usr/bin/python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import util

df = pd.read_csv("big_contribs.tsv", sep="\t")
df['timestamp'] = pd.to_datetime(df['timestamp'])
ts_df = df.set_index('timestamp').sort_index()
ts_df['ns_str'] = ts_df.ns.map(lambda x: util.NAMESPACES_INV_MAP[x])

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
    Plot the punchcard (sometimes called "time card") for DataFrame df.
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
