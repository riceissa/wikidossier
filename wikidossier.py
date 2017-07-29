#!/usr/bin/python3

import matplotlib
matplotlib.use('Agg')

import time
import os.path
from threading import Lock
from flask import Flask, request, render_template, url_for, redirect, g
import sys
import sqlite3
import pandas as pd
import base64
from io import BytesIO

import sizediff
import plot
import util

DATABASE = "wikidossier.db"

app = Flask(__name__)

lock = Lock()

# From http://flask.pocoo.org/docs/0.12/tutorial/setup/
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv

# From http://flask.pocoo.org/docs/0.12/tutorial/dbinit/
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

# From http://flask.pocoo.org/docs/0.12/tutorial/dbinit/
@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

# From http://flask.pocoo.org/docs/0.12/tutorial/dbcon/
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# From http://flask.pocoo.org/docs/0.12/tutorial/dbcon/
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route("/")
def homepage():
    return render_template("homepage.html")


@app.route("/user", methods=["GET", "POST"])
def user_front():
    if request.method == "POST":
        username = sanitize_username(request.form['username'])
        if username:
            return redirect(url_for("user_result_page", username=username))
        else:
            return "Invalid username"
    return render_template("user_front.html")

def fetch_sizediff_data(db, username):
    """
    Fetch new sizediff data from the upstream API, for the user username into
    the sqlite database db.
    """
    cur = db.execute("""select revid from usercontribs
            where username = ? order by revid desc limit 1""", (username,))
    try:
        db_rev = cur.fetchall()[0]["revid"]
    except:
        print("User not in db, so setting db revid to 0", file=sys.stderr)
        db_rev = 0
    print("DB REVID is", db_rev, file=sys.stderr)
    numRevisionsInserted = 0
    for revision in sizediff.process_user(username):
        curr_rev = revision[0]
        if curr_rev > db_rev:
            numRevisionsInserted += 1
            db.execute("""insert into usercontribs
                (revid, username, ns, timestamp, sizediff)
                values (?, ?, ?, ?, ?)""",
                revision)
        else:
            break
    print("Finished inserting " + str(numRevisionsInserted) + " revisions into db")
    db.commit()

@app.route("/user/<username>")
def user_result_page(username):
    username = sanitize_username(username)
    if not username:
        return "Invalid username"
    db = get_db()
    fetch_sizediff_data(db, username)
    df = pd.read_sql("select * from usercontribs where username = ?", db,
            params=(username,))
    df = plot.timeseries_df(df)

    # Do cumsum plot
    bio = BytesIO()
    plot.plot_user_cumsum_sizediff(username, df, figpath=bio, figformat="png")
    cumsum_plot_data = base64.encodebytes(bio.getvalue()).decode()

    # Do histogram
    bio = BytesIO()
    plot.plot_user_sizediff_histogram(username, df,
            limit=int(request.args.get("hlimit", 10000)),
            minlimit=int(request.args.get("hminlimit", 100)),
            figpath=bio, figformat="png")
    hist_plot_data = base64.encodebytes(bio.getvalue()).decode()

    return render_template("user_result.html", username=username,
            cumsum_data=cumsum_plot_data, hist_data=hist_plot_data)

@app.route("/usercompare")
def user_compare():
    usernames = request.args["usernames"].split("|")
    ns = int(request.args["ns"])
    # List of valid usernames
    usernames = list(filter(bool, map(sanitize_username, usernames)))
    db = get_db()
    for u in usernames:
        fetch_sizediff_data(db, u)
    df = pd.concat((pd.read_sql("""select * from usercontribs
        where username = ? and ns = ?""", db,
        params=(u, ns)) for u in usernames))
    df = plot.timeseries_df(df)
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
