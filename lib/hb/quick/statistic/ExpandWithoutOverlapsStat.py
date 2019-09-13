from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.ExpandWithOverlapsStat import ExpandWithOverlapsStat
from quick.statistic.MergeStat import MergeStatUnsplittable


class ExpandWithoutOverlapsStat(MagicStatFactory):
    pass


class ExpandWithoutOverlapsStatUnsplittable(MergeStatUnsplittable):

    def _createChildren(self):
        print 'expand wo overlaps addChild'
        self._addChild(ExpandWithOverlapsStat(self._region, self._track, **self._kwArgs))
