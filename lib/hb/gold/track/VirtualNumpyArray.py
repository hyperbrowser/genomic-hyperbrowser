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

#abstract
class VirtualNumpyArray(object):
    def __init__(self):
        self._cachedNumpyArray = None
        
    def cacheNumpyArray(self):
        self._cachedNumpyArray = self._asNumpyArray()

    def __getattr__(self, name):
        if self._cachedNumpyArray is None:
            self.cacheNumpyArray()
        return getattr(self._cachedNumpyArray, name)

def _delegateMethod(cls, delegateCls, method_name):
    method = getattr(delegateCls, method_name)
    
    def f(self, *args, **kwArgs):
        if self._cachedNumpyArray is None:
            self.cacheNumpyArray()
        return method(self._cachedNumpyArray, *args, **kwArgs)
    
    f.func_name = method_name
    setattr(cls, method_name, f)

NDARRAY_SPECIAL_METHODS_TO_OVERRIDE = [
 '__abs__',
 '__add__',
 '__and__',
 '__contains__',
 '__copy__',
 '__deepcopy__',
 '__delitem__',
 '__delslice__',
 '__div__',
 '__divmod__',
 '__eq__',
 '__float__',
 '__floordiv__',
 '__format__',
 '__ge__',
 '__getitem__',
 '__getslice__',
 '__gt__',
 '__hash__',
 '__hex__',
 '__iadd__',
 '__iand__',
 '__idiv__',
 '__ifloordiv__',
 '__ilshift__',
 '__imod__',
 '__imul__',
 '__index__',
 '__int__',
 '__invert__',
 '__ior__',
 '__ipow__',
 '__irshift__',
 '__isub__',
 '__iter__',
 '__itruediv__',
 '__ixor__',
 '__le__',
 '__len__',
 '__long__',
 '__lshift__',
 '__lt__',
 '__mod__',
 '__mul__',
 '__ne__',
 '__neg__',
 '__nonzero__',
 '__oct__',
 '__or__',
 '__pos__',
 '__pow__',
 '__radd__',
 '__rand__',
 '__rdiv__',
 '__rdivmod__',
 '__reduce__',
 '__reduce_ex__',
 '__repr__',
 '__rfloordiv__',
 '__rlshift__',
 '__rmod__',
 '__rmul__',
 '__ror__',
 '__rpow__',
 '__rrshift__',
 '__rshift__',
 '__rsub__',
 '__rtruediv__',
 '__rxor__',
 '__setitem__',
 '__setslice__',
 '__setstate__',
 '__sizeof__',
 '__str__',
 '__sub__',
 '__subclasshook__',
 '__truediv__',
 '__xor__'
]

from numpy import ndarray
for method_name in NDARRAY_SPECIAL_METHODS_TO_OVERRIDE:
    _delegateMethod(VirtualNumpyArray, ndarray, method_name)