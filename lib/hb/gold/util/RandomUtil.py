import itertools
import random
import numpy.random

from config.Config import DebugConfig
from gold.util.CustomExceptions import ShouldNotOccurError


class HbRandom(random.Random):
    def __init__(self):
        super(HbRandom, self).__init__(self)
        self._storedFullState = None
        self._manualSeed = None
        self._stateHashAtLastManualSeeding = None
        self._seed = None
        self.initSeed()

    def initSeed(self):
        self._manualSeed = None
        self._stateHashAtLastManualSeeding = None
        self.autoSeed()

    def autoSeed(self):
        assert self._manualSeed is None, 'Automatic seed cannot override seeds that are set manually.'

        if DebugConfig.VERBOSE:
            print 'Autoseeding...'
        self._seed = self.createRandomSeed()
        self._seedAll()

    def setManualSeed(self, seed):
        assert seed is not None, 'Cannot set manual seed to None.'

        if seed != self._manualSeed:
            if DebugConfig.VERBOSE:
                print 'Current manual seed is: {}'.format(self._manualSeed)
                print 'Changing manual seed to: {}'.format(seed)
            self._manualSeed = seed
            self._stateHashAtLastManualSeeding = None

        fullStateHash = self.getFullStateHash()
        if self._stateHashAtLastManualSeeding is None or self._stateHashAtLastManualSeeding != fullStateHash:
            if DebugConfig.VERBOSE and self._stateHashAtLastManualSeeding is not None:
                print 'The current hash of the randomization state ({}) differs from the '.format(fullStateHash) + \
                      'hash of the randomization state ({}) '.format(self._stateHashAtLastManualSeeding) + \
                      'after the last manual seeding using seed: {}'.format(self._manualSeed)
            self._seed = self._manualSeed
            self._seedAll()
            self._stateHashAtLastManualSeeding = self.getFullStateHash()

    def _seedAll(self):
        if DebugConfig.VERBOSE:
            print 'Seeding all randomization algorithms with: {} '.format(self._seed)
        self.seed(self._seed)
        numpy.random.seed(self._seed)
        from proto.RSetup import r
        r('function(seed) { set.seed(seed) }')(self._seed)
        r('runif(1)')  # to harmonize with integration test results (based on earlier logic).

    def getManualSeed(self):
        return self._manualSeed

    def getSeed(self):
        return self._seed

    @staticmethod
    def createRandomSeed():
        return random.randint(0, 2 ** 31 - 1)

    def returnToStoredFullState(self):
        if self._storedFullState is None:
            return ShouldNotOccurError('Tried to return to previous random state without a stored state.')

        self.setstate(self._storedFullState[0])
        numpy.random.set_state(self._storedFullState[1])
        from proto.RSetup import r
        r('function(state) {.Random.seed <- state}')(self._storedFullState[2])
        self._storedFullState = None

    def storeFullState(self):
        self._storedFullState = self.getFullState()

    def getFullState(self):
        from proto.RSetup import r
        return self.getstate(), numpy.random.get_state(), r('.Random.seed')

    def getFullStateHash(self):
        fullState = self.getFullState()
        return hash((fullState[0], fullState[1][0], fullState[1][1].tobytes(), fullState[2].tobytes()))


random = HbRandom()

initSeed = random.initSeed
autoSeed = random.autoSeed
setManualSeed = random.setManualSeed
getManualSeed = random.getManualSeed
getSeed = random.getSeed
createRandomSeed = random.createRandomSeed
returnToStoredFullState = random.returnToStoredFullState
storeFullState = random.storeFullState