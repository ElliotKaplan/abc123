SITE = 'http://sessionsgrenoble.free.fr/articles.php?lng=fr&pg=299'
from bs4 import BeautifulSoup
import requests
import re
from pandas import Series, DataFrame
from collections import Counter
from itertools import chain
from pymongo import MongoClient
import numpy as np

datesreg = re.compile(r"\d\d?\/\d\d?\/\d\d\d\d")

print('requesting site')
r = requests.get(SITE)
print('done')
soup = BeautifulSoup(r.text, 'lxml')
setlists = {u.text: u
        for u in soup.find_all('u')
        if datesreg.search(u.text) is not None}

def cleantitle(title):
    # gets rid of some nuisance strings if the style is included it's in
    # parentheses at the end
    for paren in ('(', '['):
        parenthind = title.find(paren)
        if parenthind != -1:
            title = title[:parenthind]
    return title.strip()

WORDREG = re.compile('\w*')
def titlevector(title):
    # cleans up the title, removing 'the's, space and punctuation, and returns a pandas series with a count of letters
    title = cleantitle(title).lower()
    # get rid of the 'the's
    thereg = re.compile(r'\bthe\b')
    thes = list(thereg.finditer(title))
    while thes:
        the = thes.pop()
        title = title[:the.start()] + title[the.end():]
    title = ''.join(w.group(0) for w in WORDREG.finditer(title))
    return Series(Counter(title))

def makesetlist(key, masterlist):
    setlist = masterlist[key].find_next('ul')
    splittitles = chain(*(li.text.split('/')
                          for li in setlist.find_all('li')))
    return [cleantitle(t) for t in splittitles]

def makeguesses(morceaux,
                collectionname='grenoble',
                databasename='local'):
    with MongoClient() as client:
        coll = client[databasename][collectionname]
        dbvecs = DataFrame({d['T']: titlevector(d['T'])
                            for d in coll.find()
                            if d['T'] is not None})
        dbvecs.fillna(0, inplace=True)
        dbvecs.sort_index(inplace=True)
        dbkeys = {d['T']: d['_id']
                  for d in coll.find() if d['T'] is not None}
        # get the best fit
        guesses = (np.abs(dbvecs.subtract(titlevector(m), axis=0)).sum(axis=0).idxmin() for m in morceaux)
    return [[m, g, dbkeys[g]] for m, g in zip(morceaux, guesses)]

def makeabc(fout, keys,
            collectionname='grenoble', databasename='local'):
    with MongoClient() as client, open(fout, 'w') as fobj:
        coll = client[databasename][collectionname]
        for i, key in enumerate(keys):
            entry = next(coll.find({'_id': key[2]}))
            fobj.write('X: {}\n'.format(i))
            fobj.writelines('{}: {}\n'.format(k, entry[k])
                            for k in ('T', 'K', 'L', 'M', 'R'))
            fobj.write(entry['song'])
                       
            
            
    
