#!/usr/bin/python3

# Modified from http://stackoverflow.com/a/10181810/3422337
# See also http://stackoverflow.com/a/14257969/3422337

import matplotlib
matplotlib.use('Agg')

import time
import os.path
from threading import Lock
from flask import Flask, request
import sys
import pandas as pd
import base64
from io import BytesIO

import sizediff
import plot

app = Flask(__name__)

a = 1
b = 2
c = 3
lock = Lock()

@app.route("/user", methods=["GET", "POST"])
def user_front():
    if request.method == "POST":
        username = sanitize_username(request.form['username'])
        if username:
            return hello(username)
        else:
            return "Invalid username"
    page = """<!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
                <title>awesome app</title>
            </head>
            <body>
                <h1>Wikidossier</h1>
                <p>h-hi oniichan, who are you going to make me stalk
                    today? ;_;</p>
                <form method="post">
                    <input type="text" placeholder="Enter valid English Wikipedia username" name="username" style="width: 400px;" autofocus>
                    <input type="submit" value="stalk ’em!">
                </form>
            </body>
        </html>
    """
    return page

@app.route("/user/<username>")
def hello(username):
    username = sanitize_username(username)
    if not username:
        return "Invalid username"
    data_path = "data/" + username
    if os.path.exists(data_path):
        # The server has the data stored, so just read it
        pass
    else:
        # The server does not have the data for this user, so query the API for
        # the data
        with lock:
            # Hack to initialize the file so we can append to it
            with open(data_path, "w") as f:
                f.write("")
            for revision in sizediff.process_user(username):
                with open(data_path, "a") as f:
                    f.write(revision + "\n")
    df = pd.read_csv(data_path, sep="\t", header=None,
            names=["username", "ns", "timestamp", "sizediff"])
    df = plot.timeseries_df(df)
    fig_path = "figs/" + username + ".png"
    bio = BytesIO()
    plot.plot_user_cumsum_sizediff(username, df, figpath=bio, figformat="png")
    plot_data = base64.encodebytes(bio.getvalue()).decode()
    page = """<!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
                <title>result page</title>
            </head>
            <body>
                <h1>info for {}</h1>
                <p><img src="data:image/png;base64,{}" /></p>
            </body>
        </html>
    """
    page = page.format(username, plot_data)
    return page

def sanitize_username(username):
    '''
    Take an English Wikipedia username. If the username is safe, return a
    normalized version of the username. Otherwise return None.
    '''
    username = str(username)
    if username in [".", ".."]:
        return None
    username = username.replace("_", " ")
    bad_chars = set(map(chr, range(32)))
    bad_chars = bad_chars.union(set(map(chr, range(127, 161))))
    bad_chars = bad_chars.union(set(["|", "/", ":", "[", "]", "{", "}"]))
    if set(username).intersection(bad_chars):
        # There were bad chars, so don't continue with this username
        return None
    return username

if __name__ == "__main__":
    app.run()
