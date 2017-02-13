#!/usr/bin/python3

import pandas as pd
import matplotlib.pyplot as plt

import util

df = pd.read_csv("contribs.tsv", sep="\t")
df['timestamp'] = pd.to_datetime(df['timestamp'])
ts_df = df.set_index('timestamp').sort_index()
