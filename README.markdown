# Wikidossier – Tools to stalk Wikipedia users and pages

You can see the app deployed on Heroku.
For example:

- <https://wikidossier.herokuapp.com/user/Riceissa>
- <https://wikidossier.herokuapp.com/usercompare?usernames=Vipul|Riceissa|Ethanbas&ns=0>

## Usage

For testing/development:

```bash
$ flask initdb
$ echo "type the user agent you want to use here" > user-agent.txt
# The user agent is used for making queries to the Wikipedia API
$ flask run
# Then just visit http://127.0.0.1:5000/
# (or whatever the terminal output says) in your browser
```

For deployment on the server: (idk, it's been many years and i forgot how to do this.)

## List of scripts

* `sizediff.py`: This script uses the MediaWiki API to obtain revisions by
  username, and stores it as a TSV. The columns are "username", "ns" (namespace
  number), "timestamp", and "sizediff" (difference in bytes of the page before
  and after the edit).
* `revisions.py`: This script uses the MediaWiki API to obtain revisions by
  page name and stores it as a TSV. The columns are "pagename", "timestamp",
  and "size".
* `afd.py`: This script gathers some information from AfDs, most notably the
  voting information (a list of tuples (*v*, *u*), where *v* is the vote –
  keep, delete, merge, whatever – and *u* is the user that cast the vote).
* `plot.py`: This script takes the data collected using the other scripts and
  plots them.
* `wikidossier.py`: The main Flask app

## Notes

To filter out "strange" page titles, I used

    /[^\d9\d32-\d126“”‘’–—§éñãí¡áóâ°üčō×½êàëżıå]
    :g//d

in Vim, to find characters not in a whitelist, and then deleting all lines with
characters outside of that list.
We can work out something better later.

## License

CC0; see `LICENSE` for the full text.
