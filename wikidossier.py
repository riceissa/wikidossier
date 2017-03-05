#!/usr/bin/python3

import matplotlib
matplotlib.use('Agg')

import time
import os.path
from threading import Lock
from flask import Flask, request, render_template, url_for, redirect
import sys
import pandas as pd
import base64
from io import BytesIO

import sizediff
import plot
import util

app = Flask(__name__)

lock = Lock()

@app.route("/user", methods=["GET", "POST"])
def user_front():
    if request.method == "POST":
        username = sanitize_username(request.form['username'])
        if username:
            return redirect(url_for("user_result_page", username=username))
        else:
            return "Invalid username"
    return render_template("user_front.html")

@app.route("/user/<username>")
def user_result_page(username):
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
    bio = BytesIO()
    plot.plot_user_cumsum_sizediff(username, df, figpath=bio, figformat="png")
    plot_data = base64.encodebytes(bio.getvalue()).decode()
    return render_template("user_result.html", username=username,
            image_data=plot_data)

@app.route("/usercompare")
def user_compare():
    usernames = request.args["usernames"].split("|")
    ns = int(request.args["ns"])
    # List of valid usernames
    usernames = list(filter(bool, map(sanitize_username, usernames)))
    for u in usernames:
        data_path = "data/" + u
        if not os.path.exists(data_path):
            with lock:
                # Hack to initialize the file so we can append to it
                with open(data_path, "w") as f:
                    f.write("")
                for revision in sizediff.process_user(u):
                    with open(data_path, "a") as f:
                        f.write(revision + "\n")
    df = pd.concat((pd.read_csv("data/" + u, sep="\t", header=None,
            names=["username", "ns", "timestamp", "sizediff"])
            for u in usernames))
    df = plot.timeseries_df(df)
    df = df[df.ns == ns] # Restrict to namespace of interest
    bio = BytesIO()
    plot.plot_all_users_cumsum_sizediff(df, ns, figpath=bio, figformat="png")
    plot_data = base64.encodebytes(bio.getvalue()).decode()
    return render_template("usercompare.html", usernames=usernames,
            namespace=util.NAMESPACES_INV_MAP.get(ns),
            image_data=plot_data)

def sanitize_username(username):
    '''
    Take an English Wikipedia username. If the username is safe, return a
    normalized version of the username. Otherwise return None.
    '''
    username = str(username)
    if username in [".", ".."] or len(username) > 300:
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
