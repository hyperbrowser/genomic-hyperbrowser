from gold.track.TrackStructure import TrackStructureV2
from gold.util.CommonClasses import OrderedDefaultDict
from gold.util.CustomExceptions import ArgumentValueError
from collections import OrderedDict

from quick.application.SignatureDevianceLogging import takes

PVAL_KEY = 'P-value'
M_KEY = 'NumMoreExtremeThanObs'
NUM_SAMPLES_KEY = 'NumResamplings'

from numpy import isnan,array, median

@takes(tuple, str, basestring)
def evaluatePvalueAndNullDistribution(observedAndMcSamplesTuple, tail, rawStatisticMainClassName):
    observation = observedAndMcSamplesTuple[0]
    mcSamples = observedAndMcSamplesTuple[1]
    if isinstance(observation, TrackStructureV2):
        observation = observation.result
        mcSamples = [ts.result for ts in mcSamples]
    assert isinstance(observation, (int, float, long))
    assert all([isinstance(mcSample, (int, float, long)) for mcSample in mcSamples])

    return _evaluatePvalueAndNullDistributionCommon(mcSamples, observation, rawStatisticMainClassName, tail)


def _evaluatePvalueAndNullDistributionCommon(mcSamples, observation, rawStatisticMainClassName, tail):
    numResamplings = len(mcSamples)
    numpyRandResults = array(mcSamples)
    nonNanNumpyRandResults = numpyRandResults[~isnan(numpyRandResults)]
    numberOfNonNanRandResults = len(nonNanNumpyRandResults)
    meanOfNullDistr = nonNanNumpyRandResults.mean(dtype='float64')
    medianOfNullDistr = median(nonNanNumpyRandResults)
    sdOfNullDistr = nonNanNumpyRandResults.std(dtype='float64')
    # sdCountFromNullOfObs = (observation - meanOfNullDistr) / sdOfNullDistr
    diffObsMean = (observation - meanOfNullDistr)
    # For more info on the formula for calculating p-values:
    # "Permutation P-values should never be zero: calculating exact P-values
    #  when permutations are randomly drawn" (http://www.ncbi.nlm.nih.gov/pubmed/21044043)
    numMoreExtreme = computeNumMoreExtreme(observation, mcSamples, tail)
    pval = computePurePseudoPvalue(observation, mcSamples, tail)
    return OrderedDict(
        [(PVAL_KEY, pval), ('TSMC_' + rawStatisticMainClassName, observation), ('MeanOfNullDistr', meanOfNullDistr), \
         ('MedianOfNullDistr', medianOfNullDistr), ('SdNullDistr', sdOfNullDistr), ('DiffFromMean', diffObsMean),
         (NUM_SAMPLES_KEY, numResamplings), \
         ('NumSamplesNotNan', numberOfNonNanRandResults), (M_KEY, numMoreExtreme)])

@takes(tuple, str, basestring)
def evaluatePvalueAndNullDistributionList(observedAndMcSamplesTuple, tail, rawStatisticMainClassName):
    resultsDict = OrderedDict()
    #TODO: What is received is not a list of tuples, it is a tuple of the real result which is a
    # TrackStructure whose result is a list of raw values and list of such track structures.
    # Need to find a way to handle it.

    observedResult = observedAndMcSamplesTuple[0]
    mcSamplesTsList = observedAndMcSamplesTuple[1]
    #TODO: What about categorial ts results?
    isPairedTsResult = all([val.isPairedTs() for val in observedResult.values()])
    observedResultDict = OrderedDict()
    mcSamplesResultDict = OrderedDefaultDict(list)
    if isPairedTsResult:
        for pairedTs in observedResult.values():
            trackTitle = pairedTs['reference'].metadata['title']
            assert trackTitle not in observedResultDict, "%s already in observed results dict" % trackTitle
            observedResultDict[trackTitle] = pairedTs.result
        for mcSampleTs in mcSamplesTsList:
            for pairedTs in mcSampleTs.values():
                trackTitle = pairedTs['reference'].metadata['title']
                mcSamplesResultDict[trackTitle].append(pairedTs.result)
    else: #isFlat?
        raise Exception('not implemented yet!')

    for trackTitle, observation in observedResultDict.iteritems():
        resultsDict[trackTitle] = evaluatePvalueAndNullDistribution((observation, mcSamplesResultDict[trackTitle]), tail, rawStatisticMainClassName)

    return resultsDict

def evaluatePurePseudoPvalue(observedAndMcSamplesTuple, tail, rawStatisticMainClassName):
    observation = observedAndMcSamplesTuple[0]
    mcSamples = observedAndMcSamplesTuple[1]
    pval = computePurePseudoPvalue(observation, mcSamples, tail)
    return {PVAL_KEY:pval}

def computePurePseudoPvalue(observation, mcSamples, tail):
    numResamplings = len(mcSamples)
    if tail in ['right-tail', 'left-tail']:
        tailFactor = 1.0
    elif tail == 'two-tail':
        tailFactor = 2.0
    else:
        raise ArgumentValueError('Invalid value for tails argument:', tail)
    numMoreExtreme = computeNumMoreExtreme(observation, mcSamples, tail)
    pval = tailFactor * (numMoreExtreme+1) / (numResamplings+1)
    pval = min(1.0, pval)
    return pval

    
def computeNumMoreExtreme(observation, mcSamples, tail):
    numMoreExtremeRight = sum(1 for res in mcSamples \
                     if res >= observation ) 
    numMoreExtremeLeft = sum(1 for res in mcSamples \
                     if res <= observation ) 
    if tail == 'right-tail':
        return numMoreExtremeRight
    elif tail == 'left-tail':
        return numMoreExtremeLeft
    elif tail == 'two-tail':
        return min(numMoreExtremeLeft, numMoreExtremeRight)
    
    raise ArgumentValueError('Invalid value for tails argument:', tail)

    
    