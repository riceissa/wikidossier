#!/usr/bin/python3

def main():
    username = "Riceissa"
    print("<!DOCTYPE html>")
    print("<html>")
    print("<head>")
    print('  <meta charset="utf-8">')
    print('  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">')
    print("</head>")
    print("<body>")
    print('''<style>
            iframe{
                border:none;
                width:100%;
                height:600px;
            }</style>''')
    print("  <h1>Wikidossier for {}</h1>".format(username))
    print("  <p>Here is some basic information about this user:</p>")
    print('  <ul>')
    print('    <li><a href="#edit-count">Edit count</a></li>'.format(username))
    print('    <li><a href="#pages-created">Pages created</a></li>' \
            .format(username))
    print('    <li><a href="https://tools.wmflabs.org/afdstats/afdstats.py?name={}&amp;max=500&amp;startdate=&amp;altname=">AfD votes</a></li>'.format(username))
    print('    <li><a href="https://en.wikipedia.org/wiki/Special:PrefixIndex/User:{}/">Subpages</a></li>'.format(username))
    print('  </ul>')
    print(('''
        <h2 id="edit-count">Edit count</h2>
        <p><a href="https://tools.wmflabs.org/xtools-ec/?user={u}'''
        '''&amp;project=en.wikipedia.org">Edit count</a></p>
        <iframe src="https://tools.wmflabs.org/xtools-ec/?user={u}'''
        '''&amp;project=en.wikipedia.org"></iframe>
    ''').format(u=username))
    print(('''
        <h2 id="pages-created">Pages created</h2>
        <p><a href="https://tools.wmflabs.org/xtools/pages/?user={u}'''
        '''&amp;project=en.wikipedia.org&amp;namespace=all&amp;'''
        '''redirects=none">Pages created</a></p>
        <iframe src="https://tools.wmflabs.org/xtools/pages/?user={u}'''
        '''&amp;project=en.wikipedia.org&amp;namespace=all&amp;'''
        '''redirects=none"></iframe>
    ''').format(u=username))
    print("</body>")

if __name__ == "__main__":
    main()