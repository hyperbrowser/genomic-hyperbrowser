import numpy as np

from collections import OrderedDict


class NumpyDataFrame(object):
    def __init__(self, dictOfIterables={}, mask=None):
        self._arrayDict = OrderedDict()
        self._mask = None

        for key, iterable in dictOfIterables.iteritems():
            self.addArray(key, iterable)
        self.mask = mask  # Calls the @property setter to set self._mask

    def hasArray(self, key):
        return key in self._arrayDict

    def arrayKeys(self):
        return self._arrayDict.keys()

    def addArray(self, key, iterable):
        newArray = np.array(iterable) if not isinstance(iterable, np.ndarray) else iterable
        self._assertValidShape(newArray)
        self._arrayDict[key] = newArray

    def updateArray(self, key, iterable):
        newArray = np.array(iterable) if not isinstance(iterable, np.ndarray) else iterable
        self._arrayDict[key][:] = newArray

    def _assertValidShape(self, newArray):
        if newArray.shape == ():
            raise ValueError('Scalar (0-dimensional) arrays are not supported: ' + repr(newArray))
        if len(self._arrayDict) > 0:
            if len(newArray) != len(self):
                raise ValueError('Shape of added array does not match the shape of the existing '
                                 'arrays in the first dimension (if not scalar): %s != %s' %
                                 (len(newArray), len(self)))

    def removeArray(self, key):
        del self._arrayDict[key]

    def getArray(self, key):
        array = self._arrayDict[key]
        if self.mask is not None:
            return array[np.invert(self.mask)]
        else:
            return array

    def getArrayNoMask(self, key):
        return self._arrayDict[key]

    def asArrayDict(self):
        return OrderedDict([(key, self.getArray(key)) for key in self.arrayKeys()])

    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, mask):
        if mask is None:
            self._mask = None
        else:
            maskArray = np.array(mask, dtype=bool)
            self._assertValidShape(maskArray)
            self._mask = maskArray

    def sort(self, order):
        '''
        Sorts the NumpyDataFrame in place according to multiple arrays.
        :param order: The keys of the arrays to use in sorting, in order (primary key first)
        :return: None
        '''
        assert len(order) > 0
        assert all(key in self._arrayDict for key in order)
        # In lexsort, the last key is the primary key, so we here reverse the key order
        indices = np.lexsort([self._arrayDict[key] for key in reversed(order)])
        for array in self._arrayDict.values():
            array[:] = array[indices]
        if self.mask is not None:
            self.mask[:] = self.mask[indices]

    def __len__(self):
        if len(self._arrayDict) > 0:
            return len(self._arrayDict.values()[0])
        return 0

    def __getattr__(self, attrName):
        if hasattr(np.ndarray, attrName):
            doCall = False
            returnCallable = callable(getattr(np.ndarray, attrName))
            return _mergeAttrResultsFromAllArrays(self, attrName, doCall, returnCallable)
        else:
            raise AttributeError, attrName

    def __copy__(self):
        objCopy = NumpyDataFrame()
        objCopy._arrayDict = self._arrayDict
        objCopy._mask = self._mask
        return objCopy

    def __deepcopy__(self, memo):
        from copy import deepcopy
        objCopy = NumpyDataFrame()
        objCopy._arrayDict = deepcopy(self._arrayDict, memo)
        objCopy._mask = deepcopy(self._mask, memo)
        return objCopy


class CallableOrderedDict(OrderedDict):
    def __init__(self, *args, **kwArgs):
        super(CallableOrderedDict, self).__init__(*args, **kwArgs)
        self.mask = None

    def __call__(self, *args, **kwArgs):
        ret = OrderedDict([(key, val.__call__(*args, **kwArgs)) for key, val in self.iteritems()])

        try:
            return NumpyDataFrame(ret, mask=self.mask)
        except:
            return ret


def _mergeAttrResultsFromAllArrays(self, attrName, doCall, returnCallable, *args, **kwArgs):
    ret = OrderedDict([(key, _getAttrResultsFromArray(key, array, attrName, doCall, *args, **kwArgs))
                       for key, array in self._arrayDict.iteritems()])
    if self.mask is None:
        mask = None
    else:
        mask = _getAttrResultsFromArray(None, self.mask, attrName, doCall, *args, **kwArgs)

    if returnCallable:
        callableRet = CallableOrderedDict(ret)
        callableRet.mask = mask
        return callableRet
    else:
        try:
            return NumpyDataFrame(ret, mask=mask)
        except:
            return ret


def _getAttrResultsFromArray(key, array, attrName, doCall, *args, **kwArgs):
    if doCall:
        if key is not None:
            args = list(args)
            for i, arg in enumerate(args):
                if isinstance(arg, OrderedDict):
                    args[i] = arg[key]
                elif isinstance(arg, NumpyDataFrame):
                    args[i] = arg.getArray(key)
        return getattr(array, attrName)(*args, **kwArgs)
    else:
        return getattr(array, attrName)


NDARRAY_SPECIAL_ATTRIBUTES_TO_OVERRIDE = [
    '__abs__',
    '__add__',
    '__and__',
    # '__array__',
    # '__array_finalize__',
    # '__array_interface__',
    # '__array_prepare__',
    # '__array_priority__',
    # '__array_struct__',
    # '__array_wrap__',
    '__contains__',
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
    #'__hash__',
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
    # '__repr__',
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
    # '__str__',
    '__sub__',
    '__subclasshook__',
    '__truediv__',
    '__xor__'
]


def _setupAttr(cls, attrName):
    returnCallable = False

    if callable(getattr(np.ndarray, attrName)):
        doCall = True

        def newAttr(self, *args, **kwArgs):
            return _mergeAttrResultsFromAllArrays(self, attrName, doCall, returnCallable,
                                                  *args, **kwArgs)
    else:
        doCall = False

        @property
        def newAttr(self):
            return _mergeAttrResultsFromAllArrays(self, attrName, doCall, returnCallable)

    setattr(cls, attrName, newAttr)


for attrName in NDARRAY_SPECIAL_ATTRIBUTES_TO_OVERRIDE:
    _setupAttr(NumpyDataFrame, attrName)
