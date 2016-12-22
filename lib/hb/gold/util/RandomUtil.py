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

import random
import numpy.random
from gold.util.CustomExceptions import ShouldNotOccurError

class HbRandom(random.Random):
    _seed = None
    _storedStates = None

random = HbRandom()

def setManualSeed(seed):
    random._seed = seed
    
    if seed is None:
        seed = getRandomSeed()
        
    random.seed(seed)
    numpy.random.seed(seed)
    from proto.RSetup import r
    r('function(seed) {set.seed(seed)}')(seed)
    
def getManualSeed():
    return random._seed

def initSeed():
    setManualSeed(None)
    
def getRandomSeed():
    random.seed()
    return random.randint(0, 2**31-1)    
    
def returnToStoredState():
    if random._storedStates is None:
        return ShouldNotOccurError('Tried to return to previous random state without a stored state.')
    
    random.setstate(random._storedStates[0])
    numpy.random.set_state(random._storedStates[1])
    from proto.RSetup import r
    r('function(state) {.Random.seed <- state}')(random._storedStates[2])

def storeState():
    from proto.RSetup import r
    r('runif(1)')
    random._storedStates = [random.getstate(), numpy.random.get_state(), r('.Random.seed')]
    
