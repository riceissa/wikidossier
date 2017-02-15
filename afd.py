import re

def get_votes(wikitext, normalize=True):
    '''
    Given the wikitext of an AfD page, return a list of tuples (vote, username)
    for votes in the AfD.
    '''
    # Modified from
    # https://github.com/APerson241/afdstats/blob/d1932ecf5447d2b621dce99c982da7cb877d3778/public_html/afdstats.py#L139-L140
    # Remove all parts tagged as strikeouts
    wikitext = re.sub("<(s|strike|del)>.*?</(s|strike|del)>", "", data,
            flags=re.IGNORECASE|re.DOTALL)
    votes = re.findall(
            "\*[ ]*'''(.*?)'''" # capture the vote
            + ".*?\[\[User.*?:(.*?)(?:\|.*?)?\]\]" # capture username
            + ".*?\(UTC\)", data, flags=re.IGNORECASE)
    if normalize:
        # Just some rudimentary normalization for now
        votes = [(v.lower(), u) for v, u in votes]
    return votes
