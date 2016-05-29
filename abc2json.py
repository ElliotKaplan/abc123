import pandas as pd
from pandas import Series, DataFrame
from collections import deque
from itertools import groupby, takewhile

class GroupByX():
    """Checks for new songs. For use with groupby"""
    def __init__(self, sentinel='X:'):
        self.sentinel = sentinel
        self.lastx = None

    def findsentinel(self, line):
        if line.startswith(self.sentinel):
            self.lastx = line
        return self.lastx

class isMeta():
    """splits off the meta data, saves the last line"""
    def __init__(self):
        self.last = None
        
    def ismeta(self, line):
        self.last=line
        return (line[1] == ':') and (not line.startswith('|'))


def parseabc(iterable):
    """converts lines to a Series object"""
    im = isMeta()
    datum = {ell[0]: ell[2:].strip()
             for ell in takewhile(im.ismeta, iterable)}
    datum['song'] = im.last + ''.join(iterable)
    return Series(datum)
    

def abc2pandas(fname, encoding='iso8859'):
    im = isMeta()
    with open(fname, 'r', encoding=encoding) as fobj:
        data = pd.concat([parseabc(lines)
                          for head, lines in groupby(fobj, GroupByX().findsentinel)], axis=1)
    return data


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(
        """reads in an abc file and writes a JSON file""")
    parser.add_argument('abcin', type=str,
                        help='file to read, must end with abc')
    parser.add_argument('jsonout', type=str,
                        help='file to write, must end with json')
    clin = parser.parse_args()
    assert clin.abcin.endswith('.abc'), 'must read an abc file'
    assert clin.jsonout.endswith('.json'), 'must write a json file'
    
    df = abc2pandas(clin.abcin)
    df.drop('X', axis=0, inplace=True)
    df.to_json(clin.jsonout)
                   
