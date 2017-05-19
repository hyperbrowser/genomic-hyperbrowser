from collections import OrderedDict

from gold.track.Track import Track
from gold.util.CustomExceptions import LackingTsResultsError
from quick.application.SignatureDevianceLogging import takes
import copy

class TrackStructure(dict):
    '''
    Dictionary-like object that contains lists of tracks.
    For now only query and reference track lists are supported.
    '''
    QUERY_KEY = 'query'
    REF_KEY = 'reference'
    
    ALLOWED_KEYS = [QUERY_KEY, REF_KEY]

    def __setitem__(self, *args, **kwargs):
        assert len(args) == 2
        assert args[0] in self.ALLOWED_KEYS, '%s is not an allowed key' % args[0]
        assert isinstance(args[1], list)
        assert all([isinstance(x, Track) for x in args[1]])
        return dict.__setitem__(self, *args, **kwargs)
  
    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)
    
    def update(self, *args, **kwargs):
        for key, val in dict(*args, **kwargs).iteritems():
            self[key] = val
                
    def getQueryTrackList(self):
        if self.QUERY_KEY in self:
            return self[self.QUERY_KEY]
    
    def getReferenceTrackList(self):
        if self.REF_KEY in self:
            return self[self.REF_KEY]
    
    def __eq__(self, other):
        
        if len(self.keys()) != len(other.keys()):
            return False
        
        for k in self.keys():
            if k not in other.keys():
                return False
            
        return hash(self) == hash(other)

    def __hash__(self):
        '''
        Pre-sort the keys to always get the same order of the track lists in the Track structure.
        Return the hash of the tuple whose elements are tuples created from the lists of tracks.
        '''
        keys = sorted(self.keys())
        #TODO: boris 20150924, is Track.getUniqueKey a good candidate for hashing and equality check?
        #It doesn't work without specifying a genome
        #return hash(tuple([tuple([x.getUniqueKey() for x in self[k]]) for k in keys]))
        return hash(tuple([tuple([tuple(x.trackName) for x in self[k]]) for k in keys]))

class TrackStructureV2(dict):
    #Note: we might want an init method here that creates an attribute "results"
    #For now, this attribute is created when assigned a value
    #An advantage of this is that it distinguished lack of result from a result that has value None (if that might be relevant)
    #A disadvantage is that it becomes less clear that such an attribute might exist,
    # and its existence has to be checked with hasattr(ts,'results')

    #@takes(object, str, TrackStructureV2)
    def __setitem__(self, key, value):
        assert isinstance(key, str)
        assert isinstance(value, TrackStructureV2)
        dict.__setitem__(self, key, value)


    def _getResult(self):
        if hasattr(self, '_result'):
            return self._result
        else:
            return self._inferResult()

    def _inferResult(self):
        return dict([(childTSKey, self[childTSKey].result) for childTSKey in self.keys()]) #TODO: if the class itself is changed to become OrderedDict, then also this should be an OrderedDict

    def _setResult(self, value):
        self._result = value

    result = property(_getResult, _setResult)

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        if len(self.keys()) != len(other.keys()):
            return False

        for k in self.keys():
            if k not in other.keys():
                return False

        return hash(self) == hash(other)

    def __hash__(self):
        '''
        Pre-sort the keys to always get the same order of the track lists in the Track structure.
        Return the hash of the tuple with the hash values of self.values (recursive)
        The recursion ends at a TrackStructure without children (returns hash of empty tuple),
        or at a SingleTrackStructure (returns the hash of the track name and title)
        '''
        keys = sorted(self.keys())
        return hash(tuple([hash(self[key]) for key in keys]))

    def isFlat(self):
        # All children are SingleTrackTS -> True
        # There are no children -> True
        # Is SingleTrackTS -> True
        # Is FlatTracksTS -> True
        for child in self.values():
            if not isinstance(child, SingleTrackTS):
                return False
        return True

    def isPairedTs(self):
        return self.keys() == ['query', 'reference'] \
               and isinstance(self['query'], SingleTrackTS) \
               and isinstance(self['reference'], SingleTrackTS)

    def isSingleTs(self):
        return isinstance(self, SingleTrackTS)

    def _copyTreeStructure(self):
        newCopy = copy.copy(self)
        for key in self.keys():
            newCopy[key] = newCopy[key]._copyTreeStructure()
        return newCopy

    def _copySegregatedSubtree(self, nodeToSplitOn, subCategoryKey):
        newCopy = copy.copy(self)
        for key, value in self.items():
            if value == nodeToSplitOn:
                newCopy[key] = value[subCategoryKey]._copyTreeStructure()
            else:
                newCopy[key] = value._copySegregatedSubtree(nodeToSplitOn, subCategoryKey)
        return newCopy


    def makeTreeSegregatedByCategory(self, nodeToSplitOn):
        # TODO Lonneke: what if root is given, how to split?

        assert len(nodeToSplitOn.items()) > 0
        #if self == nodeToSplitOn:
        #    return self._copyTreeStructure()

        newRoot = TrackStructureV2()
        for subCategoryKey, subtree in nodeToSplitOn.items():
            newRoot[subCategoryKey] = self._copySegregatedSubtree(nodeToSplitOn, subCategoryKey)
        return newRoot

    def _getLeafNodes(self):
        leafNodes = []
        for subtree in self.values():
            leafNodes += subtree._getLeafNodes()
        return leafNodes

    def _getOriginalNodeName(self, originalName, usedNames):
        nodeName = str(originalName)

        counter = 2
        while nodeName in usedNames:
            nodeName = str(originalName) + " (" + str(counter) + ")"
            counter += 1

        return nodeName

    def getFlattenedTS(self):
        '''Returns a flattened (FlatTracksTS) copy of the TrackStructure, does not alter the
        TrackStructure itself. Only the metadata in leaf nodes is preserved.'''
        if self.isFlat():
            return self._copyTreeStructure()

        # copy the root and clear the key/value pairs
        # this way all other (metadata) fields won't be removed
        newRoot = FlatTracksTS()

        for leafNode in self._getLeafNodes():
            # TODO Lonneke use a better, original key to represent the tracks
            newRoot[self._getOriginalNodeName(leafNode.track.trackName, newRoot.keys())] = leafNode

        return newRoot


    def makePairwiseCombinations(self, referenceTS):
        # Not necessary? See Trello
        # assert self.isFlat()
        # assert referenceTS.isFlat()

        queryLeafNodes = self._getLeafNodes()
        referenceLeafNodes = referenceTS._getLeafNodes()

        root = TrackStructureV2()

        for query in queryLeafNodes:
            for reference in referenceLeafNodes:
                newPair = TrackStructureV2()
                newPair['query'] = query
                newPair['reference'] = reference
                root[str(query.track.trackName) + "_" + str(reference.track.trackName)] = newPair
        return root

class SingleTrackTS(TrackStructureV2):
    @takes(object, Track, dict)
    def __init__(self, track, metadata):
        assert isinstance(track, Track), track
        assert isinstance(metadata, dict)
        for key, value in metadata.items():
            assert isinstance(key, str)
            assert isinstance(value, basestring), (type(value), value)
        self.track = track
        self.metadata = metadata

    def __setitem__(self, key, value):
        raise

    def _inferResult(self):
        raise LackingTsResultsError

    def __hash__(self):
        # track.getUniqueKey(...) is not a good candidate for hashing as it needs a genome
        # when a new track is created you can only be sure a name and title have been provided
        return hash((hash(tuple(self.track.trackName)), hash(self.track.trackTitle)))

    def _copyTreeStructure(self):
        return self

    def _copySegregatedSubtree(self, nodeToSplitOn, keyOfSubtree):
        return self

    def _getLeafNodes(self):
        return [self]


class FlatTracksTS(TrackStructureV2):
    pass
    # def __init__(self):
    #     pass

    #@takes(object, str, TrackStructureV2)
    def __setitem__(self, key, value):
        assert isinstance(key, str)
        assert isinstance(value, SingleTrackTS)
        dict.__setitem__(self, key, value)

    def getMetadataFields(self):
        allMetadataFields = OrderedDict()

        for ts in self.values():
            for metadataField in ts.metadata.keys():
                allMetadataFields[metadataField] = True

        return allMetadataFields.keys()

    def getAllValuesForMetadataField(self, metadataField):
        return set([str(ts.metadata.get(metadataField)) for ts in self.values() if metadataField in ts.metadata.keys()])


    def getTrackSubsetTS(self, metadataField, selectedValue):
        assert isinstance(metadataField, (str,unicode)), (metadataField, type(metadataField))

        subsetTS = FlatTracksTS()
        for key, ts in self.iteritems():
            assert isinstance(ts, SingleTrackTS)
            if metadataField in [str(field) for field in ts.metadata] and str(ts.metadata.get(metadataField)) == str(selectedValue):
                subsetTS[key] = ts
        return subsetTS

    def getSplittedByCategoryTS(self, metadataField):
        '''
        Returns a categorical TS, containing a separate MultipleTracksTS per value in selected
        metadata field. Nodes that do not contain the given metadata field are not returned.
        '''
        categoricalTS = CategoricalTS()
        catValues = self.getAllValuesForMetadataField(metadataField)
        for cat in catValues:
            categoricalTS[str(cat)] = self.getTrackSubsetTS(metadataField, cat)
        return categoricalTS


class CategoricalTS(TrackStructureV2):
    pass

