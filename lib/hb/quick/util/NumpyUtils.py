# Utility functions for Numpy objects
import numpy as np


def getNumpyMatrixMaxElement(npMat):
    maxRowInd=0
    maxColInd=0
    try:
        maxRowInd, maxColInd = np.unravel_index(np.nanargmax(npMat), npMat.shape)
    except ValueError as e:
        pass
    return npMat[maxRowInd, maxColInd], maxRowInd, maxColInd



def getNumpyMatrixMinElement(npMat):
    minRowInd = 0
    minColInd = 0
    try:
        minRowInd, minColInd = np.unravel_index(np.nanargmin(npMat), npMat.shape)
    except ValueError as e:
        pass
    return npMat[minRowInd, minColInd], minRowInd, minColInd