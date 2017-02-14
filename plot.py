#!/usr/bin/python3

import pandas as pd
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

def plot_all_users_cumsum_sizediff(ns):
    '''
    Plot the cumulative sum of sizediff as timeseries for namespace ns.
    '''
    for key, g in ts_df[ts_df.ns == ns].groupby('username').sizediff:
        gcs = g.cumsum()
        gcs.plot(legend=False, label=key)
        plt.text(g.index.values[-1], gcs[-1], key)
