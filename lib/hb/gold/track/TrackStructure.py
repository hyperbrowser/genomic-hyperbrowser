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
from collections import OrderedDict

from gold.track.Track import Track
from quick.application.SignatureDevianceLogging import takes
import copy

'''
Created on Sep 23, 2015

@author: boris
'''

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

    def _copyTreeStructure(self):
        newCopy = copy.copy(self)
        for key in self.keys():
            newCopy[key] = newCopy[key]._copyTreeStructure()
        return newCopy

class SingleTrackTS(TrackStructureV2):
    @takes(object, Track, dict)
    def __init__(self, track, metadata):
        self.track = track
        self.metadata = metadata

    def __setitem__(self, key, value):
        raise

    def _copyTreeStructure(self):
        return self

    def _copySegregatedSubtree(self, nodeToSplitOn, keyOfSubtree):
        return self


class MultipleTracksTS(TrackStructureV2):
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
        return set([ts.metadata.get(metadataField) for ts in self.values()])


    def getTrackSubsetTS(self, metadataField, selectedValue):
        subsetTS = MultipleTracksTS()
        for key, ts in self.iteritems():
            assert isinstance(ts, SingleTrackTS)
            if ts.metadata.get(metadataField) == selectedValue:
                subsetTS[key] = ts
        return subsetTS

    def getSplittedByCategoryTS(self, metadataField):
        '''
        Returns a categorical TS, containing a separate MultipleTracksTS
        per value in selected metadata field
        '''
        categoricalTS = CategoricalTS()
        catValues = self.getAllValuesForMetadataField(metadataField)
        for cat in catValues:
            categoricalTS[str(cat)] = self.getTrackSubsetTS(metadataField, cat)
        return categoricalTS

    def _copySegregatedSubtree(self, nodeToSplitOn, subCategoryKey):
        newCopy = copy.copy(self)
        for key, value in self.items():
            if value == nodeToSplitOn:
                newCopy[key] = value[subCategoryKey]._copyTreeStructure()
            else:
                newCopy[key] = value._copySegregatedSubtree(nodeToSplitOn, subCategoryKey)
        return newCopy


    def makeTreeSegregatedByCategory(self, nodeToSplitOn):
        # TODO Lonneke; add asserts to test input

        newRoot = MultipleTracksTS()
        for subCategoryKey, subtree in nodeToSplitOn.items():
            newRoot[subCategoryKey] = self._copySegregatedSubtree(nodeToSplitOn, subCategoryKey)
        return newRoot



class CategoricalTS(TrackStructureV2):
    pass


