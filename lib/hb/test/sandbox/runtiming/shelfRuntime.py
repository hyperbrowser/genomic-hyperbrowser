# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.

import shelve
import copy
from cPickle import dump, load

def createS():
    s = shelve.open('slett','c')
    for i in xrange(100000):
        s[str(i)] = i*3    
    print len(s.keys())
    s.close()

def createS2():
    s = shelve.open('slett','c')
    s2 = {}
    for i in xrange(100000):
        s2[str(i)] = i*3        
    print len(s2.keys())
    s.update(s2)
    s.close()
    
def createSpickle():
    #s = open('slett','c')
    s2 = {}
    for i in xrange(100000):
        s2[str(i)] = i*3        
    print len(s2.keys())
    dump(s2,open('slett.pickle','w'))
    #s.close()
    
def loadS1():
    s = shelve.open('slett','r')
    for i in xrange(100000):
        temp = s[str(i)]+1
    s.close()

def loadS2():
    s = shelve.open('slett','r')
    #s2 = dict(s.items())
    s2 = {}
    s2.update(s)
    #s.close()
    print 'mid..'
    for i in xrange(100000):
        temp = s[str(i)]+1
    
def loadPickle():
    s = load(open('slett.pickle'))
    for i in xrange(100000):
        temp = s[str(i)]+1
    #s.close()

print 'starting'
#createSpickle()
loadPickle()
#loadS2()
print 'finished'