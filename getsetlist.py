SITE = 'http://sessionsgrenoble.free.fr/articles.php?lng=fr&pg=299'
from bs4 import BeautifulSoup
import requests
import re
from pandas import Series
from collections import Counter
from itertools import chain

datesreg = re.compile(r"\d\d?\/\d\d?\/\d\d\d\d")

print('requesting site')
r = requests.get(SITE)
print('done')
soup = BeautifulSoup(r.text, 'lxml')
setlists = {u.text: u
        for u in soup.find_all('u')
        if datesreg.search(u.text) is not None}

def cleantitle(title):
    # splits sets into individual songs, gets rid of some nuisance strings
    # if the style is included it's in parentheses at the end
    parenthind = title.find('(')
    if parenthind != -1:
        title = title[:parenthind]
    # split the sets
    title = [t.strip() for t in title.split('/')]
    return title

def titlevector(title):
    # cleans up the title, removing 'the's, space and punctuation, and returns a pandas series with a count of letters
    title = title.lower()
    # get rid of the 'the's
    thereg = re.compile(r'\bthe\b')
    thes = list(thereg.finditer(title))
    while thes:
        the = thes.pop()
        title = title[:the.start()] + title[the.end():]
        print(title)
    wordreg = re.compile('\w*')
    title = ''.join(w.group(0) for w in wordreg.finditer(title))
    return Series(Counter(title))

def makesetlist(key, masterlist):
    setlist = masterlist[key].find_next('ul')
    morceaux = list(chain(*(cleantitle(li.text) for li in setlist.findAll('li'))))
    return morceaux

