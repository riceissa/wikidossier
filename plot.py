#!/usr/bin/python3

import pandas as pd
import matplotlib.pyplot as plt

import util

df = pd.read_csv("contribs.tsv", sep="\t")
df['timestamp'] = pd.to_datetime(df['timestamp'])
ts_df = df.set_index('timestamp').sort_index()
ts_df['ns_str'] = ts_df.ns.map(lambda x: util.NAMESPACES_INV_MAP[x])
